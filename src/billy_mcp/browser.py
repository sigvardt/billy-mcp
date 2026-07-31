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
    UiAddonsOpenSuccess,
    UiBankAccountsListSuccess,
    UiBankReconciliationOpenSuccess,
    UiBillsListSuccess,
    UiClientsListSuccess,
    UiCreditorBalancesListSuccess,
    UiDaybooksOpenSuccess,
    UiDebtorBalancesListSuccess,
    UiExportsOpenSuccess,
    UiFinancingOpenSuccess,
    UiIntegrationsOpenSuccess,
    UiInvoicesListSuccess,
    UiProductsImportSuccess,
    UiProductsListSuccess,
    UiQuotesListSuccess,
    UiReceiptInboxListSuccess,
    UiRecurringInvoicesListSuccess,
    UiReportsOpenSuccess,
    UiSaftExportsOpenSuccess,
    UiSuppliersListSuccess,
    UiTransactionsListSuccess,
    UiUploadsListSuccess,
    UiVatDeclarationsListSuccess,
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
# Research109: suppliers list shell (vendors; contacts isSupplier UI surface).
_SUPPLIERS_LIST_PATH = re.compile(r"^/[^/]+/suppliers$")
_SUPPLIERS_LIST_HEADING = "Leverandører"
_SUPPLIERS_CREATE_CTA = "Opret kontakt"
# Research110: purchases discovery maps to bills list shell (Køb); no /purchases route.
_BILLS_LIST_PATH = re.compile(r"^/[^/]+/bills$")
_BILLS_LIST_HEADING = "Køb"
_BILLS_CREATE_CTA = "Opret køb"
# Research111: debtor balances list shell (receivables); no /v2/debtorbalance API resource.
_DEBTOR_BALANCES_LIST_PATH = re.compile(r"^/[^/]+/debtorbalance$")
_DEBTOR_BALANCES_LIST_HEADING = "Tilgodehavender"
_DEBTOR_BALANCES_CREATE_CTA = "Opret faktura"
# Research112: creditor balances list shell (payables); no /v2/creditorbalance API resource.
_CREDITOR_BALANCES_LIST_PATH = re.compile(r"^/[^/]+/creditorbalance$")
_CREDITOR_BALANCES_LIST_HEADING = "Skyldige udgifter"
_CREDITOR_BALANCES_CREATE_CTA = "Opret køb"
# Research113: uploads (Bilag) shell; no /v2/uploads API resource. Never set file inputs.
_UPLOADS_LIST_PATH = re.compile(r"^/[^/]+/uploads$")
_UPLOADS_LIST_HEADING = "Bilag"
_UPLOADS_UPLOAD_CTA = "Upload filer"
# Research114: receipt inbox (Bilagsindbakke) via /vouchers; distinct from uploads/Bilag.
# Never set file inputs; never click Ret or upload CTAs.
_RECEIPT_INBOX_LIST_PATH = re.compile(r"^/[^/]+/vouchers$")
_RECEIPT_INBOX_LIST_HEADING = "Bilagsindbakke"
# Research115: bank reconciliation (Afstemning) via bank_accounts/:id/sync (underscore).
# Distinct from bank-accounts list (hyphen) / Bankkonti. Harvest Afstemning href only.
# Never click Forbind til bank / Importer / Match.
_BANK_RECONCILIATION_PATH = re.compile(r"^/[^/]+/bank_accounts/[^/]+/sync$")
_AFSTEMNING_NAV_LABEL = "Afstemning"
_AFSTEMNING_HREF_SELECTORS = (
    "a[href*='/bank_accounts/'][href*='/sync']",
    "a[href*='bank_accounts'][href$='/sync']",
    "text=Afstemning",
)
# Research123: add-ons (Fordele) hub. Path hyphen required. Soft aliases rejected.
# Never click partner CTAs (install/connect/access-token/loan/apply).
_ADDONS_PATH = re.compile(r"^/[^/]+/add-ons$")
_ADDONS_HEADING = "Fordele"
_ADDONS_NAV_LABEL = "Udforsk integrationer"
# Research124: integrations soft-empty classification (not Fordele; not marketing).
# Path exact integrations leaf. Never navigate www.billy.dk; never partner CTAs.
_INTEGRATIONS_PATH = re.compile(r"^/[^/]+/integrations$")
# Research116: financing landing shell (Ansøg om erhvervslån). No invent financing API.
# Never click apply/offer/consent/submit (design §14.4 external financing).
_FINANCING_PATH = re.compile(r"^/[^/]+/financing$")
_FINANCING_HEADING = "Ansøg om erhvervslån"
_FINANCING_NAV_LABEL = "Ansøg om lån"
_FINANCING_APPLY_CTA = "Få et uforpligtende tilbud"
# Research117: daybook editor shell (Kassekladde). Bare /daybooks is Upsedasse.
# Never click Opret ny kassekladde / Tilføj kassekladdelinje / Bogfør / Ny postering.
_DAYBOOKS_EDITOR_PATH = re.compile(r"^/[^/]+/daybooks/new$")
_DAYBOOKS_BARE_PATH = re.compile(r"^/[^/]+/daybooks$")
_DAYBOOKS_EDITOR_MARKERS = (
    "Opret ny kassekladde",
    "Tilføj kassekladdelinje",
    "Ingen postering valgt",
)
# Research118: transactions (Posteringer) list shell. Nested /transactions/:segment is create.
# Never click Ny postering / Bogfør / void / delete.
_TRANSACTIONS_LIST_PATH = re.compile(r"^/[^/]+/transactions$")
_TRANSACTIONS_LIST_HEADING = "Posteringer"
_TRANSACTIONS_CREATE_CTA = "Ny postering"
# Research119: reports (Rapporter) hub. Bare /reports is soft empty chrome.
# Accept optional tab profit-and-loss|balance|trial-balance. Never click Eksport.
_REPORTS_HUB_PATH = re.compile(
    r"^/[^/]+/reports-all(?:/(?:profit-and-loss|balance|trial-balance))?$"
)
_REPORTS_HUB_HEADING = "Rapporter"
_REPORTS_EXPORT_CTA = "Eksport"
_REPORTS_TAB_MARKERS = (
    "Resultatopgørelse",
    "Balance",
    "Saldobalance",
)
# Research120: VAT declarations (Momsangivelser) list shell. Soft aliases reject.
# Empty table body valid. Never click declare/submit/export.
_VAT_DECLARATIONS_LIST_PATH = re.compile(r"^/[^/]+/vat-declarations$")
_VAT_DECLARATIONS_LIST_HEADING = "Momsangivelser"
_VAT_DECLARATIONS_PERIOD_MARKER = "Periode"
# Research121: exports hub (Eksportér data). Soft aliases reject. Never click
# Eksport / Download / Eksportér som SAF-T (observe-only).
_EXPORTS_HUB_PATH = re.compile(r"^/[^/]+/exports$")
_EXPORTS_HUB_HEADING = "Eksportér data"
_EXPORTS_HUB_CHROME_MARKERS = (
    "Genveje til rapporten",
    "Eksport",
    "Debitorliste",
    "Kreditorliste",
)
_EXPORTS_SAFT_CTA = "Eksportér som SAF-T"
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

    @property
    def first(self) -> LoginControl:
        """Playwright first-match seam for multi-match locators."""
        ...

    async def count(self) -> int: ...

    async def is_visible(self) -> bool: ...

    async def inner_text(self) -> str: ...

    async def fill(self, value: str) -> None: ...

    async def check(self) -> None: ...

    async def click(self) -> None: ...

    async def get_attribute(self, name: str) -> str | None: ...


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


