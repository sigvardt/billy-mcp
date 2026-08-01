"""Shared typed contracts used by the server and coverage machinery."""

from __future__ import annotations

from enum import StrEnum
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field


class StableErrorCode(StrEnum):
    """Public errors defined by the approved Billy MCP design."""

    AUTH_REQUIRED = "AUTH_REQUIRED"
    AUTH_EXPIRED = "AUTH_EXPIRED"
    AUTH_INTERACTION_REQUIRED = "AUTH_INTERACTION_REQUIRED"
    ORGANIZATION_REQUIRED = "ORGANIZATION_REQUIRED"
    ORGANIZATION_MISMATCH = "ORGANIZATION_MISMATCH"
    VALIDATION_ERROR = "VALIDATION_ERROR"
    NOT_FOUND = "NOT_FOUND"
    CONFLICT = "CONFLICT"
    CONFIRMATION_INVALID = "CONFIRMATION_INVALID"
    CONFIRMATION_EXPIRED = "CONFIRMATION_EXPIRED"
    CONFIRMATION_CONSUMED = "CONFIRMATION_CONSUMED"
    CONFIRMATION_MISMATCH = "CONFIRMATION_MISMATCH"
    FILE_NOT_ALLOWED = "FILE_NOT_ALLOWED"
    FILE_CHANGED = "FILE_CHANGED"
    PLAN_UNAVAILABLE = "PLAN_UNAVAILABLE"
    UI_CHANGED = "UI_CHANGED"
    EGRESS_DENIED = "EGRESS_DENIED"
    RATE_LIMITED = "RATE_LIMITED"
    BILLY_ERROR = "BILLY_ERROR"
    CLEANUP_FAILED = "CLEANUP_FAILED"


class ToolError(BaseModel):
    """Stable, serialisable failure returned by any registered MCP tool."""

    model_config = ConfigDict(extra="forbid")

    code: StableErrorCode
    message: str
    details: dict[str, Any] = Field(default_factory=dict)


class AuthStatusInput(BaseModel):
    """Empty, strict input boundary for the read-only browser session check."""

    model_config = ConfigDict(extra="forbid")


class AuthStatusSuccess(BaseModel):
    """The one browser-authentication state verified by the login signature."""

    model_config = ConfigDict(extra="forbid")

    status: Literal[StableErrorCode.AUTH_REQUIRED] = StableErrorCode.AUTH_REQUIRED


class AuthLoginStartInput(BaseModel):
    """Empty, strict input boundary for the fixed pre-submit transition."""

    model_config = ConfigDict(extra="forbid")


class AuthLoginStartSuccess(BaseModel):
    """The only positive result proved immediately after the internal submit action."""

    model_config = ConfigDict(extra="forbid")

    status: Literal["AUTHENTICATING"] = "AUTHENTICATING"


class AuthLoginWaitInput(BaseModel):
    """Empty, strict input boundary for observing post-login session state."""

    model_config = ConfigDict(extra="forbid")


class AuthLoginWaitSuccess(BaseModel):
    """Post-login observation: login still required, or authenticated shell READY."""

    model_config = ConfigDict(extra="forbid")

    status: Literal["AUTH_REQUIRED", "READY"]


class UiInvoicesListInput(BaseModel):
    """Empty, strict input boundary for the read-only invoices list shell tool."""

    model_config = ConfigDict(extra="forbid")


class UiInvoicesListSuccess(BaseModel):
    """Non-PII classification of the observed Billy invoices list shell."""

    model_config = ConfigDict(extra="forbid")

    path_class: Literal["/:org_slug/invoices"] = "/:org_slug/invoices"
    heading: Literal["Fakturaer"] = "Fakturaer"
    create_action_visible: bool
    shell_markers_present: bool


class UiInvoicesCreateOpenInput(BaseModel):
    """Empty, strict input boundary for the read-only invoice create form open tool."""

    model_config = ConfigDict(extra="forbid")


