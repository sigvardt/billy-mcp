"""Headless-only persistent Playwright runtime with deny-by-default egress."""

from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Callable, Iterable
from pathlib import Path
from typing import Literal, Protocol, cast
from urllib.parse import urlsplit

import yaml
from pydantic import BaseModel, ConfigDict, Field, ValidationError, field_validator, model_validator

from billy_mcp.credentials import (
    BrowserCredentialReferences,
    CredentialResolver,
    KeyringCredentialResolver,
)
from billy_mcp.models import AuthLoginStartSuccess, AuthStatusSuccess, StableErrorCode, ToolError

DEFAULT_BROWSER_EGRESS_MANIFEST = (
    Path(__file__).resolve().parents[2] / "coverage" / "browser_egress.yaml"
)
_BILLY_APP_ROOT_URL = "https://mit.billy.dk/"
_BILLY_LOGIN_URL_PATH = "/login"
_LOGIN_CONTROL_SELECTORS = (
    "input[type='email'][name='email']",
    "input[type='password'][name='password']",
    "input[type='checkbox'][name='remember']",
)
_LOGIN_SUBMIT_SELECTOR = "button[data-cy='login-button']"
_LOGIN_SUBMIT_LABELS = frozenset({"Log in", "Log ind"})


class BrowserEgressManifestHost(BaseModel):
    """One reviewed browser/API egress entry from the frozen manifest."""

    model_config = ConfigDict(extra="forbid", strict=True)

    api_client_action: Literal["deny", "exclusive_allow"]
    browser_action: Literal["allow", "deny"]
    condition: str
    evidence: str
    host: str
    owner: str
    purpose: str
    test_references: list[str] = Field(min_length=1)

    @field_validator("host")
    @classmethod
    def require_exact_host(cls, value: str) -> str:
        normalized = value.lower()
        if value != value.strip() or not _is_exact_host(normalized):
            raise ValueError("host must be an exact DNS host name")
        return normalized


class BrowserEgressManifest(BaseModel):
    """The deny-by-default manifest contract approved for browser egress."""

    model_config = ConfigDict(extra="forbid", strict=True)

    default_action: Literal["deny"]
    hosts: list[BrowserEgressManifestHost] = Field(min_length=1)
    manifest: Literal["billy_browser_egress_phase_0"]
    schema_version: Literal[1]

    @model_validator(mode="after")
    def require_unique_hosts(self) -> BrowserEgressManifest:
        hosts = [entry.host for entry in self.hosts]
        if len(hosts) != len(set(hosts)):
            raise ValueError("browser egress hosts must be unique")
        return self


class BrowserEgressPolicyLoadError(ValueError):
    """Raised when the reviewed browser-egress manifest cannot be trusted."""


def _is_exact_host(value: str) -> bool:
    """Accept only normal DNS names, never URLs, wildcards, ports, or paths."""

    labels = value.split(".")
    return (
        value.isascii()
        and len(value) <= 253
        and len(labels) >= 2
        and all(
            1 <= len(label) <= 63
            and label[0].isalnum()
            and label[-1].isalnum()
            and all(character.isalnum() or character == "-" for character in label)
            for label in labels
        )
    )


class BrowserRequest(Protocol):
    """The small request surface needed for egress enforcement."""

    @property
    def url(self) -> str: ...


class BrowserRoute(Protocol):
    """The small route surface needed for allow/deny decisions."""

    @property
    def request(self) -> BrowserRequest: ...

    async def continue_(self) -> None: ...

    async def abort(self, error_code: str | None = None) -> None: ...


RouteHandler = Callable[[BrowserRoute], Awaitable[None]]


class PersistentContext(Protocol):
    """Persistent-context operations permitted to this bounded runtime."""

    async def route(self, url: str, handler: RouteHandler) -> None: ...

    async def new_page(self) -> LoginPage: ...

    async def close(self) -> None: ...


class LoginControl(Protocol):
    """The exact, internal DOM reads needed to verify the recorded login form."""

    async def count(self) -> int: ...

    async def is_visible(self) -> bool: ...

    async def inner_text(self) -> str: ...

    async def fill(self, value: str) -> None: ...

    async def click(self) -> None: ...


class LoginPage(Protocol):
    """A deliberately minimal page surface for the fixed auth-status workflow."""

    @property
    def url(self) -> str: ...

    async def goto(self, url: str, *, wait_until: Literal["domcontentloaded"]) -> object: ...

    def locator(self, selector: str) -> LoginControl: ...

    async def close(self) -> None: ...


class AuthStatusChecker(Protocol):
    """Injectable, auth-status-only seam for deterministic server tests."""

    async def auth_status(self) -> AuthStatusSuccess | ToolError: ...


class AuthLoginService(Protocol):
    """Injectable seam for the two purpose-built login operations."""

    async def auth_login_start(self) -> AuthLoginStartSuccess | ToolError: ...

    async def auth_login_wait(self) -> AuthStatusSuccess | ToolError: ...


