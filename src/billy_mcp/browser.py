"""Headless-only persistent Playwright runtime with deny-by-default egress."""

from __future__ import annotations

import asyncio
import json
import re
from collections.abc import Awaitable, Callable, Iterable, Mapping
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
from billy_mcp.models import (
    AuthLoginStartSuccess,
    AuthLoginWaitSuccess,
    AuthStatusSuccess,
    StableErrorCode,
    ToolError,
    UiBankAccountsListSuccess,
    UiClientsListSuccess,
    UiInvoicesListSuccess,
    UiProductsImportSuccess,
    UiProductsListSuccess,
    UiQuotesListSuccess,
    UiRecurringInvoicesListSuccess,
)

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
# Non-PII shell markers from research100 (Danish authenticated dashboard).
_SHELL_NAV_MARKERS = (
    "text=Overblik",
    "text=Fakturering",
    "text=Menu",
)
_INTERACTION_CHALLENGE_SELECTORS = (
    "iframe[src*='recaptcha']",
    "iframe[src*='hcaptcha']",
    "input[autocomplete='one-time-code']",
    "input[name*='otp' i]",
    "input[name*='totp' i]",
)
_DASHBOARD_PATH = re.compile(r"^/[^/]+/dashboard$")
_INVOICES_LIST_PATH = re.compile(r"^/[^/]+/invoices$")
_INVOICES_LIST_HEADING = "Fakturaer"
_INVOICES_CREATE_CTA = "Opret faktura"
_PRODUCTS_LIST_PATH = re.compile(r"^/[^/]+/products$")
_PRODUCTS_LIST_HEADING = "Produkter"
_PRODUCTS_SEARCH_CONTROL = "[data-cy='search-button']"
_CLIENTS_LIST_PATH = re.compile(r"^/[^/]+/clients$")
_CLIENTS_LIST_HEADING = "Kunder"
_CLIENTS_CREATE_CTA = "Opret kontakt"
_BANK_ACCOUNTS_LIST_PATH = re.compile(r"^/[^/]+/bank-accounts$")
_BANK_ACCOUNTS_LIST_HEADING = "Bankkonti"
_BANK_ACCOUNTS_CONNECT_CTA = "Forbind til bank"
# Empty orgs land on /quotes/empty (research106); bare /quotes is also valid.
_QUOTES_LIST_PATH = re.compile(r"^/[^/]+/quotes(?:/empty)?$")
_QUOTES_LIST_HEADING = "Tilbud"
_QUOTES_CREATE_CTA = "Opret tilbud"
# Research107: bare /recurring_invoices observed; optional /empty accepted for symmetry.
_RECURRING_INVOICES_LIST_PATH = re.compile(r"^/[^/]+/recurring_invoices(?:/empty)?$")
_RECURRING_INVOICES_LIST_HEADING = "Abonnementer"
_RECURRING_INVOICES_CREATE_CTA = "Opret abonnement"
# Research108: product CSV import shell under products (shell open only; never choose file).
_PRODUCTS_IMPORT_PATH = re.compile(r"^/[^/]+/products/import$")
_PRODUCTS_IMPORT_HEADING = "Import af produkter"
_PRODUCTS_IMPORT_CHOOSE_CSV_CTA = "Vælg CSV-fil"
_ERROR_SHELL_MARKERS = (
    "text=Upsedasse!",
    "text=Upsedasse",
    "text=Log ind igen",
)
_ORG_IDENTITY_PATH = Path.home() / ".local" / "share" / "billy-mcp" / "ui-org-identity.json"
_HttpMethod = Literal["GET", "POST", "PUT", "PATCH", "DELETE", "HEAD", "OPTIONS"]


class BrowserPathAllowRule(BaseModel):
    """One reviewed method+path exception for a host that is not fully browser-open."""

    model_config = ConfigDict(extra="forbid", strict=True)

    methods: list[_HttpMethod] = Field(min_length=1)
    match: Literal["exact", "prefix"]
    path: str = Field(min_length=1)

    @field_validator("path")
    @classmethod
    def require_absolute_path(cls, value: str) -> str:
        if not value.startswith("/") or "*" in value or "://" in value:
            raise ValueError("path must be an absolute path without wildcards")
        return value

    @field_validator("methods")
    @classmethod
    def require_unique_methods(cls, value: list[_HttpMethod]) -> list[_HttpMethod]:
        if len(value) != len(set(value)):
            raise ValueError("path allow methods must be unique")
        return value


class BrowserEgressManifestHost(BaseModel):
    """One reviewed browser/API egress entry from the frozen manifest."""

    model_config = ConfigDict(extra="forbid", strict=True)

    api_client_action: Literal["deny", "exclusive_allow"]
    browser_action: Literal["allow", "deny", "path_allow"]
    browser_path_allows: list[BrowserPathAllowRule] = Field(
        default_factory=lambda: list[BrowserPathAllowRule]()
    )
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

    @model_validator(mode="after")
    def require_path_rules_for_path_allow(self) -> BrowserEgressManifestHost:
        if self.browser_action == "path_allow" and not self.browser_path_allows:
            raise ValueError("path_allow requires at least one browser_path_allows rule")
        if self.browser_action != "path_allow" and self.browser_path_allows:
            raise ValueError("browser_path_allows is only valid with browser_action path_allow")
        return self


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

    @property
    def method(self) -> str: ...


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

    async def check(self) -> None: ...

    async def click(self) -> None: ...