class UiInvoicesCreateOpenSuccess(BaseModel):
    """Non-PII classification of the observed Billy invoice create form shell."""

    model_config = ConfigDict(extra="forbid")

    path_class: Literal["/:org_slug/invoices/new"] = "/:org_slug/invoices/new"
    heading: Literal["Opret faktura"] = "Opret faktura"
    shell_kind: Literal["invoices_create"] = "invoices_create"
    draft_save_chrome_visible: bool
    line_chrome_visible: bool
    shell_markers_present: bool


class UiProductsListInput(BaseModel):
    """Empty, strict input boundary for the read-only products list shell tool."""

    model_config = ConfigDict(extra="forbid")


class UiProductsListSuccess(BaseModel):
    """Non-PII classification of the observed Billy products list shell."""

    model_config = ConfigDict(extra="forbid")

    path_class: Literal["/:org_slug/products"] = "/:org_slug/products"
    heading: Literal["Produkter"] = "Produkter"
    search_control_visible: bool
    shell_markers_present: bool


class UiClientsListInput(BaseModel):
    """Empty, strict input boundary for the read-only clients list shell tool."""

    model_config = ConfigDict(extra="forbid")


class UiClientsListSuccess(BaseModel):
    """Non-PII classification of the observed Billy clients list shell."""

    model_config = ConfigDict(extra="forbid")

    path_class: Literal["/:org_slug/clients"] = "/:org_slug/clients"
    heading: Literal["Kunder"] = "Kunder"
    create_action_visible: bool
    shell_markers_present: bool


class UiBankAccountsListInput(BaseModel):
    """Empty, strict input boundary for the read-only bank accounts list shell tool."""

    model_config = ConfigDict(extra="forbid")


class UiBankAccountsListSuccess(BaseModel):
    """Non-PII classification of the observed Billy bank accounts list shell."""

    model_config = ConfigDict(extra="forbid")

    path_class: Literal["/:org_slug/bank-accounts"] = "/:org_slug/bank-accounts"
    heading: Literal["Bankkonti"] = "Bankkonti"
    connect_bank_action_visible: bool
    shell_markers_present: bool


class UiQuotesListInput(BaseModel):
    """Empty, strict input boundary for the read-only quotes list shell tool."""

    model_config = ConfigDict(extra="forbid")


class UiQuotesListSuccess(BaseModel):
    """Non-PII classification of the observed Billy quotes list shell."""

    model_config = ConfigDict(extra="forbid")

    path_class: Literal["/:org_slug/quotes"] = "/:org_slug/quotes"
    heading: Literal["Tilbud"] = "Tilbud"
    create_action_visible: bool
    shell_markers_present: bool


class UiRecurringInvoicesListInput(BaseModel):
    """Empty, strict input boundary for the read-only recurring invoices list shell tool."""

    model_config = ConfigDict(extra="forbid")


class UiRecurringInvoicesListSuccess(BaseModel):
    """Non-PII classification of the observed Billy recurring invoices list shell."""

    model_config = ConfigDict(extra="forbid")

    path_class: Literal["/:org_slug/recurring_invoices"] = "/:org_slug/recurring_invoices"
    heading: Literal["Abonnementer"] = "Abonnementer"
    create_action_visible: bool
    shell_markers_present: bool


class UiProductsImportInput(BaseModel):
    """Empty, strict input boundary for the read-only products import shell tool."""

    model_config = ConfigDict(extra="forbid")


class UiProductsImportSuccess(BaseModel):
    """Non-PII classification of the observed Billy products import shell."""

    model_config = ConfigDict(extra="forbid")

    path_class: Literal["/:org_slug/products/import"] = "/:org_slug/products/import"
    heading: Literal["Import af produkter"] = "Import af produkter"
    choose_csv_action_visible: bool
    shell_markers_present: bool


class UiSuppliersListInput(BaseModel):
    """Empty, strict input boundary for the read-only suppliers list shell tool."""

    model_config = ConfigDict(extra="forbid")


class UiSuppliersListSuccess(BaseModel):
    """Non-PII classification of the observed Billy suppliers list shell."""

    model_config = ConfigDict(extra="forbid")

    path_class: Literal["/:org_slug/suppliers"] = "/:org_slug/suppliers"
    heading: Literal["Leverandører"] = "Leverandører"
    create_action_visible: bool
    shell_markers_present: bool