class PersistentContextLauncher(Protocol):
    """Injectable launcher used to make the no-window policy unit-testable."""

    async def __call__(
        self,
        profile_path: str,
        *,
        headless: bool,
        accept_downloads: bool,
    ) -> PersistentContext: ...


class BrowserEgressPolicy:
    """Exact, trusted hosts only; callers cannot expand this policy per request."""

    def __init__(self, allowed_hosts: Iterable[str]) -> None:
        hosts = frozenset(host.strip().lower() for host in allowed_hosts if host.strip())
        if not hosts or any("*" in host or "/" in host for host in hosts):
            raise ValueError("Browser egress hosts must be non-empty exact host names")
        self._allowed_hosts = hosts

    @classmethod
    def from_manifest(cls, manifest_path: Path) -> BrowserEgressPolicy:
        """Construct a policy from the reviewed manifest, failing closed on every defect."""

        try:
            with manifest_path.open(encoding="utf-8") as manifest_file:
                raw_manifest = yaml.safe_load(manifest_file)
            manifest = BrowserEgressManifest.model_validate(raw_manifest)
            return cls(entry.host for entry in manifest.hosts if entry.browser_action == "allow")
        except (OSError, ValidationError, ValueError, yaml.YAMLError) as error:
            raise BrowserEgressPolicyLoadError(
                "Browser egress manifest is unavailable or invalid."
            ) from error

    @property
    def allowed_hosts(self) -> frozenset[str]:
        return self._allowed_hosts

    def allows(self, url: str) -> bool:
        parsed = urlsplit(url)
        try:
            port = parsed.port
        except ValueError:
            return False
        return (
            parsed.scheme == "https"
            and port in {None, 443}
            and (parsed.hostname or "").lower() in self._allowed_hosts
        )


class BrowserRuntime:
    """Own at most one headless persistent context and no browser-control tools."""

    def __init__(
        self,
        profile_path: Path,
        *,
        egress_manifest_path: Path = DEFAULT_BROWSER_EGRESS_MANIFEST,
        launcher: PersistentContextLauncher | None = None,
        credential_references: BrowserCredentialReferences | None = None,
        credential_resolver: CredentialResolver | None = None,
    ) -> None:
        self._profile_path = profile_path.expanduser().resolve(strict=False)
        self._egress_manifest_path = egress_manifest_path.expanduser().resolve(strict=False)
        self._policy: BrowserEgressPolicy | None = None
        self._launcher = launcher
        self._credential_references = credential_references or BrowserCredentialReferences()
        self._credential_resolver = credential_resolver or KeyringCredentialResolver()
        self._context: PersistentContext | None = None
        self._playwright_stopper: Callable[[], Awaitable[None]] | None = None
        self._lock = asyncio.Lock()

    async def start(self) -> PersistentContext:
        """Launch exactly one persistent context with headless mode forced on."""

        async with self._lock:
            if self._context is None:
                # Resolve the reviewed policy at the only browser start boundary.
                # A missing, malformed, or deny-only manifest therefore prevents
                # Playwright from launching rather than silently broadening egress.
                self._policy = BrowserEgressPolicy.from_manifest(self._egress_manifest_path)
                stopper: Callable[[], Awaitable[None]] | None = None
                if self._launcher is None:
                    context, stopper = await _launch_persistent_context(
                        str(self._profile_path),
                        headless=True,
                        accept_downloads=False,
                    )
                else:
                    context = await self._launcher(
                        str(self._profile_path),
                        headless=True,
                        accept_downloads=False,
                    )
                try:
                    await context.route("**/*", self._enforce_egress)
                except BaseException:
                    try:
                        await context.close()
                    finally:
                        if stopper is not None:
                            await stopper()
                    raise
                self._playwright_stopper = stopper
                self._context = context
            return self._context

    async def close(self) -> None:
        """Close the owned context; no screenshot, tracing, video, or HAR is retained."""

        async with self._lock:
            if self._context is not None:
                context = self._context
                self._context = None
                stopper = self._playwright_stopper
                self._playwright_stopper = None
                try:
                    await context.close()
                finally:
                    if stopper is not None:
                        await stopper()

    async def auth_status(self) -> AuthStatusSuccess | ToolError:
        """Classify only the recorded Billy login page without exposing browser controls."""

        try:
            context = await self.start()
            page = await context.new_page()
            try:
                await page.goto(_BILLY_APP_ROOT_URL, wait_until="domcontentloaded")
                if not await _has_known_login_page(page):
                    return _ui_changed_error()
                return AuthStatusSuccess()
            finally:
                await page.close()
        except BrowserEgressPolicyLoadError:
            return ToolError(
                code=StableErrorCode.EGRESS_DENIED,
                message="Browser egress policy prevented the authentication status check.",
            )
        except Exception:
            return ToolError(
                code=StableErrorCode.BILLY_ERROR,
                message="Browser authentication status could not be determined.",
            )

    async def auth_login_start(self) -> AuthLoginStartSuccess | ToolError:
        """Perform only the fixed pre-submit transition and retain no resolved values."""

        page: LoginPage | None = None
        try:
            context = await self.start()
            page = await context.new_page()
            await page.goto(_BILLY_APP_ROOT_URL, wait_until="domcontentloaded")
            if not await _has_known_login_page(page):
                return _ui_changed_error()

            resolved_values = self._resolve_required_values()
            if resolved_values is None:
                return _auth_required_error()
            primary_value, secondary_value = resolved_values

            if not await _has_known_login_page(page):
                return _ui_changed_error()
            await page.locator(_LOGIN_CONTROL_SELECTORS[0]).fill(primary_value)

            if not await _has_known_login_page(page):
                return _ui_changed_error()
            await page.locator(_LOGIN_CONTROL_SELECTORS[1]).fill(secondary_value)

            if not await _has_known_login_page(page):
                return _ui_changed_error()
            await page.locator(_LOGIN_SUBMIT_SELECTOR).click()
            return AuthLoginStartSuccess()
        except BrowserEgressPolicyLoadError:
            return ToolError(
                code=StableErrorCode.EGRESS_DENIED,
                message="Browser egress policy prevented the login transition.",
            )
        except Exception:
            return ToolError(
                code=StableErrorCode.BILLY_ERROR,
                message="Browser login transition could not be completed.",
            )
        finally:
            if page is not None:
                try:
                    await page.close()
                except Exception:
                    # The original outcome remains redacted even when a browser
                    # implementation cannot confirm page closure.
                    pass

    async def auth_login_wait(self) -> AuthStatusSuccess | ToolError:
        """Observe only the already-reviewed login state after a transition starts."""

        return await self.auth_status()

    def _resolve_required_values(self) -> tuple[str, str] | None:
        """Resolve exactly two required values after signature validation only."""

        references = self._credential_references
        if not references.has_required_references():
            return None
        primary_reference = references.primary
        secondary_reference = references.secondary
        if primary_reference is None or secondary_reference is None:
            return None
        try:
            primary_value = self._credential_resolver.resolve(primary_reference)
        except Exception:
            return None
        if not primary_value or not primary_value.strip():
            return None
        try:
            secondary_value = self._credential_resolver.resolve(secondary_reference)
        except Exception:
            return None
        if not secondary_value or not secondary_value.strip():
            return None
        return primary_value, secondary_value

    async def _enforce_egress(self, route: BrowserRoute) -> None:
        policy = self._policy
        if policy is None:
            await route.abort("blockedbyclient")
        elif policy.allows(route.request.url):
            await route.continue_()
        else:
            await route.abort("blockedbyclient")