class LoginPage(Protocol):
    """A deliberately minimal page surface for the fixed auth workflows."""

    @property
    def url(self) -> str: ...

    async def goto(self, url: str, *, wait_until: Literal["domcontentloaded"]) -> object: ...

    def locator(self, selector: str) -> LoginControl: ...

    async def close(self) -> None: ...

    async def wait_for_load_state(
        self,
        state: Literal["load", "domcontentloaded", "networkidle"],
        *,
        timeout: float | None = None,
    ) -> None: ...


class AuthStatusChecker(Protocol):
    """Injectable, auth-status-only seam for deterministic server tests."""

    async def auth_status(self) -> AuthStatusSuccess | ToolError: ...


class AuthLoginService(Protocol):
    """Injectable seam for the two purpose-built login operations."""

    async def auth_login_start(self) -> AuthLoginStartSuccess | ToolError: ...

    async def auth_login_wait(self) -> AuthLoginWaitSuccess | ToolError: ...


class UiInvoicesListService(Protocol):
    """Injectable seam for the read-only invoices list shell observation."""

    async def ui_invoices_list(self) -> UiInvoicesListSuccess | ToolError: ...


class UiProductsListService(Protocol):
    """Injectable seam for the read-only products list shell observation."""

    async def ui_products_list(self) -> UiProductsListSuccess | ToolError: ...


class UiClientsListService(Protocol):
    """Injectable seam for the read-only clients list shell observation."""

    async def ui_clients_list(self) -> UiClientsListSuccess | ToolError: ...


class UiBankAccountsListService(Protocol):
    """Injectable seam for the read-only bank accounts list shell observation."""

    async def ui_bank_accounts_list(self) -> UiBankAccountsListSuccess | ToolError: ...


class UiQuotesListService(Protocol):
    """Injectable seam for the read-only quotes list shell observation."""

    async def ui_quotes_list(self) -> UiQuotesListSuccess | ToolError: ...


class UiRecurringInvoicesListService(Protocol):
    """Injectable seam for the read-only recurring invoices list shell observation."""

    async def ui_recurring_invoices_list(self) -> UiRecurringInvoicesListSuccess | ToolError: ...