class UiSuppliersListService(Protocol):
    """Injectable seam for the read-only suppliers list shell observation."""

    async def ui_suppliers_list(self) -> UiSuppliersListSuccess | ToolError: ...


class UiBillsListService(Protocol):
    """Injectable seam for the read-only bills (purchases) list shell observation."""

    async def ui_bills_list(self) -> UiBillsListSuccess | ToolError: ...


class UiDebtorBalancesListService(Protocol):
    """Injectable seam for the read-only debtor balances list shell observation."""

    async def ui_debtor_balances_list(self) -> UiDebtorBalancesListSuccess | ToolError: ...


class UiCreditorBalancesListService(Protocol):
    """Injectable seam for the read-only creditor balances list shell observation."""

    async def ui_creditor_balances_list(self) -> UiCreditorBalancesListSuccess | ToolError: ...


class UiUploadsListService(Protocol):
    """Injectable seam for the read-only uploads (Bilag) list shell observation."""

    async def ui_uploads_list(self) -> UiUploadsListSuccess | ToolError: ...


class UiReceiptInboxListService(Protocol):
    """Injectable seam for the read-only receipt inbox (Bilagsindbakke) list shell."""

    async def ui_receipt_inbox_list(self) -> UiReceiptInboxListSuccess | ToolError: ...


class UiBankReconciliationOpenService(Protocol):
    """Injectable seam for the read-only bank reconciliation (Afstemning) shell open."""

    async def ui_bank_reconciliation_open(self) -> UiBankReconciliationOpenSuccess | ToolError: ...


class UiFinancingOpenService(Protocol):
    """Injectable seam for the read-only financing (Ansøg om erhvervslån) shell open."""

    async def ui_financing_open(self) -> UiFinancingOpenSuccess | ToolError: ...


class UiDaybooksOpenService(Protocol):
    """Injectable seam for the read-only daybook (Kassekladde) editor shell open."""

    async def ui_daybooks_open(self) -> UiDaybooksOpenSuccess | ToolError: ...


class UiTransactionsListService(Protocol):
    """Injectable seam for the read-only transactions (Posteringer) list shell open."""

    async def ui_transactions_list(self) -> UiTransactionsListSuccess | ToolError: ...


class UiReportsOpenService(Protocol):
    """Injectable seam for the read-only reports (Rapporter) hub shell open."""

    async def ui_reports_open(self) -> UiReportsOpenSuccess | ToolError: ...


class UiVatDeclarationsListService(Protocol):
    """Injectable seam for the read-only VAT declarations (Momsangivelser) list shell."""

    async def ui_vat_declarations_list(self) -> UiVatDeclarationsListSuccess | ToolError: ...


class UiExportsOpenService(Protocol):
    """Injectable seam for the read-only exports (Eksportér data) hub shell open."""

    async def ui_exports_open(self) -> UiExportsOpenSuccess | ToolError: ...


class UiSaftExportsOpenService(Protocol):
    """Injectable seam for SAF-T CTA observe-only open on the exports hub."""

    async def ui_saft_exports_open(self) -> UiSaftExportsOpenSuccess | ToolError: ...


class UiAddonsOpenService(Protocol):
    """Injectable seam for the read-only Fordele (add-ons) hub shell open."""

    async def ui_addons_open(self) -> UiAddonsOpenSuccess | ToolError: ...


