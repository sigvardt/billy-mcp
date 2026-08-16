from __future__ import annotations

import asyncio
import json
import re
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
    UiAddonsOpenSuccess,
    UiBankAccountsListSuccess,
    UiBankReconciliationOpenSuccess,
    UiBillsCreateOpenSuccess,
    UiBillsGetOpenSuccess,
    UiBillsListSuccess,
    UiBillsUpdateOpenSuccess,
    UiClientsCreateOpenSuccess,
    UiClientsDeleteOpenSuccess,
    UiClientsGetOpenSuccess,
    UiClientsListSuccess,
    UiClientsUpdateOpenSuccess,
    UiCreditorBalancesListSuccess,
    UiDaybooksDeleteOpenSuccess,
    UiDaybooksGetOpenSuccess,
    UiDaybooksOpenSuccess,
    UiDaybookTransactionsCreateOpenSuccess,
    UiDebtorBalancesListSuccess,
    UiExportsOpenSuccess,
    UiFinancingOpenSuccess,
    UiIntegrationsOpenSuccess,
    UiInventoryOpenSuccess,
    UiInvoicesCreateOpenSuccess,
    UiInvoicesDeleteOpenSuccess,
    UiInvoicesGetOpenSuccess,
    UiInvoicesListSuccess,
    UiInvoicesUpdateOpenSuccess,
    UiProductsCreateOpenSuccess,
    UiProductsImportSuccess,
    UiProductsListSuccess,
    UiQuotesListSuccess,
    UiReceiptInboxListSuccess,
    UiRecurringInvoicesListSuccess,
    UiReportsOpenSuccess,
    UiSaftExportsOpenSuccess,
    UiSettingsAccessTokenOpenSuccess,
    UiSettingsAccountingOpenSuccess,
    UiSettingsBetaOpenSuccess,
    UiSettingsCompanyOpenSuccess,
    UiSettingsInvoicingOpenSuccess,
    UiSettingsSubscriptionOpenSuccess,
    UiSettingsUserOpenSuccess,
    UiSettingsUserOrganizationsOpenSuccess,
    UiSettingsUsersOpenSuccess,
    UiSettingsVatOpenSuccess,
    UiSuppliersCreateOpenSuccess,
    UiSuppliersListSuccess,
    UiTransactionsCreateOpenSuccess,
    UiTransactionsListSuccess,
    UiUploadsListSuccess,
    UiVatDeclarationsListSuccess,
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
        value: str = "",
        fill_error: Exception | None = None,
        click_error: Exception | None = None,
        on_click: Callable[[], None] | None = None,
    ) -> None:
        self._count = count
        self._visible = visible
        self._text = text
        self._href = href
        self._value = value
        self._fill_error = fill_error
        self._click_error = click_error
        self._on_click = on_click
        self._events: list[str] | None = None
        self._selector = ""

    def bind(self, events: list[str], selector: str) -> None:
        self._events = events
        self._selector = selector

    @property
    def first(self) -> FakeLoginControl:
        """Playwright-style first match; fakes are already a single control."""

        return self

    def nth(self, index: int) -> FakeLoginControl:
        """Playwright-style nth match; fakes treat every index as this control."""

        del index
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
        self._value = value
        self._record("fill")
        if self._fill_error is not None:
            raise self._fill_error

    async def input_value(self) -> str:
        self._record("input_value")
        return self._value

    async def check(self) -> None:
        self._record("check")

    async def click(self, **kwargs: object) -> None:
        del kwargs
        self._record("click")
        if self._click_error is not None:
            raise self._click_error
        if self._on_click is not None:
            self._on_click()

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

    def get_by_role(self, role: str, *, name: str | re.Pattern[str]) -> FakeLoginControl:
        if isinstance(name, re.Pattern):
            label = name.pattern.strip("^$")
        else:
            label = name
        key = f"role:{role}:{label}"
        return self.controls.get(key, FakeLoginControl(count=0, visible=False))

    async def close(self) -> None:
        self.closed = True

    async def wait_for_load_state(self, state: str, *, timeout: float | None = None) -> None:
        del state, timeout
        self.events.append("wait_for_load_state")

    async def wait_for_timeout(self, timeout: float) -> None:
        del timeout
        self.events.append("wait_for_timeout")

    def on(self, event: str, handler: object) -> None:
        self.events.append(f"on:{event}")
        if event != "request" or not callable(handler):
            return

        class _SyntheticRequest:
            url = "https://api.billysbilling.com/v2/user"
            headers = {
                "x-access-token": "test-token",
                "x-organizationid": "orgTestId01",
            }

        handler(_SyntheticRequest())


class _FakeApiResponse:
    def __init__(self, payload: object) -> None:
        self._payload = payload
        self.status = 200

    async def json(self) -> object:
        return self._payload


class _FakeApiRequest:
    def __init__(self, *, daybook_ids: list[str] | None = None) -> None:
        self.daybook_ids = ["daybookTestId01"] if daybook_ids is None else list(daybook_ids)
        self.calls: list[str] = []

    async def get(self, url: str, headers: dict[str, str] | None = None) -> _FakeApiResponse:
        del headers
        self.calls.append(url)
        if "/user/organizations" in url:
            return _FakeApiResponse(
                {
                    "data": [
                        {
                            "organizationId": "orgTestId01",
                            "url": "test-org-slug",
                            "name": "Test Org",
                        }
                    ]
                }
            )
        rows = [{"id": i} for i in self.daybook_ids]
        return _FakeApiResponse({"daybooks": rows})


class FakeLoginContext(FakeContext):
    def __init__(
        self,
        page: FakeLoginPage,
        *,
        daybook_ids: list[str] | None = None,
    ) -> None:
        super().__init__()
        self.page = page
        self.request = _FakeApiRequest(daybook_ids=daybook_ids)

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


def test_browser_policy_real_manifest_allows_contacts_data_plane() -> None:
    """Research164/165/168/169/170: contacts + products + invoices + bills seed planes."""

    policy = BrowserEgressPolicy.from_manifest(
        Path(__file__).resolve().parents[2] / "coverage" / "browser_egress.yaml"
    )
    assert policy.allows("https://api.billysbilling.com/v2/contacts", "GET")
    assert policy.allows("https://api.billysbilling.com/v2/contacts/abc", "GET")
    assert policy.allows("https://api.billysbilling.com/v2/contacts", "POST")
    assert policy.allows("https://api.billysbilling.com/v2/contacts/abc", "DELETE")
    assert policy.allows("https://api.billysbilling.com/v2/countries", "GET")
    assert policy.allows("https://api.billysbilling.com/v2/products", "GET")
    assert policy.allows("https://api.billysbilling.com/v2/products/abc", "GET")
    assert policy.allows("https://api.billysbilling.com/v2/products", "POST")
    assert policy.allows("https://api.billysbilling.com/v2/products/abc", "DELETE")
    assert policy.allows("https://api.billysbilling.com/v2/accounts", "GET")
    assert policy.allows("https://api.billysbilling.com/v2/salesTaxRulesets", "GET")
    assert policy.allows("https://api.billysbilling.com/v2/invoices", "GET")
    assert policy.allows("https://api.billysbilling.com/v2/invoices/summary", "GET")
    assert policy.allows("https://api.billysbilling.com/v2/invoices/abc", "GET")
    assert policy.allows("https://api.billysbilling.com/v2/bills", "GET")
    assert policy.allows("https://api.billysbilling.com/v2/bills/summary", "GET")
    assert policy.allows("https://api.billysbilling.com/v2/bills/abc", "GET")
    assert policy.allows("https://api.billysbilling.com/v2/bills", "POST")
    assert policy.allows("https://api.billysbilling.com/v2/bills/abc", "DELETE")
    assert policy.allows("https://api.billysbilling.com/v2/taxRates", "GET")
    assert policy.allows("https://api.billysbilling.com/v2/daybooks", "GET")
    assert policy.allows("https://api.billysbilling.com/v2/daybooks/abc", "GET")
    assert policy.allows("https://api.billysbilling.com/v2/daybooks", "POST")
    assert policy.allows("https://api.billysbilling.com/v2/daybooks/abc", "DELETE")
    assert not policy.allows("https://api.billysbilling.com/v2/invoices/x/emails", "POST")
    assert policy.allows("https://api.billysbilling.com/v2/invoices", "POST")
    assert policy.allows("https://api.billysbilling.com/v2/invoices/abc", "DELETE")


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

    assert result == AuthLoginWaitSuccess(status="READY", organization_id="test-org-slug")
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


def _invoices_create_shell_controls() -> dict[str, FakeLoginControl]:
    return {
        "input[type='email'][name='email']": FakeLoginControl(count=0, visible=False),
        "input[type='password'][name='password']": FakeLoginControl(count=0, visible=False),
        "input[type='checkbox'][name='remember']": FakeLoginControl(count=0, visible=False),
        "button[data-cy='login-button']": FakeLoginControl(count=0, visible=False),
        "h1": FakeLoginControl(text="Opret faktura"),
        "text=Gem som kladde": FakeLoginControl(text="Gem som kladde"),
        "text=Tilføj linje": FakeLoginControl(text="Tilføj linje"),
        "text=Beskrivelse": FakeLoginControl(text="Beskrivelse"),
        "text=Overblik": FakeLoginControl(text="Overblik"),
        "text=Menu": FakeLoginControl(text="Menu"),
        "text=Upsedasse!": FakeLoginControl(count=0, visible=False),
        "text=Upsedasse": FakeLoginControl(count=0, visible=False),
        "text=Log ind igen": FakeLoginControl(count=0, visible=False),
    }


def _bills_create_shell_controls() -> dict[str, FakeLoginControl]:
    return {
        "input[type='email'][name='email']": FakeLoginControl(count=0, visible=False),
        "input[type='password'][name='password']": FakeLoginControl(count=0, visible=False),
        "input[type='checkbox'][name='remember']": FakeLoginControl(count=0, visible=False),
        "button[data-cy='login-button']": FakeLoginControl(count=0, visible=False),
        "h1": FakeLoginControl(text="Opret køb"),
        "text=Gem som kladde": FakeLoginControl(text="Gem som kladde"),
        "text=Tilføj linje": FakeLoginControl(text="Tilføj linje"),
        "text=Beskrivelse": FakeLoginControl(text="Beskrivelse"),
        "text=Linje": FakeLoginControl(text="Linje"),
        "text=Overblik": FakeLoginControl(text="Overblik"),
        "text=Menu": FakeLoginControl(text="Menu"),
        "text=Upsedasse!": FakeLoginControl(count=0, visible=False),
        "text=Upsedasse": FakeLoginControl(count=0, visible=False),
        "text=Log ind igen": FakeLoginControl(count=0, visible=False),
    }


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


def test_ui_invoices_create_open_returns_auth_required_on_login_page(tmp_path: Path) -> None:
    page = FakeLoginPage()
    context = FakeLoginContext(page)

    async def launcher(profile_path: str, **kwargs: bool) -> PersistentContext:
        return cast(PersistentContext, context)

    runtime = BrowserRuntime(
        profile_path=tmp_path / "profile",
        egress_manifest_path=write_browser_egress_fixture(tmp_path),
        launcher=launcher,
    )

    result = asyncio.run(runtime.ui_invoices_create_open())

    assert isinstance(result, ToolError)
    assert result.code is StableErrorCode.AUTH_REQUIRED
    assert page.closed