class UiProductsImportService(Protocol):
    """Injectable seam for the read-only products import shell observation."""

    async def ui_products_import(self) -> UiProductsImportSuccess | ToolError: ...


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
    """Trusted hosts and optional path-scoped API exceptions; no per-request expansion."""

    def __init__(
        self,
        allowed_hosts: Iterable[str],
        path_allows: Mapping[str, tuple[BrowserPathAllowRule, ...]] | None = None,
    ) -> None:
        hosts = frozenset(host.strip().lower() for host in allowed_hosts if host.strip())
        if any("*" in host or "/" in host for host in hosts):
            raise ValueError("Browser egress hosts must be exact host names")
        path_map = {
            host.strip().lower(): rules
            for host, rules in (path_allows or {}).items()
            if host.strip() and rules
        }
        if not hosts and not path_map:
            raise ValueError("Browser egress policy must allow at least one host or path rule")
        self._allowed_hosts = hosts
        self._path_allows = path_map

    @classmethod
    def from_manifest(cls, manifest_path: Path) -> BrowserEgressPolicy:
        """Construct a policy from the reviewed manifest, failing closed on every defect."""

        try:
            with manifest_path.open(encoding="utf-8") as manifest_file:
                raw_manifest = yaml.safe_load(manifest_file)
            manifest = BrowserEgressManifest.model_validate(raw_manifest)
            full_hosts = [entry.host for entry in manifest.hosts if entry.browser_action == "allow"]
            path_allows = {
                entry.host: tuple(entry.browser_path_allows)
                for entry in manifest.hosts
                if entry.browser_action == "path_allow"
            }
            return cls(full_hosts, path_allows)
        except (OSError, ValidationError, ValueError, yaml.YAMLError) as error:
            raise BrowserEgressPolicyLoadError(
                "Browser egress manifest is unavailable or invalid."
            ) from error

    @property
    def allowed_hosts(self) -> frozenset[str]:
        return self._allowed_hosts

    def allows(self, url: str, method: str = "GET") -> bool:
        parsed = urlsplit(url)
        try:
            port = parsed.port
        except ValueError:
            return False
        if parsed.scheme != "https" or port not in {None, 443}:
            return False
        host = (parsed.hostname or "").lower()
        if host in self._allowed_hosts:
            return True
        rules = self._path_allows.get(host)
        if not rules:
            return False
        request_method = method.upper()
        path = parsed.path or "/"
        for rule in rules:
            if request_method not in rule.methods:
                continue
            if rule.match == "exact" and path == rule.path:
                return True
            if rule.match == "prefix" and path.startswith(rule.path):
                return True
        return False


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
        org_identity_path: Path | None = None,
    ) -> None:
        self._profile_path = profile_path.expanduser().resolve(strict=False)
        self._egress_manifest_path = egress_manifest_path.expanduser().resolve(strict=False)
        self._policy: BrowserEgressPolicy | None = None
        self._launcher = launcher
        self._credential_references = credential_references or BrowserCredentialReferences()
        self._credential_resolver = credential_resolver or KeyringCredentialResolver()
        self._org_identity_path = (
            org_identity_path.expanduser().resolve(strict=False)
            if org_identity_path is not None
            else _ORG_IDENTITY_PATH
        )
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

            # Persistent MCP profiles require Billy's "remember" control so the
            # session can restore after process close (research101).
            if not await _has_known_login_page(page):
                return _ui_changed_error()
            await page.locator(_LOGIN_CONTROL_SELECTORS[2]).check()

            if not await _has_known_login_page(page):
                return _ui_changed_error()
            await page.locator(_LOGIN_SUBMIT_SELECTOR).click()
            # Keep the page open long enough for the path-scoped login XHR and
            # cookie write to complete; classification remains auth_login_wait.
            await _await_login_transition_settle(page)
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

    async def auth_login_wait(self) -> AuthLoginWaitSuccess | ToolError:
        """Classify login-required vs READY shell after a transition on the persistent profile."""

        page: LoginPage | None = None
        try:
            context = await self.start()
            page = await context.new_page()
            await page.goto(_BILLY_APP_ROOT_URL, wait_until="domcontentloaded")
            # Poll briefly so real sessions can settle after auth_login_start.
            for _ in range(30):
                classification = await _classify_session_page(page)
                if isinstance(classification, AuthLoginWaitSuccess):
                    if classification.status == "READY":
                        _persist_org_slug_outside_git(page.url, self._org_identity_path)
                    return classification
                if isinstance(classification, ToolError):
                    return classification
                await asyncio.sleep(0.2)
            return _ui_changed_error()
        except BrowserEgressPolicyLoadError:
            return ToolError(
                code=StableErrorCode.EGRESS_DENIED,
                message="Browser egress policy prevented the login wait observation.",
            )
        except Exception:
            return ToolError(
                code=StableErrorCode.BILLY_ERROR,
                message="Browser login wait observation could not be completed.",
            )
        finally:
            if page is not None:
                try:
                    await page.close()
                except Exception:
                    pass

    async def ui_invoices_list(self) -> UiInvoicesListSuccess | ToolError:
        """Open the invoices list shell for the current authenticated UI session only."""

        page: LoginPage | None = None
        try:
            context = await self.start()
            page = await context.new_page()
            await page.goto(_BILLY_APP_ROOT_URL, wait_until="domcontentloaded")
            await _await_page_settle(page)

            if await _has_known_login_page(page):
                return _auth_required_error()
            if await _has_interaction_challenge(page):
                return ToolError(
                    code=StableErrorCode.AUTH_INTERACTION_REQUIRED,
                    message="Browser authentication requires a non-automatable challenge.",
                )

            slug = _resolve_org_slug(page.url, self._org_identity_path)
            if slug is None:
                return _ui_invoices_changed_error()

            invoices_url = f"https://mit.billy.dk/{slug}/invoices"
            await page.goto(invoices_url, wait_until="domcontentloaded")
            await _await_page_settle(page)

            for _ in range(30):
                if await _has_known_login_page(page):
                    return _auth_required_error()
                if await _has_interaction_challenge(page):
                    return ToolError(
                        code=StableErrorCode.AUTH_INTERACTION_REQUIRED,
                        message="Browser authentication requires a non-automatable challenge.",
                    )
                if await _has_error_shell_markers(page):
                    return _ui_invoices_changed_error()
                if _is_invoices_list_url(page.url) and await _has_invoices_list_signature(page):
                    return UiInvoicesListSuccess(
                        create_action_visible=True,
                        shell_markers_present=await _has_shell_nav_markers(page),
                    )
                await asyncio.sleep(0.2)
            return _ui_invoices_changed_error()
        except BrowserEgressPolicyLoadError:
            return ToolError(
                code=StableErrorCode.EGRESS_DENIED,
                message="Browser egress policy prevented the invoices list observation.",
            )
        except Exception:
            return ToolError(
                code=StableErrorCode.BILLY_ERROR,
                message="Browser invoices list observation could not be completed.",
            )
        finally:
            if page is not None:
                try:
                    await page.close()
                except Exception:
                    pass

    async def ui_products_list(self) -> UiProductsListSuccess | ToolError:
        """Open the products list shell for the current authenticated UI session only."""

        page: LoginPage | None = None
        try:
            context = await self.start()
            page = await context.new_page()
            await page.goto(_BILLY_APP_ROOT_URL, wait_until="domcontentloaded")
            await _await_page_settle(page)

            if await _has_known_login_page(page):
                return _auth_required_error()
            if await _has_interaction_challenge(page):
                return ToolError(
                    code=StableErrorCode.AUTH_INTERACTION_REQUIRED,
                    message="Browser authentication requires a non-automatable challenge.",
                )

            slug = _resolve_org_slug(page.url, self._org_identity_path)
            if slug is None:
                return _ui_products_changed_error()

            products_url = f"https://mit.billy.dk/{slug}/products"
            await page.goto(products_url, wait_until="domcontentloaded")
            await _await_page_settle(page)

            for _ in range(30):
                if await _has_known_login_page(page):
                    return _auth_required_error()
                if await _has_interaction_challenge(page):
                    return ToolError(
                        code=StableErrorCode.AUTH_INTERACTION_REQUIRED,
                        message="Browser authentication requires a non-automatable challenge.",
                    )
                if await _has_error_shell_markers(page):
                    return _ui_products_changed_error()
                if _is_products_list_url(page.url) and await _has_products_list_signature(page):
                    return UiProductsListSuccess(
                        search_control_visible=True,
                        shell_markers_present=await _has_shell_nav_markers(page),
                    )
                await asyncio.sleep(0.2)
            return _ui_products_changed_error()
        except BrowserEgressPolicyLoadError:
            return ToolError(
                code=StableErrorCode.EGRESS_DENIED,
                message="Browser egress policy prevented the products list observation.",
            )
        except Exception:
            return ToolError(
                code=StableErrorCode.BILLY_ERROR,
                message="Browser products list observation could not be completed.",
            )
        finally:
            if page is not None:
                try:
                    await page.close()
                except Exception:
                    pass

    async def ui_clients_list(self) -> UiClientsListSuccess | ToolError:
        """Open the clients list shell for the current authenticated UI session only."""

        page: LoginPage | None = None
        try:
            context = await self.start()
            page = await context.new_page()
            await page.goto(_BILLY_APP_ROOT_URL, wait_until="domcontentloaded")
            await _await_page_settle(page)

            if await _has_known_login_page(page):
                return _auth_required_error()
            if await _has_interaction_challenge(page):
                return ToolError(
                    code=StableErrorCode.AUTH_INTERACTION_REQUIRED,
                    message="Browser authentication requires a non-automatable challenge.",
                )

            slug = _resolve_org_slug(page.url, self._org_identity_path)
            if slug is None:
                return _ui_clients_changed_error()

            clients_url = f"https://mit.billy.dk/{slug}/clients"
            await page.goto(clients_url, wait_until="domcontentloaded")
            await _await_page_settle(page)

            for _ in range(30):
                if await _has_known_login_page(page):
                    return _auth_required_error()
                if await _has_interaction_challenge(page):
                    return ToolError(
                        code=StableErrorCode.AUTH_INTERACTION_REQUIRED,
                        message="Browser authentication requires a non-automatable challenge.",
                    )
                if await _has_error_shell_markers(page):
                    return _ui_clients_changed_error()
                if _is_clients_list_url(page.url) and await _has_clients_list_signature(page):
                    return UiClientsListSuccess(
                        create_action_visible=True,
                        shell_markers_present=await _has_shell_nav_markers(page),
                    )
                await asyncio.sleep(0.2)
            return _ui_clients_changed_error()
        except BrowserEgressPolicyLoadError:
            return ToolError(
                code=StableErrorCode.EGRESS_DENIED,
                message="Browser egress policy prevented the clients list observation.",
            )
        except Exception:
            return ToolError(
                code=StableErrorCode.BILLY_ERROR,
                message="Browser clients list observation could not be completed.",
            )
        finally:
            if page is not None:
                try:
                    await page.close()
                except Exception:
                    pass

    async def ui_bank_accounts_list(self) -> UiBankAccountsListSuccess | ToolError:
        """Open the bank accounts list shell for the current authenticated UI session only."""

        page: LoginPage | None = None
        try:
            context = await self.start()
            page = await context.new_page()
            await page.goto(_BILLY_APP_ROOT_URL, wait_until="domcontentloaded")
            await _await_page_settle(page)

            if await _has_known_login_page(page):
                return _auth_required_error()
            if await _has_interaction_challenge(page):
                return ToolError(
                    code=StableErrorCode.AUTH_INTERACTION_REQUIRED,
                    message="Browser authentication requires a non-automatable challenge.",
                )

            slug = _resolve_org_slug(page.url, self._org_identity_path)
            if slug is None:
                return _ui_bank_accounts_changed_error()

            bank_accounts_url = f"https://mit.billy.dk/{slug}/bank-accounts"
            await page.goto(bank_accounts_url, wait_until="domcontentloaded")
            await _await_page_settle(page)

            for _ in range(30):
                if await _has_known_login_page(page):
                    return _auth_required_error()
                if await _has_interaction_challenge(page):
                    return ToolError(
                        code=StableErrorCode.AUTH_INTERACTION_REQUIRED,
                        message="Browser authentication requires a non-automatable challenge.",
                    )
                if await _has_error_shell_markers(page):
                    return _ui_bank_accounts_changed_error()
                if _is_bank_accounts_list_url(page.url) and await _has_bank_accounts_list_signature(
                    page
                ):
                    return UiBankAccountsListSuccess(
                        connect_bank_action_visible=True,
                        shell_markers_present=await _has_shell_nav_markers(page),
                    )
                await asyncio.sleep(0.2)
            return _ui_bank_accounts_changed_error()
        except BrowserEgressPolicyLoadError:
            return ToolError(
                code=StableErrorCode.EGRESS_DENIED,
                message="Browser egress policy prevented the bank accounts list observation.",
            )
        except Exception:
            return ToolError(
                code=StableErrorCode.BILLY_ERROR,
                message="Browser bank accounts list observation could not be completed.",
            )
        finally:
            if page is not None:
                try:
                    await page.close()
                except Exception:
                    pass

    async def ui_quotes_list(self) -> UiQuotesListSuccess | ToolError:
        """Open the quotes list shell for the current authenticated UI session only."""

        page: LoginPage | None = None
        try:
            context = await self.start()
            page = await context.new_page()
            await page.goto(_BILLY_APP_ROOT_URL, wait_until="domcontentloaded")
            await _await_page_settle(page)

            if await _has_known_login_page(page):
                return _auth_required_error()
            if await _has_interaction_challenge(page):
                return ToolError(
                    code=StableErrorCode.AUTH_INTERACTION_REQUIRED,
                    message="Browser authentication requires a non-automatable challenge.",
                )

            slug = _resolve_org_slug(page.url, self._org_identity_path)
            if slug is None:
                return _ui_quotes_changed_error()

            quotes_url = f"https://mit.billy.dk/{slug}/quotes"
            await page.goto(quotes_url, wait_until="domcontentloaded")
            await _await_page_settle(page)

            for _ in range(30):
                if await _has_known_login_page(page):
                    return _auth_required_error()
                if await _has_interaction_challenge(page):
                    return ToolError(
                        code=StableErrorCode.AUTH_INTERACTION_REQUIRED,
                        message="Browser authentication requires a non-automatable challenge.",
                    )
                if await _has_error_shell_markers(page):
                    return _ui_quotes_changed_error()
                if _is_quotes_list_url(page.url) and await _has_quotes_list_signature(page):
                    return UiQuotesListSuccess(
                        create_action_visible=True,
                        shell_markers_present=await _has_shell_nav_markers(page),
                    )
                await asyncio.sleep(0.2)
            return _ui_quotes_changed_error()
        except BrowserEgressPolicyLoadError:
            return ToolError(
                code=StableErrorCode.EGRESS_DENIED,
                message="Browser egress policy prevented the quotes list observation.",
            )
        except Exception:
            return ToolError(
                code=StableErrorCode.BILLY_ERROR,
                message="Browser quotes list observation could not be completed.",
            )
        finally:
            if page is not None:
                try:
                    await page.close()
                except Exception:
                    pass

    async def ui_recurring_invoices_list(self) -> UiRecurringInvoicesListSuccess | ToolError:
        """Open the recurring invoices list shell for the current authenticated UI session only."""

        page: LoginPage | None = None
        try:
            context = await self.start()
            page = await context.new_page()
            await page.goto(_BILLY_APP_ROOT_URL, wait_until="domcontentloaded")
            await _await_page_settle(page)

            if await _has_known_login_page(page):
                return _auth_required_error()
            if await _has_interaction_challenge(page):
                return ToolError(
                    code=StableErrorCode.AUTH_INTERACTION_REQUIRED,
                    message="Browser authentication requires a non-automatable challenge.",
                )

            slug = _resolve_org_slug(page.url, self._org_identity_path)
            if slug is None:
                return _ui_recurring_invoices_changed_error()

            recurring_url = f"https://mit.billy.dk/{slug}/recurring_invoices"
            await page.goto(recurring_url, wait_until="domcontentloaded")
            await _await_page_settle(page)

            for _ in range(30):
                if await _has_known_login_page(page):
                    return _auth_required_error()
                if await _has_interaction_challenge(page):
                    return ToolError(
                        code=StableErrorCode.AUTH_INTERACTION_REQUIRED,
                        message="Browser authentication requires a non-automatable challenge.",
                    )
                if await _has_error_shell_markers(page):
                    return _ui_recurring_invoices_changed_error()
                if _is_recurring_invoices_list_url(
                    page.url
                ) and await _has_recurring_invoices_list_signature(page):
                    return UiRecurringInvoicesListSuccess(
                        create_action_visible=True,
                        shell_markers_present=await _has_shell_nav_markers(page),
                    )
                await asyncio.sleep(0.2)
            return _ui_recurring_invoices_changed_error()
        except BrowserEgressPolicyLoadError:
            return ToolError(
                code=StableErrorCode.EGRESS_DENIED,
                message="Browser egress policy prevented the recurring invoices list observation.",
            )
        except Exception:
            return ToolError(
                code=StableErrorCode.BILLY_ERROR,
                message="Browser recurring invoices list observation could not be completed.",
            )
        finally:
            if page is not None:
                try:
                    await page.close()
                except Exception:
                    pass

    async def ui_products_import(self) -> UiProductsImportSuccess | ToolError:
        """Open the products import shell for the current authenticated UI session only."""

        page: LoginPage | None = None
        try:
            context = await self.start()
            page = await context.new_page()
            await page.goto(_BILLY_APP_ROOT_URL, wait_until="domcontentloaded")
            await _await_page_settle(page)

            if await _has_known_login_page(page):
                return _auth_required_error()
            if await _has_interaction_challenge(page):
                return ToolError(
                    code=StableErrorCode.AUTH_INTERACTION_REQUIRED,
                    message="Browser authentication requires a non-automatable challenge.",
                )

            slug = _resolve_org_slug(page.url, self._org_identity_path)
            if slug is None:
                return _ui_products_import_changed_error()

            import_url = f"https://mit.billy.dk/{slug}/products/import"
            await page.goto(import_url, wait_until="domcontentloaded")
            await _await_page_settle(page)

            for _ in range(30):
                if await _has_known_login_page(page):
                    return _auth_required_error()
                if await _has_interaction_challenge(page):
                    return ToolError(
                        code=StableErrorCode.AUTH_INTERACTION_REQUIRED,
                        message="Browser authentication requires a non-automatable challenge.",
                    )
                if await _has_error_shell_markers(page):
                    return _ui_products_import_changed_error()
                if _is_products_import_url(page.url) and await _has_products_import_signature(page):
                    return UiProductsImportSuccess(
                        choose_csv_action_visible=True,
                        shell_markers_present=await _has_shell_nav_markers(page),
                    )
                await asyncio.sleep(0.2)
            return _ui_products_import_changed_error()
        except BrowserEgressPolicyLoadError:
            return ToolError(
                code=StableErrorCode.EGRESS_DENIED,
                message="Browser egress policy prevented the products import observation.",
            )
        except Exception:
            return ToolError(
                code=StableErrorCode.BILLY_ERROR,
                message="Browser products import observation could not be completed.",
            )
        finally:
            if page is not None:
                try:
                    await page.close()
                except Exception:
                    pass

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
        method = getattr(route.request, "method", "GET") or "GET"
        if policy is None:
            await route.abort("blockedbyclient")
        elif policy.allows(route.request.url, method):
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


