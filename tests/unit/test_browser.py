from __future__ import annotations

import asyncio
import json
from pathlib import Path
from typing import cast

import pytest

from billy_mcp.browser import (
    BrowserEgressPolicy,
    BrowserEgressPolicyLoadError,
    BrowserRuntime,
    PersistentContext,
    RouteHandler,
)
from billy_mcp.models import AuthStatusSuccess, StableErrorCode, ToolError


class FakeRequest:
    def __init__(self, url: str) -> None:
        self.url = url


class FakeRoute:
    def __init__(self, url: str) -> None:
        self.request = FakeRequest(url)
        self.action = ""

    async def continue_(self) -> None:
        self.action = "continued"

    async def abort(self, error_code: str | None = None) -> None:
        self.action = f"aborted:{error_code}"


class FakeContext:
    def __init__(self) -> None:
        self.pattern = ""
        self.handler: RouteHandler | None = None
        self.closed = False

    async def route(self, url: str, handler: RouteHandler) -> None:
        self.pattern = url
        self.handler = handler

    async def close(self) -> None:
        self.closed = True


class FailingRouteContext(FakeContext):
    async def route(self, url: str, handler: RouteHandler) -> None:
        raise RuntimeError("route installation failed")


class FakeLoginControl:
    def __init__(self, *, count: int = 1, visible: bool = True, text: str = "") -> None:
        self._count = count
        self._visible = visible
        self._text = text

    async def count(self) -> int:
        return self._count

    async def is_visible(self) -> bool:
        return self._visible

    async def inner_text(self) -> str:
        return self._text


class FakeLoginPage:
    def __init__(
        self,
        *,
        final_url: str = "https://mit.billy.dk/login",
        controls: dict[str, FakeLoginControl] | None = None,
        goto_error: Exception | None = None,
    ) -> None:
        self.url = final_url
        self.controls = controls or {
            "input[type='email'][name='email']": FakeLoginControl(),
            "input[type='password'][name='password']": FakeLoginControl(),
            "input[type='checkbox'][name='remember']": FakeLoginControl(),
            "button[data-cy='login-button']": FakeLoginControl(text="Log in"),
        }
        self.goto_error = goto_error
        self.navigation: list[tuple[str, str]] = []
        self.closed = False

    async def goto(self, url: str, *, wait_until: str) -> object:
        self.navigation.append((url, wait_until))
        if self.goto_error is not None:
            raise self.goto_error
        return object()

    def locator(self, selector: str) -> FakeLoginControl:
        return self.controls.get(selector, FakeLoginControl(count=0, visible=False))

    async def close(self) -> None:
        self.closed = True


class FakeLoginContext(FakeContext):
    def __init__(self, page: FakeLoginPage) -> None:
        super().__init__()
        self.page = page

    async def new_page(self) -> FakeLoginPage:
        return self.page


class FailingLoginPage(FakeLoginPage):
    def locator(self, selector: str) -> FakeLoginControl:
        raise RuntimeError("login DOM changed")


async def invoke_handler(handler: RouteHandler, route: FakeRoute) -> None:
    await handler(route)


def write_browser_egress_fixture(tmp_path: Path, *, browser_action: str = "allow") -> Path:
    path = tmp_path / "browser_egress.yaml"
    path.write_text(
        json.dumps(
            {
                "manifest": "billy_browser_egress_phase_0",
                "schema_version": 1,
                "default_action": "deny",
                "hosts": [
                    {
                        "host": "mit.billy.dk",
                        "browser_action": browser_action,
                        "api_client_action": "deny",
                        "condition": "typed UI/auth workflow",
                        "evidence": "reviewed fixture",
                        "owner": "ui_auth",
                        "purpose": "headless authentication only",
                        "test_references": ["tests/unit/test_browser.py"],
                    },
                    {
                        "host": "api.billysbilling.com",
                        "browser_action": "deny",
                        "api_client_action": "exclusive_allow",
                        "condition": "not available to browser lane",
                        "evidence": "reviewed fixture",
                        "owner": "api_client",
                        "purpose": "locked official API destination",
                        "test_references": ["tests/unit/test_browser.py"],
                    },
                ],
            }
        ),
        encoding="utf-8",
    )
    return path


