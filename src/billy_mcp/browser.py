"""Headless-only persistent Playwright runtime with deny-by-default egress."""

from __future__ import annotations

import asyncio
import json
import re
from collections.abc import Awaitable, Callable, Iterable, Mapping
from pathlib import Path
from typing import Any, Literal, Protocol, cast
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
    UiBillsCreateOpenSuccess,
    UiBillsDeleteOpenSuccess,
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
_INVOICES_CREATE_PATH = re.compile(r"^/[^/]+/invoices/new$")
_INVOICES_CREATE_HEADING = "Opret faktura"
_INVOICES_CREATE_DRAFT_SAVE_CHROME = "Gem som kladde"
_INVOICES_CREATE_LINE_CHROME_MARKERS = ("Tilføj linje", "Beskrivelse")
_INVOICES_EDIT_PATH = re.compile(r"^/[^/]+/invoices/(?!new$)[^/]+/edit$")
_INVOICES_GET_LINE_CHROME_MARKERS = ("Tilføj linje", "Beskrivelse", "Antal", "Pris")
# Research174: update form freeze — stronger than get detail_open_only.
_INVOICES_UPDATE_SAVE_MARKERS = ("Gem som kladde", "Godkend og send", "Godkend")
_INVOICES_UPDATE_FIELD_MARKERS = (
    "Fakturanr",
    "Betalingsfrist",
    "Valuta",
    "Priser er",
    "Design",
)
_PRODUCTS_LIST_PATH = re.compile(r"^/[^/]+/products$")
_PRODUCTS_LIST_HEADING = "Produkter"
_PRODUCTS_SEARCH_CONTROL = "[data-cy='search-button']"
_CLIENTS_LIST_PATH = re.compile(r"^/[^/]+/clients$")
_CLIENTS_DETAIL_PATH = re.compile(
    r"^/[^/]+/contacts/([^/]+)/(customer|supplier)$",
    re.I,
)
_CLIENTS_LIST_HEADING = "Kunder"
_CLIENTS_CREATE_CTA = "Opret kontakt"
_CLIENTS_HEADER_ROW_RE = re.compile(
    r"^(navn|e-?mail|telefon|land|oprettet|name|email|phone|country|created)"
    r"(\s|$)",
    re.I,
)
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
_BILLS_CREATE_PATH = re.compile(r"^/[^/]+/bills/new$")
_BILLS_CREATE_HEADING = "Opret køb"
_BILLS_CREATE_DRAFT_SAVE_CHROME = "Gem som kladde"
_BILLS_CREATE_LINE_CHROME_MARKERS = ("Tilføj linje", "Beskrivelse", "Linje")
# Research170: bill detail/get path class /:org_slug/bills/:id (not /new, not bare list).
_BILLS_DETAIL_PATH = re.compile(r"^/[^/]+/bills/(?!new$)[^/]+$")
_BILLS_EDIT_PATH = re.compile(r"^/[^/]+/bills/(?!new$)[^/]+/edit$")
_BILLS_GET_STATE_MARKERS = ("Kladde", "Godkendt", "Annulleret", "Draft")
_BILLS_GET_SUPPLIER_MARKERS = ("Leverandør", "Køb fra", "Ret køb", "Supplier")
_BILLS_GET_AMOUNT_MARKERS = ("Restbeløb", "Beløb", "Beskrivelse", "Linje", "Amount")
_BILLS_UPDATE_RET_MARKERS = ("Ret regning", "Ret køb", "Ret kob")
_BILLS_UPDATE_FIELD_MARKERS = ("Leverandør", "Leverandor", "Bilagsdato", "Forfaldsdato")
_BILLS_UPDATE_ACTION_MARKERS = ("Opdater",)
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
# Research125: Lagermodul inventory open shell (not products list).
# Never click Opret primo / Opret produkt / Opret status.
_INVENTORY_PATH = re.compile(r"^/[^/]+/inventory$")
_INVENTORY_HEADING = "Lagermodul"
_INVENTORY_CREATE_CTAS = ("Opret primo", "Opret produkt", "Opret status")
_PRODUCTS_CREATE_CTA = "Opret produkt"
# Research126: Indstillinger company (Virksomhed) open shell.
# Never click Gem ændringer / Tilføj ejer / upload / Opret* / Opgrader.
_SETTINGS_COMPANY_PATH = re.compile(r"^/[^/]+/settings$")
_SETTINGS_COMPANY_HEADING = "Indstillinger"
_SETTINGS_COMPANY_PANEL_MARKERS = ("Navn og adresse", "Kontaktinformation")
_SETTINGS_COMPANY_WRITE_CTAS = (
    "Gem ændringer",
    "Tilføj ejer",
    "Opret adgangsnøgle",
    "Opret betalingsmetode",
)
# Research127: Indstillinger accounting (Regnskab) panel on same hub path.
# Open via settings/accounting SPA seed (rewrites to bare /settings).
# Never click Gem / Sæt låsedato / Opret* / Tilføj* / Upload / Opgrader.
_SETTINGS_ACCOUNTING_PATH = _SETTINGS_COMPANY_PATH
_SETTINGS_ACCOUNTING_HEADING = "Indstillinger"
_SETTINGS_ACCOUNTING_PANEL_MARKERS = ("Regnskab", "Køb", "Kontoplan")
# Research128: Indstillinger invoicing (Faktura) panel on same hub path.
# Open via settings/invoicing SPA seed (rewrites to bare /settings).
# Never click Gem / Opret* / Tilføj* / Upload / Opgrader / Opret betalingsmetode.
_SETTINGS_INVOICING_PATH = _SETTINGS_COMPANY_PATH
_SETTINGS_INVOICING_HEADING = "Indstillinger"
_SETTINGS_INVOICING_REQUIRED_MARKERS = ("Faktura", "Produkter")
_SETTINGS_INVOICING_OPTIONAL_MARKERS = ("Betalingsmetoder", "Standard fakturalogo")
# Research129: Indstillinger user (Profil) panel on same hub path.
# Soft seeds insufficient; open hub then observe-only click side label Profil.
# Never click Gem / Upload / password submit / Opret* / Tilføj* / Opgrader.
_SETTINGS_USER_PATH = _SETTINGS_COMPANY_PATH
_SETTINGS_USER_HEADING = "Indstillinger"
_SETTINGS_USER_SIDE_NAV_LABEL = "Profil"
_SETTINGS_USER_PANEL_MARKERS = (
    "Profil",
    "Billede",
    "Sprog og tema",
    "Skift adgangskode",
)
_SETTINGS_USER_WRITE_CTA_LABELS = frozenset(
    {
        "Gem ændringer",
        "Gem",
        "Save",
        "Upload",
        "Opret",
        "Tilføj",
        "Slet",
        "Opgrader",
        "Inviter",
        "Invite",
        "Opret adgangsnøgle",
        "Opret betalingsmetode",
        "Tilføj ejer",
    }
)
# Research152: Indstillinger user organizations (Virksomheder) multi-org panel.
# Soft seeds insufficient; open hub then observe-only click Profil then Virksomheder.
# Never click Opret organisation / Gem / Upload / Slet / Tilføj.
_SETTINGS_USER_ORGANIZATIONS_PATH = _SETTINGS_COMPANY_PATH
_SETTINGS_USER_ORGANIZATIONS_HEADING = "Indstillinger"
_SETTINGS_USER_ORGANIZATIONS_SIDE_NAV_LABEL = "Virksomheder"
_SETTINGS_USER_ORGANIZATIONS_PANEL_MARKERS = (
    "Virksomheder",
    "Alle organisationer",
    "Opret organisation",
)
_SETTINGS_USER_ORGANIZATIONS_WRITE_CTA_LABELS = _SETTINGS_USER_WRITE_CTA_LABELS | frozenset(
    {
        "Opret organisation",
        "Opret virksomhed",
    }
)
# Research130: Indstillinger VAT (Momssatser) panel on same hub path.
# Soft seeds insufficient; open hub then observe-only click side label Momssatser.
# Never click Opret* / Gem* / Tilføj* / Upload / Opgrader.
_SETTINGS_VAT_PATH = _SETTINGS_COMPANY_PATH
_SETTINGS_VAT_HEADING = "Indstillinger"
_SETTINGS_VAT_SIDE_NAV_LABEL = "Momssatser"
_SETTINGS_VAT_PANEL_MARKERS = (
    "Regelsæt",
    "Satser for salg",
    "Satser for køb",
)
_SETTINGS_VAT_WRITE_CTA_LABELS = _SETTINGS_USER_WRITE_CTA_LABELS | frozenset(
    {
        "Opret regelsæt",
        "Opret sats",
    }
)
# Research131: Indstillinger org users (Brugere) panel on same hub path.
# Soft seeds insufficient; open hub then observe-only click side label Brugere.
# Never click Invitér* / Overdrag* / Find en bogholder* / Gem* / Opret*.
_SETTINGS_USERS_PATH = _SETTINGS_COMPANY_PATH
_SETTINGS_USERS_HEADING = "Indstillinger"
_SETTINGS_USERS_SIDE_NAV_LABEL = "Brugere"
_SETTINGS_USERS_PANEL_MARKERS = (
    "Brugere",
    "Revisorer og bogholdere",
)
_SETTINGS_USERS_WRITE_CTA_LABELS = _SETTINGS_USER_WRITE_CTA_LABELS | frozenset(
    {
        "Invitér",
        "Invitér bruger",
        "Invitér revisor",
        "Overdrag ejerskab",
        "Find en bogholder eller revisor",
    }
)
# Research132: Indstillinger access keys (Adgangsnøgler) panel on same hub path.
# Soft seeds insufficient; open hub then observe-only click side label Adgangsnøgler.
# Never click Opret adgangsnøgle / Opret* / Gem* / Slet.
_SETTINGS_ACCESS_TOKEN_PATH = _SETTINGS_COMPANY_PATH
_SETTINGS_ACCESS_TOKEN_HEADING = "Indstillinger"
_SETTINGS_ACCESS_TOKEN_SIDE_NAV_LABEL = "Adgangsnøgler"
_SETTINGS_ACCESS_TOKEN_PANEL_MARKERS = ("Adgangsnøgler",)
_SETTINGS_ACCESS_TOKEN_WRITE_CTA_LABELS = _SETTINGS_USER_WRITE_CTA_LABELS | frozenset(
    {
        "Opret adgangsnøgle",
    }
)
# Research133: Indstillinger betas (Betas / Tidlig adgang) panel on same hub path.
# Soft seeds mostly empty; open hub then observe-only click side label Betas.
# Never click Opret* / Gem* / Tilføj* / Upload / Opgrader*.
_SETTINGS_BETA_PATH = _SETTINGS_COMPANY_PATH
_SETTINGS_BETA_HEADING = "Indstillinger"
_SETTINGS_BETA_SIDE_NAV_LABEL = "Betas"
_SETTINGS_BETA_PANEL_MARKERS = (
    "Betas",
    "Tidlig adgang",
)
_SETTINGS_BETA_WRITE_CTA_LABELS = _SETTINGS_USER_WRITE_CTA_LABELS
# Research134: Indstillinger Abonnement empty panel on same hub path.
# Soft seeds mostly empty; open hub then observe-only click side label Abonnement.
# Success = empty h2 panel (not company/beta/other). Never click billing/write CTAs.
_SETTINGS_SUBSCRIPTION_PATH = _SETTINGS_COMPANY_PATH
_SETTINGS_SUBSCRIPTION_HEADING = "Indstillinger"
_SETTINGS_SUBSCRIPTION_SIDE_NAV_LABEL = "Abonnement"
# Panel-only content markers that mean the active panel is NOT empty Abonnement.
# Side-rail labels alone (Profil, Virksomhed, Betas, Adgangsnøgler, …) must not
# trip this set.
_SETTINGS_SUBSCRIPTION_NONEMPTY_PANEL_MARKERS = (
    "Navn og adresse",
    "Kontaktinformation",
    "Virksomhedsikon",
    "Ejere",
    "Tidlig adgang",
    "Regelsæt",
    "Satser for salg",
    "Satser for køb",
    "Revisorer og bogholdere",
    "Billede",
    "Sprog og tema",
    "Skift adgangskode",
    "Produkter",
    "Betalingsmetoder",
    "Standard fakturalogo",
    "Kontoplan",
    "Opret adgangsnøgle",
)
_SETTINGS_SUBSCRIPTION_WRITE_CTA_LABELS = _SETTINGS_USER_WRITE_CTA_LABELS | frozenset(
    {
        "Opgrader",
        "Skift abonnement",
        "Skift plan",
        "Betal",
        "Køb",
        "Annuller",
        "Opsig",
        "Opret adgangsnøgle",
        "Opret betalingsmetode",
    }
)
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
_DAYBOOKS_GET_PATH = re.compile(r"^/[^/]+/daybooks/(?!new$)[^/]+$")
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

    def nth(self, index: int) -> LoginControl:
        """Playwright nth-match seam for multi-match locators."""
        ...

    async def count(self) -> int: ...

    async def is_visible(self) -> bool: ...

    async def inner_text(self) -> str: ...

    async def fill(self, value: str) -> None: ...

    async def check(self) -> None: ...

    async def click(self, **kwargs: object) -> None: ...

    async def set_input_files(self, path: str | Path) -> None: ...

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


class UiInvoicesCreateOpenService(Protocol):
    """Injectable seam for the read-only invoice create form open observation."""

    async def ui_invoices_create_open(self) -> UiInvoicesCreateOpenSuccess | ToolError: ...


class UiInvoicesGetOpenService(Protocol):
    """Injectable seam for the read-only invoices detail get-open observation."""

    async def ui_invoices_get_open(self) -> UiInvoicesGetOpenSuccess | ToolError: ...


class UiInvoicesUpdateOpenService(Protocol):
    """Injectable seam for the read-only invoices edit form open observation."""

    async def ui_invoices_update_open(self) -> UiInvoicesUpdateOpenSuccess | ToolError: ...


class UiInvoicesDeleteOpenService(Protocol):
    """Injectable seam for the read-only invoices delete chrome (Mere) observation."""

    async def ui_invoices_delete_open(self) -> UiInvoicesDeleteOpenSuccess | ToolError: ...


class UiBillsGetOpenService(Protocol):
    """Injectable seam for the read-only bills detail get-open observation."""

    async def ui_bills_get_open(self) -> UiBillsGetOpenSuccess | ToolError: ...


class UiBillsUpdateOpenService(Protocol):
    """Injectable seam for the read-only bills edit form open observation."""

    async def ui_bills_update_open(self) -> UiBillsUpdateOpenSuccess | ToolError: ...


class UiBillsDeleteOpenService(Protocol):
    """Injectable seam for the read-only bills delete chrome open observation."""

    async def ui_bills_delete_open(self) -> UiBillsDeleteOpenSuccess | ToolError: ...


class UiProductsListService(Protocol):
    """Injectable seam for the read-only products list shell observation."""

    async def ui_products_list(self) -> UiProductsListSuccess | ToolError: ...


class UiClientsListService(Protocol):
    """Injectable seam for the read-only clients list shell observation."""

    async def ui_clients_list(self) -> UiClientsListSuccess | ToolError: ...


class UiClientsCreateOpenService(Protocol):
    """Injectable seam for the read-only clients create form open observation."""

    async def ui_clients_create_open(self) -> UiClientsCreateOpenSuccess | ToolError: ...


class UiClientsGetOpenService(Protocol):
    """Injectable seam for the read-only clients detail get-open observation."""

    async def ui_clients_get_open(self) -> UiClientsGetOpenSuccess | ToolError: ...


class UiClientsUpdateOpenService(Protocol):
    """Injectable seam for the read-only clients update (Ret) form open observation."""

    async def ui_clients_update_open(self) -> UiClientsUpdateOpenSuccess | ToolError: ...


class UiClientsDeleteOpenService(Protocol):
    """Injectable seam for the read-only clients delete chrome (Mere) observation."""

    async def ui_clients_delete_open(self) -> UiClientsDeleteOpenSuccess | ToolError: ...


class UiSuppliersCreateOpenService(Protocol):
    """Injectable seam for the read-only suppliers create form open observation."""

    async def ui_suppliers_create_open(self) -> UiSuppliersCreateOpenSuccess | ToolError: ...


class UiProductsCreateOpenService(Protocol):
    """Injectable seam for the read-only products create form open observation."""

    async def ui_products_create_open(self) -> UiProductsCreateOpenSuccess | ToolError: ...


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


class UiBillsCreateOpenService(Protocol):
    """Injectable seam for the read-only bill create form open observation."""

    async def ui_bills_create_open(self) -> UiBillsCreateOpenSuccess | ToolError: ...


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


class UiDaybooksGetOpenService(Protocol):
    """Injectable seam for the read-only daybook detail get-open observation."""

    async def ui_daybooks_get_open(self) -> UiDaybooksGetOpenSuccess | ToolError: ...


class UiDaybooksDeleteOpenService(Protocol):
    """Injectable seam for the read-only daybook delete chrome open observation."""

    async def ui_daybooks_delete_open(self) -> UiDaybooksDeleteOpenSuccess | ToolError: ...


class UiDaybookTransactionsCreateOpenService(Protocol):
    """Bounded daybookTransactions create chrome open workflow."""

    async def ui_daybook_transactions_create_open(
        self,
    ) -> UiDaybookTransactionsCreateOpenSuccess | ToolError: ...


class UiTransactionsCreateOpenService(Protocol):
    """Bounded transactions.create chrome open workflow."""

    async def ui_transactions_create_open(
        self,
    ) -> UiTransactionsCreateOpenSuccess | ToolError: ...


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


class UiInventoryOpenService(Protocol):
    """Injectable seam for the read-only Lagermodul inventory shell open."""

    async def ui_inventory_open(self) -> UiInventoryOpenSuccess | ToolError: ...


class UiSettingsCompanyOpenService(Protocol):
    """Injectable seam for the read-only company settings shell open."""

    async def ui_settings_company_open(self) -> UiSettingsCompanyOpenSuccess | ToolError: ...


class UiSettingsAccountingOpenService(Protocol):
    """Injectable seam for the read-only accounting settings shell open."""

    async def ui_settings_accounting_open(
        self,
    ) -> UiSettingsAccountingOpenSuccess | ToolError: ...


class UiSettingsInvoicingOpenService(Protocol):
    """Injectable seam for the read-only invoicing settings shell open."""

    async def ui_settings_invoicing_open(
        self,
    ) -> UiSettingsInvoicingOpenSuccess | ToolError: ...


class UiSettingsUserOpenService(Protocol):
    """Injectable seam for the read-only user settings (Profil) shell open."""

    async def ui_settings_user_open(self) -> UiSettingsUserOpenSuccess | ToolError: ...


class UiSettingsUserOrganizationsOpenService(Protocol):
    """Injectable seam for the read-only user organizations (Virksomheder) shell open."""

    async def ui_settings_user_organizations_open(
        self,
    ) -> UiSettingsUserOrganizationsOpenSuccess | ToolError: ...


class UiSettingsVatOpenService(Protocol):
    """Injectable seam for the read-only VAT settings (Momssatser) shell open."""

    async def ui_settings_vat_open(self) -> UiSettingsVatOpenSuccess | ToolError: ...


class UiSettingsUsersOpenService(Protocol):
    """Injectable seam for the read-only org users settings (Brugere) shell open."""

    async def ui_settings_users_open(self) -> UiSettingsUsersOpenSuccess | ToolError: ...


class UiSettingsAccessTokenOpenService(Protocol):
    """Injectable seam for the read-only access-token settings (Adgangsnøgler) shell open."""

    async def ui_settings_access_token_open(
        self,
    ) -> UiSettingsAccessTokenOpenSuccess | ToolError: ...


class UiSettingsBetaOpenService(Protocol):
    """Injectable seam for the read-only betas settings (Betas) shell open."""

    async def ui_settings_beta_open(self) -> UiSettingsBetaOpenSuccess | ToolError: ...