class UiBillsListInput(BaseModel):
    """Empty, strict input boundary for the read-only bills (purchases) list shell tool."""

    model_config = ConfigDict(extra="forbid")


class UiBillsListSuccess(BaseModel):
    """Non-PII classification of the observed Billy bills list shell (UI purchases / Køb)."""

    model_config = ConfigDict(extra="forbid")

    path_class: Literal["/:org_slug/bills"] = "/:org_slug/bills"
    heading: Literal["Køb"] = "Køb"
    create_action_visible: bool
    shell_markers_present: bool


class UiDebtorBalancesListInput(BaseModel):
    """Empty, strict input boundary for the read-only debtor balances list shell tool."""

    model_config = ConfigDict(extra="forbid")


class UiDebtorBalancesListSuccess(BaseModel):
    """Non-PII classification of the observed Billy debtor balances (Tilgodehavender) shell."""

    model_config = ConfigDict(extra="forbid")

    path_class: Literal["/:org_slug/debtorbalance"] = "/:org_slug/debtorbalance"
    heading: Literal["Tilgodehavender"] = "Tilgodehavender"
    create_action_visible: bool
    shell_markers_present: bool


class UiCreditorBalancesListInput(BaseModel):
    """Empty, strict input boundary for the read-only creditor balances list shell tool."""

    model_config = ConfigDict(extra="forbid")


class UiCreditorBalancesListSuccess(BaseModel):
    """Non-PII classification of the observed Billy creditor balances (Skyldige udgifter) shell."""

    model_config = ConfigDict(extra="forbid")

    path_class: Literal["/:org_slug/creditorbalance"] = "/:org_slug/creditorbalance"
    heading: Literal["Skyldige udgifter"] = "Skyldige udgifter"
    create_action_visible: bool
    shell_markers_present: bool


class UiUploadsListInput(BaseModel):
    """Empty, strict input boundary for the read-only uploads (Bilag) list shell tool."""

    model_config = ConfigDict(extra="forbid")


class UiUploadsListSuccess(BaseModel):
    """Non-PII classification of the observed Billy uploads (Bilag) shell."""

    model_config = ConfigDict(extra="forbid")

    path_class: Literal["/:org_slug/uploads"] = "/:org_slug/uploads"
    heading: Literal["Bilag"] = "Bilag"
    upload_action_visible: bool
    shell_markers_present: bool


class UiReceiptInboxListInput(BaseModel):
    """Empty, strict input boundary for the read-only receipt inbox list shell tool."""

    model_config = ConfigDict(extra="forbid")


class UiReceiptInboxListSuccess(BaseModel):
    """Non-PII classification of the observed Billy receipt inbox (Bilagsindbakke) shell."""

    model_config = ConfigDict(extra="forbid")

    path_class: Literal["/:org_slug/vouchers"] = "/:org_slug/vouchers"
    heading: Literal["Bilagsindbakke"] = "Bilagsindbakke"
    file_control_present: bool
    shell_markers_present: bool


class UiBankReconciliationOpenInput(BaseModel):
    """Empty, strict input for the read-only bank reconciliation (Afstemning) shell tool."""

    model_config = ConfigDict(extra="forbid")


class UiBankReconciliationOpenSuccess(BaseModel):
    """Non-PII classification of the observed Billy bank reconciliation (Afstemning) shell."""

    model_config = ConfigDict(extra="forbid")

    path_class: Literal["/:org_slug/bank_accounts/:id/sync"] = "/:org_slug/bank_accounts/:id/sync"
    heading: str = ""
    empty_content_shell: bool
    afstemning_nav_visible: bool
    shell_markers_present: bool


class UiFinancingOpenInput(BaseModel):
    """Empty, strict input for the read-only financing (Ansøg om erhvervslån) shell tool."""

    model_config = ConfigDict(extra="forbid")


