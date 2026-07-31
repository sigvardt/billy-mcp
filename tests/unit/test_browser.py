from __future__ import annotations

import asyncio
import json
from collections.abc import Callable
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
from billy_mcp.credentials import BrowserCredentialReferences, CredentialReference
from billy_mcp.models import (
    AuthLoginStartSuccess,
    AuthLoginWaitSuccess,
    AuthStatusSuccess,
    StableErrorCode,
    ToolError,
    UiBankAccountsListSuccess,
    UiBankReconciliationOpenSuccess,
    UiBillsListSuccess,
    UiClientsListSuccess,
    UiCreditorBalancesListSuccess,
    UiDaybooksOpenSuccess,
    UiDebtorBalancesListSuccess,
    UiFinancingOpenSuccess,
    UiInvoicesListSuccess,
    UiProductsImportSuccess,
    UiProductsListSuccess,
    UiQuotesListSuccess,
    UiReceiptInboxListSuccess,
    UiRecurringInvoicesListSuccess,
    UiSuppliersListSuccess,
    UiUploadsListSuccess,
)


class FakeRequest:
    def __init__(self, url: str, method: str = "GET") -> None:
        self.url = url
        self.method = method


class FakeRoute:
    def __init__(self, url: str, method: str = "GET") -> None:
        self.request = FakeRequest(url, method=method)
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
    def __init__(
        self,
        *,
        count: int = 1,
        visible: bool = True,
        text: str = "",
        href: str | None = None,
        fill_error: Exception | None = None,
        click_error: Exception | None = None,
    ) -> None:
        self._count = count
        self._visible = visible
        self._text = text
        self._href = href
        self._fill_error = fill_error
        self._click_error = click_error
        self._events: list[str] | None = None
        self._selector = ""

    def bind(self, events: list[str], selector: str) -> None:
        self._events = events
        self._selector = selector

    @property
    def first(self) -> FakeLoginControl:
        """Playwright-style first match; fakes are already a single control."""

        return self

    def _record(self, action: str) -> None:
        if self._events is not None:
            self._events.append(f"{action}:{self._selector}")

    async def count(self) -> int:
        self._record("count")
        return self._count

    async def is_visible(self) -> bool:
        self._record("visible")
        return self._visible

    async def inner_text(self) -> str:
        self._record("text")
        return self._text

    async def fill(self, value: str) -> None:
        del value
        self._record("fill")
        if self._fill_error is not None:
            raise self._fill_error

    async def check(self) -> None:
        self._record("check")

    async def click(self) -> None:
        self._record("click")
        if self._click_error is not None:
            raise self._click_error

    async def get_attribute(self, name: str) -> str | None:
        self._record(f"get_attribute:{name}")
        if name == "href":
            return self._href
        return None


class FakeLoginPage:
    def __init__(
        self,
        *,
        final_url: str = "https://mit.billy.dk/login",
        controls: dict[str, FakeLoginControl] | None = None,
        goto_error: Exception | None = None,
        follow_goto: bool = False,
    ) -> None:
        self.url = final_url
        self.controls = controls or {
            "input[type='email'][name='email']": FakeLoginControl(),
            "input[type='password'][name='password']": FakeLoginControl(),
            "input[type='checkbox'][name='remember']": FakeLoginControl(),
            "button[data-cy='login-button']": FakeLoginControl(text="Log in"),
        }
        self.goto_error = goto_error
        self.follow_goto = follow_goto
        self.navigation: list[tuple[str, str]] = []
        self.events: list[str] = []
        self.closed = False
        for selector, control in self.controls.items():
            control.bind(self.events, selector)

    async def goto(self, url: str, *, wait_until: str) -> object:
        self.navigation.append((url, wait_until))
        self.events.append("goto")
        if self.goto_error is not None:
            raise self.goto_error
        if self.follow_goto:
            self.url = url
        return object()

    def locator(self, selector: str) -> FakeLoginControl:
        return self.controls.get(selector, FakeLoginControl(count=0, visible=False))

    async def close(self) -> None:
        self.closed = True

    async def wait_for_load_state(self, state: str, *, timeout: float | None = None) -> None:
        del state, timeout
        self.events.append("wait_for_load_state")


class FakeLoginContext(FakeContext):
    def __init__(self, page: FakeLoginPage) -> None:
        super().__init__()
        self.page = page

    async def new_page(self) -> FakeLoginPage:
        return self.page


class FailingLoginPage(FakeLoginPage):
    def locator(self, selector: str) -> FakeLoginControl:
        raise RuntimeError("login DOM changed")


class FakeCredentialResolver:
    def __init__(
        self,
        *,
        events: list[str] | None = None,
        failure: Exception | None = None,
        after_resolve: Callable[[int], None] | None = None,
        returns_none: bool = False,
    ) -> None:
        self.calls: list[str] = []
        self._events = events
        self._failure = failure
        self._after_resolve = after_resolve
        self._returns_none = returns_none

    def resolve(self, reference: CredentialReference) -> str | None:
        self.calls.append(reference.opaque_id)
        if self._events is not None:
            self._events.append(f"resolve:{reference.opaque_id}")
        if self._failure is not None:
            raise self._failure
        if self._after_resolve is not None:
            self._after_resolve(len(self.calls))
        if self._returns_none:
            return None
        return f"synthetic-{len(self.calls)}"


def browser_references() -> BrowserCredentialReferences:
    return BrowserCredentialReferences(
        primary=CredentialReference(opaque_id="opaque-primary-ref"),
        secondary=CredentialReference(opaque_id="opaque-secondary-ref"),
    )


async def invoke_handler(handler: RouteHandler, route: FakeRoute) -> None:
    await handler(route)


def write_browser_egress_fixture(
    tmp_path: Path,
    *,
    browser_action: str = "allow",
    api_browser_action: str = "path_allow",
) -> Path:
    path = tmp_path / "browser_egress.yaml"
    api_host: dict[str, object] = {
        "host": "api.billysbilling.com",
        "browser_action": api_browser_action,
        "api_client_action": "exclusive_allow",
        "condition": "browser auth/bootstrap paths only",
        "evidence": "reviewed fixture",
        "owner": "ui_auth",
        "purpose": "path-scoped login XHR",
        "test_references": ["tests/unit/test_browser.py"],
    }
    if api_browser_action == "path_allow":
        api_host["browser_path_allows"] = [
            {"match": "exact", "methods": ["POST"], "path": "/v2/user/login"},
            {"match": "exact", "methods": ["GET"], "path": "/v2/user"},
            {"match": "prefix", "methods": ["GET"], "path": "/v2/organizations/"},
        ]
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
                    api_host,
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
    assert policy.allows("https://api.billysbilling.com/v2/user/login", "POST")
    assert policy.allows("https://api.billysbilling.com/v2/user", "GET")
    assert not policy.allows("https://api.billysbilling.com/v2/user/login", "GET")
    assert not policy.allows("https://api.billysbilling.com/v2/invoices", "GET")


def test_browser_policy_rejects_missing_manifest(tmp_path: Path) -> None:
    with pytest.raises(BrowserEgressPolicyLoadError, match="unavailable or invalid"):
        BrowserEgressPolicy.from_manifest(tmp_path / "browser_egress.yaml")