class UiSettingsSubscriptionOpenService(Protocol):
    """Injectable seam for the read-only subscription settings (Abonnement) shell open."""

    async def ui_settings_subscription_open(
        self,
    ) -> UiSettingsSubscriptionOpenSuccess | ToolError: ...


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

    @property
    def profile_path(self) -> Path:
        """Resolved persistent profile directory. Never a repository path."""

        return self._profile_path

    def independent_readback_runtime(self) -> BrowserRuntime:
        """Return a second persistent profile that does not share this session."""

        return BrowserRuntime(
            self._profile_path.with_name(f"{self._profile_path.name}-readback"),
            egress_manifest_path=self._egress_manifest_path,
            credential_references=self._credential_references,
            credential_resolver=self._credential_resolver,
            org_identity_path=self._org_identity_path,
        )

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

    async def ui_invoices_create_open(self) -> UiInvoicesCreateOpenSuccess | ToolError:
        """Open the invoice create form shell for the current authenticated UI session only.

        Research153: navigate to /:org_slug/invoices/new (dual-proved real form).
        Form open only — never click Godkend / Godkend og send / Send / Gem som
        kladde / Vis preview / Tilføj linje / Vedhæft / Slet. Distinct from list
        shell and special POST /invoices/:id/emails.
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
                return _ui_invoices_create_changed_error()

            create_url = f"https://mit.billy.dk/{slug}/invoices/new"
            await page.goto(create_url, wait_until="domcontentloaded")
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
                    return _ui_invoices_create_changed_error()
                if _is_invoices_create_url(page.url) and await _has_invoices_create_signature(page):
                    return UiInvoicesCreateOpenSuccess(
                        draft_save_chrome_visible=True,
                        line_chrome_visible=True,
                        shell_markers_present=await _has_shell_nav_markers(page),
                    )
                await asyncio.sleep(0.2)
            return _ui_invoices_create_changed_error()
        except BrowserEgressPolicyLoadError:
            return ToolError(
                code=StableErrorCode.EGRESS_DENIED,
                message="Browser egress policy prevented the invoices create form observation.",
            )
        except Exception:
            return ToolError(
                code=StableErrorCode.BILLY_ERROR,
                message="Browser invoices create form observation could not be completed.",
            )
        finally:
            if page is not None:
                try:
                    await page.close()
                except Exception:
                    pass

    async def ui_invoices_get_open(self) -> UiInvoicesGetOpenSuccess | ToolError:
        """Open an invoice detail/edit surface for the authenticated UI session only.

        Research169: path-scoped invoices GET/POST/DELETE unlocks list rows and
        disposable seed. Open first non-header invoice detail at path class
        /:org_slug/invoices/:id/edit. Never Gem/Send/Slet/submit. Distinct from
        list shell and create form_open. Soft /invoices/new is not success.
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
                return _ui_invoices_get_changed_error()

            invoices_url = f"https://mit.billy.dk/{slug}/invoices"
            await page.goto(invoices_url, wait_until="domcontentloaded")
            await _await_page_settle(page)

            for _ in range(50):
                if await _has_known_login_page(page):
                    return _auth_required_error()
                if await _has_interaction_challenge(page):
                    return ToolError(
                        code=StableErrorCode.AUTH_INTERACTION_REQUIRED,
                        message="Browser authentication requires a non-automatable challenge.",
                    )
                if await _has_error_shell_markers(page):
                    return _ui_invoices_get_changed_error()
                if _is_invoices_create_url(page.url):
                    return _ui_invoices_get_changed_error()

                if await _has_invoices_detail_signature(page, slug):
                    flags = await _invoices_detail_flags(page)
                    return UiInvoicesGetOpenSuccess(
                        detail_open=True,
                        entry_date_control_present=flags["entry_date_control_present"],
                        contact_control_present=flags["contact_control_present"],
                        line_chrome_present=flags["line_chrome_present"],
                        shell_markers_present=await _has_shell_nav_markers(page),
                    )

                if _is_invoices_list_url(page.url) and await _has_invoices_list_signature(page):
                    opened = await _click_invoices_detail_candidate(page, slug)
                    if opened:
                        await _await_page_settle(page)
                        continue
                await asyncio.sleep(0.25)
            return _ui_invoices_get_changed_error()
        except BrowserEgressPolicyLoadError:
            return ToolError(
                code=StableErrorCode.EGRESS_DENIED,
                message="Browser egress policy prevented the invoices detail observation.",
            )
        except Exception:
            return ToolError(
                code=StableErrorCode.BILLY_ERROR,
                message="Browser invoices detail observation could not be completed.",
            )
        finally:
            if page is not None:
                try:
                    await page.close()
                except Exception:
                    pass

    async def ui_invoices_delete_open(self) -> UiInvoicesDeleteOpenSuccess | ToolError:
        """Open invoice delete chrome for the authenticated UI session only.

        Research175: path-scoped invoices GET/POST/DELETE unlock list rows and
        disposable seed. Open first non-header invoice edit surface at path class
        /:org_slug/invoices/:id/edit. Assert primary Slet button absent; open Mere;
        classify exact Slet text (+ Duplikér). Never click Slet / confirm / Gem /
        Godkend og send / Send. Soft /invoices/new is not success. Distinct from
        get/update freezes on the same path class (clients-delete Mere pattern).
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
                return _ui_invoices_delete_changed_error()

            invoices_url = f"https://mit.billy.dk/{slug}/invoices"
            await page.goto(invoices_url, wait_until="domcontentloaded")
            await _await_page_settle(page)

            for _ in range(50):
                if await _has_known_login_page(page):
                    return _auth_required_error()
                if await _has_interaction_challenge(page):
                    return ToolError(
                        code=StableErrorCode.AUTH_INTERACTION_REQUIRED,
                        message="Browser authentication requires a non-automatable challenge.",
                    )
                if await _has_error_shell_markers(page):
                    return _ui_invoices_delete_changed_error()
                if _is_invoices_create_url(page.url):
                    return _ui_invoices_delete_changed_error()

                if await _has_invoices_delete_chrome_signature(page):
                    flags = await _invoices_delete_chrome_flags(page)
                    primary = await _invoices_delete_primary_flags(page)
                    return UiInvoicesDeleteOpenSuccess(
                        edit_open=True,
                        mere_open=flags["mere_open"],
                        slet_text_visible=flags["slet_text_visible"],
                        dupliker_visible=flags["dupliker_visible"],
                        primary_slet_absent=primary["primary_slet_absent"],
                        shell_markers_present=await _has_shell_nav_markers(page),
                    )

                if _is_invoices_edit_url(page.url):
                    primary = await _invoices_delete_primary_flags(page)
                    if not primary.get("primary_slet_absent"):
                        return _ui_invoices_delete_changed_error()
                    if not primary.get("mere_present"):
                        return _ui_invoices_delete_changed_error()
                    clicked_mere = await _click_invoices_mere_action(page)
                    if clicked_mere:
                        await _await_page_settle(page)
                        if await _has_invoices_delete_chrome_signature(page):
                            flags = await _invoices_delete_chrome_flags(page)
                            return UiInvoicesDeleteOpenSuccess(
                                edit_open=True,
                                mere_open=True,
                                slet_text_visible=flags["slet_text_visible"],
                                dupliker_visible=flags["dupliker_visible"],
                                primary_slet_absent=True,
                                shell_markers_present=await _has_shell_nav_markers(page),
                            )
                        continue
                    return _ui_invoices_delete_changed_error()

                if _is_invoices_list_url(page.url) and await _has_invoices_list_signature(page):
                    opened = await _click_invoices_detail_candidate(page, slug)
                    if opened:
                        await _await_page_settle(page)
                        continue
                await asyncio.sleep(0.25)
            return _ui_invoices_delete_changed_error()
        except BrowserEgressPolicyLoadError:
            return ToolError(
                code=StableErrorCode.EGRESS_DENIED,
                message="Browser egress policy prevented the invoices delete chrome observation.",
            )
        except Exception:
            return ToolError(
                code=StableErrorCode.BILLY_ERROR,
                message="Browser invoices delete chrome observation could not be completed.",
            )
        finally:
            if page is not None:
                try:
                    await page.close()
                except Exception:
                    pass

    async def ui_invoices_update_open(self) -> UiInvoicesUpdateOpenSuccess | ToolError:
        """Open an invoice edit form for the authenticated UI session only.

        Research174: path-scoped invoices GET/POST/DELETE unlock list rows and
        disposable seed. Open first non-header invoice edit surface at path class
        /:org_slug/invoices/:id/edit. Assert form freeze (Gem som kladde family +
        Fakturanr/Dato/Betalingsfrist + inputs≥3). Never Gem/Gem som kladde/
        Godkend og send/Send/Slet/Mere→Slet submit. Soft /invoices/new is not
        success. Distinct from get detail_open_only on the same path class.
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
                return _ui_invoices_update_changed_error()

            invoices_url = f"https://mit.billy.dk/{slug}/invoices"
            await page.goto(invoices_url, wait_until="domcontentloaded")
            await _await_page_settle(page)

            for _ in range(50):
                if await _has_known_login_page(page):
                    return _auth_required_error()
                if await _has_interaction_challenge(page):
                    return ToolError(
                        code=StableErrorCode.AUTH_INTERACTION_REQUIRED,
                        message="Browser authentication requires a non-automatable challenge.",
                    )
                if await _has_error_shell_markers(page):
                    return _ui_invoices_update_changed_error()
                if _is_invoices_create_url(page.url):
                    return _ui_invoices_update_changed_error()

                if await _has_invoices_update_form_signature(page, slug):
                    flags = await _invoices_update_form_flags(page)
                    return UiInvoicesUpdateOpenSuccess(
                        form_open=True,
                        gem_kladde_or_save_chrome_present=flags[
                            "gem_kladde_or_save_chrome_present"
                        ],
                        date_or_payment_terms_chrome_present=flags[
                            "date_or_payment_terms_chrome_present"
                        ],
                        contact_or_customer_chrome_present=flags[
                            "contact_or_customer_chrome_present"
                        ],
                        inputs_present=flags["inputs_present"],
                        shell_markers_present=await _has_shell_nav_markers(page),
                    )

                if _is_invoices_list_url(page.url) and await _has_invoices_list_signature(page):
                    opened = await _click_invoices_detail_candidate(page, slug)
                    if opened:
                        await _await_page_settle(page)
                        continue
                await asyncio.sleep(0.25)
            return _ui_invoices_update_changed_error()
        except BrowserEgressPolicyLoadError:
            return ToolError(
                code=StableErrorCode.EGRESS_DENIED,
                message="Browser egress policy prevented the invoices update form observation.",
            )
        except Exception:
            return ToolError(
                code=StableErrorCode.BILLY_ERROR,
                message="Browser invoices update form observation could not be completed.",
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

    async def ui_clients_create_open(self) -> UiClientsCreateOpenSuccess | ToolError:
        """Open the clients create form dialog for the current authenticated UI session only.

        Research160: open /:org_slug/clients, click text CTA Opret kontakt, classify
        dialog form fields (name / registrationNo / address-or-person). Form open only
        — never Gem / Opret submit / Save / Create. Soft /clients/new is not success.
        Distinct from list shell ui_clients_list and special invoice email.
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
                return _ui_clients_create_changed_error()

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
                    return _ui_clients_create_changed_error()
                if _is_clients_new_soft_url(page.url):
                    return _ui_clients_create_changed_error()
                if not _is_clients_list_url(page.url):
                    await asyncio.sleep(0.2)
                    continue
                if not await _has_clients_list_heading(page):
                    await asyncio.sleep(0.2)
                    continue
                if not await _has_clients_create_form_signature(page):
                    clicked = await _click_clients_create_cta(page)
                    if not clicked:
                        await asyncio.sleep(0.2)
                        continue
                    await _await_page_settle(page)
                if _is_clients_new_soft_url(page.url):
                    return _ui_clients_create_changed_error()
                if _is_clients_list_url(page.url) and await _has_clients_create_form_signature(
                    page
                ):
                    signature = await _clients_create_form_field_flags(page)
                    return UiClientsCreateOpenSuccess(
                        create_dialog_open=True,
                        name_field_visible=signature["name_field_visible"],
                        registration_no_field_present=signature["registration_no_field_present"],
                        address_or_person_fields_present=signature[
                            "address_or_person_fields_present"
                        ],
                        shell_markers_present=await _has_shell_nav_markers(page),
                    )
                await asyncio.sleep(0.2)
            return _ui_clients_create_changed_error()
        except BrowserEgressPolicyLoadError:
            return ToolError(
                code=StableErrorCode.EGRESS_DENIED,
                message="Browser egress policy prevented the clients create form observation.",
            )
        except Exception:
            return ToolError(
                code=StableErrorCode.BILLY_ERROR,
                message="Browser clients create form observation could not be completed.",
            )
        finally:
            if page is not None:
                try:
                    await page.close()
                except Exception:
                    pass

    async def ui_clients_get_open(self) -> UiClientsGetOpenSuccess | ToolError:
        """Open a client (contact) detail surface for the authenticated UI session only.

        Research164: path-scoped contacts egress unlocks GET /v2/contacts so list rows
        can load. Open first non-header client detail (path /:org_slug/clients/:id or
        valued name on detail drawer). Never Gem/Slet/submit. Distinct from list shell
        and create form_open. Header-only dialogs are not success.
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
                return _ui_clients_get_changed_error()

            clients_url = f"https://mit.billy.dk/{slug}/clients"
            await page.goto(clients_url, wait_until="domcontentloaded")
            await _await_page_settle(page)

            for _ in range(40):
                if await _has_known_login_page(page):
                    return _auth_required_error()
                if await _has_interaction_challenge(page):
                    return ToolError(
                        code=StableErrorCode.AUTH_INTERACTION_REQUIRED,
                        message="Browser authentication requires a non-automatable challenge.",
                    )
                if await _has_error_shell_markers(page):
                    return _ui_clients_get_changed_error()
                if _is_clients_new_soft_url(page.url):
                    return _ui_clients_get_changed_error()

                if await _has_clients_detail_signature(page, slug):
                    flags = await _clients_detail_flags(page)
                    return UiClientsGetOpenSuccess(
                        detail_open=True,
                        contact_name_visible=flags["contact_name_visible"],
                        edit_action_visible=flags["edit_action_visible"],
                        detail_markers_present=True,
                        shell_markers_present=await _has_shell_nav_markers(page),
                    )

                if _is_clients_list_url(page.url) and await _has_clients_list_heading(page):
                    opened = await _click_clients_detail_candidate(page, slug)
                    if opened:
                        await _await_page_settle(page)
                        continue
                await asyncio.sleep(0.25)
            return _ui_clients_get_changed_error()
        except BrowserEgressPolicyLoadError:
            return ToolError(
                code=StableErrorCode.EGRESS_DENIED,
                message="Browser egress policy prevented the clients detail observation.",
            )
        except Exception:
            return ToolError(
                code=StableErrorCode.BILLY_ERROR,
                message="Browser clients detail observation could not be completed.",
            )
        finally:
            if page is not None:
                try:
                    await page.close()
                except Exception:
                    pass

    async def ui_clients_update_open(self) -> UiClientsUpdateOpenSuccess | ToolError:
        """Open a client edit form (Ret) for the authenticated UI session only.

        Research166: open /:org_slug/clients, open non-header contact detail
        (/contacts/:id/customer), click Ret, classify name-valued edit fields.
        Never Gem/Slet/Save submit. Distinct from get overview and create form.
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
                return _ui_clients_update_changed_error()

            clients_url = f"https://mit.billy.dk/{slug}/clients"
            await page.goto(clients_url, wait_until="domcontentloaded")
            await _await_page_settle(page)

            for _ in range(50):
                if await _has_known_login_page(page):
                    return _auth_required_error()
                if await _has_interaction_challenge(page):
                    return ToolError(
                        code=StableErrorCode.AUTH_INTERACTION_REQUIRED,
                        message="Browser authentication requires a non-automatable challenge.",
                    )
                if await _has_error_shell_markers(page):
                    return _ui_clients_update_changed_error()
                if _is_clients_new_soft_url(page.url):
                    return _ui_clients_update_changed_error()

                if await _has_clients_update_form_signature(page):
                    flags = await _clients_update_form_field_flags(page)
                    # Ret panel can collapse primary nav labels; shell_markers_present
                    # is the edit-ready aggregate (path + valued name + content floor).
                    return UiClientsUpdateOpenSuccess(
                        edit_form_open=True,
                        name_field_visible=flags["name_field_visible"],
                        name_field_has_value=flags["name_field_has_value"],
                        address_or_person_fields_present=flags["address_or_person_fields_present"],
                        country_field_present=flags["country_field_present"],
                        shell_markers_present=True,
                    )

                if _is_clients_detail_url(page.url) and await _has_clients_detail_signature(
                    page, slug
                ):
                    clicked_ret = await _click_clients_ret_action(page)
                    if clicked_ret:
                        await _await_page_settle(page)
                        continue
                    return _ui_clients_update_changed_error()

                if _is_clients_list_url(page.url) and await _has_clients_list_heading(page):
                    opened = await _click_clients_detail_candidate(page, slug)
                    if opened:
                        await _await_page_settle(page)
                        continue
                await asyncio.sleep(0.25)
            return _ui_clients_update_changed_error()
        except BrowserEgressPolicyLoadError:
            return ToolError(
                code=StableErrorCode.EGRESS_DENIED,
                message="Browser egress policy prevented the clients update form observation.",
            )
        except Exception:
            return ToolError(
                code=StableErrorCode.BILLY_ERROR,
                message="Browser clients update form observation could not be completed.",
            )
        finally:
            if page is not None:
                try:
                    await page.close()
                except Exception:
                    pass

    async def ui_clients_delete_open(self) -> UiClientsDeleteOpenSuccess | ToolError:
        """Open client delete chrome (Mere → Slet kontakt) for the authenticated UI session.

        Research167: open /:org_slug/clients, open non-header contact detail
        (/contacts/:id/customer), open Mere, classify Slet kontakt visibility.
        Never confirm Slet / permanent delete / Arkivér. Distinct from get/update/create.
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
                return _ui_clients_delete_changed_error()

            clients_url = f"https://mit.billy.dk/{slug}/clients"
            await page.goto(clients_url, wait_until="domcontentloaded")
            await _await_page_settle(page)

            for _ in range(50):
                if await _has_known_login_page(page):
                    return _auth_required_error()
                if await _has_interaction_challenge(page):
                    return ToolError(
                        code=StableErrorCode.AUTH_INTERACTION_REQUIRED,
                        message="Browser authentication requires a non-automatable challenge.",
                    )
                if await _has_error_shell_markers(page):
                    return _ui_clients_delete_changed_error()
                if _is_clients_new_soft_url(page.url):
                    return _ui_clients_delete_changed_error()

                if await _has_clients_delete_chrome_signature(page):
                    flags = await _clients_delete_chrome_flags(page)
                    return UiClientsDeleteOpenSuccess(
                        detail_open=True,
                        mere_open=flags["mere_open"],
                        slet_kontakt_visible=flags["slet_kontakt_visible"],
                        arkiver_kontakt_visible=flags["arkiver_kontakt_visible"],
                        primary_slet_absent=flags["primary_slet_absent"],
                        shell_markers_present=True,
                    )

                if _is_clients_detail_url(page.url) and await _has_clients_detail_signature(
                    page, slug
                ):
                    # Capture primary chrome before Mere (Slet should be absent).
                    pre = await _clients_delete_primary_flags(page)
                    clicked_mere = await _click_clients_mere_action(page)
                    if clicked_mere:
                        await _await_page_settle(page)
                        if await _has_clients_delete_chrome_signature(page):
                            flags = await _clients_delete_chrome_flags(page)
                            # Prefer pre-Mere primary observation for primary_slet_absent.
                            return UiClientsDeleteOpenSuccess(
                                detail_open=True,
                                mere_open=True,
                                slet_kontakt_visible=flags["slet_kontakt_visible"],
                                arkiver_kontakt_visible=flags["arkiver_kontakt_visible"],
                                primary_slet_absent=pre["primary_slet_absent"],
                                shell_markers_present=True,
                            )
                        continue
                    return _ui_clients_delete_changed_error()

                if _is_clients_list_url(page.url) and await _has_clients_list_heading(page):
                    opened = await _click_clients_detail_candidate(page, slug)
                    if opened:
                        await _await_page_settle(page)
                        continue
                await asyncio.sleep(0.25)
            return _ui_clients_delete_changed_error()
        except BrowserEgressPolicyLoadError:
            return ToolError(
                code=StableErrorCode.EGRESS_DENIED,
                message="Browser egress policy prevented the clients delete chrome observation.",
            )
        except Exception:
            return ToolError(
                code=StableErrorCode.BILLY_ERROR,
                message="Browser clients delete chrome observation could not be completed.",
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

    async def ui_suppliers_create_open(self) -> UiSuppliersCreateOpenSuccess | ToolError:
        """Open the suppliers create form dialog for the current authenticated UI session only.

        Research161: open /:org_slug/suppliers, click text CTA Opret kontakt, classify
        dialog form fields (name / registrationNo / address-or-person). Form open only
        — never Gem / Opret submit / Save / Create. Soft /suppliers/new is not success.
        Distinct from list shell ui_suppliers_list and clients create (contacts.create
        already dual-counted via clients).
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
                return _ui_suppliers_create_changed_error()

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
                    return _ui_suppliers_create_changed_error()
                if _is_suppliers_new_soft_url(page.url):
                    return _ui_suppliers_create_changed_error()
                if not _is_suppliers_list_url(page.url):
                    await asyncio.sleep(0.2)
                    continue
                if not await _has_suppliers_list_heading(page):
                    await asyncio.sleep(0.2)
                    continue
                if not await _has_suppliers_create_form_signature(page):
                    clicked = await _click_suppliers_create_cta(page)
                    if not clicked:
                        await asyncio.sleep(0.2)
                        continue
                    await _await_page_settle(page)
                if _is_suppliers_new_soft_url(page.url):
                    return _ui_suppliers_create_changed_error()
                if _is_suppliers_list_url(page.url) and await _has_suppliers_create_form_signature(
                    page
                ):
                    signature = await _suppliers_create_form_field_flags(page)
                    return UiSuppliersCreateOpenSuccess(
                        create_dialog_open=True,
                        name_field_visible=signature["name_field_visible"],
                        registration_no_field_present=signature["registration_no_field_present"],
                        address_or_person_fields_present=signature[
                            "address_or_person_fields_present"
                        ],
                        shell_markers_present=await _has_shell_nav_markers(page),
                    )
                await asyncio.sleep(0.2)
            return _ui_suppliers_create_changed_error()
        except BrowserEgressPolicyLoadError:
            return ToolError(
                code=StableErrorCode.EGRESS_DENIED,
                message="Browser egress policy prevented the suppliers create form observation.",
            )
        except Exception:
            return ToolError(
                code=StableErrorCode.BILLY_ERROR,
                message="Browser suppliers create form observation could not be completed.",
            )
        finally:
            if page is not None:
                try:
                    await page.close()
                except Exception:
                    pass

    async def ui_products_create_open(self) -> UiProductsCreateOpenSuccess | ToolError:
        """Open the products create form for the current authenticated UI session only.

        Research163: open /:org_slug/inventory, click Opret produkt, classify form fields
        (name / account / salesTaxRuleset / unitPrice). Form open only — never Gem /
        Opret submit / Save / Create / file upload. Soft /products/new is not success.
        Catalog /products has no create CTA. Distinct from list shell ui_products_list
        and shell-only ui_inventory_open (which never clicks Opret*).
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
                return _ui_products_create_changed_error()

            inventory_url = f"https://mit.billy.dk/{slug}/inventory"
            await page.goto(inventory_url, wait_until="domcontentloaded")
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
                    return _ui_products_create_changed_error()
                if _is_products_new_soft_url(page.url):
                    return _ui_products_create_changed_error()
                if not _is_inventory_url(page.url):
                    await asyncio.sleep(0.2)
                    continue
                if not await _has_inventory_heading(page):
                    await asyncio.sleep(0.2)
                    continue
                if not await _has_products_create_form_signature(page):
                    clicked = await _click_products_create_cta(page)
                    if not clicked:
                        await asyncio.sleep(0.2)
                        continue
                    await _await_page_settle(page)
                if _is_products_new_soft_url(page.url):
                    return _ui_products_create_changed_error()
                if _is_inventory_url(page.url) and await _has_products_create_form_signature(page):
                    signature = await _products_create_form_field_flags(page)
                    return UiProductsCreateOpenSuccess(
                        create_form_open=True,
                        name_field_visible=signature["name_field_visible"],
                        account_field_present=signature["account_field_present"],
                        sales_tax_ruleset_field_present=signature[
                            "sales_tax_ruleset_field_present"
                        ],
                        unit_price_field_present=signature["unit_price_field_present"],
                        shell_markers_present=await _has_shell_nav_markers(page),
                    )
                await asyncio.sleep(0.2)
            return _ui_products_create_changed_error()
        except BrowserEgressPolicyLoadError:
            return ToolError(
                code=StableErrorCode.EGRESS_DENIED,
                message="Browser egress policy prevented the products create form observation.",
            )
        except Exception:
            return ToolError(
                code=StableErrorCode.BILLY_ERROR,
                message="Browser products create form observation could not be completed.",
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

    async def ui_bills_create_open(self) -> UiBillsCreateOpenSuccess | ToolError:
        """Open the bill create form shell for the current authenticated UI session only.

        Research154: navigate to /:org_slug/bills/new (dual-proved real form).
        Form open only — never click Godkend / Gem som kladde / Upload fil / Træk /
        Tilføj linje / Slet. Distinct from list shell and invoice specials.
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
                return _ui_bills_create_changed_error()

            create_url = f"https://mit.billy.dk/{slug}/bills/new"
            await page.goto(create_url, wait_until="domcontentloaded")
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
                    return _ui_bills_create_changed_error()
                if _is_bills_create_url(page.url) and await _has_bills_create_signature(page):
                    return UiBillsCreateOpenSuccess(
                        draft_save_chrome_visible=True,
                        line_chrome_visible=True,
                        shell_markers_present=await _has_shell_nav_markers(page),
                    )
                await asyncio.sleep(0.2)
            return _ui_bills_create_changed_error()
        except BrowserEgressPolicyLoadError:
            return ToolError(
                code=StableErrorCode.EGRESS_DENIED,
                message="Browser egress policy prevented the bills create form observation.",
            )
        except Exception:
            return ToolError(
                code=StableErrorCode.BILLY_ERROR,
                message="Browser bills create form observation could not be completed.",
            )
        finally:
            if page is not None:
                try:
                    await page.close()
                except Exception:
                    pass

    async def ui_bills_get_open(self) -> UiBillsGetOpenSuccess | ToolError:
        """Open a bill detail surface for the authenticated UI session only.

        Research170: path-scoped bills GET/POST/DELETE + taxRates GET unlocks list
        rows and disposable seed. Open first non-header bill detail at path class
        /:org_slug/bills/:id. List text-click may land on /edit; normalize by
        soft-navigating to the read path. Never Gem/Godkend/Opdater/Slet/Træk.
        Soft /bills/new is not success.
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
                return _ui_bills_get_changed_error()

            bills_url = f"https://mit.billy.dk/{slug}/bills"
            await page.goto(bills_url, wait_until="domcontentloaded")
            await _await_page_settle(page)

            for _ in range(50):
                if await _has_known_login_page(page):
                    return _auth_required_error()
                if await _has_interaction_challenge(page):
                    return ToolError(
                        code=StableErrorCode.AUTH_INTERACTION_REQUIRED,
                        message="Browser authentication requires a non-automatable challenge.",
                    )
                if await _has_error_shell_markers(page):
                    return _ui_bills_get_changed_error()
                if _is_bills_create_url(page.url):
                    return _ui_bills_get_changed_error()

                # research170: text-click often lands on /edit; prefer read path.
                if _is_bills_edit_url(page.url):
                    read_url = _bills_edit_url_to_read_url(page.url)
                    if read_url is not None:
                        await page.goto(read_url, wait_until="domcontentloaded")
                        await _await_page_settle(page)
                        continue

                if await _has_bills_detail_signature(page, slug):
                    flags = await _bills_detail_flags(page)
                    return UiBillsGetOpenSuccess(
                        detail_open=True,
                        kladde_or_state_chrome_present=flags["kladde_or_state_chrome_present"],
                        supplier_chrome_present=flags["supplier_chrome_present"],
                        amount_or_line_chrome_present=flags["amount_or_line_chrome_present"],
                        shell_markers_present=await _has_shell_nav_markers(page),
                    )

                if _is_bills_list_url(page.url) and await _has_bills_list_signature(page):
                    opened = await _click_bills_detail_candidate(page, slug)
                    if opened:
                        await _await_page_settle(page)
                        continue
                await asyncio.sleep(0.25)
            return _ui_bills_get_changed_error()
        except BrowserEgressPolicyLoadError:
            return ToolError(
                code=StableErrorCode.EGRESS_DENIED,
                message="Browser egress policy prevented the bills detail observation.",
            )
        except Exception:
            return ToolError(
                code=StableErrorCode.BILLY_ERROR,
                message="Browser bills detail observation could not be completed.",
            )
        finally:
            if page is not None:
                try:
                    await page.close()
                except Exception:
                    pass

    async def ui_bills_update_open(self) -> UiBillsUpdateOpenSuccess | ToolError:
        """Open a bill edit form for the authenticated UI session only.

        Research172: path-scoped bills GET/POST/DELETE + taxRates GET unlocks list
        rows and disposable seed. Open first non-header bill edit surface at path
        class /:org_slug/bills/:id/edit. Read detail may appear first; soft-navigate
        to /edit. Never Opdater/Godkend/Slet/Træk/Upload/Registrer betaling submit.
        Soft /bills/new is not success. Distinct from get-open read path.
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
                return _ui_bills_update_changed_error()

            bills_url = f"https://mit.billy.dk/{slug}/bills"
            await page.goto(bills_url, wait_until="domcontentloaded")
            await _await_page_settle(page)

            for _ in range(50):
                if await _has_known_login_page(page):
                    return _auth_required_error()
                if await _has_interaction_challenge(page):
                    return ToolError(
                        code=StableErrorCode.AUTH_INTERACTION_REQUIRED,
                        message="Browser authentication requires a non-automatable challenge.",
                    )
                if await _has_error_shell_markers(page):
                    return _ui_bills_update_changed_error()
                if _is_bills_create_url(page.url):
                    return _ui_bills_update_changed_error()

                # research172: prefer edit path; soft-nav from read detail.
                if _is_bills_detail_url(page.url):
                    edit_url = _bills_read_url_to_edit_url(page.url)
                    if edit_url is not None:
                        await page.goto(edit_url, wait_until="domcontentloaded")
                        await _await_page_settle(page)
                        continue

                if await _has_bills_update_form_signature(page, slug):
                    flags = await _bills_update_form_flags(page)
                    return UiBillsUpdateOpenSuccess(
                        form_open=True,
                        ret_regning_chrome_present=flags["ret_regning_chrome_present"],
                        opdater_present=flags["opdater_present"],
                        leverandor_or_dates_chrome_present=flags[
                            "leverandor_or_dates_chrome_present"
                        ],
                        inputs_present=flags["inputs_present"],
                        shell_markers_present=await _has_shell_nav_markers(page),
                    )

                if _is_bills_list_url(page.url) and await _has_bills_list_signature(page):
                    opened = await _click_bills_detail_candidate(page, slug)
                    if opened:
                        await _await_page_settle(page)
                        continue
                await asyncio.sleep(0.25)
            return _ui_bills_update_changed_error()
        except BrowserEgressPolicyLoadError:
            return ToolError(
                code=StableErrorCode.EGRESS_DENIED,
                message="Browser egress policy prevented the bills update form observation.",
            )
        except Exception:
            return ToolError(
                code=StableErrorCode.BILLY_ERROR,
                message="Browser bills update form observation could not be completed.",
            )
        finally:
            if page is not None:
                try:
                    await page.close()
                except Exception:
                    pass

    async def ui_bills_delete_open(self) -> UiBillsDeleteOpenSuccess | ToolError:
        """Open bill delete chrome for the authenticated UI session only.

        Research173: path-scoped bills GET/POST/DELETE + taxRates GET unlock list
        rows and disposable seed. Open first non-header bill edit surface at path
        class /:org_slug/bills/:id/edit. Assert primary Slet; click Slet once to
        open confirm (Slet≥2 + Annuller); dismiss with Annuller only. Never second
        Slet / permanent delete / Opdater / Godkend. Soft /bills/new and read detail
        alone (no Slet) are not success. Distinct from update form_open.
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
                return _ui_bills_delete_changed_error()

            bills_url = f"https://mit.billy.dk/{slug}/bills"
            await page.goto(bills_url, wait_until="domcontentloaded")
            await _await_page_settle(page)

            for _ in range(50):
                if await _has_known_login_page(page):
                    return _auth_required_error()
                if await _has_interaction_challenge(page):
                    return ToolError(
                        code=StableErrorCode.AUTH_INTERACTION_REQUIRED,
                        message="Browser authentication requires a non-automatable challenge.",
                    )
                if await _has_error_shell_markers(page):
                    return _ui_bills_delete_changed_error()
                if _is_bills_create_url(page.url):
                    return _ui_bills_delete_changed_error()

                # Prefer edit path; soft-nav from read detail (Slet absent on read).
                if _is_bills_detail_url(page.url):
                    edit_url = _bills_read_url_to_edit_url(page.url)
                    if edit_url is not None:
                        await page.goto(edit_url, wait_until="domcontentloaded")
                        await _await_page_settle(page)
                        continue

                if await _has_bills_delete_primary_signature(page, slug):
                    primary = await _bills_delete_primary_flags(page)
                    if not primary.get("slet_present"):
                        return _ui_bills_delete_changed_error()

                    clicked = await _click_bills_primary_slet(page)
                    if not clicked:
                        return _ui_bills_delete_changed_error()
                    await _await_page_settle(page)

                    confirm = await _bills_delete_confirm_flags(page)
                    if not (
                        confirm.get("confirm_open")
                        and confirm.get("annuller_present")
                        and confirm.get("slet_present")
                    ):
                        # Dismiss any partial overlay; fail closed without permanent delete.
                        await _dismiss_bills_delete_confirm(page)
                        return _ui_bills_delete_changed_error()

                    dismissed = await _dismiss_bills_delete_confirm(page)
                    if not dismissed:
                        return _ui_bills_delete_changed_error()
                    await _await_page_settle(page)

                    if not _is_bills_edit_url(page.url):
                        return _ui_bills_delete_changed_error()

                    return UiBillsDeleteOpenSuccess(
                        edit_open=True,
                        slet_present=True,
                        confirm_open=True,
                        annuller_present=True,
                        confirm_dismissed=True,
                        shell_markers_present=await _has_shell_nav_markers(page),
                    )

                if _is_bills_list_url(page.url) and await _has_bills_list_signature(page):
                    opened = await _click_bills_detail_candidate(page, slug)
                    if opened:
                        await _await_page_settle(page)
                        continue
                await asyncio.sleep(0.25)
            return _ui_bills_delete_changed_error()
        except BrowserEgressPolicyLoadError:
            return ToolError(
                code=StableErrorCode.EGRESS_DENIED,
                message="Browser egress policy prevented the bills delete chrome observation.",
            )
        except Exception:
            return ToolError(
                code=StableErrorCode.BILLY_ERROR,
                message="Browser bills delete chrome observation could not be completed.",
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
                    file_input_present = await _has_file_input_present(page)
                    if not file_input_present:
                        # research155: Bilag upload surface requires file input
                        # binding chrome; never set_input_files.
                        await asyncio.sleep(0.2)
                        continue
                    return UiUploadsListSuccess(
                        upload_action_visible=True,
                        file_input_present=True,
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

    async def ui_daybooks_get_open(self) -> UiDaybooksGetOpenSuccess | ToolError:
        """Open an existing daybook editor surface for the authenticated UI session only.

        Research179: SPA list/get under committed egress unlocks daybook ids. Open
        first daybook at path class /:org_slug/daybooks/:id with editor markers.
        Distinct from list+create on /daybooks/new. Never Opret/Tilføj/Bogfør/Slet.
        Bare /daybooks Upsedasse is not success.
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
                return _ui_daybooks_get_changed_error()

            daybooks_new_url = f"https://mit.billy.dk/{slug}/daybooks/new"
            capture = _DaybookSpaCapture()
            capture.attach(page)
            await page.goto(daybooks_new_url, wait_until="domcontentloaded")
            await _await_page_settle(page)
            if await _has_known_login_page(page):
                return _auth_required_error()
            if await _has_error_shell_markers(page):
                return _ui_daybooks_get_changed_error()
            if _is_daybooks_bare_url(page.url):
                return _ui_daybooks_get_changed_error()

            daybook_id = await _resolve_first_daybook_id(context, page, capture, org_slug=slug)
            if not daybook_id:
                return _ui_daybooks_get_changed_error()

            get_url = f"https://mit.billy.dk/{slug}/daybooks/{daybook_id}"
            await page.goto(get_url, wait_until="domcontentloaded")
            await _await_page_settle(page)

            for _ in range(40):
                if await _has_known_login_page(page):
                    return _auth_required_error()
                if await _has_interaction_challenge(page):
                    return ToolError(
                        code=StableErrorCode.AUTH_INTERACTION_REQUIRED,
                        message="Browser authentication requires a non-automatable challenge.",
                    )
                if await _has_error_shell_markers(page):
                    return _ui_daybooks_get_changed_error()
                if _is_daybooks_bare_url(page.url) or _is_daybooks_editor_url(page.url):
                    return _ui_daybooks_get_changed_error()
                if _is_daybooks_get_url(page.url) and await _has_daybooks_editor_signature(page):
                    if _is_transactions_list_url(page.url):
                        return _ui_daybooks_get_changed_error()
                    return UiDaybooksGetOpenSuccess(
                        detail_open=True,
                        editor_markers_present=True,
                        shell_markers_present=await _has_shell_nav_markers(page),
                    )
                await asyncio.sleep(0.2)
            return _ui_daybooks_get_changed_error()
        except BrowserEgressPolicyLoadError:
            return ToolError(
                code=StableErrorCode.EGRESS_DENIED,
                message="Browser egress policy prevented the daybooks get observation.",
            )
        except Exception:
            return ToolError(
                code=StableErrorCode.BILLY_ERROR,
                message="Browser daybooks get observation could not be completed.",
            )
        finally:
            if page is not None:
                try:
                    await page.close()
                except Exception:
                    pass

    async def ui_daybooks_delete_open(self) -> UiDaybooksDeleteOpenSuccess | ToolError:
        """Open daybook delete chrome for the authenticated UI session only.

        Research180: SPA list under committed egress unlocks daybook ids. Open a
        daybook at path class /:org_slug/daybooks/:id, open Mere, classify Slet
        text in menu (export CSV/XLS/Importér + Slet). Primary Slet button
        absent. Prefer daybooks that expose Slet (system journals may omit it).
        Never confirm Slet / Gem / Bogfør / Tilføj. Distinct from get open and
        list+create on /daybooks/new.
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
                return _ui_daybooks_delete_changed_error()

            daybooks_new_url = f"https://mit.billy.dk/{slug}/daybooks/new"
            capture = _DaybookSpaCapture()
            capture.attach(page)
            await page.goto(daybooks_new_url, wait_until="domcontentloaded")
            await _await_page_settle(page)
            if await _has_known_login_page(page):
                return _auth_required_error()
            if await _has_error_shell_markers(page):
                return _ui_daybooks_delete_changed_error()
            if _is_daybooks_bare_url(page.url):
                return _ui_daybooks_delete_changed_error()

            daybook_ids = await _resolve_daybook_ids(context, page, capture, org_slug=slug)
            if not daybook_ids:
                return _ui_daybooks_delete_changed_error()

            for daybook_id in daybook_ids[:12]:
                get_url = f"https://mit.billy.dk/{slug}/daybooks/{daybook_id}"
                await page.goto(get_url, wait_until="domcontentloaded")
                await _await_page_settle(page)

                for _ in range(20):
                    if await _has_known_login_page(page):
                        return _auth_required_error()
                    if await _has_interaction_challenge(page):
                        return ToolError(
                            code=StableErrorCode.AUTH_INTERACTION_REQUIRED,
                            message="Browser authentication requires a non-automatable challenge.",
                        )
                    if await _has_error_shell_markers(page):
                        break
                    if _is_daybooks_bare_url(page.url) or _is_daybooks_editor_url(page.url):
                        break

                    if await _has_daybooks_delete_chrome_signature(page):
                        flags = await _daybooks_delete_chrome_flags(page)
                        primary = await _daybooks_delete_primary_flags(page)
                        return UiDaybooksDeleteOpenSuccess(
                            detail_open=True,
                            mere_open=flags["mere_open"],
                            slet_text_visible=flags["slet_text_visible"],
                            export_menu_visible=flags["export_menu_visible"],
                            primary_slet_absent=primary["primary_slet_absent"],
                            shell_markers_present=await _has_shell_nav_markers(page),
                        )

                    if _is_daybooks_get_url(page.url) and await _has_daybooks_editor_signature(
                        page
                    ):
                        primary = await _daybooks_delete_primary_flags(page)
                        if not primary.get("primary_slet_absent"):
                            break
                        if not primary.get("mere_present"):
                            break
                        clicked_mere = await _click_daybooks_mere_action(page)
                        if clicked_mere:
                            await _await_page_settle(page)
                            if await _has_daybooks_delete_chrome_signature(page):
                                flags = await _daybooks_delete_chrome_flags(page)
                                return UiDaybooksDeleteOpenSuccess(
                                    detail_open=True,
                                    mere_open=True,
                                    slet_text_visible=flags["slet_text_visible"],
                                    export_menu_visible=flags["export_menu_visible"],
                                    primary_slet_absent=True,
                                    shell_markers_present=await _has_shell_nav_markers(page),
                                )
                        break
                    await asyncio.sleep(0.15)
            return _ui_daybooks_delete_changed_error()
        except BrowserEgressPolicyLoadError:
            return ToolError(
                code=StableErrorCode.EGRESS_DENIED,
                message="Browser egress policy prevented the daybooks delete chrome observation.",
            )
        except Exception:
            return ToolError(
                code=StableErrorCode.BILLY_ERROR,
                message="Browser daybooks delete chrome observation could not be completed.",
            )
        finally:
            if page is not None:
                try:
                    await page.close()
                except Exception:
                    pass

    async def ui_daybook_transactions_create_open(
        self,
    ) -> UiDaybookTransactionsCreateOpenSuccess | ToolError:
        """Open daybookTransactions create chrome for the authenticated UI session only.

        Research181: SPA list under committed egress unlocks daybook ids. Open a
        daybook at path class /:org_slug/daybooks/:id and classify create chrome
        markers (Tilføj kassekladdelinje + Ingen postering valgt). Never click
        Tilføj / Bogfør / confirm Slet. Distinct from get open, Mere delete chrome,
        and list+create on /daybooks/new. Maps only daybookTransactions.create.
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
                return _ui_daybook_transactions_create_changed_error()

            daybooks_new_url = f"https://mit.billy.dk/{slug}/daybooks/new"
            capture = _DaybookSpaCapture()
            capture.attach(page)
            await page.goto(daybooks_new_url, wait_until="domcontentloaded")
            await _await_page_settle(page)
            if await _has_known_login_page(page):
                return _auth_required_error()
            if await _has_error_shell_markers(page):
                return _ui_daybook_transactions_create_changed_error()
            if _is_daybooks_bare_url(page.url):
                return _ui_daybook_transactions_create_changed_error()

            daybook_ids = await _resolve_daybook_ids(context, page, capture, org_slug=slug)
            if not daybook_ids:
                return _ui_daybook_transactions_create_changed_error()

            for daybook_id in daybook_ids[:12]:
                get_url = f"https://mit.billy.dk/{slug}/daybooks/{daybook_id}"
                await page.goto(get_url, wait_until="domcontentloaded")
                await _await_page_settle(page)

                for _ in range(40):
                    if await _has_known_login_page(page):
                        return _auth_required_error()
                    if await _has_interaction_challenge(page):
                        return ToolError(
                            code=StableErrorCode.AUTH_INTERACTION_REQUIRED,
                            message="Browser authentication requires a non-automatable challenge.",
                        )
                    if await _has_error_shell_markers(page):
                        break
                    if _is_daybooks_bare_url(page.url) or _is_daybooks_editor_url(page.url):
                        break

                    if _is_daybooks_get_url(
                        page.url
                    ) and await _has_daybook_transactions_create_chrome_signature(page):
                        if _is_transactions_list_url(page.url):
                            return _ui_daybook_transactions_create_changed_error()
                        flags = await _daybook_transactions_create_chrome_flags(page)
                        return UiDaybookTransactionsCreateOpenSuccess(
                            detail_open=True,
                            line_add_chrome_visible=flags["line_add_chrome_visible"],
                            empty_postering_state=flags["empty_postering_state"],
                            shell_markers_present=await _has_shell_nav_markers(page),
                        )
                    await asyncio.sleep(0.15)
            return _ui_daybook_transactions_create_changed_error()
        except BrowserEgressPolicyLoadError:
            return ToolError(
                code=StableErrorCode.EGRESS_DENIED,
                message=(
                    "Browser egress policy prevented the daybook transactions "
                    "create chrome observation."
                ),
            )
        except Exception:
            return ToolError(
                code=StableErrorCode.BILLY_ERROR,
                message=(
                    "Browser daybook transactions create chrome observation could not be completed."
                ),
            )
        finally:
            if page is not None:
                try:
                    await page.close()
                except Exception:
                    pass

    async def ui_transactions_create_open(
        self,
    ) -> UiTransactionsCreateOpenSuccess | ToolError:
        """Open transactions create chrome for the authenticated UI session only.

        Research182: open /:org_slug/transactions and classify create chrome markers
        (Posteringer heading + Ny postering CTA). Never click Gem / Bogfør / Opret
        submit / void / Slet. Soft /transactions/new title shell is not success.
        Distinct from ui_transactions_list (list mapping only). Maps only
        transactions.create.
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
                return _ui_transactions_create_changed_error()

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
                    return _ui_transactions_create_changed_error()
                if _is_transactions_list_url(
                    page.url
                ) and await _has_transactions_create_chrome_signature(page):
                    flags = await _transactions_create_chrome_flags(page)
                    return UiTransactionsCreateOpenSuccess(
                        list_open=True,
                        create_cta_visible=flags["create_cta_visible"],
                        shell_markers_present=await _has_shell_nav_markers(page),
                    )
                await asyncio.sleep(0.2)
            return _ui_transactions_create_changed_error()
        except BrowserEgressPolicyLoadError:
            return ToolError(
                code=StableErrorCode.EGRESS_DENIED,
                message=(
                    "Browser egress policy prevented the transactions create chrome observation."
                ),
            )
        except Exception:
            return ToolError(
                code=StableErrorCode.BILLY_ERROR,
                message="Browser transactions create chrome observation could not be completed.",
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

    async def ui_inventory_open(self) -> UiInventoryOpenSuccess | ToolError:
        """Open the Lagermodul inventory shell for the current session only.

        Research125: path /:org_slug/inventory, h1 Lagermodul. Soft aliases
        rejected. Distinct from products (Produkter). Never click Opret primo /
        Opret produkt / Opret status or other create CTAs. No invent api_inventory_*.
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
                return _ui_inventory_changed_error()

            inventory_url = f"https://mit.billy.dk/{slug}/inventory"
            await page.goto(inventory_url, wait_until="domcontentloaded")
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
                    return _ui_inventory_changed_error()
                # Fail closed if Billy routes inventory to products list shell.
                if await _has_products_list_signature(page):
                    return _ui_inventory_changed_error()
                if _is_inventory_url(page.url) and await _has_inventory_signature(page):
                    return UiInventoryOpenSuccess(
                        create_cta_markers_present=await _has_inventory_create_cta_markers(page),
                    )
                await asyncio.sleep(0.2)
            return _ui_inventory_changed_error()
        except BrowserEgressPolicyLoadError:
            return ToolError(
                code=StableErrorCode.EGRESS_DENIED,
                message="Browser egress policy prevented the inventory shell observation.",
            )
        except Exception:
            return ToolError(
                code=StableErrorCode.BILLY_ERROR,
                message="Browser inventory shell observation could not be completed.",
            )
        finally:
            if page is not None:
                try:
                    await page.close()
                except Exception:
                    pass

    async def ui_settings_company_open(self) -> UiSettingsCompanyOpenSuccess | ToolError:
        """Open the Indstillinger company (Virksomhed) settings shell.

        Research126: path /:org_slug/settings, h1 Indstillinger, company panel
        markers (Navn og adresse + Kontaktinformation). Soft aliases rejected.
        Never click Gem / Tilføj ejer / upload / Opret* / Opgrader. No invent
        api_settings_*.
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
                return _ui_settings_company_changed_error()

            settings_url = f"https://mit.billy.dk/{slug}/settings"
            await page.goto(settings_url, wait_until="domcontentloaded")
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
                    return _ui_settings_company_changed_error()
                if _is_settings_company_url(page.url) and await _has_settings_company_signature(
                    page
                ):
                    return UiSettingsCompanyOpenSuccess(
                        company_panel_markers_present=True,
                    )
                await asyncio.sleep(0.2)
            return _ui_settings_company_changed_error()
        except BrowserEgressPolicyLoadError:
            return ToolError(
                code=StableErrorCode.EGRESS_DENIED,
                message="Browser egress policy prevented the settings company shell observation.",
            )
        except Exception:
            return ToolError(
                code=StableErrorCode.BILLY_ERROR,
                message="Browser settings company shell observation could not be completed.",
            )
        finally:
            if page is not None:
                try:
                    await page.close()
                except Exception:
                    pass

    async def ui_settings_accounting_open(
        self,
    ) -> UiSettingsAccountingOpenSuccess | ToolError:
        """Open the Indstillinger accounting (Regnskab) settings panel.

        Research127: request /:org_slug/settings/accounting (SPA lands bare
        /:org_slug/settings), h1 Indstillinger, panel markers Regnskab + Køb +
        Kontoplan. Distinct from company default. Soft aliases and invoicing
        panel rejected. Never click Gem / Sæt låsedato / Opret* / Tilføj* /
        Upload / Opgrader. No invent api_settings_*.
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
                return _ui_settings_accounting_changed_error()

            # SPA seed: nested accounting rewrites to bare settings with Regnskab panel.
            accounting_url = f"https://mit.billy.dk/{slug}/settings/accounting"
            await page.goto(accounting_url, wait_until="domcontentloaded")
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
                    return _ui_settings_accounting_changed_error()
                if _is_settings_accounting_url(
                    page.url
                ) and await _has_settings_accounting_signature(page):
                    return UiSettingsAccountingOpenSuccess(
                        accounting_panel_markers_present=True,
                    )
                await asyncio.sleep(0.2)
            return _ui_settings_accounting_changed_error()
        except BrowserEgressPolicyLoadError:
            return ToolError(
                code=StableErrorCode.EGRESS_DENIED,
                message=(
                    "Browser egress policy prevented the settings accounting shell observation."
                ),
            )
        except Exception:
            return ToolError(
                code=StableErrorCode.BILLY_ERROR,
                message=("Browser settings accounting shell observation could not be completed."),
            )
        finally:
            if page is not None:
                try:
                    await page.close()
                except Exception:
                    pass

    async def ui_settings_invoicing_open(
        self,
    ) -> UiSettingsInvoicingOpenSuccess | ToolError:
        """Open the Indstillinger invoicing (Faktura) settings panel.

        Research128: request /:org_slug/settings/invoicing (SPA lands bare
        /:org_slug/settings), h1 Indstillinger, panel markers Faktura + Produkter +
        (Betalingsmetoder or Standard fakturalogo). Distinct from company default
        and accounting Regnskab panel. Soft aliases rejected. Never click Gem /
        Opret* / Tilføj* / Upload / Opgrader / Opret betalingsmetode. No invent
        api_settings_*.
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
                return _ui_settings_invoicing_changed_error()

            # SPA seed: nested invoicing rewrites to bare settings with Faktura panel.
            invoicing_url = f"https://mit.billy.dk/{slug}/settings/invoicing"
            await page.goto(invoicing_url, wait_until="domcontentloaded")
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
                    return _ui_settings_invoicing_changed_error()
                if _is_settings_invoicing_url(page.url) and await _has_settings_invoicing_signature(
                    page
                ):
                    return UiSettingsInvoicingOpenSuccess(
                        invoicing_panel_markers_present=True,
                    )
                await asyncio.sleep(0.2)
            return _ui_settings_invoicing_changed_error()
        except BrowserEgressPolicyLoadError:
            return ToolError(
                code=StableErrorCode.EGRESS_DENIED,
                message=(
                    "Browser egress policy prevented the settings invoicing shell observation."
                ),
            )
        except Exception:
            return ToolError(
                code=StableErrorCode.BILLY_ERROR,
                message=("Browser settings invoicing shell observation could not be completed."),
            )
        finally:
            if page is not None:
                try:
                    await page.close()
                except Exception:
                    pass

    async def ui_settings_user_open(self) -> UiSettingsUserOpenSuccess | ToolError:
        """Open the Indstillinger user (Profil) settings panel.

        Research129: soft URL seeds are insufficient. Open hub
        /:org_slug/settings then observe-only click side label Profil. Final
        path stays bare /:org_slug/settings with h1 Indstillinger and panel
        markers Profil + Billede + Sprog og tema + Skift adgangskode. Distinct
        from company, accounting, and invoicing panels. Never click Gem /
        Upload / password submit / Opret* / Tilføj*. No invent api_settings_*.
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
                return _ui_settings_user_changed_error()

            settings_url = f"https://mit.billy.dk/{slug}/settings"
            await page.goto(settings_url, wait_until="domcontentloaded")
            await _await_page_settle(page)

            if await _has_known_login_page(page):
                return _auth_required_error()
            if await _has_interaction_challenge(page):
                return ToolError(
                    code=StableErrorCode.AUTH_INTERACTION_REQUIRED,
                    message="Browser authentication requires a non-automatable challenge.",
                )
            if await _has_error_shell_markers(page):
                return _ui_settings_user_changed_error()
            if not _is_settings_user_url(page.url):
                return _ui_settings_user_changed_error()

            clicked = await _click_settings_side_nav_label(page, _SETTINGS_USER_SIDE_NAV_LABEL)
            if not clicked:
                return _ui_settings_user_changed_error()
            await _await_page_settle(page)

            for _ in range(30):
                if await _has_known_login_page(page):
                    return _auth_required_error()
                if await _has_interaction_challenge(page):
                    return ToolError(
                        code=StableErrorCode.AUTH_INTERACTION_REQUIRED,
                        message=("Browser authentication requires a non-automatable challenge."),
                    )
                if await _has_error_shell_markers(page):
                    return _ui_settings_user_changed_error()
                if _is_settings_user_url(page.url) and await _has_settings_user_signature(page):
                    return UiSettingsUserOpenSuccess(user_panel_markers_present=True)
                await asyncio.sleep(0.2)
            return _ui_settings_user_changed_error()
        except BrowserEgressPolicyLoadError:
            return ToolError(
                code=StableErrorCode.EGRESS_DENIED,
                message=("Browser egress policy prevented the settings user shell observation."),
            )
        except Exception:
            return ToolError(
                code=StableErrorCode.BILLY_ERROR,
                message=("Browser settings user shell observation could not be completed."),
            )
        finally:
            if page is not None:
                try:
                    await page.close()
                except Exception:
                    pass

    async def ui_settings_user_organizations_open(
        self,
    ) -> UiSettingsUserOrganizationsOpenSuccess | ToolError:
        """Open the Indstillinger user-organizations (Virksomheder) settings panel.

        Research152: soft URL seeds are insufficient. Open hub
        /:org_slug/settings then observe-only click Profil (group) then
        Virksomheder. Final path stays bare /:org_slug/settings with h1
        Indstillinger and panel markers Virksomheder + Alle organisationer +
        Opret organisation (chrome only; never click Opret). Distinct from
        Profil user fields, company form, and Brugere. No invent api_settings_*.
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
                return _ui_settings_user_organizations_changed_error()

            settings_url = f"https://mit.billy.dk/{slug}/settings"
            await page.goto(settings_url, wait_until="domcontentloaded")
            await _await_page_settle(page)

            if await _has_known_login_page(page):
                return _auth_required_error()
            if await _has_interaction_challenge(page):
                return ToolError(
                    code=StableErrorCode.AUTH_INTERACTION_REQUIRED,
                    message="Browser authentication requires a non-automatable challenge.",
                )
            if await _has_error_shell_markers(page):
                return _ui_settings_user_organizations_changed_error()
            if not _is_settings_user_organizations_url(page.url):
                return _ui_settings_user_organizations_changed_error()

            # Open Profil group first when present (research152 dual path).
            await _click_settings_side_nav_label(page, _SETTINGS_USER_SIDE_NAV_LABEL)
            await _await_page_settle(page)

            clicked = await _click_settings_side_nav_label(
                page, _SETTINGS_USER_ORGANIZATIONS_SIDE_NAV_LABEL
            )
            if not clicked:
                return _ui_settings_user_organizations_changed_error()
            await _await_page_settle(page)

            for _ in range(30):
                if await _has_known_login_page(page):
                    return _auth_required_error()
                if await _has_interaction_challenge(page):
                    return ToolError(
                        code=StableErrorCode.AUTH_INTERACTION_REQUIRED,
                        message=("Browser authentication requires a non-automatable challenge."),
                    )
                if await _has_error_shell_markers(page):
                    return _ui_settings_user_organizations_changed_error()
                if _is_settings_user_organizations_url(
                    page.url
                ) and await _has_settings_user_organizations_signature(page):
                    return UiSettingsUserOrganizationsOpenSuccess(
                        user_organizations_panel_markers_present=True
                    )
                await asyncio.sleep(0.2)
            return _ui_settings_user_organizations_changed_error()
        except BrowserEgressPolicyLoadError:
            return ToolError(
                code=StableErrorCode.EGRESS_DENIED,
                message=(
                    "Browser egress policy prevented the settings user "
                    "organizations shell observation."
                ),
            )
        except Exception:
            return ToolError(
                code=StableErrorCode.BILLY_ERROR,
                message=(
                    "Browser settings user organizations shell observation could not be completed."
                ),
            )
        finally:
            if page is not None:
                try:
                    await page.close()
                except Exception:
                    pass

    async def ui_settings_vat_open(self) -> UiSettingsVatOpenSuccess | ToolError:
        """Open the Indstillinger VAT (Momssatser) settings panel.

        Research130: soft URL seeds are insufficient. Open hub
        /:org_slug/settings then observe-only click side label Momssatser. Final
        path stays bare /:org_slug/settings with h1 Indstillinger and panel
        markers Regelsæt + Satser for salg + Satser for køb. Distinct from
        company, accounting, invoicing, and user panels. Never click Opret /
        Gem / Tilføj / Upload. No invent api_settings_*.
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
                return _ui_settings_vat_changed_error()

            settings_url = f"https://mit.billy.dk/{slug}/settings"
            await page.goto(settings_url, wait_until="domcontentloaded")
            await _await_page_settle(page)

            if await _has_known_login_page(page):
                return _auth_required_error()
            if await _has_interaction_challenge(page):
                return ToolError(
                    code=StableErrorCode.AUTH_INTERACTION_REQUIRED,
                    message="Browser authentication requires a non-automatable challenge.",
                )
            if await _has_error_shell_markers(page):
                return _ui_settings_vat_changed_error()
            if not _is_settings_vat_url(page.url):
                return _ui_settings_vat_changed_error()

            clicked = await _click_settings_side_nav_label(page, _SETTINGS_VAT_SIDE_NAV_LABEL)
            if not clicked:
                return _ui_settings_vat_changed_error()
            await _await_page_settle(page)

            for _ in range(30):
                if await _has_known_login_page(page):
                    return _auth_required_error()
                if await _has_interaction_challenge(page):
                    return ToolError(
                        code=StableErrorCode.AUTH_INTERACTION_REQUIRED,
                        message=("Browser authentication requires a non-automatable challenge."),
                    )
                if await _has_error_shell_markers(page):
                    return _ui_settings_vat_changed_error()
                if _is_settings_vat_url(page.url) and await _has_settings_vat_signature(page):
                    return UiSettingsVatOpenSuccess(vat_panel_markers_present=True)
                await asyncio.sleep(0.2)
            return _ui_settings_vat_changed_error()
        except BrowserEgressPolicyLoadError:
            return ToolError(
                code=StableErrorCode.EGRESS_DENIED,
                message=("Browser egress policy prevented the settings VAT shell observation."),
            )
        except Exception:
            return ToolError(
                code=StableErrorCode.BILLY_ERROR,
                message=("Browser settings VAT shell observation could not be completed."),
            )
        finally:
            if page is not None:
                try:
                    await page.close()
                except Exception:
                    pass

    async def ui_settings_users_open(self) -> UiSettingsUsersOpenSuccess | ToolError:
        """Open the Indstillinger org users (Brugere) settings panel.

        Research131: soft URL seeds are insufficient. Open hub
        /:org_slug/settings then observe-only click side label Brugere. Final
        path stays bare /:org_slug/settings with h1 Indstillinger and panel
        markers Brugere + Revisorer og bogholdere. Distinct from company,
        accounting, invoicing, user, and vat panels. Never click Invitér /
        Overdrag / Find en bogholder / Gem / Opret. No invent api_settings_*.
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
                return _ui_settings_users_changed_error()

            settings_url = f"https://mit.billy.dk/{slug}/settings"
            await page.goto(settings_url, wait_until="domcontentloaded")
            await _await_page_settle(page)

            if await _has_known_login_page(page):
                return _auth_required_error()
            if await _has_interaction_challenge(page):
                return ToolError(
                    code=StableErrorCode.AUTH_INTERACTION_REQUIRED,
                    message="Browser authentication requires a non-automatable challenge.",
                )
            if await _has_error_shell_markers(page):
                return _ui_settings_users_changed_error()
            if not _is_settings_users_url(page.url):
                return _ui_settings_users_changed_error()

            clicked = await _click_settings_side_nav_label(page, _SETTINGS_USERS_SIDE_NAV_LABEL)
            if not clicked:
                return _ui_settings_users_changed_error()
            await _await_page_settle(page)

            for _ in range(30):
                if await _has_known_login_page(page):
                    return _auth_required_error()
                if await _has_interaction_challenge(page):
                    return ToolError(
                        code=StableErrorCode.AUTH_INTERACTION_REQUIRED,
                        message=("Browser authentication requires a non-automatable challenge."),
                    )
                if await _has_error_shell_markers(page):
                    return _ui_settings_users_changed_error()
                if _is_settings_users_url(page.url) and await _has_settings_users_signature(page):
                    return UiSettingsUsersOpenSuccess(users_panel_markers_present=True)
                await asyncio.sleep(0.2)
            return _ui_settings_users_changed_error()
        except BrowserEgressPolicyLoadError:
            return ToolError(
                code=StableErrorCode.EGRESS_DENIED,
                message=("Browser egress policy prevented the settings users shell observation."),
            )
        except Exception:
            return ToolError(
                code=StableErrorCode.BILLY_ERROR,
                message=("Browser settings users shell observation could not be completed."),
            )
        finally:
            if page is not None:
                try:
                    await page.close()
                except Exception:
                    pass

    async def ui_settings_access_token_open(
        self,
    ) -> UiSettingsAccessTokenOpenSuccess | ToolError:
        """Open the Indstillinger access-keys (Adgangsnøgler) settings panel.

        Research132: soft URL seeds are insufficient. Open hub
        /:org_slug/settings then observe-only click side label Adgangsnøgler.
        Final path stays bare /:org_slug/settings with h1 Indstillinger and
        panel marker Adgangsnøgler. Distinct from company, accounting,
        invoicing, user, vat, users, and beta panels. Never click Opret
        adgangsnøgle / Gem / Opret. No invent api_settings_*.
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
                return _ui_settings_access_token_changed_error()

            settings_url = f"https://mit.billy.dk/{slug}/settings"
            await page.goto(settings_url, wait_until="domcontentloaded")
            await _await_page_settle(page)

            if await _has_known_login_page(page):
                return _auth_required_error()
            if await _has_interaction_challenge(page):
                return ToolError(
                    code=StableErrorCode.AUTH_INTERACTION_REQUIRED,
                    message="Browser authentication requires a non-automatable challenge.",
                )
            if await _has_error_shell_markers(page):
                return _ui_settings_access_token_changed_error()
            if not _is_settings_access_token_url(page.url):
                return _ui_settings_access_token_changed_error()

            clicked = await _click_settings_side_nav_label(
                page, _SETTINGS_ACCESS_TOKEN_SIDE_NAV_LABEL
            )
            if not clicked:
                return _ui_settings_access_token_changed_error()
            await _await_page_settle(page)

            for _ in range(30):
                if await _has_known_login_page(page):
                    return _auth_required_error()
                if await _has_interaction_challenge(page):
                    return ToolError(
                        code=StableErrorCode.AUTH_INTERACTION_REQUIRED,
                        message=("Browser authentication requires a non-automatable challenge."),
                    )
                if await _has_error_shell_markers(page):
                    return _ui_settings_access_token_changed_error()
                if _is_settings_access_token_url(
                    page.url
                ) and await _has_settings_access_token_signature(page):
                    return UiSettingsAccessTokenOpenSuccess(access_token_panel_markers_present=True)
                await asyncio.sleep(0.2)
            return _ui_settings_access_token_changed_error()
        except BrowserEgressPolicyLoadError:
            return ToolError(
                code=StableErrorCode.EGRESS_DENIED,
                message=(
                    "Browser egress policy prevented the settings access token shell observation."
                ),
            )
        except Exception:
            return ToolError(
                code=StableErrorCode.BILLY_ERROR,
                message=("Browser settings access token shell observation could not be completed."),
            )
        finally:
            if page is not None:
                try:
                    await page.close()
                except Exception:
                    pass

    async def ui_settings_beta_open(self) -> UiSettingsBetaOpenSuccess | ToolError:
        """Open the Indstillinger betas (Betas / Tidlig adgang) settings panel.

        Research133: soft URL seeds are mostly insufficient (settings/betas may
        open beta dual but product uses hub+click). Open hub /:org_slug/settings
        then observe-only click side label Betas. Final path stays bare
        /:org_slug/settings with h1 Indstillinger and panel markers Betas +
        Tidlig adgang. Distinct from company, accounting, invoicing, user, vat,
        users, and access_token panels. Never click Opret / Gem. No invent
        api_settings_* / api_beta_*.
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
                return _ui_settings_beta_changed_error()

            settings_url = f"https://mit.billy.dk/{slug}/settings"
            await page.goto(settings_url, wait_until="domcontentloaded")
            await _await_page_settle(page)

            if await _has_known_login_page(page):
                return _auth_required_error()
            if await _has_interaction_challenge(page):
                return ToolError(
                    code=StableErrorCode.AUTH_INTERACTION_REQUIRED,
                    message="Browser authentication requires a non-automatable challenge.",
                )
            if await _has_error_shell_markers(page):
                return _ui_settings_beta_changed_error()
            if not _is_settings_beta_url(page.url):
                return _ui_settings_beta_changed_error()

            clicked = await _click_settings_side_nav_label(page, _SETTINGS_BETA_SIDE_NAV_LABEL)
            if not clicked:
                return _ui_settings_beta_changed_error()
            await _await_page_settle(page)

            for _ in range(30):
                if await _has_known_login_page(page):
                    return _auth_required_error()
                if await _has_interaction_challenge(page):
                    return ToolError(
                        code=StableErrorCode.AUTH_INTERACTION_REQUIRED,
                        message=("Browser authentication requires a non-automatable challenge."),
                    )
                if await _has_error_shell_markers(page):
                    return _ui_settings_beta_changed_error()
                if _is_settings_beta_url(page.url) and await _has_settings_beta_signature(page):
                    return UiSettingsBetaOpenSuccess(beta_panel_markers_present=True)
                await asyncio.sleep(0.2)
            return _ui_settings_beta_changed_error()
        except BrowserEgressPolicyLoadError:
            return ToolError(
                code=StableErrorCode.EGRESS_DENIED,
                message=("Browser egress policy prevented the settings beta shell observation."),
            )
        except Exception:
            return ToolError(
                code=StableErrorCode.BILLY_ERROR,
                message=("Browser settings beta shell observation could not be completed."),
            )
        finally:
            if page is not None:
                try:
                    await page.close()
                except Exception:
                    pass

    async def ui_settings_subscription_open(
        self,
    ) -> UiSettingsSubscriptionOpenSuccess | ToolError:
        """Open the Indstillinger Abonnement empty-panel settings shell.

        Research134: soft URL seeds are mostly insufficient (settings/subscription
        may open empty dual but product uses hub+click). Open hub
        /:org_slug/settings then observe-only click side label Abonnement. Final
        path stays bare /:org_slug/settings with h1 Indstillinger and empty h2
        panel (no company/beta/other panel content). Never click Opgrader /
        Skift abonnement / Betal / Køb / Gem. No invent api_settings_* /
        api_subscription_*.
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
                return _ui_settings_subscription_changed_error()

            settings_url = f"https://mit.billy.dk/{slug}/settings"
            await page.goto(settings_url, wait_until="domcontentloaded")
            await _await_page_settle(page)

            if await _has_known_login_page(page):
                return _auth_required_error()
            if await _has_interaction_challenge(page):
                return ToolError(
                    code=StableErrorCode.AUTH_INTERACTION_REQUIRED,
                    message="Browser authentication requires a non-automatable challenge.",
                )
            if await _has_error_shell_markers(page):
                return _ui_settings_subscription_changed_error()
            if not _is_settings_subscription_url(page.url):
                return _ui_settings_subscription_changed_error()

            clicked = await _click_settings_side_nav_label(
                page, _SETTINGS_SUBSCRIPTION_SIDE_NAV_LABEL
            )
            if not clicked:
                return _ui_settings_subscription_changed_error()
            await _await_page_settle(page)

            for _ in range(30):
                if await _has_known_login_page(page):
                    return _auth_required_error()
                if await _has_interaction_challenge(page):
                    return ToolError(
                        code=StableErrorCode.AUTH_INTERACTION_REQUIRED,
                        message=("Browser authentication requires a non-automatable challenge."),
                    )
                if await _has_error_shell_markers(page):
                    return _ui_settings_subscription_changed_error()
                if _is_settings_subscription_url(
                    page.url
                ) and await _has_settings_subscription_signature(page):
                    return UiSettingsSubscriptionOpenSuccess(empty_panel=True)
                await asyncio.sleep(0.2)
            return _ui_settings_subscription_changed_error()
        except BrowserEgressPolicyLoadError:
            return ToolError(
                code=StableErrorCode.EGRESS_DENIED,
                message=(
                    "Browser egress policy prevented the settings subscription shell observation."
                ),
            )
        except Exception:
            return ToolError(
                code=StableErrorCode.BILLY_ERROR,
                message=("Browser settings subscription shell observation could not be completed."),
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


def _is_invoices_create_url(url: str) -> bool:
    """Accept mit.billy.dk /:org_slug/invoices/new, including Billy query params."""

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
        and bool(_INVOICES_CREATE_PATH.match(parsed.path or ""))
    )


def _is_invoices_edit_url(url: str) -> bool:
    """Accept mit.billy.dk /:org_slug/invoices/:id/edit detail (not list, not /new)."""

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
        and bool(_INVOICES_EDIT_PATH.match(parsed.path or ""))
    )


def _is_bills_create_url(url: str) -> bool:
    """Accept mit.billy.dk /:org_slug/bills/new, including Billy query params."""

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
        and bool(_BILLS_CREATE_PATH.match(parsed.path or ""))
    )


def _is_bills_detail_url(url: str) -> bool:
    """Accept mit.billy.dk /:org_slug/bills/:id read detail (not list, not /new, not /edit)."""

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
        and bool(_BILLS_DETAIL_PATH.match(parsed.path or ""))
    )


def _is_bills_edit_url(url: str) -> bool:
    """Accept mit.billy.dk /:org_slug/bills/:id/edit intermediate surface."""

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
        and bool(_BILLS_EDIT_PATH.match(parsed.path or ""))
    )


def _bills_edit_url_to_read_url(url: str) -> str | None:
    """Map /bills/:id/edit → /bills/:id for research170 preferred get path."""

    try:
        parsed = urlsplit(url)
    except ValueError:
        return None
    path = parsed.path or ""
    if not path.endswith("/edit"):
        return None
    read_path = path[: -len("/edit")]
    if not _BILLS_DETAIL_PATH.match(read_path):
        return None
    return f"https://mit.billy.dk{read_path}"


def _bills_read_url_to_edit_url(url: str) -> str | None:
    """Map /bills/:id → /bills/:id/edit for research172 update form path."""

    try:
        parsed = urlsplit(url)
    except ValueError:
        return None
    path = (parsed.path or "").rstrip("/")
    if not _BILLS_DETAIL_PATH.match(path):
        return None
    return f"https://mit.billy.dk{path}/edit"


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


def _is_inventory_url(url: str) -> bool:
    """Return True when the URL is the inventory (Lagermodul) path on the app host."""

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
        and bool(_INVENTORY_PATH.match(parsed.path or ""))
    )


def _is_settings_company_url(url: str) -> bool:
    """Return True when the URL is the settings hub leaf on the app host."""

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
        and bool(_SETTINGS_COMPANY_PATH.match(parsed.path or ""))
    )


def _is_settings_accounting_url(url: str) -> bool:
    """Return True when the URL is the bare settings hub leaf (after SPA rewrite)."""

    return _is_settings_company_url(url)


def _is_settings_invoicing_url(url: str) -> bool:
    """Return True when the URL is the bare settings hub leaf (after SPA rewrite)."""

    return _is_settings_company_url(url)


def _is_settings_user_url(url: str) -> bool:
    """Return True when the URL is the bare settings hub leaf (Profil panel path)."""

    return _is_settings_company_url(url)


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


def _is_daybooks_get_url(url: str) -> bool:
    """Return True when the URL is an existing daybook id path (research179)."""

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
        and bool(_DAYBOOKS_GET_PATH.match(parsed.path or ""))
    )


class _DaybookSpaCapture:
    """Capture SPA access token and organisation id from allowlisted API traffic."""

    def __init__(self) -> None:
        self.token: str | None = None
        self.org_id: str | None = None

    def attach(self, page: LoginPage) -> None:
        def on_req(req: Any) -> None:  # pyright: ignore[reportUnknownParameterType]
            try:
                url = str(req.url)
            except Exception:
                return
            if "api.billysbilling.com" not in url:
                return
            try:
                headers = {str(k).lower(): str(v) for k, v in dict(req.headers).items()}
            except Exception:
                headers = {}
            tok = headers.get("x-access-token") or headers.get("x-token")
            if tok and not self.token:
                self.token = tok
            org = headers.get("x-organizationid") or headers.get("x-organization-id")
            if org and not self.org_id:
                self.org_id = org

        cast(Any, page).on("request", on_req)


async def _resolve_first_daybook_id(
    context: Any, page: LoginPage, capture: _DaybookSpaCapture, *, org_slug: str | None = None
) -> str | None:
    """List daybooks via SPA under egress; return first id or None."""

    try:
        if _is_daybooks_get_url(page.url):
            path = urlsplit(page.url).path or ""
            parts = [part for part in path.split("/") if part]
            if len(parts) >= 2 and parts[-2] == "daybooks" and parts[-1] != "new":
                return parts[-1]
    except Exception:
        pass

    if not capture.token:
        try:
            await cast(Any, page).wait_for_timeout(1500)
        except Exception:
            await asyncio.sleep(1.5)

    if not capture.token:
        return None

    org_id = capture.org_id
    if not org_id:
        org_id = await _resolve_organization_id_for_slug(context, capture.token, org_slug)
    if not org_id:
        return None

    headers: dict[str, str] = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "X-Access-Token": capture.token,
    }
    url = f"https://api.billysbilling.com/v2/daybooks?organizationId={org_id}&pageSize=50"
    try:
        response: Any = await context.request.get(url, headers=headers)
        payload: object = await response.json()
    except Exception:
        return None
    if not isinstance(payload, dict):
        return None
    rows_obj: object = cast(dict[str, object], payload).get("daybooks")
    if not isinstance(rows_obj, list) or len(cast(list[object], rows_obj)) < 1:
        return None
    first_obj: object = cast(list[object], rows_obj)[0]
    if not isinstance(first_obj, dict):
        return None
    daybook_id_obj: object = cast(dict[str, object], first_obj).get("id")
    if not isinstance(daybook_id_obj, (str, int)):
        return None
    return str(daybook_id_obj)


async def _resolve_daybook_ids(
    context: Any, page: LoginPage, capture: _DaybookSpaCapture, *, org_slug: str | None = None
) -> list[str]:
    """List daybook ids via SPA under egress (prefer later rows first)."""

    if not capture.token:
        try:
            await cast(Any, page).wait_for_timeout(1500)
        except Exception:
            await asyncio.sleep(1.5)
    if not capture.token:
        return []
    org_id = capture.org_id
    if not org_id:
        org_id = await _resolve_organization_id_for_slug(context, capture.token, org_slug)
    if not org_id:
        return []
    headers: dict[str, str] = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "X-Access-Token": capture.token,
    }
    url = f"https://api.billysbilling.com/v2/daybooks?organizationId={org_id}&pageSize=50"
    try:
        response: Any = await context.request.get(url, headers=headers)
        payload: object = await response.json()
    except Exception:
        return []
    if not isinstance(payload, dict):
        return []
    rows_obj: object = cast(dict[str, object], payload).get("daybooks")
    if not isinstance(rows_obj, list):
        return []
    ids: list[str] = []
    for row_obj in cast(list[object], rows_obj):
        if not isinstance(row_obj, dict):
            continue
        daybook_id_obj: object = cast(dict[str, object], row_obj).get("id")
        if isinstance(daybook_id_obj, (str, int)):
            ids.append(str(daybook_id_obj))
    return list(reversed(ids))


async def _resolve_organization_id_for_slug(
    context: Any, token: str, org_slug: str | None
) -> str | None:
    """Resolve Billy organisation id via allowlisted /user/organizations."""

    headers = {
        "Accept": "application/json",
        "Authorization": f"Bearer {token}",
    }
    try:
        response: Any = await context.request.get(
            "https://api.billysbilling.com/user/organizations",
            headers=headers,
        )
        payload: object = await response.json()
    except Exception:
        return None
    if not isinstance(payload, dict):
        return None
    rows_obj: object = cast(dict[str, object], payload).get("data")
    if not isinstance(rows_obj, list) or not rows_obj:
        return None
    rows = cast(list[object], rows_obj)
    chosen: dict[str, object] | None = None
    if org_slug:
        for row_obj in rows:
            if not isinstance(row_obj, dict):
                continue
            row = cast(dict[str, object], row_obj)
            if str(row.get("url") or "") == org_slug:
                chosen = row
                break
    if chosen is None:
        first = rows[0]
        if not isinstance(first, dict):
            return None
        chosen = cast(dict[str, object], first)
    org_id_obj: object = chosen.get("organizationId")
    if not isinstance(org_id_obj, str) or not org_id_obj:
        return None
    return org_id_obj


def _ui_daybooks_get_changed_error() -> ToolError:
    return ToolError(
        code=StableErrorCode.UI_CHANGED,
        message="Billy daybooks get surface could not be classified.",
    )


def _ui_daybooks_delete_changed_error() -> ToolError:
    return ToolError(
        code=StableErrorCode.UI_CHANGED,
        message="Billy daybooks delete chrome could not be classified.",
    )


def _ui_daybook_transactions_create_changed_error() -> ToolError:
    return ToolError(
        code=StableErrorCode.UI_CHANGED,
        message="Billy daybook transactions create chrome could not be classified.",
    )


async def _daybook_transactions_create_chrome_flags(page: LoginPage) -> dict[str, bool]:
    """Non-PII create chrome flags on daybook id surface (research181). Never clicks Tilføj."""

    try:
        body = re.sub(r"\s+", " ", await page.locator("body").inner_text())[:2200]
    except Exception:
        body = ""
    line_add = bool(re.search(r"Tilføj kassekladdelinje", body)) or (
        await _count_labeled_buttons(page, "Tilføj kassekladdelinje") >= 1
    )
    # text-only fallback for marker visibility
    if not line_add:
        try:
            control = page.locator("text=Tilføj kassekladdelinje")
            line_add = await control.count() >= 1 and await control.first.is_visible()
        except Exception:
            line_add = False
    empty_state = bool(re.search(r"Ingen postering valgt", body))
    if not empty_state:
        try:
            control = page.locator("text=Ingen postering valgt")
            empty_state = await control.count() >= 1 and await control.first.is_visible()
        except Exception:
            empty_state = False
    return {
        "line_add_chrome_visible": bool(line_add),
        "empty_postering_state": bool(empty_state),
    }


async def _has_daybook_transactions_create_chrome_signature(page: LoginPage) -> bool:
    """Strict create-chrome signature — daybook id path + line-add + empty postering."""

    try:
        if _is_daybooks_editor_url(page.url) or _is_daybooks_bare_url(page.url):
            return False
        if not _is_daybooks_get_url(page.url):
            return False
        flags = await _daybook_transactions_create_chrome_flags(page)
        return bool(flags.get("line_add_chrome_visible") and flags.get("empty_postering_state"))
    except Exception:
        return False


def _ui_transactions_create_changed_error() -> ToolError:
    return ToolError(
        code=StableErrorCode.UI_CHANGED,
        message="Billy transactions create chrome could not be classified.",
    )


async def _transactions_create_chrome_flags(page: LoginPage) -> dict[str, bool]:
    """Non-PII create chrome flags on Posteringer list (research182). Never clicks Ny postering."""

    try:
        body = re.sub(r"\s+", " ", await page.locator("body").inner_text())[:2200]
    except Exception:
        body = ""
    heading_ok = False
    try:
        heading = page.locator("h1")
        if await heading.count() >= 1:
            first = heading.first
            if await first.is_visible():
                heading_ok = (await first.inner_text()).strip() == _TRANSACTIONS_LIST_HEADING
    except Exception:
        heading_ok = False
    if not heading_ok:
        heading_ok = bool(re.search(rf"\b{re.escape(_TRANSACTIONS_LIST_HEADING)}\b", body))
    cta = False
    try:
        create_action = page.locator(f"text={_TRANSACTIONS_CREATE_CTA}")
        if await create_action.count() >= 1:
            cta = await create_action.first.is_visible()
    except Exception:
        cta = False
    if not cta:
        cta = bool(re.search(re.escape(_TRANSACTIONS_CREATE_CTA), body)) or (
            await _count_labeled_buttons(page, _TRANSACTIONS_CREATE_CTA) >= 1
        )
    return {
        "list_heading_visible": bool(heading_ok),
        "create_cta_visible": bool(cta),
    }


async def _has_transactions_create_chrome_signature(page: LoginPage) -> bool:
    """Strict create-chrome signature — list path + Posteringer + Ny postering."""

    try:
        if not _is_transactions_list_url(page.url):
            return False
        flags = await _transactions_create_chrome_flags(page)
        return bool(flags.get("list_heading_visible") and flags.get("create_cta_visible"))
    except Exception:
        return False


async def _daybooks_delete_primary_flags(page: LoginPage) -> dict[str, bool]:
    """Primary id-path chrome before Mere — Slet should not be a primary button."""

    try:
        body = re.sub(r"\s+", " ", await page.locator("body").inner_text())[:1800]
    except Exception:
        body = ""
    slet_btn_n = await _count_role_button_exact(page, "Slet")
    mere_btn_n = await _count_labeled_buttons(page, "Mere")
    mere_text = bool(re.search(r"\bMere\b", body))
    return {
        "primary_slet_absent": slet_btn_n == 0,
        "mere_present": mere_btn_n >= 1 or mere_text,
    }


async def _daybooks_delete_chrome_flags(page: LoginPage) -> dict[str, bool]:
    """Non-PII delete chrome flags after Mere (research180). Never confirms delete."""

    try:
        body = re.sub(r"\s+", " ", await page.locator("body").inner_text())[:2200]
    except Exception:
        body = ""
    slet_text = bool(re.search(r"(?<![A-Za-zÆØÅæøå])Slet(?![A-Za-zÆØÅæøå])", body))
    export_menu = bool(
        re.search(r"Eksport[eé]r", body, re.I)
        or re.search(r"\.CSV", body, re.I)
        or re.search(r"\.XLS", body, re.I)
        or re.search(r"Import[eé]r", body, re.I)
    )
    mere_label = bool(re.search(r"\bMere\b", body))
    mere_open = mere_label and slet_text and export_menu
    return {
        "mere_open": mere_open,
        "slet_text_visible": slet_text,
        "export_menu_visible": export_menu,
        "primary_slet_absent": (await _count_role_button_exact(page, "Slet")) == 0,
    }


async def _has_daybooks_delete_chrome_signature(page: LoginPage) -> bool:
    """Strict delete-chrome signature — daybook id path + Mere menu + Slet text."""

    try:
        if _is_daybooks_editor_url(page.url) or _is_daybooks_bare_url(page.url):
            return False
        if not _is_daybooks_get_url(page.url):
            return False
        flags = await _daybooks_delete_chrome_flags(page)
        return bool(flags.get("mere_open") and flags.get("slet_text_visible"))
    except Exception:
        return False


async def _click_daybooks_mere_action(page: LoginPage) -> bool:
    """Click Mere/More on daybook id surface without Slet confirm. Research180."""

    live = cast(Any, page)
    for selector in ("text=Mere", "text=More"):
        try:
            mere = live.locator(selector)
            count = int(await mere.count())
            for index in range(min(count, 6)):
                el = mere.nth(index)
                try:
                    if not await el.is_visible():
                        continue
                    await el.click(timeout=2500)
                    return True
                except Exception:
                    continue
        except Exception:
            continue
    try:
        mere_btn = live.get_by_role("button", name="Mere", exact=True)
        if int(await mere_btn.count()) >= 1:
            await mere_btn.first.click(timeout=2500)
            return True
    except Exception:
        pass
    return False


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


def _ui_inventory_changed_error() -> ToolError:
    """Fail closed when Lagermodul inventory shell no longer matches research125."""

    return ToolError(
        code=StableErrorCode.UI_CHANGED,
        message="Billy inventory interface no longer matches the recorded signature.",
    )


def _ui_settings_accounting_changed_error() -> ToolError:
    """Stable UI_CHANGED for settings accounting shell classification failures."""

    return ToolError(
        code=StableErrorCode.UI_CHANGED,
        message="Billy settings accounting shell was not available in the expected form.",
    )


def _ui_settings_invoicing_changed_error() -> ToolError:
    """Stable UI_CHANGED for settings invoicing shell classification failures."""

    return ToolError(
        code=StableErrorCode.UI_CHANGED,
        message="Billy settings invoicing shell was not available in the expected form.",
    )


def _ui_settings_user_changed_error() -> ToolError:
    """Stable UI_CHANGED for settings user (Profil) shell classification failures."""

    return ToolError(
        code=StableErrorCode.UI_CHANGED,
        message="Billy settings user shell was not available in the expected form.",
    )


def _ui_settings_company_changed_error() -> ToolError:
    """Fail closed when company settings shell no longer matches research126."""

    return ToolError(
        code=StableErrorCode.UI_CHANGED,
        message="Billy settings company interface no longer matches the recorded signature.",
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
        headings = page.locator("h1")
        if await headings.count() < 1:
            return False
        heading = headings.first
        if not await heading.is_visible():
            return False
        if (await heading.inner_text()).strip() != _INVOICES_LIST_HEADING:
            return False
        create_action = page.locator(f"text={_INVOICES_CREATE_CTA}")
        return await create_action.count() >= 1 and await create_action.first.is_visible()
    except Exception:
        return False


async def _has_invoices_create_signature(page: LoginPage) -> bool:
    """Verify research153 create form heading + draft chrome + line chrome without clicking."""

    try:
        heading = page.locator("h1")
        if await heading.count() < 1 or not await heading.is_visible():
            return False
        if (await heading.inner_text()).strip() != _INVOICES_CREATE_HEADING:
            return False
        draft = page.locator(f"text={_INVOICES_CREATE_DRAFT_SAVE_CHROME}")
        if await draft.count() < 1 or not await draft.is_visible():
            return False
        line_ok = False
        for marker in _INVOICES_CREATE_LINE_CHROME_MARKERS:
            control = page.locator(f"text={marker}")
            if await control.count() >= 1 and await control.is_visible():
                line_ok = True
                break
        return line_ok
    except Exception:
        return False


async def _invoices_detail_flags(page: LoginPage) -> dict[str, bool]:
    """Non-PII invoice edit-form flags (research169)."""

    flags = {
        "entry_date_control_present": False,
        "contact_control_present": False,
        "line_chrome_present": False,
    }
    try:
        entry = page.locator(
            "input[name='entryDate'], input[name='entry_date'], input[type='date']"
        )
        flags["entry_date_control_present"] = await entry.count() >= 1
        contact_css = page.locator(
            "input[name='contactId'], input[name='contact'], [data-cy*='contact' i]"
        )
        contact_ok = await contact_css.count() >= 1
        if not contact_ok:
            for label in ("Kunde", "Customer", "Kontakt"):
                control = page.locator(f"text={label}")
                if await control.count() >= 1:
                    contact_ok = True
                    break
        # body may show contact name without explicit field name
        if not contact_ok:
            try:
                body = page.locator("body")
                text = (await body.inner_text())[:2000]
                if "Kunde" in text or "Customer" in text:
                    contact_ok = True
            except Exception:
                pass
        flags["contact_control_present"] = contact_ok
        line_ok = False
        for marker in _INVOICES_GET_LINE_CHROME_MARKERS:
            control = page.locator(f"text={marker}")
            if await control.count() >= 1:
                line_ok = True
                break
        if not line_ok:
            line_inputs = page.locator("textarea")
            line_ok = await line_inputs.count() >= 1
        if not line_ok:
            for marker in ("Produkt", "Enhedspris", "Antal", "Tilføj linje"):
                control = page.locator(f"text={marker}")
                if await control.count() >= 1:
                    line_ok = True
                    break
        flags["line_chrome_present"] = line_ok
    except Exception:
        pass
    return flags


async def _has_invoices_detail_signature(page: LoginPage, slug: str) -> bool:
    """Strict invoice detail/edit signature — /invoices/:id/edit with form chrome."""

    del slug
    try:
        if not _is_invoices_edit_url(page.url):
            return False
        flags = await _invoices_detail_flags(page)
        hits = sum(
            1
            for k in (
                "entry_date_control_present",
                "contact_control_present",
                "line_chrome_present",
            )
            if flags.get(k)
        )
        if hits >= 2:
            return True
        # research169 dual: edit path + any line/textarea chrome is enough
        if hits >= 1 and flags.get("line_chrome_present"):
            return True
        # generic form field count on edit surface
        try:
            fields = page.locator("input, textarea, select")
            if await fields.count() >= 3:
                return True
        except Exception:
            pass
        return False
    except Exception:
        return False


async def _invoices_update_form_flags(page: LoginPage) -> dict[str, bool]:
    """Non-PII invoice edit-form flags (research174). Stronger than get detail."""

    flags = {
        "gem_kladde_or_save_chrome_present": False,
        "date_or_payment_terms_chrome_present": False,
        "contact_or_customer_chrome_present": False,
        "inputs_present": False,
    }
    try:
        body_text = ""
        try:
            body_text = (await page.locator("body").inner_text())[:2500]
        except Exception:
            body_text = ""
        flags["gem_kladde_or_save_chrome_present"] = any(
            m in body_text for m in _INVOICES_UPDATE_SAVE_MARKERS
        )
        # Prefer explicit draft save chrome when counting buttons.
        if not flags["gem_kladde_or_save_chrome_present"]:
            try:
                n = await _count_labeled_buttons(page, "Gem som kladde")
                if n >= 1:
                    flags["gem_kladde_or_save_chrome_present"] = True
            except Exception:
                pass
        date_ok = any(
            m in body_text
            for m in ("Dato", "Betalingsfrist", "entryDate", "entry_date", "Fakturanr")
        )
        if not date_ok:
            try:
                entry = page.locator(
                    "input[name='entryDate'], input[name='entry_date'], input[type='date']"
                )
                date_ok = await entry.count() >= 1
            except Exception:
                date_ok = False
        if not date_ok:
            date_ok = any(m in body_text for m in _INVOICES_UPDATE_FIELD_MARKERS)
        flags["date_or_payment_terms_chrome_present"] = date_ok
        contact_ok = bool(re.search(r"Kunde|Customer|Kontakt", body_text, re.I))
        if not contact_ok:
            try:
                contact_css = page.locator(
                    "input[name='contactId'], input[name='contact'], [data-cy*='contact' i]"
                )
                contact_ok = await contact_css.count() >= 1
            except Exception:
                contact_ok = False
        flags["contact_or_customer_chrome_present"] = contact_ok
        try:
            n_inputs = await page.locator("input:visible, textarea:visible, select:visible").count()
        except Exception:
            try:
                n_inputs = await page.locator("input, textarea, select").count()
            except Exception:
                n_inputs = 0
        flags["inputs_present"] = n_inputs >= 3
    except Exception:
        pass
    return flags


async def _has_invoices_update_form_signature(page: LoginPage, slug: str) -> bool:
    """Strict invoice edit form signature — update freeze (research174).

    Requires Gem som kladde / save chrome + form inputs; distinct from get
    detail_open_only which only needs entry_date/contact/line chrome.
    """

    del slug
    try:
        if not _is_invoices_edit_url(page.url):
            return False
        flags = await _invoices_update_form_flags(page)
        if flags.get("gem_kladde_or_save_chrome_present") and flags.get("inputs_present"):
            return True
        if flags.get("gem_kladde_or_save_chrome_present") and flags.get(
            "date_or_payment_terms_chrome_present"
        ):
            return True
        hits = sum(1 for v in flags.values() if v)
        return hits >= 3 and bool(flags.get("gem_kladde_or_save_chrome_present"))
    except Exception:
        return False


async def _count_role_button_exact(page: LoginPage, label: str) -> int:
    """Count role=button only (avoid text= menu items matching Slet after Mere)."""

    live = cast(Any, page)
    get_by_role = getattr(live, "get_by_role", None)
    if callable(get_by_role):
        try:
            exact = cast(
                Any, get_by_role("button", name=re.compile(rf"^{re.escape(label)}$", re.I))
            )
            return int(await exact.count())
        except Exception:
            return 0
    # Unit fakes without get_by_role: do not treat text= menu labels as buttons.
    try:
        return int(await live.locator(f"button:text-is('{label}')").count())
    except Exception:
        return 0


async def _invoices_delete_primary_flags(page: LoginPage) -> dict[str, bool]:
    """Primary edit chrome before Mere — Slet should not be a primary button."""

    try:
        body = re.sub(r"\s+", " ", await page.locator("body").inner_text())[:1800]
    except Exception:
        body = ""
    slet_btn_n = await _count_role_button_exact(page, "Slet")
    mere_btn_n = await _count_labeled_buttons(page, "Mere")
    mere_text = bool(re.search(r"\bMere\b", body))
    return {
        "primary_slet_absent": slet_btn_n == 0,
        "mere_present": mere_btn_n >= 1 or mere_text,
    }


async def _invoices_delete_chrome_flags(page: LoginPage) -> dict[str, bool]:
    """Non-PII delete chrome flags after Mere (research175). Never confirms delete."""

    try:
        body = re.sub(r"\s+", " ", await page.locator("body").inner_text())[:2000]
    except Exception:
        body = ""
    # Exact menu text after Mere (not role=button Slet; research175 dual).
    slet_text = bool(re.search(r"(?<![A-Za-zÆØÅæøå])Slet(?![A-Za-zÆØÅæøå])", body))
    dupliker = bool(re.search(r"Duplik[eé]r", body, re.I))
    mere_label = bool(re.search(r"\bMere\b", body))
    # Mere menu is open when delete/duplicate items appear with Mere chrome.
    mere_open = mere_label and slet_text and (dupliker or "Udskriv" in body)
    return {
        "mere_open": mere_open,
        "slet_text_visible": slet_text,
        "dupliker_visible": dupliker,
        "primary_slet_absent": (await _count_role_button_exact(page, "Slet")) == 0,
    }


async def _has_invoices_delete_chrome_signature(page: LoginPage) -> bool:
    """Strict delete-chrome signature — edit path + Mere menu + Slet text."""

    try:
        if _is_invoices_create_url(page.url):
            return False
        if not _is_invoices_edit_url(page.url):
            return False
        flags = await _invoices_delete_chrome_flags(page)
        return bool(flags.get("mere_open") and flags.get("slet_text_visible"))
    except Exception:
        return False


async def _click_invoices_mere_action(page: LoginPage) -> bool:
    """Click Mere/More on invoice edit without Slet confirm. Research175 delete open."""

    live = cast(Any, page)
    for selector in ("text=Mere", "text=More"):
        try:
            mere = live.locator(selector)
            count = int(await mere.count())
            for index in range(min(count, 6)):
                el = mere.nth(index)
                try:
                    if await el.is_visible():
                        txt = ""
                        try:
                            txt = (await el.inner_text() or "").strip()
                        except Exception:
                            txt = ""
                        if txt and not re.fullmatch(r"Mere|More", txt, re.I):
                            continue
                        await el.click()
                        return True
                except Exception:
                    continue
        except Exception:
            continue
    return False


async def _bills_detail_flags(page: LoginPage) -> dict[str, bool]:
    """Non-PII bill read-detail flags (research170)."""

    flags = {
        "kladde_or_state_chrome_present": False,
        "supplier_chrome_present": False,
        "amount_or_line_chrome_present": False,
    }
    try:
        body_text = ""
        try:
            body_text = (await page.locator("body").inner_text())[:2500]
        except Exception:
            body_text = ""
        flags["kladde_or_state_chrome_present"] = any(
            m in body_text for m in _BILLS_GET_STATE_MARKERS
        )
        supplier_ok = any(m in body_text for m in _BILLS_GET_SUPPLIER_MARKERS)
        if not supplier_ok:
            for marker in _BILLS_GET_SUPPLIER_MARKERS:
                control = page.locator(f"text={marker}")
                if await control.count() >= 1:
                    supplier_ok = True
                    break
        flags["supplier_chrome_present"] = supplier_ok
        amount_ok = any(m in body_text for m in _BILLS_GET_AMOUNT_MARKERS)
        if not amount_ok:
            for marker in _BILLS_GET_AMOUNT_MARKERS:
                control = page.locator(f"text={marker}")
                if await control.count() >= 1:
                    amount_ok = True
                    break
        if not amount_ok:
            amount_ok = await page.locator("textarea").count() >= 1
        flags["amount_or_line_chrome_present"] = amount_ok
    except Exception:
        pass
    return flags


async def _has_bills_detail_signature(page: LoginPage, slug: str) -> bool:
    """Strict bill detail signature — /bills/:id with read chrome (research170)."""

    del slug
    try:
        if not _is_bills_detail_url(page.url):
            return False
        flags = await _bills_detail_flags(page)
        hits = sum(1 for v in flags.values() if v)
        if hits >= 2:
            return True
        # research170 dual: read path + state/amount chrome is enough
        if flags.get("kladde_or_state_chrome_present") and flags.get(
            "amount_or_line_chrome_present"
        ):
            return True
        if flags.get("supplier_chrome_present") and flags.get("amount_or_line_chrome_present"):
            return True
        return False
    except Exception:
        return False


async def _bills_update_form_flags(page: LoginPage) -> dict[str, bool]:
    """Non-PII bill edit-form flags (research172)."""

    flags = {
        "ret_regning_chrome_present": False,
        "opdater_present": False,
        "leverandor_or_dates_chrome_present": False,
        "inputs_present": False,
    }
    try:
        body_text = ""
        try:
            body_text = (await page.locator("body").inner_text())[:2500]
        except Exception:
            body_text = ""
        flags["ret_regning_chrome_present"] = any(m in body_text for m in _BILLS_UPDATE_RET_MARKERS)
        flags["opdater_present"] = any(m in body_text for m in _BILLS_UPDATE_ACTION_MARKERS)
        flags["leverandor_or_dates_chrome_present"] = any(
            m in body_text for m in _BILLS_UPDATE_FIELD_MARKERS
        )
        try:
            n_inputs = await page.locator("input:visible, textarea:visible, select:visible").count()
        except Exception:
            try:
                n_inputs = await page.locator("input, textarea, select").count()
            except Exception:
                n_inputs = 0
        flags["inputs_present"] = n_inputs >= 2
    except Exception:
        pass
    return flags


async def _has_bills_update_form_signature(page: LoginPage, slug: str) -> bool:
    """Strict bill edit form signature — /bills/:id/edit with update chrome (research172)."""

    del slug
    try:
        if not _is_bills_edit_url(page.url):
            return False
        flags = await _bills_update_form_flags(page)
        if flags.get("ret_regning_chrome_present") and flags.get("opdater_present"):
            return True
        if flags.get("opdater_present") and flags.get("leverandor_or_dates_chrome_present"):
            return True
        if flags.get("ret_regning_chrome_present") and flags.get("inputs_present"):
            return True
        hits = sum(1 for v in flags.values() if v)
        return hits >= 3
    except Exception:
        return False


async def _count_labeled_buttons(page: LoginPage, label: str) -> int:
    """Count visible controls matching a Danish action label (role=button or text=)."""

    live = cast(Any, page)
    get_by_role = getattr(live, "get_by_role", None)
    if callable(get_by_role):
        try:
            exact = cast(
                Any, get_by_role("button", name=re.compile(rf"^{re.escape(label)}$", re.I))
            )
            n_exact = int(await exact.count())
            if n_exact > 0:
                return n_exact
            loose = cast(Any, get_by_role("button", name=re.compile(label, re.I)))
            n_loose = int(await loose.count())
            if n_loose > 0:
                return n_loose
        except Exception:
            pass
    try:
        return int(await live.locator(f"text={label}").count())
    except Exception:
        return 0


async def _bills_delete_primary_flags(page: LoginPage) -> dict[str, bool]:
    """Non-PII primary bill edit delete-chrome flags before confirm (research173)."""

    flags = {
        "ret_regning_chrome_present": False,
        "slet_present": False,
    }
    try:
        body_text = ""
        try:
            body_text = (await page.locator("body").inner_text())[:2500]
        except Exception:
            body_text = ""
        flags["ret_regning_chrome_present"] = any(m in body_text for m in _BILLS_UPDATE_RET_MARKERS)
        slet_n = await _count_labeled_buttons(page, "Slet")
        flags["slet_present"] = slet_n >= 1 or (
            "Slet" in body_text and _is_bills_edit_url(page.url)
        )
        if slet_n >= 1:
            flags["slet_present"] = True
    except Exception:
        pass
    return flags


async def _has_bills_delete_primary_signature(page: LoginPage, slug: str) -> bool:
    """Edit path with primary Slet chrome present (research173)."""

    del slug
    try:
        if not _is_bills_edit_url(page.url):
            return False
        flags = await _bills_delete_primary_flags(page)
        if flags.get("slet_present") and flags.get("ret_regning_chrome_present"):
            return True
        return bool(flags.get("slet_present") and await _count_labeled_buttons(page, "Slet") >= 1)
    except Exception:
        return False


async def _bills_delete_confirm_flags(page: LoginPage) -> dict[str, bool]:
    """Confirm overlay flags after primary Slet (research173: Slet≥2 + Annuller)."""

    flags = {
        "slet_present": False,
        "annuller_present": False,
        "confirm_open": False,
    }
    try:
        slet_n = await _count_labeled_buttons(page, "Slet")
        annuller_n = await _count_labeled_buttons(page, "Annuller")
        if annuller_n == 0:
            annuller_n = await _count_labeled_buttons(page, "Cancel")
        flags["slet_present"] = slet_n >= 1
        flags["annuller_present"] = annuller_n >= 1
        # research173 dual: confirm raises Slet button count to 2 with Annuller=1
        flags["confirm_open"] = annuller_n >= 1 and slet_n >= 2
        if not flags["confirm_open"] and annuller_n >= 1 and slet_n >= 1:
            # Accept Annuller + Slet as confirm chrome if role counting under-counts.
            body_text = ""
            try:
                body_text = (await page.locator("body").inner_text())[:2500]
            except Exception:
                body_text = ""
            flags["confirm_open"] = "Annuller" in body_text or "annuller" in body_text.lower()
    except Exception:
        pass
    return flags


async def _click_bills_primary_slet(page: LoginPage) -> bool:
    """Click primary Slet once to open confirm. Never clicks the confirm Slet."""

    live = cast(Any, page)
    for selector in ("text=Slet",):
        try:
            slet = live.locator(selector)
            count = int(await slet.count())
            for index in range(min(count, 4)):
                el = slet.nth(index)
                try:
                    if not await el.is_visible():
                        continue
                    txt = ""
                    try:
                        txt = (await el.inner_text() or "").strip()
                    except Exception:
                        txt = ""
                    if txt and not re.fullmatch(r"Slet", txt, re.I):
                        continue
                    await el.click()
                    return True
                except Exception:
                    continue
        except Exception:
            continue
    get_by_role = getattr(live, "get_by_role", None)
    if callable(get_by_role):
        try:
            btn = cast(Any, get_by_role("button", name=re.compile(r"^Slet$", re.I))).first
            if await btn.count() > 0 and await btn.is_visible():
                await btn.click()
                return True
        except Exception:
            pass
    return False


async def _dismiss_bills_delete_confirm(page: LoginPage) -> bool:
    """Dismiss delete confirm with Annuller (or Escape). Never confirm second Slet."""

    live = cast(Any, page)
    for label in ("Annuller", "Cancel", "Nej", "Luk"):
        try:
            btn = live.locator(f"text={label}")
            count = int(await btn.count())
            for index in range(min(count, 4)):
                el = btn.nth(index)
                try:
                    if not await el.is_visible():
                        continue
                    txt = ""
                    try:
                        txt = (await el.inner_text() or "").strip()
                    except Exception:
                        txt = ""
                    if txt and not re.fullmatch(rf"{label}", txt, re.I):
                        continue
                    await el.click()
                    return True
                except Exception:
                    continue
        except Exception:
            continue
    get_by_role = getattr(live, "get_by_role", None)
    if callable(get_by_role):
        for label in ("Annuller", "Cancel", "Nej", "Luk"):
            try:
                btn = cast(Any, get_by_role("button", name=re.compile(rf"^{label}$", re.I))).first
                if await btn.count() > 0 and await btn.is_visible():
                    await btn.click()
                    return True
            except Exception:
                continue
    keyboard = getattr(live, "keyboard", None)
    if keyboard is not None:
        try:
            await keyboard.press("Escape")
            return True
        except Exception:
            pass
    return False


async def _click_bills_detail_candidate(page: LoginPage, slug: str) -> bool:
    """Click first non-header bill list row or href to open detail/edit."""

    try:
        links = page.locator(f"a[href*='/{slug}/bills/']")
        n_links = await links.count()
        for i in range(min(n_links, 24)):
            link = links.nth(i)
            href = await link.get_attribute("href") or ""
            if href.rstrip("/").endswith("/bills") or "/new" in href:
                continue
            if re.search(rf"/{re.escape(slug)}/bills/[^/?#]+", href):
                await link.click(timeout=5000)
                return True
        rows = page.locator("table tbody tr, [data-cy='table-item'], [role='row'], tr")
        n_rows = await rows.count()
        for i in range(min(n_rows, 40)):
            row = rows.nth(i)
            try:
                text = (await row.inner_text() or "").strip()
            except Exception:
                continue
            if not text or len(text) < 4:
                continue
            if (
                re.search(
                    r"Nr\.|Dato|Forfald|Leverandør|Beløb|Status|Supplier|Bill\s*#",
                    text,
                    re.I,
                )
                and len(text) < 90
            ):
                continue
            if re.search(r"Ingen køb|Opret køb", text, re.I) and len(text) < 80:
                continue
            try:
                await row.click(timeout=5000)
                return True
            except Exception:
                continue
        live_page = cast(Any, page)
        get_by_text = getattr(live_page, "get_by_text", None)
        if callable(get_by_text):
            for needle in (
                "R18671-TMP-BILL",
                "R170B",
                "TMP-BILL",
                "DO-NOT-USE",
            ):
                try:
                    loc = cast(Any, get_by_text(needle, exact=False))
                    if await loc.count() >= 1:
                        await loc.first.click(timeout=4000)
                        return True
                except Exception:
                    continue
        return False
    except Exception:
        return False


async def _click_invoices_detail_candidate(page: LoginPage, slug: str) -> bool:
    """Click first non-header invoice list row or href to open detail/edit."""

    try:
        links = page.locator(f"a[href*='/{slug}/invoices/']")
        n_links = await links.count()
        for i in range(min(n_links, 24)):
            link = links.nth(i)
            href = await link.get_attribute("href") or ""
            if href.rstrip("/").endswith("/invoices") or "/new" in href:
                continue
            if re.search(rf"/{re.escape(slug)}/invoices/[^/?#]+", href):
                await link.click(timeout=5000)
                return True
        rows = page.locator("table tbody tr, [data-cy='table-item'], [role='row'], tr")
        n_rows = await rows.count()
        for i in range(min(n_rows, 40)):
            row = rows.nth(i)
            try:
                text = (await row.inner_text() or "").strip()
            except Exception:
                continue
            if not text or len(text) < 4:
                continue
            if (
                re.search(
                    r"Nr\.|Dato|Forfald|Kunde|Beløb|Status|Invoice\s*#|Customer",
                    text,
                    re.I,
                )
                and len(text) < 90
            ):
                continue
            if re.search(r"Ingen fakturaer|Opret faktura", text, re.I) and len(text) < 80:
                continue
            try:
                await row.click(timeout=5000)
                return True
            except Exception:
                continue
        # research169: text click on disposable line description or draft markers
        live_page = cast(Any, page)
        get_by_text = getattr(live_page, "get_by_text", None)
        if callable(get_by_text):
            for needle in (
                "R18670-TMP-INVOICE",
                "R169I",
                "TMP-INVOICE",
                "DO-NOT-USE",
            ):
                try:
                    loc = cast(Any, get_by_text(needle, exact=False))
                    if int(await loc.count()) >= 1:
                        await loc.first.click(timeout=5000)
                        return True
                except Exception:
                    continue
            # last resort: click a visible "Kladde" cell that is not the overview tile alone
            try:
                loc = cast(Any, get_by_text("Kladde", exact=False))
                n = int(await loc.count())
                for i in range(min(n, 12)):
                    try:
                        await loc.nth(i).click(timeout=3000)
                        return True
                    except Exception:
                        continue
            except Exception:
                pass
        return False
    except Exception:
        return False


async def _has_bills_create_signature(page: LoginPage) -> bool:
    """Verify research154 create form heading + draft chrome + line chrome without clicking.

    Billy may render more than one h1 on /bills/new; use .first so multi-match
    locators do not fail Playwright strict-mode visibility checks.
    """

    try:
        headings = page.locator("h1")
        if await headings.count() < 1:
            return False
        heading = headings.first
        if not await heading.is_visible():
            return False
        if (await heading.inner_text()).strip() != _BILLS_CREATE_HEADING:
            return False
        draft = page.locator(f"text={_BILLS_CREATE_DRAFT_SAVE_CHROME}")
        if await draft.count() < 1 or not await draft.first.is_visible():
            return False
        line_ok = False
        for marker in _BILLS_CREATE_LINE_CHROME_MARKERS:
            control = page.locator(f"text={marker}")
            if await control.count() >= 1 and await control.first.is_visible():
                line_ok = True
                break
        return line_ok
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


def _is_clients_new_soft_url(url: str) -> bool:
    """Reject soft /:org_slug/clients/new chrome-only routes (research160)."""

    try:
        parsed = urlsplit(url)
        port = parsed.port
    except ValueError:
        return False
    path = parsed.path or ""
    return (
        parsed.scheme == "https"
        and parsed.hostname == "mit.billy.dk"
        and port in {None, 443}
        and parsed.username is None
        and parsed.password is None
        and bool(re.match(r"^/[^/]+/clients/new/?$", path))
    )


async def _has_clients_list_heading(page: LoginPage) -> bool:
    """True when the clients list h1 is Kunder."""

    try:
        heading = page.locator("h1")
        if await heading.count() < 1 or not await heading.is_visible():
            return False
        return (await heading.inner_text()).strip() == _CLIENTS_LIST_HEADING
    except Exception:
        return False


async def _click_clients_create_cta(page: LoginPage) -> bool:
    """Observe-only click of research160 text CTA Opret kontakt. Never submits the form."""

    try:
        cta = page.locator(f"text={_CLIENTS_CREATE_CTA}")
        if await cta.count() < 1:
            return False
        target = cta.first
        if not await target.is_visible():
            return False
        await target.click()
        return True
    except Exception:
        return False


async def _clients_create_form_field_flags(page: LoginPage) -> dict[str, bool]:
    """Non-PII field presence flags for the clients create dialog (research160)."""

    name_visible = False
    registration_present = False
    address_or_person = False
    try:
        name = page.locator("input[name='name']")
        if await name.count() >= 1 and await name.first.is_visible():
            name_visible = True
    except Exception:
        pass
    try:
        reg = page.locator("input[name='registrationNo']")
        if await reg.count() >= 1:
            registration_present = True
    except Exception:
        pass
    for selector in (
        "input[name='street']",
        "input[name='person_email']",
        "input[name='person_firstName']",
        "input[name='person_lastName']",
    ):
        try:
            field = page.locator(selector)
            if await field.count() >= 1:
                address_or_person = True
                break
        except Exception:
            continue
    return {
        "name_field_visible": name_visible,
        "registration_no_field_present": registration_present,
        "address_or_person_fields_present": address_or_person,
    }


async def _has_clients_create_form_signature(page: LoginPage) -> bool:
    """Verify research160 create dialog form signature without submitting."""

    try:
        if not await _has_clients_list_heading(page):
            return False
        flags = await _clients_create_form_field_flags(page)
        return (
            flags["name_field_visible"]
            and flags["registration_no_field_present"]
            and flags["address_or_person_fields_present"]
        )
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


def _is_clients_detail_url(url: str) -> bool:
    """Accept mit.billy.dk /:org_slug/contacts/:id/customer|supplier profile paths."""

    try:
        parsed = urlsplit(url)
        port = parsed.port
    except ValueError:
        return False
    if not (
        parsed.scheme == "https"
        and parsed.hostname == "mit.billy.dk"
        and port in {None, 443}
        and parsed.username is None
        and parsed.password is None
    ):
        return False
    return bool(_CLIENTS_DETAIL_PATH.match(parsed.path or ""))


def _is_clients_header_row_text(text: str) -> bool:
    """Reject table header rows (research162 false-positive trap)."""

    compact = re.sub(r"\s+", " ", text).strip()
    if not compact or len(compact) < 2:
        return True
    labels = re.split(r"[\n\t|/]+", compact)
    hits = sum(1 for lab in labels if _CLIENTS_HEADER_ROW_RE.search(lab.strip()))
    if hits >= 2:
        return True
    if _CLIENTS_HEADER_ROW_RE.search(compact) and len(compact) < 48:
        return True
    return False


async def _clients_detail_flags(page: LoginPage) -> dict[str, bool]:
    """Non-PII detail flags for customer profile overview (research164 execute)."""

    contact_name_visible = False
    edit_action_visible = False
    try:
        body = re.sub(r"\s+", " ", await page.locator("body").inner_text())[:1200]
    except Exception:
        body = ""
    # Profile header uses "Name (Kunde)" / "Name (Leverandør)" without name input.
    if re.search(r"\(\s*(Kunde|Leverandør|Customer|Supplier)\s*\)", body, re.I):
        contact_name_visible = True
    if re.search(r"\b(Ret|Edit)\b", body):
        edit_action_visible = True
    try:
        ret = page.locator("text=Ret")
        if await ret.count() >= 1 and await ret.first.is_visible():
            edit_action_visible = True
    except Exception:
        pass
    return {
        "contact_name_visible": contact_name_visible,
        "edit_action_visible": edit_action_visible,
    }


async def _has_clients_detail_signature(page: LoginPage, slug: str) -> bool:
    """Strict clients detail signature — contacts/:id/customer profile overview."""

    del slug
    try:
        if _is_clients_new_soft_url(page.url):
            return False
        if not _is_clients_detail_url(page.url):
            return False
        flags = await _clients_detail_flags(page)
        return flags["contact_name_visible"] and flags["edit_action_visible"]
    except Exception:
        return False


async def _click_clients_detail_candidate(page: LoginPage, slug: str) -> bool:
    """Click first non-header client row or contacts profile link. Never create CTA or Gem."""

    # Prefer anchors to contact profile
    try:
        links = page.locator(f"a[href*='/{slug}/contacts/'], a[href*='/{slug}/clients/']")
        count = await links.count()
        for index in range(min(count, 20)):
            link = links.nth(index)
            try:
                if not await link.is_visible():
                    continue
                href = await link.get_attribute("href") or ""
                if href.rstrip("/").endswith("/clients") or "/new" in href or "import" in href:
                    continue
                if not re.search(
                    rf"/{re.escape(slug)}/(contacts|clients)/[^/?#]+",
                    href,
                ):
                    continue
                text = (await link.inner_text()).strip()
                if _is_clients_header_row_text(text):
                    continue
                await link.click()
                return True
            except Exception:
                continue
    except Exception:
        pass

    # Table / role rows (Billy clients list often has no id anchors)
    try:
        rows = page.locator("table tbody tr, [role='row']")
        count = await rows.count()
        for index in range(min(count, 25)):
            row = rows.nth(index)
            try:
                if not await row.is_visible():
                    continue
                text = (await row.inner_text()).strip()
                if _is_clients_header_row_text(text):
                    continue
                if len(text) < 2:
                    continue
                await row.click()
                return True
            except Exception:
                continue
    except Exception:
        pass
    return False


async def _click_clients_ret_action(page: LoginPage) -> bool:
    """Click Ret/Edit on contact detail without Gem/Slet. Research166 update open."""

    live = cast(Any, page)
    for selector in ("text=Ret", "text=Edit"):
        try:
            ret = live.locator(selector)
            count = int(await ret.count())
            for index in range(min(count, 6)):
                el = ret.nth(index)
                try:
                    if await el.is_visible():
                        await el.click()
                        return True
                except Exception:
                    continue
        except Exception:
            continue
    return False


async def _clients_update_form_field_flags(page: LoginPage) -> dict[str, Any]:
    """Non-PII edit-form flags after Ret (research166). Never reads PII into return."""

    live = cast(Any, page)
    name_visible = False
    name_has_value = False
    address_or_person = False
    country_present = False
    named_content = 0
    try:
        name = live.locator("input[name='name']")
        if await name.count() >= 1 and await name.first.is_visible():
            name_visible = True
            try:
                val = str(await name.first.input_value()).strip()
                name_has_value = bool(val)
            except Exception:
                name_has_value = False
    except Exception:
        pass
    for selector in (
        "input[name='street']",
        "input[name='city']",
        "input[name='zipcode']",
        "input[name='phone']",
        "input[name='person_email']",
        "input[name='person_firstName']",
        "input[name='person_lastName']",
    ):
        try:
            field = live.locator(selector)
            if await field.count() >= 1 and await field.first.is_visible():
                address_or_person = True
                named_content += 1
        except Exception:
            continue
    try:
        country = live.locator("select[name='country'], input[name='country']")
        if await country.count() >= 1 and await country.first.is_visible():
            country_present = True
            named_content += 1
    except Exception:
        pass
    if name_visible:
        named_content += 1
    return {
        "name_field_visible": name_visible,
        "name_field_has_value": name_has_value,
        "address_or_person_fields_present": address_or_person,
        "country_field_present": country_present,
        "named_content_count": named_content,
    }


async def _has_clients_update_form_signature(page: LoginPage) -> bool:
    """Strict edit-form signature after Ret — path + valued name + content floor."""

    try:
        if _is_clients_new_soft_url(page.url):
            return False
        if not _is_clients_detail_url(page.url):
            return False
        flags = await _clients_update_form_field_flags(page)
        content_count = int(flags.get("named_content_count") or 0)
        return bool(
            flags.get("name_field_visible")
            and flags.get("name_field_has_value")
            and content_count >= 3
            and (
                flags.get("address_or_person_fields_present") or flags.get("country_field_present")
            )
        )
    except Exception:
        return False


async def _clients_delete_primary_flags(page: LoginPage) -> dict[str, bool]:
    """Primary detail chrome before Mere — Slet should not be a primary control."""

    try:
        body = re.sub(r"\s+", " ", await page.locator("body").inner_text())[:1500]
    except Exception:
        body = ""
    # Primary chrome research167: Opret/Ret/Mere without Slet kontakt label.
    slet_kontakt = bool(re.search(r"Slet kontakt", body, re.I))
    # Standalone primary Slet button text without "Slet kontakt" menu wording.
    standalone_slet = bool(re.search(r"\bSlet\b", body)) and not slet_kontakt
    return {
        "primary_slet_absent": not slet_kontakt and not standalone_slet,
        "slet_kontakt_visible": slet_kontakt,
    }


async def _clients_delete_chrome_flags(page: LoginPage) -> dict[str, bool]:
    """Non-PII delete chrome flags after Mere (research167). Never confirms delete."""

    try:
        body = re.sub(r"\s+", " ", await page.locator("body").inner_text())[:1800]
    except Exception:
        body = ""
    slet_kontakt = bool(re.search(r"Slet kontakt", body, re.I))
    arkiver = bool(re.search(r"Arkiv[eé]r kontakt", body, re.I))
    mere_label = bool(re.search(r"\bMere\b", body))
    # Mere is open when delete/archive menu items are visible on detail path.
    mere_open = slet_kontakt or arkiver
    return {
        "mere_open": mere_open and mere_label,
        "slet_kontakt_visible": slet_kontakt,
        "arkiver_kontakt_visible": arkiver,
        # After Mere, primary chrome assessment is historical; default true when
        # delete lives under Mere (Slet kontakt wording, not a lone primary Slet).
        "primary_slet_absent": slet_kontakt,
    }


async def _has_clients_delete_chrome_signature(page: LoginPage) -> bool:
    """Strict delete-chrome signature — detail path + Mere menu + Slet kontakt."""

    try:
        if _is_clients_new_soft_url(page.url):
            return False
        if not _is_clients_detail_url(page.url):
            return False
        flags = await _clients_delete_chrome_flags(page)
        return bool(flags.get("mere_open") and flags.get("slet_kontakt_visible"))
    except Exception:
        return False


async def _click_clients_mere_action(page: LoginPage) -> bool:
    """Click Mere/More on contact detail without Slet confirm. Research167 delete open."""

    live = cast(Any, page)
    for selector in ("text=Mere", "text=More"):
        try:
            mere = live.locator(selector)
            count = int(await mere.count())
            for index in range(min(count, 6)):
                el = mere.nth(index)
                try:
                    if await el.is_visible():
                        txt = ""
                        try:
                            txt = (await el.inner_text() or "").strip()
                        except Exception:
                            txt = ""
                        # Avoid menu items that embed "Mere" inside longer labels.
                        if txt and not re.fullmatch(r"Mere|More", txt, re.I):
                            continue
                        await el.click()
                        return True
                except Exception:
                    continue
        except Exception:
            continue
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


def _is_suppliers_new_soft_url(url: str) -> bool:
    """Reject soft /:org_slug/suppliers/new as create-form success (research161)."""

    try:
        parsed = urlsplit(url)
        if parsed.scheme not in {"http", "https"}:
            return False
        if parsed.hostname not in {"mit.billy.dk", "www.mit.billy.dk"}:
            return False
        path = (parsed.path or "").rstrip("/")
        return bool(re.match(r"^/[^/]+/suppliers/new$", path))
    except Exception:
        return False


async def _has_suppliers_list_heading(page: LoginPage) -> bool:
    """True when suppliers list h1 Leverandører is visible."""

    try:
        heading = page.locator("h1")
        if await heading.count() < 1 or not await heading.is_visible():
            return False
        return (await heading.inner_text()).strip() == _SUPPLIERS_LIST_HEADING
    except Exception:
        return False


async def _click_suppliers_create_cta(page: LoginPage) -> bool:
    """Observe-only click of research161 text CTA Opret kontakt. Never submits the form."""

    try:
        cta = page.locator(f"text={_SUPPLIERS_CREATE_CTA}")
        if await cta.count() < 1:
            return False
        target = cta.first
        if not await target.is_visible():
            return False
        await target.click()
        return True
    except Exception:
        return False


async def _suppliers_create_form_field_flags(page: LoginPage) -> dict[str, bool]:
    """Non-PII field presence flags for the suppliers create dialog (research161)."""

    name_visible = False
    registration_present = False
    address_or_person = False
    try:
        name = page.locator("input[name='name']")
        if await name.count() >= 1 and await name.first.is_visible():
            name_visible = True
    except Exception:
        pass
    try:
        reg = page.locator("input[name='registrationNo']")
        if await reg.count() >= 1:
            registration_present = True
    except Exception:
        pass
    for selector in (
        "input[name='street']",
        "input[name='person_email']",
        "input[name='person_firstName']",
        "input[name='person_lastName']",
    ):
        try:
            field = page.locator(selector)
            if await field.count() >= 1:
                address_or_person = True
                break
        except Exception:
            continue
    return {
        "name_field_visible": name_visible,
        "registration_no_field_present": registration_present,
        "address_or_person_fields_present": address_or_person,
    }


async def _has_suppliers_create_form_signature(page: LoginPage) -> bool:
    """Verify research161 create dialog form signature without submitting."""

    try:
        if not await _has_suppliers_list_heading(page):
            return False
        flags = await _suppliers_create_form_field_flags(page)
        return (
            flags["name_field_visible"]
            and flags["registration_no_field_present"]
            and flags["address_or_person_fields_present"]
        )
    except Exception:
        return False


async def _click_products_create_cta(page: LoginPage) -> bool:
    """Observe-only click of research163 CTA Opret produkt. Never submits the form."""

    try:
        cta = page.locator(f"text={_PRODUCTS_CREATE_CTA}")
        if await cta.count() < 1:
            return False
        target = cta.first
        if not await target.is_visible():
            return False
        await target.click()
        return True
    except Exception:
        return False


async def _products_create_form_field_flags(page: LoginPage) -> dict[str, bool]:
    """Non-PII field presence flags for the inventory product create form (research163)."""

    name_visible = False
    account_present = False
    ruleset_present = False
    unit_price_present = False
    try:
        name = page.locator("input[name='name']")
        if await name.count() >= 1 and await name.first.is_visible():
            name_visible = True
    except Exception:
        pass
    try:
        account = page.locator("input[name='account']")
        if await account.count() >= 1:
            account_present = True
    except Exception:
        pass
    try:
        ruleset = page.locator("input[name='salesTaxRuleset']")
        if await ruleset.count() >= 1:
            ruleset_present = True
    except Exception:
        pass
    try:
        unit_price = page.locator("input[name='unitPrice']")
        if await unit_price.count() >= 1:
            unit_price_present = True
    except Exception:
        pass
    return {
        "name_field_visible": name_visible,
        "account_field_present": account_present,
        "sales_tax_ruleset_field_present": ruleset_present,
        "unit_price_field_present": unit_price_present,
    }


async def _has_products_create_form_signature(page: LoginPage) -> bool:
    """Verify research163 product create form signature without submitting."""

    try:
        if not await _has_inventory_heading(page):
            return False
        flags = await _products_create_form_field_flags(page)
        if not flags["name_field_visible"]:
            return False
        present = sum(
            1
            for key in (
                "account_field_present",
                "sales_tax_ruleset_field_present",
                "unit_price_field_present",
            )
            if flags[key]
        )
        return present >= 2
    except Exception:
        return False


async def _has_inventory_heading(page: LoginPage) -> bool:
    """True when the inventory Lagermodul h1 is visible."""

    try:
        heading = page.locator("h1")
        if await heading.count() < 1:
            return False
        first = heading.first
        if not await first.is_visible():
            return False
        return (await first.inner_text()).strip() == _INVENTORY_HEADING
    except Exception:
        return False


def _is_products_new_soft_url(url: str) -> bool:
    """Return True for soft /products/new chrome-only paths (not success)."""

    try:
        parsed = urlsplit(url)
        port = parsed.port
    except ValueError:
        return False
    path = parsed.path or ""
    return (
        parsed.scheme == "https"
        and parsed.hostname == "mit.billy.dk"
        and port in {None, 443}
        and parsed.username is None
        and parsed.password is None
        and path.rstrip("/").endswith("/products/new")
    )


def _ui_products_create_changed_error() -> ToolError:
    """Fail closed when the products create form no longer matches research163."""

    return ToolError(
        code=StableErrorCode.UI_CHANGED,
        message="Billy products create form interface no longer matches the recorded signature.",
    )


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


async def _has_inventory_signature(page: LoginPage) -> bool:
    """Verify research125 Lagermodul heading without create CTA clicks.

    Never click Opret primo / Opret produkt / Opret status. Soft aliases and
    products list (Produkter) are not success paths for this tool.
    """

    try:
        heading = page.locator("h1")
        if await heading.count() < 1:
            return False
        first = heading.first
        if not await first.is_visible():
            return False
        return (await first.inner_text()).strip() == _INVENTORY_HEADING
    except Exception:
        return False


async def _has_inventory_create_cta_markers(page: LoginPage) -> bool:
    """Observe Lagermodul create CTA text only; never click."""

    try:
        for label in _INVENTORY_CREATE_CTAS:
            control = page.locator(f"text={label}")
            if await control.count() >= 1 and await control.is_visible():
                return True
        return False
    except Exception:
        return False


async def _has_settings_company_signature(page: LoginPage) -> bool:
    """Verify research126 Indstillinger + company panel markers; never click writes.

    Requires h1 Indstillinger and both Navn og adresse + Kontaktinformation.
    Soft aliases and other settings panels are not success for this tool.
    """

    try:
        heading = page.locator("h1")
        if await heading.count() < 1:
            return False
        first = heading.first
        if not await first.is_visible():
            return False
        if (await first.inner_text()).strip() != _SETTINGS_COMPANY_HEADING:
            return False
        for label in _SETTINGS_COMPANY_PANEL_MARKERS:
            control = page.locator(f"text={label}")
            if await control.count() < 1 or not await control.is_visible():
                return False
        return True
    except Exception:
        return False


async def _has_settings_accounting_signature(page: LoginPage) -> bool:
    """Verify research127 Indstillinger + Regnskab panel markers; never click writes.

    Requires h1 Indstillinger and Regnskab + Køb + Kontoplan. Rejects company
    default panel (Navn og adresse + Kontaktinformation both present as panel).
    Soft aliases and other settings panels are not success for this tool.
    Use .first for multi-match rail/body labels (Regnskab/Køb count > 1).
    """

    try:
        heading = page.locator("h1")
        if await heading.count() < 1:
            return False
        first = heading.first
        if not await first.is_visible():
            return False
        if (await first.inner_text()).strip() != _SETTINGS_ACCOUNTING_HEADING:
            return False
        for label in _SETTINGS_ACCOUNTING_PANEL_MARKERS:
            control = page.locator(f"text={label}")
            if await control.count() < 1:
                return False
            if not await control.first.is_visible():
                return False
        # Reject company default panel (rail alone may show Regnskab label).
        company_hits = 0
        for label in _SETTINGS_COMPANY_PANEL_MARKERS:
            control = page.locator(f"text={label}")
            if await control.count() >= 1 and await control.first.is_visible():
                company_hits += 1
        if company_hits >= len(_SETTINGS_COMPANY_PANEL_MARKERS):
            return False
        return True
    except Exception:
        return False


async def _has_settings_invoicing_signature(page: LoginPage) -> bool:
    """Verify research128 Indstillinger + Faktura panel markers; never click writes.

    Requires h1 Indstillinger, Faktura + Produkter, and Betalingsmetoder or
    Standard fakturalogo. Rejects company default panel and accounting Regnskab
    panel (Regnskab+Køb+Kontoplan). Soft aliases and other settings panels are
    not success for this tool. Use .first for multi-match rail/body labels
    (Faktura appears on the left rail of other panels).
    """

    try:
        heading = page.locator("h1")
        if await heading.count() < 1:
            return False
        first = heading.first
        if not await first.is_visible():
            return False
        if (await first.inner_text()).strip() != _SETTINGS_INVOICING_HEADING:
            return False
        for label in _SETTINGS_INVOICING_REQUIRED_MARKERS:
            control = page.locator(f"text={label}")
            if await control.count() < 1:
                return False
            if not await control.first.is_visible():
                return False
        optional_ok = False
        for label in _SETTINGS_INVOICING_OPTIONAL_MARKERS:
            control = page.locator(f"text={label}")
            if await control.count() >= 1 and await control.first.is_visible():
                optional_ok = True
                break
        if not optional_ok:
            return False
        # Reject company default panel (rail alone may show Faktura label).
        company_hits = 0
        for label in _SETTINGS_COMPANY_PANEL_MARKERS:
            control = page.locator(f"text={label}")
            if await control.count() >= 1 and await control.first.is_visible():
                company_hits += 1
        if company_hits >= len(_SETTINGS_COMPANY_PANEL_MARKERS):
            return False
        # Reject accounting Regnskab panel when its required trio is active.
        accounting_hits = 0
        for label in _SETTINGS_ACCOUNTING_PANEL_MARKERS:
            control = page.locator(f"text={label}")
            if await control.count() >= 1 and await control.first.is_visible():
                accounting_hits += 1
        if accounting_hits >= len(_SETTINGS_ACCOUNTING_PANEL_MARKERS):
            return False
        return True
    except Exception:
        return False


async def _click_settings_side_nav_label(page: LoginPage, label: str) -> bool:
    """Observe-only click of an Indstillinger side-nav label. Never write CTAs."""

    if (
        label in _SETTINGS_USER_WRITE_CTA_LABELS
        or label in _SETTINGS_USER_ORGANIZATIONS_WRITE_CTA_LABELS
        or label in _SETTINGS_VAT_WRITE_CTA_LABELS
        or label in _SETTINGS_USERS_WRITE_CTA_LABELS
        or label in _SETTINGS_ACCESS_TOKEN_WRITE_CTA_LABELS
        or label in _SETTINGS_SUBSCRIPTION_WRITE_CTA_LABELS
        or label.startswith(
            (
                "Gem",
                "Opret",
                "Slet",
                "Tilføj",
                "Upload",
                "Inviter",
                "Invitér",
                "Overdrag",
                "Opgrader",
                "Save",
                "Betal",
                "Køb",
                "Skift",
                "Annuller",
                "Opsig",
            )
        )
    ):
        return False
    try:
        control = page.locator(f"text={label}")
        if await control.count() < 1:
            return False
        first = control.first
        if not await first.is_visible():
            return False
        await first.click()
        return True
    except Exception:
        return False


async def _has_settings_user_signature(page: LoginPage) -> bool:
    """Verify research129 Indstillinger + Profil panel markers; never click writes.

    Requires h1 Indstillinger and Profil + Billede + Sprog og tema + Skift
    adgangskode. Rejects company default, accounting Regnskab, and invoicing
    Faktura panels. Soft seeds and other settings panels are not success.
    Use .first for multi-match rail/body labels (Profil may appear twice).
    """

    try:
        heading = page.locator("h1")
        if await heading.count() < 1:
            return False
        first = heading.first
        if not await first.is_visible():
            return False
        if (await first.inner_text()).strip() != _SETTINGS_USER_HEADING:
            return False
        for label in _SETTINGS_USER_PANEL_MARKERS:
            control = page.locator(f"text={label}")
            if await control.count() < 1:
                return False
            if not await control.first.is_visible():
                return False
        # Reject company default panel.
        company_hits = 0
        for label in _SETTINGS_COMPANY_PANEL_MARKERS:
            control = page.locator(f"text={label}")
            if await control.count() >= 1 and await control.first.is_visible():
                company_hits += 1
        if company_hits >= len(_SETTINGS_COMPANY_PANEL_MARKERS):
            return False
        # Reject accounting Regnskab panel.
        accounting_hits = 0
        for label in _SETTINGS_ACCOUNTING_PANEL_MARKERS:
            control = page.locator(f"text={label}")
            if await control.count() >= 1 and await control.first.is_visible():
                accounting_hits += 1
        if accounting_hits >= len(_SETTINGS_ACCOUNTING_PANEL_MARKERS):
            return False
        # Reject invoicing Faktura panel when required markers + optional present.
        invoicing_required = 0
        for label in _SETTINGS_INVOICING_REQUIRED_MARKERS:
            control = page.locator(f"text={label}")
            if await control.count() >= 1 and await control.first.is_visible():
                invoicing_required += 1
        if invoicing_required >= len(_SETTINGS_INVOICING_REQUIRED_MARKERS):
            optional_ok = False
            for label in _SETTINGS_INVOICING_OPTIONAL_MARKERS:
                control = page.locator(f"text={label}")
                if await control.count() >= 1 and await control.first.is_visible():
                    optional_ok = True
                    break
            if optional_ok:
                return False
        return True
    except Exception:
        return False


def _is_settings_vat_url(url: str) -> bool:
    """Return True when the URL is the bare settings hub leaf (Momssatser path)."""

    return _is_settings_company_url(url)


def _ui_settings_vat_changed_error() -> ToolError:
    """Stable UI_CHANGED for settings VAT (Momssatser) shell classification failures."""

    return ToolError(
        code=StableErrorCode.UI_CHANGED,
        message="Billy settings VAT shell could not be classified.",
    )


async def _has_settings_vat_signature(page: LoginPage) -> bool:
    """Verify research130 Indstillinger + Momssatser panel markers; never click writes.

    Requires h1 Indstillinger and Regelsæt + Satser for salg + Satser for køb.
    Rejects company default, accounting Regnskab, invoicing Faktura, and user
    Profil panels. Soft seeds and other settings panels are not success.
    Use .first for multi-match rail/body labels.
    """

    try:
        heading = page.locator("h1")
        if await heading.count() < 1:
            return False
        first = heading.first
        if not await first.is_visible():
            return False
        if (await first.inner_text()).strip() != _SETTINGS_VAT_HEADING:
            return False
        for label in _SETTINGS_VAT_PANEL_MARKERS:
            control = page.locator(f"text={label}")
            if await control.count() < 1:
                return False
            if not await control.first.is_visible():
                return False
        # Reject company default panel.
        company_hits = 0
        for label in _SETTINGS_COMPANY_PANEL_MARKERS:
            control = page.locator(f"text={label}")
            if await control.count() >= 1 and await control.first.is_visible():
                company_hits += 1
        if company_hits >= len(_SETTINGS_COMPANY_PANEL_MARKERS):
            return False
        # Reject accounting Regnskab panel.
        accounting_hits = 0
        for label in _SETTINGS_ACCOUNTING_PANEL_MARKERS:
            control = page.locator(f"text={label}")
            if await control.count() >= 1 and await control.first.is_visible():
                accounting_hits += 1
        if accounting_hits >= len(_SETTINGS_ACCOUNTING_PANEL_MARKERS):
            return False
        # Reject invoicing Faktura panel when required markers + optional present.
        invoicing_required = 0
        for label in _SETTINGS_INVOICING_REQUIRED_MARKERS:
            control = page.locator(f"text={label}")
            if await control.count() >= 1 and await control.first.is_visible():
                invoicing_required += 1
        if invoicing_required >= len(_SETTINGS_INVOICING_REQUIRED_MARKERS):
            optional_ok = False
            for label in _SETTINGS_INVOICING_OPTIONAL_MARKERS:
                control = page.locator(f"text={label}")
                if await control.count() >= 1 and await control.first.is_visible():
                    optional_ok = True
                    break
            if optional_ok:
                return False
        # Reject user Profil panel when full marker set is active.
        user_hits = 0
        for label in _SETTINGS_USER_PANEL_MARKERS:
            control = page.locator(f"text={label}")
            if await control.count() >= 1 and await control.first.is_visible():
                user_hits += 1
        if user_hits >= len(_SETTINGS_USER_PANEL_MARKERS):
            return False
        return True
    except Exception:
        return False


def _is_settings_access_token_url(url: str) -> bool:
    """Return True when the URL is the bare settings hub leaf (Adgangsnøgler path)."""

    return _is_settings_company_url(url)


def _ui_settings_access_token_changed_error() -> ToolError:
    """Stable UI_CHANGED for settings access-token (Adgangsnøgler) shell failures."""

    return ToolError(
        code=StableErrorCode.UI_CHANGED,
        message="Billy settings access token shell could not be classified.",
    )


async def _has_settings_access_token_signature(page: LoginPage) -> bool:
    """Verify research132 Indstillinger + Adgangsnøgler panel markers.

    Requires h1 Indstillinger and Adgangsnøgler. Rejects company default,
    accounting Regnskab, invoicing Faktura, user Profil, VAT Momssatser,
    users Brugere, and beta panels. Soft seeds and other settings panels
    are not success. Use .first for multi-match rail/body labels
    (Adgangsnøgler may appear as side-nav + panel h2).
    """

    try:
        heading = page.locator("h1")
        if await heading.count() < 1:
            return False
        first = heading.first
        if not await first.is_visible():
            return False
        if (await first.inner_text()).strip() != _SETTINGS_ACCESS_TOKEN_HEADING:
            return False
        for label in _SETTINGS_ACCESS_TOKEN_PANEL_MARKERS:
            control = page.locator(f"text={label}")
            if await control.count() < 1:
                return False
            if not await control.first.is_visible():
                return False
        company_hits = 0
        for label in _SETTINGS_COMPANY_PANEL_MARKERS:
            control = page.locator(f"text={label}")
            if await control.count() >= 1 and await control.first.is_visible():
                company_hits += 1
        if company_hits >= len(_SETTINGS_COMPANY_PANEL_MARKERS):
            return False
        accounting_hits = 0
        for label in _SETTINGS_ACCOUNTING_PANEL_MARKERS:
            control = page.locator(f"text={label}")
            if await control.count() >= 1 and await control.first.is_visible():
                accounting_hits += 1
        if accounting_hits >= len(_SETTINGS_ACCOUNTING_PANEL_MARKERS):
            return False
        invoicing_required = 0
        for label in _SETTINGS_INVOICING_REQUIRED_MARKERS:
            control = page.locator(f"text={label}")
            if await control.count() >= 1 and await control.first.is_visible():
                invoicing_required += 1
        if invoicing_required >= len(_SETTINGS_INVOICING_REQUIRED_MARKERS):
            optional_ok = False
            for label in _SETTINGS_INVOICING_OPTIONAL_MARKERS:
                control = page.locator(f"text={label}")
                if await control.count() >= 1 and await control.first.is_visible():
                    optional_ok = True
                    break
            if optional_ok:
                return False
        user_hits = 0
        for label in _SETTINGS_USER_PANEL_MARKERS:
            control = page.locator(f"text={label}")
            if await control.count() >= 1 and await control.first.is_visible():
                user_hits += 1
        if user_hits >= len(_SETTINGS_USER_PANEL_MARKERS):
            return False
        vat_hits = 0
        for label in _SETTINGS_VAT_PANEL_MARKERS:
            control = page.locator(f"text={label}")
            if await control.count() >= 1 and await control.first.is_visible():
                vat_hits += 1
        if vat_hits >= len(_SETTINGS_VAT_PANEL_MARKERS):
            return False
        users_hits = 0
        for label in _SETTINGS_USERS_PANEL_MARKERS:
            control = page.locator(f"text={label}")
            if await control.count() >= 1 and await control.first.is_visible():
                users_hits += 1
        if users_hits >= len(_SETTINGS_USERS_PANEL_MARKERS):
            return False
        beta_hits = 0
        for label in _SETTINGS_BETA_PANEL_MARKERS:
            control = page.locator(f"text={label}")
            if await control.count() >= 1 and await control.first.is_visible():
                beta_hits += 1
        if beta_hits >= len(_SETTINGS_BETA_PANEL_MARKERS):
            return False
        return True
    except Exception:
        return False


def _is_settings_beta_url(url: str) -> bool:
    """Return True when the URL is the bare settings hub leaf (Betas path)."""

    return _is_settings_company_url(url)


def _ui_settings_beta_changed_error() -> ToolError:
    """Stable UI_CHANGED for settings beta (Betas) shell failures."""

    return ToolError(
        code=StableErrorCode.UI_CHANGED,
        message="Billy settings beta shell could not be classified.",
    )


async def _has_settings_beta_signature(page: LoginPage) -> bool:
    """Verify research133 Indstillinger + Betas + Tidlig adgang panel markers.

    Requires h1 Indstillinger and Betas + Tidlig adgang. Rejects company
    default, accounting Regnskab, invoicing Faktura, user Profil, VAT
    Momssatser, users Brugere, and access-token Adgangsnøgler panels. Soft
    seeds and other settings panels are not success. Use .first for
    multi-match rail/body labels (Betas may appear as side-nav + panel h2).
    """

    try:
        heading = page.locator("h1")
        if await heading.count() < 1:
            return False
        first = heading.first
        if not await first.is_visible():
            return False
        if (await first.inner_text()).strip() != _SETTINGS_BETA_HEADING:
            return False
        for label in _SETTINGS_BETA_PANEL_MARKERS:
            control = page.locator(f"text={label}")
            if await control.count() < 1:
                return False
            if not await control.first.is_visible():
                return False
        company_hits = 0
        for label in _SETTINGS_COMPANY_PANEL_MARKERS:
            control = page.locator(f"text={label}")
            if await control.count() >= 1 and await control.first.is_visible():
                company_hits += 1
        if company_hits >= len(_SETTINGS_COMPANY_PANEL_MARKERS):
            return False
        accounting_hits = 0
        for label in _SETTINGS_ACCOUNTING_PANEL_MARKERS:
            control = page.locator(f"text={label}")
            if await control.count() >= 1 and await control.first.is_visible():
                accounting_hits += 1
        if accounting_hits >= len(_SETTINGS_ACCOUNTING_PANEL_MARKERS):
            return False
        invoicing_required = 0
        for label in _SETTINGS_INVOICING_REQUIRED_MARKERS:
            control = page.locator(f"text={label}")
            if await control.count() >= 1 and await control.first.is_visible():
                invoicing_required += 1
        if invoicing_required >= len(_SETTINGS_INVOICING_REQUIRED_MARKERS):
            optional_ok = False
            for label in _SETTINGS_INVOICING_OPTIONAL_MARKERS:
                control = page.locator(f"text={label}")
                if await control.count() >= 1 and await control.first.is_visible():
                    optional_ok = True
                    break
            if optional_ok:
                return False
        user_hits = 0
        for label in _SETTINGS_USER_PANEL_MARKERS:
            control = page.locator(f"text={label}")
            if await control.count() >= 1 and await control.first.is_visible():
                user_hits += 1
        if user_hits >= len(_SETTINGS_USER_PANEL_MARKERS):
            return False
        vat_hits = 0
        for label in _SETTINGS_VAT_PANEL_MARKERS:
            control = page.locator(f"text={label}")
            if await control.count() >= 1 and await control.first.is_visible():
                vat_hits += 1
        if vat_hits >= len(_SETTINGS_VAT_PANEL_MARKERS):
            return False
        users_hits = 0
        for label in _SETTINGS_USERS_PANEL_MARKERS:
            control = page.locator(f"text={label}")
            if await control.count() >= 1 and await control.first.is_visible():
                users_hits += 1
        if users_hits >= len(_SETTINGS_USERS_PANEL_MARKERS):
            return False
        # Access-token panel lacks Tidlig adgang (required above). Side-nav
        # Adgangsnøgler may still appear on the beta panel and is not a reject.
        return True
    except Exception:
        return False


def _is_settings_subscription_url(url: str) -> bool:
    """Return True when the URL is the bare settings hub leaf (Abonnement path)."""

    return _is_settings_company_url(url)


def _ui_settings_subscription_changed_error() -> ToolError:
    """Stable UI_CHANGED for settings subscription (Abonnement) shell failures."""

    return ToolError(
        code=StableErrorCode.UI_CHANGED,
        message="Billy settings subscription shell could not be classified.",
    )


async def _has_settings_subscription_signature(page: LoginPage) -> bool:
    """Verify research134 Indstillinger empty Abonnement panel.

    Requires h1 Indstillinger, empty non-rail panel content (no nonempty h2 and
    no panel-only content markers), and rejection of company/accounting/
    invoicing/user/vat/users/beta full panel signatures. Side-nav labels alone
    (including Abonnement / Adgangsnøgler / Betas) are not success markers.
    Soft seeds and other settings panels are not success.
    """

    try:
        heading = page.locator("h1")
        if await heading.count() < 1:
            return False
        first = heading.first
        if not await first.is_visible():
            return False
        if (await first.inner_text()).strip() != _SETTINGS_SUBSCRIPTION_HEADING:
            return False

        # Empty content panel: no nonempty h2 headings.
        h2 = page.locator("h2")
        h2_count = await h2.count()
        for index in range(h2_count):
            control = h2.nth(index)
            try:
                if not await control.is_visible():
                    continue
            except Exception:
                continue
            text = (await control.inner_text()).strip()
            if text:
                return False

        # Reject panel-only content markers (not side-rail chrome alone).
        for label in _SETTINGS_SUBSCRIPTION_NONEMPTY_PANEL_MARKERS:
            control = page.locator(f"text={label}")
            if await control.count() >= 1 and await control.first.is_visible():
                return False

        company_hits = 0
        for label in _SETTINGS_COMPANY_PANEL_MARKERS:
            control = page.locator(f"text={label}")
            if await control.count() >= 1 and await control.first.is_visible():
                company_hits += 1
        if company_hits >= len(_SETTINGS_COMPANY_PANEL_MARKERS):
            return False
        accounting_hits = 0
        for label in _SETTINGS_ACCOUNTING_PANEL_MARKERS:
            control = page.locator(f"text={label}")
            if await control.count() >= 1 and await control.first.is_visible():
                accounting_hits += 1
        if accounting_hits >= len(_SETTINGS_ACCOUNTING_PANEL_MARKERS):
            return False
        invoicing_required = 0
        for label in _SETTINGS_INVOICING_REQUIRED_MARKERS:
            control = page.locator(f"text={label}")
            if await control.count() >= 1 and await control.first.is_visible():
                invoicing_required += 1
        if invoicing_required >= len(_SETTINGS_INVOICING_REQUIRED_MARKERS):
            optional_ok = False
            for label in _SETTINGS_INVOICING_OPTIONAL_MARKERS:
                control = page.locator(f"text={label}")
                if await control.count() >= 1 and await control.first.is_visible():
                    optional_ok = True
                    break
            if optional_ok:
                return False
        user_hits = 0
        for label in _SETTINGS_USER_PANEL_MARKERS:
            control = page.locator(f"text={label}")
            if await control.count() >= 1 and await control.first.is_visible():
                user_hits += 1
        if user_hits >= len(_SETTINGS_USER_PANEL_MARKERS):
            return False
        vat_hits = 0
        for label in _SETTINGS_VAT_PANEL_MARKERS:
            control = page.locator(f"text={label}")
            if await control.count() >= 1 and await control.first.is_visible():
                vat_hits += 1
        if vat_hits >= len(_SETTINGS_VAT_PANEL_MARKERS):
            return False
        users_hits = 0
        for label in _SETTINGS_USERS_PANEL_MARKERS:
            control = page.locator(f"text={label}")
            if await control.count() >= 1 and await control.first.is_visible():
                users_hits += 1
        if users_hits >= len(_SETTINGS_USERS_PANEL_MARKERS):
            return False
        beta_hits = 0
        for label in _SETTINGS_BETA_PANEL_MARKERS:
            control = page.locator(f"text={label}")
            if await control.count() >= 1 and await control.first.is_visible():
                beta_hits += 1
        if beta_hits >= len(_SETTINGS_BETA_PANEL_MARKERS):
            return False
        return True
    except Exception:
        return False


def _is_settings_user_organizations_url(url: str) -> bool:
    """Return True when the URL is the bare settings hub leaf (Virksomheder path)."""

    return _is_settings_company_url(url)


def _ui_settings_user_organizations_changed_error() -> ToolError:
    """Stable UI_CHANGED for settings user-organizations shell classification failures."""

    return ToolError(
        code=StableErrorCode.UI_CHANGED,
        message="Billy settings user organizations shell could not be classified.",
    )


async def _has_settings_user_organizations_signature(page: LoginPage) -> bool:
    """Verify research152 Indstillinger + Virksomheder multi-org panel markers.

    Requires h1 Indstillinger and Virksomheder + Alle organisationer + Opret
    organisation (chrome present only). Rejects full Profil user-edit panel,
    company default, accounting, invoicing, Brugere, and VAT panels. Soft seeds
    are not success. Never click Opret organisation.
    """

    try:
        heading = page.locator("h1")
        if await heading.count() < 1:
            return False
        first = heading.first
        if not await first.is_visible():
            return False
        if (await first.inner_text()).strip() != _SETTINGS_USER_ORGANIZATIONS_HEADING:
            return False
        for label in _SETTINGS_USER_ORGANIZATIONS_PANEL_MARKERS:
            control = page.locator(f"text={label}")
            if await control.count() < 1:
                return False
            if not await control.first.is_visible():
                return False
        # Reject full Profil user-edit panel (Billede + Sprog + password).
        user_hits = 0
        for label in _SETTINGS_USER_PANEL_MARKERS:
            control = page.locator(f"text={label}")
            if await control.count() >= 1 and await control.first.is_visible():
                user_hits += 1
        if user_hits >= len(_SETTINGS_USER_PANEL_MARKERS):
            return False
        # Reject company default panel.
        company_hits = 0
        for label in _SETTINGS_COMPANY_PANEL_MARKERS:
            control = page.locator(f"text={label}")
            if await control.count() >= 1 and await control.first.is_visible():
                company_hits += 1
        if company_hits >= len(_SETTINGS_COMPANY_PANEL_MARKERS):
            return False
        # Reject accounting Regnskab panel.
        accounting_hits = 0
        for label in _SETTINGS_ACCOUNTING_PANEL_MARKERS:
            control = page.locator(f"text={label}")
            if await control.count() >= 1 and await control.first.is_visible():
                accounting_hits += 1
        if accounting_hits >= len(_SETTINGS_ACCOUNTING_PANEL_MARKERS):
            return False
        # Reject invoicing Faktura panel (required markers).
        invoicing_hits = 0
        for label in _SETTINGS_INVOICING_REQUIRED_MARKERS:
            control = page.locator(f"text={label}")
            if await control.count() >= 1 and await control.first.is_visible():
                invoicing_hits += 1
        if invoicing_hits >= len(_SETTINGS_INVOICING_REQUIRED_MARKERS):
            return False
        # Reject Brugere panel.
        users_hits = 0
        for label in _SETTINGS_USERS_PANEL_MARKERS:
            control = page.locator(f"text={label}")
            if await control.count() >= 1 and await control.first.is_visible():
                users_hits += 1
        if users_hits >= len(_SETTINGS_USERS_PANEL_MARKERS):
            return False
        # Reject VAT Momssatser panel.
        vat_hits = 0
        for label in _SETTINGS_VAT_PANEL_MARKERS:
            control = page.locator(f"text={label}")
            if await control.count() >= 1 and await control.first.is_visible():
                vat_hits += 1
        if vat_hits >= len(_SETTINGS_VAT_PANEL_MARKERS):
            return False
        return True
    except Exception:
        return False


def _is_settings_users_url(url: str) -> bool:
    """Return True when the URL is the bare settings hub leaf (Brugere path)."""

    return _is_settings_company_url(url)


def _ui_settings_users_changed_error() -> ToolError:
    """Stable UI_CHANGED for settings users (Brugere) shell classification failures."""

    return ToolError(
        code=StableErrorCode.UI_CHANGED,
        message="Billy settings users shell could not be classified.",
    )


async def _has_settings_users_signature(page: LoginPage) -> bool:
    """Verify research131 Indstillinger + Brugere panel markers; never click writes.

    Requires h1 Indstillinger and Brugere + Revisorer og bogholdere.
    Rejects company default, accounting Regnskab, invoicing Faktura, user
    Profil, and VAT Momssatser panels. Soft seeds and other settings panels
    are not success. Use .first for multi-match rail/body labels (Brugere may
    appear as side-nav + panel h2).
    """

    try:
        heading = page.locator("h1")
        if await heading.count() < 1:
            return False
        first = heading.first
        if not await first.is_visible():
            return False
        if (await first.inner_text()).strip() != _SETTINGS_USERS_HEADING:
            return False
        for label in _SETTINGS_USERS_PANEL_MARKERS:
            control = page.locator(f"text={label}")
            if await control.count() < 1:
                return False
            if not await control.first.is_visible():
                return False
        # Reject company default panel.
        company_hits = 0
        for label in _SETTINGS_COMPANY_PANEL_MARKERS:
            control = page.locator(f"text={label}")
            if await control.count() >= 1 and await control.first.is_visible():
                company_hits += 1
        if company_hits >= len(_SETTINGS_COMPANY_PANEL_MARKERS):
            return False
        # Reject accounting Regnskab panel.
        accounting_hits = 0
        for label in _SETTINGS_ACCOUNTING_PANEL_MARKERS:
            control = page.locator(f"text={label}")
            if await control.count() >= 1 and await control.first.is_visible():
                accounting_hits += 1
        if accounting_hits >= len(_SETTINGS_ACCOUNTING_PANEL_MARKERS):
            return False
        # Reject invoicing Faktura panel when required markers + optional present.
        invoicing_required = 0
        for label in _SETTINGS_INVOICING_REQUIRED_MARKERS:
            control = page.locator(f"text={label}")
            if await control.count() >= 1 and await control.first.is_visible():
                invoicing_required += 1
        if invoicing_required >= len(_SETTINGS_INVOICING_REQUIRED_MARKERS):
            optional_ok = False
            for label in _SETTINGS_INVOICING_OPTIONAL_MARKERS:
                control = page.locator(f"text={label}")
                if await control.count() >= 1 and await control.first.is_visible():
                    optional_ok = True
                    break
            if optional_ok:
                return False
        # Reject user Profil panel when full marker set is active.
        user_hits = 0
        for label in _SETTINGS_USER_PANEL_MARKERS:
            control = page.locator(f"text={label}")
            if await control.count() >= 1 and await control.first.is_visible():
                user_hits += 1
        if user_hits >= len(_SETTINGS_USER_PANEL_MARKERS):
            return False
        # Reject VAT Momssatser panel when triad is active.
        vat_hits = 0
        for label in _SETTINGS_VAT_PANEL_MARKERS:
            control = page.locator(f"text={label}")
            if await control.count() >= 1 and await control.first.is_visible():
                vat_hits += 1
        if vat_hits >= len(_SETTINGS_VAT_PANEL_MARKERS):
            return False
        return True
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
        slug = _org_slug_from_url(page.url)
        if slug is None:
            return ToolError(
                code=StableErrorCode.ORGANIZATION_REQUIRED,
                message="Billy organisation slug is not available for the UI write.",
            )
        return AuthLoginWaitSuccess(status="READY", organization_id=slug)
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


def _ui_invoices_create_changed_error() -> ToolError:
    """Fail closed when the invoices create form no longer matches research153."""

    return ToolError(
        code=StableErrorCode.UI_CHANGED,
        message="Billy invoices create form interface no longer matches the recorded signature.",
    )


def _ui_invoices_get_changed_error() -> ToolError:
    return ToolError(
        code=StableErrorCode.UI_CHANGED,
        message="Billy invoices detail surface did not match the recorded get-open contract.",
    )


def _ui_invoices_delete_changed_error() -> ToolError:
    return ToolError(
        code=StableErrorCode.UI_CHANGED,
        message=(
            "Browser invoices delete chrome observation could not match "
            "the expected Mere menu surface."
        ),
    )


def _ui_invoices_update_changed_error() -> ToolError:
    return ToolError(
        code=StableErrorCode.UI_CHANGED,
        message=(
            "Billy invoices edit form surface did not match the recorded update-open contract."
        ),
    )


def _ui_bills_get_changed_error() -> ToolError:
    return ToolError(
        code=StableErrorCode.UI_CHANGED,
        message="Billy bills detail surface did not match the recorded get-open contract.",
    )


def _ui_bills_update_changed_error() -> ToolError:
    return ToolError(
        code=StableErrorCode.UI_CHANGED,
        message="Billy bills edit form surface did not match the recorded update-open contract.",
    )


def _ui_bills_delete_changed_error() -> ToolError:
    return ToolError(
        code=StableErrorCode.UI_CHANGED,
        message=(
            "Billy bills delete chrome surface did not match the recorded delete-open contract."
        ),
    )


def _ui_clients_create_changed_error() -> ToolError:
    """Fail closed when the clients create form no longer matches research160."""

    return ToolError(
        code=StableErrorCode.UI_CHANGED,
        message="Billy clients create form interface no longer matches the recorded signature.",
    )


def _ui_clients_get_changed_error() -> ToolError:
    """Fail closed when the clients detail surface no longer matches research164."""

    return ToolError(
        code=StableErrorCode.UI_CHANGED,
        message="Billy clients detail interface no longer matches the recorded signature.",
    )


def _ui_clients_update_changed_error() -> ToolError:
    """Fail closed when the clients update form no longer matches research166."""

    return ToolError(
        code=StableErrorCode.UI_CHANGED,
        message="Billy clients update form interface no longer matches the recorded signature.",
    )


def _ui_clients_delete_changed_error() -> ToolError:
    """Fail closed when the clients delete chrome no longer matches research167."""

    return ToolError(
        code=StableErrorCode.UI_CHANGED,
        message="Billy clients delete chrome interface no longer matches the recorded signature.",
    )


def _ui_bills_create_changed_error() -> ToolError:
    """Fail closed when the bills create form no longer matches research154."""

    return ToolError(
        code=StableErrorCode.UI_CHANGED,
        message="Billy bills create form interface no longer matches the recorded signature.",
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


def _ui_suppliers_create_changed_error() -> ToolError:
    """Fail closed when the suppliers create form no longer matches research161."""

    return ToolError(
        code=StableErrorCode.UI_CHANGED,
        message="Billy suppliers create form interface no longer matches the recorded signature.",
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