def _is_dashboard_shell_url(url: str) -> bool:
    """Accept only mit.billy.dk /:org_slug/dashboard without leaking the slug."""

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
        and not parsed.query
        and not parsed.fragment
        and bool(_DASHBOARD_PATH.match(parsed.path or ""))
    )


def _is_invoices_list_url(url: str) -> bool:
    """Accept mit.billy.dk /:org_slug/invoices, including Billy's list query params."""

    try:
        parsed = urlsplit(url)
        port = parsed.port
    except ValueError:
        return False
    # Query params (page, filters) are allowed; the path class stays redacted.
    return (
        parsed.scheme == "https"
        and parsed.hostname == "mit.billy.dk"
        and port in {None, 443}
        and parsed.username is None
        and parsed.password is None
        and bool(_INVOICES_LIST_PATH.match(parsed.path or ""))
    )


def _is_products_list_url(url: str) -> bool:
    """Accept mit.billy.dk /:org_slug/products, including Billy list query params."""

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
        and bool(_PRODUCTS_LIST_PATH.match(parsed.path or ""))
    )


def _is_clients_list_url(url: str) -> bool:
    """Accept mit.billy.dk /:org_slug/clients, including Billy list query params."""

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
        and bool(_CLIENTS_LIST_PATH.match(parsed.path or ""))
    )