def test_browser_policy_loads_only_explicit_manifest_allow_hosts(tmp_path: Path) -> None:
    policy = BrowserEgressPolicy.from_manifest(write_browser_egress_fixture(tmp_path))

    assert policy.allowed_hosts == frozenset({"mit.billy.dk"})
    assert policy.allows("https://mit.billy.dk/")
    assert not policy.allows("https://api.billysbilling.com/v2/user")


def test_browser_policy_rejects_missing_manifest(tmp_path: Path) -> None:
    with pytest.raises(BrowserEgressPolicyLoadError, match="unavailable or invalid"):
        BrowserEgressPolicy.from_manifest(tmp_path / "browser_egress.yaml")


@pytest.mark.parametrize("browser_action", ["prompt", "deny"])
def test_browser_policy_rejects_unknown_or_no_allow_manifest_policy(
    tmp_path: Path, browser_action: str
) -> None:
    with pytest.raises(BrowserEgressPolicyLoadError, match="unavailable or invalid"):
        BrowserEgressPolicy.from_manifest(
            write_browser_egress_fixture(tmp_path, browser_action=browser_action)
        )


def test_browser_policy_rejects_malformed_manifest(tmp_path: Path) -> None:
    path = tmp_path / "browser_egress.yaml"
    path.write_text("hosts: [\n", encoding="utf-8")

    with pytest.raises(BrowserEgressPolicyLoadError, match="unavailable or invalid"):
        BrowserEgressPolicy.from_manifest(path)


def test_browser_forces_headless_and_denies_unknown_egress() -> None:
    context = FakeContext()
    launch_arguments: dict[str, object] = {}

    async def launcher(profile_path: str, **kwargs: bool) -> PersistentContext:
        launch_arguments["profile_path"] = profile_path
        launch_arguments.update(kwargs)
        return cast(PersistentContext, context)

    runtime = BrowserRuntime(
        profile_path=Path("/tmp/billy-profile"),
        launcher=launcher,
    )
    asyncio.run(runtime.start())

    assert launch_arguments["headless"] is True
    assert launch_arguments["accept_downloads"] is False
    assert context.pattern == "**/*"
    assert callable(context.handler)

    allowed = FakeRoute("https://mit.billy.dk/")
    wrong_port = FakeRoute("https://mit.billy.dk:444/")
    denied = FakeRoute("https://analytics.example/")
    handler = context.handler
    assert handler is not None
    asyncio.run(invoke_handler(handler, allowed))
    asyncio.run(invoke_handler(handler, wrong_port))
    asyncio.run(invoke_handler(handler, denied))

    assert allowed.action == "continued"
    assert wrong_port.action == "aborted:blockedbyclient"
    assert denied.action == "aborted:blockedbyclient"


def test_browser_runtime_fails_closed_before_launch_for_missing_manifest(tmp_path: Path) -> None:
    launched = False

    async def launcher(profile_path: str, **kwargs: bool) -> PersistentContext:
        nonlocal launched
        launched = True
        return cast(PersistentContext, FakeContext())

    runtime = BrowserRuntime(
        profile_path=tmp_path / "profile",
        egress_manifest_path=tmp_path / "missing.yaml",
        launcher=launcher,
    )

    with pytest.raises(BrowserEgressPolicyLoadError, match="unavailable or invalid"):
        asyncio.run(runtime.start())

    assert not launched


def test_browser_closes_context_when_egress_route_cannot_be_installed(tmp_path: Path) -> None:
    context = FailingRouteContext()

    async def launcher(profile_path: str, **kwargs: bool) -> PersistentContext:
        return cast(PersistentContext, context)

    runtime = BrowserRuntime(
        profile_path=tmp_path / "profile",
        egress_manifest_path=write_browser_egress_fixture(tmp_path),
        launcher=launcher,
    )

    with pytest.raises(RuntimeError, match="route installation failed"):
        asyncio.run(runtime.start())

    assert context.closed