def _is_known_login_url(url: str) -> bool:
    """Accept only the observed HTTPS Billy login route, without redirect parameters."""

    try:
        parsed = urlsplit(url)
        port = parsed.port
    except ValueError:
        return False
    return (
        parsed.scheme == "https"
        and parsed.hostname == "mit.billy.dk"
        and port in {None, 443}
        and parsed.username is None
        and parsed.password is None
        and parsed.path == _BILLY_LOGIN_URL_PATH
        and not parsed.query
        and not parsed.fragment
    )


async def _has_login_signature(page: LoginPage) -> bool:
    """Verify every observed login control exactly once and visibly present."""

    try:
        for selector in _LOGIN_CONTROL_SELECTORS:
            control = page.locator(selector)
            if await control.count() != 1 or not await control.is_visible():
                return False
        submit = page.locator(_LOGIN_SUBMIT_SELECTOR)
        return (
            await submit.count() == 1
            and await submit.is_visible()
            and (await submit.inner_text()).strip() in _LOGIN_SUBMIT_LABELS
        )
    except Exception:
        # Any DOM-read failure means the recorded page signature is no longer
        # trustworthy; do not disclose its contents or infer session state.
        return False


async def _has_known_login_page(page: LoginPage) -> bool:
    """Validate the fixed URL and exact signature without exposing page content."""

    return _is_known_login_url(page.url) and await _has_login_signature(page)


def _ui_changed_error() -> ToolError:
    """Return the stable fail-closed result without echoing page or session values."""

    return ToolError(
        code=StableErrorCode.UI_CHANGED,
        message="Billy login interface no longer matches the recorded signature.",
    )


def _auth_required_error() -> ToolError:
    """Return the stable missing-reference result without naming a locator."""

    return ToolError(
        code=StableErrorCode.AUTH_REQUIRED,
        message="Browser authentication material is unavailable.",
    )


async def _launch_persistent_context(
    profile_path: str,
    *,
    headless: bool,
    accept_downloads: bool,
) -> tuple[PersistentContext, Callable[[], Awaitable[None]]]:
    """Launch Playwright's persistent Chromium context without any desktop controls."""

    from playwright.async_api import async_playwright

    playwright = await async_playwright().start()
    try:
        context = await playwright.chromium.launch_persistent_context(
            profile_path,
            headless=headless,
            accept_downloads=accept_downloads,
        )
    except Exception:
        await playwright.stop()
        raise
    return cast(PersistentContext, context), playwright.stop