def _is_bank_accounts_list_url(url: str) -> bool:
    """Accept mit.billy.dk /:org_slug/bank-accounts, including Billy list query params."""

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
        and bool(_BANK_ACCOUNTS_LIST_PATH.match(parsed.path or ""))
    )


def _is_quotes_list_url(url: str) -> bool:
    """Accept mit.billy.dk /:org_slug/quotes or /quotes/empty, including query params."""

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
        and bool(_QUOTES_LIST_PATH.match(parsed.path or ""))
    )


def _is_recurring_invoices_list_url(url: str) -> bool:
    """Accept mit.billy.dk /:org_slug/recurring_invoices or optional /empty, including query."""

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
        and bool(_RECURRING_INVOICES_LIST_PATH.match(parsed.path or ""))
    )


def _is_products_import_url(url: str) -> bool:
    """Accept mit.billy.dk /:org_slug/products/import, including Billy query params."""

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
        and bool(_PRODUCTS_IMPORT_PATH.match(parsed.path or ""))
    )


def _org_slug_from_url(url: str) -> str | None:
    """Return the first path segment for an authenticated Billy app URL, or None."""

    try:
        parsed = urlsplit(url)
        if parsed.scheme != "https" or (parsed.hostname or "").lower() != "mit.billy.dk":
            return None
        path = parsed.path or ""
        if path == _BILLY_LOGIN_URL_PATH:
            return None
        parts = [segment for segment in path.split("/") if segment]
        if not parts:
            return None
        slug = parts[0]
        if slug == "login" or "/" in slug:
            return None
        return slug
    except Exception:
        return None