@pytest.mark.parametrize(
    ("browser_action", "api_browser_action"),
    [("prompt", "deny"), ("deny", "deny")],
)
def test_browser_policy_rejects_unknown_or_no_allow_manifest_policy(
    tmp_path: Path, browser_action: str, api_browser_action: str
) -> None:
    with pytest.raises(BrowserEgressPolicyLoadError, match="unavailable or invalid"):
        BrowserEgressPolicy.from_manifest(
            write_browser_egress_fixture(
                tmp_path,
                browser_action=browser_action,
                api_browser_action=api_browser_action,
            )
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
    sensitive_value = "unreported-browser-state"
    page = FakeLoginPage(goto_error=RuntimeError(sensitive_value))
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
    assert sensitive_value not in str(result.model_dump())
    assert page.closed


@pytest.mark.parametrize("submit_label", ["Log in", "Log ind"])
def test_auth_login_start_resolves_only_after_validation_and_rechecks_before_actions(
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
    resolver = FakeCredentialResolver(events=page.events)
    launch_arguments: dict[str, object] = {}

    async def launcher(profile_path: str, **kwargs: bool) -> PersistentContext:
        launch_arguments["profile_path"] = profile_path
        launch_arguments.update(kwargs)
        return cast(PersistentContext, context)

    runtime = BrowserRuntime(
        profile_path=tmp_path / "profile",
        egress_manifest_path=write_browser_egress_fixture(tmp_path),
        launcher=launcher,
        credential_references=browser_references(),
        credential_resolver=resolver,
    )

    result = asyncio.run(runtime.auth_login_start())

    assert result == AuthLoginStartSuccess()
    assert launch_arguments["headless"] is True
    assert launch_arguments["accept_downloads"] is False
    assert resolver.calls == ["opaque-primary-ref", "opaque-secondary-ref"]
    assert page.navigation == [("https://mit.billy.dk/", "domcontentloaded")]
    assert page.events.index("resolve:opaque-primary-ref") > page.events.index(
        "text:button[data-cy='login-button']"
    )
    assert page.events.index("fill:input[type='email'][name='email']") > page.events.index(
        "resolve:opaque-secondary-ref"
    )
    assert page.events.index("fill:input[type='password'][name='password']") > page.events.index(
        "fill:input[type='email'][name='email']"
    )
    assert page.events.index("check:input[type='checkbox'][name='remember']") > page.events.index(
        "fill:input[type='password'][name='password']"
    )
    assert "click:button[data-cy='login-button']" in page.events
    assert page.events.index("click:button[data-cy='login-button']") > page.events.index(
        "check:input[type='checkbox'][name='remember']"
    )
    assert page.events.index("wait_for_load_state") > page.events.index(
        "click:button[data-cy='login-button']"
    )
    assert "fill:input[type='checkbox'][name='remember']" not in page.events
    assert page.events.count("count:input[type='email'][name='email']") == 5
    assert page.closed


def test_auth_login_start_returns_auth_required_without_resolver_or_action_for_missing_refs(
    tmp_path: Path,
) -> None:
    page = FakeLoginPage()
    context = FakeLoginContext(page)
    resolver = FakeCredentialResolver(events=page.events)

    async def launcher(profile_path: str, **kwargs: bool) -> PersistentContext:
        return cast(PersistentContext, context)

    runtime = BrowserRuntime(
        profile_path=tmp_path / "profile",
        egress_manifest_path=write_browser_egress_fixture(tmp_path),
        launcher=launcher,
        credential_references=BrowserCredentialReferences(),
        credential_resolver=resolver,
    )

    result = asyncio.run(runtime.auth_login_start())

    assert isinstance(result, ToolError)
    assert result.code is StableErrorCode.AUTH_REQUIRED
    assert result.details == {}
    assert resolver.calls == []
    assert not any(event.startswith(("fill:", "click:")) for event in page.events)
    assert page.closed


def test_auth_login_start_redacts_resolver_failure_and_closes_page(tmp_path: Path) -> None:
    page = FakeLoginPage()
    context = FakeLoginContext(page)
    unreported_value = "unreported-resolver-value"
    resolver = FakeCredentialResolver(events=page.events, failure=RuntimeError(unreported_value))

    async def launcher(profile_path: str, **kwargs: bool) -> PersistentContext:
        return cast(PersistentContext, context)

    runtime = BrowserRuntime(
        profile_path=tmp_path / "profile",
        egress_manifest_path=write_browser_egress_fixture(tmp_path),
        launcher=launcher,
        credential_references=browser_references(),
        credential_resolver=resolver,
    )

    result = asyncio.run(runtime.auth_login_start())

    assert isinstance(result, ToolError)
    assert result.code is StableErrorCode.AUTH_REQUIRED
    assert result.details == {}
    assert unreported_value not in str(result.model_dump())
    assert resolver.calls == ["opaque-primary-ref"]
    assert not any(event.startswith(("fill:", "click:")) for event in page.events)
    assert page.closed


def test_auth_login_start_returns_auth_required_for_unresolvable_reference(tmp_path: Path) -> None:
    page = FakeLoginPage()
    context = FakeLoginContext(page)
    resolver = FakeCredentialResolver(events=page.events, returns_none=True)

    async def launcher(profile_path: str, **kwargs: bool) -> PersistentContext:
        return cast(PersistentContext, context)

    runtime = BrowserRuntime(
        profile_path=tmp_path / "profile",
        egress_manifest_path=write_browser_egress_fixture(tmp_path),
        launcher=launcher,
        credential_references=browser_references(),
        credential_resolver=resolver,
    )

    result = asyncio.run(runtime.auth_login_start())

    assert isinstance(result, ToolError)
    assert result.code is StableErrorCode.AUTH_REQUIRED
    assert result.details == {}
    assert resolver.calls == ["opaque-primary-ref"]
    assert not any(event.startswith(("fill:", "click:")) for event in page.events)
    assert page.closed


@pytest.mark.parametrize("drift", ["route", "duplicate", "hidden", "missing", "legacy_page_title"])
def test_auth_login_start_rejects_signature_drift_before_resolution(
    tmp_path: Path, drift: str
) -> None:
    controls = {
        "input[type='email'][name='email']": FakeLoginControl(),
        "input[type='password'][name='password']": FakeLoginControl(),
        "input[type='checkbox'][name='remember']": FakeLoginControl(),
        "button[data-cy='login-button']": FakeLoginControl(text="Log in"),
    }
    final_url = "https://mit.billy.dk/login"
    if drift == "route":
        final_url = "https://mit.billy.dk/unknown"
    elif drift == "duplicate":
        controls["input[type='email'][name='email']"] = FakeLoginControl(count=2)
    elif drift == "hidden":
        controls["input[type='password'][name='password']"] = FakeLoginControl(visible=False)
    elif drift == "missing":
        controls["input[type='checkbox'][name='remember']"] = FakeLoginControl(count=0)
    else:
        controls["button[data-cy='login-button']"] = FakeLoginControl(text="Login")
    page = FakeLoginPage(final_url=final_url, controls=controls)
    context = FakeLoginContext(page)
    resolver = FakeCredentialResolver(events=page.events)

    async def launcher(profile_path: str, **kwargs: bool) -> PersistentContext:
        return cast(PersistentContext, context)

    runtime = BrowserRuntime(
        profile_path=tmp_path / "profile",
        egress_manifest_path=write_browser_egress_fixture(tmp_path),
        launcher=launcher,
        credential_references=browser_references(),
        credential_resolver=resolver,
    )

    result = asyncio.run(runtime.auth_login_start())

    assert isinstance(result, ToolError)
    assert result.code is StableErrorCode.UI_CHANGED
    assert resolver.calls == []
    assert not any(event.startswith(("fill:", "click:")) for event in page.events)
    assert page.closed


def test_auth_login_start_rechecks_signature_after_resolution_before_fill(tmp_path: Path) -> None:
    page = FakeLoginPage()
    context = FakeLoginContext(page)

    def change_route_after_second_resolution(call_count: int) -> None:
        if call_count == 2:
            page.url = "https://mit.billy.dk/unknown"

    resolver = FakeCredentialResolver(
        events=page.events,
        after_resolve=change_route_after_second_resolution,
    )

    async def launcher(profile_path: str, **kwargs: bool) -> PersistentContext:
        return cast(PersistentContext, context)

    runtime = BrowserRuntime(
        profile_path=tmp_path / "profile",
        egress_manifest_path=write_browser_egress_fixture(tmp_path),
        launcher=launcher,
        credential_references=browser_references(),
        credential_resolver=resolver,
    )

    result = asyncio.run(runtime.auth_login_start())

    assert isinstance(result, ToolError)
    assert result.code is StableErrorCode.UI_CHANGED
    assert resolver.calls == ["opaque-primary-ref", "opaque-secondary-ref"]
    assert not any(event.startswith(("fill:", "click:")) for event in page.events)
    assert page.closed


def test_auth_login_start_reports_egress_denied_without_launch_or_resolution(
    tmp_path: Path,
) -> None:
    launched = False
    resolver = FakeCredentialResolver()

    async def launcher(profile_path: str, **kwargs: bool) -> PersistentContext:
        nonlocal launched
        launched = True
        return cast(PersistentContext, FakeContext())

    runtime = BrowserRuntime(
        profile_path=tmp_path / "profile",
        egress_manifest_path=tmp_path / "missing.yaml",
        launcher=launcher,
        credential_references=browser_references(),
        credential_resolver=resolver,
    )

    result = asyncio.run(runtime.auth_login_start())

    assert isinstance(result, ToolError)
    assert result.code is StableErrorCode.EGRESS_DENIED
    assert not launched
    assert resolver.calls == []


def test_auth_login_start_redacts_unexpected_runtime_failure_and_closes_page(
    tmp_path: Path,
) -> None:
    unreported_value = "unreported-browser-value"
    page = FakeLoginPage(
        controls={
            "input[type='email'][name='email']": FakeLoginControl(),
            "input[type='password'][name='password']": FakeLoginControl(),
            "input[type='checkbox'][name='remember']": FakeLoginControl(),
            "button[data-cy='login-button']": FakeLoginControl(
                text="Log in", click_error=RuntimeError(unreported_value)
            ),
        }
    )
    context = FakeLoginContext(page)
    resolver = FakeCredentialResolver(events=page.events)

    async def launcher(profile_path: str, **kwargs: bool) -> PersistentContext:
        return cast(PersistentContext, context)

    runtime = BrowserRuntime(
        profile_path=tmp_path / "profile",
        egress_manifest_path=write_browser_egress_fixture(tmp_path),
        launcher=launcher,
        credential_references=browser_references(),
        credential_resolver=resolver,
    )

    result = asyncio.run(runtime.auth_login_start())

    assert isinstance(result, ToolError)
    assert result.code is StableErrorCode.BILLY_ERROR
    assert result.details == {}
    assert unreported_value not in str(result.model_dump())
    assert page.closed


def test_browser_policy_path_allow_denies_unlisted_api_methods(tmp_path: Path) -> None:
    policy = BrowserEgressPolicy.from_manifest(write_browser_egress_fixture(tmp_path))

    assert not policy.allows("https://api.billysbilling.com/v2/user", "DELETE")
    assert not policy.allows("http://api.billysbilling.com/v2/user/login", "POST")


def test_auth_login_wait_observes_only_the_existing_known_login_state(tmp_path: Path) -> None:
    page = FakeLoginPage()
    context = FakeLoginContext(page)
    resolver = FakeCredentialResolver(events=page.events)

    async def launcher(profile_path: str, **kwargs: bool) -> PersistentContext:
        return cast(PersistentContext, context)

    runtime = BrowserRuntime(
        profile_path=tmp_path / "profile",
        egress_manifest_path=write_browser_egress_fixture(tmp_path),
        launcher=launcher,
        credential_references=browser_references(),
        credential_resolver=resolver,
    )

    result = asyncio.run(runtime.auth_login_wait())

    assert result == AuthLoginWaitSuccess(status="AUTH_REQUIRED")
    assert resolver.calls == []
    assert page.closed


def test_auth_login_wait_returns_ready_for_dashboard_shell(tmp_path: Path) -> None:
    identity_path = tmp_path / "ui-org-identity.json"
    page = FakeLoginPage(
        final_url="https://mit.billy.dk/test-org-slug/dashboard",
        controls={
            "input[type='email'][name='email']": FakeLoginControl(count=0, visible=False),
            "input[type='password'][name='password']": FakeLoginControl(count=0, visible=False),
            "input[type='checkbox'][name='remember']": FakeLoginControl(count=0, visible=False),
            "button[data-cy='login-button']": FakeLoginControl(count=0, visible=False),
            "text=Overblik": FakeLoginControl(text="Overblik"),
            "text=Menu": FakeLoginControl(text="Menu"),
        },
    )
    context = FakeLoginContext(page)

    async def launcher(profile_path: str, **kwargs: bool) -> PersistentContext:
        return cast(PersistentContext, context)

    runtime = BrowserRuntime(
        profile_path=tmp_path / "profile",
        egress_manifest_path=write_browser_egress_fixture(tmp_path),
        launcher=launcher,
        org_identity_path=identity_path,
    )

    result = asyncio.run(runtime.auth_login_wait())

    assert result == AuthLoginWaitSuccess(status="READY")
    assert page.closed
    stored = json.loads(identity_path.read_text(encoding="utf-8"))
    assert stored == {"source": "ui_dashboard_path", "org_slug": "test-org-slug"}


def test_auth_login_wait_returns_interaction_required_for_challenge(tmp_path: Path) -> None:
    page = FakeLoginPage(
        final_url="https://mit.billy.dk/login",
        controls={
            "input[type='email'][name='email']": FakeLoginControl(count=0, visible=False),
            "input[type='password'][name='password']": FakeLoginControl(count=0, visible=False),
            "input[type='checkbox'][name='remember']": FakeLoginControl(count=0, visible=False),
            "button[data-cy='login-button']": FakeLoginControl(count=0, visible=False),
            "iframe[src*='recaptcha']": FakeLoginControl(count=1, visible=True),
        },
    )
    context = FakeLoginContext(page)

    async def launcher(profile_path: str, **kwargs: bool) -> PersistentContext:
        return cast(PersistentContext, context)

    runtime = BrowserRuntime(
        profile_path=tmp_path / "profile",
        egress_manifest_path=write_browser_egress_fixture(tmp_path),
        launcher=launcher,
    )

    result = asyncio.run(runtime.auth_login_wait())

    assert isinstance(result, ToolError)
    assert result.code is StableErrorCode.AUTH_INTERACTION_REQUIRED


def test_auth_login_wait_returns_ui_changed_for_unreviewed_state(tmp_path: Path) -> None:
    page = FakeLoginPage(final_url="https://mit.billy.dk/unknown")
    context = FakeLoginContext(page)
    resolver = FakeCredentialResolver(events=page.events)

    async def launcher(profile_path: str, **kwargs: bool) -> PersistentContext:
        return cast(PersistentContext, context)

    runtime = BrowserRuntime(
        profile_path=tmp_path / "profile",
        egress_manifest_path=write_browser_egress_fixture(tmp_path),
        launcher=launcher,
        credential_references=browser_references(),
        credential_resolver=resolver,
    )

    result = asyncio.run(runtime.auth_login_wait())

    assert isinstance(result, ToolError)
    assert result.code is StableErrorCode.UI_CHANGED
    assert resolver.calls == []
    assert page.closed


def _invoices_shell_controls() -> dict[str, FakeLoginControl]:
    return {
        "input[type='email'][name='email']": FakeLoginControl(count=0, visible=False),
        "input[type='password'][name='password']": FakeLoginControl(count=0, visible=False),
        "input[type='checkbox'][name='remember']": FakeLoginControl(count=0, visible=False),
        "button[data-cy='login-button']": FakeLoginControl(count=0, visible=False),
        "h1": FakeLoginControl(text="Fakturaer"),
        "text=Opret faktura": FakeLoginControl(text="Opret faktura"),
        "text=Overblik": FakeLoginControl(text="Overblik"),
        "text=Menu": FakeLoginControl(text="Menu"),
        "text=Upsedasse!": FakeLoginControl(count=0, visible=False),
        "text=Upsedasse": FakeLoginControl(count=0, visible=False),
        "text=Log ind igen": FakeLoginControl(count=0, visible=False),
    }


def test_ui_invoices_list_accepts_list_url_with_query_params(tmp_path: Path) -> None:
    identity_path = tmp_path / "ui-org-identity.json"
    identity_path.write_text(
        json.dumps({"source": "ui_dashboard_path", "org_slug": "test-org-slug"}) + "\n",
        encoding="utf-8",
    )
    page = FakeLoginPage(
        final_url=(
            "https://mit.billy.dk/test-org-slug/invoices"
            "?page=1&pageSize=50&sortDirection=DESC&status=all"
        ),
        controls=_invoices_shell_controls(),
        follow_goto=True,
    )
    # After product goto, keep Billy's query-bearing list URL (research live shape).
    original_goto = page.goto

    async def goto_keep_query(url: str, *, wait_until: str) -> object:
        result = await original_goto(url, wait_until=wait_until)
        if url.rstrip("/").endswith("/invoices"):
            page.url = (
                "https://mit.billy.dk/test-org-slug/invoices"
                "?page=1&pageSize=50&sortDirection=DESC&status=all"
            )
        return result

    page.goto = goto_keep_query  # type: ignore[method-assign]
    context = FakeLoginContext(page)

    async def launcher(profile_path: str, **kwargs: bool) -> PersistentContext:
        return cast(PersistentContext, context)

    runtime = BrowserRuntime(
        profile_path=tmp_path / "profile",
        egress_manifest_path=write_browser_egress_fixture(tmp_path),
        launcher=launcher,
        org_identity_path=identity_path,
    )

    result = asyncio.run(runtime.ui_invoices_list())

    assert result == UiInvoicesListSuccess(
        create_action_visible=True,
        shell_markers_present=True,
    )


def test_ui_invoices_list_returns_auth_required_on_login_page(tmp_path: Path) -> None:
    page = FakeLoginPage()
    context = FakeLoginContext(page)

    async def launcher(profile_path: str, **kwargs: bool) -> PersistentContext:
        return cast(PersistentContext, context)

    runtime = BrowserRuntime(
        profile_path=tmp_path / "profile",
        egress_manifest_path=write_browser_egress_fixture(tmp_path),
        launcher=launcher,
    )

    result = asyncio.run(runtime.ui_invoices_list())

    assert isinstance(result, ToolError)
    assert result.code is StableErrorCode.AUTH_REQUIRED
    assert page.closed


def test_ui_invoices_list_returns_success_for_list_shell(tmp_path: Path) -> None:
    identity_path = tmp_path / "ui-org-identity.json"
    identity_path.write_text(
        json.dumps({"source": "ui_dashboard_path", "org_slug": "test-org-slug"}) + "\n",
        encoding="utf-8",
    )
    page = FakeLoginPage(
        final_url="https://mit.billy.dk/test-org-slug/dashboard",
        controls=_invoices_shell_controls(),
        follow_goto=True,
    )
    context = FakeLoginContext(page)

    async def launcher(profile_path: str, **kwargs: bool) -> PersistentContext:
        return cast(PersistentContext, context)

    runtime = BrowserRuntime(
        profile_path=tmp_path / "profile",
        egress_manifest_path=write_browser_egress_fixture(tmp_path),
        launcher=launcher,
        org_identity_path=identity_path,
    )

    result = asyncio.run(runtime.ui_invoices_list())

    assert result == UiInvoicesListSuccess(
        create_action_visible=True,
        shell_markers_present=True,
    )
    assert any(url.endswith("/invoices") for url, _ in page.navigation)
    assert "test-org-slug" not in str(result.model_dump())
    assert page.closed


def test_ui_invoices_list_returns_ui_changed_for_error_shell(tmp_path: Path) -> None:
    identity_path = tmp_path / "ui-org-identity.json"
    identity_path.write_text(
        json.dumps({"source": "ui_dashboard_path", "org_slug": "test-org-slug"}) + "\n",
        encoding="utf-8",
    )
    controls = _invoices_shell_controls()
    controls["h1"] = FakeLoginControl(text="Upsedasse!")
    controls["text=Opret faktura"] = FakeLoginControl(count=0, visible=False)
    controls["text=Upsedasse!"] = FakeLoginControl(text="Upsedasse!")
    page = FakeLoginPage(
        final_url="https://mit.billy.dk/test-org-slug/dashboard",
        controls=controls,
        follow_goto=True,
    )
    context = FakeLoginContext(page)

    async def launcher(profile_path: str, **kwargs: bool) -> PersistentContext:
        return cast(PersistentContext, context)

    runtime = BrowserRuntime(
        profile_path=tmp_path / "profile",
        egress_manifest_path=write_browser_egress_fixture(tmp_path),
        launcher=launcher,
        org_identity_path=identity_path,
    )

    result = asyncio.run(runtime.ui_invoices_list())

    assert isinstance(result, ToolError)
    assert result.code is StableErrorCode.UI_CHANGED
    assert "invoices list" in result.message
    assert "test-org-slug" not in str(result.model_dump())
    assert page.closed


def test_ui_invoices_list_returns_ui_changed_when_heading_missing(tmp_path: Path) -> None:
    identity_path = tmp_path / "ui-org-identity.json"
    identity_path.write_text(
        json.dumps({"source": "ui_dashboard_path", "org_slug": "test-org-slug"}) + "\n",
        encoding="utf-8",
    )
    controls = _invoices_shell_controls()
    controls["h1"] = FakeLoginControl(count=0, visible=False)
    page = FakeLoginPage(
        final_url="https://mit.billy.dk/test-org-slug/dashboard",
        controls=controls,
        follow_goto=True,
    )
    context = FakeLoginContext(page)

    async def launcher(profile_path: str, **kwargs: bool) -> PersistentContext:
        return cast(PersistentContext, context)

    runtime = BrowserRuntime(
        profile_path=tmp_path / "profile",
        egress_manifest_path=write_browser_egress_fixture(tmp_path),
        launcher=launcher,
        org_identity_path=identity_path,
    )

    result = asyncio.run(runtime.ui_invoices_list())

    assert isinstance(result, ToolError)
    assert result.code is StableErrorCode.UI_CHANGED
    assert page.closed


def _products_shell_controls() -> dict[str, FakeLoginControl]:
    return {
        "input[type='email'][name='email']": FakeLoginControl(count=0, visible=False),
        "input[type='password'][name='password']": FakeLoginControl(count=0, visible=False),
        "input[type='checkbox'][name='remember']": FakeLoginControl(count=0, visible=False),
        "button[data-cy='login-button']": FakeLoginControl(count=0, visible=False),
        "h1": FakeLoginControl(text="Produkter"),
        "[data-cy='search-button']": FakeLoginControl(text="Search"),
        "text=Overblik": FakeLoginControl(text="Overblik"),
        "text=Fakturering": FakeLoginControl(text="Fakturering"),
        "text=Menu": FakeLoginControl(text="Menu"),
        "text=Upsedasse!": FakeLoginControl(count=0, visible=False),
        "text=Upsedasse": FakeLoginControl(count=0, visible=False),
        "text=Log ind igen": FakeLoginControl(count=0, visible=False),
    }


def test_ui_products_list_returns_auth_required_on_login_page(tmp_path: Path) -> None:
    page = FakeLoginPage()
    context = FakeLoginContext(page)

    async def launcher(profile_path: str, **kwargs: bool) -> PersistentContext:
        return cast(PersistentContext, context)

    runtime = BrowserRuntime(
        profile_path=tmp_path / "profile",
        egress_manifest_path=write_browser_egress_fixture(tmp_path),
        launcher=launcher,
    )

    result = asyncio.run(runtime.ui_products_list())

    assert isinstance(result, ToolError)
    assert result.code is StableErrorCode.AUTH_REQUIRED
    assert page.closed


def test_ui_products_list_returns_success_for_list_shell(tmp_path: Path) -> None:
    identity_path = tmp_path / "ui-org-identity.json"
    identity_path.write_text(
        json.dumps({"source": "ui_dashboard_path", "org_slug": "test-org-slug"}) + "\n",
        encoding="utf-8",
    )
    page = FakeLoginPage(
        final_url="https://mit.billy.dk/test-org-slug/dashboard",
        controls=_products_shell_controls(),
        follow_goto=True,
    )
    context = FakeLoginContext(page)

    async def launcher(profile_path: str, **kwargs: bool) -> PersistentContext:
        return cast(PersistentContext, context)

    runtime = BrowserRuntime(
        profile_path=tmp_path / "profile",
        egress_manifest_path=write_browser_egress_fixture(tmp_path),
        launcher=launcher,
        org_identity_path=identity_path,
    )

    result = asyncio.run(runtime.ui_products_list())

    assert result == UiProductsListSuccess(
        search_control_visible=True,
        shell_markers_present=True,
    )
    assert any(url.endswith("/products") for url, _ in page.navigation)
    assert "test-org-slug" not in str(result.model_dump())
    assert page.closed


def test_ui_products_list_returns_ui_changed_for_error_shell(tmp_path: Path) -> None:
    identity_path = tmp_path / "ui-org-identity.json"
    identity_path.write_text(
        json.dumps({"source": "ui_dashboard_path", "org_slug": "test-org-slug"}) + "\n",
        encoding="utf-8",
    )
    controls = _products_shell_controls()
    controls["h1"] = FakeLoginControl(text="Upsedasse!")
    controls["[data-cy='search-button']"] = FakeLoginControl(count=0, visible=False)
    controls["text=Upsedasse!"] = FakeLoginControl(text="Upsedasse!")
    page = FakeLoginPage(
        final_url="https://mit.billy.dk/test-org-slug/dashboard",
        controls=controls,
        follow_goto=True,
    )
    context = FakeLoginContext(page)

    async def launcher(profile_path: str, **kwargs: bool) -> PersistentContext:
        return cast(PersistentContext, context)

    runtime = BrowserRuntime(
        profile_path=tmp_path / "profile",
        egress_manifest_path=write_browser_egress_fixture(tmp_path),
        launcher=launcher,
        org_identity_path=identity_path,
    )

    result = asyncio.run(runtime.ui_products_list())

    assert isinstance(result, ToolError)
    assert result.code is StableErrorCode.UI_CHANGED
    assert "products list" in result.message
    assert "test-org-slug" not in str(result.model_dump())
    assert page.closed


def test_ui_products_list_returns_ui_changed_when_heading_missing(tmp_path: Path) -> None:
    identity_path = tmp_path / "ui-org-identity.json"
    identity_path.write_text(
        json.dumps({"source": "ui_dashboard_path", "org_slug": "test-org-slug"}) + "\n",
        encoding="utf-8",
    )
    controls = _products_shell_controls()
    controls["h1"] = FakeLoginControl(count=0, visible=False)
    page = FakeLoginPage(
        final_url="https://mit.billy.dk/test-org-slug/dashboard",
        controls=controls,
        follow_goto=True,
    )
    context = FakeLoginContext(page)

    async def launcher(profile_path: str, **kwargs: bool) -> PersistentContext:
        return cast(PersistentContext, context)

    runtime = BrowserRuntime(
        profile_path=tmp_path / "profile",
        egress_manifest_path=write_browser_egress_fixture(tmp_path),
        launcher=launcher,
        org_identity_path=identity_path,
    )

    result = asyncio.run(runtime.ui_products_list())

    assert isinstance(result, ToolError)
    assert result.code is StableErrorCode.UI_CHANGED
    assert page.closed


def test_ui_products_list_accepts_list_url_with_query_params(tmp_path: Path) -> None:
    identity_path = tmp_path / "ui-org-identity.json"
    identity_path.write_text(
        json.dumps({"source": "ui_dashboard_path", "org_slug": "test-org-slug"}) + "\n",
        encoding="utf-8",
    )
    page = FakeLoginPage(
        final_url=(
            "https://mit.billy.dk/test-org-slug/products?page=1&pageSize=50&sortDirection=DESC"
        ),
        controls=_products_shell_controls(),
        follow_goto=True,
    )
    original_goto = page.goto

    async def goto_keep_query(url: str, *, wait_until: str) -> object:
        result = await original_goto(url, wait_until=wait_until)
        if url.rstrip("/").endswith("/products"):
            page.url = (
                "https://mit.billy.dk/test-org-slug/products?page=1&pageSize=50&sortDirection=DESC"
            )
        return result

    page.goto = goto_keep_query  # type: ignore[method-assign]
    context = FakeLoginContext(page)

    async def launcher(profile_path: str, **kwargs: bool) -> PersistentContext:
        return cast(PersistentContext, context)

    runtime = BrowserRuntime(
        profile_path=tmp_path / "profile",
        egress_manifest_path=write_browser_egress_fixture(tmp_path),
        launcher=launcher,
        org_identity_path=identity_path,
    )

    result = asyncio.run(runtime.ui_products_list())

    assert result == UiProductsListSuccess(
        search_control_visible=True,
        shell_markers_present=True,
    )


def _clients_shell_controls() -> dict[str, FakeLoginControl]:
    return {
        "input[type='email'][name='email']": FakeLoginControl(count=0, visible=False),
        "input[type='password'][name='password']": FakeLoginControl(count=0, visible=False),
        "input[type='checkbox'][name='remember']": FakeLoginControl(count=0, visible=False),
        "button[data-cy='login-button']": FakeLoginControl(count=0, visible=False),
        "h1": FakeLoginControl(text="Kunder"),
        "text=Opret kontakt": FakeLoginControl(text="Opret kontakt"),
        "text=Overblik": FakeLoginControl(text="Overblik"),
        "text=Fakturering": FakeLoginControl(text="Fakturering"),
        "text=Menu": FakeLoginControl(text="Menu"),
        "text=Upsedasse!": FakeLoginControl(count=0, visible=False),
        "text=Upsedasse": FakeLoginControl(count=0, visible=False),
        "text=Log ind igen": FakeLoginControl(count=0, visible=False),
    }


def test_ui_clients_list_returns_auth_required_on_login_page(tmp_path: Path) -> None:
    page = FakeLoginPage()
    context = FakeLoginContext(page)

    async def launcher(profile_path: str, **kwargs: bool) -> PersistentContext:
        return cast(PersistentContext, context)

    runtime = BrowserRuntime(
        profile_path=tmp_path / "profile",
        egress_manifest_path=write_browser_egress_fixture(tmp_path),
        launcher=launcher,
    )

    result = asyncio.run(runtime.ui_clients_list())

    assert isinstance(result, ToolError)
    assert result.code is StableErrorCode.AUTH_REQUIRED
    assert page.closed


def test_ui_clients_list_returns_success_for_list_shell(tmp_path: Path) -> None:
    identity_path = tmp_path / "ui-org-identity.json"
    identity_path.write_text(
        json.dumps({"source": "ui_dashboard_path", "org_slug": "test-org-slug"}) + "\n",
        encoding="utf-8",
    )
    page = FakeLoginPage(
        final_url="https://mit.billy.dk/test-org-slug/dashboard",
        controls=_clients_shell_controls(),
        follow_goto=True,
    )
    context = FakeLoginContext(page)

    async def launcher(profile_path: str, **kwargs: bool) -> PersistentContext:
        return cast(PersistentContext, context)

    runtime = BrowserRuntime(
        profile_path=tmp_path / "profile",
        egress_manifest_path=write_browser_egress_fixture(tmp_path),
        launcher=launcher,
        org_identity_path=identity_path,
    )

    result = asyncio.run(runtime.ui_clients_list())

    assert result == UiClientsListSuccess(
        create_action_visible=True,
        shell_markers_present=True,
    )
    assert any(url.endswith("/clients") for url, _ in page.navigation)
    assert "test-org-slug" not in str(result.model_dump())
    assert page.closed


def test_ui_clients_list_returns_ui_changed_for_error_shell(tmp_path: Path) -> None:
    identity_path = tmp_path / "ui-org-identity.json"
    identity_path.write_text(
        json.dumps({"source": "ui_dashboard_path", "org_slug": "test-org-slug"}) + "\n",
        encoding="utf-8",
    )
    controls = _clients_shell_controls()
    controls["h1"] = FakeLoginControl(text="Upsedasse!")
    controls["text=Opret kontakt"] = FakeLoginControl(count=0, visible=False)
    controls["text=Upsedasse!"] = FakeLoginControl(text="Upsedasse!")
    page = FakeLoginPage(
        final_url="https://mit.billy.dk/test-org-slug/dashboard",
        controls=controls,
        follow_goto=True,
    )
    context = FakeLoginContext(page)

    async def launcher(profile_path: str, **kwargs: bool) -> PersistentContext:
        return cast(PersistentContext, context)

    runtime = BrowserRuntime(
        profile_path=tmp_path / "profile",
        egress_manifest_path=write_browser_egress_fixture(tmp_path),
        launcher=launcher,
        org_identity_path=identity_path,
    )

    result = asyncio.run(runtime.ui_clients_list())

    assert isinstance(result, ToolError)
    assert result.code is StableErrorCode.UI_CHANGED
    assert "clients list" in result.message
    assert "test-org-slug" not in str(result.model_dump())
    assert page.closed


def test_ui_clients_list_returns_ui_changed_when_heading_missing(tmp_path: Path) -> None:
    identity_path = tmp_path / "ui-org-identity.json"
    identity_path.write_text(
        json.dumps({"source": "ui_dashboard_path", "org_slug": "test-org-slug"}) + "\n",
        encoding="utf-8",
    )
    controls = _clients_shell_controls()
    controls["h1"] = FakeLoginControl(count=0, visible=False)
    page = FakeLoginPage(
        final_url="https://mit.billy.dk/test-org-slug/dashboard",
        controls=controls,
        follow_goto=True,
    )
    context = FakeLoginContext(page)

    async def launcher(profile_path: str, **kwargs: bool) -> PersistentContext:
        return cast(PersistentContext, context)

    runtime = BrowserRuntime(
        profile_path=tmp_path / "profile",
        egress_manifest_path=write_browser_egress_fixture(tmp_path),
        launcher=launcher,
        org_identity_path=identity_path,
    )

    result = asyncio.run(runtime.ui_clients_list())

    assert isinstance(result, ToolError)
    assert result.code is StableErrorCode.UI_CHANGED
    assert page.closed


def test_ui_clients_list_accepts_list_url_with_query_params(tmp_path: Path) -> None:
    identity_path = tmp_path / "ui-org-identity.json"
    identity_path.write_text(
        json.dumps({"source": "ui_dashboard_path", "org_slug": "test-org-slug"}) + "\n",
        encoding="utf-8",
    )
    page = FakeLoginPage(
        final_url=(
            "https://mit.billy.dk/test-org-slug/clients?page=1&pageSize=50&sortDirection=DESC"
        ),
        controls=_clients_shell_controls(),
        follow_goto=True,
    )
    original_goto = page.goto

    async def goto_keep_query(url: str, *, wait_until: str) -> object:
        result = await original_goto(url, wait_until=wait_until)
        if url.rstrip("/").endswith("/clients"):
            page.url = (
                "https://mit.billy.dk/test-org-slug/clients?page=1&pageSize=50&sortDirection=DESC"
            )
        return result

    page.goto = goto_keep_query  # type: ignore[method-assign]
    context = FakeLoginContext(page)

    async def launcher(profile_path: str, **kwargs: bool) -> PersistentContext:
        return cast(PersistentContext, context)

    runtime = BrowserRuntime(
        profile_path=tmp_path / "profile",
        egress_manifest_path=write_browser_egress_fixture(tmp_path),
        launcher=launcher,
        org_identity_path=identity_path,
    )

    result = asyncio.run(runtime.ui_clients_list())

    assert result == UiClientsListSuccess(
        create_action_visible=True,
        shell_markers_present=True,
    )


def _bank_accounts_shell_controls() -> dict[str, FakeLoginControl]:
    return {
        "input[type='email'][name='email']": FakeLoginControl(count=0, visible=False),
        "input[type='password'][name='password']": FakeLoginControl(count=0, visible=False),
        "input[type='checkbox'][name='remember']": FakeLoginControl(count=0, visible=False),
        "button[data-cy='login-button']": FakeLoginControl(count=0, visible=False),
        "h1": FakeLoginControl(text="Bankkonti"),
        "text=Forbind til bank": FakeLoginControl(text="Forbind til bank"),
        "text=Overblik": FakeLoginControl(text="Overblik"),
        "text=Fakturering": FakeLoginControl(text="Fakturering"),
        "text=Menu": FakeLoginControl(text="Menu"),
        "text=Upsedasse!": FakeLoginControl(count=0, visible=False),
        "text=Upsedasse": FakeLoginControl(count=0, visible=False),
        "text=Log ind igen": FakeLoginControl(count=0, visible=False),
    }


def test_ui_bank_accounts_list_returns_auth_required_on_login_page(tmp_path: Path) -> None:
    page = FakeLoginPage()
    context = FakeLoginContext(page)

    async def launcher(profile_path: str, **kwargs: bool) -> PersistentContext:
        return cast(PersistentContext, context)

    runtime = BrowserRuntime(
        profile_path=tmp_path / "profile",
        egress_manifest_path=write_browser_egress_fixture(tmp_path),
        launcher=launcher,
    )

    result = asyncio.run(runtime.ui_bank_accounts_list())

    assert isinstance(result, ToolError)
    assert result.code is StableErrorCode.AUTH_REQUIRED
    assert page.closed


def test_ui_bank_accounts_list_returns_success_for_list_shell(tmp_path: Path) -> None:
    identity_path = tmp_path / "ui-org-identity.json"
    identity_path.write_text(
        json.dumps({"source": "ui_dashboard_path", "org_slug": "test-org-slug"}) + "\n",
        encoding="utf-8",
    )
    page = FakeLoginPage(
        final_url="https://mit.billy.dk/test-org-slug/dashboard",
        controls=_bank_accounts_shell_controls(),
        follow_goto=True,
    )
    context = FakeLoginContext(page)

    async def launcher(profile_path: str, **kwargs: bool) -> PersistentContext:
        return cast(PersistentContext, context)

    runtime = BrowserRuntime(
        profile_path=tmp_path / "profile",
        egress_manifest_path=write_browser_egress_fixture(tmp_path),
        launcher=launcher,
        org_identity_path=identity_path,
    )

    result = asyncio.run(runtime.ui_bank_accounts_list())

    assert result == UiBankAccountsListSuccess(
        connect_bank_action_visible=True,
        shell_markers_present=True,
    )
    assert any(url.endswith("/bank-accounts") for url, _ in page.navigation)
    assert "test-org-slug" not in str(result.model_dump())
    assert page.closed


def test_ui_bank_accounts_list_returns_ui_changed_for_error_shell(tmp_path: Path) -> None:
    identity_path = tmp_path / "ui-org-identity.json"
    identity_path.write_text(
        json.dumps({"source": "ui_dashboard_path", "org_slug": "test-org-slug"}) + "\n",
        encoding="utf-8",
    )
    controls = _bank_accounts_shell_controls()
    controls["h1"] = FakeLoginControl(text="Upsedasse!")
    controls["text=Forbind til bank"] = FakeLoginControl(count=0, visible=False)
    controls["text=Upsedasse!"] = FakeLoginControl(text="Upsedasse!")
    page = FakeLoginPage(
        final_url="https://mit.billy.dk/test-org-slug/dashboard",
        controls=controls,
        follow_goto=True,
    )
    context = FakeLoginContext(page)

    async def launcher(profile_path: str, **kwargs: bool) -> PersistentContext:
        return cast(PersistentContext, context)

    runtime = BrowserRuntime(
        profile_path=tmp_path / "profile",
        egress_manifest_path=write_browser_egress_fixture(tmp_path),
        launcher=launcher,
        org_identity_path=identity_path,
    )

    result = asyncio.run(runtime.ui_bank_accounts_list())

    assert isinstance(result, ToolError)
    assert result.code is StableErrorCode.UI_CHANGED
    assert "bank accounts list" in result.message
    assert "test-org-slug" not in str(result.model_dump())
    assert page.closed


def test_ui_bank_accounts_list_returns_ui_changed_when_heading_missing(tmp_path: Path) -> None:
    identity_path = tmp_path / "ui-org-identity.json"
    identity_path.write_text(
        json.dumps({"source": "ui_dashboard_path", "org_slug": "test-org-slug"}) + "\n",
        encoding="utf-8",
    )
    controls = _bank_accounts_shell_controls()
    controls["h1"] = FakeLoginControl(count=0, visible=False)
    page = FakeLoginPage(
        final_url="https://mit.billy.dk/test-org-slug/dashboard",
        controls=controls,
        follow_goto=True,
    )
    context = FakeLoginContext(page)

    async def launcher(profile_path: str, **kwargs: bool) -> PersistentContext:
        return cast(PersistentContext, context)

    runtime = BrowserRuntime(
        profile_path=tmp_path / "profile",
        egress_manifest_path=write_browser_egress_fixture(tmp_path),
        launcher=launcher,
        org_identity_path=identity_path,
    )

    result = asyncio.run(runtime.ui_bank_accounts_list())

    assert isinstance(result, ToolError)
    assert result.code is StableErrorCode.UI_CHANGED
    assert page.closed


def test_ui_bank_accounts_list_accepts_list_url_with_query_params(tmp_path: Path) -> None:
    identity_path = tmp_path / "ui-org-identity.json"
    identity_path.write_text(
        json.dumps({"source": "ui_dashboard_path", "org_slug": "test-org-slug"}) + "\n",
        encoding="utf-8",
    )
    page = FakeLoginPage(
        final_url=(
            "https://mit.billy.dk/test-org-slug/bank-accounts?page=1&pageSize=50&sortDirection=DESC"
        ),
        controls=_bank_accounts_shell_controls(),
        follow_goto=True,
    )
    original_goto = page.goto

    async def goto_keep_query(url: str, *, wait_until: str) -> object:
        result = await original_goto(url, wait_until=wait_until)
        if url.rstrip("/").endswith("/bank-accounts"):
            page.url = (
                "https://mit.billy.dk/test-org-slug/bank-accounts"
                "?page=1&pageSize=50&sortDirection=DESC"
            )
        return result

    page.goto = goto_keep_query  # type: ignore[method-assign]
    context = FakeLoginContext(page)

    async def launcher(profile_path: str, **kwargs: bool) -> PersistentContext:
        return cast(PersistentContext, context)

    runtime = BrowserRuntime(
        profile_path=tmp_path / "profile",
        egress_manifest_path=write_browser_egress_fixture(tmp_path),
        launcher=launcher,
        org_identity_path=identity_path,
    )

    result = asyncio.run(runtime.ui_bank_accounts_list())

    assert result == UiBankAccountsListSuccess(
        connect_bank_action_visible=True,
        shell_markers_present=True,
    )


def _quotes_shell_controls() -> dict[str, FakeLoginControl]:
    return {
        "input[type='email'][name='email']": FakeLoginControl(count=0, visible=False),
        "input[type='password'][name='password']": FakeLoginControl(count=0, visible=False),
        "input[type='checkbox'][name='remember']": FakeLoginControl(count=0, visible=False),
        "button[data-cy='login-button']": FakeLoginControl(count=0, visible=False),
        "h1": FakeLoginControl(text="Tilbud"),
        "text=Opret tilbud": FakeLoginControl(text="Opret tilbud"),
        "text=Overblik": FakeLoginControl(text="Overblik"),
        "text=Fakturering": FakeLoginControl(text="Fakturering"),
        "text=Menu": FakeLoginControl(text="Menu"),
        "text=Upsedasse!": FakeLoginControl(count=0, visible=False),
        "text=Upsedasse": FakeLoginControl(count=0, visible=False),
        "text=Log ind igen": FakeLoginControl(count=0, visible=False),
    }


def _recurring_invoices_shell_controls() -> dict[str, FakeLoginControl]:
    return {
        "input[type='email'][name='email']": FakeLoginControl(count=0, visible=False),
        "input[type='password'][name='password']": FakeLoginControl(count=0, visible=False),
        "input[type='checkbox'][name='remember']": FakeLoginControl(count=0, visible=False),
        "button[data-cy='login-button']": FakeLoginControl(count=0, visible=False),
        "h1": FakeLoginControl(text="Abonnementer"),
        "text=Opret abonnement": FakeLoginControl(text="Opret abonnement"),
        "text=Overblik": FakeLoginControl(text="Overblik"),
        "text=Fakturering": FakeLoginControl(text="Fakturering"),
        "text=Menu": FakeLoginControl(text="Menu"),
        "text=Upsedasse!": FakeLoginControl(count=0, visible=False),
        "text=Upsedasse": FakeLoginControl(count=0, visible=False),
        "text=Log ind igen": FakeLoginControl(count=0, visible=False),
    }


def _products_import_shell_controls() -> dict[str, FakeLoginControl]:
    return {
        "input[type='email'][name='email']": FakeLoginControl(count=0, visible=False),
        "input[type='password'][name='password']": FakeLoginControl(count=0, visible=False),
        "input[type='checkbox'][name='remember']": FakeLoginControl(count=0, visible=False),
        "button[data-cy='login-button']": FakeLoginControl(count=0, visible=False),
        "h1": FakeLoginControl(text="Import af produkter"),
        "text=Vælg CSV-fil": FakeLoginControl(text="Vælg CSV-fil"),
        "text=Overblik": FakeLoginControl(text="Overblik"),
        "text=Fakturering": FakeLoginControl(text="Fakturering"),
        "text=Menu": FakeLoginControl(text="Menu"),
        "text=Upsedasse!": FakeLoginControl(count=0, visible=False),
        "text=Upsedasse": FakeLoginControl(count=0, visible=False),
        "text=Log ind igen": FakeLoginControl(count=0, visible=False),
    }


def test_ui_quotes_list_returns_auth_required_on_login_page(tmp_path: Path) -> None:
    page = FakeLoginPage()
    context = FakeLoginContext(page)

    async def launcher(profile_path: str, **kwargs: bool) -> PersistentContext:
        return cast(PersistentContext, context)

    runtime = BrowserRuntime(
        profile_path=tmp_path / "profile",
        egress_manifest_path=write_browser_egress_fixture(tmp_path),
        launcher=launcher,
    )

    result = asyncio.run(runtime.ui_quotes_list())

    assert isinstance(result, ToolError)
    assert result.code is StableErrorCode.AUTH_REQUIRED
    assert page.closed


def test_ui_quotes_list_returns_success_for_list_shell(tmp_path: Path) -> None:
    identity_path = tmp_path / "ui-org-identity.json"
    identity_path.write_text(
        json.dumps({"source": "ui_dashboard_path", "org_slug": "test-org-slug"}) + "\n",
        encoding="utf-8",
    )
    page = FakeLoginPage(
        final_url="https://mit.billy.dk/test-org-slug/dashboard",
        controls=_quotes_shell_controls(),
        follow_goto=True,
    )
    context = FakeLoginContext(page)

    async def launcher(profile_path: str, **kwargs: bool) -> PersistentContext:
        return cast(PersistentContext, context)

    runtime = BrowserRuntime(
        profile_path=tmp_path / "profile",
        egress_manifest_path=write_browser_egress_fixture(tmp_path),
        launcher=launcher,
        org_identity_path=identity_path,
    )

    result = asyncio.run(runtime.ui_quotes_list())

    assert result == UiQuotesListSuccess(
        create_action_visible=True,
        shell_markers_present=True,
    )
    assert any(url.endswith("/quotes") for url, _ in page.navigation)
    assert "test-org-slug" not in str(result.model_dump())
    assert page.closed


def test_ui_quotes_list_accepts_empty_path_suffix(tmp_path: Path) -> None:
    identity_path = tmp_path / "ui-org-identity.json"
    identity_path.write_text(
        json.dumps({"source": "ui_dashboard_path", "org_slug": "test-org-slug"}) + "\n",
        encoding="utf-8",
    )
    page = FakeLoginPage(
        final_url="https://mit.billy.dk/test-org-slug/dashboard",
        controls=_quotes_shell_controls(),
        follow_goto=True,
    )
    original_goto = page.goto

    async def goto_empty_state(url: str, *, wait_until: str) -> object:
        result = await original_goto(url, wait_until=wait_until)
        if url.rstrip("/").endswith("/quotes"):
            page.url = "https://mit.billy.dk/test-org-slug/quotes/empty"
        return result

    page.goto = goto_empty_state  # type: ignore[method-assign]
    context = FakeLoginContext(page)

    async def launcher(profile_path: str, **kwargs: bool) -> PersistentContext:
        return cast(PersistentContext, context)

    runtime = BrowserRuntime(
        profile_path=tmp_path / "profile",
        egress_manifest_path=write_browser_egress_fixture(tmp_path),
        launcher=launcher,
        org_identity_path=identity_path,
    )

    result = asyncio.run(runtime.ui_quotes_list())

    assert isinstance(result, UiQuotesListSuccess)
    assert result == UiQuotesListSuccess(
        create_action_visible=True,
        shell_markers_present=True,
    )
    assert result.path_class == "/:org_slug/quotes"


def test_ui_quotes_list_returns_ui_changed_for_error_shell(tmp_path: Path) -> None:
    identity_path = tmp_path / "ui-org-identity.json"
    identity_path.write_text(
        json.dumps({"source": "ui_dashboard_path", "org_slug": "test-org-slug"}) + "\n",
        encoding="utf-8",
    )
    controls = _quotes_shell_controls()
    controls["h1"] = FakeLoginControl(text="Upsedasse!")
    controls["text=Opret tilbud"] = FakeLoginControl(count=0, visible=False)
    controls["text=Upsedasse!"] = FakeLoginControl(text="Upsedasse!")
    page = FakeLoginPage(
        final_url="https://mit.billy.dk/test-org-slug/dashboard",
        controls=controls,
        follow_goto=True,
    )
    context = FakeLoginContext(page)

    async def launcher(profile_path: str, **kwargs: bool) -> PersistentContext:
        return cast(PersistentContext, context)

    runtime = BrowserRuntime(
        profile_path=tmp_path / "profile",
        egress_manifest_path=write_browser_egress_fixture(tmp_path),
        launcher=launcher,
        org_identity_path=identity_path,
    )

    result = asyncio.run(runtime.ui_quotes_list())

    assert isinstance(result, ToolError)
    assert result.code is StableErrorCode.UI_CHANGED
    assert "quotes list" in result.message
    assert "test-org-slug" not in str(result.model_dump())
    assert page.closed


def test_ui_quotes_list_returns_ui_changed_when_heading_missing(tmp_path: Path) -> None:
    identity_path = tmp_path / "ui-org-identity.json"
    identity_path.write_text(
        json.dumps({"source": "ui_dashboard_path", "org_slug": "test-org-slug"}) + "\n",
        encoding="utf-8",
    )
    controls = _quotes_shell_controls()
    controls["h1"] = FakeLoginControl(count=0, visible=False)
    page = FakeLoginPage(
        final_url="https://mit.billy.dk/test-org-slug/dashboard",
        controls=controls,
        follow_goto=True,
    )
    context = FakeLoginContext(page)

    async def launcher(profile_path: str, **kwargs: bool) -> PersistentContext:
        return cast(PersistentContext, context)

    runtime = BrowserRuntime(
        profile_path=tmp_path / "profile",
        egress_manifest_path=write_browser_egress_fixture(tmp_path),
        launcher=launcher,
        org_identity_path=identity_path,
    )

    result = asyncio.run(runtime.ui_quotes_list())

    assert isinstance(result, ToolError)
    assert result.code is StableErrorCode.UI_CHANGED
    assert page.closed


def test_ui_quotes_list_accepts_list_url_with_query_params(tmp_path: Path) -> None:
    identity_path = tmp_path / "ui-org-identity.json"
    identity_path.write_text(
        json.dumps({"source": "ui_dashboard_path", "org_slug": "test-org-slug"}) + "\n",
        encoding="utf-8",
    )
    page = FakeLoginPage(
        final_url=(
            "https://mit.billy.dk/test-org-slug/quotes?page=1&pageSize=50&sortDirection=DESC"
        ),
        controls=_quotes_shell_controls(),
        follow_goto=True,
    )
    original_goto = page.goto

    async def goto_keep_query(url: str, *, wait_until: str) -> object:
        result = await original_goto(url, wait_until=wait_until)
        if url.rstrip("/").endswith("/quotes"):
            page.url = (
                "https://mit.billy.dk/test-org-slug/quotes?page=1&pageSize=50&sortDirection=DESC"
            )
        return result

    page.goto = goto_keep_query  # type: ignore[method-assign]
    context = FakeLoginContext(page)

    async def launcher(profile_path: str, **kwargs: bool) -> PersistentContext:
        return cast(PersistentContext, context)

    runtime = BrowserRuntime(
        profile_path=tmp_path / "profile",
        egress_manifest_path=write_browser_egress_fixture(tmp_path),
        launcher=launcher,
        org_identity_path=identity_path,
    )

    result = asyncio.run(runtime.ui_quotes_list())

    assert result == UiQuotesListSuccess(
        create_action_visible=True,
        shell_markers_present=True,
    )


def test_ui_recurring_invoices_list_returns_auth_required_on_login_page(tmp_path: Path) -> None:
    page = FakeLoginPage()
    context = FakeLoginContext(page)

    async def launcher(profile_path: str, **kwargs: bool) -> PersistentContext:
        return cast(PersistentContext, context)

    runtime = BrowserRuntime(
        profile_path=tmp_path / "profile",
        egress_manifest_path=write_browser_egress_fixture(tmp_path),
        launcher=launcher,
    )

    result = asyncio.run(runtime.ui_recurring_invoices_list())

    assert isinstance(result, ToolError)
    assert result.code is StableErrorCode.AUTH_REQUIRED
    assert page.closed


def test_ui_recurring_invoices_list_returns_success_for_list_shell(tmp_path: Path) -> None:
    identity_path = tmp_path / "ui-org-identity.json"
    identity_path.write_text(
        json.dumps({"source": "ui_dashboard_path", "org_slug": "test-org-slug"}) + "\n",
        encoding="utf-8",
    )
    page = FakeLoginPage(
        final_url="https://mit.billy.dk/test-org-slug/dashboard",
        controls=_recurring_invoices_shell_controls(),
        follow_goto=True,
    )
    context = FakeLoginContext(page)

    async def launcher(profile_path: str, **kwargs: bool) -> PersistentContext:
        return cast(PersistentContext, context)

    runtime = BrowserRuntime(
        profile_path=tmp_path / "profile",
        egress_manifest_path=write_browser_egress_fixture(tmp_path),
        launcher=launcher,
        org_identity_path=identity_path,
    )

    result = asyncio.run(runtime.ui_recurring_invoices_list())

    assert result == UiRecurringInvoicesListSuccess(
        create_action_visible=True,
        shell_markers_present=True,
    )
    assert any(url.endswith("/recurring_invoices") for url, _ in page.navigation)
    assert "test-org-slug" not in str(result.model_dump())
    assert page.closed


def test_ui_recurring_invoices_list_accepts_empty_path_suffix(tmp_path: Path) -> None:
    identity_path = tmp_path / "ui-org-identity.json"
    identity_path.write_text(
        json.dumps({"source": "ui_dashboard_path", "org_slug": "test-org-slug"}) + "\n",
        encoding="utf-8",
    )
    page = FakeLoginPage(
        final_url="https://mit.billy.dk/test-org-slug/dashboard",
        controls=_recurring_invoices_shell_controls(),
        follow_goto=True,
    )
    original_goto = page.goto

    async def goto_empty_state(url: str, *, wait_until: str) -> object:
        result = await original_goto(url, wait_until=wait_until)
        if url.rstrip("/").endswith("/recurring_invoices"):
            page.url = "https://mit.billy.dk/test-org-slug/recurring_invoices/empty"
        return result

    page.goto = goto_empty_state  # type: ignore[method-assign]
    context = FakeLoginContext(page)

    async def launcher(profile_path: str, **kwargs: bool) -> PersistentContext:
        return cast(PersistentContext, context)

    runtime = BrowserRuntime(
        profile_path=tmp_path / "profile",
        egress_manifest_path=write_browser_egress_fixture(tmp_path),
        launcher=launcher,
        org_identity_path=identity_path,
    )

    result = asyncio.run(runtime.ui_recurring_invoices_list())

    assert isinstance(result, UiRecurringInvoicesListSuccess)
    assert result == UiRecurringInvoicesListSuccess(
        create_action_visible=True,
        shell_markers_present=True,
    )
    assert result.path_class == "/:org_slug/recurring_invoices"


def test_ui_recurring_invoices_list_returns_ui_changed_for_error_shell(tmp_path: Path) -> None:
    identity_path = tmp_path / "ui-org-identity.json"
    identity_path.write_text(
        json.dumps({"source": "ui_dashboard_path", "org_slug": "test-org-slug"}) + "\n",
        encoding="utf-8",
    )
    controls = _recurring_invoices_shell_controls()
    controls["h1"] = FakeLoginControl(text="Upsedasse!")
    controls["text=Opret abonnement"] = FakeLoginControl(count=0, visible=False)
    controls["text=Upsedasse!"] = FakeLoginControl(text="Upsedasse!")
    page = FakeLoginPage(
        final_url="https://mit.billy.dk/test-org-slug/dashboard",
        controls=controls,
        follow_goto=True,
    )
    context = FakeLoginContext(page)

    async def launcher(profile_path: str, **kwargs: bool) -> PersistentContext:
        return cast(PersistentContext, context)

    runtime = BrowserRuntime(
        profile_path=tmp_path / "profile",
        egress_manifest_path=write_browser_egress_fixture(tmp_path),
        launcher=launcher,
        org_identity_path=identity_path,
    )

    result = asyncio.run(runtime.ui_recurring_invoices_list())

    assert isinstance(result, ToolError)
    assert result.code is StableErrorCode.UI_CHANGED
    assert "recurring invoices list" in result.message
    assert "test-org-slug" not in str(result.model_dump())
    assert page.closed


def test_ui_recurring_invoices_list_returns_ui_changed_when_heading_missing(
    tmp_path: Path,
) -> None:
    identity_path = tmp_path / "ui-org-identity.json"
    identity_path.write_text(
        json.dumps({"source": "ui_dashboard_path", "org_slug": "test-org-slug"}) + "\n",
        encoding="utf-8",
    )
    controls = _recurring_invoices_shell_controls()
    controls["h1"] = FakeLoginControl(count=0, visible=False)
    page = FakeLoginPage(
        final_url="https://mit.billy.dk/test-org-slug/dashboard",
        controls=controls,
        follow_goto=True,
    )
    context = FakeLoginContext(page)

    async def launcher(profile_path: str, **kwargs: bool) -> PersistentContext:
        return cast(PersistentContext, context)

    runtime = BrowserRuntime(
        profile_path=tmp_path / "profile",
        egress_manifest_path=write_browser_egress_fixture(tmp_path),
        launcher=launcher,
        org_identity_path=identity_path,
    )

    result = asyncio.run(runtime.ui_recurring_invoices_list())

    assert isinstance(result, ToolError)
    assert result.code is StableErrorCode.UI_CHANGED
    assert page.closed


def test_ui_recurring_invoices_list_accepts_list_url_with_query_params(tmp_path: Path) -> None:
    identity_path = tmp_path / "ui-org-identity.json"
    identity_path.write_text(
        json.dumps({"source": "ui_dashboard_path", "org_slug": "test-org-slug"}) + "\n",
        encoding="utf-8",
    )
    page = FakeLoginPage(
        final_url=(
            "https://mit.billy.dk/test-org-slug/recurring_invoices"
            "?page=1&pageSize=50&sortDirection=DESC"
        ),
        controls=_recurring_invoices_shell_controls(),
        follow_goto=True,
    )
    original_goto = page.goto

    async def goto_keep_query(url: str, *, wait_until: str) -> object:
        result = await original_goto(url, wait_until=wait_until)
        if url.rstrip("/").endswith("/recurring_invoices"):
            page.url = (
                "https://mit.billy.dk/test-org-slug/recurring_invoices"
                "?page=1&pageSize=50&sortDirection=DESC"
            )
        return result

    page.goto = goto_keep_query  # type: ignore[method-assign]
    context = FakeLoginContext(page)

    async def launcher(profile_path: str, **kwargs: bool) -> PersistentContext:
        return cast(PersistentContext, context)

    runtime = BrowserRuntime(
        profile_path=tmp_path / "profile",
        egress_manifest_path=write_browser_egress_fixture(tmp_path),
        launcher=launcher,
        org_identity_path=identity_path,
    )

    result = asyncio.run(runtime.ui_recurring_invoices_list())

    assert result == UiRecurringInvoicesListSuccess(
        create_action_visible=True,
        shell_markers_present=True,
    )


def test_ui_products_import_returns_auth_required_on_login_page(tmp_path: Path) -> None:
    page = FakeLoginPage()
    context = FakeLoginContext(page)

    async def launcher(profile_path: str, **kwargs: bool) -> PersistentContext:
        return cast(PersistentContext, context)

    runtime = BrowserRuntime(
        profile_path=tmp_path / "profile",
        egress_manifest_path=write_browser_egress_fixture(tmp_path),
        launcher=launcher,
    )

    result = asyncio.run(runtime.ui_products_import())

    assert isinstance(result, ToolError)
    assert result.code is StableErrorCode.AUTH_REQUIRED
    assert page.closed


def test_ui_products_import_returns_success_for_import_shell(tmp_path: Path) -> None:
    identity_path = tmp_path / "ui-org-identity.json"
    identity_path.write_text(
        json.dumps({"source": "ui_dashboard_path", "org_slug": "test-org-slug"}) + "\n",
        encoding="utf-8",
    )
    page = FakeLoginPage(
        final_url="https://mit.billy.dk/test-org-slug/dashboard",
        controls=_products_import_shell_controls(),
        follow_goto=True,
    )
    context = FakeLoginContext(page)

    async def launcher(profile_path: str, **kwargs: bool) -> PersistentContext:
        return cast(PersistentContext, context)

    runtime = BrowserRuntime(
        profile_path=tmp_path / "profile",
        egress_manifest_path=write_browser_egress_fixture(tmp_path),
        launcher=launcher,
        org_identity_path=identity_path,
    )

    result = asyncio.run(runtime.ui_products_import())

    assert result == UiProductsImportSuccess(
        choose_csv_action_visible=True,
        shell_markers_present=True,
    )
    assert any(url.endswith("/products/import") for url, _ in page.navigation)
    assert "test-org-slug" not in str(result.model_dump())
    assert page.closed


def test_ui_products_import_returns_ui_changed_for_error_shell(tmp_path: Path) -> None:
    identity_path = tmp_path / "ui-org-identity.json"
    identity_path.write_text(
        json.dumps({"source": "ui_dashboard_path", "org_slug": "test-org-slug"}) + "\n",
        encoding="utf-8",
    )
    controls = _products_import_shell_controls()
    controls["h1"] = FakeLoginControl(text="Upsedasse!")
    controls["text=Vælg CSV-fil"] = FakeLoginControl(count=0, visible=False)
    controls["text=Upsedasse!"] = FakeLoginControl(text="Upsedasse!")
    page = FakeLoginPage(
        final_url="https://mit.billy.dk/test-org-slug/dashboard",
        controls=controls,
        follow_goto=True,
    )
    context = FakeLoginContext(page)

    async def launcher(profile_path: str, **kwargs: bool) -> PersistentContext:
        return cast(PersistentContext, context)

    runtime = BrowserRuntime(
        profile_path=tmp_path / "profile",
        egress_manifest_path=write_browser_egress_fixture(tmp_path),
        launcher=launcher,
        org_identity_path=identity_path,
    )

    result = asyncio.run(runtime.ui_products_import())

    assert isinstance(result, ToolError)
    assert result.code is StableErrorCode.UI_CHANGED
    assert "products import" in result.message
    assert "test-org-slug" not in str(result.model_dump())
    assert page.closed


def test_ui_products_import_returns_ui_changed_when_heading_missing(tmp_path: Path) -> None:
    identity_path = tmp_path / "ui-org-identity.json"
    identity_path.write_text(
        json.dumps({"source": "ui_dashboard_path", "org_slug": "test-org-slug"}) + "\n",
        encoding="utf-8",
    )
    controls = _products_import_shell_controls()
    controls["h1"] = FakeLoginControl(count=0, visible=False)
    page = FakeLoginPage(
        final_url="https://mit.billy.dk/test-org-slug/dashboard",
        controls=controls,
        follow_goto=True,
    )
    context = FakeLoginContext(page)

    async def launcher(profile_path: str, **kwargs: bool) -> PersistentContext:
        return cast(PersistentContext, context)

    runtime = BrowserRuntime(
        profile_path=tmp_path / "profile",
        egress_manifest_path=write_browser_egress_fixture(tmp_path),
        launcher=launcher,
        org_identity_path=identity_path,
    )

    result = asyncio.run(runtime.ui_products_import())

    assert isinstance(result, ToolError)
    assert result.code is StableErrorCode.UI_CHANGED
    assert page.closed


def test_ui_products_import_accepts_import_url_with_query_params(tmp_path: Path) -> None:
    identity_path = tmp_path / "ui-org-identity.json"
    identity_path.write_text(
        json.dumps({"source": "ui_dashboard_path", "org_slug": "test-org-slug"}) + "\n",
        encoding="utf-8",
    )
    page = FakeLoginPage(
        final_url="https://mit.billy.dk/test-org-slug/products/import?step=1",
        controls=_products_import_shell_controls(),
        follow_goto=True,
    )
    original_goto = page.goto

    async def goto_keep_query(url: str, *, wait_until: str) -> object:
        result = await original_goto(url, wait_until=wait_until)
        if url.rstrip("/").endswith("/products/import"):
            page.url = "https://mit.billy.dk/test-org-slug/products/import?step=1"
        return result

    page.goto = goto_keep_query  # type: ignore[method-assign]
    context = FakeLoginContext(page)

    async def launcher(profile_path: str, **kwargs: bool) -> PersistentContext:
        return cast(PersistentContext, context)

    runtime = BrowserRuntime(
        profile_path=tmp_path / "profile",
        egress_manifest_path=write_browser_egress_fixture(tmp_path),
        launcher=launcher,
        org_identity_path=identity_path,
    )

    result = asyncio.run(runtime.ui_products_import())

    assert result == UiProductsImportSuccess(
        choose_csv_action_visible=True,
        shell_markers_present=True,
    )


def _suppliers_shell_controls() -> dict[str, FakeLoginControl]:
    return {
        "input[type='email'][name='email']": FakeLoginControl(count=0, visible=False),
        "input[type='password'][name='password']": FakeLoginControl(count=0, visible=False),
        "input[type='checkbox'][name='remember']": FakeLoginControl(count=0, visible=False),
        "button[data-cy='login-button']": FakeLoginControl(count=0, visible=False),
        "h1": FakeLoginControl(text="Leverandører"),
        "text=Opret kontakt": FakeLoginControl(text="Opret kontakt"),
        "text=Overblik": FakeLoginControl(text="Overblik"),
        "text=Fakturering": FakeLoginControl(text="Fakturering"),
        "text=Menu": FakeLoginControl(text="Menu"),
        "text=Upsedasse!": FakeLoginControl(count=0, visible=False),
        "text=Upsedasse": FakeLoginControl(count=0, visible=False),
        "text=Log ind igen": FakeLoginControl(count=0, visible=False),
    }


def _bills_shell_controls() -> dict[str, FakeLoginControl]:
    return {
        "input[type='email'][name='email']": FakeLoginControl(count=0, visible=False),
        "input[type='password'][name='password']": FakeLoginControl(count=0, visible=False),
        "input[type='checkbox'][name='remember']": FakeLoginControl(count=0, visible=False),
        "button[data-cy='login-button']": FakeLoginControl(count=0, visible=False),
        "h1": FakeLoginControl(text="Køb"),
        "text=Opret køb": FakeLoginControl(text="Opret køb"),
        "text=Overblik": FakeLoginControl(text="Overblik"),
        "text=Fakturering": FakeLoginControl(text="Fakturering"),
        "text=Menu": FakeLoginControl(text="Menu"),
        "text=Upsedasse!": FakeLoginControl(count=0, visible=False),
        "text=Upsedasse": FakeLoginControl(count=0, visible=False),
        "text=Log ind igen": FakeLoginControl(count=0, visible=False),
    }


def _debtor_balances_shell_controls() -> dict[str, FakeLoginControl]:
    return {
        "input[type='email'][name='email']": FakeLoginControl(count=0, visible=False),
        "input[type='password'][name='password']": FakeLoginControl(count=0, visible=False),
        "input[type='checkbox'][name='remember']": FakeLoginControl(count=0, visible=False),
        "button[data-cy='login-button']": FakeLoginControl(count=0, visible=False),
        "h1": FakeLoginControl(text="Tilgodehavender"),
        "text=Opret faktura": FakeLoginControl(text="Opret faktura"),
        "text=Overblik": FakeLoginControl(text="Overblik"),
        "text=Fakturering": FakeLoginControl(text="Fakturering"),
        "text=Menu": FakeLoginControl(text="Menu"),
        "text=Upsedasse!": FakeLoginControl(count=0, visible=False),
        "text=Upsedasse": FakeLoginControl(count=0, visible=False),
        "text=Log ind igen": FakeLoginControl(count=0, visible=False),
    }


def _creditor_balances_shell_controls() -> dict[str, FakeLoginControl]:
    return {
        "input[type='email'][name='email']": FakeLoginControl(count=0, visible=False),
        "input[type='password'][name='password']": FakeLoginControl(count=0, visible=False),
        "input[type='checkbox'][name='remember']": FakeLoginControl(count=0, visible=False),
        "button[data-cy='login-button']": FakeLoginControl(count=0, visible=False),
        "h1": FakeLoginControl(text="Skyldige udgifter"),
        "text=Opret køb": FakeLoginControl(text="Opret køb"),
        "text=Overblik": FakeLoginControl(text="Overblik"),
        "text=Fakturering": FakeLoginControl(text="Fakturering"),
        "text=Menu": FakeLoginControl(text="Menu"),
        "text=Upsedasse!": FakeLoginControl(count=0, visible=False),
        "text=Upsedasse": FakeLoginControl(count=0, visible=False),
        "text=Log ind igen": FakeLoginControl(count=0, visible=False),
    }


def _uploads_shell_controls() -> dict[str, FakeLoginControl]:
    return {
        "input[type='email'][name='email']": FakeLoginControl(count=0, visible=False),
        "input[type='password'][name='password']": FakeLoginControl(count=0, visible=False),
        "input[type='checkbox'][name='remember']": FakeLoginControl(count=0, visible=False),
        "button[data-cy='login-button']": FakeLoginControl(count=0, visible=False),
        "h1": FakeLoginControl(text="Bilag"),
        "text=Upload filer": FakeLoginControl(text="Upload filer"),
        "text=Overblik": FakeLoginControl(text="Overblik"),
        "text=Fakturering": FakeLoginControl(text="Fakturering"),
        "text=Menu": FakeLoginControl(text="Menu"),
        "text=Upsedasse!": FakeLoginControl(count=0, visible=False),
        "text=Upsedasse": FakeLoginControl(count=0, visible=False),
        "text=Log ind igen": FakeLoginControl(count=0, visible=False),
    }


def _receipt_inbox_shell_controls() -> dict[str, FakeLoginControl]:
    return {
        "input[type='email'][name='email']": FakeLoginControl(count=0, visible=False),
        "input[type='password'][name='password']": FakeLoginControl(count=0, visible=False),
        "input[type='checkbox'][name='remember']": FakeLoginControl(count=0, visible=False),
        "button[data-cy='login-button']": FakeLoginControl(count=0, visible=False),
        "h1": FakeLoginControl(text="Bilagsindbakke"),
        "input[type=file]": FakeLoginControl(count=1, visible=True),
        "text=Overblik": FakeLoginControl(text="Overblik"),
        "text=Fakturering": FakeLoginControl(text="Fakturering"),
        "text=Menu": FakeLoginControl(text="Menu"),
        "text=Upsedasse!": FakeLoginControl(count=0, visible=False),
        "text=Upsedasse": FakeLoginControl(count=0, visible=False),
        "text=Log ind igen": FakeLoginControl(count=0, visible=False),
    }


def test_ui_suppliers_list_returns_auth_required_on_login_page(tmp_path: Path) -> None:
    page = FakeLoginPage()
    context = FakeLoginContext(page)

    async def launcher(profile_path: str, **kwargs: bool) -> PersistentContext:
        return cast(PersistentContext, context)

    runtime = BrowserRuntime(
        profile_path=tmp_path / "profile",
        egress_manifest_path=write_browser_egress_fixture(tmp_path),
        launcher=launcher,
    )

    result = asyncio.run(runtime.ui_suppliers_list())

    assert isinstance(result, ToolError)
    assert result.code is StableErrorCode.AUTH_REQUIRED
    assert page.closed


def test_ui_suppliers_list_returns_success_for_list_shell(tmp_path: Path) -> None:
    identity_path = tmp_path / "ui-org-identity.json"
    identity_path.write_text(
        json.dumps({"source": "ui_dashboard_path", "org_slug": "test-org-slug"}) + "\n",
        encoding="utf-8",
    )
    page = FakeLoginPage(
        final_url="https://mit.billy.dk/test-org-slug/dashboard",
        controls=_suppliers_shell_controls(),
        follow_goto=True,
    )
    context = FakeLoginContext(page)

    async def launcher(profile_path: str, **kwargs: bool) -> PersistentContext:
        return cast(PersistentContext, context)

    runtime = BrowserRuntime(
        profile_path=tmp_path / "profile",
        egress_manifest_path=write_browser_egress_fixture(tmp_path),
        launcher=launcher,
        org_identity_path=identity_path,
    )

    result = asyncio.run(runtime.ui_suppliers_list())

    assert result == UiSuppliersListSuccess(
        create_action_visible=True,
        shell_markers_present=True,
    )
    assert any(url.endswith("/suppliers") for url, _ in page.navigation)
    assert "test-org-slug" not in str(result.model_dump())
    assert page.closed


def test_ui_suppliers_list_returns_ui_changed_for_error_shell(tmp_path: Path) -> None:
    identity_path = tmp_path / "ui-org-identity.json"
    identity_path.write_text(
        json.dumps({"source": "ui_dashboard_path", "org_slug": "test-org-slug"}) + "\n",
        encoding="utf-8",
    )
    controls = _suppliers_shell_controls()
    controls["h1"] = FakeLoginControl(text="Upsedasse!")
    controls["text=Opret kontakt"] = FakeLoginControl(count=0, visible=False)
    controls["text=Upsedasse!"] = FakeLoginControl(text="Upsedasse!")
    page = FakeLoginPage(
        final_url="https://mit.billy.dk/test-org-slug/dashboard",
        controls=controls,
        follow_goto=True,
    )
    context = FakeLoginContext(page)

    async def launcher(profile_path: str, **kwargs: bool) -> PersistentContext:
        return cast(PersistentContext, context)

    runtime = BrowserRuntime(
        profile_path=tmp_path / "profile",
        egress_manifest_path=write_browser_egress_fixture(tmp_path),
        launcher=launcher,
        org_identity_path=identity_path,
    )

    result = asyncio.run(runtime.ui_suppliers_list())

    assert isinstance(result, ToolError)
    assert result.code is StableErrorCode.UI_CHANGED
    assert "suppliers list" in result.message
    assert "test-org-slug" not in str(result.model_dump())
    assert page.closed


def test_ui_suppliers_list_returns_ui_changed_when_heading_missing(tmp_path: Path) -> None:
    identity_path = tmp_path / "ui-org-identity.json"
    identity_path.write_text(
        json.dumps({"source": "ui_dashboard_path", "org_slug": "test-org-slug"}) + "\n",
        encoding="utf-8",
    )
    controls = _suppliers_shell_controls()
    controls["h1"] = FakeLoginControl(count=0, visible=False)
    page = FakeLoginPage(
        final_url="https://mit.billy.dk/test-org-slug/dashboard",
        controls=controls,
        follow_goto=True,
    )
    context = FakeLoginContext(page)

    async def launcher(profile_path: str, **kwargs: bool) -> PersistentContext:
        return cast(PersistentContext, context)

    runtime = BrowserRuntime(
        profile_path=tmp_path / "profile",
        egress_manifest_path=write_browser_egress_fixture(tmp_path),
        launcher=launcher,
        org_identity_path=identity_path,
    )

    result = asyncio.run(runtime.ui_suppliers_list())

    assert isinstance(result, ToolError)
    assert result.code is StableErrorCode.UI_CHANGED
    assert page.closed


def test_ui_suppliers_list_accepts_list_url_with_query_params(tmp_path: Path) -> None:
    identity_path = tmp_path / "ui-org-identity.json"
    identity_path.write_text(
        json.dumps({"source": "ui_dashboard_path", "org_slug": "test-org-slug"}) + "\n",
        encoding="utf-8",
    )
    page = FakeLoginPage(
        final_url=(
            "https://mit.billy.dk/test-org-slug/suppliers?page=1&pageSize=50&sortDirection=DESC"
        ),
        controls=_suppliers_shell_controls(),
        follow_goto=True,
    )
    original_goto = page.goto

    async def goto_keep_query(url: str, *, wait_until: str) -> object:
        result = await original_goto(url, wait_until=wait_until)
        if url.rstrip("/").endswith("/suppliers"):
            page.url = (
                "https://mit.billy.dk/test-org-slug/suppliers?page=1&pageSize=50&sortDirection=DESC"
            )
        return result

    page.goto = goto_keep_query  # type: ignore[method-assign]
    context = FakeLoginContext(page)

    async def launcher(profile_path: str, **kwargs: bool) -> PersistentContext:
        return cast(PersistentContext, context)

    runtime = BrowserRuntime(
        profile_path=tmp_path / "profile",
        egress_manifest_path=write_browser_egress_fixture(tmp_path),
        launcher=launcher,
        org_identity_path=identity_path,
    )

    result = asyncio.run(runtime.ui_suppliers_list())

    assert result == UiSuppliersListSuccess(
        create_action_visible=True,
        shell_markers_present=True,
    )


def test_ui_bills_list_returns_auth_required_on_login_page(tmp_path: Path) -> None:
    page = FakeLoginPage()
    context = FakeLoginContext(page)

    async def launcher(profile_path: str, **kwargs: bool) -> PersistentContext:
        return cast(PersistentContext, context)

    runtime = BrowserRuntime(
        profile_path=tmp_path / "profile",
        egress_manifest_path=write_browser_egress_fixture(tmp_path),
        launcher=launcher,
    )

    result = asyncio.run(runtime.ui_bills_list())

    assert isinstance(result, ToolError)
    assert result.code is StableErrorCode.AUTH_REQUIRED
    assert page.closed


def test_ui_bills_list_returns_success_for_list_shell(tmp_path: Path) -> None:
    identity_path = tmp_path / "ui-org-identity.json"
    identity_path.write_text(
        json.dumps({"source": "ui_dashboard_path", "org_slug": "test-org-slug"}) + "\n",
        encoding="utf-8",
    )
    page = FakeLoginPage(
        final_url="https://mit.billy.dk/test-org-slug/dashboard",
        controls=_bills_shell_controls(),
        follow_goto=True,
    )
    context = FakeLoginContext(page)

    async def launcher(profile_path: str, **kwargs: bool) -> PersistentContext:
        return cast(PersistentContext, context)

    runtime = BrowserRuntime(
        profile_path=tmp_path / "profile",
        egress_manifest_path=write_browser_egress_fixture(tmp_path),
        launcher=launcher,
        org_identity_path=identity_path,
    )

    result = asyncio.run(runtime.ui_bills_list())

    assert result == UiBillsListSuccess(
        create_action_visible=True,
        shell_markers_present=True,
    )
    assert any(url.endswith("/bills") for url, _ in page.navigation)
    assert "test-org-slug" not in str(result.model_dump())
    assert page.closed


def test_ui_bills_list_returns_ui_changed_for_error_shell(tmp_path: Path) -> None:
    identity_path = tmp_path / "ui-org-identity.json"
    identity_path.write_text(
        json.dumps({"source": "ui_dashboard_path", "org_slug": "test-org-slug"}) + "\n",
        encoding="utf-8",
    )
    controls = _bills_shell_controls()
    controls["h1"] = FakeLoginControl(text="Upsedasse!")
    controls["text=Opret køb"] = FakeLoginControl(count=0, visible=False)
    controls["text=Upsedasse!"] = FakeLoginControl(text="Upsedasse!")
    page = FakeLoginPage(
        final_url="https://mit.billy.dk/test-org-slug/dashboard",
        controls=controls,
        follow_goto=True,
    )
    context = FakeLoginContext(page)

    async def launcher(profile_path: str, **kwargs: bool) -> PersistentContext:
        return cast(PersistentContext, context)

    runtime = BrowserRuntime(
        profile_path=tmp_path / "profile",
        egress_manifest_path=write_browser_egress_fixture(tmp_path),
        launcher=launcher,
        org_identity_path=identity_path,
    )

    result = asyncio.run(runtime.ui_bills_list())

    assert isinstance(result, ToolError)
    assert result.code is StableErrorCode.UI_CHANGED
    assert "bills list" in result.message
    assert "test-org-slug" not in str(result.model_dump())
    assert page.closed


def test_ui_bills_list_returns_ui_changed_when_heading_missing(tmp_path: Path) -> None:
    identity_path = tmp_path / "ui-org-identity.json"
    identity_path.write_text(
        json.dumps({"source": "ui_dashboard_path", "org_slug": "test-org-slug"}) + "\n",
        encoding="utf-8",
    )
    controls = _bills_shell_controls()
    controls["h1"] = FakeLoginControl(count=0, visible=False)
    page = FakeLoginPage(
        final_url="https://mit.billy.dk/test-org-slug/dashboard",
        controls=controls,
        follow_goto=True,
    )
    context = FakeLoginContext(page)

    async def launcher(profile_path: str, **kwargs: bool) -> PersistentContext:
        return cast(PersistentContext, context)

    runtime = BrowserRuntime(
        profile_path=tmp_path / "profile",
        egress_manifest_path=write_browser_egress_fixture(tmp_path),
        launcher=launcher,
        org_identity_path=identity_path,
    )

    result = asyncio.run(runtime.ui_bills_list())

    assert isinstance(result, ToolError)
    assert result.code is StableErrorCode.UI_CHANGED
    assert page.closed


def test_ui_bills_list_rejects_purchases_alias_path(tmp_path: Path) -> None:
    identity_path = tmp_path / "ui-org-identity.json"
    identity_path.write_text(
        json.dumps({"source": "ui_dashboard_path", "org_slug": "test-org-slug"}) + "\n",
        encoding="utf-8",
    )
    page = FakeLoginPage(
        final_url="https://mit.billy.dk/test-org-slug/dashboard",
        controls=_bills_shell_controls(),
        follow_goto=True,
    )
    original_goto = page.goto

    async def goto_to_purchases_alias(url: str, *, wait_until: str) -> object:
        result = await original_goto(url, wait_until=wait_until)
        if url.rstrip("/").endswith("/bills"):
            page.url = "https://mit.billy.dk/test-org-slug/purchases"
            page.controls["h1"] = FakeLoginControl(count=0, visible=False)
            page.controls["text=Opret køb"] = FakeLoginControl(count=0, visible=False)
        return result

    page.goto = goto_to_purchases_alias  # type: ignore[method-assign]
    context = FakeLoginContext(page)

    async def launcher(profile_path: str, **kwargs: bool) -> PersistentContext:
        return cast(PersistentContext, context)

    runtime = BrowserRuntime(
        profile_path=tmp_path / "profile",
        egress_manifest_path=write_browser_egress_fixture(tmp_path),
        launcher=launcher,
        org_identity_path=identity_path,
    )

    result = asyncio.run(runtime.ui_bills_list())

    assert isinstance(result, ToolError)
    assert result.code is StableErrorCode.UI_CHANGED
    assert page.closed


def test_ui_bills_list_accepts_list_url_with_query_params(tmp_path: Path) -> None:
    identity_path = tmp_path / "ui-org-identity.json"
    identity_path.write_text(
        json.dumps({"source": "ui_dashboard_path", "org_slug": "test-org-slug"}) + "\n",
        encoding="utf-8",
    )
    page = FakeLoginPage(
        final_url=(
            "https://mit.billy.dk/test-org-slug/bills?page=1&pageSize=50&sortDirection=DESC"
        ),
        controls=_bills_shell_controls(),
        follow_goto=True,
    )
    original_goto = page.goto

    async def goto_keep_query(url: str, *, wait_until: str) -> object:
        result = await original_goto(url, wait_until=wait_until)
        if url.rstrip("/").endswith("/bills"):
            page.url = (
                "https://mit.billy.dk/test-org-slug/bills?page=1&pageSize=50&sortDirection=DESC"
            )
        return result

    page.goto = goto_keep_query  # type: ignore[method-assign]
    context = FakeLoginContext(page)

    async def launcher(profile_path: str, **kwargs: bool) -> PersistentContext:
        return cast(PersistentContext, context)

    runtime = BrowserRuntime(
        profile_path=tmp_path / "profile",
        egress_manifest_path=write_browser_egress_fixture(tmp_path),
        launcher=launcher,
        org_identity_path=identity_path,
    )

    result = asyncio.run(runtime.ui_bills_list())

    assert result == UiBillsListSuccess(
        create_action_visible=True,
        shell_markers_present=True,
    )


def test_ui_debtor_balances_list_returns_auth_required_on_login_page(tmp_path: Path) -> None:
    page = FakeLoginPage()
    context = FakeLoginContext(page)

    async def launcher(profile_path: str, **kwargs: bool) -> PersistentContext:
        return cast(PersistentContext, context)

    runtime = BrowserRuntime(
        profile_path=tmp_path / "profile",
        egress_manifest_path=write_browser_egress_fixture(tmp_path),
        launcher=launcher,
    )

    result = asyncio.run(runtime.ui_debtor_balances_list())

    assert isinstance(result, ToolError)
    assert result.code is StableErrorCode.AUTH_REQUIRED
    assert page.closed


def test_ui_debtor_balances_list_returns_success_for_list_shell(tmp_path: Path) -> None:
    identity_path = tmp_path / "ui-org-identity.json"
    identity_path.write_text(
        json.dumps({"source": "ui_dashboard_path", "org_slug": "test-org-slug"}) + "\n",
        encoding="utf-8",
    )
    page = FakeLoginPage(
        final_url="https://mit.billy.dk/test-org-slug/dashboard",
        controls=_debtor_balances_shell_controls(),
        follow_goto=True,
    )
    context = FakeLoginContext(page)

    async def launcher(profile_path: str, **kwargs: bool) -> PersistentContext:
        return cast(PersistentContext, context)

    runtime = BrowserRuntime(
        profile_path=tmp_path / "profile",
        egress_manifest_path=write_browser_egress_fixture(tmp_path),
        launcher=launcher,
        org_identity_path=identity_path,
    )

    result = asyncio.run(runtime.ui_debtor_balances_list())

    assert result == UiDebtorBalancesListSuccess(
        create_action_visible=True,
        shell_markers_present=True,
    )
    assert any(url.endswith("/debtorbalance") for url, _ in page.navigation)
    assert "test-org-slug" not in str(result.model_dump())
    assert page.closed


def test_ui_debtor_balances_list_returns_ui_changed_for_error_shell(tmp_path: Path) -> None:
    identity_path = tmp_path / "ui-org-identity.json"
    identity_path.write_text(
        json.dumps({"source": "ui_dashboard_path", "org_slug": "test-org-slug"}) + "\n",
        encoding="utf-8",
    )
    controls = _debtor_balances_shell_controls()
    controls["h1"] = FakeLoginControl(text="Upsedasse!")
    controls["text=Opret faktura"] = FakeLoginControl(count=0, visible=False)
    controls["text=Upsedasse!"] = FakeLoginControl(text="Upsedasse!")
    page = FakeLoginPage(
        final_url="https://mit.billy.dk/test-org-slug/dashboard",
        controls=controls,
        follow_goto=True,
    )
    context = FakeLoginContext(page)

    async def launcher(profile_path: str, **kwargs: bool) -> PersistentContext:
        return cast(PersistentContext, context)

    runtime = BrowserRuntime(
        profile_path=tmp_path / "profile",
        egress_manifest_path=write_browser_egress_fixture(tmp_path),
        launcher=launcher,
        org_identity_path=identity_path,
    )

    result = asyncio.run(runtime.ui_debtor_balances_list())

    assert isinstance(result, ToolError)
    assert result.code is StableErrorCode.UI_CHANGED
    assert "debtor balances" in result.message
    assert "test-org-slug" not in str(result.model_dump())
    assert page.closed


def test_ui_debtor_balances_list_returns_ui_changed_when_heading_missing(tmp_path: Path) -> None:
    identity_path = tmp_path / "ui-org-identity.json"
    identity_path.write_text(
        json.dumps({"source": "ui_dashboard_path", "org_slug": "test-org-slug"}) + "\n",
        encoding="utf-8",
    )
    controls = _debtor_balances_shell_controls()
    controls["h1"] = FakeLoginControl(count=0, visible=False)
    page = FakeLoginPage(
        final_url="https://mit.billy.dk/test-org-slug/dashboard",
        controls=controls,
        follow_goto=True,
    )
    context = FakeLoginContext(page)

    async def launcher(profile_path: str, **kwargs: bool) -> PersistentContext:
        return cast(PersistentContext, context)

    runtime = BrowserRuntime(
        profile_path=tmp_path / "profile",
        egress_manifest_path=write_browser_egress_fixture(tmp_path),
        launcher=launcher,
        org_identity_path=identity_path,
    )

    result = asyncio.run(runtime.ui_debtor_balances_list())

    assert isinstance(result, ToolError)
    assert result.code is StableErrorCode.UI_CHANGED
    assert page.closed


def test_ui_debtor_balances_list_rejects_alias_path(tmp_path: Path) -> None:
    identity_path = tmp_path / "ui-org-identity.json"
    identity_path.write_text(
        json.dumps({"source": "ui_dashboard_path", "org_slug": "test-org-slug"}) + "\n",
        encoding="utf-8",
    )
    page = FakeLoginPage(
        final_url="https://mit.billy.dk/test-org-slug/dashboard",
        controls=_debtor_balances_shell_controls(),
        follow_goto=True,
    )
    original_goto = page.goto

    async def goto_to_alias(url: str, *, wait_until: str) -> object:
        result = await original_goto(url, wait_until=wait_until)
        if url.rstrip("/").endswith("/debtorbalance"):
            page.url = "https://mit.billy.dk/test-org-slug/debtor-balances"
            page.controls["h1"] = FakeLoginControl(count=0, visible=False)
            page.controls["text=Opret faktura"] = FakeLoginControl(count=0, visible=False)
        return result

    page.goto = goto_to_alias  # type: ignore[method-assign]
    context = FakeLoginContext(page)

    async def launcher(profile_path: str, **kwargs: bool) -> PersistentContext:
        return cast(PersistentContext, context)

    runtime = BrowserRuntime(
        profile_path=tmp_path / "profile",
        egress_manifest_path=write_browser_egress_fixture(tmp_path),
        launcher=launcher,
        org_identity_path=identity_path,
    )

    result = asyncio.run(runtime.ui_debtor_balances_list())

    assert isinstance(result, ToolError)
    assert result.code is StableErrorCode.UI_CHANGED
    assert page.closed


def test_ui_debtor_balances_list_accepts_list_url_with_query_params(tmp_path: Path) -> None:
    identity_path = tmp_path / "ui-org-identity.json"
    identity_path.write_text(
        json.dumps({"source": "ui_dashboard_path", "org_slug": "test-org-slug"}) + "\n",
        encoding="utf-8",
    )
    page = FakeLoginPage(
        final_url=("https://mit.billy.dk/test-org-slug/debtorbalance?page=1&pageSize=50"),
        controls=_debtor_balances_shell_controls(),
        follow_goto=True,
    )
    original_goto = page.goto

    async def goto_keep_query(url: str, *, wait_until: str) -> object:
        result = await original_goto(url, wait_until=wait_until)
        if url.rstrip("/").endswith("/debtorbalance"):
            page.url = "https://mit.billy.dk/test-org-slug/debtorbalance?page=1&pageSize=50"
        return result

    page.goto = goto_keep_query  # type: ignore[method-assign]
    context = FakeLoginContext(page)

    async def launcher(profile_path: str, **kwargs: bool) -> PersistentContext:
        return cast(PersistentContext, context)

    runtime = BrowserRuntime(
        profile_path=tmp_path / "profile",
        egress_manifest_path=write_browser_egress_fixture(tmp_path),
        launcher=launcher,
        org_identity_path=identity_path,
    )

    result = asyncio.run(runtime.ui_debtor_balances_list())

    assert result == UiDebtorBalancesListSuccess(
        create_action_visible=True,
        shell_markers_present=True,
    )


def test_ui_creditor_balances_list_returns_auth_required_on_login_page(tmp_path: Path) -> None:
    page = FakeLoginPage()
    context = FakeLoginContext(page)

    async def launcher(profile_path: str, **kwargs: bool) -> PersistentContext:
        return cast(PersistentContext, context)

    runtime = BrowserRuntime(
        profile_path=tmp_path / "profile",
        egress_manifest_path=write_browser_egress_fixture(tmp_path),
        launcher=launcher,
    )

    result = asyncio.run(runtime.ui_creditor_balances_list())

    assert isinstance(result, ToolError)
    assert result.code is StableErrorCode.AUTH_REQUIRED
    assert page.closed


def test_ui_creditor_balances_list_returns_success_for_list_shell(tmp_path: Path) -> None:
    identity_path = tmp_path / "ui-org-identity.json"
    identity_path.write_text(
        json.dumps({"source": "ui_dashboard_path", "org_slug": "test-org-slug"}) + "\n",
        encoding="utf-8",
    )
    page = FakeLoginPage(
        final_url="https://mit.billy.dk/test-org-slug/dashboard",
        controls=_creditor_balances_shell_controls(),
        follow_goto=True,
    )
    context = FakeLoginContext(page)

    async def launcher(profile_path: str, **kwargs: bool) -> PersistentContext:
        return cast(PersistentContext, context)

    runtime = BrowserRuntime(
        profile_path=tmp_path / "profile",
        egress_manifest_path=write_browser_egress_fixture(tmp_path),
        launcher=launcher,
        org_identity_path=identity_path,
    )

    result = asyncio.run(runtime.ui_creditor_balances_list())

    assert result == UiCreditorBalancesListSuccess(
        create_action_visible=True,
        shell_markers_present=True,
    )
    assert any(url.endswith("/creditorbalance") for url, _ in page.navigation)
    assert "test-org-slug" not in str(result.model_dump())
    assert page.closed


def test_ui_creditor_balances_list_returns_ui_changed_for_error_shell(tmp_path: Path) -> None:
    identity_path = tmp_path / "ui-org-identity.json"
    identity_path.write_text(
        json.dumps({"source": "ui_dashboard_path", "org_slug": "test-org-slug"}) + "\n",
        encoding="utf-8",
    )
    controls = _creditor_balances_shell_controls()
    controls["h1"] = FakeLoginControl(text="Upsedasse!")
    controls["text=Opret køb"] = FakeLoginControl(count=0, visible=False)
    controls["text=Upsedasse!"] = FakeLoginControl(text="Upsedasse!")
    page = FakeLoginPage(
        final_url="https://mit.billy.dk/test-org-slug/dashboard",
        controls=controls,
        follow_goto=True,
    )
    context = FakeLoginContext(page)

    async def launcher(profile_path: str, **kwargs: bool) -> PersistentContext:
        return cast(PersistentContext, context)

    runtime = BrowserRuntime(
        profile_path=tmp_path / "profile",
        egress_manifest_path=write_browser_egress_fixture(tmp_path),
        launcher=launcher,
        org_identity_path=identity_path,
    )

    result = asyncio.run(runtime.ui_creditor_balances_list())

    assert isinstance(result, ToolError)
    assert result.code is StableErrorCode.UI_CHANGED
    assert "creditor balances" in result.message
    assert "test-org-slug" not in str(result.model_dump())
    assert page.closed


def test_ui_creditor_balances_list_returns_ui_changed_when_heading_missing(
    tmp_path: Path,
) -> None:
    identity_path = tmp_path / "ui-org-identity.json"
    identity_path.write_text(
        json.dumps({"source": "ui_dashboard_path", "org_slug": "test-org-slug"}) + "\n",
        encoding="utf-8",
    )
    controls = _creditor_balances_shell_controls()
    controls["h1"] = FakeLoginControl(count=0, visible=False)
    page = FakeLoginPage(
        final_url="https://mit.billy.dk/test-org-slug/dashboard",
        controls=controls,
        follow_goto=True,
    )
    context = FakeLoginContext(page)

    async def launcher(profile_path: str, **kwargs: bool) -> PersistentContext:
        return cast(PersistentContext, context)

    runtime = BrowserRuntime(
        profile_path=tmp_path / "profile",
        egress_manifest_path=write_browser_egress_fixture(tmp_path),
        launcher=launcher,
        org_identity_path=identity_path,
    )

    result = asyncio.run(runtime.ui_creditor_balances_list())

    assert isinstance(result, ToolError)
    assert result.code is StableErrorCode.UI_CHANGED
    assert page.closed


def test_ui_creditor_balances_list_rejects_alias_path(tmp_path: Path) -> None:
    identity_path = tmp_path / "ui-org-identity.json"
    identity_path.write_text(
        json.dumps({"source": "ui_dashboard_path", "org_slug": "test-org-slug"}) + "\n",
        encoding="utf-8",
    )
    page = FakeLoginPage(
        final_url="https://mit.billy.dk/test-org-slug/dashboard",
        controls=_creditor_balances_shell_controls(),
        follow_goto=True,
    )
    original_goto = page.goto

    async def goto_to_alias(url: str, *, wait_until: str) -> object:
        result = await original_goto(url, wait_until=wait_until)
        if url.rstrip("/").endswith("/creditorbalance"):
            page.url = "https://mit.billy.dk/test-org-slug/creditor-balances"
            page.controls["h1"] = FakeLoginControl(count=0, visible=False)
            page.controls["text=Opret køb"] = FakeLoginControl(count=0, visible=False)
        return result

    page.goto = goto_to_alias  # type: ignore[method-assign]
    context = FakeLoginContext(page)

    async def launcher(profile_path: str, **kwargs: bool) -> PersistentContext:
        return cast(PersistentContext, context)

    runtime = BrowserRuntime(
        profile_path=tmp_path / "profile",
        egress_manifest_path=write_browser_egress_fixture(tmp_path),
        launcher=launcher,
        org_identity_path=identity_path,
    )

    result = asyncio.run(runtime.ui_creditor_balances_list())

    assert isinstance(result, ToolError)
    assert result.code is StableErrorCode.UI_CHANGED
    assert page.closed


def test_ui_creditor_balances_list_accepts_list_url_with_query_params(tmp_path: Path) -> None:
    identity_path = tmp_path / "ui-org-identity.json"
    identity_path.write_text(
        json.dumps({"source": "ui_dashboard_path", "org_slug": "test-org-slug"}) + "\n",
        encoding="utf-8",
    )
    page = FakeLoginPage(
        final_url=("https://mit.billy.dk/test-org-slug/creditorbalance?page=1&pageSize=50"),
        controls=_creditor_balances_shell_controls(),
        follow_goto=True,
    )
    original_goto = page.goto

    async def goto_keep_query(url: str, *, wait_until: str) -> object:
        result = await original_goto(url, wait_until=wait_until)
        if url.rstrip("/").endswith("/creditorbalance"):
            page.url = "https://mit.billy.dk/test-org-slug/creditorbalance?page=1&pageSize=50"
        return result

    page.goto = goto_keep_query  # type: ignore[method-assign]
    context = FakeLoginContext(page)

    async def launcher(profile_path: str, **kwargs: bool) -> PersistentContext:
        return cast(PersistentContext, context)

    runtime = BrowserRuntime(
        profile_path=tmp_path / "profile",
        egress_manifest_path=write_browser_egress_fixture(tmp_path),
        launcher=launcher,
        org_identity_path=identity_path,
    )

    result = asyncio.run(runtime.ui_creditor_balances_list())

    assert result == UiCreditorBalancesListSuccess(
        create_action_visible=True,
        shell_markers_present=True,
    )


def test_ui_uploads_list_returns_auth_required_on_login_page(tmp_path: Path) -> None:
    page = FakeLoginPage()
    context = FakeLoginContext(page)

    async def launcher(profile_path: str, **kwargs: bool) -> PersistentContext:
        return cast(PersistentContext, context)

    runtime = BrowserRuntime(
        profile_path=tmp_path / "profile",
        egress_manifest_path=write_browser_egress_fixture(tmp_path),
        launcher=launcher,
    )

    result = asyncio.run(runtime.ui_uploads_list())

    assert isinstance(result, ToolError)
    assert result.code is StableErrorCode.AUTH_REQUIRED
    assert page.closed


def test_ui_uploads_list_returns_success_for_list_shell(tmp_path: Path) -> None:
    identity_path = tmp_path / "ui-org-identity.json"
    identity_path.write_text(
        json.dumps({"source": "ui_dashboard_path", "org_slug": "test-org-slug"}) + "\n",
        encoding="utf-8",
    )
    page = FakeLoginPage(
        final_url="https://mit.billy.dk/test-org-slug/dashboard",
        controls=_uploads_shell_controls(),
        follow_goto=True,
    )
    context = FakeLoginContext(page)

    async def launcher(profile_path: str, **kwargs: bool) -> PersistentContext:
        return cast(PersistentContext, context)

    runtime = BrowserRuntime(
        profile_path=tmp_path / "profile",
        egress_manifest_path=write_browser_egress_fixture(tmp_path),
        launcher=launcher,
        org_identity_path=identity_path,
    )

    result = asyncio.run(runtime.ui_uploads_list())

    assert result == UiUploadsListSuccess(
        upload_action_visible=True,
        shell_markers_present=True,
    )
    assert any(url.rstrip("/").endswith("/uploads") for url, _ in page.navigation)
    assert "test-org-slug" not in str(result.model_dump())
    assert "fill:" not in " ".join(page.events)
    assert page.closed


def test_ui_uploads_list_returns_ui_changed_for_error_shell(tmp_path: Path) -> None:
    identity_path = tmp_path / "ui-org-identity.json"
    identity_path.write_text(
        json.dumps({"source": "ui_dashboard_path", "org_slug": "test-org-slug"}) + "\n",
        encoding="utf-8",
    )
    controls = _uploads_shell_controls()
    controls["h1"] = FakeLoginControl(text="Upsedasse!")
    controls["text=Upload filer"] = FakeLoginControl(count=0, visible=False)
    controls["text=Upsedasse!"] = FakeLoginControl(text="Upsedasse!")
    page = FakeLoginPage(
        final_url="https://mit.billy.dk/test-org-slug/dashboard",
        controls=controls,
        follow_goto=True,
    )
    context = FakeLoginContext(page)

    async def launcher(profile_path: str, **kwargs: bool) -> PersistentContext:
        return cast(PersistentContext, context)

    runtime = BrowserRuntime(
        profile_path=tmp_path / "profile",
        egress_manifest_path=write_browser_egress_fixture(tmp_path),
        launcher=launcher,
        org_identity_path=identity_path,
    )

    result = asyncio.run(runtime.ui_uploads_list())

    assert isinstance(result, ToolError)
    assert result.code is StableErrorCode.UI_CHANGED
    assert "uploads" in result.message
    assert "test-org-slug" not in str(result.model_dump())
    assert page.closed


def test_ui_uploads_list_returns_ui_changed_when_heading_missing(tmp_path: Path) -> None:
    identity_path = tmp_path / "ui-org-identity.json"
    identity_path.write_text(
        json.dumps({"source": "ui_dashboard_path", "org_slug": "test-org-slug"}) + "\n",
        encoding="utf-8",
    )
    controls = _uploads_shell_controls()
    controls["h1"] = FakeLoginControl(count=0, visible=False)
    page = FakeLoginPage(
        final_url="https://mit.billy.dk/test-org-slug/dashboard",
        controls=controls,
        follow_goto=True,
    )
    context = FakeLoginContext(page)

    async def launcher(profile_path: str, **kwargs: bool) -> PersistentContext:
        return cast(PersistentContext, context)

    runtime = BrowserRuntime(
        profile_path=tmp_path / "profile",
        egress_manifest_path=write_browser_egress_fixture(tmp_path),
        launcher=launcher,
        org_identity_path=identity_path,
    )

    result = asyncio.run(runtime.ui_uploads_list())

    assert isinstance(result, ToolError)
    assert result.code is StableErrorCode.UI_CHANGED
    assert page.closed


def test_ui_uploads_list_rejects_alias_path(tmp_path: Path) -> None:
    identity_path = tmp_path / "ui-org-identity.json"
    identity_path.write_text(
        json.dumps({"source": "ui_dashboard_path", "org_slug": "test-org-slug"}) + "\n",
        encoding="utf-8",
    )
    page = FakeLoginPage(
        final_url="https://mit.billy.dk/test-org-slug/dashboard",
        controls=_uploads_shell_controls(),
        follow_goto=True,
    )
    original_goto = page.goto

    async def goto_to_alias(url: str, *, wait_until: str) -> object:
        result = await original_goto(url, wait_until=wait_until)
        if url.rstrip("/").endswith("/uploads"):
            page.url = "https://mit.billy.dk/test-org-slug/bilag"
            page.controls["h1"] = FakeLoginControl(count=0, visible=False)
            page.controls["text=Upload filer"] = FakeLoginControl(count=0, visible=False)
        return result

    page.goto = goto_to_alias  # type: ignore[method-assign]
    context = FakeLoginContext(page)

    async def launcher(profile_path: str, **kwargs: bool) -> PersistentContext:
        return cast(PersistentContext, context)

    runtime = BrowserRuntime(
        profile_path=tmp_path / "profile",
        egress_manifest_path=write_browser_egress_fixture(tmp_path),
        launcher=launcher,
        org_identity_path=identity_path,
    )

    result = asyncio.run(runtime.ui_uploads_list())

    assert isinstance(result, ToolError)
    assert result.code is StableErrorCode.UI_CHANGED
    assert page.closed


def test_ui_uploads_list_accepts_list_url_with_query_params(tmp_path: Path) -> None:
    identity_path = tmp_path / "ui-org-identity.json"
    identity_path.write_text(
        json.dumps({"source": "ui_dashboard_path", "org_slug": "test-org-slug"}) + "\n",
        encoding="utf-8",
    )
    page = FakeLoginPage(
        final_url=("https://mit.billy.dk/test-org-slug/uploads?drawerMode&type"),
        controls=_uploads_shell_controls(),
        follow_goto=True,
    )
    original_goto = page.goto

    async def goto_keep_query(url: str, *, wait_until: str) -> object:
        result = await original_goto(url, wait_until=wait_until)
        if url.rstrip("/").endswith("/uploads"):
            page.url = "https://mit.billy.dk/test-org-slug/uploads?drawerMode&type"
        return result

    page.goto = goto_keep_query  # type: ignore[method-assign]
    context = FakeLoginContext(page)

    async def launcher(profile_path: str, **kwargs: bool) -> PersistentContext:
        return cast(PersistentContext, context)

    runtime = BrowserRuntime(
        profile_path=tmp_path / "profile",
        egress_manifest_path=write_browser_egress_fixture(tmp_path),
        launcher=launcher,
        org_identity_path=identity_path,
    )

    result = asyncio.run(runtime.ui_uploads_list())

    assert result == UiUploadsListSuccess(
        upload_action_visible=True,
        shell_markers_present=True,
    )


def test_ui_receipt_inbox_list_returns_auth_required_on_login_page(tmp_path: Path) -> None:
    page = FakeLoginPage()
    context = FakeLoginContext(page)

    async def launcher(profile_path: str, **kwargs: bool) -> PersistentContext:
        return cast(PersistentContext, context)

    runtime = BrowserRuntime(
        profile_path=tmp_path / "profile",
        egress_manifest_path=write_browser_egress_fixture(tmp_path),
        launcher=launcher,
    )

    result = asyncio.run(runtime.ui_receipt_inbox_list())

    assert isinstance(result, ToolError)
    assert result.code is StableErrorCode.AUTH_REQUIRED
    assert page.closed


def test_ui_receipt_inbox_list_returns_success_for_list_shell(tmp_path: Path) -> None:
    identity_path = tmp_path / "ui-org-identity.json"
    identity_path.write_text(
        json.dumps({"source": "ui_dashboard_path", "org_slug": "test-org-slug"}) + "\n",
        encoding="utf-8",
    )
    page = FakeLoginPage(
        final_url="https://mit.billy.dk/test-org-slug/dashboard",
        controls=_receipt_inbox_shell_controls(),
        follow_goto=True,
    )
    context = FakeLoginContext(page)

    async def launcher(profile_path: str, **kwargs: bool) -> PersistentContext:
        return cast(PersistentContext, context)

    runtime = BrowserRuntime(
        profile_path=tmp_path / "profile",
        egress_manifest_path=write_browser_egress_fixture(tmp_path),
        launcher=launcher,
        org_identity_path=identity_path,
    )

    result = asyncio.run(runtime.ui_receipt_inbox_list())

    assert result == UiReceiptInboxListSuccess(
        file_control_present=True,
        shell_markers_present=True,
    )
    assert any(url.rstrip("/").endswith("/vouchers") for url, _ in page.navigation)
    assert "test-org-slug" not in str(result.model_dump())
    assert "fill:" not in " ".join(page.events)
    assert "click:" not in " ".join(page.events)
    assert page.closed


def test_ui_receipt_inbox_list_returns_ui_changed_for_error_shell(tmp_path: Path) -> None:
    identity_path = tmp_path / "ui-org-identity.json"
    identity_path.write_text(
        json.dumps({"source": "ui_dashboard_path", "org_slug": "test-org-slug"}) + "\n",
        encoding="utf-8",
    )
    controls = _receipt_inbox_shell_controls()
    controls["h1"] = FakeLoginControl(text="Upsedasse!")
    controls["text=Upsedasse!"] = FakeLoginControl(text="Upsedasse!")
    page = FakeLoginPage(
        final_url="https://mit.billy.dk/test-org-slug/dashboard",
        controls=controls,
        follow_goto=True,
    )
    context = FakeLoginContext(page)

    async def launcher(profile_path: str, **kwargs: bool) -> PersistentContext:
        return cast(PersistentContext, context)

    runtime = BrowserRuntime(
        profile_path=tmp_path / "profile",
        egress_manifest_path=write_browser_egress_fixture(tmp_path),
        launcher=launcher,
        org_identity_path=identity_path,
    )

    result = asyncio.run(runtime.ui_receipt_inbox_list())

    assert isinstance(result, ToolError)
    assert result.code is StableErrorCode.UI_CHANGED
    assert "receipt inbox" in result.message
    assert "test-org-slug" not in str(result.model_dump())
    assert page.closed


def test_ui_receipt_inbox_list_returns_ui_changed_when_heading_missing(tmp_path: Path) -> None:
    identity_path = tmp_path / "ui-org-identity.json"
    identity_path.write_text(
        json.dumps({"source": "ui_dashboard_path", "org_slug": "test-org-slug"}) + "\n",
        encoding="utf-8",
    )
    controls = _receipt_inbox_shell_controls()
    controls["h1"] = FakeLoginControl(count=0, visible=False)
    page = FakeLoginPage(
        final_url="https://mit.billy.dk/test-org-slug/dashboard",
        controls=controls,
        follow_goto=True,
    )
    context = FakeLoginContext(page)

    async def launcher(profile_path: str, **kwargs: bool) -> PersistentContext:
        return cast(PersistentContext, context)

    runtime = BrowserRuntime(
        profile_path=tmp_path / "profile",
        egress_manifest_path=write_browser_egress_fixture(tmp_path),
        launcher=launcher,
        org_identity_path=identity_path,
    )

    result = asyncio.run(runtime.ui_receipt_inbox_list())

    assert isinstance(result, ToolError)
    assert result.code is StableErrorCode.UI_CHANGED
    assert page.closed


def test_ui_receipt_inbox_list_rejects_uploads_bilag_path(tmp_path: Path) -> None:
    """Must not accept the Bilag uploads shell as receipt inbox."""

    identity_path = tmp_path / "ui-org-identity.json"
    identity_path.write_text(
        json.dumps({"source": "ui_dashboard_path", "org_slug": "test-org-slug"}) + "\n",
        encoding="utf-8",
    )
    page = FakeLoginPage(
        final_url="https://mit.billy.dk/test-org-slug/dashboard",
        controls=_receipt_inbox_shell_controls(),
        follow_goto=True,
    )
    original_goto = page.goto

    async def goto_to_uploads(url: str, *, wait_until: str) -> object:
        result = await original_goto(url, wait_until=wait_until)
        if url.rstrip("/").endswith("/vouchers"):
            page.url = "https://mit.billy.dk/test-org-slug/uploads"
            page.controls["h1"] = FakeLoginControl(text="Bilag")
            page.controls["text=Upload filer"] = FakeLoginControl(text="Upload filer")
        return result

    page.goto = goto_to_uploads  # type: ignore[method-assign]
    context = FakeLoginContext(page)

    async def launcher(profile_path: str, **kwargs: bool) -> PersistentContext:
        return cast(PersistentContext, context)

    runtime = BrowserRuntime(
        profile_path=tmp_path / "profile",
        egress_manifest_path=write_browser_egress_fixture(tmp_path),
        launcher=launcher,
        org_identity_path=identity_path,
    )

    result = asyncio.run(runtime.ui_receipt_inbox_list())

    assert isinstance(result, ToolError)
    assert result.code is StableErrorCode.UI_CHANGED
    assert page.closed


def test_ui_receipt_inbox_list_rejects_alias_path(tmp_path: Path) -> None:
    identity_path = tmp_path / "ui-org-identity.json"
    identity_path.write_text(
        json.dumps({"source": "ui_dashboard_path", "org_slug": "test-org-slug"}) + "\n",
        encoding="utf-8",
    )
    page = FakeLoginPage(
        final_url="https://mit.billy.dk/test-org-slug/dashboard",
        controls=_receipt_inbox_shell_controls(),
        follow_goto=True,
    )
    original_goto = page.goto

    async def goto_to_alias(url: str, *, wait_until: str) -> object:
        result = await original_goto(url, wait_until=wait_until)
        if url.rstrip("/").endswith("/vouchers"):
            page.url = "https://mit.billy.dk/test-org-slug/inbox"
            page.controls["h1"] = FakeLoginControl(count=0, visible=False)
        return result

    page.goto = goto_to_alias  # type: ignore[method-assign]
    context = FakeLoginContext(page)

    async def launcher(profile_path: str, **kwargs: bool) -> PersistentContext:
        return cast(PersistentContext, context)

    runtime = BrowserRuntime(
        profile_path=tmp_path / "profile",
        egress_manifest_path=write_browser_egress_fixture(tmp_path),
        launcher=launcher,
        org_identity_path=identity_path,
    )

    result = asyncio.run(runtime.ui_receipt_inbox_list())

    assert isinstance(result, ToolError)
    assert result.code is StableErrorCode.UI_CHANGED
    assert page.closed


def _bank_reconciliation_shell_controls() -> dict[str, FakeLoginControl]:
    recon_href = "https://mit.billy.dk/test-org-slug/bank_accounts/acctTestId0123456789/sync"
    return {
        "input[type='email'][name='email']": FakeLoginControl(count=0, visible=False),
        "input[type='password'][name='password']": FakeLoginControl(count=0, visible=False),
        "input[type='checkbox'][name='remember']": FakeLoginControl(count=0, visible=False),
        "button[data-cy='login-button']": FakeLoginControl(count=0, visible=False),
        "h1": FakeLoginControl(count=0, visible=False),
        "table": FakeLoginControl(count=0, visible=False),
        "[role=grid], [role=table]": FakeLoginControl(count=0, visible=False),
        "a[href*='/bank_accounts/'][href*='/sync']": FakeLoginControl(
            text="Afstemning", href=recon_href
        ),
        "a[href*='bank_accounts'][href$='/sync']": FakeLoginControl(
            text="Afstemning", href=recon_href
        ),
        "text=Afstemning": FakeLoginControl(text="Afstemning", href=recon_href),
        "text=Overblik": FakeLoginControl(text="Overblik"),
        "text=Fakturering": FakeLoginControl(text="Fakturering"),
        "text=Menu": FakeLoginControl(text="Menu"),
        "text=Upsedasse!": FakeLoginControl(count=0, visible=False),
        "text=Upsedasse": FakeLoginControl(count=0, visible=False),
        "text=Log ind igen": FakeLoginControl(count=0, visible=False),
    }


def test_ui_bank_reconciliation_open_returns_auth_required_on_login_page(tmp_path: Path) -> None:
    page = FakeLoginPage()
    context = FakeLoginContext(page)

    async def launcher(profile_path: str, **kwargs: bool) -> PersistentContext:
        return cast(PersistentContext, context)

    runtime = BrowserRuntime(
        profile_path=tmp_path / "profile",
        egress_manifest_path=write_browser_egress_fixture(tmp_path),
        launcher=launcher,
    )

    result = asyncio.run(runtime.ui_bank_reconciliation_open())

    assert isinstance(result, ToolError)
    assert result.code is StableErrorCode.AUTH_REQUIRED
    assert page.closed


def test_ui_bank_reconciliation_open_returns_success_for_empty_shell(tmp_path: Path) -> None:
    identity_path = tmp_path / "ui-org-identity.json"
    identity_path.write_text(
        json.dumps({"source": "ui_dashboard_path", "org_slug": "test-org-slug"}) + "\n",
        encoding="utf-8",
    )
    page = FakeLoginPage(
        final_url="https://mit.billy.dk/test-org-slug/dashboard",
        controls=_bank_reconciliation_shell_controls(),
        follow_goto=True,
    )
    context = FakeLoginContext(page)

    async def launcher(profile_path: str, **kwargs: bool) -> PersistentContext:
        return cast(PersistentContext, context)

    runtime = BrowserRuntime(
        profile_path=tmp_path / "profile",
        egress_manifest_path=write_browser_egress_fixture(tmp_path),
        launcher=launcher,
        org_identity_path=identity_path,
    )

    result = asyncio.run(runtime.ui_bank_reconciliation_open())

    assert result == UiBankReconciliationOpenSuccess(
        heading="",
        empty_content_shell=True,
        afstemning_nav_visible=True,
        shell_markers_present=True,
    )
    assert any("/bank-accounts" in url for url, _ in page.navigation)
    assert any(
        "/bank_accounts/" in url and url.rstrip("/").endswith("/sync") for url, _ in page.navigation
    )
    assert "test-org-slug" not in str(result.model_dump())
    assert "acctTestId" not in str(result.model_dump())
    assert "click:" not in " ".join(page.events)
    assert page.closed


def test_ui_bank_reconciliation_open_returns_ui_changed_when_harvest_missing(
    tmp_path: Path,
) -> None:
    identity_path = tmp_path / "ui-org-identity.json"
    identity_path.write_text(
        json.dumps({"source": "ui_dashboard_path", "org_slug": "test-org-slug"}) + "\n",
        encoding="utf-8",
    )
    controls = _bank_reconciliation_shell_controls()
    controls["a[href*='/bank_accounts/'][href*='/sync']"] = FakeLoginControl(count=0, visible=False)
    controls["a[href*='bank_accounts'][href$='/sync']"] = FakeLoginControl(count=0, visible=False)
    controls["text=Afstemning"] = FakeLoginControl(count=0, visible=False)
    page = FakeLoginPage(
        final_url="https://mit.billy.dk/test-org-slug/dashboard",
        controls=controls,
        follow_goto=True,
    )
    context = FakeLoginContext(page)

    async def launcher(profile_path: str, **kwargs: bool) -> PersistentContext:
        return cast(PersistentContext, context)

    runtime = BrowserRuntime(
        profile_path=tmp_path / "profile",
        egress_manifest_path=write_browser_egress_fixture(tmp_path),
        launcher=launcher,
        org_identity_path=identity_path,
    )

    result = asyncio.run(runtime.ui_bank_reconciliation_open())

    assert isinstance(result, ToolError)
    assert result.code is StableErrorCode.UI_CHANGED
    assert "bank reconciliation" in result.message
    assert "test-org-slug" not in str(result.model_dump())
    assert page.closed


def test_ui_bank_reconciliation_open_rejects_bank_accounts_list_conflation(
    tmp_path: Path,
) -> None:
    identity_path = tmp_path / "ui-org-identity.json"
    identity_path.write_text(
        json.dumps({"source": "ui_dashboard_path", "org_slug": "test-org-slug"}) + "\n",
        encoding="utf-8",
    )
    controls = _bank_reconciliation_shell_controls()
    # Harvest returns a valid recon href but final page is forced to Bankkonti list.
    page = FakeLoginPage(
        final_url="https://mit.billy.dk/test-org-slug/dashboard",
        controls=controls,
        follow_goto=True,
    )
    original_goto = page.goto

    async def goto_force_list(url: str, *, wait_until: str) -> object:
        result = await original_goto(url, wait_until=wait_until)
        if "/bank_accounts/" in url and url.rstrip("/").endswith("/sync"):
            page.url = "https://mit.billy.dk/test-org-slug/bank-accounts"
            page.controls["h1"] = FakeLoginControl(text="Bankkonti")
        return result

    page.goto = goto_force_list  # type: ignore[method-assign]
    context = FakeLoginContext(page)

    async def launcher(profile_path: str, **kwargs: bool) -> PersistentContext:
        return cast(PersistentContext, context)

    runtime = BrowserRuntime(
        profile_path=tmp_path / "profile",
        egress_manifest_path=write_browser_egress_fixture(tmp_path),
        launcher=launcher,
        org_identity_path=identity_path,
    )

    result = asyncio.run(runtime.ui_bank_reconciliation_open())

    assert isinstance(result, ToolError)
    assert result.code is StableErrorCode.UI_CHANGED
    assert page.closed


def _financing_shell_controls() -> dict[str, FakeLoginControl]:
    return {
        "input[type='email'][name='email']": FakeLoginControl(count=0, visible=False),
        "input[type='password'][name='password']": FakeLoginControl(count=0, visible=False),
        "input[type='checkbox'][name='remember']": FakeLoginControl(count=0, visible=False),
        "button[data-cy='login-button']": FakeLoginControl(count=0, visible=False),
        "h1": FakeLoginControl(text="Ansøg om erhvervslån"),
        "text=Få et uforpligtende tilbud": FakeLoginControl(text="Få et uforpligtende tilbud"),
        "text=Ansøg om lån": FakeLoginControl(text="Ansøg om lån"),
        "text=Overblik": FakeLoginControl(text="Overblik"),
        "text=Fakturering": FakeLoginControl(text="Fakturering"),
        "text=Menu": FakeLoginControl(text="Menu"),
        "text=Upsedasse!": FakeLoginControl(count=0, visible=False),
        "text=Upsedasse": FakeLoginControl(count=0, visible=False),
        "text=Log ind igen": FakeLoginControl(count=0, visible=False),
    }


def test_ui_financing_open_returns_auth_required_on_login_page(tmp_path: Path) -> None:
    page = FakeLoginPage()
    context = FakeLoginContext(page)

    async def launcher(profile_path: str, **kwargs: bool) -> PersistentContext:
        return cast(PersistentContext, context)

    runtime = BrowserRuntime(
        profile_path=tmp_path / "profile",
        egress_manifest_path=write_browser_egress_fixture(tmp_path),
        launcher=launcher,
    )

    result = asyncio.run(runtime.ui_financing_open())

    assert isinstance(result, ToolError)
    assert result.code is StableErrorCode.AUTH_REQUIRED
    assert page.closed


def test_ui_financing_open_returns_success_for_shell(tmp_path: Path) -> None:
    identity_path = tmp_path / "ui-org-identity.json"
    identity_path.write_text(
        json.dumps({"source": "ui_dashboard_path", "org_slug": "test-org-slug"}) + "\n",
        encoding="utf-8",
    )
    page = FakeLoginPage(
        final_url="https://mit.billy.dk/test-org-slug/dashboard",
        controls=_financing_shell_controls(),
        follow_goto=True,
    )
    context = FakeLoginContext(page)

    async def launcher(profile_path: str, **kwargs: bool) -> PersistentContext:
        return cast(PersistentContext, context)

    runtime = BrowserRuntime(
        profile_path=tmp_path / "profile",
        egress_manifest_path=write_browser_egress_fixture(tmp_path),
        launcher=launcher,
        org_identity_path=identity_path,
    )

    result = asyncio.run(runtime.ui_financing_open())

    assert result == UiFinancingOpenSuccess(
        apply_cta_observed=True,
        shell_markers_present=True,
    )
    assert any(url.rstrip("/").endswith("/financing") for url, _ in page.navigation)
    assert "test-org-slug" not in str(result.model_dump())
    assert "fill:" not in " ".join(page.events)
    assert "click:" not in " ".join(page.events)
    assert page.closed


def test_ui_financing_open_returns_ui_changed_for_error_shell(tmp_path: Path) -> None:
    identity_path = tmp_path / "ui-org-identity.json"
    identity_path.write_text(
        json.dumps({"source": "ui_dashboard_path", "org_slug": "test-org-slug"}) + "\n",
        encoding="utf-8",
    )
    controls = _financing_shell_controls()
    controls["h1"] = FakeLoginControl(text="Upsedasse!")
    controls["text=Upsedasse!"] = FakeLoginControl(text="Upsedasse!")
    page = FakeLoginPage(
        final_url="https://mit.billy.dk/test-org-slug/dashboard",
        controls=controls,
        follow_goto=True,
    )
    context = FakeLoginContext(page)

    async def launcher(profile_path: str, **kwargs: bool) -> PersistentContext:
        return cast(PersistentContext, context)

    runtime = BrowserRuntime(
        profile_path=tmp_path / "profile",
        egress_manifest_path=write_browser_egress_fixture(tmp_path),
        launcher=launcher,
        org_identity_path=identity_path,
    )

    result = asyncio.run(runtime.ui_financing_open())

    assert isinstance(result, ToolError)
    assert result.code is StableErrorCode.UI_CHANGED
    assert "financing" in result.message
    assert "test-org-slug" not in str(result.model_dump())
    assert page.closed


def test_ui_financing_open_returns_ui_changed_when_heading_missing(tmp_path: Path) -> None:
    identity_path = tmp_path / "ui-org-identity.json"
    identity_path.write_text(
        json.dumps({"source": "ui_dashboard_path", "org_slug": "test-org-slug"}) + "\n",
        encoding="utf-8",
    )
    controls = _financing_shell_controls()
    controls["h1"] = FakeLoginControl(count=0, visible=False)
    page = FakeLoginPage(
        final_url="https://mit.billy.dk/test-org-slug/dashboard",
        controls=controls,
        follow_goto=True,
    )
    context = FakeLoginContext(page)

    async def launcher(profile_path: str, **kwargs: bool) -> PersistentContext:
        return cast(PersistentContext, context)

    runtime = BrowserRuntime(
        profile_path=tmp_path / "profile",
        egress_manifest_path=write_browser_egress_fixture(tmp_path),
        launcher=launcher,
        org_identity_path=identity_path,
    )

    result = asyncio.run(runtime.ui_financing_open())

    assert isinstance(result, ToolError)
    assert result.code is StableErrorCode.UI_CHANGED
    assert page.closed


def test_ui_financing_open_rejects_soft_subpath(tmp_path: Path) -> None:
    """Must not accept financing/apply empty soft shell as the landing product."""

    identity_path = tmp_path / "ui-org-identity.json"
    identity_path.write_text(
        json.dumps({"source": "ui_dashboard_path", "org_slug": "test-org-slug"}) + "\n",
        encoding="utf-8",
    )
    page = FakeLoginPage(
        final_url="https://mit.billy.dk/test-org-slug/dashboard",
        controls=_financing_shell_controls(),
        follow_goto=True,
    )
    original_goto = page.goto

    async def goto_to_soft_subpath(url: str, *, wait_until: str) -> object:
        result = await original_goto(url, wait_until=wait_until)
        if url.rstrip("/").endswith("/financing"):
            page.url = "https://mit.billy.dk/test-org-slug/financing/apply"
            page.controls["h1"] = FakeLoginControl(count=0, visible=False)
        return result

    page.goto = goto_to_soft_subpath  # type: ignore[method-assign]
    context = FakeLoginContext(page)

    async def launcher(profile_path: str, **kwargs: bool) -> PersistentContext:
        return cast(PersistentContext, context)

    runtime = BrowserRuntime(
        profile_path=tmp_path / "profile",
        egress_manifest_path=write_browser_egress_fixture(tmp_path),
        launcher=launcher,
        org_identity_path=identity_path,
    )

    result = asyncio.run(runtime.ui_financing_open())

    assert isinstance(result, ToolError)
    assert result.code is StableErrorCode.UI_CHANGED
    assert page.closed


def test_ui_financing_open_rejects_bank_accounts_path(tmp_path: Path) -> None:
    identity_path = tmp_path / "ui-org-identity.json"
    identity_path.write_text(
        json.dumps({"source": "ui_dashboard_path", "org_slug": "test-org-slug"}) + "\n",
        encoding="utf-8",
    )
    page = FakeLoginPage(
        final_url="https://mit.billy.dk/test-org-slug/dashboard",
        controls=_financing_shell_controls(),
        follow_goto=True,
    )
    original_goto = page.goto

    async def goto_to_bank(url: str, *, wait_until: str) -> object:
        result = await original_goto(url, wait_until=wait_until)
        if url.rstrip("/").endswith("/financing"):
            page.url = "https://mit.billy.dk/test-org-slug/bank-accounts"
            page.controls["h1"] = FakeLoginControl(text="Bankkonti")
        return result

    page.goto = goto_to_bank  # type: ignore[method-assign]
    context = FakeLoginContext(page)

    async def launcher(profile_path: str, **kwargs: bool) -> PersistentContext:
        return cast(PersistentContext, context)

    runtime = BrowserRuntime(
        profile_path=tmp_path / "profile",
        egress_manifest_path=write_browser_egress_fixture(tmp_path),
        launcher=launcher,
        org_identity_path=identity_path,
    )

    result = asyncio.run(runtime.ui_financing_open())

    assert isinstance(result, ToolError)
    assert result.code is StableErrorCode.UI_CHANGED
    assert page.closed


def _daybooks_editor_shell_controls() -> dict[str, FakeLoginControl]:
    return {
        "input[type='email'][name='email']": FakeLoginControl(count=0, visible=False),
        "input[type='password'][name='password']": FakeLoginControl(count=0, visible=False),
        "input[type='checkbox'][name='remember']": FakeLoginControl(count=0, visible=False),
        "button[data-cy='login-button']": FakeLoginControl(count=0, visible=False),
        "h1": FakeLoginControl(count=0, visible=False),
        "text=Opret ny kassekladde": FakeLoginControl(text="Opret ny kassekladde"),
        "text=Tilføj kassekladdelinje": FakeLoginControl(text="Tilføj kassekladdelinje"),
        "text=Ingen postering valgt": FakeLoginControl(text="Ingen postering valgt"),
        "text=Overblik": FakeLoginControl(text="Overblik"),
        "text=Fakturering": FakeLoginControl(text="Fakturering"),
        "text=Menu": FakeLoginControl(text="Menu"),
        "text=Bogføring": FakeLoginControl(text="Bogføring"),
        "text=Upsedasse!": FakeLoginControl(count=0, visible=False),
        "text=Upsedasse": FakeLoginControl(count=0, visible=False),
        "text=Log ind igen": FakeLoginControl(count=0, visible=False),
    }


def test_ui_daybooks_open_returns_auth_required_on_login_page(tmp_path: Path) -> None:
    page = FakeLoginPage()
    context = FakeLoginContext(page)

    async def launcher(profile_path: str, **kwargs: bool) -> PersistentContext:
        return cast(PersistentContext, context)

    runtime = BrowserRuntime(
        profile_path=tmp_path / "profile",
        egress_manifest_path=write_browser_egress_fixture(tmp_path),
        launcher=launcher,
    )

    result = asyncio.run(runtime.ui_daybooks_open())

    assert isinstance(result, ToolError)
    assert result.code is StableErrorCode.AUTH_REQUIRED
    assert page.closed


def test_ui_daybooks_open_returns_success_for_editor_shell(tmp_path: Path) -> None:
    identity_path = tmp_path / "ui-org-identity.json"
    identity_path.write_text(
        json.dumps({"source": "ui_dashboard_path", "org_slug": "test-org-slug"}) + "\n",
        encoding="utf-8",
    )
    page = FakeLoginPage(
        final_url="https://mit.billy.dk/test-org-slug/dashboard",
        controls=_daybooks_editor_shell_controls(),
        follow_goto=True,
    )
    context = FakeLoginContext(page)

    async def launcher(profile_path: str, **kwargs: bool) -> PersistentContext:
        return cast(PersistentContext, context)

    runtime = BrowserRuntime(
        profile_path=tmp_path / "profile",
        egress_manifest_path=write_browser_egress_fixture(tmp_path),
        launcher=launcher,
        org_identity_path=identity_path,
    )

    result = asyncio.run(runtime.ui_daybooks_open())

    assert result == UiDaybooksOpenSuccess(
        heading="",
        editor_markers_present=True,
        shell_markers_present=True,
    )
    assert any(url.rstrip("/").endswith("/daybooks/new") for url, _ in page.navigation)
    assert "test-org-slug" not in str(result.model_dump())
    assert "fill:" not in " ".join(page.events)
    assert "click:" not in " ".join(page.events)
    assert page.closed


def test_ui_daybooks_open_returns_ui_changed_for_error_shell(tmp_path: Path) -> None:
    identity_path = tmp_path / "ui-org-identity.json"
    identity_path.write_text(
        json.dumps({"source": "ui_dashboard_path", "org_slug": "test-org-slug"}) + "\n",
        encoding="utf-8",
    )
    controls = _daybooks_editor_shell_controls()
    controls["h1"] = FakeLoginControl(text="Upsedasse!")
    controls["text=Upsedasse!"] = FakeLoginControl(text="Upsedasse!")
    page = FakeLoginPage(
        final_url="https://mit.billy.dk/test-org-slug/dashboard",
        controls=controls,
        follow_goto=True,
    )
    context = FakeLoginContext(page)

    async def launcher(profile_path: str, **kwargs: bool) -> PersistentContext:
        return cast(PersistentContext, context)

    runtime = BrowserRuntime(
        profile_path=tmp_path / "profile",
        egress_manifest_path=write_browser_egress_fixture(tmp_path),
        launcher=launcher,
        org_identity_path=identity_path,
    )

    result = asyncio.run(runtime.ui_daybooks_open())

    assert isinstance(result, ToolError)
    assert result.code is StableErrorCode.UI_CHANGED
    assert "daybooks" in result.message
    assert "test-org-slug" not in str(result.model_dump())
    assert page.closed


def test_ui_daybooks_open_rejects_bare_daybooks_path(tmp_path: Path) -> None:
    """Bare /daybooks is research117 Upsedasse shell; never product success."""

    identity_path = tmp_path / "ui-org-identity.json"
    identity_path.write_text(
        json.dumps({"source": "ui_dashboard_path", "org_slug": "test-org-slug"}) + "\n",
        encoding="utf-8",
    )
    page = FakeLoginPage(
        final_url="https://mit.billy.dk/test-org-slug/dashboard",
        controls=_daybooks_editor_shell_controls(),
        follow_goto=True,
    )
    original_goto = page.goto

    async def goto_bare(url: str, *, wait_until: str) -> object:
        result = await original_goto(url, wait_until=wait_until)
        if "/daybooks/new" in url:
            page.url = "https://mit.billy.dk/test-org-slug/daybooks"
            page.controls["h1"] = FakeLoginControl(text="Upsedasse!")
            page.controls["text=Upsedasse!"] = FakeLoginControl(text="Upsedasse!")
        return result

    page.goto = goto_bare  # type: ignore[method-assign]
    context = FakeLoginContext(page)

    async def launcher(profile_path: str, **kwargs: bool) -> PersistentContext:
        return cast(PersistentContext, context)

    runtime = BrowserRuntime(
        profile_path=tmp_path / "profile",
        egress_manifest_path=write_browser_egress_fixture(tmp_path),
        launcher=launcher,
        org_identity_path=identity_path,
    )

    result = asyncio.run(runtime.ui_daybooks_open())

    assert isinstance(result, ToolError)
    assert result.code is StableErrorCode.UI_CHANGED
    assert page.closed


def test_ui_daybooks_open_returns_ui_changed_when_editor_markers_missing(
    tmp_path: Path,
) -> None:
    identity_path = tmp_path / "ui-org-identity.json"
    identity_path.write_text(
        json.dumps({"source": "ui_dashboard_path", "org_slug": "test-org-slug"}) + "\n",
        encoding="utf-8",
    )
    controls = _daybooks_editor_shell_controls()
    controls["text=Opret ny kassekladde"] = FakeLoginControl(count=0, visible=False)
    page = FakeLoginPage(
        final_url="https://mit.billy.dk/test-org-slug/dashboard",
        controls=controls,
        follow_goto=True,
    )
    context = FakeLoginContext(page)

    async def launcher(profile_path: str, **kwargs: bool) -> PersistentContext:
        return cast(PersistentContext, context)

    runtime = BrowserRuntime(
        profile_path=tmp_path / "profile",
        egress_manifest_path=write_browser_egress_fixture(tmp_path),
        launcher=launcher,
        org_identity_path=identity_path,
    )

    result = asyncio.run(runtime.ui_daybooks_open())

    assert isinstance(result, ToolError)
    assert result.code is StableErrorCode.UI_CHANGED
    assert page.closed


def test_ui_daybooks_open_rejects_transactions_list_path(tmp_path: Path) -> None:
    identity_path = tmp_path / "ui-org-identity.json"
    identity_path.write_text(
        json.dumps({"source": "ui_dashboard_path", "org_slug": "test-org-slug"}) + "\n",
        encoding="utf-8",
    )
    page = FakeLoginPage(
        final_url="https://mit.billy.dk/test-org-slug/dashboard",
        controls=_daybooks_editor_shell_controls(),
        follow_goto=True,
    )
    original_goto = page.goto

    async def goto_tx(url: str, *, wait_until: str) -> object:
        result = await original_goto(url, wait_until=wait_until)
        if "/daybooks/new" in url:
            page.url = "https://mit.billy.dk/test-org-slug/transactions"
            page.controls["h1"] = FakeLoginControl(text="Posteringer")
        return result

    page.goto = goto_tx  # type: ignore[method-assign]
    context = FakeLoginContext(page)

    async def launcher(profile_path: str, **kwargs: bool) -> PersistentContext:
        return cast(PersistentContext, context)

    runtime = BrowserRuntime(
        profile_path=tmp_path / "profile",
        egress_manifest_path=write_browser_egress_fixture(tmp_path),
        launcher=launcher,
        org_identity_path=identity_path,
    )

    result = asyncio.run(runtime.ui_daybooks_open())

    assert isinstance(result, ToolError)
    assert result.code is StableErrorCode.UI_CHANGED
    assert page.closed