class UiIntegrationsOpenService(Protocol):
    """Injectable seam for integrations soft-empty classification (research124)."""

    async def ui_integrations_open(self) -> UiIntegrationsOpenSuccess | ToolError: ...


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

    async def ui_suppliers_list(self) -> UiSuppliersListSuccess | ToolError:
        """Open the suppliers list shell for the current authenticated UI session only."""

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
                return _ui_suppliers_changed_error()

            suppliers_url = f"https://mit.billy.dk/{slug}/suppliers"
            await page.goto(suppliers_url, wait_until="domcontentloaded")
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
                    return _ui_suppliers_changed_error()
                if _is_suppliers_list_url(page.url) and await _has_suppliers_list_signature(page):
                    return UiSuppliersListSuccess(
                        create_action_visible=True,
                        shell_markers_present=await _has_shell_nav_markers(page),
                    )
                await asyncio.sleep(0.2)
            return _ui_suppliers_changed_error()
        except BrowserEgressPolicyLoadError:
            return ToolError(
                code=StableErrorCode.EGRESS_DENIED,
                message="Browser egress policy prevented the suppliers list observation.",
            )
        except Exception:
            return ToolError(
                code=StableErrorCode.BILLY_ERROR,
                message="Browser suppliers list observation could not be completed.",
            )
        finally:
            if page is not None:
                try:
                    await page.close()
                except Exception:
                    pass

    async def ui_bills_list(self) -> UiBillsListSuccess | ToolError:
        """Open the bills (purchases / Køb) list shell for the authenticated UI session only."""

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
                return _ui_bills_changed_error()

            bills_url = f"https://mit.billy.dk/{slug}/bills"
            await page.goto(bills_url, wait_until="domcontentloaded")
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
                    return _ui_bills_changed_error()
                if _is_bills_list_url(page.url) and await _has_bills_list_signature(page):
                    return UiBillsListSuccess(
                        create_action_visible=True,
                        shell_markers_present=await _has_shell_nav_markers(page),
                    )
                await asyncio.sleep(0.2)
            return _ui_bills_changed_error()
        except BrowserEgressPolicyLoadError:
            return ToolError(
                code=StableErrorCode.EGRESS_DENIED,
                message="Browser egress policy prevented the bills list observation.",
            )
        except Exception:
            return ToolError(
                code=StableErrorCode.BILLY_ERROR,
                message="Browser bills list observation could not be completed.",
            )
        finally:
            if page is not None:
                try:
                    await page.close()
                except Exception:
                    pass

    async def ui_debtor_balances_list(self) -> UiDebtorBalancesListSuccess | ToolError:
        """Open the debtor balances list shell for the authenticated UI session only."""

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
                return _ui_debtor_balances_changed_error()

            debtor_url = f"https://mit.billy.dk/{slug}/debtorbalance"
            await page.goto(debtor_url, wait_until="domcontentloaded")
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
                    return _ui_debtor_balances_changed_error()
                if _is_debtor_balances_list_url(
                    page.url
                ) and await _has_debtor_balances_list_signature(page):
                    return UiDebtorBalancesListSuccess(
                        create_action_visible=True,
                        shell_markers_present=await _has_shell_nav_markers(page),
                    )
                await asyncio.sleep(0.2)
            return _ui_debtor_balances_changed_error()
        except BrowserEgressPolicyLoadError:
            return ToolError(
                code=StableErrorCode.EGRESS_DENIED,
                message="Browser egress policy prevented the debtor balances list observation.",
            )
        except Exception:
            return ToolError(
                code=StableErrorCode.BILLY_ERROR,
                message="Browser debtor balances list observation could not be completed.",
            )
        finally:
            if page is not None:
                try:
                    await page.close()
                except Exception:
                    pass

    async def ui_creditor_balances_list(self) -> UiCreditorBalancesListSuccess | ToolError:
        """Open the creditor balances list shell for the authenticated UI session only."""

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
                return _ui_creditor_balances_changed_error()

            creditor_url = f"https://mit.billy.dk/{slug}/creditorbalance"
            await page.goto(creditor_url, wait_until="domcontentloaded")
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
                    return _ui_creditor_balances_changed_error()
                if _is_creditor_balances_list_url(
                    page.url
                ) and await _has_creditor_balances_list_signature(page):
                    return UiCreditorBalancesListSuccess(
                        create_action_visible=True,
                        shell_markers_present=await _has_shell_nav_markers(page),
                    )
                await asyncio.sleep(0.2)
            return _ui_creditor_balances_changed_error()
        except BrowserEgressPolicyLoadError:
            return ToolError(
                code=StableErrorCode.EGRESS_DENIED,
                message="Browser egress policy prevented the creditor balances list observation.",
            )
        except Exception:
            return ToolError(
                code=StableErrorCode.BILLY_ERROR,
                message="Browser creditor balances list observation could not be completed.",
            )
        finally:
            if page is not None:
                try:
                    await page.close()
                except Exception:
                    pass

    async def ui_uploads_list(self) -> UiUploadsListSuccess | ToolError:
        """Open the uploads (Bilag) list shell for the authenticated UI session only."""

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
                return _ui_uploads_changed_error()

            uploads_url = f"https://mit.billy.dk/{slug}/uploads"
            await page.goto(uploads_url, wait_until="domcontentloaded")
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
                    return _ui_uploads_changed_error()
                if _is_uploads_list_url(page.url) and await _has_uploads_list_signature(page):
                    return UiUploadsListSuccess(
                        upload_action_visible=True,
                        shell_markers_present=await _has_shell_nav_markers(page),
                    )
                await asyncio.sleep(0.2)
            return _ui_uploads_changed_error()
        except BrowserEgressPolicyLoadError:
            return ToolError(
                code=StableErrorCode.EGRESS_DENIED,
                message="Browser egress policy prevented the uploads list observation.",
            )
        except Exception:
            return ToolError(
                code=StableErrorCode.BILLY_ERROR,
                message="Browser uploads list observation could not be completed.",
            )
        finally:
            if page is not None:
                try:
                    await page.close()
                except Exception:
                    pass

    async def ui_receipt_inbox_list(self) -> UiReceiptInboxListSuccess | ToolError:
        """Open the receipt inbox (Bilagsindbakke / vouchers) list shell only."""

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
                return _ui_receipt_inbox_changed_error()

            vouchers_url = f"https://mit.billy.dk/{slug}/vouchers"
            await page.goto(vouchers_url, wait_until="domcontentloaded")
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
                    return _ui_receipt_inbox_changed_error()
                if _is_receipt_inbox_list_url(page.url) and await _has_receipt_inbox_list_signature(
                    page
                ):
                    return UiReceiptInboxListSuccess(
                        file_control_present=await _has_file_input_present(page),
                        shell_markers_present=await _has_shell_nav_markers(page),
                    )
                await asyncio.sleep(0.2)
            return _ui_receipt_inbox_changed_error()
        except BrowserEgressPolicyLoadError:
            return ToolError(
                code=StableErrorCode.EGRESS_DENIED,
                message="Browser egress policy prevented the receipt inbox list observation.",
            )
        except Exception:
            return ToolError(
                code=StableErrorCode.BILLY_ERROR,
                message="Browser receipt inbox list observation could not be completed.",
            )
        finally:
            if page is not None:
                try:
                    await page.close()
                except Exception:
                    pass

    async def ui_bank_reconciliation_open(self) -> UiBankReconciliationOpenSuccess | ToolError:
        """Open the bank reconciliation (Afstemning) shell for the current session only."""

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
                return _ui_bank_reconciliation_changed_error()

            # Land on bank accounts list first so Afstemning nav href is present.
            bank_accounts_url = f"https://mit.billy.dk/{slug}/bank-accounts"
            await page.goto(bank_accounts_url, wait_until="domcontentloaded")
            await _await_page_settle(page)

            if await _has_known_login_page(page):
                return _auth_required_error()
            if await _has_interaction_challenge(page):
                return ToolError(
                    code=StableErrorCode.AUTH_INTERACTION_REQUIRED,
                    message="Browser authentication requires a non-automatable challenge.",
                )
            if await _has_error_shell_markers(page):
                return _ui_bank_reconciliation_changed_error()

            recon_url = await _harvest_afstemning_reconciliation_url(page, slug)
            if recon_url is None:
                return _ui_bank_reconciliation_changed_error()

            await page.goto(recon_url, wait_until="domcontentloaded")
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
                    return _ui_bank_reconciliation_changed_error()
                if _is_bank_reconciliation_url(page.url):
                    heading = await _read_optional_heading(page)
                    empty_shell = await _is_empty_content_shell(page, heading)
                    # Reject conflation with bank accounts list (Bankkonti on hyphen path).
                    if heading.strip() == _BANK_ACCOUNTS_LIST_HEADING:
                        return _ui_bank_reconciliation_changed_error()
                    if _is_bank_accounts_list_url(page.url):
                        return _ui_bank_reconciliation_changed_error()
                    return UiBankReconciliationOpenSuccess(
                        heading=heading,
                        empty_content_shell=empty_shell,
                        afstemning_nav_visible=await _has_afstemning_nav_visible(page),
                        shell_markers_present=await _has_shell_nav_markers(page),
                    )
                await asyncio.sleep(0.2)
            return _ui_bank_reconciliation_changed_error()
        except BrowserEgressPolicyLoadError:
            return ToolError(
                code=StableErrorCode.EGRESS_DENIED,
                message=(
                    "Browser egress policy prevented the bank reconciliation shell observation."
                ),
            )
        except Exception:
            return ToolError(
                code=StableErrorCode.BILLY_ERROR,
                message="Browser bank reconciliation shell observation could not be completed.",
            )
        finally:
            if page is not None:
                try:
                    await page.close()
                except Exception:
                    pass

    async def ui_financing_open(self) -> UiFinancingOpenSuccess | ToolError:
        """Open the financing (Ansøg om erhvervslån) shell for the current session only."""

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
                return _ui_financing_changed_error()

            financing_url = f"https://mit.billy.dk/{slug}/financing"
            await page.goto(financing_url, wait_until="domcontentloaded")
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
                    return _ui_financing_changed_error()
                if _is_financing_url(page.url) and await _has_financing_signature(page):
                    # Reject bank shells if Billy ever redirects incorrectly.
                    if _is_bank_accounts_list_url(page.url) or _is_bank_reconciliation_url(
                        page.url
                    ):
                        return _ui_financing_changed_error()
                    return UiFinancingOpenSuccess(
                        apply_cta_observed=await _has_financing_apply_cta_observed(page),
                        shell_markers_present=await _has_shell_nav_markers(page),
                    )
                await asyncio.sleep(0.2)
            return _ui_financing_changed_error()
        except BrowserEgressPolicyLoadError:
            return ToolError(
                code=StableErrorCode.EGRESS_DENIED,
                message="Browser egress policy prevented the financing shell observation.",
            )
        except Exception:
            return ToolError(
                code=StableErrorCode.BILLY_ERROR,
                message="Browser financing shell observation could not be completed.",
            )
        finally:
            if page is not None:
                try:
                    await page.close()
                except Exception:
                    pass

    async def ui_daybooks_open(self) -> UiDaybooksOpenSuccess | ToolError:
        """Open the daybook editor (Kassekladde) shell for the current session only."""

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
                return _ui_daybooks_changed_error()

            daybooks_url = f"https://mit.billy.dk/{slug}/daybooks/new"
            await page.goto(daybooks_url, wait_until="domcontentloaded")
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
                    return _ui_daybooks_changed_error()
                if _is_daybooks_bare_url(page.url):
                    return _ui_daybooks_changed_error()
                if _is_daybooks_editor_url(page.url) and await _has_daybooks_editor_signature(page):
                    if _is_transactions_list_url(page.url):
                        return _ui_daybooks_changed_error()
                    return UiDaybooksOpenSuccess(
                        heading=await _read_optional_heading(page),
                        editor_markers_present=True,
                        shell_markers_present=await _has_shell_nav_markers(page),
                    )
                await asyncio.sleep(0.2)
            return _ui_daybooks_changed_error()
        except BrowserEgressPolicyLoadError:
            return ToolError(
                code=StableErrorCode.EGRESS_DENIED,
                message="Browser egress policy prevented the daybooks shell observation.",
            )
        except Exception:
            return ToolError(
                code=StableErrorCode.BILLY_ERROR,
                message="Browser daybooks shell observation could not be completed.",
            )
        finally:
            if page is not None:
                try:
                    await page.close()
                except Exception:
                    pass

    async def ui_transactions_list(self) -> UiTransactionsListSuccess | ToolError:
        """Open the transactions (Posteringer) list shell for the authenticated UI session only."""

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
                return _ui_transactions_changed_error()

            transactions_url = f"https://mit.billy.dk/{slug}/transactions"
            await page.goto(transactions_url, wait_until="domcontentloaded")
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
                    return _ui_transactions_changed_error()
                if _is_transactions_list_url(page.url) and await _has_transactions_list_signature(
                    page
                ):
                    return UiTransactionsListSuccess(
                        create_action_visible=True,
                        shell_markers_present=await _has_shell_nav_markers(page),
                    )
                await asyncio.sleep(0.2)
            return _ui_transactions_changed_error()
        except BrowserEgressPolicyLoadError:
            return ToolError(
                code=StableErrorCode.EGRESS_DENIED,
                message="Browser egress policy prevented the transactions list observation.",
            )
        except Exception:
            return ToolError(
                code=StableErrorCode.BILLY_ERROR,
                message="Browser transactions list observation could not be completed.",
            )
        finally:
            if page is not None:
                try:
                    await page.close()
                except Exception:
                    pass

    async def ui_reports_open(self) -> UiReportsOpenSuccess | ToolError:
        """Open the reports (Rapporter) hub shell for the authenticated UI session only."""

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
                return _ui_reports_changed_error()

            reports_url = f"https://mit.billy.dk/{slug}/reports-all"
            await page.goto(reports_url, wait_until="domcontentloaded")
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
                    return _ui_reports_changed_error()
                if _is_reports_hub_url(page.url) and await _has_reports_hub_signature(page):
                    return UiReportsOpenSuccess(
                        export_action_visible=await _has_reports_export_cta_visible(page),
                        shell_markers_present=await _has_shell_nav_markers(page),
                    )
                await asyncio.sleep(0.2)
            return _ui_reports_changed_error()
        except BrowserEgressPolicyLoadError:
            return ToolError(
                code=StableErrorCode.EGRESS_DENIED,
                message="Browser egress policy prevented the reports hub observation.",
            )
        except Exception:
            return ToolError(
                code=StableErrorCode.BILLY_ERROR,
                message="Browser reports hub observation could not be completed.",
            )
        finally:
            if page is not None:
                try:
                    await page.close()
                except Exception:
                    pass

    async def ui_vat_declarations_list(self) -> UiVatDeclarationsListSuccess | ToolError:
        """Open the VAT declarations (Momsangivelser) list shell for the session only."""

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
                return _ui_vat_declarations_changed_error()

            vat_url = f"https://mit.billy.dk/{slug}/vat-declarations"
            await page.goto(vat_url, wait_until="domcontentloaded")
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
                    return _ui_vat_declarations_changed_error()
                if _is_vat_declarations_list_url(
                    page.url
                ) and await _has_vat_declarations_list_signature(page):
                    return UiVatDeclarationsListSuccess(
                        period_column_visible=await _has_vat_declarations_period_visible(page),
                        shell_markers_present=await _has_shell_nav_markers(page),
                    )
                await asyncio.sleep(0.2)
            return _ui_vat_declarations_changed_error()
        except BrowserEgressPolicyLoadError:
            return ToolError(
                code=StableErrorCode.EGRESS_DENIED,
                message="Browser egress policy prevented the VAT declarations observation.",
            )
        except Exception:
            return ToolError(
                code=StableErrorCode.BILLY_ERROR,
                message="Browser VAT declarations list observation could not be completed.",
            )
        finally:
            if page is not None:
                try:
                    await page.close()
                except Exception:
                    pass

    async def ui_exports_open(self) -> UiExportsOpenSuccess | ToolError:
        """Open the exports (Eksportér data) hub shell for the authenticated UI session only."""

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
                return _ui_exports_changed_error()

            exports_url = f"https://mit.billy.dk/{slug}/exports"
            await page.goto(exports_url, wait_until="domcontentloaded")
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
                    return _ui_exports_changed_error()
                if _is_exports_hub_url(page.url) and await _has_exports_hub_signature(page):
                    return UiExportsOpenSuccess(
                        saft_export_cta_observed=await _has_exports_saft_cta_visible(page),
                        shell_markers_present=await _has_shell_nav_markers(page),
                    )
                await asyncio.sleep(0.2)
            return _ui_exports_changed_error()
        except BrowserEgressPolicyLoadError:
            return ToolError(
                code=StableErrorCode.EGRESS_DENIED,
                message="Browser egress policy prevented the exports hub observation.",
            )
        except Exception:
            return ToolError(
                code=StableErrorCode.BILLY_ERROR,
                message="Browser exports hub observation could not be completed.",
            )
        finally:
            if page is not None:
                try:
                    await page.close()
                except Exception:
                    pass

    async def ui_saft_exports_open(self) -> UiSaftExportsOpenSuccess | ToolError:
        """Open exports hub and require SAF-T CTA observe-only (research122; never click)."""

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
                return _ui_saft_exports_changed_error()

            exports_url = f"https://mit.billy.dk/{slug}/exports"
            await page.goto(exports_url, wait_until="domcontentloaded")
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
                    return _ui_saft_exports_changed_error()
                if _is_exports_hub_url(page.url) and await _has_exports_hub_signature(page):
                    if not await _has_exports_saft_cta_visible(page):
                        return _ui_saft_exports_changed_error()
                    return UiSaftExportsOpenSuccess(
                        shell_markers_present=await _has_shell_nav_markers(page),
                    )
                await asyncio.sleep(0.2)
            return _ui_saft_exports_changed_error()
        except BrowserEgressPolicyLoadError:
            return ToolError(
                code=StableErrorCode.EGRESS_DENIED,
                message="Browser egress policy prevented the SAF-T exports observation.",
            )
        except Exception:
            return ToolError(
                code=StableErrorCode.BILLY_ERROR,
                message="Browser SAF-T exports observation could not be completed.",
            )
        finally:
            if page is not None:
                try:
                    await page.close()
                except Exception:
                    pass

    async def ui_addons_open(self) -> UiAddonsOpenSuccess | ToolError:
        """Open the Fordele (add-ons) hub shell for the current session only.

        Research123: path /:org_slug/add-ons, h1 Fordele. Soft aliases rejected.
        Never click partner CTAs (Opret adgangsnøgle, Tilføj som betalingsmetode,
        Aktivér rykkerservice, Kom i gang, Ansøg om lån, Læs mere, Se alle vores
        integrationer, Install/Connect).
        """

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
                return _ui_addons_changed_error()

            addons_url = f"https://mit.billy.dk/{slug}/add-ons"
            await page.goto(addons_url, wait_until="domcontentloaded")
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
                    return _ui_addons_changed_error()
                if _is_addons_url(page.url) and await _has_addons_signature(page):
                    return UiAddonsOpenSuccess(
                        shell_markers_present=await _has_shell_nav_markers(page),
                    )
                await asyncio.sleep(0.2)
            return _ui_addons_changed_error()
        except BrowserEgressPolicyLoadError:
            return ToolError(
                code=StableErrorCode.EGRESS_DENIED,
                message="Browser egress policy prevented the add-ons shell observation.",
            )
        except Exception:
            return ToolError(
                code=StableErrorCode.BILLY_ERROR,
                message="Browser add-ons shell observation could not be completed.",
            )
        finally:
            if page is not None:
                try:
                    await page.close()
                except Exception:
                    pass

    async def ui_integrations_open(self) -> UiIntegrationsOpenSuccess | ToolError:
        """Classify the integrations soft-empty shell for the current session only.

        Research124: path /:org_slug/integrations is soft empty (empty h1, chrome
        only). Not Fordele/add-ons. Soft aliases rejected. Never navigate
        www.billy.dk. Never click Se alle vores integrationer or partner CTAs.
        Do not use nav label Udforsk integrationer (targets add-ons).
        """

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
                return _ui_integrations_changed_error()

            integrations_url = f"https://mit.billy.dk/{slug}/integrations"
            await page.goto(integrations_url, wait_until="domcontentloaded")
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
                    return _ui_integrations_changed_error()
                # Fail closed if Billy starts routing integrations to Fordele.
                if _is_addons_url(page.url) or await _has_addons_signature(page):
                    return _ui_integrations_changed_error()
                if _is_integrations_url(page.url) and await _has_integrations_soft_empty_signature(
                    page
                ):
                    return UiIntegrationsOpenSuccess(
                        shell_markers_present=await _has_shell_nav_markers(page),
                    )
                await asyncio.sleep(0.2)
            return _ui_integrations_changed_error()
        except BrowserEgressPolicyLoadError:
            return ToolError(
                code=StableErrorCode.EGRESS_DENIED,
                message="Browser egress policy prevented the integrations shell observation.",
            )
        except Exception:
            return ToolError(
                code=StableErrorCode.BILLY_ERROR,
                message="Browser integrations shell observation could not be completed.",
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


def _is_suppliers_list_url(url: str) -> bool:
    """Accept mit.billy.dk /:org_slug/suppliers, including Billy list query params."""

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
        and bool(_SUPPLIERS_LIST_PATH.match(parsed.path or ""))
    )