def _resolve_org_slug(url: str, identity_path: Path) -> str | None:
    """Resolve org slug from the current URL or the outside-git identity file only."""

    from_url = _org_slug_from_url(url)
    if from_url is not None:
        return from_url
    try:
        payload = json.loads(identity_path.read_text(encoding="utf-8"))
        slug = payload.get("org_slug")
        if isinstance(slug, str) and slug and "/" not in slug and slug != "login":
            return slug
    except Exception:
        return None
    return None


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


async def _await_login_transition_settle(page: LoginPage) -> None:
    """Allow the login XHR and navigation to finish without classifying success."""

    try:
        await page.wait_for_load_state("networkidle", timeout=15000)
        return
    except Exception:
        pass
    for _ in range(8):
        if not await _has_known_login_page(page):
            return
        await asyncio.sleep(0.05)


async def _await_page_settle(page: LoginPage) -> None:
    """Wait briefly for SPA navigation without classifying page content."""

    try:
        await page.wait_for_load_state("networkidle", timeout=15000)
    except Exception:
        await asyncio.sleep(0.2)


async def _has_shell_nav_markers(page: LoginPage) -> bool:
    """Require at least one non-PII shell marker observed in research100."""

    try:
        for selector in _SHELL_NAV_MARKERS:
            control = page.locator(selector)
            if await control.count() >= 1 and await control.is_visible():
                return True
        return False
    except Exception:
        return False


