"""Headless-only persistent Playwright runtime with deny-by-default egress."""

from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Callable, Iterable
from pathlib import Path
from typing import Literal, Protocol, cast
from urllib.parse import urlsplit

import yaml
from pydantic import BaseModel, ConfigDict, Field, ValidationError, field_validator, model_validator


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

    async def close(self) -> None: ...


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
        policy: BrowserEgressPolicy,
        *,
        launcher: PersistentContextLauncher | None = None,
    ) -> None:
        self._profile_path = profile_path.expanduser().resolve(strict=False)
        self._policy = policy
        self._launcher = launcher
        self._context: PersistentContext | None = None
        self._playwright_stopper: Callable[[], Awaitable[None]] | None = None
        self._lock = asyncio.Lock()

    async def start(self) -> PersistentContext:
        """Launch exactly one persistent context with headless mode forced on."""

        async with self._lock:
            if self._context is None:
                if self._launcher is None:
                    context, stopper = await _launch_persistent_context(
                        str(self._profile_path),
                        headless=True,
                        accept_downloads=False,
                    )
                    self._playwright_stopper = stopper
                else:
                    context = await self._launcher(
                        str(self._profile_path),
                        headless=True,
                        accept_downloads=False,
                    )
                await context.route("**/*", self._enforce_egress)
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

    async def _enforce_egress(self, route: BrowserRoute) -> None:
        if self._policy.allows(route.request.url):
            await route.continue_()
        else:
            await route.abort("blockedbyclient")


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