class UiFinancingOpenSuccess(BaseModel):
    """Non-PII classification of the observed Billy financing shell."""

    model_config = ConfigDict(extra="forbid")

    path_class: Literal["/:org_slug/financing"] = "/:org_slug/financing"
    heading: Literal["Ansøg om erhvervslån"] = "Ansøg om erhvervslån"
    apply_cta_observed: bool
    shell_markers_present: bool


class UiDaybooksOpenInput(BaseModel):
    """Empty, strict input for the read-only daybook (Kassekladde) editor shell tool."""

    model_config = ConfigDict(extra="forbid")


class UiDaybooksOpenSuccess(BaseModel):
    """Non-PII classification of the observed Billy daybook editor shell."""

    model_config = ConfigDict(extra="forbid")

    path_class: Literal["/:org_slug/daybooks/new"] = "/:org_slug/daybooks/new"
    heading: str = ""
    editor_markers_present: bool
    shell_markers_present: bool


class UiTransactionsListInput(BaseModel):
    """Empty, strict input for the read-only transactions (Posteringer) list shell tool."""

    model_config = ConfigDict(extra="forbid")


class UiTransactionsListSuccess(BaseModel):
    """Non-PII classification of the observed Billy Posteringer list shell."""

    model_config = ConfigDict(extra="forbid")

    path_class: Literal["/:org_slug/transactions"] = "/:org_slug/transactions"
    heading: Literal["Posteringer"] = "Posteringer"
    create_action_visible: bool
    shell_markers_present: bool


class UiReportsOpenInput(BaseModel):
    """Empty, strict input for the read-only reports (Rapporter) hub shell tool."""

    model_config = ConfigDict(extra="forbid")


class UiReportsOpenSuccess(BaseModel):
    """Non-PII classification of the observed Billy Rapporter hub shell."""

    model_config = ConfigDict(extra="forbid")

    path_class: Literal["/:org_slug/reports-all"] = "/:org_slug/reports-all"
    heading: Literal["Rapporter"] = "Rapporter"
    export_action_visible: bool
    shell_markers_present: bool


class UiVatDeclarationsListInput(BaseModel):
    """Empty, strict input for the read-only VAT declarations (Momsangivelser) list shell."""

    model_config = ConfigDict(extra="forbid")


class UiVatDeclarationsListSuccess(BaseModel):
    """Non-PII classification of the observed Billy Momsangivelser list shell."""

    model_config = ConfigDict(extra="forbid")

    path_class: Literal["/:org_slug/vat-declarations"] = "/:org_slug/vat-declarations"
    heading: Literal["Momsangivelser"] = "Momsangivelser"
    period_column_visible: bool
    shell_markers_present: bool


class UiExportsOpenInput(BaseModel):
    """Empty, strict input for the read-only exports (Eksportér data) hub shell tool."""

    model_config = ConfigDict(extra="forbid")


class UiExportsOpenSuccess(BaseModel):
    """Non-PII classification of the observed Billy Eksportér data hub shell."""

    model_config = ConfigDict(extra="forbid")

    path_class: Literal["/:org_slug/exports"] = "/:org_slug/exports"
    heading: Literal["Eksportér data"] = "Eksportér data"
    saft_export_cta_observed: bool
    shell_markers_present: bool


class UiSaftExportsOpenInput(BaseModel):
    """Empty, strict input for the read-only SAF-T CTA observe shell on exports hub."""

    model_config = ConfigDict(extra="forbid")


class UiSaftExportsOpenSuccess(BaseModel):
    """Non-PII classification requiring SAF-T CTA on the Eksportér data hub."""

    model_config = ConfigDict(extra="forbid")

    path_class: Literal["/:org_slug/exports"] = "/:org_slug/exports"
    heading: Literal["Eksportér data"] = "Eksportér data"
    saft_export_cta_observed: Literal[True] = True
    shell_markers_present: bool


class UiAddonsOpenInput(BaseModel):
    """Empty, strict input for the read-only Fordele (add-ons) hub shell open."""

    model_config = ConfigDict(extra="forbid")


class UiAddonsOpenSuccess(BaseModel):
    """Non-PII classification for the Fordele hub at /:org_slug/add-ons."""

    model_config = ConfigDict(extra="forbid")

    path_class: Literal["/:org_slug/add-ons"] = "/:org_slug/add-ons"
    heading: Literal["Fordele"] = "Fordele"
    shell_markers_present: bool