async def _has_invoices_list_signature(page: LoginPage) -> bool:
    """Verify the research102 invoices list heading and create CTA without clicking."""

    try:
        heading = page.locator("h1")
        if await heading.count() < 1 or not await heading.is_visible():
            return False
        if (await heading.inner_text()).strip() != _INVOICES_LIST_HEADING:
            return False
        create_action = page.locator(f"text={_INVOICES_CREATE_CTA}")
        return await create_action.count() >= 1 and await create_action.is_visible()
    except Exception:
        return False


async def _has_products_list_signature(page: LoginPage) -> bool:
    """Verify the research103 products list heading and search control without clicking."""

    try:
        heading = page.locator("h1")
        if await heading.count() < 1 or not await heading.is_visible():
            return False
        if (await heading.inner_text()).strip() != _PRODUCTS_LIST_HEADING:
            return False
        search = page.locator(_PRODUCTS_SEARCH_CONTROL)
        return await search.count() >= 1 and await search.is_visible()
    except Exception:
        return False


async def _has_clients_list_signature(page: LoginPage) -> bool:
    """Verify the research104 clients list heading and create CTA without clicking."""

    try:
        heading = page.locator("h1")
        if await heading.count() < 1 or not await heading.is_visible():
            return False
        if (await heading.inner_text()).strip() != _CLIENTS_LIST_HEADING:
            return False
        create_action = page.locator(f"text={_CLIENTS_CREATE_CTA}")
        return await create_action.count() >= 1 and await create_action.is_visible()
    except Exception:
        return False


async def _has_bank_accounts_list_signature(page: LoginPage) -> bool:
    """Verify the research105 bank accounts list heading and connect CTA without clicking."""

    try:
        heading = page.locator("h1")
        if await heading.count() < 1 or not await heading.is_visible():
            return False
        if (await heading.inner_text()).strip() != _BANK_ACCOUNTS_LIST_HEADING:
            return False
        connect_action = page.locator(f"text={_BANK_ACCOUNTS_CONNECT_CTA}")
        return await connect_action.count() >= 1 and await connect_action.is_visible()
    except Exception:
        return False


async def _has_quotes_list_signature(page: LoginPage) -> bool:
    """Verify the research106 quotes list heading and create CTA without clicking."""

    try:
        heading = page.locator("h1")
        if await heading.count() < 1 or not await heading.is_visible():
            return False
        if (await heading.inner_text()).strip() != _QUOTES_LIST_HEADING:
            return False
        create_action = page.locator(f"text={_QUOTES_CREATE_CTA}")
        return await create_action.count() >= 1 and await create_action.is_visible()
    except Exception:
        return False


async def _has_recurring_invoices_list_signature(page: LoginPage) -> bool:
    """Verify the research107 recurring invoices list heading and create CTA without clicking."""

    try:
        heading = page.locator("h1")
        if await heading.count() < 1 or not await heading.is_visible():
            return False
        if (await heading.inner_text()).strip() != _RECURRING_INVOICES_LIST_HEADING:
            return False
        create_action = page.locator(f"text={_RECURRING_INVOICES_CREATE_CTA}")
        return await create_action.count() >= 1 and await create_action.is_visible()
    except Exception:
        return False