@pytest.mark.parametrize("submit_label", ["Log in", "Log ind"])
def test_auth_status_returns_only_the_observed_login_state_in_headless_context(
    tmp_path: Path, submit_label: str
) -> None:
    page = FakeLoginPage(
        controls={
            "input[type='email'][name='email']": FakeLoginControl(),
            "input[type='password'][name='password']": FakeLoginControl(),
            "input[type='checkbox'][name='remember']": FakeLoginControl(),
            "button[data-cy='login-button']": FakeLoginControl(text=submit_label),
        }
    )
    context = FakeLoginContext(page)
    launch_arguments: dict[str, object] = {}

    async def launcher(profile_path: str, **kwargs: bool) -> PersistentContext:
        launch_arguments["profile_path"] = profile_path
        launch_arguments.update(kwargs)
        return cast(PersistentContext, context)

    runtime = BrowserRuntime(
        profile_path=tmp_path / "profile",
        egress_manifest_path=write_browser_egress_fixture(tmp_path),
        launcher=launcher,
    )

    result = asyncio.run(runtime.auth_status())

    assert result == AuthStatusSuccess()
    assert launch_arguments["headless"] is True
    assert launch_arguments["accept_downloads"] is False
    assert page.navigation == [("https://mit.billy.dk/", "domcontentloaded")]
    assert page.closed


@pytest.mark.parametrize(
    "final_url",
    [
        "https://mit.billy.dk/organizations",
        "https://mit.billy.dk/login?returnTo=%2F",
        "https://[malformed",
    ],
)
def test_auth_status_fails_closed_when_the_final_route_changes(
    tmp_path: Path, final_url: str
) -> None:
    page = FakeLoginPage(final_url=final_url)
    context = FakeLoginContext(page)

    async def launcher(profile_path: str, **kwargs: bool) -> PersistentContext:
        return cast(PersistentContext, context)

    runtime = BrowserRuntime(
        profile_path=tmp_path / "profile",
        egress_manifest_path=write_browser_egress_fixture(tmp_path),
        launcher=launcher,
    )

    result = asyncio.run(runtime.auth_status())

    assert isinstance(result, ToolError)
    assert result.code is StableErrorCode.UI_CHANGED
    assert result.details == {}
    assert page.closed


def test_auth_status_fails_closed_when_the_login_signature_changes(tmp_path: Path) -> None:
    page = FakeLoginPage(
        controls={
            "input[type='email'][name='email']": FakeLoginControl(),
            "input[type='password'][name='password']": FakeLoginControl(),
            "input[type='checkbox'][name='remember']": FakeLoginControl(),
            "button[data-cy='login-button']": FakeLoginControl(text="Continue"),
        }
    )
    context = FakeLoginContext(page)

    async def launcher(profile_path: str, **kwargs: bool) -> PersistentContext:
        return cast(PersistentContext, context)

    runtime = BrowserRuntime(
        profile_path=tmp_path / "profile",
        egress_manifest_path=write_browser_egress_fixture(tmp_path),
        launcher=launcher,
    )

    result = asyncio.run(runtime.auth_status())

    assert isinstance(result, ToolError)
    assert result.code is StableErrorCode.UI_CHANGED


def test_auth_status_fails_closed_when_login_control_reads_fail(tmp_path: Path) -> None:
    page = FailingLoginPage()
    context = FakeLoginContext(page)

    async def launcher(profile_path: str, **kwargs: bool) -> PersistentContext:
        return cast(PersistentContext, context)

    runtime = BrowserRuntime(
        profile_path=tmp_path / "profile",
        egress_manifest_path=write_browser_egress_fixture(tmp_path),
        launcher=launcher,
    )

    result = asyncio.run(runtime.auth_status())

    assert isinstance(result, ToolError)
    assert result.code is StableErrorCode.UI_CHANGED


def test_auth_status_does_not_echo_browser_session_or_credential_failures(tmp_path: Path) -> None:
    secret = "cookie=session-secret password=browser-secret"
    page = FakeLoginPage(goto_error=RuntimeError(secret))
    context = FakeLoginContext(page)

    async def launcher(profile_path: str, **kwargs: bool) -> PersistentContext:
        return cast(PersistentContext, context)

    runtime = BrowserRuntime(
        profile_path=tmp_path / "profile",
        egress_manifest_path=write_browser_egress_fixture(tmp_path),
        launcher=launcher,
    )

    result = asyncio.run(runtime.auth_status())

    assert isinstance(result, ToolError)
    assert result.code is StableErrorCode.BILLY_ERROR
    assert result.details == {}
    assert secret not in str(result.model_dump())
    assert page.closed