class UiIntegrationsOpenInput(BaseModel):
    """Empty, strict input for integrations soft-empty classification."""

    model_config = ConfigDict(extra="forbid")


class UiIntegrationsOpenSuccess(BaseModel):
    """Non-PII soft-empty classification for /:org_slug/integrations (research124)."""

    model_config = ConfigDict(extra="forbid")

    path_class: Literal["/:org_slug/integrations"] = "/:org_slug/integrations"
    shell_kind: Literal["soft_empty"] = "soft_empty"
    dedicated_shell: Literal[False] = False
    same_shell_as_addons: Literal[False] = False
    heading: Literal[""] = ""
    shell_markers_present: bool


class UiInventoryOpenInput(BaseModel):
    """Empty, strict input for the read-only Lagermodul inventory shell open."""

    model_config = ConfigDict(extra="forbid")


class UiInventoryOpenSuccess(BaseModel):
    """Non-PII classification for the Lagermodul shell at /:org_slug/inventory."""

    model_config = ConfigDict(extra="forbid")

    path_class: Literal["/:org_slug/inventory"] = "/:org_slug/inventory"
    heading: Literal["Lagermodul"] = "Lagermodul"
    shell_kind: Literal["lagermodul"] = "lagermodul"
    create_cta_markers_present: bool


class UiSettingsCompanyOpenInput(BaseModel):
    """Empty, strict input for the read-only company settings shell open."""

    model_config = ConfigDict(extra="forbid")


class UiSettingsCompanyOpenSuccess(BaseModel):
    """Non-PII classification for Indstillinger company panel at /:org_slug/settings."""

    model_config = ConfigDict(extra="forbid")

    path_class: Literal["/:org_slug/settings"] = "/:org_slug/settings"
    heading: Literal["Indstillinger"] = "Indstillinger"
    shell_kind: Literal["settings_company"] = "settings_company"
    company_panel_markers_present: bool


class UiSettingsAccountingOpenInput(BaseModel):
    """Empty, strict input for the read-only accounting settings shell open."""

    model_config = ConfigDict(extra="forbid")


class UiSettingsAccountingOpenSuccess(BaseModel):
    """Non-PII classification for Indstillinger Regnskab panel at /:org_slug/settings."""

    model_config = ConfigDict(extra="forbid")

    path_class: Literal["/:org_slug/settings"] = "/:org_slug/settings"
    heading: Literal["Indstillinger"] = "Indstillinger"
    shell_kind: Literal["settings_accounting"] = "settings_accounting"
    accounting_panel_markers_present: bool


class UiSettingsInvoicingOpenInput(BaseModel):
    """Empty, strict input for the read-only invoicing settings shell open."""

    model_config = ConfigDict(extra="forbid")


class UiSettingsInvoicingOpenSuccess(BaseModel):
    """Non-PII classification for Indstillinger Faktura panel at /:org_slug/settings."""

    model_config = ConfigDict(extra="forbid")

    path_class: Literal["/:org_slug/settings"] = "/:org_slug/settings"
    heading: Literal["Indstillinger"] = "Indstillinger"
    shell_kind: Literal["settings_invoicing"] = "settings_invoicing"
    invoicing_panel_markers_present: bool


class UiSettingsUserOpenInput(BaseModel):
    """Empty, strict input for the read-only user settings (Profil) shell open."""

    model_config = ConfigDict(extra="forbid")


class UiSettingsUserOpenSuccess(BaseModel):
    """Non-PII classification for Indstillinger Profil panel at /:org_slug/settings."""

    model_config = ConfigDict(extra="forbid")

    path_class: Literal["/:org_slug/settings"] = "/:org_slug/settings"
    heading: Literal["Indstillinger"] = "Indstillinger"
    shell_kind: Literal["settings_user"] = "settings_user"
    user_panel_markers_present: bool


class UiSettingsUserOrganizationsOpenInput(BaseModel):
    """Empty, strict input for the read-only user organizations (Virksomheder) shell open."""

    model_config = ConfigDict(extra="forbid")