def _is_bills_list_url(url: str) -> bool:
    """Return True when the URL is the bills list shell path on the app host."""

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
        and bool(_BILLS_LIST_PATH.match(parsed.path or ""))
    )


def _is_debtor_balances_list_url(url: str) -> bool:
    """Return True when the URL is the debtor balances list shell path on the app host."""

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
        and bool(_DEBTOR_BALANCES_LIST_PATH.match(parsed.path or ""))
    )


def _is_creditor_balances_list_url(url: str) -> bool:
    """Return True when the URL is the creditor balances list shell path on the app host."""

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
        and bool(_CREDITOR_BALANCES_LIST_PATH.match(parsed.path or ""))
    )


def _is_uploads_list_url(url: str) -> bool:
    """Return True when the URL is the uploads (Bilag) list shell path on the app host."""

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
        and bool(_UPLOADS_LIST_PATH.match(parsed.path or ""))
    )


def _is_receipt_inbox_list_url(url: str) -> bool:
    """Return True when the URL is the receipt inbox (vouchers) list shell path."""

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
        and bool(_RECEIPT_INBOX_LIST_PATH.match(parsed.path or ""))
    )


def _is_bank_reconciliation_url(url: str) -> bool:
    """Return True when the URL is the Afstemning bank_accounts/:id/sync path class."""

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
        and bool(_BANK_RECONCILIATION_PATH.match(parsed.path or ""))
    )