async def _has_products_import_signature(page: LoginPage) -> bool:
    """Verify the research108 products import heading and choose-CSV control without clicking."""

    try:
        heading = page.locator("h1")
        if await heading.count() < 1 or not await heading.is_visible():
            return False
        if (await heading.inner_text()).strip() != _PRODUCTS_IMPORT_HEADING:
            return False
        choose_csv = page.locator(f"text={_PRODUCTS_IMPORT_CHOOSE_CSV_CTA}")
        return await choose_csv.count() >= 1 and await choose_csv.is_visible()
    except Exception:
        return False


async def _has_error_shell_markers(page: LoginPage) -> bool:
    """Detect Billy error shells (for example Upsedasse) without echoing page text."""

    try:
        for selector in _ERROR_SHELL_MARKERS:
            control = page.locator(selector)
            if await control.count() >= 1 and await control.is_visible():
                return True
        return False
    except Exception:
        return False


async def _has_interaction_challenge(page: LoginPage) -> bool:
    """Detect captcha/MFA-style controls without naming page content in errors."""

    try:
        for selector in _INTERACTION_CHALLENGE_SELECTORS:
            control = page.locator(selector)
            if await control.count() >= 1:
                return True
        return False
    except Exception:
        return False


async def _classify_session_page(page: LoginPage) -> AuthLoginWaitSuccess | ToolError | None:
    """Return a terminal classification, or None when the page is still settling."""

    if await _has_known_login_page(page):
        return AuthLoginWaitSuccess(status="AUTH_REQUIRED")
    if await _has_interaction_challenge(page):
        return ToolError(
            code=StableErrorCode.AUTH_INTERACTION_REQUIRED,
            message="Browser authentication requires a non-automatable challenge.",
        )
    if _is_dashboard_shell_url(page.url) and await _has_shell_nav_markers(page):
        if await _has_login_signature(page):
            return None
        return AuthLoginWaitSuccess(status="READY")
    # Login controls away from the fixed login URL, or an incomplete shell, are
    # treated as settling rather than hard drift until the wait timeout.
    return None


def _persist_org_slug_outside_git(url: str, destination: Path) -> None:
    """Store only the UI-derived org slug outside the repository for later equality checks."""

    try:
        parsed = urlsplit(url)
        match = _DASHBOARD_PATH.match(parsed.path or "")
        if match is None:
            return
        slug = (parsed.path or "").strip("/").split("/", 1)[0]
        if not slug or "/" in slug:
            return
        destination.parent.mkdir(parents=True, exist_ok=True)
        payload = {"source": "ui_dashboard_path", "org_slug": slug}
        destination.write_text(json.dumps(payload, sort_keys=True) + "\n", encoding="utf-8")
        try:
            destination.chmod(0o600)
        except OSError:
            pass
    except Exception:
        # Persistence is best-effort and must never change the tool result.
        return


def _ui_changed_error() -> ToolError:
    """Return the stable fail-closed result without echoing page or session values."""

    return ToolError(
        code=StableErrorCode.UI_CHANGED,
        message="Billy login interface no longer matches the recorded signature.",
    )


def _ui_invoices_changed_error() -> ToolError:
    """Fail closed when the invoices list shell no longer matches research102."""

    return ToolError(
        code=StableErrorCode.UI_CHANGED,
        message="Billy invoices list interface no longer matches the recorded signature.",
    )


def _ui_products_changed_error() -> ToolError:
    """Fail closed when the products list shell no longer matches research103."""

    return ToolError(
        code=StableErrorCode.UI_CHANGED,
        message="Billy products list interface no longer matches the recorded signature.",
    )


def _ui_clients_changed_error() -> ToolError:
    """Fail closed when the clients list shell no longer matches research104."""

    return ToolError(
        code=StableErrorCode.UI_CHANGED,
        message="Billy clients list interface no longer matches the recorded signature.",
    )


def _ui_bank_accounts_changed_error() -> ToolError:
    """Fail closed when the bank accounts list shell no longer matches research105."""

    return ToolError(
        code=StableErrorCode.UI_CHANGED,
        message="Billy bank accounts list interface no longer matches the recorded signature.",
    )


def _ui_quotes_changed_error() -> ToolError:
    """Fail closed when the quotes list shell no longer matches research106."""

    return ToolError(
        code=StableErrorCode.UI_CHANGED,
        message="Billy quotes list interface no longer matches the recorded signature.",
    )


def _ui_recurring_invoices_changed_error() -> ToolError:
    """Fail closed when the recurring invoices list shell no longer matches research107."""

    return ToolError(
        code=StableErrorCode.UI_CHANGED,
        message="Billy recurring invoices list interface no longer matches the recorded signature.",
    )


def _ui_products_import_changed_error() -> ToolError:
    """Fail closed when the products import shell no longer matches research108."""

    return ToolError(
        code=StableErrorCode.UI_CHANGED,
        message="Billy products import interface no longer matches the recorded signature.",
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