class UiSettingsUserOrganizationsOpenSuccess(BaseModel):
    """Non-PII classification for Indstillinger Virksomheder multi-org panel."""

    model_config = ConfigDict(extra="forbid")

    path_class: Literal["/:org_slug/settings"] = "/:org_slug/settings"
    heading: Literal["Indstillinger"] = "Indstillinger"
    shell_kind: Literal["settings_user_organizations"] = "settings_user_organizations"
    user_organizations_panel_markers_present: bool


class UiSettingsVatOpenInput(BaseModel):
    """Empty, strict input for the read-only VAT settings (Momssatser) shell open."""

    model_config = ConfigDict(extra="forbid")


class UiSettingsVatOpenSuccess(BaseModel):
    """Non-PII classification for Indstillinger Momssatser panel at /:org_slug/settings."""

    model_config = ConfigDict(extra="forbid")

    path_class: Literal["/:org_slug/settings"] = "/:org_slug/settings"
    heading: Literal["Indstillinger"] = "Indstillinger"
    shell_kind: Literal["settings_vat"] = "settings_vat"
    vat_panel_markers_present: bool


class UiSettingsUsersOpenInput(BaseModel):
    """Empty, strict input for the read-only org users settings (Brugere) shell open."""

    model_config = ConfigDict(extra="forbid")


class UiSettingsUsersOpenSuccess(BaseModel):
    """Non-PII classification for Indstillinger Brugere panel at /:org_slug/settings."""

    model_config = ConfigDict(extra="forbid")

    path_class: Literal["/:org_slug/settings"] = "/:org_slug/settings"
    heading: Literal["Indstillinger"] = "Indstillinger"
    shell_kind: Literal["settings_users"] = "settings_users"
    users_panel_markers_present: bool


class UiSettingsAccessTokenOpenInput(BaseModel):
    """Empty, strict input for the read-only access-token settings (Adgangsnøgler) shell open."""

    model_config = ConfigDict(extra="forbid")


class UiSettingsAccessTokenOpenSuccess(BaseModel):
    """Non-PII classification for Indstillinger Adgangsnøgler panel at /:org_slug/settings."""

    model_config = ConfigDict(extra="forbid")

    path_class: Literal["/:org_slug/settings"] = "/:org_slug/settings"
    heading: Literal["Indstillinger"] = "Indstillinger"
    shell_kind: Literal["settings_access_token"] = "settings_access_token"
    access_token_panel_markers_present: bool


class UiSettingsBetaOpenInput(BaseModel):
    """Empty, strict input for the read-only betas settings (Betas) shell open."""

    model_config = ConfigDict(extra="forbid")


class UiSettingsBetaOpenSuccess(BaseModel):
    """Non-PII classification for Indstillinger Betas panel at /:org_slug/settings."""

    model_config = ConfigDict(extra="forbid")

    path_class: Literal["/:org_slug/settings"] = "/:org_slug/settings"
    heading: Literal["Indstillinger"] = "Indstillinger"
    shell_kind: Literal["settings_beta"] = "settings_beta"
    beta_panel_markers_present: bool


class UiSettingsSubscriptionOpenInput(BaseModel):
    """Empty, strict input for the read-only subscription settings (Abonnement) shell open."""

    model_config = ConfigDict(extra="forbid")


class UiSettingsSubscriptionOpenSuccess(BaseModel):
    """Non-PII classification for Indstillinger Abonnement empty panel at /:org_slug/settings."""

    model_config = ConfigDict(extra="forbid")

    path_class: Literal["/:org_slug/settings"] = "/:org_slug/settings"
    heading: Literal["Indstillinger"] = "Indstillinger"
    shell_kind: Literal["settings_subscription"] = "settings_subscription"
    empty_panel: bool


class CoverageStatus(BaseModel):
    """The four required API states plus the UI-only visual verification state."""

    model_config = ConfigDict(extra="forbid")

    discovered: bool = False
    implemented: bool = False
    contract_tested: bool = False
    live_tested: bool = False
    vision_verified: bool | None = None