def _is_financing_url(url: str) -> bool:
    """Return True when the URL is the financing landing path on the app host."""

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
        and bool(_FINANCING_PATH.match(parsed.path or ""))
    )


def _is_addons_url(url: str) -> bool:
    """Return True when the URL is the add-ons (Fordele) hub path on the app host."""

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
        and bool(_ADDONS_PATH.match(parsed.path or ""))
    )


def _is_integrations_url(url: str) -> bool:
    """Return True when the URL is the integrations soft-empty path on the app host."""

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
        and bool(_INTEGRATIONS_PATH.match(parsed.path or ""))
    )


def _is_daybooks_editor_url(url: str) -> bool:
    """Return True when the URL is the daybook editor open path on the app host."""

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
        and bool(_DAYBOOKS_EDITOR_PATH.match(parsed.path or ""))
    )


def _is_daybooks_bare_url(url: str) -> bool:
    """Return True when the URL is bare /daybooks (research117 Upsedasse shell)."""

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
        and bool(_DAYBOOKS_BARE_PATH.match(parsed.path or ""))
    )


def _is_transactions_list_url(url: str) -> bool:
    """Return True when the URL is the Posteringer list path (not create shell)."""

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
        and bool(_TRANSACTIONS_LIST_PATH.match(parsed.path or ""))
    )