def test_ui_invoices_create_open_returns_success_for_create_form(tmp_path: Path) -> None:
    identity_path = tmp_path / "ui-org-identity.json"
    identity_path.write_text(
        json.dumps({"source": "ui_dashboard_path", "org_slug": "test-org-slug"}) + "\n",
        encoding="utf-8",
    )
    page = FakeLoginPage(
        final_url="https://mit.billy.dk/test-org-slug/dashboard",
        controls=_invoices_create_shell_controls(),
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

    result = asyncio.run(runtime.ui_invoices_create_open())

    assert result == UiInvoicesCreateOpenSuccess(
        draft_save_chrome_visible=True,
        line_chrome_visible=True,
        shell_markers_present=True,
    )
    assert any(url.endswith("/invoices/new") for url, _ in page.navigation)
    assert "test-org-slug" not in str(result.model_dump())
    assert page.closed
    assert "click:" not in " ".join(page.events)


def test_ui_invoices_create_open_returns_ui_changed_for_error_shell(tmp_path: Path) -> None:
    identity_path = tmp_path / "ui-org-identity.json"
    identity_path.write_text(
        json.dumps({"source": "ui_dashboard_path", "org_slug": "test-org-slug"}) + "\n",
        encoding="utf-8",
    )
    controls = _invoices_create_shell_controls()
    controls["h1"] = FakeLoginControl(text="Upsedasse!")
    controls["text=Gem som kladde"] = FakeLoginControl(count=0, visible=False)
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

    result = asyncio.run(runtime.ui_invoices_create_open())

    assert isinstance(result, ToolError)
    assert result.code is StableErrorCode.UI_CHANGED
    assert "invoices create form" in result.message
    assert "test-org-slug" not in str(result.model_dump())
    assert page.closed


def test_ui_invoices_create_open_returns_ui_changed_when_heading_missing(
    tmp_path: Path,
) -> None:
    identity_path = tmp_path / "ui-org-identity.json"
    identity_path.write_text(
        json.dumps({"source": "ui_dashboard_path", "org_slug": "test-org-slug"}) + "\n",
        encoding="utf-8",
    )
    controls = _invoices_create_shell_controls()
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

    result = asyncio.run(runtime.ui_invoices_create_open())

    assert isinstance(result, ToolError)
    assert result.code is StableErrorCode.UI_CHANGED
    assert page.closed


def test_ui_invoices_create_open_accepts_create_url_with_query_params(tmp_path: Path) -> None:
    identity_path = tmp_path / "ui-org-identity.json"
    identity_path.write_text(
        json.dumps({"source": "ui_dashboard_path", "org_slug": "test-org-slug"}) + "\n",
        encoding="utf-8",
    )
    page = FakeLoginPage(
        final_url="https://mit.billy.dk/test-org-slug/dashboard",
        controls=_invoices_create_shell_controls(),
        follow_goto=True,
    )
    context = FakeLoginContext(page)

    async def launcher(profile_path: str, **kwargs: bool) -> PersistentContext:
        return cast(PersistentContext, context)

    async def goto_keep_query(url: str, *, wait_until: str) -> object:
        page.navigation.append((url, wait_until))
        page.events.append("goto")
        if url.rstrip("/").endswith("/invoices/new") or "/invoices/new?" in url:
            page.url = "https://mit.billy.dk/test-org-slug/invoices/new?source=nav"
        else:
            page.url = url
        return object()

    page.goto = goto_keep_query  # type: ignore[method-assign]

    runtime = BrowserRuntime(
        profile_path=tmp_path / "profile",
        egress_manifest_path=write_browser_egress_fixture(tmp_path),
        launcher=launcher,
        org_identity_path=identity_path,
    )

    result = asyncio.run(runtime.ui_invoices_create_open())

    assert result == UiInvoicesCreateOpenSuccess(
        draft_save_chrome_visible=True,
        line_chrome_visible=True,
        shell_markers_present=True,
    )


def test_ui_bills_create_open_returns_auth_required_on_login_page(tmp_path: Path) -> None:
    page = FakeLoginPage()
    context = FakeLoginContext(page)

    async def launcher(profile_path: str, **kwargs: bool) -> PersistentContext:
        return cast(PersistentContext, context)

    runtime = BrowserRuntime(
        profile_path=tmp_path / "profile",
        egress_manifest_path=write_browser_egress_fixture(tmp_path),
        launcher=launcher,
    )

    result = asyncio.run(runtime.ui_bills_create_open())

    assert isinstance(result, ToolError)
    assert result.code is StableErrorCode.AUTH_REQUIRED
    assert page.closed


def test_ui_bills_create_open_returns_success_for_create_form(tmp_path: Path) -> None:
    identity_path = tmp_path / "ui-org-identity.json"
    identity_path.write_text(
        json.dumps({"source": "ui_dashboard_path", "org_slug": "test-org-slug"}) + "\n",
        encoding="utf-8",
    )
    page = FakeLoginPage(
        final_url="https://mit.billy.dk/test-org-slug/dashboard",
        controls=_bills_create_shell_controls(),
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

    result = asyncio.run(runtime.ui_bills_create_open())

    assert result == UiBillsCreateOpenSuccess(
        draft_save_chrome_visible=True,
        line_chrome_visible=True,
        shell_markers_present=True,
    )
    assert any(url.endswith("/bills/new") for url, _ in page.navigation)
    assert "test-org-slug" not in str(result.model_dump())
    assert page.closed
    assert "click:" not in " ".join(page.events)


def test_ui_bills_create_open_returns_ui_changed_for_error_shell(tmp_path: Path) -> None:
    identity_path = tmp_path / "ui-org-identity.json"
    identity_path.write_text(
        json.dumps({"source": "ui_dashboard_path", "org_slug": "test-org-slug"}) + "\n",
        encoding="utf-8",
    )
    controls = _bills_create_shell_controls()
    controls["h1"] = FakeLoginControl(text="Upsedasse!")
    controls["text=Gem som kladde"] = FakeLoginControl(count=0, visible=False)
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

    result = asyncio.run(runtime.ui_bills_create_open())

    assert isinstance(result, ToolError)
    assert result.code is StableErrorCode.UI_CHANGED
    assert "bills create form" in result.message
    assert "test-org-slug" not in str(result.model_dump())
    assert page.closed


def test_ui_bills_create_open_returns_ui_changed_when_heading_missing(
    tmp_path: Path,
) -> None:
    identity_path = tmp_path / "ui-org-identity.json"
    identity_path.write_text(
        json.dumps({"source": "ui_dashboard_path", "org_slug": "test-org-slug"}) + "\n",
        encoding="utf-8",
    )
    controls = _bills_create_shell_controls()
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

    result = asyncio.run(runtime.ui_bills_create_open())

    assert isinstance(result, ToolError)
    assert result.code is StableErrorCode.UI_CHANGED
    assert page.closed


def test_ui_bills_create_open_accepts_create_url_with_query_params(tmp_path: Path) -> None:
    identity_path = tmp_path / "ui-org-identity.json"
    identity_path.write_text(
        json.dumps({"source": "ui_dashboard_path", "org_slug": "test-org-slug"}) + "\n",
        encoding="utf-8",
    )
    page = FakeLoginPage(
        final_url="https://mit.billy.dk/test-org-slug/dashboard",
        controls=_bills_create_shell_controls(),
        follow_goto=True,
    )
    context = FakeLoginContext(page)

    async def launcher(profile_path: str, **kwargs: bool) -> PersistentContext:
        return cast(PersistentContext, context)

    async def goto_keep_query(url: str, *, wait_until: str) -> object:
        page.navigation.append((url, wait_until))
        page.events.append("goto")
        if url.rstrip("/").endswith("/bills/new") or "/bills/new?" in url:
            page.url = "https://mit.billy.dk/test-org-slug/bills/new?source=nav"
        else:
            page.url = url
        return object()

    page.goto = goto_keep_query  # type: ignore[method-assign]

    runtime = BrowserRuntime(
        profile_path=tmp_path / "profile",
        egress_manifest_path=write_browser_egress_fixture(tmp_path),
        launcher=launcher,
        org_identity_path=identity_path,
    )

    result = asyncio.run(runtime.ui_bills_create_open())

    assert result == UiBillsCreateOpenSuccess(
        draft_save_chrome_visible=True,
        line_chrome_visible=True,
        shell_markers_present=True,
    )


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


def test_ui_clients_list_accepts_empty_path_and_kontakter_heading(tmp_path: Path) -> None:
    identity_path = tmp_path / "ui-org-identity.json"
    identity_path.write_text(
        json.dumps({"source": "ui_dashboard_path", "org_slug": "test-org-slug"}) + "\n",
        encoding="utf-8",
    )
    controls = _clients_shell_controls()
    controls["h1"] = FakeLoginControl(text="Kontakter")
    page = FakeLoginPage(
        final_url="https://mit.billy.dk/test-org-slug/dashboard",
        controls=controls,
        follow_goto=True,
    )
    original_goto = page.goto

    async def goto_empty_state(url: str, *, wait_until: str) -> object:
        result = await original_goto(url, wait_until=wait_until)
        if url.rstrip("/").endswith("/clients"):
            page.url = "https://mit.billy.dk/test-org-slug/clients/empty"
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

    result = asyncio.run(runtime.ui_clients_list())

    assert result == UiClientsListSuccess(
        path_class="/:org_slug/clients/empty",
        heading="Kontakter",
        create_action_visible=True,
        shell_markers_present=True,
    )
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
        # research155: Bilag upload surface dual-proved file input present
        "input[type=file]": FakeLoginControl(count=2, visible=True),
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
        file_input_present=True,
        shell_markers_present=True,
    )
    assert any(url.rstrip("/").endswith("/uploads") for url, _ in page.navigation)
    assert "test-org-slug" not in str(result.model_dump())
    assert "fill:" not in " ".join(page.events)
    assert page.closed


def test_ui_uploads_list_returns_ui_changed_when_file_input_missing(tmp_path: Path) -> None:
    identity_path = tmp_path / "ui-org-identity.json"
    identity_path.write_text(
        json.dumps({"source": "ui_dashboard_path", "org_slug": "test-org-slug"}) + "\n",
        encoding="utf-8",
    )
    controls = _uploads_shell_controls()
    controls["input[type=file]"] = FakeLoginControl(count=0, visible=False)
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
        file_input_present=True,
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


def _transactions_shell_controls() -> dict[str, FakeLoginControl]:
    return {
        "input[type='email'][name='email']": FakeLoginControl(count=0, visible=False),
        "input[type='password'][name='password']": FakeLoginControl(count=0, visible=False),
        "input[type='checkbox'][name='remember']": FakeLoginControl(count=0, visible=False),
        "button[data-cy='login-button']": FakeLoginControl(count=0, visible=False),
        "h1": FakeLoginControl(text="Posteringer"),
        "text=Ny postering": FakeLoginControl(text="Ny postering"),
        "text=Overblik": FakeLoginControl(text="Overblik"),
        "text=Fakturering": FakeLoginControl(text="Fakturering"),
        "text=Menu": FakeLoginControl(text="Menu"),
        "text=Upsedasse!": FakeLoginControl(count=0, visible=False),
        "text=Upsedasse": FakeLoginControl(count=0, visible=False),
        "text=Log ind igen": FakeLoginControl(count=0, visible=False),
    }


def _reports_hub_controls() -> dict[str, FakeLoginControl]:
    return {
        "input[type='email'][name='email']": FakeLoginControl(count=0, visible=False),
        "input[type='password'][name='password']": FakeLoginControl(count=0, visible=False),
        "input[type='checkbox'][name='remember']": FakeLoginControl(count=0, visible=False),
        "button[data-cy='login-button']": FakeLoginControl(count=0, visible=False),
        "h1": FakeLoginControl(text="Rapporter"),
        "text=Eksport": FakeLoginControl(text="Eksport"),
        "text=Resultatopgørelse": FakeLoginControl(text="Resultatopgørelse"),
        "text=Balance": FakeLoginControl(text="Balance"),
        "text=Saldobalance": FakeLoginControl(text="Saldobalance"),
        "text=Overblik": FakeLoginControl(text="Overblik"),
        "text=Fakturering": FakeLoginControl(text="Fakturering"),
        "text=Menu": FakeLoginControl(text="Menu"),
        "text=Upsedasse!": FakeLoginControl(count=0, visible=False),
        "text=Upsedasse": FakeLoginControl(count=0, visible=False),
        "text=Log ind igen": FakeLoginControl(count=0, visible=False),
    }


def _vat_declarations_shell_controls() -> dict[str, FakeLoginControl]:
    return {
        "input[type='email'][name='email']": FakeLoginControl(count=0, visible=False),
        "input[type='password'][name='password']": FakeLoginControl(count=0, visible=False),
        "input[type='checkbox'][name='remember']": FakeLoginControl(count=0, visible=False),
        "button[data-cy='login-button']": FakeLoginControl(count=0, visible=False),
        "h1": FakeLoginControl(text="Momsangivelser"),
        "text=Periode": FakeLoginControl(text="Periode"),
        "text=Overblik": FakeLoginControl(text="Overblik"),
        "text=Fakturering": FakeLoginControl(text="Fakturering"),
        "text=Menu": FakeLoginControl(text="Menu"),
        "text=Upsedasse!": FakeLoginControl(count=0, visible=False),
        "text=Upsedasse": FakeLoginControl(count=0, visible=False),
        "text=Log ind igen": FakeLoginControl(count=0, visible=False),
    }


def _exports_shell_controls() -> dict[str, FakeLoginControl]:
    return {
        "input[type='email'][name='email']": FakeLoginControl(count=0, visible=False),
        "input[type='password'][name='password']": FakeLoginControl(count=0, visible=False),
        "input[type='checkbox'][name='remember']": FakeLoginControl(count=0, visible=False),
        "button[data-cy='login-button']": FakeLoginControl(count=0, visible=False),
        "h1": FakeLoginControl(text="Eksportér data"),
        "text=Genveje til rapporten": FakeLoginControl(text="Genveje til rapporten"),
        "text=Eksport": FakeLoginControl(text="Eksport"),
        "text=Debitorliste": FakeLoginControl(text="Debitorliste"),
        "text=Kreditorliste": FakeLoginControl(text="Kreditorliste"),
        "text=Eksportér som SAF-T": FakeLoginControl(text="Eksportér som SAF-T"),
        "text=Overblik": FakeLoginControl(text="Overblik"),
        "text=Fakturering": FakeLoginControl(text="Fakturering"),
        "text=Menu": FakeLoginControl(text="Menu"),
        "text=Upsedasse!": FakeLoginControl(count=0, visible=False),
        "text=Upsedasse": FakeLoginControl(count=0, visible=False),
        "text=Log ind igen": FakeLoginControl(count=0, visible=False),
    }


def _addons_shell_controls() -> dict[str, FakeLoginControl]:
    return {
        "input[type='email'][name='email']": FakeLoginControl(count=0, visible=False),
        "input[type='password'][name='password']": FakeLoginControl(count=0, visible=False),
        "input[type='checkbox'][name='remember']": FakeLoginControl(count=0, visible=False),
        "button[data-cy='login-button']": FakeLoginControl(count=0, visible=False),
        "h1": FakeLoginControl(text="Fordele"),
        "text=Udforsk integrationer": FakeLoginControl(text="Udforsk integrationer"),
        "text=Opret adgangsnøgle": FakeLoginControl(text="Opret adgangsnøgle"),
        "text=Overblik": FakeLoginControl(text="Overblik"),
        "text=Fakturering": FakeLoginControl(text="Fakturering"),
        "text=Menu": FakeLoginControl(text="Menu"),
        "text=Upsedasse!": FakeLoginControl(count=0, visible=False),
        "text=Upsedasse": FakeLoginControl(count=0, visible=False),
        "text=Log ind igen": FakeLoginControl(count=0, visible=False),
    }


def _inventory_shell_controls() -> dict[str, FakeLoginControl]:
    return {
        "input[type='email'][name='email']": FakeLoginControl(count=0, visible=False),
        "input[type='password'][name='password']": FakeLoginControl(count=0, visible=False),
        "input[type='checkbox'][name='remember']": FakeLoginControl(count=0, visible=False),
        "button[data-cy='login-button']": FakeLoginControl(count=0, visible=False),
        "h1": FakeLoginControl(text="Lagermodul"),
        "text=Opret primo": FakeLoginControl(text="Opret primo"),
        "text=Opret produkt": FakeLoginControl(text="Opret produkt"),
        "text=Opret status": FakeLoginControl(text="Opret status"),
        "text=Overblik": FakeLoginControl(text="Overblik"),
        "text=Fakturering": FakeLoginControl(text="Fakturering"),
        "text=Menu": FakeLoginControl(text="Menu"),
        "text=Upsedasse!": FakeLoginControl(count=0, visible=False),
        "text=Upsedasse": FakeLoginControl(count=0, visible=False),
        "text=Log ind igen": FakeLoginControl(count=0, visible=False),
    }


def _settings_company_shell_controls() -> dict[str, FakeLoginControl]:
    return {
        "input[type='email'][name='email']": FakeLoginControl(count=0, visible=False),
        "input[type='password'][name='password']": FakeLoginControl(count=0, visible=False),
        "input[type='checkbox'][name='remember']": FakeLoginControl(count=0, visible=False),
        "button[data-cy='login-button']": FakeLoginControl(count=0, visible=False),
        "h1": FakeLoginControl(text="Indstillinger"),
        "text=Navn og adresse": FakeLoginControl(text="Navn og adresse"),
        "text=Kontaktinformation": FakeLoginControl(text="Kontaktinformation"),
        "text=Gem ændringer": FakeLoginControl(text="Gem ændringer"),
        "text=Overblik": FakeLoginControl(text="Overblik"),
        "text=Fakturering": FakeLoginControl(text="Fakturering"),
        "text=Menu": FakeLoginControl(text="Menu"),
        "text=Upsedasse!": FakeLoginControl(count=0, visible=False),
        "text=Upsedasse": FakeLoginControl(count=0, visible=False),
        "text=Log ind igen": FakeLoginControl(count=0, visible=False),
    }


def _settings_invoicing_shell_controls() -> dict[str, FakeLoginControl]:
    return {
        "input[type='email'][name='email']": FakeLoginControl(count=0, visible=False),
        "input[type='password'][name='password']": FakeLoginControl(count=0, visible=False),
        "input[type='checkbox'][name='remember']": FakeLoginControl(count=0, visible=False),
        "button[data-cy='login-button']": FakeLoginControl(count=0, visible=False),
        "h1": FakeLoginControl(text="Indstillinger"),
        "text=Faktura": FakeLoginControl(text="Faktura"),
        "text=Produkter": FakeLoginControl(text="Produkter"),
        "text=Betalingsmetoder": FakeLoginControl(text="Betalingsmetoder"),
        "text=Standard fakturalogo": FakeLoginControl(text="Standard fakturalogo"),
        "text=Regnskab": FakeLoginControl(count=0, visible=False),
        "text=Køb": FakeLoginControl(count=0, visible=False),
        "text=Kontoplan": FakeLoginControl(count=0, visible=False),
        "text=Navn og adresse": FakeLoginControl(count=0, visible=False),
        "text=Kontaktinformation": FakeLoginControl(count=0, visible=False),
        "text=Gem ændringer": FakeLoginControl(text="Gem ændringer"),
        "text=Overblik": FakeLoginControl(text="Overblik"),
        "text=Fakturering": FakeLoginControl(text="Fakturering"),
        "text=Menu": FakeLoginControl(text="Menu"),
        "text=Upsedasse!": FakeLoginControl(count=0, visible=False),
        "text=Upsedasse": FakeLoginControl(count=0, visible=False),
        "text=Log ind igen": FakeLoginControl(count=0, visible=False),
    }


def _settings_accounting_shell_controls() -> dict[str, FakeLoginControl]:
    return {
        "input[type='email'][name='email']": FakeLoginControl(count=0, visible=False),
        "input[type='password'][name='password']": FakeLoginControl(count=0, visible=False),
        "input[type='checkbox'][name='remember']": FakeLoginControl(count=0, visible=False),
        "button[data-cy='login-button']": FakeLoginControl(count=0, visible=False),
        "h1": FakeLoginControl(text="Indstillinger"),
        "text=Regnskab": FakeLoginControl(text="Regnskab"),
        "text=Køb": FakeLoginControl(text="Køb"),
        "text=Kontoplan": FakeLoginControl(text="Kontoplan"),
        "text=Bankafstemning": FakeLoginControl(text="Bankafstemning"),
        "text=Momsopgørelse": FakeLoginControl(text="Momsopgørelse"),
        "text=Navn og adresse": FakeLoginControl(count=0, visible=False),
        "text=Kontaktinformation": FakeLoginControl(count=0, visible=False),
        "text=Gem ændringer": FakeLoginControl(text="Gem ændringer"),
        "text=Overblik": FakeLoginControl(text="Overblik"),
        "text=Fakturering": FakeLoginControl(text="Fakturering"),
        "text=Menu": FakeLoginControl(text="Menu"),
        "text=Upsedasse!": FakeLoginControl(count=0, visible=False),
        "text=Upsedasse": FakeLoginControl(count=0, visible=False),
        "text=Log ind igen": FakeLoginControl(count=0, visible=False),
    }


def _integrations_soft_empty_controls() -> dict[str, FakeLoginControl]:

    return {
        "input[type='email'][name='email']": FakeLoginControl(count=0, visible=False),
        "input[type='password'][name='password']": FakeLoginControl(count=0, visible=False),
        "input[type='checkbox'][name='remember']": FakeLoginControl(count=0, visible=False),
        "button[data-cy='login-button']": FakeLoginControl(count=0, visible=False),
        "h1": FakeLoginControl(count=0, visible=False),
        "text=Overblik": FakeLoginControl(text="Overblik"),
        "text=Fakturering": FakeLoginControl(text="Fakturering"),
        "text=Menu": FakeLoginControl(text="Menu"),
        "text=Upsedasse!": FakeLoginControl(count=0, visible=False),
        "text=Upsedasse": FakeLoginControl(count=0, visible=False),
        "text=Log ind igen": FakeLoginControl(count=0, visible=False),
    }


def test_ui_daybooks_get_open_returns_auth_required_on_login_page(tmp_path: Path) -> None:
    page = FakeLoginPage(final_url="https://mit.billy.dk/login")
    context = FakeLoginContext(page)

    async def launcher(profile_path: str, **kwargs: bool) -> PersistentContext:
        return cast(PersistentContext, context)

    runtime = BrowserRuntime(
        profile_path=tmp_path / "profile",
        egress_manifest_path=write_browser_egress_fixture(tmp_path),
        launcher=launcher,
    )
    result = asyncio.run(runtime.ui_daybooks_get_open())
    assert isinstance(result, ToolError)
    assert result.code == StableErrorCode.AUTH_REQUIRED


def test_ui_daybooks_get_open_returns_success_for_id_path(tmp_path: Path) -> None:
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
    context = FakeLoginContext(page, daybook_ids=["daybookTestId01"])

    async def launcher(profile_path: str, **kwargs: bool) -> PersistentContext:
        return cast(PersistentContext, context)

    runtime = BrowserRuntime(
        profile_path=tmp_path / "profile",
        egress_manifest_path=write_browser_egress_fixture(tmp_path),
        launcher=launcher,
        org_identity_path=identity_path,
    )

    result = asyncio.run(runtime.ui_daybooks_get_open())

    assert result == UiDaybooksGetOpenSuccess(
        detail_open=True,
        editor_markers_present=True,
        shell_markers_present=True,
    )
    assert any("/daybooks/daybookTestId01" in url for url, _ in page.navigation)
    assert "test-org-slug" not in str(result.model_dump())
    assert "fill:" not in " ".join(page.events)
    assert page.closed


def test_ui_daybooks_get_open_rejects_new_path_as_success(tmp_path: Path) -> None:
    """SPA returns id but if navigation stays on /new, fail closed."""

    identity_path = tmp_path / "ui-org-identity.json"
    identity_path.write_text(
        json.dumps({"source": "ui_dashboard_path", "org_slug": "test-org-slug"}) + "\n",
        encoding="utf-8",
    )
    page = FakeLoginPage(
        final_url="https://mit.billy.dk/test-org-slug/dashboard",
        controls=_daybooks_editor_shell_controls(),
        follow_goto=False,  # stay off get path
    )
    context = FakeLoginContext(page, daybook_ids=["daybookTestId01"])

    async def launcher(profile_path: str, **kwargs: bool) -> PersistentContext:
        return cast(PersistentContext, context)

    runtime = BrowserRuntime(
        profile_path=tmp_path / "profile",
        egress_manifest_path=write_browser_egress_fixture(tmp_path),
        launcher=launcher,
        org_identity_path=identity_path,
    )
    result = asyncio.run(runtime.ui_daybooks_get_open())
    assert isinstance(result, ToolError)
    assert result.code == StableErrorCode.UI_CHANGED


def test_ui_daybooks_get_open_returns_ui_changed_when_list_empty(tmp_path: Path) -> None:
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
    context = FakeLoginContext(page, daybook_ids=[])

    async def launcher(profile_path: str, **kwargs: bool) -> PersistentContext:
        return cast(PersistentContext, context)

    runtime = BrowserRuntime(
        profile_path=tmp_path / "profile",
        egress_manifest_path=write_browser_egress_fixture(tmp_path),
        launcher=launcher,
        org_identity_path=identity_path,
    )
    result = asyncio.run(runtime.ui_daybooks_get_open())
    assert isinstance(result, ToolError)
    assert result.code == StableErrorCode.UI_CHANGED


def _daybooks_delete_shell_controls(
    page_holder: dict[str, FakeLoginPage],
) -> dict[str, FakeLoginControl]:
    def open_mere() -> None:
        page = page_holder["page"]
        page.url = "https://mit.billy.dk/test-org-slug/daybooks/daybookTestId01"
        page.controls["body"] = FakeLoginControl(
            text=(
                "Opret ny kassekladde Tilføj kassekladdelinje Ingen postering valgt Mere "
                "Eksportér som .CSV Eksportér som .XLS Importér Slet Overblik Menu Bogføring"
            )
        )
        page.controls["body"].bind(page.events, "body")
        page.controls["text=Mere"] = FakeLoginControl(text="Mere")
        page.controls["text=Mere"].bind(page.events, "text=Mere")
        page.controls["text=Slet"] = FakeLoginControl(text="Slet")
        page.controls["text=Slet"].bind(page.events, "text=Slet")

    base = _daybooks_editor_shell_controls()
    base["body"] = FakeLoginControl(
        text=(
            "Opret ny kassekladde Tilføj kassekladdelinje Ingen postering valgt Mere "
            "Overblik Menu Bogføring"
        )
    )
    base["text=Mere"] = FakeLoginControl(text="Mere", on_click=open_mere)
    return base


def test_ui_daybooks_delete_open_returns_auth_required_on_login_page(tmp_path: Path) -> None:
    page = FakeLoginPage(final_url="https://mit.billy.dk/login")
    context = FakeLoginContext(page)

    async def launcher(profile_path: str, **kwargs: bool) -> PersistentContext:
        return cast(PersistentContext, context)

    runtime = BrowserRuntime(
        profile_path=tmp_path / "profile",
        egress_manifest_path=write_browser_egress_fixture(tmp_path),
        launcher=launcher,
    )
    result = asyncio.run(runtime.ui_daybooks_delete_open())
    assert isinstance(result, ToolError)
    assert result.code == StableErrorCode.AUTH_REQUIRED


def test_ui_daybooks_delete_open_returns_success_for_mere_delete_chrome(tmp_path: Path) -> None:
    identity_path = tmp_path / "ui-org-identity.json"
    identity_path.write_text(
        json.dumps({"source": "ui_dashboard_path", "org_slug": "test-org-slug"}) + "\n",
        encoding="utf-8",
    )
    page_holder: dict[str, FakeLoginPage] = {}
    page = FakeLoginPage(
        final_url="https://mit.billy.dk/test-org-slug/dashboard",
        controls=_daybooks_delete_shell_controls(page_holder),
        follow_goto=True,
    )
    page_holder["page"] = page
    context = FakeLoginContext(page, daybook_ids=["daybookTestId01"])

    async def launcher(profile_path: str, **kwargs: bool) -> PersistentContext:
        return cast(PersistentContext, context)

    runtime = BrowserRuntime(
        profile_path=tmp_path / "profile",
        egress_manifest_path=write_browser_egress_fixture(tmp_path),
        launcher=launcher,
        org_identity_path=identity_path,
    )

    result = asyncio.run(runtime.ui_daybooks_delete_open())

    assert result == UiDaybooksDeleteOpenSuccess(
        detail_open=True,
        mere_open=True,
        slet_text_visible=True,
        export_menu_visible=True,
        primary_slet_absent=True,
        shell_markers_present=True,
    )
    assert "test-org-slug" not in str(result.model_dump())
    assert page.closed
    assert any("click:text=Mere" in e for e in page.events)
    assert not any("click:text=Slet" in e for e in page.events)


def test_ui_daybooks_delete_open_returns_ui_changed_when_list_empty(tmp_path: Path) -> None:
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
    context = FakeLoginContext(page, daybook_ids=[])

    async def launcher(profile_path: str, **kwargs: bool) -> PersistentContext:
        return cast(PersistentContext, context)

    runtime = BrowserRuntime(
        profile_path=tmp_path / "profile",
        egress_manifest_path=write_browser_egress_fixture(tmp_path),
        launcher=launcher,
        org_identity_path=identity_path,
    )
    result = asyncio.run(runtime.ui_daybooks_delete_open())
    assert isinstance(result, ToolError)
    assert result.code == StableErrorCode.UI_CHANGED


def test_ui_daybook_transactions_create_open_returns_auth_required_on_login_page(
    tmp_path: Path,
) -> None:
    page = FakeLoginPage(final_url="https://mit.billy.dk/login")
    context = FakeLoginContext(page)

    async def launcher(profile_path: str, **kwargs: bool) -> PersistentContext:
        return cast(PersistentContext, context)

    runtime = BrowserRuntime(
        profile_path=tmp_path / "profile",
        egress_manifest_path=write_browser_egress_fixture(tmp_path),
        launcher=launcher,
    )
    result = asyncio.run(runtime.ui_daybook_transactions_create_open())
    assert isinstance(result, ToolError)
    assert result.code == StableErrorCode.AUTH_REQUIRED


def test_ui_daybook_transactions_create_open_returns_success_for_create_chrome(
    tmp_path: Path,
) -> None:
    identity_path = tmp_path / "ui-org-identity.json"
    identity_path.write_text(
        json.dumps({"source": "ui_dashboard_path", "org_slug": "test-org-slug"}) + "\n",
        encoding="utf-8",
    )
    controls = _daybooks_editor_shell_controls()
    controls["body"] = FakeLoginControl(
        text=(
            "Opret ny kassekladde Tilføj kassekladdelinje Ingen postering valgt "
            "Overblik Menu Bogføring"
        )
    )
    page = FakeLoginPage(
        final_url="https://mit.billy.dk/test-org-slug/dashboard",
        controls=controls,
        follow_goto=True,
    )
    context = FakeLoginContext(page, daybook_ids=["daybookTestId01"])

    async def launcher(profile_path: str, **kwargs: bool) -> PersistentContext:
        return cast(PersistentContext, context)

    runtime = BrowserRuntime(
        profile_path=tmp_path / "profile",
        egress_manifest_path=write_browser_egress_fixture(tmp_path),
        launcher=launcher,
        org_identity_path=identity_path,
    )

    result = asyncio.run(runtime.ui_daybook_transactions_create_open())

    assert result == UiDaybookTransactionsCreateOpenSuccess(
        detail_open=True,
        line_add_chrome_visible=True,
        empty_postering_state=True,
        shell_markers_present=True,
    )
    assert any("/daybooks/daybookTestId01" in url for url, _ in page.navigation)
    assert "test-org-slug" not in str(result.model_dump())
    assert "fill:" not in " ".join(page.events)
    assert not any("click:text=Tilføj kassekladdelinje" in e for e in page.events)
    assert page.closed


def test_ui_daybook_transactions_create_open_returns_ui_changed_when_list_empty(
    tmp_path: Path,
) -> None:
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
    context = FakeLoginContext(page, daybook_ids=[])

    async def launcher(profile_path: str, **kwargs: bool) -> PersistentContext:
        return cast(PersistentContext, context)

    runtime = BrowserRuntime(
        profile_path=tmp_path / "profile",
        egress_manifest_path=write_browser_egress_fixture(tmp_path),
        launcher=launcher,
        org_identity_path=identity_path,
    )
    result = asyncio.run(runtime.ui_daybook_transactions_create_open())
    assert isinstance(result, ToolError)
    assert result.code == StableErrorCode.UI_CHANGED


def test_ui_transactions_create_open_returns_auth_required_on_login_page(
    tmp_path: Path,
) -> None:
    page = FakeLoginPage()
    context = FakeLoginContext(page)

    async def launcher(profile_path: str, **kwargs: bool) -> PersistentContext:
        return cast(PersistentContext, context)

    runtime = BrowserRuntime(
        profile_path=tmp_path / "profile",
        egress_manifest_path=write_browser_egress_fixture(tmp_path),
        launcher=launcher,
    )
    result = asyncio.run(runtime.ui_transactions_create_open())
    assert isinstance(result, ToolError)
    assert result.code is StableErrorCode.AUTH_REQUIRED
    assert page.closed


def test_ui_transactions_create_open_returns_success_for_create_chrome(
    tmp_path: Path,
) -> None:
    identity_path = tmp_path / "ui-org-identity.json"
    identity_path.write_text(
        json.dumps({"source": "ui_dashboard_path", "org_slug": "test-org-slug"}) + "\n",
        encoding="utf-8",
    )
    page = FakeLoginPage(
        final_url="https://mit.billy.dk/test-org-slug/dashboard",
        controls=_transactions_shell_controls(),
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

    result = asyncio.run(runtime.ui_transactions_create_open())

    assert result == UiTransactionsCreateOpenSuccess(
        list_open=True,
        create_cta_visible=True,
        shell_markers_present=True,
    )
    assert any("/transactions" in url for url, _ in page.navigation)
    assert "test-org-slug" not in str(result.model_dump())
    assert "fill:" not in " ".join(page.events)
    assert not any("click:text=Ny postering" in e for e in page.events)
    assert page.closed


def test_ui_transactions_create_open_returns_ui_changed_when_cta_missing(
    tmp_path: Path,
) -> None:
    identity_path = tmp_path / "ui-org-identity.json"
    identity_path.write_text(
        json.dumps({"source": "ui_dashboard_path", "org_slug": "test-org-slug"}) + "\n",
        encoding="utf-8",
    )
    controls = _transactions_shell_controls()
    controls["text=Ny postering"] = FakeLoginControl(count=0, visible=False)
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
    result = asyncio.run(runtime.ui_transactions_create_open())
    assert isinstance(result, ToolError)
    assert result.code == StableErrorCode.UI_CHANGED


def test_ui_transactions_list_returns_auth_required_on_login_page(tmp_path: Path) -> None:
    page = FakeLoginPage()
    context = FakeLoginContext(page)

    async def launcher(profile_path: str, **kwargs: bool) -> PersistentContext:
        return cast(PersistentContext, context)

    runtime = BrowserRuntime(
        profile_path=tmp_path / "profile",
        egress_manifest_path=write_browser_egress_fixture(tmp_path),
        launcher=launcher,
    )

    result = asyncio.run(runtime.ui_transactions_list())

    assert isinstance(result, ToolError)
    assert result.code is StableErrorCode.AUTH_REQUIRED
    assert page.closed


def test_ui_transactions_list_returns_success_for_list_shell(tmp_path: Path) -> None:
    identity_path = tmp_path / "ui-org-identity.json"
    identity_path.write_text(
        json.dumps({"source": "ui_dashboard_path", "org_slug": "test-org-slug"}) + "\n",
        encoding="utf-8",
    )
    page = FakeLoginPage(
        final_url="https://mit.billy.dk/test-org-slug/dashboard",
        controls=_transactions_shell_controls(),
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

    result = asyncio.run(runtime.ui_transactions_list())

    assert result == UiTransactionsListSuccess(
        create_action_visible=True,
        shell_markers_present=True,
    )
    assert any("/transactions" in url for url, _ in page.navigation)
    assert "test-org-slug" not in str(result.model_dump())
    assert page.closed


def test_ui_transactions_list_returns_ui_changed_for_error_shell(tmp_path: Path) -> None:
    identity_path = tmp_path / "ui-org-identity.json"
    identity_path.write_text(
        json.dumps({"source": "ui_dashboard_path", "org_slug": "test-org-slug"}) + "\n",
        encoding="utf-8",
    )
    controls = _transactions_shell_controls()
    controls["h1"] = FakeLoginControl(text="Upsedasse!")
    controls["text=Ny postering"] = FakeLoginControl(count=0, visible=False)
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

    result = asyncio.run(runtime.ui_transactions_list())

    assert isinstance(result, ToolError)
    assert result.code is StableErrorCode.UI_CHANGED
    assert "transactions list" in result.message
    assert "test-org-slug" not in str(result.model_dump())
    assert page.closed


def test_ui_transactions_list_returns_ui_changed_when_heading_missing(tmp_path: Path) -> None:
    identity_path = tmp_path / "ui-org-identity.json"
    identity_path.write_text(
        json.dumps({"source": "ui_dashboard_path", "org_slug": "test-org-slug"}) + "\n",
        encoding="utf-8",
    )
    controls = _transactions_shell_controls()
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

    result = asyncio.run(runtime.ui_transactions_list())

    assert isinstance(result, ToolError)
    assert result.code is StableErrorCode.UI_CHANGED
    assert page.closed


def test_ui_transactions_list_rejects_create_shell_path(tmp_path: Path) -> None:
    identity_path = tmp_path / "ui-org-identity.json"
    identity_path.write_text(
        json.dumps({"source": "ui_dashboard_path", "org_slug": "test-org-slug"}) + "\n",
        encoding="utf-8",
    )
    page = FakeLoginPage(
        final_url="https://mit.billy.dk/test-org-slug/dashboard",
        controls=_transactions_shell_controls(),
        follow_goto=True,
    )
    original_goto = page.goto

    async def goto_to_create_shell(url: str, *, wait_until: str) -> object:
        result = await original_goto(url, wait_until=wait_until)
        if url.rstrip("/").endswith("/transactions"):
            page.url = "https://mit.billy.dk/test-org-slug/transactions/new"
            page.controls["h1"] = FakeLoginControl(text="Postering:")
            page.controls["text=Ny postering"] = FakeLoginControl(count=0, visible=False)
        return result

    page.goto = goto_to_create_shell  # type: ignore[method-assign]
    context = FakeLoginContext(page)

    async def launcher(profile_path: str, **kwargs: bool) -> PersistentContext:
        return cast(PersistentContext, context)

    runtime = BrowserRuntime(
        profile_path=tmp_path / "profile",
        egress_manifest_path=write_browser_egress_fixture(tmp_path),
        launcher=launcher,
        org_identity_path=identity_path,
    )

    result = asyncio.run(runtime.ui_transactions_list())

    assert isinstance(result, ToolError)
    assert result.code is StableErrorCode.UI_CHANGED
    assert page.closed


def test_ui_transactions_list_rejects_soft_alias_path(tmp_path: Path) -> None:
    identity_path = tmp_path / "ui-org-identity.json"
    identity_path.write_text(
        json.dumps({"source": "ui_dashboard_path", "org_slug": "test-org-slug"}) + "\n",
        encoding="utf-8",
    )
    page = FakeLoginPage(
        final_url="https://mit.billy.dk/test-org-slug/dashboard",
        controls=_transactions_shell_controls(),
        follow_goto=True,
    )
    original_goto = page.goto

    async def goto_to_alias(url: str, *, wait_until: str) -> object:
        result = await original_goto(url, wait_until=wait_until)
        if url.rstrip("/").endswith("/transactions"):
            page.url = "https://mit.billy.dk/test-org-slug/posteringer"
            page.controls["h1"] = FakeLoginControl(count=0, visible=False)
            page.controls["text=Ny postering"] = FakeLoginControl(count=0, visible=False)
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

    result = asyncio.run(runtime.ui_transactions_list())

    assert isinstance(result, ToolError)
    assert result.code is StableErrorCode.UI_CHANGED
    assert page.closed


def test_ui_transactions_list_accepts_list_url_with_query_params(tmp_path: Path) -> None:
    identity_path = tmp_path / "ui-org-identity.json"
    identity_path.write_text(
        json.dumps({"source": "ui_dashboard_path", "org_slug": "test-org-slug"}) + "\n",
        encoding="utf-8",
    )
    page = FakeLoginPage(
        final_url=("https://mit.billy.dk/test-org-slug/transactions?period=2026"),
        controls=_transactions_shell_controls(),
        follow_goto=True,
    )
    original_goto = page.goto

    async def goto_keep_query(url: str, *, wait_until: str) -> object:
        result = await original_goto(url, wait_until=wait_until)
        if url.rstrip("/").endswith("/transactions"):
            page.url = "https://mit.billy.dk/test-org-slug/transactions?period=2026"
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

    result = asyncio.run(runtime.ui_transactions_list())

    assert result == UiTransactionsListSuccess(
        create_action_visible=True,
        shell_markers_present=True,
    )


def test_ui_reports_open_returns_auth_required_on_login_page(tmp_path: Path) -> None:
    page = FakeLoginPage()
    context = FakeLoginContext(page)

    async def launcher(profile_path: str, **kwargs: bool) -> PersistentContext:
        return cast(PersistentContext, context)

    runtime = BrowserRuntime(
        profile_path=tmp_path / "profile",
        egress_manifest_path=write_browser_egress_fixture(tmp_path),
        launcher=launcher,
    )

    result = asyncio.run(runtime.ui_reports_open())

    assert isinstance(result, ToolError)
    assert result.code is StableErrorCode.AUTH_REQUIRED
    assert page.closed


def test_ui_reports_open_returns_success_for_hub_shell(tmp_path: Path) -> None:
    identity_path = tmp_path / "ui-org-identity.json"
    identity_path.write_text(
        json.dumps({"source": "ui_dashboard_path", "org_slug": "test-org-slug"}) + "\n",
        encoding="utf-8",
    )
    page = FakeLoginPage(
        final_url="https://mit.billy.dk/test-org-slug/dashboard",
        controls=_reports_hub_controls(),
        follow_goto=True,
    )
    original_goto = page.goto

    async def goto_to_hub(url: str, *, wait_until: str) -> object:
        result = await original_goto(url, wait_until=wait_until)
        if url.rstrip("/").endswith("/reports-all"):
            page.url = "https://mit.billy.dk/test-org-slug/reports-all/profit-and-loss?period=2026"
        return result

    page.goto = goto_to_hub  # type: ignore[method-assign]
    context = FakeLoginContext(page)

    async def launcher(profile_path: str, **kwargs: bool) -> PersistentContext:
        return cast(PersistentContext, context)

    runtime = BrowserRuntime(
        profile_path=tmp_path / "profile",
        egress_manifest_path=write_browser_egress_fixture(tmp_path),
        launcher=launcher,
        org_identity_path=identity_path,
    )

    result = asyncio.run(runtime.ui_reports_open())

    assert result == UiReportsOpenSuccess(
        export_action_visible=True,
        shell_markers_present=True,
    )
    assert any("/reports-all" in url for url, _ in page.navigation)
    assert "test-org-slug" not in str(result.model_dump())
    assert page.closed
    assert not any(event.startswith("click:") for event in page.events)


def test_ui_reports_open_returns_ui_changed_for_error_shell(tmp_path: Path) -> None:
    identity_path = tmp_path / "ui-org-identity.json"
    identity_path.write_text(
        json.dumps({"source": "ui_dashboard_path", "org_slug": "test-org-slug"}) + "\n",
        encoding="utf-8",
    )
    controls = _reports_hub_controls()
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

    result = asyncio.run(runtime.ui_reports_open())

    assert isinstance(result, ToolError)
    assert result.code is StableErrorCode.UI_CHANGED
    assert "reports hub" in result.message
    assert "test-org-slug" not in str(result.model_dump())
    assert page.closed


def test_ui_reports_open_returns_ui_changed_when_heading_missing(tmp_path: Path) -> None:
    identity_path = tmp_path / "ui-org-identity.json"
    identity_path.write_text(
        json.dumps({"source": "ui_dashboard_path", "org_slug": "test-org-slug"}) + "\n",
        encoding="utf-8",
    )
    controls = _reports_hub_controls()
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

    result = asyncio.run(runtime.ui_reports_open())

    assert isinstance(result, ToolError)
    assert result.code is StableErrorCode.UI_CHANGED
    assert page.closed


def test_ui_reports_open_rejects_bare_reports_path(tmp_path: Path) -> None:
    identity_path = tmp_path / "ui-org-identity.json"
    identity_path.write_text(
        json.dumps({"source": "ui_dashboard_path", "org_slug": "test-org-slug"}) + "\n",
        encoding="utf-8",
    )
    page = FakeLoginPage(
        final_url="https://mit.billy.dk/test-org-slug/dashboard",
        controls=_reports_hub_controls(),
        follow_goto=True,
    )
    original_goto = page.goto

    async def goto_to_bare(url: str, *, wait_until: str) -> object:
        result = await original_goto(url, wait_until=wait_until)
        if "reports-all" in url:
            page.url = "https://mit.billy.dk/test-org-slug/reports"
            page.controls["h1"] = FakeLoginControl(count=0, visible=False)
        return result

    page.goto = goto_to_bare  # type: ignore[method-assign]
    context = FakeLoginContext(page)

    async def launcher(profile_path: str, **kwargs: bool) -> PersistentContext:
        return cast(PersistentContext, context)

    runtime = BrowserRuntime(
        profile_path=tmp_path / "profile",
        egress_manifest_path=write_browser_egress_fixture(tmp_path),
        launcher=launcher,
        org_identity_path=identity_path,
    )

    result = asyncio.run(runtime.ui_reports_open())

    assert isinstance(result, ToolError)
    assert result.code is StableErrorCode.UI_CHANGED
    assert page.closed


def test_ui_reports_open_rejects_exports_path(tmp_path: Path) -> None:
    identity_path = tmp_path / "ui-org-identity.json"
    identity_path.write_text(
        json.dumps({"source": "ui_dashboard_path", "org_slug": "test-org-slug"}) + "\n",
        encoding="utf-8",
    )
    page = FakeLoginPage(
        final_url="https://mit.billy.dk/test-org-slug/dashboard",
        controls=_reports_hub_controls(),
        follow_goto=True,
    )
    original_goto = page.goto

    async def goto_to_exports(url: str, *, wait_until: str) -> object:
        result = await original_goto(url, wait_until=wait_until)
        if "reports-all" in url:
            page.url = "https://mit.billy.dk/test-org-slug/exports"
            page.controls["h1"] = FakeLoginControl(text="Eksportér data")
        return result

    page.goto = goto_to_exports  # type: ignore[method-assign]
    context = FakeLoginContext(page)

    async def launcher(profile_path: str, **kwargs: bool) -> PersistentContext:
        return cast(PersistentContext, context)

    runtime = BrowserRuntime(
        profile_path=tmp_path / "profile",
        egress_manifest_path=write_browser_egress_fixture(tmp_path),
        launcher=launcher,
        org_identity_path=identity_path,
    )

    result = asyncio.run(runtime.ui_reports_open())

    assert isinstance(result, ToolError)
    assert result.code is StableErrorCode.UI_CHANGED
    assert page.closed


def test_ui_reports_open_accepts_balance_tab_path(tmp_path: Path) -> None:
    identity_path = tmp_path / "ui-org-identity.json"
    identity_path.write_text(
        json.dumps({"source": "ui_dashboard_path", "org_slug": "test-org-slug"}) + "\n",
        encoding="utf-8",
    )
    page = FakeLoginPage(
        final_url="https://mit.billy.dk/test-org-slug/dashboard",
        controls=_reports_hub_controls(),
        follow_goto=True,
    )
    original_goto = page.goto

    async def goto_to_balance(url: str, *, wait_until: str) -> object:
        result = await original_goto(url, wait_until=wait_until)
        if "reports-all" in url:
            page.url = "https://mit.billy.dk/test-org-slug/reports-all/balance?period=2026-07"
        return result

    page.goto = goto_to_balance  # type: ignore[method-assign]
    context = FakeLoginContext(page)

    async def launcher(profile_path: str, **kwargs: bool) -> PersistentContext:
        return cast(PersistentContext, context)

    runtime = BrowserRuntime(
        profile_path=tmp_path / "profile",
        egress_manifest_path=write_browser_egress_fixture(tmp_path),
        launcher=launcher,
        org_identity_path=identity_path,
    )

    result = asyncio.run(runtime.ui_reports_open())

    assert result == UiReportsOpenSuccess(
        export_action_visible=True,
        shell_markers_present=True,
    )


def test_ui_vat_declarations_list_returns_auth_required_on_login_page(tmp_path: Path) -> None:
    page = FakeLoginPage()
    context = FakeLoginContext(page)

    async def launcher(profile_path: str, **kwargs: bool) -> PersistentContext:
        return cast(PersistentContext, context)

    runtime = BrowserRuntime(
        profile_path=tmp_path / "profile",
        egress_manifest_path=write_browser_egress_fixture(tmp_path),
        launcher=launcher,
    )

    result = asyncio.run(runtime.ui_vat_declarations_list())

    assert isinstance(result, ToolError)
    assert result.code is StableErrorCode.AUTH_REQUIRED
    assert page.closed


def test_ui_vat_declarations_list_returns_success_for_list_shell(tmp_path: Path) -> None:
    identity_path = tmp_path / "ui-org-identity.json"
    identity_path.write_text(
        json.dumps({"source": "ui_dashboard_path", "org_slug": "test-org-slug"}) + "\n",
        encoding="utf-8",
    )
    page = FakeLoginPage(
        final_url="https://mit.billy.dk/test-org-slug/dashboard",
        controls=_vat_declarations_shell_controls(),
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

    result = asyncio.run(runtime.ui_vat_declarations_list())

    assert result == UiVatDeclarationsListSuccess(
        period_column_visible=True,
        shell_markers_present=True,
    )
    assert any("vat-declarations" in url for url, _ in page.navigation)
    assert page.closed


def test_ui_vat_declarations_list_returns_ui_changed_for_error_shell(tmp_path: Path) -> None:
    identity_path = tmp_path / "ui-org-identity.json"
    identity_path.write_text(
        json.dumps({"source": "ui_dashboard_path", "org_slug": "test-org-slug"}) + "\n",
        encoding="utf-8",
    )
    controls = _vat_declarations_shell_controls()
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

    result = asyncio.run(runtime.ui_vat_declarations_list())

    assert isinstance(result, ToolError)
    assert result.code is StableErrorCode.UI_CHANGED
    assert "VAT declarations" in result.message
    assert "test-org-slug" not in str(result.model_dump())
    assert page.closed


def test_ui_vat_declarations_list_returns_ui_changed_when_heading_missing(
    tmp_path: Path,
) -> None:
    identity_path = tmp_path / "ui-org-identity.json"
    identity_path.write_text(
        json.dumps({"source": "ui_dashboard_path", "org_slug": "test-org-slug"}) + "\n",
        encoding="utf-8",
    )
    controls = _vat_declarations_shell_controls()
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

    result = asyncio.run(runtime.ui_vat_declarations_list())

    assert isinstance(result, ToolError)
    assert result.code is StableErrorCode.UI_CHANGED
    assert page.closed


def test_ui_vat_declarations_list_rejects_soft_alias_path(tmp_path: Path) -> None:
    identity_path = tmp_path / "ui-org-identity.json"
    identity_path.write_text(
        json.dumps({"source": "ui_dashboard_path", "org_slug": "test-org-slug"}) + "\n",
        encoding="utf-8",
    )
    page = FakeLoginPage(
        final_url="https://mit.billy.dk/test-org-slug/dashboard",
        controls=_vat_declarations_shell_controls(),
        follow_goto=True,
    )
    original_goto = page.goto

    async def goto_to_alias(url: str, *, wait_until: str) -> object:
        result = await original_goto(url, wait_until=wait_until)
        if "vat-declarations" in url:
            page.url = "https://mit.billy.dk/test-org-slug/vat"
            page.controls["h1"] = FakeLoginControl(count=0, visible=False)
            page.controls["text=Periode"] = FakeLoginControl(count=0, visible=False)
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

    result = asyncio.run(runtime.ui_vat_declarations_list())

    assert isinstance(result, ToolError)
    assert result.code is StableErrorCode.UI_CHANGED
    assert page.closed


def test_ui_vat_declarations_list_rejects_underscore_path(tmp_path: Path) -> None:
    identity_path = tmp_path / "ui-org-identity.json"
    identity_path.write_text(
        json.dumps({"source": "ui_dashboard_path", "org_slug": "test-org-slug"}) + "\n",
        encoding="utf-8",
    )
    page = FakeLoginPage(
        final_url="https://mit.billy.dk/test-org-slug/dashboard",
        controls=_vat_declarations_shell_controls(),
        follow_goto=True,
    )
    original_goto = page.goto

    async def goto_underscore(url: str, *, wait_until: str) -> object:
        result = await original_goto(url, wait_until=wait_until)
        if "vat-declarations" in url:
            page.url = "https://mit.billy.dk/test-org-slug/vat_declarations"
            page.controls["h1"] = FakeLoginControl(count=0, visible=False)
        return result

    page.goto = goto_underscore  # type: ignore[method-assign]
    context = FakeLoginContext(page)

    async def launcher(profile_path: str, **kwargs: bool) -> PersistentContext:
        return cast(PersistentContext, context)

    runtime = BrowserRuntime(
        profile_path=tmp_path / "profile",
        egress_manifest_path=write_browser_egress_fixture(tmp_path),
        launcher=launcher,
        org_identity_path=identity_path,
    )

    result = asyncio.run(runtime.ui_vat_declarations_list())

    assert isinstance(result, ToolError)
    assert result.code is StableErrorCode.UI_CHANGED
    assert page.closed


def test_ui_vat_declarations_list_accepts_query_params(tmp_path: Path) -> None:
    identity_path = tmp_path / "ui-org-identity.json"
    identity_path.write_text(
        json.dumps({"source": "ui_dashboard_path", "org_slug": "test-org-slug"}) + "\n",
        encoding="utf-8",
    )
    page = FakeLoginPage(
        final_url="https://mit.billy.dk/test-org-slug/dashboard",
        controls=_vat_declarations_shell_controls(),
        follow_goto=True,
    )
    original_goto = page.goto

    async def goto_keep_query(url: str, *, wait_until: str) -> object:
        result = await original_goto(url, wait_until=wait_until)
        if "vat-declarations" in url:
            page.url = "https://mit.billy.dk/test-org-slug/vat-declarations?period=2026"
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

    result = asyncio.run(runtime.ui_vat_declarations_list())

    assert result == UiVatDeclarationsListSuccess(
        period_column_visible=True,
        shell_markers_present=True,
    )


def test_ui_exports_open_returns_auth_required_on_login_page(tmp_path: Path) -> None:
    page = FakeLoginPage()
    context = FakeLoginContext(page)

    async def launcher(profile_path: str, **kwargs: bool) -> PersistentContext:
        return cast(PersistentContext, context)

    runtime = BrowserRuntime(
        profile_path=tmp_path / "profile",
        egress_manifest_path=write_browser_egress_fixture(tmp_path),
        launcher=launcher,
    )

    result = asyncio.run(runtime.ui_exports_open())

    assert isinstance(result, ToolError)
    assert result.code is StableErrorCode.AUTH_REQUIRED
    assert page.closed


def test_ui_exports_open_returns_success_for_hub_shell(tmp_path: Path) -> None:
    identity_path = tmp_path / "ui-org-identity.json"
    identity_path.write_text(
        json.dumps({"source": "ui_dashboard_path", "org_slug": "test-org-slug"}) + "\n",
        encoding="utf-8",
    )
    page = FakeLoginPage(
        final_url="https://mit.billy.dk/test-org-slug/dashboard",
        controls=_exports_shell_controls(),
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

    result = asyncio.run(runtime.ui_exports_open())

    assert result == UiExportsOpenSuccess(
        saft_export_cta_observed=True,
        shell_markers_present=True,
    )
    assert any("/exports" in url for url, _ in page.navigation)
    assert page.closed


def test_ui_exports_open_returns_ui_changed_for_error_shell(tmp_path: Path) -> None:
    identity_path = tmp_path / "ui-org-identity.json"
    identity_path.write_text(
        json.dumps({"source": "ui_dashboard_path", "org_slug": "test-org-slug"}) + "\n",
        encoding="utf-8",
    )
    controls = _exports_shell_controls()
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

    result = asyncio.run(runtime.ui_exports_open())

    assert isinstance(result, ToolError)
    assert result.code is StableErrorCode.UI_CHANGED
    assert "exports" in result.message.lower()
    assert "test-org-slug" not in str(result.model_dump())
    assert page.closed


def test_ui_exports_open_returns_ui_changed_when_heading_missing(tmp_path: Path) -> None:
    identity_path = tmp_path / "ui-org-identity.json"
    identity_path.write_text(
        json.dumps({"source": "ui_dashboard_path", "org_slug": "test-org-slug"}) + "\n",
        encoding="utf-8",
    )
    controls = _exports_shell_controls()
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

    result = asyncio.run(runtime.ui_exports_open())

    assert isinstance(result, ToolError)
    assert result.code is StableErrorCode.UI_CHANGED
    assert page.closed


def test_ui_exports_open_rejects_soft_alias_path(tmp_path: Path) -> None:
    identity_path = tmp_path / "ui-org-identity.json"
    identity_path.write_text(
        json.dumps({"source": "ui_dashboard_path", "org_slug": "test-org-slug"}) + "\n",
        encoding="utf-8",
    )
    page = FakeLoginPage(
        final_url="https://mit.billy.dk/test-org-slug/dashboard",
        controls=_exports_shell_controls(),
        follow_goto=True,
    )
    original_goto = page.goto

    async def goto_to_alias(url: str, *, wait_until: str) -> object:
        result = await original_goto(url, wait_until=wait_until)
        if "/exports" in url:
            page.url = "https://mit.billy.dk/test-org-slug/export"
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

    result = asyncio.run(runtime.ui_exports_open())

    assert isinstance(result, ToolError)
    assert result.code is StableErrorCode.UI_CHANGED
    assert page.closed


def test_ui_exports_open_accepts_query_params(tmp_path: Path) -> None:
    identity_path = tmp_path / "ui-org-identity.json"
    identity_path.write_text(
        json.dumps({"source": "ui_dashboard_path", "org_slug": "test-org-slug"}) + "\n",
        encoding="utf-8",
    )
    page = FakeLoginPage(
        final_url="https://mit.billy.dk/test-org-slug/dashboard",
        controls=_exports_shell_controls(),
        follow_goto=True,
    )
    original_goto = page.goto

    async def goto_keep_query(url: str, *, wait_until: str) -> object:
        result = await original_goto(url, wait_until=wait_until)
        if "/exports" in url:
            page.url = "https://mit.billy.dk/test-org-slug/exports?tab=list"
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

    result = asyncio.run(runtime.ui_exports_open())

    assert result == UiExportsOpenSuccess(
        saft_export_cta_observed=True,
        shell_markers_present=True,
    )


def test_ui_saft_exports_open_returns_auth_required_on_login_page(tmp_path: Path) -> None:
    page = FakeLoginPage()
    context = FakeLoginContext(page)

    async def launcher(profile_path: str, **kwargs: bool) -> PersistentContext:
        return cast(PersistentContext, context)

    runtime = BrowserRuntime(
        profile_path=tmp_path / "profile",
        egress_manifest_path=write_browser_egress_fixture(tmp_path),
        launcher=launcher,
    )

    result = asyncio.run(runtime.ui_saft_exports_open())

    assert isinstance(result, ToolError)
    assert result.code is StableErrorCode.AUTH_REQUIRED
    assert page.closed


def test_ui_saft_exports_open_returns_success_when_saft_cta_present(tmp_path: Path) -> None:
    identity_path = tmp_path / "ui-org-identity.json"
    identity_path.write_text(
        json.dumps({"source": "ui_dashboard_path", "org_slug": "test-org-slug"}) + "\n",
        encoding="utf-8",
    )
    page = FakeLoginPage(
        final_url="https://mit.billy.dk/test-org-slug/dashboard",
        controls=_exports_shell_controls(),
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

    result = asyncio.run(runtime.ui_saft_exports_open())

    assert result == UiSaftExportsOpenSuccess(shell_markers_present=True)
    assert isinstance(result, UiSaftExportsOpenSuccess)
    assert result.saft_export_cta_observed is True
    assert any("/exports" in url for url, _ in page.navigation)
    assert page.closed


def test_ui_saft_exports_open_returns_ui_changed_when_saft_cta_missing(
    tmp_path: Path,
) -> None:
    identity_path = tmp_path / "ui-org-identity.json"
    identity_path.write_text(
        json.dumps({"source": "ui_dashboard_path", "org_slug": "test-org-slug"}) + "\n",
        encoding="utf-8",
    )
    controls = _exports_shell_controls()
    controls["text=Eksportér som SAF-T"] = FakeLoginControl(count=0, visible=False)
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

    result = asyncio.run(runtime.ui_saft_exports_open())

    assert isinstance(result, ToolError)
    assert result.code is StableErrorCode.UI_CHANGED
    assert "saft" in result.message.lower() or "saf" in result.message.lower()
    assert "test-org-slug" not in str(result.model_dump())
    assert page.closed


def test_ui_saft_exports_open_returns_ui_changed_for_error_shell(tmp_path: Path) -> None:
    identity_path = tmp_path / "ui-org-identity.json"
    identity_path.write_text(
        json.dumps({"source": "ui_dashboard_path", "org_slug": "test-org-slug"}) + "\n",
        encoding="utf-8",
    )
    controls = _exports_shell_controls()
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

    result = asyncio.run(runtime.ui_saft_exports_open())

    assert isinstance(result, ToolError)
    assert result.code is StableErrorCode.UI_CHANGED
    assert page.closed


def test_ui_addons_open_returns_auth_required_on_login_page(tmp_path: Path) -> None:
    page = FakeLoginPage()
    context = FakeLoginContext(page)

    async def launcher(profile_path: str, **kwargs: bool) -> PersistentContext:
        return cast(PersistentContext, context)

    runtime = BrowserRuntime(
        profile_path=tmp_path / "profile",
        egress_manifest_path=write_browser_egress_fixture(tmp_path),
        launcher=launcher,
    )

    result = asyncio.run(runtime.ui_addons_open())

    assert isinstance(result, ToolError)
    assert result.code is StableErrorCode.AUTH_REQUIRED
    assert page.closed


def test_ui_addons_open_returns_success_for_fordele_hub(tmp_path: Path) -> None:
    identity_path = tmp_path / "ui-org-identity.json"
    identity_path.write_text(
        json.dumps({"source": "ui_dashboard_path", "org_slug": "test-org-slug"}) + "\n",
        encoding="utf-8",
    )
    page = FakeLoginPage(
        final_url="https://mit.billy.dk/test-org-slug/dashboard",
        controls=_addons_shell_controls(),
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

    result = asyncio.run(runtime.ui_addons_open())

    assert result == UiAddonsOpenSuccess(shell_markers_present=True)
    assert isinstance(result, UiAddonsOpenSuccess)
    assert result.path_class == "/:org_slug/add-ons"
    assert result.heading == "Fordele"
    assert any("/add-ons" in url for url, _ in page.navigation)
    assert page.closed


def test_ui_addons_open_returns_ui_changed_for_wrong_heading(tmp_path: Path) -> None:
    identity_path = tmp_path / "ui-org-identity.json"
    identity_path.write_text(
        json.dumps({"source": "ui_dashboard_path", "org_slug": "test-org-slug"}) + "\n",
        encoding="utf-8",
    )
    controls = _addons_shell_controls()
    controls["h1"] = FakeLoginControl(text="Integrationer")
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

    result = asyncio.run(runtime.ui_addons_open())

    assert isinstance(result, ToolError)
    assert result.code is StableErrorCode.UI_CHANGED
    assert "test-org-slug" not in str(result.model_dump())
    assert page.closed


def test_ui_addons_open_returns_ui_changed_for_error_shell(tmp_path: Path) -> None:
    identity_path = tmp_path / "ui-org-identity.json"
    identity_path.write_text(
        json.dumps({"source": "ui_dashboard_path", "org_slug": "test-org-slug"}) + "\n",
        encoding="utf-8",
    )
    controls = _addons_shell_controls()
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

    result = asyncio.run(runtime.ui_addons_open())

    assert isinstance(result, ToolError)
    assert result.code is StableErrorCode.UI_CHANGED
    assert page.closed


def test_ui_integrations_open_returns_auth_required_on_login_page(tmp_path: Path) -> None:
    page = FakeLoginPage()
    context = FakeLoginContext(page)

    async def launcher(profile_path: str, **kwargs: bool) -> PersistentContext:
        return cast(PersistentContext, context)

    runtime = BrowserRuntime(
        profile_path=tmp_path / "profile",
        egress_manifest_path=write_browser_egress_fixture(tmp_path),
        launcher=launcher,
    )

    result = asyncio.run(runtime.ui_integrations_open())

    assert isinstance(result, ToolError)
    assert result.code is StableErrorCode.AUTH_REQUIRED
    assert page.closed


def test_ui_integrations_open_returns_success_for_soft_empty_shell(tmp_path: Path) -> None:
    identity_path = tmp_path / "ui-org-identity.json"
    identity_path.write_text(
        json.dumps({"source": "ui_dashboard_path", "org_slug": "test-org-slug"}) + "\n",
        encoding="utf-8",
    )
    page = FakeLoginPage(
        final_url="https://mit.billy.dk/test-org-slug/dashboard",
        controls=_integrations_soft_empty_controls(),
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

    result = asyncio.run(runtime.ui_integrations_open())

    assert result == UiIntegrationsOpenSuccess(shell_markers_present=True)
    assert isinstance(result, UiIntegrationsOpenSuccess)
    assert result.path_class == "/:org_slug/integrations"
    assert result.shell_kind == "soft_empty"
    assert result.dedicated_shell is False
    assert result.same_shell_as_addons is False
    assert result.heading == ""
    assert any("/integrations" in url for url, _ in page.navigation)
    assert page.closed


def test_ui_integrations_open_returns_ui_changed_for_fordele_heading(tmp_path: Path) -> None:
    identity_path = tmp_path / "ui-org-identity.json"
    identity_path.write_text(
        json.dumps({"source": "ui_dashboard_path", "org_slug": "test-org-slug"}) + "\n",
        encoding="utf-8",
    )
    controls = _integrations_soft_empty_controls()
    controls["h1"] = FakeLoginControl(text="Fordele")
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

    result = asyncio.run(runtime.ui_integrations_open())

    assert isinstance(result, ToolError)
    assert result.code is StableErrorCode.UI_CHANGED
    assert "integrations" in result.message
    assert "test-org-slug" not in str(result.model_dump())
    assert page.closed


def test_ui_integrations_open_returns_ui_changed_for_content_h1(tmp_path: Path) -> None:
    identity_path = tmp_path / "ui-org-identity.json"
    identity_path.write_text(
        json.dumps({"source": "ui_dashboard_path", "org_slug": "test-org-slug"}) + "\n",
        encoding="utf-8",
    )
    controls = _integrations_soft_empty_controls()
    controls["h1"] = FakeLoginControl(text="Integrationer")
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

    result = asyncio.run(runtime.ui_integrations_open())

    assert isinstance(result, ToolError)
    assert result.code is StableErrorCode.UI_CHANGED
    assert page.closed


def test_ui_integrations_open_returns_ui_changed_for_error_shell(tmp_path: Path) -> None:
    identity_path = tmp_path / "ui-org-identity.json"
    identity_path.write_text(
        json.dumps({"source": "ui_dashboard_path", "org_slug": "test-org-slug"}) + "\n",
        encoding="utf-8",
    )
    controls = _integrations_soft_empty_controls()
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

    result = asyncio.run(runtime.ui_integrations_open())

    assert isinstance(result, ToolError)
    assert result.code is StableErrorCode.UI_CHANGED
    assert page.closed


def test_ui_inventory_open_returns_auth_required_on_login_page(tmp_path: Path) -> None:
    page = FakeLoginPage()
    context = FakeLoginContext(page)

    async def launcher(profile_path: str, **kwargs: bool) -> PersistentContext:
        return cast(PersistentContext, context)

    runtime = BrowserRuntime(
        profile_path=tmp_path / "profile",
        egress_manifest_path=write_browser_egress_fixture(tmp_path),
        launcher=launcher,
    )

    result = asyncio.run(runtime.ui_inventory_open())

    assert isinstance(result, ToolError)
    assert result.code is StableErrorCode.AUTH_REQUIRED
    assert page.closed


def test_ui_inventory_open_returns_success_for_lagermodul_shell(tmp_path: Path) -> None:
    identity_path = tmp_path / "ui-org-identity.json"
    identity_path.write_text(
        json.dumps({"source": "ui_dashboard_path", "org_slug": "test-org-slug"}) + "\n",
        encoding="utf-8",
    )
    page = FakeLoginPage(
        final_url="https://mit.billy.dk/test-org-slug/dashboard",
        controls=_inventory_shell_controls(),
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

    result = asyncio.run(runtime.ui_inventory_open())

    assert result == UiInventoryOpenSuccess(create_cta_markers_present=True)
    assert isinstance(result, UiInventoryOpenSuccess)
    assert result.path_class == "/:org_slug/inventory"
    assert result.heading == "Lagermodul"
    assert result.shell_kind == "lagermodul"
    assert result.create_cta_markers_present is True
    assert any("/inventory" in url for url, _ in page.navigation)
    assert page.closed


def test_ui_inventory_open_returns_ui_changed_for_wrong_heading(tmp_path: Path) -> None:
    identity_path = tmp_path / "ui-org-identity.json"
    identity_path.write_text(
        json.dumps({"source": "ui_dashboard_path", "org_slug": "test-org-slug"}) + "\n",
        encoding="utf-8",
    )
    controls = _inventory_shell_controls()
    controls["h1"] = FakeLoginControl(text="Produkter")
    controls["[data-cy='search-button']"] = FakeLoginControl(text="Search")
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

    result = asyncio.run(runtime.ui_inventory_open())

    assert isinstance(result, ToolError)
    assert result.code is StableErrorCode.UI_CHANGED
    assert "test-org-slug" not in str(result.model_dump())
    assert page.closed


def test_ui_inventory_open_returns_ui_changed_for_error_shell(tmp_path: Path) -> None:
    identity_path = tmp_path / "ui-org-identity.json"
    identity_path.write_text(
        json.dumps({"source": "ui_dashboard_path", "org_slug": "test-org-slug"}) + "\n",
        encoding="utf-8",
    )
    controls = _inventory_shell_controls()
    controls["h1"] = FakeLoginControl(text="Upsedasse!")
    controls["text=Upsedasse!"] = FakeLoginControl(text="Upsedasse!")
    controls["text=Opret primo"] = FakeLoginControl(count=0, visible=False)
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

    result = asyncio.run(runtime.ui_inventory_open())

    assert isinstance(result, ToolError)
    assert result.code is StableErrorCode.UI_CHANGED
    assert page.closed


def test_ui_settings_company_open_returns_auth_required_on_login_page(tmp_path: Path) -> None:
    page = FakeLoginPage()
    context = FakeLoginContext(page)

    async def launcher(profile_path: str, **kwargs: bool) -> PersistentContext:
        return cast(PersistentContext, context)

    runtime = BrowserRuntime(
        profile_path=tmp_path / "profile",
        egress_manifest_path=write_browser_egress_fixture(tmp_path),
        launcher=launcher,
    )

    result = asyncio.run(runtime.ui_settings_company_open())

    assert isinstance(result, ToolError)
    assert result.code is StableErrorCode.AUTH_REQUIRED
    assert page.closed


def test_ui_settings_company_open_returns_success_for_company_shell(tmp_path: Path) -> None:
    identity_path = tmp_path / "ui-org-identity.json"
    identity_path.write_text(
        json.dumps({"source": "ui_dashboard_path", "org_slug": "test-org-slug"}) + "\n",
        encoding="utf-8",
    )
    page = FakeLoginPage(
        final_url="https://mit.billy.dk/test-org-slug/dashboard",
        controls=_settings_company_shell_controls(),
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

    result = asyncio.run(runtime.ui_settings_company_open())

    assert result == UiSettingsCompanyOpenSuccess(company_panel_markers_present=True)
    assert isinstance(result, UiSettingsCompanyOpenSuccess)
    assert result.path_class == "/:org_slug/settings"
    assert result.heading == "Indstillinger"
    assert result.shell_kind == "settings_company"
    assert result.company_panel_markers_present is True
    assert any(url.rstrip("/").endswith("/settings") for url, _ in page.navigation)
    assert page.closed


def test_ui_settings_company_open_returns_ui_changed_for_wrong_heading(tmp_path: Path) -> None:
    identity_path = tmp_path / "ui-org-identity.json"
    identity_path.write_text(
        json.dumps({"source": "ui_dashboard_path", "org_slug": "test-org-slug"}) + "\n",
        encoding="utf-8",
    )
    controls = _settings_company_shell_controls()
    controls["h1"] = FakeLoginControl(text="Lagermodul")
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

    result = asyncio.run(runtime.ui_settings_company_open())

    assert isinstance(result, ToolError)
    assert result.code is StableErrorCode.UI_CHANGED
    assert "test-org-slug" not in str(result.model_dump())
    assert page.closed


def test_ui_settings_company_open_returns_ui_changed_without_company_markers(
    tmp_path: Path,
) -> None:
    identity_path = tmp_path / "ui-org-identity.json"
    identity_path.write_text(
        json.dumps({"source": "ui_dashboard_path", "org_slug": "test-org-slug"}) + "\n",
        encoding="utf-8",
    )
    controls = _settings_company_shell_controls()
    controls["text=Navn og adresse"] = FakeLoginControl(count=0, visible=False)
    controls["text=Kontaktinformation"] = FakeLoginControl(count=0, visible=False)
    controls["text=Regnskab"] = FakeLoginControl(text="Regnskab")
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

    result = asyncio.run(runtime.ui_settings_company_open())

    assert isinstance(result, ToolError)
    assert result.code is StableErrorCode.UI_CHANGED
    assert page.closed


def test_ui_settings_company_open_returns_ui_changed_for_error_shell(tmp_path: Path) -> None:
    identity_path = tmp_path / "ui-org-identity.json"
    identity_path.write_text(
        json.dumps({"source": "ui_dashboard_path", "org_slug": "test-org-slug"}) + "\n",
        encoding="utf-8",
    )
    controls = _settings_company_shell_controls()
    controls["h1"] = FakeLoginControl(text="Upsedasse!")
    controls["text=Upsedasse!"] = FakeLoginControl(text="Upsedasse!")
    controls["text=Navn og adresse"] = FakeLoginControl(count=0, visible=False)
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

    result = asyncio.run(runtime.ui_settings_company_open())

    assert isinstance(result, ToolError)
    assert result.code is StableErrorCode.UI_CHANGED
    assert page.closed


def _spa_rewrite_accounting_goto(page: FakeLoginPage) -> None:
    """Simulate Billy SPA rewrite: settings/accounting → bare settings hub."""

    original_goto = page.goto

    async def goto_spa(url: str, *, wait_until: str) -> object:
        result = await original_goto(url, wait_until=wait_until)
        if url.rstrip("/").endswith("/settings/accounting"):
            page.url = url[: -len("/accounting")]
        return result

    page.goto = goto_spa  # type: ignore[method-assign]


def test_ui_settings_accounting_open_returns_auth_required_on_login_page(tmp_path: Path) -> None:
    page = FakeLoginPage()
    context = FakeLoginContext(page)

    async def launcher(profile_path: str, **kwargs: bool) -> PersistentContext:
        return cast(PersistentContext, context)

    runtime = BrowserRuntime(
        profile_path=tmp_path / "profile",
        egress_manifest_path=write_browser_egress_fixture(tmp_path),
        launcher=launcher,
    )

    result = asyncio.run(runtime.ui_settings_accounting_open())

    assert isinstance(result, ToolError)
    assert result.code is StableErrorCode.AUTH_REQUIRED
    assert page.closed


def test_ui_settings_accounting_open_returns_success_for_accounting_shell(
    tmp_path: Path,
) -> None:
    identity_path = tmp_path / "ui-org-identity.json"
    identity_path.write_text(
        json.dumps({"source": "ui_dashboard_path", "org_slug": "test-org-slug"}) + "\n",
        encoding="utf-8",
    )
    page = FakeLoginPage(
        final_url="https://mit.billy.dk/test-org-slug/dashboard",
        controls=_settings_accounting_shell_controls(),
        follow_goto=True,
    )
    _spa_rewrite_accounting_goto(page)
    context = FakeLoginContext(page)

    async def launcher(profile_path: str, **kwargs: bool) -> PersistentContext:
        return cast(PersistentContext, context)

    runtime = BrowserRuntime(
        profile_path=tmp_path / "profile",
        egress_manifest_path=write_browser_egress_fixture(tmp_path),
        launcher=launcher,
        org_identity_path=identity_path,
    )

    result = asyncio.run(runtime.ui_settings_accounting_open())

    assert result == UiSettingsAccountingOpenSuccess(accounting_panel_markers_present=True)
    assert isinstance(result, UiSettingsAccountingOpenSuccess)
    assert result.path_class == "/:org_slug/settings"
    assert result.heading == "Indstillinger"
    assert result.shell_kind == "settings_accounting"
    assert result.accounting_panel_markers_present is True
    assert any(url.rstrip("/").endswith("/settings/accounting") for url, _ in page.navigation)
    assert page.url.rstrip("/").endswith("/settings")
    assert page.closed


def test_ui_settings_accounting_open_returns_ui_changed_for_company_panel(
    tmp_path: Path,
) -> None:
    identity_path = tmp_path / "ui-org-identity.json"
    identity_path.write_text(
        json.dumps({"source": "ui_dashboard_path", "org_slug": "test-org-slug"}) + "\n",
        encoding="utf-8",
    )
    # Company markers present → must not classify as accounting even with rail Regnskab.
    controls = _settings_company_shell_controls()
    controls["text=Regnskab"] = FakeLoginControl(text="Regnskab")
    page = FakeLoginPage(
        final_url="https://mit.billy.dk/test-org-slug/dashboard",
        controls=controls,
        follow_goto=True,
    )
    _spa_rewrite_accounting_goto(page)
    context = FakeLoginContext(page)

    async def launcher(profile_path: str, **kwargs: bool) -> PersistentContext:
        return cast(PersistentContext, context)

    runtime = BrowserRuntime(
        profile_path=tmp_path / "profile",
        egress_manifest_path=write_browser_egress_fixture(tmp_path),
        launcher=launcher,
        org_identity_path=identity_path,
    )

    result = asyncio.run(runtime.ui_settings_accounting_open())

    assert isinstance(result, ToolError)
    assert result.code is StableErrorCode.UI_CHANGED
    assert page.closed


def test_ui_settings_accounting_open_returns_ui_changed_without_markers(
    tmp_path: Path,
) -> None:
    identity_path = tmp_path / "ui-org-identity.json"
    identity_path.write_text(
        json.dumps({"source": "ui_dashboard_path", "org_slug": "test-org-slug"}) + "\n",
        encoding="utf-8",
    )
    controls = _settings_accounting_shell_controls()
    controls["text=Kontoplan"] = FakeLoginControl(count=0, visible=False)
    page = FakeLoginPage(
        final_url="https://mit.billy.dk/test-org-slug/dashboard",
        controls=controls,
        follow_goto=True,
    )
    _spa_rewrite_accounting_goto(page)
    context = FakeLoginContext(page)

    async def launcher(profile_path: str, **kwargs: bool) -> PersistentContext:
        return cast(PersistentContext, context)

    runtime = BrowserRuntime(
        profile_path=tmp_path / "profile",
        egress_manifest_path=write_browser_egress_fixture(tmp_path),
        launcher=launcher,
        org_identity_path=identity_path,
    )

    result = asyncio.run(runtime.ui_settings_accounting_open())

    assert isinstance(result, ToolError)
    assert result.code is StableErrorCode.UI_CHANGED
    assert page.closed


def test_ui_settings_accounting_open_returns_ui_changed_for_error_shell(
    tmp_path: Path,
) -> None:
    identity_path = tmp_path / "ui-org-identity.json"
    identity_path.write_text(
        json.dumps({"source": "ui_dashboard_path", "org_slug": "test-org-slug"}) + "\n",
        encoding="utf-8",
    )
    controls = _settings_accounting_shell_controls()
    controls["h1"] = FakeLoginControl(text="Upsedasse!")
    controls["text=Upsedasse!"] = FakeLoginControl(text="Upsedasse!")
    controls["text=Regnskab"] = FakeLoginControl(count=0, visible=False)
    page = FakeLoginPage(
        final_url="https://mit.billy.dk/test-org-slug/dashboard",
        controls=controls,
        follow_goto=True,
    )
    _spa_rewrite_accounting_goto(page)
    context = FakeLoginContext(page)

    async def launcher(profile_path: str, **kwargs: bool) -> PersistentContext:
        return cast(PersistentContext, context)

    runtime = BrowserRuntime(
        profile_path=tmp_path / "profile",
        egress_manifest_path=write_browser_egress_fixture(tmp_path),
        launcher=launcher,
        org_identity_path=identity_path,
    )

    result = asyncio.run(runtime.ui_settings_accounting_open())

    assert isinstance(result, ToolError)
    assert result.code is StableErrorCode.UI_CHANGED
    assert page.closed


def _spa_rewrite_invoicing_goto(page: FakeLoginPage) -> None:
    """Simulate Billy SPA rewrite: settings/invoicing → bare settings hub."""

    original_goto = page.goto

    async def goto_spa(url: str, *, wait_until: str) -> object:
        result = await original_goto(url, wait_until=wait_until)
        if url.rstrip("/").endswith("/settings/invoicing"):
            page.url = url[: -len("/invoicing")]
        return result

    page.goto = goto_spa  # type: ignore[method-assign]


def test_ui_settings_invoicing_open_returns_auth_required_on_login_page(tmp_path: Path) -> None:
    page = FakeLoginPage()
    context = FakeLoginContext(page)

    async def launcher(profile_path: str, **kwargs: bool) -> PersistentContext:
        return cast(PersistentContext, context)

    runtime = BrowserRuntime(
        profile_path=tmp_path / "profile",
        egress_manifest_path=write_browser_egress_fixture(tmp_path),
        launcher=launcher,
    )

    result = asyncio.run(runtime.ui_settings_invoicing_open())

    assert isinstance(result, ToolError)
    assert result.code is StableErrorCode.AUTH_REQUIRED
    assert page.closed


def test_ui_settings_invoicing_open_returns_success_for_invoicing_shell(
    tmp_path: Path,
) -> None:
    identity_path = tmp_path / "ui-org-identity.json"
    identity_path.write_text(
        json.dumps({"source": "ui_dashboard_path", "org_slug": "test-org-slug"}) + "\n",
        encoding="utf-8",
    )
    page = FakeLoginPage(
        final_url="https://mit.billy.dk/test-org-slug/dashboard",
        controls=_settings_invoicing_shell_controls(),
        follow_goto=True,
    )
    _spa_rewrite_invoicing_goto(page)
    context = FakeLoginContext(page)

    async def launcher(profile_path: str, **kwargs: bool) -> PersistentContext:
        return cast(PersistentContext, context)

    runtime = BrowserRuntime(
        profile_path=tmp_path / "profile",
        egress_manifest_path=write_browser_egress_fixture(tmp_path),
        launcher=launcher,
        org_identity_path=identity_path,
    )

    result = asyncio.run(runtime.ui_settings_invoicing_open())

    assert result == UiSettingsInvoicingOpenSuccess(invoicing_panel_markers_present=True)
    assert isinstance(result, UiSettingsInvoicingOpenSuccess)
    assert result.path_class == "/:org_slug/settings"
    assert result.heading == "Indstillinger"
    assert result.shell_kind == "settings_invoicing"
    assert result.invoicing_panel_markers_present is True
    assert any(url.rstrip("/").endswith("/settings/invoicing") for url, _ in page.navigation)
    assert page.url.rstrip("/").endswith("/settings")
    assert page.closed


def test_ui_settings_invoicing_open_returns_ui_changed_for_company_panel(
    tmp_path: Path,
) -> None:
    identity_path = tmp_path / "ui-org-identity.json"
    identity_path.write_text(
        json.dumps({"source": "ui_dashboard_path", "org_slug": "test-org-slug"}) + "\n",
        encoding="utf-8",
    )
    controls = _settings_company_shell_controls()
    controls["text=Faktura"] = FakeLoginControl(text="Faktura")
    page = FakeLoginPage(
        final_url="https://mit.billy.dk/test-org-slug/dashboard",
        controls=controls,
        follow_goto=True,
    )
    _spa_rewrite_invoicing_goto(page)
    context = FakeLoginContext(page)

    async def launcher(profile_path: str, **kwargs: bool) -> PersistentContext:
        return cast(PersistentContext, context)

    runtime = BrowserRuntime(
        profile_path=tmp_path / "profile",
        egress_manifest_path=write_browser_egress_fixture(tmp_path),
        launcher=launcher,
        org_identity_path=identity_path,
    )

    result = asyncio.run(runtime.ui_settings_invoicing_open())

    assert isinstance(result, ToolError)
    assert result.code is StableErrorCode.UI_CHANGED
    assert page.closed


def test_ui_settings_invoicing_open_returns_ui_changed_for_accounting_panel(
    tmp_path: Path,
) -> None:
    identity_path = tmp_path / "ui-org-identity.json"
    identity_path.write_text(
        json.dumps({"source": "ui_dashboard_path", "org_slug": "test-org-slug"}) + "\n",
        encoding="utf-8",
    )
    # Accounting panel with rail Faktura must not classify as invoicing.
    controls = _settings_accounting_shell_controls()
    controls["text=Faktura"] = FakeLoginControl(text="Faktura")
    page = FakeLoginPage(
        final_url="https://mit.billy.dk/test-org-slug/dashboard",
        controls=controls,
        follow_goto=True,
    )
    _spa_rewrite_invoicing_goto(page)
    context = FakeLoginContext(page)

    async def launcher(profile_path: str, **kwargs: bool) -> PersistentContext:
        return cast(PersistentContext, context)

    runtime = BrowserRuntime(
        profile_path=tmp_path / "profile",
        egress_manifest_path=write_browser_egress_fixture(tmp_path),
        launcher=launcher,
        org_identity_path=identity_path,
    )

    result = asyncio.run(runtime.ui_settings_invoicing_open())

    assert isinstance(result, ToolError)
    assert result.code is StableErrorCode.UI_CHANGED
    assert page.closed


def test_ui_settings_invoicing_open_returns_ui_changed_without_markers(
    tmp_path: Path,
) -> None:
    identity_path = tmp_path / "ui-org-identity.json"
    identity_path.write_text(
        json.dumps({"source": "ui_dashboard_path", "org_slug": "test-org-slug"}) + "\n",
        encoding="utf-8",
    )
    controls = _settings_invoicing_shell_controls()
    controls["text=Produkter"] = FakeLoginControl(count=0, visible=False)
    page = FakeLoginPage(
        final_url="https://mit.billy.dk/test-org-slug/dashboard",
        controls=controls,
        follow_goto=True,
    )
    _spa_rewrite_invoicing_goto(page)
    context = FakeLoginContext(page)

    async def launcher(profile_path: str, **kwargs: bool) -> PersistentContext:
        return cast(PersistentContext, context)

    runtime = BrowserRuntime(
        profile_path=tmp_path / "profile",
        egress_manifest_path=write_browser_egress_fixture(tmp_path),
        launcher=launcher,
        org_identity_path=identity_path,
    )

    result = asyncio.run(runtime.ui_settings_invoicing_open())

    assert isinstance(result, ToolError)
    assert result.code is StableErrorCode.UI_CHANGED
    assert page.closed


def test_ui_settings_invoicing_open_returns_ui_changed_for_error_shell(
    tmp_path: Path,
) -> None:
    identity_path = tmp_path / "ui-org-identity.json"
    identity_path.write_text(
        json.dumps({"source": "ui_dashboard_path", "org_slug": "test-org-slug"}) + "\n",
        encoding="utf-8",
    )
    controls = _settings_invoicing_shell_controls()
    controls["h1"] = FakeLoginControl(text="Upsedasse!")
    controls["text=Upsedasse!"] = FakeLoginControl(text="Upsedasse!")
    controls["text=Faktura"] = FakeLoginControl(count=0, visible=False)
    page = FakeLoginPage(
        final_url="https://mit.billy.dk/test-org-slug/dashboard",
        controls=controls,
        follow_goto=True,
    )
    _spa_rewrite_invoicing_goto(page)
    context = FakeLoginContext(page)

    async def launcher(profile_path: str, **kwargs: bool) -> PersistentContext:
        return cast(PersistentContext, context)

    runtime = BrowserRuntime(
        profile_path=tmp_path / "profile",
        egress_manifest_path=write_browser_egress_fixture(tmp_path),
        launcher=launcher,
        org_identity_path=identity_path,
    )

    result = asyncio.run(runtime.ui_settings_invoicing_open())

    assert isinstance(result, ToolError)
    assert result.code is StableErrorCode.UI_CHANGED
    assert page.closed


def _settings_user_shell_controls() -> dict[str, FakeLoginControl]:
    return {
        "input[type='email'][name='email']": FakeLoginControl(count=0, visible=False),
        "input[type='password'][name='password']": FakeLoginControl(count=0, visible=False),
        "input[type='checkbox'][name='remember']": FakeLoginControl(count=0, visible=False),
        "button[data-cy='login-button']": FakeLoginControl(count=0, visible=False),
        "h1": FakeLoginControl(text="Indstillinger"),
        "text=Profil": FakeLoginControl(text="Profil"),
        "text=Billede": FakeLoginControl(text="Billede"),
        "text=Sprog og tema": FakeLoginControl(text="Sprog og tema"),
        "text=Skift adgangskode": FakeLoginControl(text="Skift adgangskode"),
        "text=Faktura": FakeLoginControl(count=0, visible=False),
        "text=Produkter": FakeLoginControl(count=0, visible=False),
        "text=Betalingsmetoder": FakeLoginControl(count=0, visible=False),
        "text=Standard fakturalogo": FakeLoginControl(count=0, visible=False),
        "text=Regnskab": FakeLoginControl(count=0, visible=False),
        "text=Køb": FakeLoginControl(count=0, visible=False),
        "text=Kontoplan": FakeLoginControl(count=0, visible=False),
        "text=Navn og adresse": FakeLoginControl(count=0, visible=False),
        "text=Kontaktinformation": FakeLoginControl(count=0, visible=False),
        "text=Gem ændringer": FakeLoginControl(text="Gem ændringer"),
        "text=Overblik": FakeLoginControl(text="Overblik"),
        "text=Fakturering": FakeLoginControl(text="Fakturering"),
        "text=Menu": FakeLoginControl(text="Menu"),
        "text=Upsedasse!": FakeLoginControl(count=0, visible=False),
        "text=Upsedasse": FakeLoginControl(count=0, visible=False),
        "text=Log ind igen": FakeLoginControl(count=0, visible=False),
    }


def _bind_profil_click_to_user_panel(page: FakeLoginPage) -> None:
    """Hub starts as company; clicking Profil swaps controls to user panel."""

    def apply_user() -> None:
        user = _settings_user_shell_controls()
        page.controls = user
        for selector, control in page.controls.items():
            control.bind(page.events, selector)

    hub = _settings_company_shell_controls()
    hub["text=Profil"] = FakeLoginControl(text="Profil", on_click=apply_user)
    hub["text=Billede"] = FakeLoginControl(count=0, visible=False)
    hub["text=Sprog og tema"] = FakeLoginControl(count=0, visible=False)
    hub["text=Skift adgangskode"] = FakeLoginControl(count=0, visible=False)
    page.controls = hub
    for selector, control in page.controls.items():
        control.bind(page.events, selector)


def test_ui_settings_user_open_returns_auth_required_on_login_page(tmp_path: Path) -> None:
    page = FakeLoginPage()
    context = FakeLoginContext(page)

    async def launcher(profile_path: str, **kwargs: bool) -> PersistentContext:
        return cast(PersistentContext, context)

    runtime = BrowserRuntime(
        profile_path=tmp_path / "profile",
        egress_manifest_path=write_browser_egress_fixture(tmp_path),
        launcher=launcher,
    )

    result = asyncio.run(runtime.ui_settings_user_open())

    assert isinstance(result, ToolError)
    assert result.code is StableErrorCode.AUTH_REQUIRED
    assert page.closed


def test_ui_settings_user_open_returns_success_for_user_shell(tmp_path: Path) -> None:
    identity_path = tmp_path / "ui-org-identity.json"
    identity_path.write_text(
        json.dumps({"source": "ui_dashboard_path", "org_slug": "test-org-slug"}) + "\n",
        encoding="utf-8",
    )
    page = FakeLoginPage(
        final_url="https://mit.billy.dk/test-org-slug/dashboard",
        follow_goto=True,
    )
    _bind_profil_click_to_user_panel(page)
    context = FakeLoginContext(page)

    async def launcher(profile_path: str, **kwargs: bool) -> PersistentContext:
        return cast(PersistentContext, context)

    runtime = BrowserRuntime(
        profile_path=tmp_path / "profile",
        egress_manifest_path=write_browser_egress_fixture(tmp_path),
        launcher=launcher,
        org_identity_path=identity_path,
    )

    result = asyncio.run(runtime.ui_settings_user_open())

    assert result == UiSettingsUserOpenSuccess(user_panel_markers_present=True)
    assert isinstance(result, UiSettingsUserOpenSuccess)
    assert result.path_class == "/:org_slug/settings"
    assert result.heading == "Indstillinger"
    assert result.shell_kind == "settings_user"
    assert result.user_panel_markers_present is True
    assert any(url.rstrip("/").endswith("/settings") for url, _ in page.navigation)
    assert "click:text=Profil" in page.events
    assert page.closed


def test_ui_settings_user_open_returns_ui_changed_for_company_panel_without_click(
    tmp_path: Path,
) -> None:
    identity_path = tmp_path / "ui-org-identity.json"
    identity_path.write_text(
        json.dumps({"source": "ui_dashboard_path", "org_slug": "test-org-slug"}) + "\n",
        encoding="utf-8",
    )
    # Profil missing so click fails; company panel remains.
    controls = _settings_company_shell_controls()
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

    result = asyncio.run(runtime.ui_settings_user_open())

    assert isinstance(result, ToolError)
    assert result.code is StableErrorCode.UI_CHANGED
    assert page.closed


def test_ui_settings_user_open_returns_ui_changed_when_click_leaves_company(
    tmp_path: Path,
) -> None:
    identity_path = tmp_path / "ui-org-identity.json"
    identity_path.write_text(
        json.dumps({"source": "ui_dashboard_path", "org_slug": "test-org-slug"}) + "\n",
        encoding="utf-8",
    )
    controls = _settings_company_shell_controls()
    controls["text=Profil"] = FakeLoginControl(text="Profil")  # click no-ops panel
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

    result = asyncio.run(runtime.ui_settings_user_open())

    assert isinstance(result, ToolError)
    assert result.code is StableErrorCode.UI_CHANGED
    assert page.closed


def test_ui_settings_user_open_returns_ui_changed_for_invoicing_panel(
    tmp_path: Path,
) -> None:
    identity_path = tmp_path / "ui-org-identity.json"
    identity_path.write_text(
        json.dumps({"source": "ui_dashboard_path", "org_slug": "test-org-slug"}) + "\n",
        encoding="utf-8",
    )

    def apply_invoicing() -> None:
        inv = _settings_invoicing_shell_controls()
        inv["text=Profil"] = FakeLoginControl(text="Profil")
        page.controls = inv
        for selector, control in page.controls.items():
            control.bind(page.events, selector)

    page = FakeLoginPage(
        final_url="https://mit.billy.dk/test-org-slug/dashboard",
        follow_goto=True,
    )
    hub = _settings_company_shell_controls()
    hub["text=Profil"] = FakeLoginControl(text="Profil", on_click=apply_invoicing)
    page.controls = hub
    for selector, control in page.controls.items():
        control.bind(page.events, selector)
    context = FakeLoginContext(page)

    async def launcher(profile_path: str, **kwargs: bool) -> PersistentContext:
        return cast(PersistentContext, context)

    runtime = BrowserRuntime(
        profile_path=tmp_path / "profile",
        egress_manifest_path=write_browser_egress_fixture(tmp_path),
        launcher=launcher,
        org_identity_path=identity_path,
    )

    result = asyncio.run(runtime.ui_settings_user_open())

    assert isinstance(result, ToolError)
    assert result.code is StableErrorCode.UI_CHANGED
    assert page.closed


def test_ui_settings_user_open_returns_ui_changed_for_error_shell(tmp_path: Path) -> None:
    identity_path = tmp_path / "ui-org-identity.json"
    identity_path.write_text(
        json.dumps({"source": "ui_dashboard_path", "org_slug": "test-org-slug"}) + "\n",
        encoding="utf-8",
    )
    controls = _settings_user_shell_controls()
    controls["text=Upsedasse"] = FakeLoginControl(text="Upsedasse")
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

    result = asyncio.run(runtime.ui_settings_user_open())

    assert isinstance(result, ToolError)
    assert result.code is StableErrorCode.UI_CHANGED
    assert page.closed


def _settings_vat_shell_controls() -> dict[str, FakeLoginControl]:
    return {
        "input[type='email'][name='email']": FakeLoginControl(count=0, visible=False),
        "input[type='password'][name='password']": FakeLoginControl(count=0, visible=False),
        "input[type='checkbox'][name='remember']": FakeLoginControl(count=0, visible=False),
        "button[data-cy='login-button']": FakeLoginControl(count=0, visible=False),
        "h1": FakeLoginControl(text="Indstillinger"),
        "text=Regelsæt": FakeLoginControl(text="Regelsæt"),
        "text=Satser for salg": FakeLoginControl(text="Satser for salg"),
        "text=Satser for køb": FakeLoginControl(text="Satser for køb"),
        "text=Momssatser": FakeLoginControl(text="Momssatser"),
        "text=Profil": FakeLoginControl(text="Profil"),
        "text=Billede": FakeLoginControl(count=0, visible=False),
        "text=Sprog og tema": FakeLoginControl(count=0, visible=False),
        "text=Skift adgangskode": FakeLoginControl(count=0, visible=False),
        "text=Faktura": FakeLoginControl(count=0, visible=False),
        "text=Produkter": FakeLoginControl(count=0, visible=False),
        "text=Betalingsmetoder": FakeLoginControl(count=0, visible=False),
        "text=Standard fakturalogo": FakeLoginControl(count=0, visible=False),
        "text=Regnskab": FakeLoginControl(count=0, visible=False),
        "text=Køb": FakeLoginControl(count=0, visible=False),
        "text=Kontoplan": FakeLoginControl(count=0, visible=False),
        "text=Navn og adresse": FakeLoginControl(count=0, visible=False),
        "text=Kontaktinformation": FakeLoginControl(count=0, visible=False),
        "text=Opret": FakeLoginControl(text="Opret"),
        "text=Overblik": FakeLoginControl(text="Overblik"),
        "text=Fakturering": FakeLoginControl(text="Fakturering"),
        "text=Menu": FakeLoginControl(text="Menu"),
        "text=Upsedasse!": FakeLoginControl(count=0, visible=False),
        "text=Upsedasse": FakeLoginControl(count=0, visible=False),
        "text=Log ind igen": FakeLoginControl(count=0, visible=False),
    }


def _bind_momssatser_click_to_vat_panel(page: FakeLoginPage) -> None:
    """Hub starts as company; clicking Momssatser swaps controls to VAT panel."""

    def apply_vat() -> None:
        vat = _settings_vat_shell_controls()
        page.controls = vat
        for selector, control in page.controls.items():
            control.bind(page.events, selector)

    hub = _settings_company_shell_controls()
    hub["text=Momssatser"] = FakeLoginControl(text="Momssatser", on_click=apply_vat)
    hub["text=Regelsæt"] = FakeLoginControl(count=0, visible=False)
    hub["text=Satser for salg"] = FakeLoginControl(count=0, visible=False)
    hub["text=Satser for køb"] = FakeLoginControl(count=0, visible=False)
    page.controls = hub
    for selector, control in page.controls.items():
        control.bind(page.events, selector)


def test_ui_settings_vat_open_returns_auth_required_on_login_page(tmp_path: Path) -> None:
    page = FakeLoginPage()
    context = FakeLoginContext(page)

    async def launcher(profile_path: str, **kwargs: bool) -> PersistentContext:
        return cast(PersistentContext, context)

    runtime = BrowserRuntime(
        profile_path=tmp_path / "profile",
        egress_manifest_path=write_browser_egress_fixture(tmp_path),
        launcher=launcher,
    )

    result = asyncio.run(runtime.ui_settings_vat_open())

    assert isinstance(result, ToolError)
    assert result.code is StableErrorCode.AUTH_REQUIRED
    assert page.closed


def test_ui_settings_vat_open_returns_success_for_vat_shell(tmp_path: Path) -> None:
    identity_path = tmp_path / "ui-org-identity.json"
    identity_path.write_text(
        json.dumps({"source": "ui_dashboard_path", "org_slug": "test-org-slug"}) + "\n",
        encoding="utf-8",
    )
    page = FakeLoginPage(
        final_url="https://mit.billy.dk/test-org-slug/dashboard",
        follow_goto=True,
    )
    _bind_momssatser_click_to_vat_panel(page)
    context = FakeLoginContext(page)

    async def launcher(profile_path: str, **kwargs: bool) -> PersistentContext:
        return cast(PersistentContext, context)

    runtime = BrowserRuntime(
        profile_path=tmp_path / "profile",
        egress_manifest_path=write_browser_egress_fixture(tmp_path),
        launcher=launcher,
        org_identity_path=identity_path,
    )

    result = asyncio.run(runtime.ui_settings_vat_open())

    assert result == UiSettingsVatOpenSuccess(vat_panel_markers_present=True)
    assert isinstance(result, UiSettingsVatOpenSuccess)
    assert result.path_class == "/:org_slug/settings"
    assert result.heading == "Indstillinger"
    assert result.shell_kind == "settings_vat"
    assert result.vat_panel_markers_present is True
    assert any(url.rstrip("/").endswith("/settings") for url, _ in page.navigation)
    assert "click:text=Momssatser" in page.events
    assert page.closed


def test_ui_settings_vat_open_returns_ui_changed_for_company_panel_without_click(
    tmp_path: Path,
) -> None:
    identity_path = tmp_path / "ui-org-identity.json"
    identity_path.write_text(
        json.dumps({"source": "ui_dashboard_path", "org_slug": "test-org-slug"}) + "\n",
        encoding="utf-8",
    )
    controls = _settings_company_shell_controls()
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

    result = asyncio.run(runtime.ui_settings_vat_open())

    assert isinstance(result, ToolError)
    assert result.code is StableErrorCode.UI_CHANGED
    assert page.closed


def test_ui_settings_vat_open_returns_ui_changed_when_click_leaves_company(
    tmp_path: Path,
) -> None:
    identity_path = tmp_path / "ui-org-identity.json"
    identity_path.write_text(
        json.dumps({"source": "ui_dashboard_path", "org_slug": "test-org-slug"}) + "\n",
        encoding="utf-8",
    )
    controls = _settings_company_shell_controls()
    controls["text=Momssatser"] = FakeLoginControl(text="Momssatser")
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

    result = asyncio.run(runtime.ui_settings_vat_open())

    assert isinstance(result, ToolError)
    assert result.code is StableErrorCode.UI_CHANGED
    assert page.closed


def test_ui_settings_vat_open_returns_ui_changed_for_user_panel(
    tmp_path: Path,
) -> None:
    identity_path = tmp_path / "ui-org-identity.json"
    identity_path.write_text(
        json.dumps({"source": "ui_dashboard_path", "org_slug": "test-org-slug"}) + "\n",
        encoding="utf-8",
    )

    def apply_user() -> None:
        user = _settings_user_shell_controls()
        user["text=Momssatser"] = FakeLoginControl(text="Momssatser")
        page.controls = user
        for selector, control in page.controls.items():
            control.bind(page.events, selector)

    page = FakeLoginPage(
        final_url="https://mit.billy.dk/test-org-slug/dashboard",
        follow_goto=True,
    )
    hub = _settings_company_shell_controls()
    hub["text=Momssatser"] = FakeLoginControl(text="Momssatser", on_click=apply_user)
    page.controls = hub
    for selector, control in page.controls.items():
        control.bind(page.events, selector)
    context = FakeLoginContext(page)

    async def launcher(profile_path: str, **kwargs: bool) -> PersistentContext:
        return cast(PersistentContext, context)

    runtime = BrowserRuntime(
        profile_path=tmp_path / "profile",
        egress_manifest_path=write_browser_egress_fixture(tmp_path),
        launcher=launcher,
        org_identity_path=identity_path,
    )

    result = asyncio.run(runtime.ui_settings_vat_open())

    assert isinstance(result, ToolError)
    assert result.code is StableErrorCode.UI_CHANGED
    assert page.closed


def test_ui_settings_vat_open_returns_ui_changed_for_error_shell(tmp_path: Path) -> None:
    identity_path = tmp_path / "ui-org-identity.json"
    identity_path.write_text(
        json.dumps({"source": "ui_dashboard_path", "org_slug": "test-org-slug"}) + "\n",
        encoding="utf-8",
    )
    controls = _settings_vat_shell_controls()
    controls["text=Upsedasse"] = FakeLoginControl(text="Upsedasse")
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

    result = asyncio.run(runtime.ui_settings_vat_open())

    assert isinstance(result, ToolError)
    assert result.code is StableErrorCode.UI_CHANGED
    assert page.closed


def _settings_user_organizations_shell_controls() -> dict[str, FakeLoginControl]:
    return {
        "input[type='email'][name='email']": FakeLoginControl(count=0, visible=False),
        "input[type='password'][name='password']": FakeLoginControl(count=0, visible=False),
        "input[type='checkbox'][name='remember']": FakeLoginControl(count=0, visible=False),
        "button[data-cy='login-button']": FakeLoginControl(count=0, visible=False),
        "h1": FakeLoginControl(text="Indstillinger"),
        "text=Virksomheder": FakeLoginControl(text="Virksomheder"),
        "text=Alle organisationer": FakeLoginControl(text="Alle organisationer"),
        "text=Opret organisation": FakeLoginControl(text="Opret organisation"),
        "text=Profil": FakeLoginControl(text="Profil"),
        "text=Billede": FakeLoginControl(count=0, visible=False),
        "text=Sprog og tema": FakeLoginControl(count=0, visible=False),
        "text=Skift adgangskode": FakeLoginControl(count=0, visible=False),
        "text=Brugere": FakeLoginControl(count=0, visible=False),
        "text=Revisorer og bogholdere": FakeLoginControl(count=0, visible=False),
        "text=Faktura": FakeLoginControl(count=0, visible=False),
        "text=Produkter": FakeLoginControl(count=0, visible=False),
        "text=Betalingsmetoder": FakeLoginControl(count=0, visible=False),
        "text=Standard fakturalogo": FakeLoginControl(count=0, visible=False),
        "text=Regnskab": FakeLoginControl(count=0, visible=False),
        "text=Køb": FakeLoginControl(count=0, visible=False),
        "text=Kontoplan": FakeLoginControl(count=0, visible=False),
        "text=Navn og adresse": FakeLoginControl(count=0, visible=False),
        "text=Kontaktinformation": FakeLoginControl(count=0, visible=False),
        "text=Regelsæt": FakeLoginControl(count=0, visible=False),
        "text=Satser for salg": FakeLoginControl(count=0, visible=False),
        "text=Satser for køb": FakeLoginControl(count=0, visible=False),
        "text=Overblik": FakeLoginControl(text="Overblik"),
        "text=Fakturering": FakeLoginControl(text="Fakturering"),
        "text=Menu": FakeLoginControl(text="Menu"),
        "text=Upsedasse!": FakeLoginControl(count=0, visible=False),
        "text=Upsedasse": FakeLoginControl(count=0, visible=False),
        "text=Log ind igen": FakeLoginControl(count=0, visible=False),
    }


def _bind_virksomheder_flow_to_user_orgs_panel(page: FakeLoginPage) -> None:
    """Hub company → Profil intermediate → Virksomheder multi-org panel."""

    def apply_orgs() -> None:
        orgs = _settings_user_organizations_shell_controls()
        page.controls = orgs
        for selector, control in page.controls.items():
            control.bind(page.events, selector)

    def after_profil() -> None:
        mid = _settings_user_shell_controls()
        mid["text=Virksomheder"] = FakeLoginControl(text="Virksomheder", on_click=apply_orgs)
        mid["text=Alle organisationer"] = FakeLoginControl(count=0, visible=False)
        mid["text=Opret organisation"] = FakeLoginControl(count=0, visible=False)
        page.controls = mid
        for selector, control in page.controls.items():
            control.bind(page.events, selector)

    hub = _settings_company_shell_controls()
    hub["text=Profil"] = FakeLoginControl(text="Profil", on_click=after_profil)
    hub["text=Virksomheder"] = FakeLoginControl(count=0, visible=False)
    hub["text=Alle organisationer"] = FakeLoginControl(count=0, visible=False)
    hub["text=Opret organisation"] = FakeLoginControl(count=0, visible=False)
    hub["text=Billede"] = FakeLoginControl(count=0, visible=False)
    hub["text=Sprog og tema"] = FakeLoginControl(count=0, visible=False)
    hub["text=Skift adgangskode"] = FakeLoginControl(count=0, visible=False)
    page.controls = hub
    for selector, control in page.controls.items():
        control.bind(page.events, selector)


def _settings_users_shell_controls() -> dict[str, FakeLoginControl]:
    return {
        "input[type='email'][name='email']": FakeLoginControl(count=0, visible=False),
        "input[type='password'][name='password']": FakeLoginControl(count=0, visible=False),
        "input[type='checkbox'][name='remember']": FakeLoginControl(count=0, visible=False),
        "button[data-cy='login-button']": FakeLoginControl(count=0, visible=False),
        "h1": FakeLoginControl(text="Indstillinger"),
        "text=Brugere": FakeLoginControl(text="Brugere"),
        "text=Revisorer og bogholdere": FakeLoginControl(text="Revisorer og bogholdere"),
        "text=Invitér bruger": FakeLoginControl(text="Invitér bruger"),
        "text=Profil": FakeLoginControl(text="Profil"),
        "text=Billede": FakeLoginControl(count=0, visible=False),
        "text=Sprog og tema": FakeLoginControl(count=0, visible=False),
        "text=Skift adgangskode": FakeLoginControl(count=0, visible=False),
        "text=Faktura": FakeLoginControl(count=0, visible=False),
        "text=Produkter": FakeLoginControl(count=0, visible=False),
        "text=Betalingsmetoder": FakeLoginControl(count=0, visible=False),
        "text=Standard fakturalogo": FakeLoginControl(count=0, visible=False),
        "text=Regnskab": FakeLoginControl(count=0, visible=False),
        "text=Køb": FakeLoginControl(count=0, visible=False),
        "text=Kontoplan": FakeLoginControl(count=0, visible=False),
        "text=Navn og adresse": FakeLoginControl(count=0, visible=False),
        "text=Kontaktinformation": FakeLoginControl(count=0, visible=False),
        "text=Regelsæt": FakeLoginControl(count=0, visible=False),
        "text=Satser for salg": FakeLoginControl(count=0, visible=False),
        "text=Satser for køb": FakeLoginControl(count=0, visible=False),
        "text=Overblik": FakeLoginControl(text="Overblik"),
        "text=Fakturering": FakeLoginControl(text="Fakturering"),
        "text=Menu": FakeLoginControl(text="Menu"),
        "text=Upsedasse!": FakeLoginControl(count=0, visible=False),
        "text=Upsedasse": FakeLoginControl(count=0, visible=False),
        "text=Log ind igen": FakeLoginControl(count=0, visible=False),
    }


def _bind_brugere_click_to_users_panel(page: FakeLoginPage) -> None:
    """Hub starts as company; clicking Brugere swaps controls to users panel."""

    def apply_users() -> None:
        users = _settings_users_shell_controls()
        page.controls = users
        for selector, control in page.controls.items():
            control.bind(page.events, selector)

    hub = _settings_company_shell_controls()
    hub["text=Brugere"] = FakeLoginControl(text="Brugere", on_click=apply_users)
    hub["text=Revisorer og bogholdere"] = FakeLoginControl(count=0, visible=False)
    page.controls = hub
    for selector, control in page.controls.items():
        control.bind(page.events, selector)


def test_ui_settings_users_open_returns_auth_required_on_login_page(tmp_path: Path) -> None:
    page = FakeLoginPage()
    context = FakeLoginContext(page)

    async def launcher(profile_path: str, **kwargs: bool) -> PersistentContext:
        return cast(PersistentContext, context)

    runtime = BrowserRuntime(
        profile_path=tmp_path / "profile",
        egress_manifest_path=write_browser_egress_fixture(tmp_path),
        launcher=launcher,
    )

    result = asyncio.run(runtime.ui_settings_users_open())

    assert isinstance(result, ToolError)
    assert result.code is StableErrorCode.AUTH_REQUIRED
    assert page.closed


def test_ui_settings_users_open_returns_success_for_users_shell(tmp_path: Path) -> None:
    identity_path = tmp_path / "ui-org-identity.json"
    identity_path.write_text(
        json.dumps({"source": "ui_dashboard_path", "org_slug": "test-org-slug"}) + "\n",
        encoding="utf-8",
    )
    page = FakeLoginPage(
        final_url="https://mit.billy.dk/test-org-slug/dashboard",
        follow_goto=True,
    )
    _bind_brugere_click_to_users_panel(page)
    context = FakeLoginContext(page)

    async def launcher(profile_path: str, **kwargs: bool) -> PersistentContext:
        return cast(PersistentContext, context)

    runtime = BrowserRuntime(
        profile_path=tmp_path / "profile",
        egress_manifest_path=write_browser_egress_fixture(tmp_path),
        launcher=launcher,
        org_identity_path=identity_path,
    )

    result = asyncio.run(runtime.ui_settings_users_open())

    assert result == UiSettingsUsersOpenSuccess(users_panel_markers_present=True)
    assert isinstance(result, UiSettingsUsersOpenSuccess)
    assert result.path_class == "/:org_slug/settings"
    assert result.heading == "Indstillinger"
    assert result.shell_kind == "settings_users"
    assert result.users_panel_markers_present is True
    assert any(url.rstrip("/").endswith("/settings") for url, _ in page.navigation)
    assert "click:text=Brugere" in page.events
    assert page.closed


def test_ui_settings_users_open_returns_ui_changed_for_company_panel_without_click(
    tmp_path: Path,
) -> None:
    identity_path = tmp_path / "ui-org-identity.json"
    identity_path.write_text(
        json.dumps({"source": "ui_dashboard_path", "org_slug": "test-org-slug"}) + "\n",
        encoding="utf-8",
    )
    controls = _settings_company_shell_controls()
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

    result = asyncio.run(runtime.ui_settings_users_open())

    assert isinstance(result, ToolError)
    assert result.code is StableErrorCode.UI_CHANGED
    assert page.closed


def test_ui_settings_users_open_returns_ui_changed_when_click_leaves_company(
    tmp_path: Path,
) -> None:
    identity_path = tmp_path / "ui-org-identity.json"
    identity_path.write_text(
        json.dumps({"source": "ui_dashboard_path", "org_slug": "test-org-slug"}) + "\n",
        encoding="utf-8",
    )
    controls = _settings_company_shell_controls()
    controls["text=Brugere"] = FakeLoginControl(text="Brugere")
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

    result = asyncio.run(runtime.ui_settings_users_open())

    assert isinstance(result, ToolError)
    assert result.code is StableErrorCode.UI_CHANGED
    assert page.closed


def test_ui_settings_users_open_returns_ui_changed_for_user_panel(
    tmp_path: Path,
) -> None:
    identity_path = tmp_path / "ui-org-identity.json"
    identity_path.write_text(
        json.dumps({"source": "ui_dashboard_path", "org_slug": "test-org-slug"}) + "\n",
        encoding="utf-8",
    )

    def apply_user() -> None:
        user = _settings_user_shell_controls()
        user["text=Brugere"] = FakeLoginControl(text="Brugere")
        page.controls = user
        for selector, control in page.controls.items():
            control.bind(page.events, selector)

    page = FakeLoginPage(
        final_url="https://mit.billy.dk/test-org-slug/dashboard",
        follow_goto=True,
    )
    hub = _settings_company_shell_controls()
    hub["text=Brugere"] = FakeLoginControl(text="Brugere", on_click=apply_user)
    page.controls = hub
    for selector, control in page.controls.items():
        control.bind(page.events, selector)
    context = FakeLoginContext(page)

    async def launcher(profile_path: str, **kwargs: bool) -> PersistentContext:
        return cast(PersistentContext, context)

    runtime = BrowserRuntime(
        profile_path=tmp_path / "profile",
        egress_manifest_path=write_browser_egress_fixture(tmp_path),
        launcher=launcher,
        org_identity_path=identity_path,
    )

    result = asyncio.run(runtime.ui_settings_users_open())

    assert isinstance(result, ToolError)
    assert result.code is StableErrorCode.UI_CHANGED
    assert page.closed


def test_ui_settings_users_open_returns_ui_changed_for_vat_panel(
    tmp_path: Path,
) -> None:
    identity_path = tmp_path / "ui-org-identity.json"
    identity_path.write_text(
        json.dumps({"source": "ui_dashboard_path", "org_slug": "test-org-slug"}) + "\n",
        encoding="utf-8",
    )

    def apply_vat() -> None:
        vat = _settings_vat_shell_controls()
        vat["text=Brugere"] = FakeLoginControl(text="Brugere")
        page.controls = vat
        for selector, control in page.controls.items():
            control.bind(page.events, selector)

    page = FakeLoginPage(
        final_url="https://mit.billy.dk/test-org-slug/dashboard",
        follow_goto=True,
    )
    hub = _settings_company_shell_controls()
    hub["text=Brugere"] = FakeLoginControl(text="Brugere", on_click=apply_vat)
    page.controls = hub
    for selector, control in page.controls.items():
        control.bind(page.events, selector)
    context = FakeLoginContext(page)

    async def launcher(profile_path: str, **kwargs: bool) -> PersistentContext:
        return cast(PersistentContext, context)

    runtime = BrowserRuntime(
        profile_path=tmp_path / "profile",
        egress_manifest_path=write_browser_egress_fixture(tmp_path),
        launcher=launcher,
        org_identity_path=identity_path,
    )

    result = asyncio.run(runtime.ui_settings_users_open())

    assert isinstance(result, ToolError)
    assert result.code is StableErrorCode.UI_CHANGED
    assert page.closed


def test_ui_settings_users_open_returns_ui_changed_for_error_shell(tmp_path: Path) -> None:
    identity_path = tmp_path / "ui-org-identity.json"
    identity_path.write_text(
        json.dumps({"source": "ui_dashboard_path", "org_slug": "test-org-slug"}) + "\n",
        encoding="utf-8",
    )
    controls = _settings_users_shell_controls()
    controls["text=Upsedasse"] = FakeLoginControl(text="Upsedasse")
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

    result = asyncio.run(runtime.ui_settings_users_open())

    assert isinstance(result, ToolError)
    assert result.code is StableErrorCode.UI_CHANGED
    assert page.closed


def _settings_access_token_shell_controls() -> dict[str, FakeLoginControl]:
    return {
        "input[type='email'][name='email']": FakeLoginControl(count=0, visible=False),
        "input[type='password'][name='password']": FakeLoginControl(count=0, visible=False),
        "input[type='checkbox'][name='remember']": FakeLoginControl(count=0, visible=False),
        "button[data-cy='login-button']": FakeLoginControl(count=0, visible=False),
        "h1": FakeLoginControl(text="Indstillinger"),
        "text=Adgangsnøgler": FakeLoginControl(text="Adgangsnøgler"),
        "text=Opret adgangsnøgle": FakeLoginControl(text="Opret adgangsnøgle"),
        "text=Brugere": FakeLoginControl(count=0, visible=False),
        "text=Revisorer og bogholdere": FakeLoginControl(count=0, visible=False),
        "text=Profil": FakeLoginControl(text="Profil"),
        "text=Billede": FakeLoginControl(count=0, visible=False),
        "text=Sprog og tema": FakeLoginControl(count=0, visible=False),
        "text=Skift adgangskode": FakeLoginControl(count=0, visible=False),
        "text=Faktura": FakeLoginControl(count=0, visible=False),
        "text=Produkter": FakeLoginControl(count=0, visible=False),
        "text=Betalingsmetoder": FakeLoginControl(count=0, visible=False),
        "text=Standard fakturalogo": FakeLoginControl(count=0, visible=False),
        "text=Regnskab": FakeLoginControl(count=0, visible=False),
        "text=Køb": FakeLoginControl(count=0, visible=False),
        "text=Kontoplan": FakeLoginControl(count=0, visible=False),
        "text=Navn og adresse": FakeLoginControl(count=0, visible=False),
        "text=Kontaktinformation": FakeLoginControl(count=0, visible=False),
        "text=Regelsæt": FakeLoginControl(count=0, visible=False),
        "text=Satser for salg": FakeLoginControl(count=0, visible=False),
        "text=Satser for køb": FakeLoginControl(count=0, visible=False),
        "text=Betas": FakeLoginControl(count=0, visible=False),
        "text=Tidlig adgang": FakeLoginControl(count=0, visible=False),
        "text=Overblik": FakeLoginControl(text="Overblik"),
        "text=Fakturering": FakeLoginControl(text="Fakturering"),
        "text=Menu": FakeLoginControl(text="Menu"),
        "text=Upsedasse!": FakeLoginControl(count=0, visible=False),
        "text=Upsedasse": FakeLoginControl(count=0, visible=False),
        "text=Log ind igen": FakeLoginControl(count=0, visible=False),
    }


def _bind_adgangsnogler_click_to_access_token_panel(page: FakeLoginPage) -> None:
    """Hub starts as company; clicking Adgangsnøgler swaps controls to access-token panel."""

    def apply_access_token() -> None:
        panel = _settings_access_token_shell_controls()
        page.controls = panel
        for selector, control in page.controls.items():
            control.bind(page.events, selector)

    hub = _settings_company_shell_controls()
    hub["text=Adgangsnøgler"] = FakeLoginControl(text="Adgangsnøgler", on_click=apply_access_token)
    hub["text=Opret adgangsnøgle"] = FakeLoginControl(count=0, visible=False)
    hub["text=Betas"] = FakeLoginControl(count=0, visible=False)
    hub["text=Tidlig adgang"] = FakeLoginControl(count=0, visible=False)
    page.controls = hub
    for selector, control in page.controls.items():
        control.bind(page.events, selector)


def test_ui_settings_user_organizations_open_returns_auth_required_on_login_page(
    tmp_path: Path,
) -> None:
    page = FakeLoginPage()
    context = FakeLoginContext(page)

    async def launcher(profile_path: str, **kwargs: bool) -> PersistentContext:
        return cast(PersistentContext, context)

    runtime = BrowserRuntime(
        profile_path=tmp_path / "profile",
        egress_manifest_path=write_browser_egress_fixture(tmp_path),
        launcher=launcher,
    )

    result = asyncio.run(runtime.ui_settings_user_organizations_open())

    assert isinstance(result, ToolError)
    assert result.code is StableErrorCode.AUTH_REQUIRED
    assert page.closed


def test_ui_settings_user_organizations_open_returns_success_for_user_orgs_shell(
    tmp_path: Path,
) -> None:
    identity_path = tmp_path / "ui-org-identity.json"
    identity_path.write_text(
        json.dumps({"source": "ui_dashboard_path", "org_slug": "test-org-slug"}) + "\n",
        encoding="utf-8",
    )
    page = FakeLoginPage(
        final_url="https://mit.billy.dk/test-org-slug/dashboard",
        follow_goto=True,
    )
    _bind_virksomheder_flow_to_user_orgs_panel(page)
    context = FakeLoginContext(page)

    async def launcher(profile_path: str, **kwargs: bool) -> PersistentContext:
        return cast(PersistentContext, context)

    runtime = BrowserRuntime(
        profile_path=tmp_path / "profile",
        egress_manifest_path=write_browser_egress_fixture(tmp_path),
        launcher=launcher,
        org_identity_path=identity_path,
    )

    result = asyncio.run(runtime.ui_settings_user_organizations_open())

    assert result == UiSettingsUserOrganizationsOpenSuccess(
        user_organizations_panel_markers_present=True
    )
    assert isinstance(result, UiSettingsUserOrganizationsOpenSuccess)
    assert result.path_class == "/:org_slug/settings"
    assert result.heading == "Indstillinger"
    assert result.shell_kind == "settings_user_organizations"
    assert result.user_organizations_panel_markers_present is True
    assert any(url.rstrip("/").endswith("/settings") for url, _ in page.navigation)
    assert "click:text=Profil" in page.events
    assert "click:text=Virksomheder" in page.events
    assert page.closed


def test_ui_settings_user_organizations_open_returns_ui_changed_for_company_panel(
    tmp_path: Path,
) -> None:
    identity_path = tmp_path / "ui-org-identity.json"
    identity_path.write_text(
        json.dumps({"source": "ui_dashboard_path", "org_slug": "test-org-slug"}) + "\n",
        encoding="utf-8",
    )
    controls = _settings_company_shell_controls()
    # Profil click leaves company; Virksomheder missing → UI_CHANGED
    controls["text=Profil"] = FakeLoginControl(text="Profil")
    controls["text=Virksomheder"] = FakeLoginControl(count=0, visible=False)
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

    result = asyncio.run(runtime.ui_settings_user_organizations_open())

    assert isinstance(result, ToolError)
    assert result.code is StableErrorCode.UI_CHANGED
    assert page.closed


def test_ui_settings_user_organizations_open_returns_ui_changed_for_user_panel_only(
    tmp_path: Path,
) -> None:
    """Profil panel without Virksomheder multi-org markers is not success."""

    identity_path = tmp_path / "ui-org-identity.json"
    identity_path.write_text(
        json.dumps({"source": "ui_dashboard_path", "org_slug": "test-org-slug"}) + "\n",
        encoding="utf-8",
    )
    page = FakeLoginPage(
        final_url="https://mit.billy.dk/test-org-slug/dashboard",
        follow_goto=True,
    )
    _bind_profil_click_to_user_panel(page)

    # Virksomheder click re-applies user panel (wrong shell)
    def stay_user() -> None:
        user = _settings_user_shell_controls()
        user["text=Virksomheder"] = FakeLoginControl(text="Virksomheder", on_click=stay_user)
        user["text=Alle organisationer"] = FakeLoginControl(count=0, visible=False)
        user["text=Opret organisation"] = FakeLoginControl(count=0, visible=False)
        page.controls = user
        for selector, control in page.controls.items():
            control.bind(page.events, selector)

    def after_profil() -> None:
        user = _settings_user_shell_controls()
        user["text=Virksomheder"] = FakeLoginControl(text="Virksomheder", on_click=stay_user)
        user["text=Alle organisationer"] = FakeLoginControl(count=0, visible=False)
        user["text=Opret organisation"] = FakeLoginControl(count=0, visible=False)
        page.controls = user
        for selector, control in page.controls.items():
            control.bind(page.events, selector)

    hub = _settings_company_shell_controls()
    hub["text=Profil"] = FakeLoginControl(text="Profil", on_click=after_profil)
    hub["text=Virksomheder"] = FakeLoginControl(count=0, visible=False)
    hub["text=Alle organisationer"] = FakeLoginControl(count=0, visible=False)
    hub["text=Opret organisation"] = FakeLoginControl(count=0, visible=False)
    hub["text=Billede"] = FakeLoginControl(count=0, visible=False)
    hub["text=Sprog og tema"] = FakeLoginControl(count=0, visible=False)
    hub["text=Skift adgangskode"] = FakeLoginControl(count=0, visible=False)
    page.controls = hub
    for selector, control in page.controls.items():
        control.bind(page.events, selector)

    context = FakeLoginContext(page)

    async def launcher(profile_path: str, **kwargs: bool) -> PersistentContext:
        return cast(PersistentContext, context)

    runtime = BrowserRuntime(
        profile_path=tmp_path / "profile",
        egress_manifest_path=write_browser_egress_fixture(tmp_path),
        launcher=launcher,
        org_identity_path=identity_path,
    )

    result = asyncio.run(runtime.ui_settings_user_organizations_open())

    assert isinstance(result, ToolError)
    assert result.code is StableErrorCode.UI_CHANGED
    assert page.closed


def test_ui_settings_access_token_open_returns_auth_required_on_login_page(
    tmp_path: Path,
) -> None:
    page = FakeLoginPage()
    context = FakeLoginContext(page)

    async def launcher(profile_path: str, **kwargs: bool) -> PersistentContext:
        return cast(PersistentContext, context)

    runtime = BrowserRuntime(
        profile_path=tmp_path / "profile",
        egress_manifest_path=write_browser_egress_fixture(tmp_path),
        launcher=launcher,
    )

    result = asyncio.run(runtime.ui_settings_access_token_open())

    assert isinstance(result, ToolError)
    assert result.code is StableErrorCode.AUTH_REQUIRED
    assert page.closed


def test_ui_settings_access_token_open_returns_success_for_access_token_shell(
    tmp_path: Path,
) -> None:
    identity_path = tmp_path / "ui-org-identity.json"
    identity_path.write_text(
        json.dumps({"source": "ui_dashboard_path", "org_slug": "test-org-slug"}) + "\n",
        encoding="utf-8",
    )
    page = FakeLoginPage(
        final_url="https://mit.billy.dk/test-org-slug/dashboard",
        follow_goto=True,
    )
    _bind_adgangsnogler_click_to_access_token_panel(page)
    context = FakeLoginContext(page)

    async def launcher(profile_path: str, **kwargs: bool) -> PersistentContext:
        return cast(PersistentContext, context)

    runtime = BrowserRuntime(
        profile_path=tmp_path / "profile",
        egress_manifest_path=write_browser_egress_fixture(tmp_path),
        launcher=launcher,
        org_identity_path=identity_path,
    )

    result = asyncio.run(runtime.ui_settings_access_token_open())

    assert result == UiSettingsAccessTokenOpenSuccess(access_token_panel_markers_present=True)
    assert isinstance(result, UiSettingsAccessTokenOpenSuccess)
    assert result.path_class == "/:org_slug/settings"
    assert result.heading == "Indstillinger"
    assert result.shell_kind == "settings_access_token"
    assert result.access_token_panel_markers_present is True
    assert any(url.rstrip("/").endswith("/settings") for url, _ in page.navigation)
    assert "click:text=Adgangsnøgler" in page.events
    assert page.closed


def test_ui_settings_access_token_open_returns_ui_changed_for_company_panel_without_click(
    tmp_path: Path,
) -> None:
    identity_path = tmp_path / "ui-org-identity.json"
    identity_path.write_text(
        json.dumps({"source": "ui_dashboard_path", "org_slug": "test-org-slug"}) + "\n",
        encoding="utf-8",
    )
    controls = _settings_company_shell_controls()
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

    result = asyncio.run(runtime.ui_settings_access_token_open())

    assert isinstance(result, ToolError)
    assert result.code is StableErrorCode.UI_CHANGED
    assert page.closed


def test_ui_settings_access_token_open_returns_ui_changed_when_click_leaves_company(
    tmp_path: Path,
) -> None:
    identity_path = tmp_path / "ui-org-identity.json"
    identity_path.write_text(
        json.dumps({"source": "ui_dashboard_path", "org_slug": "test-org-slug"}) + "\n",
        encoding="utf-8",
    )
    controls = _settings_company_shell_controls()
    controls["text=Adgangsnøgler"] = FakeLoginControl(text="Adgangsnøgler")
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

    result = asyncio.run(runtime.ui_settings_access_token_open())

    assert isinstance(result, ToolError)
    assert result.code is StableErrorCode.UI_CHANGED
    assert page.closed


def test_ui_settings_access_token_open_returns_ui_changed_for_users_panel(
    tmp_path: Path,
) -> None:
    identity_path = tmp_path / "ui-org-identity.json"
    identity_path.write_text(
        json.dumps({"source": "ui_dashboard_path", "org_slug": "test-org-slug"}) + "\n",
        encoding="utf-8",
    )

    def apply_users() -> None:
        users = _settings_users_shell_controls()
        users["text=Adgangsnøgler"] = FakeLoginControl(text="Adgangsnøgler")
        page.controls = users
        for selector, control in page.controls.items():
            control.bind(page.events, selector)

    page = FakeLoginPage(
        final_url="https://mit.billy.dk/test-org-slug/dashboard",
        follow_goto=True,
    )
    hub = _settings_company_shell_controls()
    hub["text=Adgangsnøgler"] = FakeLoginControl(text="Adgangsnøgler", on_click=apply_users)
    page.controls = hub
    for selector, control in page.controls.items():
        control.bind(page.events, selector)
    context = FakeLoginContext(page)

    async def launcher(profile_path: str, **kwargs: bool) -> PersistentContext:
        return cast(PersistentContext, context)

    runtime = BrowserRuntime(
        profile_path=tmp_path / "profile",
        egress_manifest_path=write_browser_egress_fixture(tmp_path),
        launcher=launcher,
        org_identity_path=identity_path,
    )

    result = asyncio.run(runtime.ui_settings_access_token_open())

    assert isinstance(result, ToolError)
    assert result.code is StableErrorCode.UI_CHANGED
    assert page.closed


def test_ui_settings_access_token_open_returns_ui_changed_for_error_shell(
    tmp_path: Path,
) -> None:
    identity_path = tmp_path / "ui-org-identity.json"
    identity_path.write_text(
        json.dumps({"source": "ui_dashboard_path", "org_slug": "test-org-slug"}) + "\n",
        encoding="utf-8",
    )
    controls = _settings_access_token_shell_controls()
    controls["text=Upsedasse"] = FakeLoginControl(text="Upsedasse")
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

    result = asyncio.run(runtime.ui_settings_access_token_open())

    assert isinstance(result, ToolError)
    assert result.code is StableErrorCode.UI_CHANGED
    assert page.closed


def _settings_beta_shell_controls() -> dict[str, FakeLoginControl]:
    return {
        "input[type='email'][name='email']": FakeLoginControl(count=0, visible=False),
        "input[type='password'][name='password']": FakeLoginControl(count=0, visible=False),
        "input[type='checkbox'][name='remember']": FakeLoginControl(count=0, visible=False),
        "button[data-cy='login-button']": FakeLoginControl(count=0, visible=False),
        "h1": FakeLoginControl(text="Indstillinger"),
        "text=Betas": FakeLoginControl(text="Betas"),
        "text=Tidlig adgang": FakeLoginControl(text="Tidlig adgang"),
        "text=Adgangsnøgler": FakeLoginControl(text="Adgangsnøgler"),
        "text=Opret adgangsnøgle": FakeLoginControl(count=0, visible=False),
        "text=Brugere": FakeLoginControl(count=0, visible=False),
        "text=Revisorer og bogholdere": FakeLoginControl(count=0, visible=False),
        "text=Profil": FakeLoginControl(text="Profil"),
        "text=Billede": FakeLoginControl(count=0, visible=False),
        "text=Sprog og tema": FakeLoginControl(count=0, visible=False),
        "text=Skift adgangskode": FakeLoginControl(count=0, visible=False),
        "text=Faktura": FakeLoginControl(count=0, visible=False),
        "text=Produkter": FakeLoginControl(count=0, visible=False),
        "text=Betalingsmetoder": FakeLoginControl(count=0, visible=False),
        "text=Standard fakturalogo": FakeLoginControl(count=0, visible=False),
        "text=Regnskab": FakeLoginControl(count=0, visible=False),
        "text=Køb": FakeLoginControl(count=0, visible=False),
        "text=Kontoplan": FakeLoginControl(count=0, visible=False),
        "text=Navn og adresse": FakeLoginControl(count=0, visible=False),
        "text=Kontaktinformation": FakeLoginControl(count=0, visible=False),
        "text=Regelsæt": FakeLoginControl(count=0, visible=False),
        "text=Satser for salg": FakeLoginControl(count=0, visible=False),
        "text=Satser for køb": FakeLoginControl(count=0, visible=False),
        "text=Overblik": FakeLoginControl(text="Overblik"),
        "text=Fakturering": FakeLoginControl(text="Fakturering"),
        "text=Menu": FakeLoginControl(text="Menu"),
        "text=Upsedasse!": FakeLoginControl(count=0, visible=False),
        "text=Upsedasse": FakeLoginControl(count=0, visible=False),
        "text=Log ind igen": FakeLoginControl(count=0, visible=False),
    }


def _bind_betas_click_to_beta_panel(page: FakeLoginPage) -> None:
    """Hub starts as company; clicking Betas swaps controls to beta panel."""

    def apply_beta() -> None:
        panel = _settings_beta_shell_controls()
        page.controls = panel
        for selector, control in page.controls.items():
            control.bind(page.events, selector)

    hub = _settings_company_shell_controls()
    hub["text=Betas"] = FakeLoginControl(text="Betas", on_click=apply_beta)
    hub["text=Tidlig adgang"] = FakeLoginControl(count=0, visible=False)
    hub["text=Adgangsnøgler"] = FakeLoginControl(count=0, visible=False)
    page.controls = hub
    for selector, control in page.controls.items():
        control.bind(page.events, selector)


def test_ui_settings_beta_open_returns_auth_required_on_login_page(
    tmp_path: Path,
) -> None:
    page = FakeLoginPage()
    context = FakeLoginContext(page)

    async def launcher(profile_path: str, **kwargs: bool) -> PersistentContext:
        return cast(PersistentContext, context)

    runtime = BrowserRuntime(
        profile_path=tmp_path / "profile",
        egress_manifest_path=write_browser_egress_fixture(tmp_path),
        launcher=launcher,
    )

    result = asyncio.run(runtime.ui_settings_beta_open())

    assert isinstance(result, ToolError)
    assert result.code is StableErrorCode.AUTH_REQUIRED
    assert page.closed


def test_ui_settings_beta_open_returns_success_for_beta_shell(
    tmp_path: Path,
) -> None:
    identity_path = tmp_path / "ui-org-identity.json"
    identity_path.write_text(
        json.dumps({"source": "ui_dashboard_path", "org_slug": "test-org-slug"}) + "\n",
        encoding="utf-8",
    )
    page = FakeLoginPage(
        final_url="https://mit.billy.dk/test-org-slug/dashboard",
        follow_goto=True,
    )
    _bind_betas_click_to_beta_panel(page)
    context = FakeLoginContext(page)

    async def launcher(profile_path: str, **kwargs: bool) -> PersistentContext:
        return cast(PersistentContext, context)

    runtime = BrowserRuntime(
        profile_path=tmp_path / "profile",
        egress_manifest_path=write_browser_egress_fixture(tmp_path),
        launcher=launcher,
        org_identity_path=identity_path,
    )

    result = asyncio.run(runtime.ui_settings_beta_open())

    assert result == UiSettingsBetaOpenSuccess(beta_panel_markers_present=True)
    assert isinstance(result, UiSettingsBetaOpenSuccess)
    assert result.path_class == "/:org_slug/settings"
    assert result.heading == "Indstillinger"
    assert result.shell_kind == "settings_beta"
    assert result.beta_panel_markers_present is True
    assert any(url.rstrip("/").endswith("/settings") for url, _ in page.navigation)
    assert "click:text=Betas" in page.events
    assert page.closed


def test_ui_settings_beta_open_returns_ui_changed_for_company_panel_without_click(
    tmp_path: Path,
) -> None:
    identity_path = tmp_path / "ui-org-identity.json"
    identity_path.write_text(
        json.dumps({"source": "ui_dashboard_path", "org_slug": "test-org-slug"}) + "\n",
        encoding="utf-8",
    )
    controls = _settings_company_shell_controls()
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

    result = asyncio.run(runtime.ui_settings_beta_open())

    assert isinstance(result, ToolError)
    assert result.code is StableErrorCode.UI_CHANGED
    assert page.closed


def test_ui_settings_beta_open_returns_ui_changed_when_click_leaves_company(
    tmp_path: Path,
) -> None:
    identity_path = tmp_path / "ui-org-identity.json"
    identity_path.write_text(
        json.dumps({"source": "ui_dashboard_path", "org_slug": "test-org-slug"}) + "\n",
        encoding="utf-8",
    )
    controls = _settings_company_shell_controls()
    controls["text=Betas"] = FakeLoginControl(text="Betas")
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

    result = asyncio.run(runtime.ui_settings_beta_open())

    assert isinstance(result, ToolError)
    assert result.code is StableErrorCode.UI_CHANGED
    assert page.closed


def test_ui_settings_beta_open_returns_ui_changed_for_access_token_panel(
    tmp_path: Path,
) -> None:
    identity_path = tmp_path / "ui-org-identity.json"
    identity_path.write_text(
        json.dumps({"source": "ui_dashboard_path", "org_slug": "test-org-slug"}) + "\n",
        encoding="utf-8",
    )

    def apply_access() -> None:
        access = _settings_access_token_shell_controls()
        access["text=Betas"] = FakeLoginControl(text="Betas")
        page.controls = access
        for selector, control in page.controls.items():
            control.bind(page.events, selector)

    page = FakeLoginPage(
        final_url="https://mit.billy.dk/test-org-slug/dashboard",
        follow_goto=True,
    )
    hub = _settings_company_shell_controls()
    hub["text=Betas"] = FakeLoginControl(text="Betas", on_click=apply_access)
    hub["text=Tidlig adgang"] = FakeLoginControl(count=0, visible=False)
    page.controls = hub
    for selector, control in page.controls.items():
        control.bind(page.events, selector)
    context = FakeLoginContext(page)

    async def launcher(profile_path: str, **kwargs: bool) -> PersistentContext:
        return cast(PersistentContext, context)

    runtime = BrowserRuntime(
        profile_path=tmp_path / "profile",
        egress_manifest_path=write_browser_egress_fixture(tmp_path),
        launcher=launcher,
        org_identity_path=identity_path,
    )

    result = asyncio.run(runtime.ui_settings_beta_open())

    assert isinstance(result, ToolError)
    assert result.code is StableErrorCode.UI_CHANGED
    assert page.closed


def test_ui_settings_beta_open_returns_ui_changed_for_error_shell(
    tmp_path: Path,
) -> None:
    identity_path = tmp_path / "ui-org-identity.json"
    identity_path.write_text(
        json.dumps({"source": "ui_dashboard_path", "org_slug": "test-org-slug"}) + "\n",
        encoding="utf-8",
    )
    controls = _settings_beta_shell_controls()
    controls["text=Upsedasse!"] = FakeLoginControl(text="Upsedasse!")
    controls["text=Upsedasse"] = FakeLoginControl(text="Upsedasse")
    page = FakeLoginPage(
        final_url="https://mit.billy.dk/test-org-slug/dashboard",
        controls=controls,
        follow_goto=True,
    )
    # click Betas but land on error markers still present
    hub = _settings_company_shell_controls()
    hub["text=Betas"] = FakeLoginControl(
        text="Betas",
        on_click=lambda: None,
    )

    # after click keep company with error
    def apply_error() -> None:
        err = _settings_company_shell_controls()
        err["text=Upsedasse!"] = FakeLoginControl(text="Upsedasse!")
        err["text=Upsedasse"] = FakeLoginControl(text="Upsedasse")
        err["text=Betas"] = FakeLoginControl(text="Betas")
        page.controls = err
        for selector, control in page.controls.items():
            control.bind(page.events, selector)

    hub["text=Betas"] = FakeLoginControl(text="Betas", on_click=apply_error)
    page.controls = hub
    for selector, control in page.controls.items():
        control.bind(page.events, selector)
    context = FakeLoginContext(page)

    async def launcher(profile_path: str, **kwargs: bool) -> PersistentContext:
        return cast(PersistentContext, context)

    runtime = BrowserRuntime(
        profile_path=tmp_path / "profile",
        egress_manifest_path=write_browser_egress_fixture(tmp_path),
        launcher=launcher,
        org_identity_path=identity_path,
    )

    result = asyncio.run(runtime.ui_settings_beta_open())

    assert isinstance(result, ToolError)
    assert result.code is StableErrorCode.UI_CHANGED
    assert page.closed


def _settings_subscription_empty_shell_controls() -> dict[str, FakeLoginControl]:
    return {
        "input[type='email'][name='email']": FakeLoginControl(count=0, visible=False),
        "input[type='password'][name='password']": FakeLoginControl(count=0, visible=False),
        "input[type='checkbox'][name='remember']": FakeLoginControl(count=0, visible=False),
        "button[data-cy='login-button']": FakeLoginControl(count=0, visible=False),
        "h1": FakeLoginControl(text="Indstillinger"),
        "h2": FakeLoginControl(count=0, visible=False),
        "text=Abonnement": FakeLoginControl(text="Abonnement"),
        "text=Betas": FakeLoginControl(text="Betas"),
        "text=Tidlig adgang": FakeLoginControl(count=0, visible=False),
        "text=Adgangsnøgler": FakeLoginControl(text="Adgangsnøgler"),
        "text=Opret adgangsnøgle": FakeLoginControl(count=0, visible=False),
        "text=Brugere": FakeLoginControl(text="Brugere"),
        "text=Revisorer og bogholdere": FakeLoginControl(count=0, visible=False),
        "text=Profil": FakeLoginControl(text="Profil"),
        "text=Billede": FakeLoginControl(count=0, visible=False),
        "text=Sprog og tema": FakeLoginControl(count=0, visible=False),
        "text=Skift adgangskode": FakeLoginControl(count=0, visible=False),
        "text=Faktura": FakeLoginControl(text="Faktura"),
        "text=Produkter": FakeLoginControl(count=0, visible=False),
        "text=Betalingsmetoder": FakeLoginControl(count=0, visible=False),
        "text=Standard fakturalogo": FakeLoginControl(count=0, visible=False),
        "text=Regnskab": FakeLoginControl(text="Regnskab"),
        "text=Køb": FakeLoginControl(count=0, visible=False),
        "text=Kontoplan": FakeLoginControl(count=0, visible=False),
        "text=Navn og adresse": FakeLoginControl(count=0, visible=False),
        "text=Kontaktinformation": FakeLoginControl(count=0, visible=False),
        "text=Virksomhedsikon": FakeLoginControl(count=0, visible=False),
        "text=Ejere": FakeLoginControl(count=0, visible=False),
        "text=Regelsæt": FakeLoginControl(count=0, visible=False),
        "text=Satser for salg": FakeLoginControl(count=0, visible=False),
        "text=Satser for køb": FakeLoginControl(count=0, visible=False),
        "text=Overblik": FakeLoginControl(text="Overblik"),
        "text=Fakturering": FakeLoginControl(text="Fakturering"),
        "text=Menu": FakeLoginControl(text="Menu"),
        "text=Upsedasse!": FakeLoginControl(count=0, visible=False),
        "text=Upsedasse": FakeLoginControl(count=0, visible=False),
        "text=Log ind igen": FakeLoginControl(count=0, visible=False),
    }


def _bind_abonnement_click_to_empty_panel(page: FakeLoginPage) -> None:
    """Hub starts as company; clicking Abonnement swaps controls to empty panel."""

    def apply_empty() -> None:
        panel = _settings_subscription_empty_shell_controls()
        page.controls = panel
        for selector, control in page.controls.items():
            control.bind(page.events, selector)

    hub = _settings_company_shell_controls()
    hub["text=Abonnement"] = FakeLoginControl(text="Abonnement", on_click=apply_empty)
    hub["text=Tidlig adgang"] = FakeLoginControl(count=0, visible=False)
    page.controls = hub
    for selector, control in page.controls.items():
        control.bind(page.events, selector)


def test_ui_settings_subscription_open_returns_auth_required_on_login_page(
    tmp_path: Path,
) -> None:
    page = FakeLoginPage()
    context = FakeLoginContext(page)

    async def launcher(profile_path: str, **kwargs: bool) -> PersistentContext:
        return cast(PersistentContext, context)

    runtime = BrowserRuntime(
        profile_path=tmp_path / "profile",
        egress_manifest_path=write_browser_egress_fixture(tmp_path),
        launcher=launcher,
    )

    result = asyncio.run(runtime.ui_settings_subscription_open())

    assert isinstance(result, ToolError)
    assert result.code is StableErrorCode.AUTH_REQUIRED
    assert page.closed


def test_ui_settings_subscription_open_returns_success_for_empty_panel(
    tmp_path: Path,
) -> None:
    identity_path = tmp_path / "ui-org-identity.json"
    identity_path.write_text(
        json.dumps({"source": "ui_dashboard_path", "org_slug": "test-org-slug"}) + "\n",
        encoding="utf-8",
    )
    page = FakeLoginPage(
        final_url="https://mit.billy.dk/test-org-slug/dashboard",
        follow_goto=True,
    )
    _bind_abonnement_click_to_empty_panel(page)
    context = FakeLoginContext(page)

    async def launcher(profile_path: str, **kwargs: bool) -> PersistentContext:
        return cast(PersistentContext, context)

    runtime = BrowserRuntime(
        profile_path=tmp_path / "profile",
        egress_manifest_path=write_browser_egress_fixture(tmp_path),
        launcher=launcher,
        org_identity_path=identity_path,
    )

    result = asyncio.run(runtime.ui_settings_subscription_open())

    assert result == UiSettingsSubscriptionOpenSuccess(empty_panel=True)
    assert isinstance(result, UiSettingsSubscriptionOpenSuccess)
    assert result.path_class == "/:org_slug/settings"
    assert result.heading == "Indstillinger"
    assert result.shell_kind == "settings_subscription"
    assert result.empty_panel is True
    assert any(url.rstrip("/").endswith("/settings") for url, _ in page.navigation)
    assert "click:text=Abonnement" in page.events
    assert page.closed


def test_ui_settings_subscription_open_returns_ui_changed_for_company_without_click(
    tmp_path: Path,
) -> None:
    identity_path = tmp_path / "ui-org-identity.json"
    identity_path.write_text(
        json.dumps({"source": "ui_dashboard_path", "org_slug": "test-org-slug"}) + "\n",
        encoding="utf-8",
    )
    controls = _settings_company_shell_controls()
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

    result = asyncio.run(runtime.ui_settings_subscription_open())

    assert isinstance(result, ToolError)
    assert result.code is StableErrorCode.UI_CHANGED
    assert page.closed


def test_ui_settings_subscription_open_returns_ui_changed_when_click_leaves_company(
    tmp_path: Path,
) -> None:
    identity_path = tmp_path / "ui-org-identity.json"
    identity_path.write_text(
        json.dumps({"source": "ui_dashboard_path", "org_slug": "test-org-slug"}) + "\n",
        encoding="utf-8",
    )
    controls = _settings_company_shell_controls()
    controls["text=Abonnement"] = FakeLoginControl(text="Abonnement")
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

    result = asyncio.run(runtime.ui_settings_subscription_open())

    assert isinstance(result, ToolError)
    assert result.code is StableErrorCode.UI_CHANGED
    assert page.closed


def test_ui_settings_subscription_open_returns_ui_changed_for_beta_panel(
    tmp_path: Path,
) -> None:
    identity_path = tmp_path / "ui-org-identity.json"
    identity_path.write_text(
        json.dumps({"source": "ui_dashboard_path", "org_slug": "test-org-slug"}) + "\n",
        encoding="utf-8",
    )

    def apply_beta() -> None:
        beta = _settings_beta_shell_controls()
        beta["text=Abonnement"] = FakeLoginControl(text="Abonnement")
        page.controls = beta
        for selector, control in page.controls.items():
            control.bind(page.events, selector)

    page = FakeLoginPage(
        final_url="https://mit.billy.dk/test-org-slug/dashboard",
        follow_goto=True,
    )
    hub = _settings_company_shell_controls()
    hub["text=Abonnement"] = FakeLoginControl(text="Abonnement", on_click=apply_beta)
    page.controls = hub
    for selector, control in page.controls.items():
        control.bind(page.events, selector)
    context = FakeLoginContext(page)

    async def launcher(profile_path: str, **kwargs: bool) -> PersistentContext:
        return cast(PersistentContext, context)

    runtime = BrowserRuntime(
        profile_path=tmp_path / "profile",
        egress_manifest_path=write_browser_egress_fixture(tmp_path),
        launcher=launcher,
        org_identity_path=identity_path,
    )

    result = asyncio.run(runtime.ui_settings_subscription_open())

    assert isinstance(result, ToolError)
    assert result.code is StableErrorCode.UI_CHANGED
    assert page.closed


def test_ui_settings_subscription_open_returns_ui_changed_for_error_shell(
    tmp_path: Path,
) -> None:
    identity_path = tmp_path / "ui-org-identity.json"
    identity_path.write_text(
        json.dumps({"source": "ui_dashboard_path", "org_slug": "test-org-slug"}) + "\n",
        encoding="utf-8",
    )

    def apply_err() -> None:
        err = _settings_subscription_empty_shell_controls()
        err["text=Upsedasse!"] = FakeLoginControl(text="Upsedasse!")
        err["text=Upsedasse"] = FakeLoginControl(text="Upsedasse")
        page.controls = err
        for selector, control in page.controls.items():
            control.bind(page.events, selector)

    page = FakeLoginPage(
        final_url="https://mit.billy.dk/test-org-slug/dashboard",
        follow_goto=True,
    )
    hub = _settings_company_shell_controls()
    hub["text=Abonnement"] = FakeLoginControl(text="Abonnement", on_click=apply_err)
    page.controls = hub
    for selector, control in page.controls.items():
        control.bind(page.events, selector)
    context = FakeLoginContext(page)

    async def launcher(profile_path: str, **kwargs: bool) -> PersistentContext:
        return cast(PersistentContext, context)

    runtime = BrowserRuntime(
        profile_path=tmp_path / "profile",
        egress_manifest_path=write_browser_egress_fixture(tmp_path),
        launcher=launcher,
        org_identity_path=identity_path,
    )

    result = asyncio.run(runtime.ui_settings_subscription_open())

    assert isinstance(result, ToolError)
    assert result.code is StableErrorCode.UI_CHANGED
    assert page.closed


def _clients_create_shell_controls() -> dict[str, FakeLoginControl]:
    return {
        "input[type='email'][name='email']": FakeLoginControl(count=0, visible=False),
        "input[type='password'][name='password']": FakeLoginControl(count=0, visible=False),
        "input[type='checkbox'][name='remember']": FakeLoginControl(count=0, visible=False),
        "button[data-cy='login-button']": FakeLoginControl(count=0, visible=False),
        "h1": FakeLoginControl(text="Kunder"),
        "text=Opret kontakt": FakeLoginControl(text="Opret kontakt"),
        "input[name='name']": FakeLoginControl(text=""),
        "input[name='registrationNo']": FakeLoginControl(text=""),
        "input[name='street']": FakeLoginControl(text=""),
        "input[name='person_email']": FakeLoginControl(text=""),
        "text=Overblik": FakeLoginControl(text="Overblik"),
        "text=Menu": FakeLoginControl(text="Menu"),
        "text=Upsedasse!": FakeLoginControl(count=0, visible=False),
        "text=Upsedasse": FakeLoginControl(count=0, visible=False),
        "text=Log ind igen": FakeLoginControl(count=0, visible=False),
    }


def test_ui_clients_create_open_returns_auth_required_on_login_page(tmp_path: Path) -> None:
    page = FakeLoginPage()
    context = FakeLoginContext(page)

    async def launcher(profile_path: str, **kwargs: bool) -> PersistentContext:
        return cast(PersistentContext, context)

    runtime = BrowserRuntime(
        profile_path=tmp_path / "profile",
        egress_manifest_path=write_browser_egress_fixture(tmp_path),
        launcher=launcher,
    )

    result = asyncio.run(runtime.ui_clients_create_open())

    assert isinstance(result, ToolError)
    assert result.code is StableErrorCode.AUTH_REQUIRED
    assert page.closed


def test_ui_clients_create_open_returns_success_for_create_dialog(tmp_path: Path) -> None:
    identity_path = tmp_path / "ui-org-identity.json"
    identity_path.write_text(
        json.dumps({"source": "ui_dashboard_path", "org_slug": "test-org-slug"}) + "\n",
        encoding="utf-8",
    )
    page = FakeLoginPage(
        final_url="https://mit.billy.dk/test-org-slug/dashboard",
        controls=_clients_create_shell_controls(),
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

    result = asyncio.run(runtime.ui_clients_create_open())

    assert result == UiClientsCreateOpenSuccess(
        create_dialog_open=True,
        name_field_visible=True,
        registration_no_field_present=True,
        address_or_person_fields_present=True,
        shell_markers_present=True,
    )
    assert any(url.rstrip("/").endswith("/clients") for url, _ in page.navigation)
    assert not any("/clients/new" in url for url, _ in page.navigation)
    assert "test-org-slug" not in str(result.model_dump())
    assert page.closed
    # Form was already signature-complete (dialog fields present); no submit clicks.
    assert not any("click:text=Gem" in e for e in page.events)


def test_ui_clients_create_open_accepts_empty_path_and_kontakter_heading(
    tmp_path: Path,
) -> None:
    identity_path = tmp_path / "ui-org-identity.json"
    identity_path.write_text(
        json.dumps({"source": "ui_dashboard_path", "org_slug": "test-org-slug"}) + "\n",
        encoding="utf-8",
    )
    controls = _clients_create_shell_controls()
    controls["h1"] = FakeLoginControl(text="Kontakter")
    page = FakeLoginPage(
        final_url="https://mit.billy.dk/test-org-slug/dashboard",
        controls=controls,
        follow_goto=True,
    )
    original_goto = page.goto

    async def goto_empty_state(url: str, *, wait_until: str) -> object:
        result = await original_goto(url, wait_until=wait_until)
        if url.rstrip("/").endswith("/clients"):
            page.url = "https://mit.billy.dk/test-org-slug/clients/empty"
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

    result = asyncio.run(runtime.ui_clients_create_open())

    assert result == UiClientsCreateOpenSuccess(
        path_class="/:org_slug/clients/empty",
        heading="Kontakter",
        create_dialog_open=True,
        name_field_visible=True,
        registration_no_field_present=True,
        address_or_person_fields_present=True,
        shell_markers_present=True,
    )
    assert not any("/clients/new" in url for url, _ in page.navigation)
    assert "test-org-slug" not in str(result.model_dump())
    assert page.closed
    assert not any("click:text=Gem" in e for e in page.events)


def test_ui_clients_create_open_returns_ui_changed_when_name_missing(tmp_path: Path) -> None:
    identity_path = tmp_path / "ui-org-identity.json"
    identity_path.write_text(
        json.dumps({"source": "ui_dashboard_path", "org_slug": "test-org-slug"}) + "\n",
        encoding="utf-8",
    )
    controls = _clients_create_shell_controls()
    controls["input[name='name']"] = FakeLoginControl(count=0, visible=False)
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

    result = asyncio.run(runtime.ui_clients_create_open())

    assert isinstance(result, ToolError)
    assert result.code is StableErrorCode.UI_CHANGED
    assert "clients create form" in result.message
    assert page.closed


def test_ui_clients_create_open_rejects_soft_clients_new_path(tmp_path: Path) -> None:
    identity_path = tmp_path / "ui-org-identity.json"
    identity_path.write_text(
        json.dumps({"source": "ui_dashboard_path", "org_slug": "test-org-slug"}) + "\n",
        encoding="utf-8",
    )
    page = FakeLoginPage(
        final_url="https://mit.billy.dk/test-org-slug/dashboard",
        controls=_clients_create_shell_controls(),
        follow_goto=True,
    )
    context = FakeLoginContext(page)

    async def launcher(profile_path: str, **kwargs: bool) -> PersistentContext:
        return cast(PersistentContext, context)

    async def goto_to_new(url: str, *, wait_until: str) -> object:
        page.navigation.append((url, wait_until))
        page.events.append("goto")
        if url.rstrip("/").endswith("/clients"):
            page.url = "https://mit.billy.dk/test-org-slug/clients/new"
        else:
            page.url = url
        return object()

    page.goto = goto_to_new  # type: ignore[method-assign]

    runtime = BrowserRuntime(
        profile_path=tmp_path / "profile",
        egress_manifest_path=write_browser_egress_fixture(tmp_path),
        launcher=launcher,
        org_identity_path=identity_path,
    )

    result = asyncio.run(runtime.ui_clients_create_open())

    assert isinstance(result, ToolError)
    assert result.code is StableErrorCode.UI_CHANGED
    assert page.closed


def _clients_get_shell_controls(
    page_holder: dict[str, FakeLoginPage],
) -> dict[str, FakeLoginControl]:
    def open_detail() -> None:
        page = page_holder["page"]
        page.url = "https://mit.billy.dk/test-org-slug/contacts/contact-1/customer"
        page.controls["body"] = FakeLoginControl(
            text="Acme Client (Kunde) Opret Ret Mere Fakturaer Overblik Menu"
        )
        page.controls["body"].bind(page.events, "body")
        page.controls["text=Ret"] = FakeLoginControl(text="Ret")
        page.controls["text=Ret"].bind(page.events, "text=Ret")

    return {
        "input[type='email'][name='email']": FakeLoginControl(count=0, visible=False),
        "input[type='password'][name='password']": FakeLoginControl(count=0, visible=False),
        "input[type='checkbox'][name='remember']": FakeLoginControl(count=0, visible=False),
        "button[data-cy='login-button']": FakeLoginControl(count=0, visible=False),
        "h1": FakeLoginControl(text="Kunder"),
        "body": FakeLoginControl(text="Kunder Opret kontakt Mere Navn E-mail"),
        "text=Opret kontakt": FakeLoginControl(text="Opret kontakt"),
        "input[name='name']": FakeLoginControl(count=0, visible=False),
        "a[href*='/test-org-slug/contacts/'], a[href*='/test-org-slug/clients/']": FakeLoginControl(
            count=0, visible=False
        ),
        "table tbody tr, [role='row']": FakeLoginControl(
            text="Acme Client acme@example.invalid",
            on_click=open_detail,
        ),
        "text=Ret": FakeLoginControl(count=0, visible=False),
        "text=Overblik": FakeLoginControl(text="Overblik"),
        "text=Menu": FakeLoginControl(text="Menu"),
        "text=Upsedasse!": FakeLoginControl(count=0, visible=False),
        "text=Upsedasse": FakeLoginControl(count=0, visible=False),
        "text=Log ind igen": FakeLoginControl(count=0, visible=False),
    }


def test_ui_clients_get_open_returns_success_for_detail(tmp_path: Path) -> None:
    identity_path = tmp_path / "ui-org-identity.json"
    identity_path.write_text(
        json.dumps({"source": "ui_dashboard_path", "org_slug": "test-org-slug"}) + "\n",
        encoding="utf-8",
    )
    page_holder: dict[str, FakeLoginPage] = {}
    page = FakeLoginPage(
        final_url="https://mit.billy.dk/test-org-slug/dashboard",
        controls=_clients_get_shell_controls(page_holder),
        follow_goto=True,
    )
    page_holder["page"] = page
    context = FakeLoginContext(page)

    async def launcher(profile_path: str, **kwargs: bool) -> PersistentContext:
        return cast(PersistentContext, context)

    runtime = BrowserRuntime(
        profile_path=tmp_path / "profile",
        egress_manifest_path=write_browser_egress_fixture(tmp_path),
        launcher=launcher,
        org_identity_path=identity_path,
    )

    result = asyncio.run(runtime.ui_clients_get_open())

    assert result == UiClientsGetOpenSuccess(
        detail_open=True,
        contact_name_visible=True,
        edit_action_visible=True,
        detail_markers_present=True,
        shell_markers_present=True,
    )
    assert "test-org-slug" not in str(result.model_dump())
    assert page.closed
    assert not any("click:text=Gem" in e for e in page.events)


def test_ui_clients_get_open_returns_ui_changed_when_no_rows(tmp_path: Path) -> None:
    identity_path = tmp_path / "ui-org-identity.json"
    identity_path.write_text(
        json.dumps({"source": "ui_dashboard_path", "org_slug": "test-org-slug"}) + "\n",
        encoding="utf-8",
    )
    controls = {
        "input[type='email'][name='email']": FakeLoginControl(count=0, visible=False),
        "input[type='password'][name='password']": FakeLoginControl(count=0, visible=False),
        "input[type='checkbox'][name='remember']": FakeLoginControl(count=0, visible=False),
        "button[data-cy='login-button']": FakeLoginControl(count=0, visible=False),
        "h1": FakeLoginControl(text="Kunder"),
        "text=Opret kontakt": FakeLoginControl(text="Opret kontakt"),
        "input[name='name']": FakeLoginControl(count=0, visible=False),
        "a[href*='/test-org-slug/clients/']": FakeLoginControl(count=0, visible=False),
        "table tbody tr, [role='row']": FakeLoginControl(count=0, visible=False),
        "text=Overblik": FakeLoginControl(text="Overblik"),
        "text=Menu": FakeLoginControl(text="Menu"),
        "text=Upsedasse!": FakeLoginControl(count=0, visible=False),
        "text=Upsedasse": FakeLoginControl(count=0, visible=False),
        "text=Log ind igen": FakeLoginControl(count=0, visible=False),
    }
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

    result = asyncio.run(runtime.ui_clients_get_open())

    assert isinstance(result, ToolError)
    assert result.code is StableErrorCode.UI_CHANGED
    assert "clients detail" in result.message
    assert page.closed


def test_ui_clients_get_open_rejects_header_only_row(tmp_path: Path) -> None:
    identity_path = tmp_path / "ui-org-identity.json"
    identity_path.write_text(
        json.dumps({"source": "ui_dashboard_path", "org_slug": "test-org-slug"}) + "\n",
        encoding="utf-8",
    )
    controls = {
        "input[type='email'][name='email']": FakeLoginControl(count=0, visible=False),
        "input[type='password'][name='password']": FakeLoginControl(count=0, visible=False),
        "input[type='checkbox'][name='remember']": FakeLoginControl(count=0, visible=False),
        "button[data-cy='login-button']": FakeLoginControl(count=0, visible=False),
        "h1": FakeLoginControl(text="Kunder"),
        "text=Opret kontakt": FakeLoginControl(text="Opret kontakt"),
        "input[name='name']": FakeLoginControl(count=0, visible=False),
        "a[href*='/test-org-slug/clients/']": FakeLoginControl(count=0, visible=False),
        "table tbody tr, [role='row']": FakeLoginControl(
            text="Navn\n\nE-mail\n\nTelefon\n\nLand\n\nOprettet dato"
        ),
        "text=Overblik": FakeLoginControl(text="Overblik"),
        "text=Menu": FakeLoginControl(text="Menu"),
        "text=Upsedasse!": FakeLoginControl(count=0, visible=False),
        "text=Upsedasse": FakeLoginControl(count=0, visible=False),
        "text=Log ind igen": FakeLoginControl(count=0, visible=False),
    }
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

    result = asyncio.run(runtime.ui_clients_get_open())

    assert isinstance(result, ToolError)
    assert result.code is StableErrorCode.UI_CHANGED
    assert page.closed


def _clients_update_shell_controls(
    page_holder: dict[str, FakeLoginPage],
) -> dict[str, FakeLoginControl]:
    def open_detail() -> None:
        page = page_holder["page"]
        page.url = "https://mit.billy.dk/test-org-slug/contacts/contact-1/customer"
        page.controls["body"] = FakeLoginControl(
            text="Acme Client (Kunde) Opret Ret Mere Fakturaer Overblik Menu"
        )
        page.controls["body"].bind(page.events, "body")
        page.controls["role:button:Ret"] = FakeLoginControl(text="Ret", on_click=open_edit)
        page.controls["role:button:Ret"].bind(page.events, "role:button:Ret")
        page.controls["input[name='name']"] = FakeLoginControl(count=0, visible=False)
        page.controls["input[name='name']"].bind(page.events, "input[name='name']")

    def open_edit() -> None:
        page = page_holder["page"]
        page.url = "https://mit.billy.dk/test-org-slug/contacts/contact-1/customer"
        page.controls["body"] = FakeLoginControl(
            text="Acme Client (Kunde) Opret Ret Mere Gem Overblik Menu"
        )
        page.controls["body"].bind(page.events, "body")
        page.controls["input[name='name']"] = FakeLoginControl(
            text="", value="Acme Client", visible=True
        )
        page.controls["input[name='name']"].bind(page.events, "input[name='name']")
        page.controls["input[name='street']"] = FakeLoginControl(value="Testvej 1", visible=True)
        page.controls["input[name='street']"].bind(page.events, "input[name='street']")
        page.controls["input[name='city']"] = FakeLoginControl(value="København", visible=True)
        page.controls["input[name='city']"].bind(page.events, "input[name='city']")
        page.controls["select[name='country'], input[name='country']"] = FakeLoginControl(
            value="DK", visible=True
        )
        page.controls["select[name='country'], input[name='country']"].bind(
            page.events, "select[name='country'], input[name='country']"
        )
        page.controls["text=Gem"] = FakeLoginControl(text="Gem")
        page.controls["text=Gem"].bind(page.events, "text=Gem")

    return {
        "input[type='email'][name='email']": FakeLoginControl(count=0, visible=False),
        "input[type='password'][name='password']": FakeLoginControl(count=0, visible=False),
        "input[type='checkbox'][name='remember']": FakeLoginControl(count=0, visible=False),
        "button[data-cy='login-button']": FakeLoginControl(count=0, visible=False),
        "h1": FakeLoginControl(text="Kunder"),
        "body": FakeLoginControl(text="Kunder Opret kontakt Mere Navn E-mail"),
        "text=Opret kontakt": FakeLoginControl(text="Opret kontakt"),
        "input[name='name']": FakeLoginControl(count=0, visible=False),
        "input[name='street']": FakeLoginControl(count=0, visible=False),
        "input[name='city']": FakeLoginControl(count=0, visible=False),
        "select[name='country'], input[name='country']": FakeLoginControl(count=0, visible=False),
        "a[href*='/test-org-slug/contacts/'], a[href*='/test-org-slug/clients/']": FakeLoginControl(
            count=0, visible=False
        ),
        "table tbody tr, [role='row']": FakeLoginControl(
            text="Acme Client acme@example.invalid",
            on_click=open_detail,
        ),
        "text=Ret": FakeLoginControl(count=0, visible=False),
        "role:button:Ret": FakeLoginControl(count=0, visible=False),
        "text=Gem": FakeLoginControl(count=0, visible=False),
        "text=Overblik": FakeLoginControl(text="Overblik"),
        "text=Menu": FakeLoginControl(text="Menu"),
        "text=Upsedasse!": FakeLoginControl(count=0, visible=False),
        "text=Upsedasse": FakeLoginControl(count=0, visible=False),
        "text=Log ind igen": FakeLoginControl(count=0, visible=False),
    }


def test_ui_clients_update_open_returns_success_for_edit_form(tmp_path: Path) -> None:
    identity_path = tmp_path / "ui-org-identity.json"
    identity_path.write_text(
        json.dumps({"source": "ui_dashboard_path", "org_slug": "test-org-slug"}) + "\n",
        encoding="utf-8",
    )
    page_holder: dict[str, FakeLoginPage] = {}
    page = FakeLoginPage(
        final_url="https://mit.billy.dk/test-org-slug/dashboard",
        controls=_clients_update_shell_controls(page_holder),
        follow_goto=True,
    )
    page_holder["page"] = page
    context = FakeLoginContext(page)

    async def launcher(profile_path: str, **kwargs: bool) -> PersistentContext:
        return cast(PersistentContext, context)

    runtime = BrowserRuntime(
        profile_path=tmp_path / "profile",
        egress_manifest_path=write_browser_egress_fixture(tmp_path),
        launcher=launcher,
        org_identity_path=identity_path,
    )

    result = asyncio.run(runtime.ui_clients_update_open())

    assert result == UiClientsUpdateOpenSuccess(
        edit_form_open=True,
        name_field_visible=True,
        name_field_has_value=True,
        address_or_person_fields_present=True,
        country_field_present=True,
        shell_markers_present=True,
    )
    assert "test-org-slug" not in str(result.model_dump())
    assert page.closed
    assert not any("click:text=Gem" in e for e in page.events)
    assert any("click:role:button:Ret" in e for e in page.events)


def test_ui_clients_update_open_rejects_get_overview_without_ret(tmp_path: Path) -> None:
    """Detail open without Ret must not green update (get-only surface)."""

    identity_path = tmp_path / "ui-org-identity.json"
    identity_path.write_text(
        json.dumps({"source": "ui_dashboard_path", "org_slug": "test-org-slug"}) + "\n",
        encoding="utf-8",
    )
    page_holder: dict[str, FakeLoginPage] = {}

    def open_detail_no_ret() -> None:
        page = page_holder["page"]
        page.url = "https://mit.billy.dk/test-org-slug/contacts/contact-1/customer"
        page.controls["body"] = FakeLoginControl(
            text="Acme Client (Kunde) Opret Mere Fakturaer Overblik Menu"
        )
        page.controls["body"].bind(page.events, "body")
        page.controls["text=Ret"] = FakeLoginControl(count=0, visible=False)
        page.controls["text=Ret"].bind(page.events, "text=Ret")
        page.controls["input[name='name']"] = FakeLoginControl(count=0, visible=False)
        page.controls["input[name='name']"].bind(page.events, "input[name='name']")

    controls = {
        "input[type='email'][name='email']": FakeLoginControl(count=0, visible=False),
        "input[type='password'][name='password']": FakeLoginControl(count=0, visible=False),
        "input[type='checkbox'][name='remember']": FakeLoginControl(count=0, visible=False),
        "button[data-cy='login-button']": FakeLoginControl(count=0, visible=False),
        "h1": FakeLoginControl(text="Kunder"),
        "body": FakeLoginControl(text="Kunder Opret kontakt"),
        "text=Opret kontakt": FakeLoginControl(text="Opret kontakt"),
        "input[name='name']": FakeLoginControl(count=0, visible=False),
        "a[href*='/test-org-slug/contacts/'], a[href*='/test-org-slug/clients/']": FakeLoginControl(
            count=0, visible=False
        ),
        "table tbody tr, [role='row']": FakeLoginControl(
            text="Acme Client",
            on_click=open_detail_no_ret,
        ),
        "text=Ret": FakeLoginControl(count=0, visible=False),
        "text=Overblik": FakeLoginControl(text="Overblik"),
        "text=Menu": FakeLoginControl(text="Menu"),
        "text=Upsedasse!": FakeLoginControl(count=0, visible=False),
        "text=Upsedasse": FakeLoginControl(count=0, visible=False),
        "text=Log ind igen": FakeLoginControl(count=0, visible=False),
    }
    page = FakeLoginPage(
        final_url="https://mit.billy.dk/test-org-slug/dashboard",
        controls=controls,
        follow_goto=True,
    )
    page_holder["page"] = page
    context = FakeLoginContext(page)

    async def launcher(profile_path: str, **kwargs: bool) -> PersistentContext:
        return cast(PersistentContext, context)

    runtime = BrowserRuntime(
        profile_path=tmp_path / "profile",
        egress_manifest_path=write_browser_egress_fixture(tmp_path),
        launcher=launcher,
        org_identity_path=identity_path,
    )

    result = asyncio.run(runtime.ui_clients_update_open())

    assert isinstance(result, ToolError)
    assert result.code is StableErrorCode.UI_CHANGED
    assert "clients update" in result.message
    assert page.closed


def test_ui_clients_update_open_rejects_list_only(tmp_path: Path) -> None:
    identity_path = tmp_path / "ui-org-identity.json"
    identity_path.write_text(
        json.dumps({"source": "ui_dashboard_path", "org_slug": "test-org-slug"}) + "\n",
        encoding="utf-8",
    )
    controls = {
        "input[type='email'][name='email']": FakeLoginControl(count=0, visible=False),
        "input[type='password'][name='password']": FakeLoginControl(count=0, visible=False),
        "input[type='checkbox'][name='remember']": FakeLoginControl(count=0, visible=False),
        "button[data-cy='login-button']": FakeLoginControl(count=0, visible=False),
        "h1": FakeLoginControl(text="Kunder"),
        "body": FakeLoginControl(text="Kunder Opret kontakt"),
        "text=Opret kontakt": FakeLoginControl(text="Opret kontakt"),
        "input[name='name']": FakeLoginControl(count=0, visible=False),
        "table tbody tr, [role='row']": FakeLoginControl(count=0, visible=False),
        "text=Overblik": FakeLoginControl(text="Overblik"),
        "text=Menu": FakeLoginControl(text="Menu"),
        "text=Upsedasse!": FakeLoginControl(count=0, visible=False),
        "text=Upsedasse": FakeLoginControl(count=0, visible=False),
        "text=Log ind igen": FakeLoginControl(count=0, visible=False),
    }
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

    result = asyncio.run(runtime.ui_clients_update_open())

    assert isinstance(result, ToolError)
    assert result.code is StableErrorCode.UI_CHANGED
    assert page.closed


def _clients_delete_shell_controls(
    page_holder: dict[str, FakeLoginPage],
) -> dict[str, FakeLoginControl]:
    def open_detail() -> None:
        page = page_holder["page"]
        page.url = "https://mit.billy.dk/test-org-slug/contacts/contact-1/customer"
        page.controls["body"] = FakeLoginControl(
            text="Acme Client (Kunde) Opret Ret Mere Fakturaer Overblik Menu"
        )
        page.controls["body"].bind(page.events, "body")
        page.controls["text=Mere"] = FakeLoginControl(text="Mere", on_click=open_mere)
        page.controls["text=Mere"].bind(page.events, "text=Mere")
        page.controls["text=Ret"] = FakeLoginControl(text="Ret")
        page.controls["text=Ret"].bind(page.events, "text=Ret")

    def open_mere() -> None:
        page = page_holder["page"]
        page.url = "https://mit.billy.dk/test-org-slug/contacts/contact-1/customer"
        page.controls["body"] = FakeLoginControl(
            text=(
                "Acme Client (Kunde) Opret Ret Mere Indbetaling Udbetaling "
                "Kontoudtog Arkivér kontakt Slet kontakt Fakturaer Overblik Menu"
            )
        )
        page.controls["body"].bind(page.events, "body")
        page.controls["text=Mere"] = FakeLoginControl(text="Mere")
        page.controls["text=Mere"].bind(page.events, "text=Mere")
        page.controls["text=Slet kontakt"] = FakeLoginControl(text="Slet kontakt")
        page.controls["text=Slet kontakt"].bind(page.events, "text=Slet kontakt")

    return {
        "input[type='email'][name='email']": FakeLoginControl(count=0, visible=False),
        "input[type='password'][name='password']": FakeLoginControl(count=0, visible=False),
        "input[type='checkbox'][name='remember']": FakeLoginControl(count=0, visible=False),
        "button[data-cy='login-button']": FakeLoginControl(count=0, visible=False),
        "h1": FakeLoginControl(text="Kunder"),
        "body": FakeLoginControl(text="Kunder Opret kontakt Mere Navn E-mail"),
        "text=Opret kontakt": FakeLoginControl(text="Opret kontakt"),
        "a[href*='/test-org-slug/contacts/'], a[href*='/test-org-slug/clients/']": FakeLoginControl(
            count=0, visible=False
        ),
        "table tbody tr, [role='row']": FakeLoginControl(
            text="Acme Client acme@example.invalid",
            on_click=open_detail,
        ),
        "text=Mere": FakeLoginControl(count=0, visible=False),
        "text=Ret": FakeLoginControl(count=0, visible=False),
        "text=Slet kontakt": FakeLoginControl(count=0, visible=False),
        "text=Overblik": FakeLoginControl(text="Overblik"),
        "text=Menu": FakeLoginControl(text="Menu"),
        "text=Upsedasse!": FakeLoginControl(count=0, visible=False),
        "text=Upsedasse": FakeLoginControl(count=0, visible=False),
        "text=Log ind igen": FakeLoginControl(count=0, visible=False),
    }


def test_ui_clients_delete_open_returns_success_for_mere_delete_chrome(tmp_path: Path) -> None:
    identity_path = tmp_path / "ui-org-identity.json"
    identity_path.write_text(
        json.dumps({"source": "ui_dashboard_path", "org_slug": "test-org-slug"}) + "\n",
        encoding="utf-8",
    )
    page_holder: dict[str, FakeLoginPage] = {}
    page = FakeLoginPage(
        final_url="https://mit.billy.dk/test-org-slug/dashboard",
        controls=_clients_delete_shell_controls(page_holder),
        follow_goto=True,
    )
    page_holder["page"] = page
    context = FakeLoginContext(page)

    async def launcher(profile_path: str, **kwargs: bool) -> PersistentContext:
        return cast(PersistentContext, context)

    runtime = BrowserRuntime(
        profile_path=tmp_path / "profile",
        egress_manifest_path=write_browser_egress_fixture(tmp_path),
        launcher=launcher,
        org_identity_path=identity_path,
    )

    result = asyncio.run(runtime.ui_clients_delete_open())

    assert result == UiClientsDeleteOpenSuccess(
        detail_open=True,
        mere_open=True,
        slet_kontakt_visible=True,
        arkiver_kontakt_visible=True,
        primary_slet_absent=True,
        shell_markers_present=True,
    )
    assert "test-org-slug" not in str(result.model_dump())
    assert page.closed
    assert any("click:text=Mere" in e for e in page.events)
    assert not any("click:text=Slet kontakt" in e for e in page.events)


def test_ui_clients_delete_open_rejects_detail_without_mere_slet(tmp_path: Path) -> None:
    identity_path = tmp_path / "ui-org-identity.json"
    identity_path.write_text(
        json.dumps({"source": "ui_dashboard_path", "org_slug": "test-org-slug"}) + "\n",
        encoding="utf-8",
    )
    page_holder: dict[str, FakeLoginPage] = {}

    def open_detail_no_mere() -> None:
        page = page_holder["page"]
        page.url = "https://mit.billy.dk/test-org-slug/contacts/contact-1/customer"
        page.controls["body"] = FakeLoginControl(
            text="Acme Client (Kunde) Opret Ret Fakturaer Overblik Menu"
        )
        page.controls["body"].bind(page.events, "body")
        page.controls["text=Mere"] = FakeLoginControl(count=0, visible=False)
        page.controls["text=Mere"].bind(page.events, "text=Mere")
        page.controls["text=Ret"] = FakeLoginControl(text="Ret")
        page.controls["text=Ret"].bind(page.events, "text=Ret")

    controls = {
        "input[type='email'][name='email']": FakeLoginControl(count=0, visible=False),
        "input[type='password'][name='password']": FakeLoginControl(count=0, visible=False),
        "input[type='checkbox'][name='remember']": FakeLoginControl(count=0, visible=False),
        "button[data-cy='login-button']": FakeLoginControl(count=0, visible=False),
        "h1": FakeLoginControl(text="Kunder"),
        "body": FakeLoginControl(text="Kunder Opret kontakt"),
        "text=Opret kontakt": FakeLoginControl(text="Opret kontakt"),
        "a[href*='/test-org-slug/contacts/'], a[href*='/test-org-slug/clients/']": FakeLoginControl(
            count=0, visible=False
        ),
        "table tbody tr, [role='row']": FakeLoginControl(
            text="Acme Client",
            on_click=open_detail_no_mere,
        ),
        "text=Mere": FakeLoginControl(count=0, visible=False),
        "text=Ret": FakeLoginControl(count=0, visible=False),
        "text=Overblik": FakeLoginControl(text="Overblik"),
        "text=Menu": FakeLoginControl(text="Menu"),
        "text=Upsedasse!": FakeLoginControl(count=0, visible=False),
        "text=Upsedasse": FakeLoginControl(count=0, visible=False),
        "text=Log ind igen": FakeLoginControl(count=0, visible=False),
    }
    page = FakeLoginPage(
        final_url="https://mit.billy.dk/test-org-slug/dashboard",
        controls=controls,
        follow_goto=True,
    )
    page_holder["page"] = page
    context = FakeLoginContext(page)

    async def launcher(profile_path: str, **kwargs: bool) -> PersistentContext:
        return cast(PersistentContext, context)

    runtime = BrowserRuntime(
        profile_path=tmp_path / "profile",
        egress_manifest_path=write_browser_egress_fixture(tmp_path),
        launcher=launcher,
        org_identity_path=identity_path,
    )

    result = asyncio.run(runtime.ui_clients_delete_open())

    assert isinstance(result, ToolError)
    assert result.code is StableErrorCode.UI_CHANGED
    assert "clients delete" in result.message
    assert page.closed


def test_ui_clients_delete_open_rejects_list_only(tmp_path: Path) -> None:
    identity_path = tmp_path / "ui-org-identity.json"
    identity_path.write_text(
        json.dumps({"source": "ui_dashboard_path", "org_slug": "test-org-slug"}) + "\n",
        encoding="utf-8",
    )
    controls = {
        "input[type='email'][name='email']": FakeLoginControl(count=0, visible=False),
        "input[type='password'][name='password']": FakeLoginControl(count=0, visible=False),
        "input[type='checkbox'][name='remember']": FakeLoginControl(count=0, visible=False),
        "button[data-cy='login-button']": FakeLoginControl(count=0, visible=False),
        "h1": FakeLoginControl(text="Kunder"),
        "body": FakeLoginControl(text="Kunder Opret kontakt"),
        "text=Opret kontakt": FakeLoginControl(text="Opret kontakt"),
        "table tbody tr, [role='row']": FakeLoginControl(count=0, visible=False),
        "text=Overblik": FakeLoginControl(text="Overblik"),
        "text=Menu": FakeLoginControl(text="Menu"),
        "text=Upsedasse!": FakeLoginControl(count=0, visible=False),
        "text=Upsedasse": FakeLoginControl(count=0, visible=False),
        "text=Log ind igen": FakeLoginControl(count=0, visible=False),
    }
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

    result = asyncio.run(runtime.ui_clients_delete_open())

    assert isinstance(result, ToolError)
    assert result.code is StableErrorCode.UI_CHANGED
    assert page.closed


def _suppliers_create_shell_controls() -> dict[str, FakeLoginControl]:
    return {
        "input[type='email'][name='email']": FakeLoginControl(count=0, visible=False),
        "input[type='password'][name='password']": FakeLoginControl(count=0, visible=False),
        "input[type='checkbox'][name='remember']": FakeLoginControl(count=0, visible=False),
        "button[data-cy='login-button']": FakeLoginControl(count=0, visible=False),
        "h1": FakeLoginControl(text="Leverandører"),
        "text=Opret kontakt": FakeLoginControl(text="Opret kontakt"),
        "input[name='name']": FakeLoginControl(text=""),
        "input[name='registrationNo']": FakeLoginControl(text=""),
        "input[name='street']": FakeLoginControl(text=""),
        "input[name='person_email']": FakeLoginControl(text=""),
        "text=Overblik": FakeLoginControl(text="Overblik"),
        "text=Menu": FakeLoginControl(text="Menu"),
        "text=Upsedasse!": FakeLoginControl(count=0, visible=False),
        "text=Upsedasse": FakeLoginControl(count=0, visible=False),
        "text=Log ind igen": FakeLoginControl(count=0, visible=False),
    }


def test_ui_suppliers_create_open_returns_auth_required_on_login_page(tmp_path: Path) -> None:
    page = FakeLoginPage()
    context = FakeLoginContext(page)

    async def launcher(profile_path: str, **kwargs: bool) -> PersistentContext:
        return cast(PersistentContext, context)

    runtime = BrowserRuntime(
        profile_path=tmp_path / "profile",
        egress_manifest_path=write_browser_egress_fixture(tmp_path),
        launcher=launcher,
    )

    result = asyncio.run(runtime.ui_suppliers_create_open())

    assert isinstance(result, ToolError)
    assert result.code is StableErrorCode.AUTH_REQUIRED
    assert page.closed


def test_ui_suppliers_create_open_returns_success_for_create_dialog(tmp_path: Path) -> None:
    identity_path = tmp_path / "ui-org-identity.json"
    identity_path.write_text(
        json.dumps({"source": "ui_dashboard_path", "org_slug": "test-org-slug"}) + "\n",
        encoding="utf-8",
    )
    page = FakeLoginPage(
        final_url="https://mit.billy.dk/test-org-slug/dashboard",
        controls=_suppliers_create_shell_controls(),
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

    result = asyncio.run(runtime.ui_suppliers_create_open())

    assert result == UiSuppliersCreateOpenSuccess(
        create_dialog_open=True,
        name_field_visible=True,
        registration_no_field_present=True,
        address_or_person_fields_present=True,
        shell_markers_present=True,
    )
    assert any(url.rstrip("/").endswith("/suppliers") for url, _ in page.navigation)
    assert not any("/suppliers/new" in url for url, _ in page.navigation)
    assert "test-org-slug" not in str(result.model_dump())
    assert page.closed
    assert not any("click:text=Gem" in e for e in page.events)


def test_ui_suppliers_create_open_returns_ui_changed_when_name_missing(tmp_path: Path) -> None:
    identity_path = tmp_path / "ui-org-identity.json"
    identity_path.write_text(
        json.dumps({"source": "ui_dashboard_path", "org_slug": "test-org-slug"}) + "\n",
        encoding="utf-8",
    )
    controls = _suppliers_create_shell_controls()
    controls["input[name='name']"] = FakeLoginControl(count=0, visible=False)
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

    result = asyncio.run(runtime.ui_suppliers_create_open())

    assert isinstance(result, ToolError)
    assert result.code is StableErrorCode.UI_CHANGED
    assert "suppliers create form" in result.message
    assert page.closed


def test_ui_suppliers_create_open_rejects_soft_suppliers_new_path(tmp_path: Path) -> None:
    identity_path = tmp_path / "ui-org-identity.json"
    identity_path.write_text(
        json.dumps({"source": "ui_dashboard_path", "org_slug": "test-org-slug"}) + "\n",
        encoding="utf-8",
    )
    page = FakeLoginPage(
        final_url="https://mit.billy.dk/test-org-slug/dashboard",
        controls=_suppliers_create_shell_controls(),
        follow_goto=True,
    )
    context = FakeLoginContext(page)

    async def launcher(profile_path: str, **kwargs: bool) -> PersistentContext:
        return cast(PersistentContext, context)

    async def goto_to_new(url: str, *, wait_until: str) -> object:
        page.navigation.append((url, wait_until))
        page.events.append("goto")
        if url.rstrip("/").endswith("/suppliers"):
            page.url = "https://mit.billy.dk/test-org-slug/suppliers/new"
        else:
            page.url = url
        return object()

    page.goto = goto_to_new  # type: ignore[method-assign]

    runtime = BrowserRuntime(
        profile_path=tmp_path / "profile",
        egress_manifest_path=write_browser_egress_fixture(tmp_path),
        launcher=launcher,
        org_identity_path=identity_path,
    )

    result = asyncio.run(runtime.ui_suppliers_create_open())

    assert isinstance(result, ToolError)
    assert result.code is StableErrorCode.UI_CHANGED
    assert page.closed


def _products_create_shell_controls() -> dict[str, FakeLoginControl]:
    return {
        "input[type='email'][name='email']": FakeLoginControl(count=0, visible=False),
        "input[type='password'][name='password']": FakeLoginControl(count=0, visible=False),
        "input[type='checkbox'][name='remember']": FakeLoginControl(count=0, visible=False),
        "button[data-cy='login-button']": FakeLoginControl(count=0, visible=False),
        "h1": FakeLoginControl(text="Lagermodul"),
        "text=Opret produkt": FakeLoginControl(text="Opret produkt"),
        "input[name='name']": FakeLoginControl(text=""),
        "input[name='account']": FakeLoginControl(text=""),
        "input[name='salesTaxRuleset']": FakeLoginControl(text=""),
        "input[name='unitPrice']": FakeLoginControl(text=""),
        "text=Overblik": FakeLoginControl(text="Overblik"),
        "text=Menu": FakeLoginControl(text="Menu"),
        "text=Upsedasse!": FakeLoginControl(count=0, visible=False),
        "text=Upsedasse": FakeLoginControl(count=0, visible=False),
        "text=Log ind igen": FakeLoginControl(count=0, visible=False),
    }


def test_ui_products_create_open_returns_auth_required_on_login_page(tmp_path: Path) -> None:
    page = FakeLoginPage()
    context = FakeLoginContext(page)

    async def launcher(profile_path: str, **kwargs: bool) -> PersistentContext:
        return cast(PersistentContext, context)

    runtime = BrowserRuntime(
        profile_path=tmp_path / "profile",
        egress_manifest_path=write_browser_egress_fixture(tmp_path),
        launcher=launcher,
    )

    result = asyncio.run(runtime.ui_products_create_open())

    assert isinstance(result, ToolError)
    assert result.code is StableErrorCode.AUTH_REQUIRED
    assert page.closed


def test_ui_products_create_open_returns_success_for_create_form(tmp_path: Path) -> None:
    identity_path = tmp_path / "ui-org-identity.json"
    identity_path.write_text(
        json.dumps({"source": "ui_dashboard_path", "org_slug": "test-org-slug"}) + "\n",
        encoding="utf-8",
    )
    page = FakeLoginPage(
        final_url="https://mit.billy.dk/test-org-slug/dashboard",
        controls=_products_create_shell_controls(),
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

    result = asyncio.run(runtime.ui_products_create_open())

    assert result == UiProductsCreateOpenSuccess(
        create_form_open=True,
        name_field_visible=True,
        account_field_present=True,
        sales_tax_ruleset_field_present=True,
        unit_price_field_present=True,
        shell_markers_present=True,
    )
    assert any(url.rstrip("/").endswith("/inventory") for url, _ in page.navigation)
    assert not any("/products/new" in url for url, _ in page.navigation)
    assert "test-org-slug" not in str(result.model_dump())
    assert page.closed
    assert not any("click:text=Gem" in e for e in page.events)


def test_ui_products_create_open_returns_ui_changed_when_name_missing(tmp_path: Path) -> None:
    identity_path = tmp_path / "ui-org-identity.json"
    identity_path.write_text(
        json.dumps({"source": "ui_dashboard_path", "org_slug": "test-org-slug"}) + "\n",
        encoding="utf-8",
    )
    controls = _products_create_shell_controls()
    controls["input[name='name']"] = FakeLoginControl(count=0, visible=False)
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

    result = asyncio.run(runtime.ui_products_create_open())

    assert isinstance(result, ToolError)
    assert result.code is StableErrorCode.UI_CHANGED
    assert "products create form" in result.message
    assert page.closed


def test_ui_products_create_open_rejects_soft_products_new_path(tmp_path: Path) -> None:
    identity_path = tmp_path / "ui-org-identity.json"
    identity_path.write_text(
        json.dumps({"source": "ui_dashboard_path", "org_slug": "test-org-slug"}) + "\n",
        encoding="utf-8",
    )
    page = FakeLoginPage(
        final_url="https://mit.billy.dk/test-org-slug/dashboard",
        controls=_products_create_shell_controls(),
        follow_goto=True,
    )
    context = FakeLoginContext(page)

    async def launcher(profile_path: str, **kwargs: bool) -> PersistentContext:
        return cast(PersistentContext, context)

    async def goto_to_new(url: str, *, wait_until: str) -> object:
        page.navigation.append((url, wait_until))
        page.events.append("goto")
        if url.rstrip("/").endswith("/inventory"):
            page.url = "https://mit.billy.dk/test-org-slug/products/new"
        else:
            page.url = url
        return object()

    page.goto = goto_to_new  # type: ignore[method-assign]

    runtime = BrowserRuntime(
        profile_path=tmp_path / "profile",
        egress_manifest_path=write_browser_egress_fixture(tmp_path),
        launcher=launcher,
        org_identity_path=identity_path,
    )

    result = asyncio.run(runtime.ui_products_create_open())

    assert isinstance(result, ToolError)
    assert result.code is StableErrorCode.UI_CHANGED
    assert page.closed


def _invoices_get_shell_controls(
    page_holder: dict[str, FakeLoginPage],
) -> dict[str, FakeLoginControl]:
    def open_detail() -> None:
        page = page_holder["page"]
        page.url = "https://mit.billy.dk/test-org-slug/invoices/inv-1/edit"
        updates = {
            "body": FakeLoginControl(
                text="Kladde Faktura Kunde entryDate Beskrivelse Tilføj linje Overblik Menu"
            ),
            (
                "input[name='entryDate'], input[name='entry_date'], input[type='date']"
            ): FakeLoginControl(count=1, visible=True),
            (
                "input[name='contactId'], input[name='contact'], [data-cy*='contact' i]"
            ): FakeLoginControl(count=1, visible=True),
            "text=Beskrivelse": FakeLoginControl(text="Beskrivelse"),
            "text=Tilføj linje": FakeLoginControl(text="Tilføj linje"),
            "text=Produkt": FakeLoginControl(text="Produkt"),
            "textarea": FakeLoginControl(count=1, visible=True),
            "text=Overblik": FakeLoginControl(text="Overblik"),
            "text=Menu": FakeLoginControl(text="Menu"),
            "input, textarea, select": FakeLoginControl(count=5, visible=True),
        }
        for sel, control in updates.items():
            page.controls[sel] = control
            control.bind(page.events, sel)

    return {
        "input[type='email'][name='email']": FakeLoginControl(count=0, visible=False),
        "input[type='password'][name='password']": FakeLoginControl(count=0, visible=False),
        "input[type='checkbox'][name='remember']": FakeLoginControl(count=0, visible=False),
        "button[data-cy='login-button']": FakeLoginControl(count=0, visible=False),
        "h1": FakeLoginControl(text="Fakturaer"),
        "body": FakeLoginControl(text="Fakturaer Opret faktura Mere 1 Kladde TMP-INVOICE"),
        "text=Opret faktura": FakeLoginControl(text="Opret faktura"),
        "a[href*='/test-org-slug/invoices/']": FakeLoginControl(count=0, visible=False),
        "table tbody tr, [data-cy='table-item'], [role='row'], tr": FakeLoginControl(
            text="1 2026-08-01 TMP-INVOICE 10 DKK Kladde",
            on_click=open_detail,
        ),
        "text=Upsedasse!": FakeLoginControl(count=0, visible=False),
        "text=Upsedasse": FakeLoginControl(count=0, visible=False),
        "text=Log ind igen": FakeLoginControl(count=0, visible=False),
        "text=Overblik": FakeLoginControl(text="Overblik"),
        "text=Menu": FakeLoginControl(text="Menu"),
    }


def test_ui_invoices_get_open_returns_success_for_detail(tmp_path: Path) -> None:
    identity_path = tmp_path / "ui-org-identity.json"
    identity_path.write_text(
        json.dumps({"source": "ui_dashboard_path", "org_slug": "test-org-slug"}) + "\n",
        encoding="utf-8",
    )
    page_holder: dict[str, FakeLoginPage] = {}
    page = FakeLoginPage(
        final_url="https://mit.billy.dk/test-org-slug/dashboard",
        controls=_invoices_get_shell_controls(page_holder),
        follow_goto=True,
    )
    page_holder["page"] = page
    context = FakeLoginContext(page)

    async def launcher(profile_path: str, **kwargs: bool) -> PersistentContext:
        return cast(PersistentContext, context)

    runtime = BrowserRuntime(
        profile_path=tmp_path / "profile",
        egress_manifest_path=write_browser_egress_fixture(tmp_path),
        launcher=launcher,
        org_identity_path=identity_path,
    )

    result = asyncio.run(runtime.ui_invoices_get_open())

    assert result == UiInvoicesGetOpenSuccess(
        detail_open=True,
        entry_date_control_present=True,
        contact_control_present=True,
        line_chrome_present=True,
        shell_markers_present=True,
    )
    assert "test-org-slug" not in str(result.model_dump())
    assert page.closed
    assert not any("click:text=Gem" in e for e in page.events)


def _invoices_update_shell_controls(
    page_holder: dict[str, FakeLoginPage],
) -> dict[str, FakeLoginControl]:
    def open_edit() -> None:
        page = page_holder["page"]
        page.url = "https://mit.billy.dk/test-org-slug/invoices/inv-1/edit"
        updates = {
            "body": FakeLoginControl(
                text=(
                    "Rediger fakturakladde Godkend og send Vis preview Gem som kladde "
                    "Mere Kunde Fakturanr. Dato Betalingsfrist Valuta Produkt Beskrivelse "
                    "Antal Enhedspris Tilføj linje Overblik Menu"
                )
            ),
            (
                "input[name='entryDate'], input[name='entry_date'], input[type='date']"
            ): FakeLoginControl(count=1, visible=True),
            (
                "input[name='contactId'], input[name='contact'], [data-cy*='contact' i]"
            ): FakeLoginControl(count=1, visible=True),
            "text=Gem som kladde": FakeLoginControl(text="Gem som kladde", count=1, visible=True),
            "text=Godkend og send": FakeLoginControl(text="Godkend og send", count=1, visible=True),
            "text=Fakturanr.": FakeLoginControl(text="Fakturanr."),
            "text=Dato": FakeLoginControl(text="Dato"),
            "text=Betalingsfrist": FakeLoginControl(text="Betalingsfrist"),
            "text=Kunde": FakeLoginControl(text="Kunde"),
            "text=Beskrivelse": FakeLoginControl(text="Beskrivelse"),
            "text=Tilføj linje": FakeLoginControl(text="Tilføj linje"),
            "textarea": FakeLoginControl(count=1, visible=True),
            "text=Overblik": FakeLoginControl(text="Overblik"),
            "text=Menu": FakeLoginControl(text="Menu"),
            "input, textarea, select": FakeLoginControl(count=9, visible=True),
            "input:visible, textarea:visible, select:visible": FakeLoginControl(
                count=9, visible=True
            ),
        }
        for sel, control in updates.items():
            page.controls[sel] = control
            control.bind(page.events, sel)

    return {
        "input[type='email'][name='email']": FakeLoginControl(count=0, visible=False),
        "input[type='password'][name='password']": FakeLoginControl(count=0, visible=False),
        "input[type='checkbox'][name='remember']": FakeLoginControl(count=0, visible=False),
        "button[data-cy='login-button']": FakeLoginControl(count=0, visible=False),
        "h1": FakeLoginControl(text="Fakturaer"),
        "body": FakeLoginControl(text="Fakturaer Opret faktura Mere 1 Kladde TMP-INVOICE"),
        "text=Opret faktura": FakeLoginControl(text="Opret faktura"),
        "a[href*='/test-org-slug/invoices/']": FakeLoginControl(count=0, visible=False),
        "table tbody tr, [data-cy='table-item'], [role='row'], tr": FakeLoginControl(
            text="1 2026-08-01 TMP-INVOICE 10 DKK Kladde",
            on_click=open_edit,
        ),
        "text=Upsedasse!": FakeLoginControl(count=0, visible=False),
        "text=Upsedasse": FakeLoginControl(count=0, visible=False),
        "text=Log ind igen": FakeLoginControl(count=0, visible=False),
        "text=Overblik": FakeLoginControl(text="Overblik"),
        "text=Menu": FakeLoginControl(text="Menu"),
    }


def test_ui_invoices_update_open_returns_success_for_edit_form(tmp_path: Path) -> None:
    identity_path = tmp_path / "ui-org-identity.json"
    identity_path.write_text(
        json.dumps({"source": "ui_dashboard_path", "org_slug": "test-org-slug"}) + "\n",
        encoding="utf-8",
    )
    page_holder: dict[str, FakeLoginPage] = {}
    page = FakeLoginPage(
        final_url="https://mit.billy.dk/test-org-slug/dashboard",
        controls=_invoices_update_shell_controls(page_holder),
        follow_goto=True,
    )
    page_holder["page"] = page
    context = FakeLoginContext(page)

    async def launcher(profile_path: str, **kwargs: bool) -> PersistentContext:
        return cast(PersistentContext, context)

    runtime = BrowserRuntime(
        profile_path=tmp_path / "profile",
        egress_manifest_path=write_browser_egress_fixture(tmp_path),
        launcher=launcher,
        org_identity_path=identity_path,
    )

    result = asyncio.run(runtime.ui_invoices_update_open())

    assert result == UiInvoicesUpdateOpenSuccess(
        form_open=True,
        gem_kladde_or_save_chrome_present=True,
        date_or_payment_terms_chrome_present=True,
        contact_or_customer_chrome_present=True,
        inputs_present=True,
        shell_markers_present=True,
    )
    assert "test-org-slug" not in str(result.model_dump())
    assert page.closed
    assert not any("click:text=Gem" in e for e in page.events)
    assert not any("click:text=Godkend" in e for e in page.events)
    assert not any("click:text=Slet" in e for e in page.events)


def test_ui_invoices_update_open_returns_ui_changed_when_empty_list(tmp_path: Path) -> None:
    identity_path = tmp_path / "ui-org-identity.json"
    identity_path.write_text(
        json.dumps({"source": "ui_dashboard_path", "org_slug": "test-org-slug"}) + "\n",
        encoding="utf-8",
    )
    controls = {
        "input[type='email'][name='email']": FakeLoginControl(count=0, visible=False),
        "input[type='password'][name='password']": FakeLoginControl(count=0, visible=False),
        "input[type='checkbox'][name='remember']": FakeLoginControl(count=0, visible=False),
        "button[data-cy='login-button']": FakeLoginControl(count=0, visible=False),
        "h1": FakeLoginControl(text="Fakturaer"),
        "body": FakeLoginControl(text="Fakturaer Ingen fakturaer Opret faktura"),
        "text=Opret faktura": FakeLoginControl(text="Opret faktura"),
        "a[href*='/test-org-slug/invoices/']": FakeLoginControl(count=0, visible=False),
        "table tbody tr, [data-cy='table-item'], [role='row']": FakeLoginControl(
            count=0, visible=False
        ),
        "text=Upsedasse!": FakeLoginControl(count=0, visible=False),
        "text=Upsedasse": FakeLoginControl(count=0, visible=False),
        "text=Log ind igen": FakeLoginControl(count=0, visible=False),
        "text=Overblik": FakeLoginControl(text="Overblik"),
        "text=Menu": FakeLoginControl(text="Menu"),
    }
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
    result = asyncio.run(runtime.ui_invoices_update_open())
    assert isinstance(result, ToolError)
    assert result.code == StableErrorCode.UI_CHANGED


def _invoices_delete_shell_controls(
    page_holder: dict[str, FakeLoginPage],
) -> dict[str, FakeLoginControl]:
    def open_edit() -> None:
        page = page_holder["page"]
        page.url = "https://mit.billy.dk/test-org-slug/invoices/inv-1/edit"
        updates = {
            "body": FakeLoginControl(
                text=(
                    "Rediger fakturakladde Godkend og send Vis preview Gem som kladde "
                    "Mere Kunde Fakturanr. Dato Betalingsfrist Overblik Menu"
                )
            ),
            "text=Mere": FakeLoginControl(text="Mere", on_click=open_mere),
            "text=Gem som kladde": FakeLoginControl(text="Gem som kladde", count=1, visible=True),
            "text=Overblik": FakeLoginControl(text="Overblik"),
            "text=Menu": FakeLoginControl(text="Menu"),
            "input:visible, textarea:visible, select:visible": FakeLoginControl(
                count=9, visible=True
            ),
        }
        for sel, control in updates.items():
            page.controls[sel] = control
            control.bind(page.events, sel)

    def open_mere() -> None:
        page = page_holder["page"]
        page.url = "https://mit.billy.dk/test-org-slug/invoices/inv-1/edit"
        page.controls["body"] = FakeLoginControl(
            text=(
                "Rediger fakturakladde Godkend og send Vis preview Gem som kladde Mere "
                "Udskriv som PDF Duplikér Slet Evt. besked til kunde Fakturanr. Dato "
                "Betalingsfrist Overblik Menu"
            )
        )
        page.controls["body"].bind(page.events, "body")
        page.controls["text=Mere"] = FakeLoginControl(text="Mere")
        page.controls["text=Mere"].bind(page.events, "text=Mere")
        page.controls["text=Slet"] = FakeLoginControl(text="Slet")
        page.controls["text=Slet"].bind(page.events, "text=Slet")
        page.controls["text=Duplikér"] = FakeLoginControl(text="Duplikér")
        page.controls["text=Duplikér"].bind(page.events, "text=Duplikér")

    return {
        "input[type='email'][name='email']": FakeLoginControl(count=0, visible=False),
        "input[type='password'][name='password']": FakeLoginControl(count=0, visible=False),
        "input[type='checkbox'][name='remember']": FakeLoginControl(count=0, visible=False),
        "button[data-cy='login-button']": FakeLoginControl(count=0, visible=False),
        "h1": FakeLoginControl(text="Fakturaer"),
        "body": FakeLoginControl(text="Fakturaer Opret faktura Mere 1 Kladde TMP-INVOICE"),
        "text=Opret faktura": FakeLoginControl(text="Opret faktura"),
        "a[href*='/test-org-slug/invoices/']": FakeLoginControl(count=0, visible=False),
        "table tbody tr, [data-cy='table-item'], [role='row'], tr": FakeLoginControl(
            text="1 2026-08-01 TMP-INVOICE 10 DKK Kladde",
            on_click=open_edit,
        ),
        "text=Mere": FakeLoginControl(count=0, visible=False),
        "text=Slet": FakeLoginControl(count=0, visible=False),
        "text=Upsedasse!": FakeLoginControl(count=0, visible=False),
        "text=Upsedasse": FakeLoginControl(count=0, visible=False),
        "text=Log ind igen": FakeLoginControl(count=0, visible=False),
        "text=Overblik": FakeLoginControl(text="Overblik"),
        "text=Menu": FakeLoginControl(text="Menu"),
    }


def test_ui_invoices_delete_open_returns_success_for_mere_delete_chrome(tmp_path: Path) -> None:
    identity_path = tmp_path / "ui-org-identity.json"
    identity_path.write_text(
        json.dumps({"source": "ui_dashboard_path", "org_slug": "test-org-slug"}) + "\n",
        encoding="utf-8",
    )
    page_holder: dict[str, FakeLoginPage] = {}
    page = FakeLoginPage(
        final_url="https://mit.billy.dk/test-org-slug/dashboard",
        controls=_invoices_delete_shell_controls(page_holder),
        follow_goto=True,
    )
    page_holder["page"] = page
    context = FakeLoginContext(page)

    async def launcher(profile_path: str, **kwargs: bool) -> PersistentContext:
        return cast(PersistentContext, context)

    runtime = BrowserRuntime(
        profile_path=tmp_path / "profile",
        egress_manifest_path=write_browser_egress_fixture(tmp_path),
        launcher=launcher,
        org_identity_path=identity_path,
    )

    result = asyncio.run(runtime.ui_invoices_delete_open())

    assert result == UiInvoicesDeleteOpenSuccess(
        edit_open=True,
        mere_open=True,
        slet_text_visible=True,
        dupliker_visible=True,
        primary_slet_absent=True,
        shell_markers_present=True,
    )
    assert "test-org-slug" not in str(result.model_dump())
    assert page.closed
    assert any("click:text=Mere" in e for e in page.events)
    assert not any("click:text=Slet" in e for e in page.events)


def test_ui_invoices_delete_open_rejects_list_only(tmp_path: Path) -> None:
    identity_path = tmp_path / "ui-org-identity.json"
    identity_path.write_text(
        json.dumps({"source": "ui_dashboard_path", "org_slug": "test-org-slug"}) + "\n",
        encoding="utf-8",
    )
    controls = {
        "input[type='email'][name='email']": FakeLoginControl(count=0, visible=False),
        "input[type='password'][name='password']": FakeLoginControl(count=0, visible=False),
        "input[type='checkbox'][name='remember']": FakeLoginControl(count=0, visible=False),
        "button[data-cy='login-button']": FakeLoginControl(count=0, visible=False),
        "h1": FakeLoginControl(text="Fakturaer"),
        "body": FakeLoginControl(text="Fakturaer Ingen fakturaer Opret faktura"),
        "text=Opret faktura": FakeLoginControl(text="Opret faktura"),
        "a[href*='/test-org-slug/invoices/']": FakeLoginControl(count=0, visible=False),
        "table tbody tr, [data-cy='table-item'], [role='row']": FakeLoginControl(
            count=0, visible=False
        ),
        "text=Overblik": FakeLoginControl(text="Overblik"),
        "text=Menu": FakeLoginControl(text="Menu"),
        "text=Upsedasse!": FakeLoginControl(count=0, visible=False),
        "text=Upsedasse": FakeLoginControl(count=0, visible=False),
        "text=Log ind igen": FakeLoginControl(count=0, visible=False),
    }
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
    result = asyncio.run(runtime.ui_invoices_delete_open())
    assert isinstance(result, ToolError)
    assert result.code is StableErrorCode.UI_CHANGED
    assert "invoices delete" in result.message
    assert page.closed


def test_ui_invoices_get_open_returns_ui_changed_when_empty_list(tmp_path: Path) -> None:
    identity_path = tmp_path / "ui-org-identity.json"
    identity_path.write_text(
        json.dumps({"source": "ui_dashboard_path", "org_slug": "test-org-slug"}) + "\n",
        encoding="utf-8",
    )
    controls = {
        "input[type='email'][name='email']": FakeLoginControl(count=0, visible=False),
        "input[type='password'][name='password']": FakeLoginControl(count=0, visible=False),
        "input[type='checkbox'][name='remember']": FakeLoginControl(count=0, visible=False),
        "button[data-cy='login-button']": FakeLoginControl(count=0, visible=False),
        "h1": FakeLoginControl(text="Fakturaer"),
        "body": FakeLoginControl(text="Fakturaer Ingen fakturaer Opret faktura"),
        "text=Opret faktura": FakeLoginControl(text="Opret faktura"),
        "a[href*='/test-org-slug/invoices/']": FakeLoginControl(count=0, visible=False),
        "table tbody tr, [data-cy='table-item'], [role='row']": FakeLoginControl(
            count=0, visible=False
        ),
        "text=Upsedasse!": FakeLoginControl(count=0, visible=False),
        "text=Upsedasse": FakeLoginControl(count=0, visible=False),
        "text=Log ind igen": FakeLoginControl(count=0, visible=False),
        "text=Overblik": FakeLoginControl(text="Overblik"),
        "text=Menu": FakeLoginControl(text="Menu"),
    }
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
    result = asyncio.run(runtime.ui_invoices_get_open())
    assert isinstance(result, ToolError)
    assert result.code == StableErrorCode.UI_CHANGED


def _bills_get_shell_controls(
    page_holder: dict[str, FakeLoginPage],
) -> dict[str, FakeLoginControl]:
    def open_detail() -> None:
        page = page_holder["page"]
        # research170: list click may land on edit; runtime soft-navigates to read path.
        page.url = "https://mit.billy.dk/test-org-slug/bills/bill-1/edit"
        updates = {
            "body": FakeLoginControl(
                text="Ret regning Godkend Leverandør Kladde Restbeløb 25,00 Overblik Menu"
            ),
            "text=Kladde": FakeLoginControl(text="Kladde"),
            "text=Leverandør": FakeLoginControl(text="Leverandør"),
            "text=Restbeløb": FakeLoginControl(text="Restbeløb"),
            "text=Overblik": FakeLoginControl(text="Overblik"),
            "text=Menu": FakeLoginControl(text="Menu"),
        }
        for sel, control in updates.items():
            page.controls[sel] = control
            control.bind(page.events, sel)

    return {
        "input[type='email'][name='email']": FakeLoginControl(count=0, visible=False),
        "input[type='password'][name='password']": FakeLoginControl(count=0, visible=False),
        "input[type='checkbox'][name='remember']": FakeLoginControl(count=0, visible=False),
        "button[data-cy='login-button']": FakeLoginControl(count=0, visible=False),
        "h1": FakeLoginControl(text="Køb"),
        "body": FakeLoginControl(text="Køb Opret køb Mere 1 Kladde TMP-BILL"),
        "text=Opret køb": FakeLoginControl(text="Opret køb"),
        "a[href*='/test-org-slug/bills/']": FakeLoginControl(count=0, visible=False),
        "table tbody tr, [data-cy='table-item'], [role='row'], tr": FakeLoginControl(
            text="1 2026-08-01 TMP-BILL 25 DKK Kladde",
            on_click=open_detail,
        ),
        "text=Upsedasse!": FakeLoginControl(count=0, visible=False),
        "text=Upsedasse": FakeLoginControl(count=0, visible=False),
        "text=Log ind igen": FakeLoginControl(count=0, visible=False),
        "text=Overblik": FakeLoginControl(text="Overblik"),
        "text=Menu": FakeLoginControl(text="Menu"),
    }


def test_ui_bills_get_open_returns_success_for_detail(tmp_path: Path) -> None:
    identity_path = tmp_path / "ui-org-identity.json"
    identity_path.write_text(
        json.dumps({"source": "ui_dashboard_path", "org_slug": "test-org-slug"}) + "\n",
        encoding="utf-8",
    )
    page_holder: dict[str, FakeLoginPage] = {}
    page = FakeLoginPage(
        final_url="https://mit.billy.dk/test-org-slug/dashboard",
        controls=_bills_get_shell_controls(page_holder),
        follow_goto=True,
    )
    page_holder["page"] = page
    context = FakeLoginContext(page)

    async def launcher(profile_path: str, **kwargs: bool) -> PersistentContext:
        return cast(PersistentContext, context)

    runtime = BrowserRuntime(
        profile_path=tmp_path / "profile",
        egress_manifest_path=write_browser_egress_fixture(tmp_path),
        launcher=launcher,
        org_identity_path=identity_path,
    )

    result = asyncio.run(runtime.ui_bills_get_open())

    assert result == UiBillsGetOpenSuccess(
        detail_open=True,
        kladde_or_state_chrome_present=True,
        supplier_chrome_present=True,
        amount_or_line_chrome_present=True,
        shell_markers_present=True,
    )
    assert "test-org-slug" not in str(result.model_dump())
    assert page.closed
    assert not any("click:text=Gem" in e for e in page.events)
    assert not any("click:text=Godkend" in e for e in page.events)


def test_ui_bills_get_open_returns_ui_changed_when_empty_list(tmp_path: Path) -> None:
    identity_path = tmp_path / "ui-org-identity.json"
    identity_path.write_text(
        json.dumps({"source": "ui_dashboard_path", "org_slug": "test-org-slug"}) + "\n",
        encoding="utf-8",
    )
    controls = {
        "input[type='email'][name='email']": FakeLoginControl(count=0, visible=False),
        "input[type='password'][name='password']": FakeLoginControl(count=0, visible=False),
        "input[type='checkbox'][name='remember']": FakeLoginControl(count=0, visible=False),
        "button[data-cy='login-button']": FakeLoginControl(count=0, visible=False),
        "h1": FakeLoginControl(text="Køb"),
        "body": FakeLoginControl(text="Køb Ingen køb Opret køb"),
        "text=Opret køb": FakeLoginControl(text="Opret køb"),
        "a[href*='/test-org-slug/bills/']": FakeLoginControl(count=0, visible=False),
        "table tbody tr, [data-cy='table-item'], [role='row']": FakeLoginControl(
            count=0, visible=False
        ),
        "text=Upsedasse!": FakeLoginControl(count=0, visible=False),
        "text=Upsedasse": FakeLoginControl(count=0, visible=False),
        "text=Log ind igen": FakeLoginControl(count=0, visible=False),
        "text=Overblik": FakeLoginControl(text="Overblik"),
        "text=Menu": FakeLoginControl(text="Menu"),
    }
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
    result = asyncio.run(runtime.ui_bills_get_open())
    assert isinstance(result, ToolError)
    assert result.code == StableErrorCode.UI_CHANGED


def _bills_update_shell_controls(
    page_holder: dict[str, FakeLoginPage],
) -> dict[str, FakeLoginControl]:
    def open_edit() -> None:
        page = page_holder["page"]
        # research172: list text-click lands on edit dual.
        page.url = "https://mit.billy.dk/test-org-slug/bills/bill-1/edit"
        updates = {
            "body": FakeLoginControl(
                text=(
                    "Ret regning Godkend Opdater Slet Leverandør Bilagsdato "
                    "Forfaldsdato Linje #1 Beskrivelse Overblik Menu"
                )
            ),
            "text=Overblik": FakeLoginControl(text="Overblik"),
            "text=Menu": FakeLoginControl(text="Menu"),
            "input:visible, textarea:visible, select:visible": FakeLoginControl(
                count=4, visible=True
            ),
            "input, textarea, select": FakeLoginControl(count=4, visible=True),
        }
        for sel, control in updates.items():
            page.controls[sel] = control
            control.bind(page.events, sel)

    return {
        "input[type='email'][name='email']": FakeLoginControl(count=0, visible=False),
        "input[type='password'][name='password']": FakeLoginControl(count=0, visible=False),
        "input[type='checkbox'][name='remember']": FakeLoginControl(count=0, visible=False),
        "button[data-cy='login-button']": FakeLoginControl(count=0, visible=False),
        "h1": FakeLoginControl(text="Køb"),
        "body": FakeLoginControl(text="Køb Opret køb Mere 1 Kladde TMP-BILL"),
        "text=Opret køb": FakeLoginControl(text="Opret køb"),
        "a[href*='/test-org-slug/bills/']": FakeLoginControl(count=0, visible=False),
        "table tbody tr, [data-cy='table-item'], [role='row'], tr": FakeLoginControl(
            text="1 2026-08-01 TMP-BILL 25 DKK Kladde",
            on_click=open_edit,
        ),
        "text=Upsedasse!": FakeLoginControl(count=0, visible=False),
        "text=Upsedasse": FakeLoginControl(count=0, visible=False),
        "text=Log ind igen": FakeLoginControl(count=0, visible=False),
        "text=Overblik": FakeLoginControl(text="Overblik"),
        "text=Menu": FakeLoginControl(text="Menu"),
    }


def _bills_delete_shell_controls(
    page_holder: dict[str, FakeLoginPage],
) -> dict[str, FakeLoginControl]:
    def open_confirm() -> None:
        page = page_holder["page"]
        page.url = "https://mit.billy.dk/test-org-slug/bills/bill-1/edit"
        page.controls["body"] = FakeLoginControl(
            text=(
                "Ret regning Godkend Opdater Slet Annuller Leverandør Bilagsdato "
                "Forfaldsdato Overblik Menu"
            )
        )
        page.controls["body"].bind(page.events, "body")
        page.controls["text=Slet"] = FakeLoginControl(text="Slet", count=2, visible=True)
        page.controls["text=Slet"].bind(page.events, "text=Slet")
        page.controls["text=Annuller"] = FakeLoginControl(text="Annuller", on_click=dismiss_confirm)
        page.controls["text=Annuller"].bind(page.events, "text=Annuller")

    def dismiss_confirm() -> None:
        page = page_holder["page"]
        page.url = "https://mit.billy.dk/test-org-slug/bills/bill-1/edit"
        page.controls["body"] = FakeLoginControl(
            text=(
                "Ret regning Godkend Opdater Slet Leverandør Bilagsdato Forfaldsdato Overblik Menu"
            )
        )
        page.controls["body"].bind(page.events, "body")
        page.controls["text=Slet"] = FakeLoginControl(text="Slet", count=1, visible=True)
        page.controls["text=Slet"].bind(page.events, "text=Slet")
        page.controls["text=Annuller"] = FakeLoginControl(count=0, visible=False)
        page.controls["text=Annuller"].bind(page.events, "text=Annuller")

    def open_edit() -> None:
        page = page_holder["page"]
        page.url = "https://mit.billy.dk/test-org-slug/bills/bill-1/edit"
        page.controls["body"] = FakeLoginControl(
            text=(
                "Ret regning Godkend Opdater Slet Leverandør Bilagsdato "
                "Forfaldsdato Linje #1 Overblik Menu"
            )
        )
        page.controls["body"].bind(page.events, "body")
        page.controls["text=Slet"] = FakeLoginControl(
            text="Slet", count=1, visible=True, on_click=open_confirm
        )
        page.controls["text=Slet"].bind(page.events, "text=Slet")
        page.controls["text=Annuller"] = FakeLoginControl(count=0, visible=False)
        page.controls["text=Annuller"].bind(page.events, "text=Annuller")
        page.controls["text=Overblik"] = FakeLoginControl(text="Overblik")
        page.controls["text=Overblik"].bind(page.events, "text=Overblik")
        page.controls["text=Menu"] = FakeLoginControl(text="Menu")
        page.controls["text=Menu"].bind(page.events, "text=Menu")

    return {
        "input[type='email'][name='email']": FakeLoginControl(count=0, visible=False),
        "input[type='password'][name='password']": FakeLoginControl(count=0, visible=False),
        "input[type='checkbox'][name='remember']": FakeLoginControl(count=0, visible=False),
        "button[data-cy='login-button']": FakeLoginControl(count=0, visible=False),
        "h1": FakeLoginControl(text="Køb"),
        "body": FakeLoginControl(text="Køb Opret køb Mere 1 Kladde TMP-BILL"),
        "text=Opret køb": FakeLoginControl(text="Opret køb"),
        "a[href*='/test-org-slug/bills/']": FakeLoginControl(count=0, visible=False),
        "table tbody tr, [data-cy='table-item'], [role='row'], tr": FakeLoginControl(
            text="1 2026-08-01 TMP-BILL 25 DKK Kladde",
            on_click=open_edit,
        ),
        "text=Slet": FakeLoginControl(count=0, visible=False),
        "text=Annuller": FakeLoginControl(count=0, visible=False),
        "text=Upsedasse!": FakeLoginControl(count=0, visible=False),
        "text=Upsedasse": FakeLoginControl(count=0, visible=False),
        "text=Log ind igen": FakeLoginControl(count=0, visible=False),
        "text=Overblik": FakeLoginControl(text="Overblik"),
        "text=Menu": FakeLoginControl(text="Menu"),
    }


def test_ui_bills_update_open_returns_success_for_edit_form(tmp_path: Path) -> None:
    identity_path = tmp_path / "ui-org-identity.json"
    identity_path.write_text(
        json.dumps({"source": "ui_dashboard_path", "org_slug": "test-org-slug"}) + "\n",
        encoding="utf-8",
    )
    page_holder: dict[str, FakeLoginPage] = {}
    page = FakeLoginPage(
        final_url="https://mit.billy.dk/test-org-slug/dashboard",
        controls=_bills_update_shell_controls(page_holder),
        follow_goto=True,
    )
    page_holder["page"] = page
    context = FakeLoginContext(page)

    async def launcher(profile_path: str, **kwargs: bool) -> PersistentContext:
        return cast(PersistentContext, context)

    runtime = BrowserRuntime(
        profile_path=tmp_path / "profile",
        egress_manifest_path=write_browser_egress_fixture(tmp_path),
        launcher=launcher,
        org_identity_path=identity_path,
    )

    result = asyncio.run(runtime.ui_bills_update_open())

    assert result == UiBillsUpdateOpenSuccess(
        form_open=True,
        ret_regning_chrome_present=True,
        opdater_present=True,
        leverandor_or_dates_chrome_present=True,
        inputs_present=True,
        shell_markers_present=True,
    )
    assert "test-org-slug" not in str(result.model_dump())
    assert page.closed
    assert not any("click:text=Opdater" in e for e in page.events)
    assert not any("click:text=Godkend" in e for e in page.events)
    assert not any("click:text=Slet" in e for e in page.events)


def test_ui_bills_update_open_returns_ui_changed_when_empty_list(tmp_path: Path) -> None:
    identity_path = tmp_path / "ui-org-identity.json"
    identity_path.write_text(
        json.dumps({"source": "ui_dashboard_path", "org_slug": "test-org-slug"}) + "\n",
        encoding="utf-8",
    )
    controls = {
        "input[type='email'][name='email']": FakeLoginControl(count=0, visible=False),
        "input[type='password'][name='password']": FakeLoginControl(count=0, visible=False),
        "input[type='checkbox'][name='remember']": FakeLoginControl(count=0, visible=False),
        "button[data-cy='login-button']": FakeLoginControl(count=0, visible=False),
        "h1": FakeLoginControl(text="Køb"),
        "body": FakeLoginControl(text="Køb Ingen køb Opret køb"),
        "text=Opret køb": FakeLoginControl(text="Opret køb"),
        "a[href*='/test-org-slug/bills/']": FakeLoginControl(count=0, visible=False),
        "table tbody tr, [data-cy='table-item'], [role='row']": FakeLoginControl(
            count=0, visible=False
        ),
        "text=Upsedasse!": FakeLoginControl(count=0, visible=False),
        "text=Upsedasse": FakeLoginControl(count=0, visible=False),
        "text=Log ind igen": FakeLoginControl(count=0, visible=False),
        "text=Overblik": FakeLoginControl(text="Overblik"),
        "text=Menu": FakeLoginControl(text="Menu"),
    }
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
    result = asyncio.run(runtime.ui_bills_update_open())
    assert isinstance(result, ToolError)
    assert result.code == StableErrorCode.UI_CHANGED


def test_ui_bills_delete_open_returns_success_for_slet_confirm_dismiss(tmp_path: Path) -> None:
    from billy_mcp.models import UiBillsDeleteOpenSuccess

    identity_path = tmp_path / "ui-org-identity.json"
    identity_path.write_text(
        json.dumps({"source": "ui_dashboard_path", "org_slug": "test-org-slug"}) + "\n",
        encoding="utf-8",
    )
    page_holder: dict[str, FakeLoginPage] = {}
    page = FakeLoginPage(
        final_url="https://mit.billy.dk/test-org-slug/dashboard",
        controls=_bills_delete_shell_controls(page_holder),
        follow_goto=True,
    )
    page_holder["page"] = page
    context = FakeLoginContext(page)

    async def launcher(profile_path: str, **kwargs: bool) -> PersistentContext:
        return cast(PersistentContext, context)

    runtime = BrowserRuntime(
        profile_path=tmp_path / "profile",
        egress_manifest_path=write_browser_egress_fixture(tmp_path),
        launcher=launcher,
        org_identity_path=identity_path,
    )

    result = asyncio.run(runtime.ui_bills_delete_open())

    assert result == UiBillsDeleteOpenSuccess(
        edit_open=True,
        slet_present=True,
        confirm_open=True,
        annuller_present=True,
        confirm_dismissed=True,
        shell_markers_present=True,
    )
    assert "test-org-slug" not in str(result.model_dump())
    assert page.closed
    assert any("click:text=Slet" in e for e in page.events)
    assert any("click:text=Annuller" in e for e in page.events)
    # Never click second Slet as confirm; only primary open then Annuller.
    assert sum(1 for e in page.events if e == "click:text=Slet") == 1


def test_ui_bills_delete_open_returns_ui_changed_when_empty_list(tmp_path: Path) -> None:
    identity_path = tmp_path / "ui-org-identity.json"
    identity_path.write_text(
        json.dumps({"source": "ui_dashboard_path", "org_slug": "test-org-slug"}) + "\n",
        encoding="utf-8",
    )
    controls = {
        "input[type='email'][name='email']": FakeLoginControl(count=0, visible=False),
        "input[type='password'][name='password']": FakeLoginControl(count=0, visible=False),
        "input[type='checkbox'][name='remember']": FakeLoginControl(count=0, visible=False),
        "button[data-cy='login-button']": FakeLoginControl(count=0, visible=False),
        "h1": FakeLoginControl(text="Køb"),
        "body": FakeLoginControl(text="Køb Ingen køb Opret køb"),
        "text=Opret køb": FakeLoginControl(text="Opret køb"),
        "a[href*='/test-org-slug/bills/']": FakeLoginControl(count=0, visible=False),
        "table tbody tr, [data-cy='table-item'], [role='row'], tr": FakeLoginControl(
            count=0, visible=False
        ),
        "text=Slet": FakeLoginControl(count=0, visible=False),
        "text=Annuller": FakeLoginControl(count=0, visible=False),
        "text=Upsedasse!": FakeLoginControl(count=0, visible=False),
        "text=Upsedasse": FakeLoginControl(count=0, visible=False),
        "text=Log ind igen": FakeLoginControl(count=0, visible=False),
        "text=Overblik": FakeLoginControl(text="Overblik"),
        "text=Menu": FakeLoginControl(text="Menu"),
    }
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
    result = asyncio.run(runtime.ui_bills_delete_open())
    assert isinstance(result, ToolError)
    assert result.code == StableErrorCode.UI_CHANGED