def _is_reports_hub_url(url: str) -> bool:
    """Return True when the URL is the Rapporter hub (reports-all, optional tab)."""

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
        and bool(_REPORTS_HUB_PATH.match(parsed.path or ""))
    )


def _is_vat_declarations_list_url(url: str) -> bool:
    """Return True when the URL is the Momsangivelser list path (soft aliases reject)."""

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
        and bool(_VAT_DECLARATIONS_LIST_PATH.match(parsed.path or ""))
    )


def _is_exports_hub_url(url: str) -> bool:
    """Return True when the URL is the Eksportér data hub path (soft aliases reject)."""

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
        and bool(_EXPORTS_HUB_PATH.match(parsed.path or ""))
    )


def _absolute_billy_app_url(href: str) -> str | None:
    """Normalize a harvested relative or absolute mit.billy.dk href; never leak raw ids."""

    href = (href or "").strip()
    if not href or href.startswith("#") or href.startswith("mailto:"):
        return None
    if href.startswith("/"):
        return f"https://mit.billy.dk{href}"
    try:
        parsed = urlsplit(href)
    except ValueError:
        return None
    if parsed.scheme == "https" and (parsed.hostname or "").lower() == "mit.billy.dk":
        return href
    return None


async def _harvest_afstemning_reconciliation_url(page: LoginPage, org_slug: str) -> str | None:
    """Harvest the Afstemning nav href; never invent account ids."""

    del org_slug  # slug only used by callers for pre-navigation; harvest must not invent ids
    for selector in _AFSTEMNING_HREF_SELECTORS:
        try:
            control = page.locator(selector)
            if await control.count() < 1:
                continue
            href = await control.get_attribute("href")
            absolute = _absolute_billy_app_url(href or "")
            if absolute is not None and _is_bank_reconciliation_url(absolute):
                return absolute
        except Exception:
            continue
    return None


async def _read_optional_heading(page: LoginPage) -> str:
    """Return stripped h1 text when present; empty string for empty content shells."""

    try:
        heading = page.locator("h1")
        if await heading.count() < 1:
            return ""
        text = (await heading.inner_text()).strip()
        # Never return multi-line PII dumps; keep short heading class only.
        text = re.sub(r"\s+", " ", text)
        if len(text) > 80:
            return text[:80]
        return text
    except Exception:
        return ""


async def _is_empty_content_shell(page: LoginPage, heading: str) -> bool:
    """True when no h1 and no table/grid (research115 test-org empty Afstemning shell)."""

    if heading.strip():
        return False
    try:
        table_count = await page.locator("table").count()
        grid_count = await page.locator("[role=grid], [role=table]").count()
        return table_count == 0 and grid_count == 0
    except Exception:
        return False


async def _has_afstemning_nav_visible(page: LoginPage) -> bool:
    """True when the Afstemning nav label is visible on the shell."""

    try:
        control = page.locator(f"text={_AFSTEMNING_NAV_LABEL}")
        return await control.count() >= 1 and await control.is_visible()
    except Exception:
        return False


def _ui_bank_reconciliation_changed_error() -> ToolError:
    return ToolError(
        code=StableErrorCode.UI_CHANGED,
        message="Billy bank reconciliation shell could not be classified.",
    )


def _ui_financing_changed_error() -> ToolError:
    return ToolError(
        code=StableErrorCode.UI_CHANGED,
        message="Billy financing shell could not be classified.",
    )


def _ui_daybooks_changed_error() -> ToolError:
    return ToolError(
        code=StableErrorCode.UI_CHANGED,
        message="Billy daybooks shell could not be classified.",
    )


def _ui_transactions_changed_error() -> ToolError:
    """Fail closed when the transactions list shell no longer matches research118."""

    return ToolError(
        code=StableErrorCode.UI_CHANGED,
        message="Billy transactions list interface no longer matches the recorded signature.",
    )


def _ui_reports_changed_error() -> ToolError:
    """Fail closed when the reports hub shell no longer matches research119."""

    return ToolError(
        code=StableErrorCode.UI_CHANGED,
        message="Billy reports hub interface no longer matches the recorded signature.",
    )


def _ui_vat_declarations_changed_error() -> ToolError:
    """Fail closed when the VAT declarations shell no longer matches research120."""

    return ToolError(
        code=StableErrorCode.UI_CHANGED,
        message="Billy VAT declarations list interface no longer matches the recorded signature.",
    )


def _ui_exports_changed_error() -> ToolError:
    """Fail closed when the exports hub shell no longer matches research121."""

    return ToolError(
        code=StableErrorCode.UI_CHANGED,
        message="Billy exports hub interface no longer matches the recorded signature.",
    )


def _ui_saft_exports_changed_error() -> ToolError:
    """Fail closed when SAF-T CTA or exports hub no longer matches research122."""

    return ToolError(
        code=StableErrorCode.UI_CHANGED,
        message="Billy SAF-T exports interface no longer matches the recorded signature.",
    )


def _ui_addons_changed_error() -> ToolError:
    """Fail closed when Fordele (add-ons) hub no longer matches research123."""

    return ToolError(
        code=StableErrorCode.UI_CHANGED,
        message="Billy add-ons interface no longer matches the recorded signature.",
    )


def _ui_integrations_changed_error() -> ToolError:
    """Fail closed when integrations soft-empty shell no longer matches research124."""

    return ToolError(
        code=StableErrorCode.UI_CHANGED,
        message="Billy integrations interface no longer matches the recorded signature.",
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


async def _has_suppliers_list_signature(page: LoginPage) -> bool:
    """Verify the research109 suppliers list heading and create CTA without clicking."""

    try:
        heading = page.locator("h1")
        if await heading.count() < 1 or not await heading.is_visible():
            return False
        if (await heading.inner_text()).strip() != _SUPPLIERS_LIST_HEADING:
            return False
        create_action = page.locator(f"text={_SUPPLIERS_CREATE_CTA}")
        return await create_action.count() >= 1 and await create_action.is_visible()
    except Exception:
        return False


async def _has_bills_list_signature(page: LoginPage) -> bool:
    """Verify the research110 bills list heading and create CTA without clicking.

    Bills shell can render more than one h1; use the first visible heading text.
    """

    try:
        heading = page.locator("h1")
        if await heading.count() < 1:
            return False
        first = heading.first
        if not await first.is_visible():
            return False
        if (await first.inner_text()).strip() != _BILLS_LIST_HEADING:
            return False
        create_action = page.locator(f"text={_BILLS_CREATE_CTA}")
        if await create_action.count() < 1:
            return False
        return await create_action.first.is_visible()
    except Exception:
        return False


async def _has_transactions_list_signature(page: LoginPage) -> bool:
    """Verify the research118 Posteringer list heading and create CTA without clicking."""

    try:
        heading = page.locator("h1")
        if await heading.count() < 1:
            return False
        first = heading.first
        if not await first.is_visible():
            return False
        if (await first.inner_text()).strip() != _TRANSACTIONS_LIST_HEADING:
            return False
        create_action = page.locator(f"text={_TRANSACTIONS_CREATE_CTA}")
        if await create_action.count() < 1:
            return False
        return await create_action.first.is_visible()
    except Exception:
        return False


async def _has_reports_hub_signature(page: LoginPage) -> bool:
    """Verify research119 Rapporter hub heading and tab markers without export clicks."""

    try:
        heading = page.locator("h1")
        if await heading.count() < 1:
            return False
        first = heading.first
        if not await first.is_visible():
            return False
        if (await first.inner_text()).strip() != _REPORTS_HUB_HEADING:
            return False
        for label in _REPORTS_TAB_MARKERS:
            control = page.locator(f"text={label}")
            if await control.count() < 1:
                return False
            if not await control.first.is_visible():
                return False
        return True
    except Exception:
        return False


async def _has_reports_export_cta_visible(page: LoginPage) -> bool:
    """Observe-only: true when the Eksport control is present (never click)."""

    try:
        control = page.locator(f"text={_REPORTS_EXPORT_CTA}")
        if await control.count() < 1:
            return False
        return await control.first.is_visible()
    except Exception:
        return False


async def _has_vat_declarations_list_signature(page: LoginPage) -> bool:
    """Verify research120 Momsangivelser heading and Periode chrome without write clicks."""

    try:
        heading = page.locator("h1")
        if await heading.count() < 1:
            return False
        first = heading.first
        if not await first.is_visible():
            return False
        if (await first.inner_text()).strip() != _VAT_DECLARATIONS_LIST_HEADING:
            return False
        period = page.locator(f"text={_VAT_DECLARATIONS_PERIOD_MARKER}")
        if await period.count() < 1:
            return False
        return await period.first.is_visible()
    except Exception:
        return False


async def _has_vat_declarations_period_visible(page: LoginPage) -> bool:
    """Observe-only: true when Periode chrome is present (empty table body is valid)."""

    try:
        period = page.locator(f"text={_VAT_DECLARATIONS_PERIOD_MARKER}")
        if await period.count() < 1:
            return False
        return await period.first.is_visible()
    except Exception:
        return False


async def _has_exports_hub_signature(page: LoginPage) -> bool:
    """Verify research121 Eksportér data heading and export hub chrome without clicks."""

    try:
        heading = page.locator("h1")
        if await heading.count() < 1:
            return False
        first = heading.first
        if not await first.is_visible():
            return False
        if (await first.inner_text()).strip() != _EXPORTS_HUB_HEADING:
            return False
        for label in _EXPORTS_HUB_CHROME_MARKERS:
            control = page.locator(f"text={label}")
            if await control.count() < 1:
                continue
            if await control.first.is_visible():
                return True
        return False
    except Exception:
        return False


async def _has_exports_saft_cta_visible(page: LoginPage) -> bool:
    """Observe-only: true when Eksportér som SAF-T is present (never click)."""

    try:
        control = page.locator(f"text={_EXPORTS_SAFT_CTA}")
        if await control.count() < 1:
            return False
        return await control.first.is_visible()
    except Exception:
        return False


async def _has_debtor_balances_list_signature(page: LoginPage) -> bool:
    """Verify the research111 debtor balances heading and create CTA without clicking.

    Use the first visible h1 (multi-h1 shells possible, same lesson as bills).
    """

    try:
        heading = page.locator("h1")
        if await heading.count() < 1:
            return False
        first = heading.first
        if not await first.is_visible():
            return False
        if (await first.inner_text()).strip() != _DEBTOR_BALANCES_LIST_HEADING:
            return False
        create_action = page.locator(f"text={_DEBTOR_BALANCES_CREATE_CTA}")
        if await create_action.count() < 1:
            return False
        return await create_action.first.is_visible()
    except Exception:
        return False


async def _has_creditor_balances_list_signature(page: LoginPage) -> bool:
    """Verify the research112 creditor balances heading and create CTA without clicking.

    Use the first visible h1 (multi-h1 shells possible, same lesson as bills).
    """

    try:
        heading = page.locator("h1")
        if await heading.count() < 1:
            return False
        first = heading.first
        if not await first.is_visible():
            return False
        if (await first.inner_text()).strip() != _CREDITOR_BALANCES_LIST_HEADING:
            return False
        create_action = page.locator(f"text={_CREDITOR_BALANCES_CREATE_CTA}")
        if await create_action.count() < 1:
            return False
        return await create_action.first.is_visible()
    except Exception:
        return False


async def _has_uploads_list_signature(page: LoginPage) -> bool:
    """Verify the research113 uploads (Bilag) heading and Upload filer CTA without clicking.

    Use the first visible h1 (multi-h1 shells possible). Never set file inputs.
    """

    try:
        heading = page.locator("h1")
        if await heading.count() < 1:
            return False
        first = heading.first
        if not await first.is_visible():
            return False
        if (await first.inner_text()).strip() != _UPLOADS_LIST_HEADING:
            return False
        upload_action = page.locator(f"text={_UPLOADS_UPLOAD_CTA}")
        if await upload_action.count() < 1:
            return False
        return await upload_action.first.is_visible()
    except Exception:
        return False


async def _has_receipt_inbox_list_signature(page: LoginPage) -> bool:
    """Verify research114 receipt inbox heading Bilagsindbakke without write actions.

    Never set file inputs; never click Ret. Distinct from uploads/Bilag.
    """

    try:
        heading = page.locator("h1")
        if await heading.count() < 1:
            return False
        first = heading.first
        if not await first.is_visible():
            return False
        return (await first.inner_text()).strip() == _RECEIPT_INBOX_LIST_HEADING
    except Exception:
        return False


async def _has_financing_signature(page: LoginPage) -> bool:
    """Verify research116 financing heading without apply/submit actions.

    Never click Få et uforpligtende tilbud / Ansøg / Fortsæt / Send ansøgning.
    Distinct from bank-accounts and Afstemning shells.
    """

    try:
        heading = page.locator("h1")
        if await heading.count() < 1:
            return False
        first = heading.first
        if not await first.is_visible():
            return False
        return (await first.inner_text()).strip() == _FINANCING_HEADING
    except Exception:
        return False


async def _has_addons_signature(page: LoginPage) -> bool:
    """Verify research123 Fordele (add-ons) hub heading without partner CTA clicks.

    Never click Opret adgangsnøgle / Tilføj som betalingsmetode / Aktivér
    rykkerservice / Kom i gang / Ansøg om lån / Læs mere / Se alle vores
    integrationer / Install / Connect. Soft aliases (addons, integrations) are
    not success paths for this tool.
    """

    try:
        heading = page.locator("h1")
        if await heading.count() < 1:
            return False
        first = heading.first
        if not await first.is_visible():
            return False
        return (await first.inner_text()).strip() == _ADDONS_HEADING
    except Exception:
        return False


async def _has_integrations_soft_empty_signature(page: LoginPage) -> bool:
    """Verify research124 soft-empty integrations chrome without partner CTAs.

    Success requires empty/absent content h1 (not Fordele, not marketplace title),
    authenticated app chrome, and no error shell. Never click Se alle vores
    integrationer / Install / Connect. Soft aliases and Fordele are not success.
    """

    try:
        heading = page.locator("h1")
        if await heading.count() >= 1:
            first = heading.first
            if await first.is_visible():
                text = (await first.inner_text()).strip()
                if text:
                    # Any non-empty content h1 is not the soft-empty freeze.
                    return False
        return await _has_shell_nav_markers(page)
    except Exception:
        return False


async def _has_financing_apply_cta_observed(page: LoginPage) -> bool:
    """True when marketing apply CTA or financing nav label is present (observe only)."""

    try:
        for label in (_FINANCING_APPLY_CTA, _FINANCING_NAV_LABEL):
            control = page.locator(f"text={label}")
            if await control.count() >= 1 and await control.first.is_visible():
                return True
        return False
    except Exception:
        return False


async def _has_daybooks_editor_signature(page: LoginPage) -> bool:
    """Verify research117 daybook editor chrome without create/add-line actions.

    Never click Opret ny kassekladde / Tilføj kassekladdelinje / Bogfør / Ny postering.
    Requires all three dual-stable markers. Empty h1 is allowed.
    Distinct from bare /daybooks Upsedasse and transactions Posteringer.
    """

    try:
        for label in _DAYBOOKS_EDITOR_MARKERS:
            control = page.locator(f"text={label}")
            if await control.count() < 1:
                return False
            if not await control.first.is_visible():
                return False
        return True
    except Exception:
        return False


async def _has_file_input_present(page: LoginPage) -> bool:
    """Report whether any file input is present without setting or activating it."""

    try:
        return await page.locator("input[type=file]").count() >= 1
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


def _ui_suppliers_changed_error() -> ToolError:
    """Fail closed when the suppliers list shell no longer matches research109."""

    return ToolError(
        code=StableErrorCode.UI_CHANGED,
        message="Billy suppliers list interface no longer matches the recorded signature.",
    )


def _ui_bills_changed_error() -> ToolError:
    """Fail closed when the bills list shell no longer matches research110."""

    return ToolError(
        code=StableErrorCode.UI_CHANGED,
        message="Billy bills list interface no longer matches the recorded signature.",
    )


def _ui_debtor_balances_changed_error() -> ToolError:
    """Fail closed when the debtor balances list shell no longer matches research111."""

    return ToolError(
        code=StableErrorCode.UI_CHANGED,
        message="Billy debtor balances list interface no longer matches the recorded signature.",
    )


def _ui_creditor_balances_changed_error() -> ToolError:
    """Fail closed when the creditor balances list shell no longer matches research112."""

    return ToolError(
        code=StableErrorCode.UI_CHANGED,
        message="Billy creditor balances list interface no longer matches the recorded signature.",
    )


def _ui_uploads_changed_error() -> ToolError:
    """Fail closed when the uploads list shell no longer matches research113."""

    return ToolError(
        code=StableErrorCode.UI_CHANGED,
        message="Billy uploads list interface no longer matches the recorded signature.",
    )


def _ui_receipt_inbox_changed_error() -> ToolError:
    """Fail closed when the receipt inbox list shell no longer matches research114."""

    return ToolError(
        code=StableErrorCode.UI_CHANGED,
        message="Billy receipt inbox list interface no longer matches the recorded signature.",
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
