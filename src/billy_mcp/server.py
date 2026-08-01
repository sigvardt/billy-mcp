"""The Billy FastMCP stdio shell with coverage, reads, and ticketed writes."""

from __future__ import annotations

from pathlib import Path

from fastmcp import FastMCP

from billy_mcp.api.account_reads import register_account_read_tools
from billy_mcp.api.account_writes import register_account_write_tools
from billy_mcp.api.attachment_writes import register_attachment_write_tools
from billy_mcp.api.balance_invoice_ext_reads import register_balance_invoice_extension_read_tools
from billy_mcp.api.bank_line_writes import register_bank_line_write_tools
from billy_mcp.api.bank_payment_writes import register_bank_payment_write_tools
from billy_mcp.api.bank_reads import register_bank_read_tools
from billy_mcp.api.bill_line_writes import register_bill_line_write_tools
from billy_mcp.api.bill_reads import register_bill_read_tools
from billy_mcp.api.bill_writes import register_bill_write_tools
from billy_mcp.api.bootstrap_reads import register_bootstrap_read_tools
from billy_mcp.api.catalog_reads import register_catalog_read_tools
from billy_mcp.api.catalog_writes import register_catalog_write_tools
from billy_mcp.api.contact_balance_payment_writes import (
    register_contact_balance_payment_write_tools,
)
from billy_mcp.api.contact_person_reads import register_contact_person_read_tools
from billy_mcp.api.contact_person_writes import register_contact_person_write_tools
from billy_mcp.api.contact_reads import register_contact_read_tools
from billy_mcp.api.contact_writes import register_contact_write_tools
from billy_mcp.api.daybook_balance_account_writes import (
    register_daybook_balance_account_write_tools,
)
from billy_mcp.api.daybook_reads import register_daybook_read_tools
from billy_mcp.api.daybook_transaction_line_writes import (
    register_daybook_transaction_line_write_tools,
)
from billy_mcp.api.daybook_transaction_reads import register_daybook_transaction_read_tools
from billy_mcp.api.daybook_transaction_writes import register_daybook_transaction_write_tools
from billy_mcp.api.daybook_writes import register_daybook_write_tools
from billy_mcp.api.file_attachment_reads import register_file_attachment_read_tools
from billy_mcp.api.file_upload_writes import register_file_upload_tools
from billy_mcp.api.geo_reads import register_geo_read_tools
from billy_mcp.api.invoice_email_delivery_writes import register_invoice_email_delivery_write_tools
from billy_mcp.api.invoice_late_fee_writes import register_invoice_late_fee_write_tools
from billy_mcp.api.invoice_line_writes import register_invoice_line_write_tools
from billy_mcp.api.invoice_log_reads import register_invoice_log_read_tools
from billy_mcp.api.invoice_reads import register_invoice_read_tools
from billy_mcp.api.invoice_reminder_writes import register_invoice_reminder_write_tools
from billy_mcp.api.invoice_writes import register_invoice_write_tools
from billy_mcp.api.ledger_user_reads import register_ledger_user_read_tools
from billy_mcp.api.line_reads import register_line_read_tools
from billy_mcp.api.organization_writes import register_organization_write_tools
from billy_mcp.api.reference_reads import register_reference_reads
from billy_mcp.api.sales_tax_account_meta_writes import register_sales_tax_account_meta_write_tools
from billy_mcp.api.sales_tax_payment_writes import register_sales_tax_payment_write_tools
from billy_mcp.api.sales_tax_return_writes import register_sales_tax_return_write_tools
from billy_mcp.api.sales_tax_writes import register_sales_tax_write_tools
from billy_mcp.api.tax_reads import register_tax_read_tools
from billy_mcp.api.tax_writes import register_tax_write_tools
from billy_mcp.api.user_writes import register_user_write_tools
from billy_mcp.api.write_protocol import WriteProtocolService
from billy_mcp.browser import (
    AuthLoginService,
    AuthStatusChecker,
    BrowserRuntime,
    UiAddonsOpenService,
    UiBankAccountsListService,
    UiBankReconciliationOpenService,
    UiBillsCreateOpenService,
    UiBillsListService,
    UiClientsCreateOpenService,
    UiClientsGetOpenService,
    UiClientsListService,
    UiCreditorBalancesListService,
    UiDaybooksOpenService,
    UiDebtorBalancesListService,
    UiExportsOpenService,
    UiFinancingOpenService,
    UiIntegrationsOpenService,
    UiInventoryOpenService,
    UiInvoicesCreateOpenService,
    UiInvoicesListService,
    UiProductsCreateOpenService,
    UiProductsImportService,
    UiProductsListService,
    UiQuotesListService,
    UiReceiptInboxListService,
    UiRecurringInvoicesListService,
    UiReportsOpenService,
    UiSaftExportsOpenService,
    UiSettingsAccessTokenOpenService,
    UiSettingsAccountingOpenService,
    UiSettingsBetaOpenService,
    UiSettingsCompanyOpenService,
    UiSettingsInvoicingOpenService,
    UiSettingsSubscriptionOpenService,
    UiSettingsUserOpenService,
    UiSettingsUserOrganizationsOpenService,
    UiSettingsUsersOpenService,
    UiSettingsVatOpenService,
    UiSuppliersCreateOpenService,
    UiSuppliersListService,
    UiTransactionsListService,
    UiUploadsListService,
    UiVatDeclarationsListService,
)
from billy_mcp.client import BillyHttpClient
from billy_mcp.config import AppConfig
from billy_mcp.confirmations import ConfirmationStore
from billy_mcp.coverage import (
    CoverageLoadError,
    CoverageReport,
    GeneratedCoverageStatus,
    load_coverage_report,
)
from billy_mcp.models import (
    AuthLoginStartInput,
    AuthLoginStartSuccess,
    AuthLoginWaitInput,
    AuthLoginWaitSuccess,
    AuthStatusInput,
    AuthStatusSuccess,
    ToolError,
    UiAddonsOpenInput,
    UiAddonsOpenSuccess,
    UiBankAccountsListInput,
    UiBankAccountsListSuccess,
    UiBankReconciliationOpenInput,
    UiBankReconciliationOpenSuccess,
    UiBillsCreateOpenInput,
    UiBillsCreateOpenSuccess,
    UiBillsListInput,
    UiBillsListSuccess,
    UiClientsCreateOpenInput,
    UiClientsCreateOpenSuccess,
    UiClientsGetOpenInput,
    UiClientsGetOpenSuccess,
    UiClientsListInput,
    UiClientsListSuccess,
    UiCreditorBalancesListInput,
    UiCreditorBalancesListSuccess,
    UiDaybooksOpenInput,
    UiDaybooksOpenSuccess,
    UiDebtorBalancesListInput,
    UiDebtorBalancesListSuccess,
    UiExportsOpenInput,
    UiExportsOpenSuccess,
    UiFinancingOpenInput,
    UiFinancingOpenSuccess,
    UiIntegrationsOpenInput,
    UiIntegrationsOpenSuccess,
    UiInventoryOpenInput,
    UiInventoryOpenSuccess,
    UiInvoicesCreateOpenInput,
    UiInvoicesCreateOpenSuccess,
    UiInvoicesListInput,
    UiInvoicesListSuccess,
    UiProductsCreateOpenInput,
    UiProductsCreateOpenSuccess,
    UiProductsImportInput,
    UiProductsImportSuccess,
    UiProductsListInput,
    UiProductsListSuccess,
    UiQuotesListInput,
    UiQuotesListSuccess,
    UiReceiptInboxListInput,
    UiReceiptInboxListSuccess,
    UiRecurringInvoicesListInput,
    UiRecurringInvoicesListSuccess,
    UiReportsOpenInput,
    UiReportsOpenSuccess,
    UiSaftExportsOpenInput,
    UiSaftExportsOpenSuccess,
    UiSettingsAccessTokenOpenInput,
    UiSettingsAccessTokenOpenSuccess,
    UiSettingsAccountingOpenInput,
    UiSettingsAccountingOpenSuccess,
    UiSettingsBetaOpenInput,
    UiSettingsBetaOpenSuccess,
    UiSettingsCompanyOpenInput,
    UiSettingsCompanyOpenSuccess,
    UiSettingsInvoicingOpenInput,
    UiSettingsInvoicingOpenSuccess,
    UiSettingsSubscriptionOpenInput,
    UiSettingsSubscriptionOpenSuccess,
    UiSettingsUserOpenInput,
    UiSettingsUserOpenSuccess,
    UiSettingsUserOrganizationsOpenInput,
    UiSettingsUserOrganizationsOpenSuccess,
    UiSettingsUsersOpenInput,
    UiSettingsUsersOpenSuccess,
    UiSettingsVatOpenInput,
    UiSettingsVatOpenSuccess,
    UiSuppliersCreateOpenInput,
    UiSuppliersCreateOpenSuccess,
    UiSuppliersListInput,
    UiSuppliersListSuccess,
    UiTransactionsListInput,
    UiTransactionsListSuccess,
    UiUploadsListInput,
    UiUploadsListSuccess,
    UiVatDeclarationsListInput,
    UiVatDeclarationsListSuccess,
)


def create_server(
    repository_root: Path | None = None,
    *,
    auth_status_checker: AuthStatusChecker | None = None,
    auth_login_service: AuthLoginService | None = None,
    ui_invoices_list_service: UiInvoicesListService | None = None,
    ui_invoices_create_open_service: UiInvoicesCreateOpenService | None = None,
    ui_products_list_service: UiProductsListService | None = None,
    ui_products_create_open_service: UiProductsCreateOpenService | None = None,
    ui_clients_list_service: UiClientsListService | None = None,
    ui_clients_create_open_service: UiClientsCreateOpenService | None = None,
    ui_clients_get_open_service: UiClientsGetOpenService | None = None,
    ui_bank_accounts_list_service: UiBankAccountsListService | None = None,
    ui_quotes_list_service: UiQuotesListService | None = None,
    ui_recurring_invoices_list_service: UiRecurringInvoicesListService | None = None,
    ui_products_import_service: UiProductsImportService | None = None,
    ui_suppliers_list_service: UiSuppliersListService | None = None,
    ui_suppliers_create_open_service: UiSuppliersCreateOpenService | None = None,
    ui_bills_list_service: UiBillsListService | None = None,
    ui_bills_create_open_service: UiBillsCreateOpenService | None = None,
    ui_debtor_balances_list_service: UiDebtorBalancesListService | None = None,
    ui_creditor_balances_list_service: UiCreditorBalancesListService | None = None,
    ui_uploads_list_service: UiUploadsListService | None = None,
    ui_receipt_inbox_list_service: UiReceiptInboxListService | None = None,
    ui_bank_reconciliation_open_service: UiBankReconciliationOpenService | None = None,
    ui_financing_open_service: UiFinancingOpenService | None = None,
    ui_daybooks_open_service: UiDaybooksOpenService | None = None,
    ui_transactions_list_service: UiTransactionsListService | None = None,
    ui_reports_open_service: UiReportsOpenService | None = None,
    ui_vat_declarations_list_service: UiVatDeclarationsListService | None = None,
    ui_exports_open_service: UiExportsOpenService | None = None,
    ui_saft_exports_open_service: UiSaftExportsOpenService | None = None,
    ui_addons_open_service: UiAddonsOpenService | None = None,
    ui_integrations_open_service: UiIntegrationsOpenService | None = None,
    ui_inventory_open_service: UiInventoryOpenService | None = None,
    ui_settings_company_open_service: UiSettingsCompanyOpenService | None = None,
    ui_settings_accounting_open_service: UiSettingsAccountingOpenService | None = None,
    ui_settings_invoicing_open_service: UiSettingsInvoicingOpenService | None = None,
    ui_settings_user_open_service: UiSettingsUserOpenService | None = None,
    ui_settings_user_organizations_open_service: UiSettingsUserOrganizationsOpenService
    | None = None,
    ui_settings_vat_open_service: UiSettingsVatOpenService | None = None,
    ui_settings_users_open_service: UiSettingsUsersOpenService | None = None,
    ui_settings_access_token_open_service: UiSettingsAccessTokenOpenService | None = None,
    ui_settings_beta_open_service: UiSettingsBetaOpenService | None = None,
    ui_settings_subscription_open_service: UiSettingsSubscriptionOpenService | None = None,
) -> FastMCP:
    """Create the server with only implemented, typed Billy capabilities."""

    root = repository_root or Path.cwd()
    configuration = AppConfig.from_environment()
    client = BillyHttpClient(configuration.resolve_api_token)
    confirmations = ConfirmationStore()
    write_protocol = WriteProtocolService(client, confirmations)
    browser = BrowserRuntime(
        configuration.browser_profile,
        credential_references=configuration.browser_credentials,
    )
    checker = auth_status_checker or browser
    login_service = auth_login_service or browser
    invoices_list_service = ui_invoices_list_service or browser
    invoices_create_open_service = ui_invoices_create_open_service or browser
    products_list_service = ui_products_list_service or browser
    products_create_open_service = ui_products_create_open_service or browser
    clients_list_service = ui_clients_list_service or browser
    clients_create_open_service = ui_clients_create_open_service or browser
    clients_get_open_service = ui_clients_get_open_service or browser
    bank_accounts_list_service = ui_bank_accounts_list_service or browser
    quotes_list_service = ui_quotes_list_service or browser
    recurring_invoices_list_service = ui_recurring_invoices_list_service or browser
    products_import_service = ui_products_import_service or browser
    suppliers_list_service = ui_suppliers_list_service or browser
    suppliers_create_open_service = ui_suppliers_create_open_service or browser
    bills_list_service = ui_bills_list_service or browser
    bills_create_open_service = ui_bills_create_open_service or browser
    debtor_balances_list_service = ui_debtor_balances_list_service or browser
    creditor_balances_list_service = ui_creditor_balances_list_service or browser
    uploads_list_service = ui_uploads_list_service or browser
    receipt_inbox_list_service = ui_receipt_inbox_list_service or browser
    bank_reconciliation_open_service = ui_bank_reconciliation_open_service or browser
    financing_open_service = ui_financing_open_service or browser
    daybooks_open_service = ui_daybooks_open_service or browser
    transactions_list_service = ui_transactions_list_service or browser
    reports_open_service = ui_reports_open_service or browser
    vat_declarations_list_service = ui_vat_declarations_list_service or browser
    exports_open_service = ui_exports_open_service or browser
    saft_exports_open_service = ui_saft_exports_open_service or browser
    addons_open_service = ui_addons_open_service or browser
    integrations_open_service = ui_integrations_open_service or browser
    inventory_open_service = ui_inventory_open_service or browser
    settings_company_open_service = ui_settings_company_open_service or browser
    settings_accounting_open_service = ui_settings_accounting_open_service or browser
    settings_invoicing_open_service = ui_settings_invoicing_open_service or browser
    settings_user_open_service = ui_settings_user_open_service or browser
    settings_user_organizations_open_service = (
        ui_settings_user_organizations_open_service or browser
    )
    settings_vat_open_service = ui_settings_vat_open_service or browser
    settings_users_open_service = ui_settings_users_open_service or browser
    settings_access_token_open_service = ui_settings_access_token_open_service or browser
    settings_beta_open_service = ui_settings_beta_open_service or browser
    settings_subscription_open_service = ui_settings_subscription_open_service or browser
    server = FastMCP(
        "Billy MCP",
        instructions=(
            "Safety-first Billy coverage reporting, documented API reads, and "
            "confirmation-ticketed write previews and execution."
        ),
    )

    def coverage_status() -> GeneratedCoverageStatus | ToolError:
        try:
            return load_coverage_report(root).status
        except CoverageLoadError as failure:
            return failure.error

    def coverage_report() -> CoverageReport | ToolError:
        try:
            return load_coverage_report(root)
        except CoverageLoadError as failure:
            return failure.error

    async def auth_status() -> AuthStatusSuccess | ToolError:
        """Check only the known headless Billy login state without taking action."""

        AuthStatusInput()
        return await checker.auth_status()

    async def auth_login_start() -> AuthLoginStartSuccess | ToolError:
        """Start the fixed headless login transition with configured opaque references."""

        AuthLoginStartInput()
        return await login_service.auth_login_start()

    async def auth_login_wait() -> AuthLoginWaitSuccess | ToolError:
        """Observe login-required vs READY shell after a login transition begins."""

        AuthLoginWaitInput()
        return await login_service.auth_login_wait()

    async def ui_invoices_list() -> UiInvoicesListSuccess | ToolError:
        """Observe the authenticated Billy invoices list shell without writes."""

        UiInvoicesListInput()
        return await invoices_list_service.ui_invoices_list()

    async def ui_invoices_create_open() -> UiInvoicesCreateOpenSuccess | ToolError:
        """Observe the authenticated Billy invoice create form without submitting."""

        UiInvoicesCreateOpenInput()
        return await invoices_create_open_service.ui_invoices_create_open()

    async def ui_products_list() -> UiProductsListSuccess | ToolError:
        """Observe the authenticated Billy products list shell without writes."""

        UiProductsListInput()
        return await products_list_service.ui_products_list()

    async def ui_products_create_open() -> UiProductsCreateOpenSuccess | ToolError:
        """Observe the authenticated Billy products create form without submitting."""

        UiProductsCreateOpenInput()
        return await products_create_open_service.ui_products_create_open()

    async def ui_clients_list() -> UiClientsListSuccess | ToolError:
        """Observe the authenticated Billy clients list shell without writes."""

        UiClientsListInput()
        return await clients_list_service.ui_clients_list()

    async def ui_clients_create_open() -> UiClientsCreateOpenSuccess | ToolError:
        """Observe the authenticated Billy clients create form without submitting."""

        UiClientsCreateOpenInput()
        return await clients_create_open_service.ui_clients_create_open()

    async def ui_clients_get_open() -> UiClientsGetOpenSuccess | ToolError:
        """Observe an authenticated Billy client detail surface without submitting."""

        UiClientsGetOpenInput()
        return await clients_get_open_service.ui_clients_get_open()

    async def ui_suppliers_create_open() -> UiSuppliersCreateOpenSuccess | ToolError:
        """Observe the authenticated Billy suppliers create form without submitting."""

        UiSuppliersCreateOpenInput()
        return await suppliers_create_open_service.ui_suppliers_create_open()

    async def ui_bank_accounts_list() -> UiBankAccountsListSuccess | ToolError:
        """Observe the authenticated Billy bank accounts list shell without writes."""

        UiBankAccountsListInput()
        return await bank_accounts_list_service.ui_bank_accounts_list()

    async def ui_quotes_list() -> UiQuotesListSuccess | ToolError:
        """Observe the authenticated Billy quotes list shell without writes."""

        UiQuotesListInput()
        return await quotes_list_service.ui_quotes_list()

    async def ui_recurring_invoices_list() -> UiRecurringInvoicesListSuccess | ToolError:
        """Observe the authenticated Billy recurring invoices list shell without writes."""

        UiRecurringInvoicesListInput()
        return await recurring_invoices_list_service.ui_recurring_invoices_list()

    async def ui_products_import() -> UiProductsImportSuccess | ToolError:
        """Observe the Billy products import shell without file selection or upload."""

        UiProductsImportInput()
        return await products_import_service.ui_products_import()

    async def ui_suppliers_list() -> UiSuppliersListSuccess | ToolError:
        """Observe the authenticated Billy suppliers list shell without writes."""

        UiSuppliersListInput()
        return await suppliers_list_service.ui_suppliers_list()

    async def ui_bills_list() -> UiBillsListSuccess | ToolError:
        """Observe the authenticated Billy bills (purchases / Køb) list shell without writes."""

        UiBillsListInput()
        return await bills_list_service.ui_bills_list()

    async def ui_bills_create_open() -> UiBillsCreateOpenSuccess | ToolError:
        """Observe the authenticated Billy bill create form without submitting."""

        UiBillsCreateOpenInput()
        return await bills_create_open_service.ui_bills_create_open()

    async def ui_debtor_balances_list() -> UiDebtorBalancesListSuccess | ToolError:
        """Observe the authenticated Billy debtor balances list shell without writes."""

        UiDebtorBalancesListInput()
        return await debtor_balances_list_service.ui_debtor_balances_list()

    async def ui_creditor_balances_list() -> UiCreditorBalancesListSuccess | ToolError:
        """Observe the authenticated Billy creditor balances list shell without writes."""

        UiCreditorBalancesListInput()
        return await creditor_balances_list_service.ui_creditor_balances_list()

    async def ui_uploads_list() -> UiUploadsListSuccess | ToolError:
        """Observe the authenticated Billy uploads (Bilag) shell without writes or file pick."""

        UiUploadsListInput()
        return await uploads_list_service.ui_uploads_list()

    async def ui_receipt_inbox_list() -> UiReceiptInboxListSuccess | ToolError:
        """Observe the authenticated Billy receipt inbox (Bilagsindbakke) shell without writes."""

        UiReceiptInboxListInput()
        return await receipt_inbox_list_service.ui_receipt_inbox_list()

    async def ui_bank_reconciliation_open() -> UiBankReconciliationOpenSuccess | ToolError:
        """Observe the authenticated Billy bank reconciliation (Afstemning) shell without writes."""

        UiBankReconciliationOpenInput()
        return await bank_reconciliation_open_service.ui_bank_reconciliation_open()

    async def ui_financing_open() -> UiFinancingOpenSuccess | ToolError:
        """Observe the authenticated Billy financing shell without apply/submit actions."""

        UiFinancingOpenInput()
        return await financing_open_service.ui_financing_open()

    async def ui_daybooks_open() -> UiDaybooksOpenSuccess | ToolError:
        """Observe the authenticated Billy daybook editor shell without create/add-line actions."""

        UiDaybooksOpenInput()
        return await daybooks_open_service.ui_daybooks_open()

    async def ui_transactions_list() -> UiTransactionsListSuccess | ToolError:
        """Observe the authenticated Billy Posteringer list shell without create actions."""

        UiTransactionsListInput()
        return await transactions_list_service.ui_transactions_list()

    async def ui_reports_open() -> UiReportsOpenSuccess | ToolError:
        """Observe the authenticated Billy Rapporter hub shell without export actions."""

        UiReportsOpenInput()
        return await reports_open_service.ui_reports_open()

    async def ui_vat_declarations_list() -> UiVatDeclarationsListSuccess | ToolError:
        """Observe the authenticated Billy Momsangivelser list shell without write actions."""

        UiVatDeclarationsListInput()
        return await vat_declarations_list_service.ui_vat_declarations_list()

    async def ui_exports_open() -> UiExportsOpenSuccess | ToolError:
        """Observe the authenticated Billy Eksportér data hub shell without export actions."""

        UiExportsOpenInput()
        return await exports_open_service.ui_exports_open()

    async def ui_saft_exports_open() -> UiSaftExportsOpenSuccess | ToolError:
        """Observe SAF-T CTA on the exports hub without export or download actions."""

        UiSaftExportsOpenInput()
        return await saft_exports_open_service.ui_saft_exports_open()

    async def ui_addons_open() -> UiAddonsOpenSuccess | ToolError:
        """Observe the authenticated Billy Fordele (add-ons) hub without partner actions."""

        UiAddonsOpenInput()
        return await addons_open_service.ui_addons_open()

    async def ui_integrations_open() -> UiIntegrationsOpenSuccess | ToolError:
        """Classify the integrations soft-empty shell without partner actions."""

        UiIntegrationsOpenInput()
        return await integrations_open_service.ui_integrations_open()

    async def ui_inventory_open() -> UiInventoryOpenSuccess | ToolError:
        """Observe the authenticated Billy Lagermodul inventory shell without create actions."""

        UiInventoryOpenInput()
        return await inventory_open_service.ui_inventory_open()

    async def ui_settings_company_open() -> UiSettingsCompanyOpenSuccess | ToolError:
        """Observe the Indstillinger company settings panel without write actions."""

        UiSettingsCompanyOpenInput()
        return await settings_company_open_service.ui_settings_company_open()

    async def ui_settings_accounting_open() -> UiSettingsAccountingOpenSuccess | ToolError:
        """Observe the Indstillinger Regnskab settings panel without write actions."""

        UiSettingsAccountingOpenInput()
        return await settings_accounting_open_service.ui_settings_accounting_open()

    async def ui_settings_invoicing_open() -> UiSettingsInvoicingOpenSuccess | ToolError:
        """Observe the Indstillinger Faktura settings panel without write actions."""

        UiSettingsInvoicingOpenInput()
        return await settings_invoicing_open_service.ui_settings_invoicing_open()

    async def ui_settings_user_open() -> UiSettingsUserOpenSuccess | ToolError:
        """Observe the Indstillinger Profil settings panel without write actions."""

        UiSettingsUserOpenInput()
        return await settings_user_open_service.ui_settings_user_open()

    async def ui_settings_user_organizations_open() -> (
        UiSettingsUserOrganizationsOpenSuccess | ToolError
    ):
        """Observe the Indstillinger Virksomheder multi-org panel without write actions."""

        UiSettingsUserOrganizationsOpenInput()
        return await settings_user_organizations_open_service.ui_settings_user_organizations_open()

    async def ui_settings_vat_open() -> UiSettingsVatOpenSuccess | ToolError:
        """Observe the Indstillinger Momssatser settings panel without write actions."""

        UiSettingsVatOpenInput()
        return await settings_vat_open_service.ui_settings_vat_open()

    async def ui_settings_users_open() -> UiSettingsUsersOpenSuccess | ToolError:
        """Observe the Indstillinger Brugere settings panel without write actions."""

        UiSettingsUsersOpenInput()
        return await settings_users_open_service.ui_settings_users_open()

    async def ui_settings_access_token_open() -> UiSettingsAccessTokenOpenSuccess | ToolError:
        """Open the Billy Indstillinger Adgangsnøgler (access keys) settings panel (read-only)."""

        UiSettingsAccessTokenOpenInput()
        return await settings_access_token_open_service.ui_settings_access_token_open()

    async def ui_settings_beta_open() -> UiSettingsBetaOpenSuccess | ToolError:
        """Open the Billy Indstillinger Betas settings panel (read-only)."""

        UiSettingsBetaOpenInput()
        return await settings_beta_open_service.ui_settings_beta_open()

    async def ui_settings_subscription_open() -> UiSettingsSubscriptionOpenSuccess | ToolError:
        """Open the Billy Indstillinger Abonnement empty panel (read-only)."""

        UiSettingsSubscriptionOpenInput()
        return await settings_subscription_open_service.ui_settings_subscription_open()

    server.tool(name="coverage_status", description="Read generated Billy MCP coverage status.")(
        coverage_status
    )
    server.tool(name="coverage_report", description="Read typed Billy MCP coverage report rows.")(
        coverage_report
    )
    server.tool(
        name="auth_status",
        description="Read the narrowly verified headless Billy authentication status.",
    )(auth_status)
    server.tool(
        name="auth_login_start",
        description="Start the fixed headless Billy login transition using configured references.",
    )(auth_login_start)
    server.tool(
        name="auth_login_wait",
        description=(
            "Observe Billy session after login start: AUTH_REQUIRED login form or READY shell."
        ),
    )(auth_login_wait)
    server.tool(
        name="ui_invoices_list",
        description=(
            "Open the Billy invoices list shell for the authenticated session "
            "(read-only path and heading classification)."
        ),
    )(ui_invoices_list)
    server.tool(
        name="ui_invoices_create_open",
        description=(
            "Open the Billy invoice create form for the authenticated session "
            "(read-only form open; never submit, save, or send)."
        ),
    )(ui_invoices_create_open)
    server.tool(
        name="ui_products_list",
        description=(
            "Open the Billy products list shell for the authenticated session "
            "(read-only path and heading classification)."
        ),
    )(ui_products_list)
    server.tool(
        name="ui_products_create_open",
        description=(
            "Open the Billy products create form for the authenticated session "
            "(read-only form open via Lagermodul Opret produkt; never submit or save)."
        ),
    )(ui_products_create_open)
    server.tool(
        name="ui_clients_list",
        description=(
            "Open the Billy clients list shell for the authenticated session "
            "(read-only path and heading classification)."
        ),
    )(ui_clients_list)
    server.tool(
        name="ui_clients_create_open",
        description=(
            "Open the Billy clients create form for the authenticated session "
            "(read-only dialog form open; never submit or save)."
        ),
    )(ui_clients_create_open)
    server.tool(
        name="ui_clients_get_open",
        description=(
            "Open a Billy client (contact) detail surface for the authenticated session "
            "(read-only get/open; never submit, save, or delete)."
        ),
    )(ui_clients_get_open)
    server.tool(
        name="ui_bank_accounts_list",
        description=(
            "Open the Billy bank accounts list shell for the authenticated session "
            "(read-only path and heading classification)."
        ),
    )(ui_bank_accounts_list)
    server.tool(
        name="ui_quotes_list",
        description=(
            "Open the Billy quotes list shell for the authenticated session "
            "(read-only path and heading classification)."
        ),
    )(ui_quotes_list)
    server.tool(
        name="ui_recurring_invoices_list",
        description=(
            "Open the Billy recurring invoices list shell for the authenticated session "
            "(read-only path and heading classification)."
        ),
    )(ui_recurring_invoices_list)
    server.tool(
        name="ui_products_import",
        description=(
            "Open the Billy products import shell for the authenticated session "
            "(read-only path and heading classification; does not choose or upload files)."
        ),
    )(ui_products_import)
    server.tool(
        name="ui_suppliers_list",
        description=(
            "Open the Billy suppliers list shell for the authenticated session "
            "(read-only path and heading classification)."
        ),
    )(ui_suppliers_list)
    server.tool(
        name="ui_suppliers_create_open",
        description=(
            "Open the Billy suppliers create form for the authenticated session "
            "(read-only dialog form open; never submit or save)."
        ),
    )(ui_suppliers_create_open)
    server.tool(
        name="ui_bills_list",
        description=(
            "Open the Billy bills (purchases) list shell for the authenticated session "
            "(read-only path and heading classification)."
        ),
    )(ui_bills_list)
    server.tool(
        name="ui_bills_create_open",
        description=(
            "Open the Billy bill create form for the authenticated session "
            "(read-only form open; never submit, save, or upload)."
        ),
    )(ui_bills_create_open)
    server.tool(
        name="ui_debtor_balances_list",
        description=(
            "Open the Billy debtor balances list shell for the authenticated session "
            "(read-only path and heading classification)."
        ),
    )(ui_debtor_balances_list)
    server.tool(
        name="ui_creditor_balances_list",
        description=(
            "Open the Billy creditor balances list shell for the authenticated session "
            "(read-only path and heading classification)."
        ),
    )(ui_creditor_balances_list)
    server.tool(
        name="ui_uploads_list",
        description=(
            "Open the Billy uploads (Bilag) list shell for the authenticated session "
            "(read-only path and heading classification; does not choose or upload files)."
        ),
    )(ui_uploads_list)
    server.tool(
        name="ui_receipt_inbox_list",
        description=(
            "Open the Billy receipt inbox (Bilagsindbakke / vouchers) list shell for the "
            "authenticated session (read-only path and heading classification; does not "
            "choose files or click edit actions)."
        ),
    )(ui_receipt_inbox_list)
    server.tool(
        name="ui_bank_reconciliation_open",
        description=(
            "Open the Billy bank reconciliation (Afstemning) shell for the authenticated "
            "session (read-only path classification via nav harvest; does not connect "
            "bank, import transactions, or match lines)."
        ),
    )(ui_bank_reconciliation_open)
    server.tool(
        name="ui_financing_open",
        description=(
            "Open the Billy financing (Ansøg om erhvervslån) shell for the authenticated "
            "session (read-only path and heading classification; does not apply for a "
            "loan or submit partner financing)."
        ),
    )(ui_financing_open)
    server.tool(
        name="ui_daybooks_open",
        description=(
            "Open the Billy daybook editor (Kassekladde) shell for the authenticated "
            "session (read-only path and marker classification; does not create daybooks, "
            "add lines, or post entries)."
        ),
    )(ui_daybooks_open)
    server.tool(
        name="ui_transactions_list",
        description=(
            "Open the Billy transactions (Posteringer) list shell for the authenticated "
            "session (read-only path and heading classification; does not create, post, "
            "void, or delete transactions)."
        ),
    )(ui_transactions_list)
    server.tool(
        name="ui_reports_open",
        description=(
            "Open the Billy reports (Rapporter) hub shell for the authenticated "
            "session (read-only path and heading classification; does not export, "
            "download, or generate reports)."
        ),
    )(ui_reports_open)
    server.tool(
        name="ui_vat_declarations_list",
        description=(
            "Open the Billy VAT declarations (Momsangivelser) list shell for the "
            "authenticated session (read-only path and heading classification; does "
            "not declare, submit, export, or create VAT returns)."
        ),
    )(ui_vat_declarations_list)
    server.tool(
        name="ui_exports_open",
        description=(
            "Open the Billy exports (Eksportér data) hub shell for the authenticated "
            "session (read-only path and heading classification; does not export, "
            "download, or run SAF-T export)."
        ),
    )(ui_exports_open)
    server.tool(
        name="ui_saft_exports_open",
        description=(
            "Open the Billy exports hub and verify the SAF-T export control is present "
            "for the authenticated session (read-only; does not click Eksportér som "
            "SAF-T, Eksport, or Download)."
        ),
    )(ui_saft_exports_open)
    server.tool(
        name="ui_addons_open",
        description=(
            "Open the Billy add-ons (Fordele) hub shell for the authenticated session "
            "(read-only path and heading classification; does not install, connect, "
            "create access keys, or open partner destinations)."
        ),
    )(ui_addons_open)
    server.tool(
        name="ui_integrations_open",
        description=(
            "Classify the Billy integrations soft-empty shell for the authenticated "
            "session (path /:org_slug/integrations only; not Fordele; does not open "
            "marketing apps, install partners, or navigate off mit.billy.dk)."
        ),
    )(ui_integrations_open)
    server.tool(
        name="ui_inventory_open",
        description=(
            "Open the Billy inventory (Lagermodul) shell for the authenticated session "
            "(read-only path and heading classification; does not click Opret primo, "
            "Opret produkt, Opret status, or other create actions)."
        ),
    )(ui_inventory_open)
    server.tool(
        name="ui_settings_company_open",
        description=(
            "Open the Billy company settings (Indstillinger / Virksomhed) shell for the "
            "authenticated session (read-only path, heading, and company panel markers; "
            "does not click Gem, Tilføj ejer, upload, or other write actions)."
        ),
    )(ui_settings_company_open)
    server.tool(
        name="ui_settings_accounting_open",
        description=(
            "Open the Billy accounting settings (Indstillinger / Regnskab) panel for the "
            "authenticated session (read-only path, heading, and accounting panel markers; "
            "does not click Gem, Sæt låsedato, or other write actions)."
        ),
    )(ui_settings_accounting_open)
    server.tool(
        name="ui_settings_invoicing_open",
        description=(
            "Open the Billy invoicing settings (Indstillinger / Faktura) panel for the "
            "authenticated session (read-only path, heading, and invoicing panel markers; "
            "does not click Gem, Opret betalingsmetode, Upload, or other write actions)."
        ),
    )(ui_settings_invoicing_open)
    server.tool(
        name="ui_settings_user_open",
        description=(
            "Open the Billy user settings (Indstillinger / Profil) panel for the "
            "authenticated session (read-only path, heading, and user panel markers; "
            "does not click Gem, Upload, password submit, or other write actions)."
        ),
    )(ui_settings_user_open)
    server.tool(
        name="ui_settings_user_organizations_open",
        description=(
            "Open the Billy user-organizations settings (Indstillinger / Virksomheder) "
            "panel for the authenticated session (read-only path, heading, and multi-org "
            "list markers; does not click Opret organisation, Gem, or other write actions)."
        ),
    )(ui_settings_user_organizations_open)
    server.tool(
        name="ui_settings_vat_open",
        description=(
            "Open the Billy VAT settings (Indstillinger / Momssatser) panel for the "
            "authenticated session (read-only path, heading, and VAT panel markers; "
            "does not click Opret, Gem, or other write actions)."
        ),
    )(ui_settings_vat_open)
    server.tool(
        name="ui_settings_users_open",
        description=(
            "Open the Billy org users settings (Indstillinger / Brugere) panel for the "
            "authenticated session (read-only path, heading, and users panel markers; "
            "does not click Invitér, Overdrag, Gem, or other write actions)."
        ),
    )(ui_settings_users_open)

    server.tool(
        name="ui_settings_access_token_open",
        description=(
            "Open the Billy access-token settings (Indstillinger / Adgangsnøgler) panel "
            "for the authenticated session (read-only path, heading, and access-token "
            "panel markers; does not click Opret adgangsnøgle, Gem, or other write actions)."
        ),
    )(ui_settings_access_token_open)

    server.tool(
        name="ui_settings_beta_open",
        description=(
            "Open the Billy betas settings (Indstillinger / Betas) panel for the "
            "authenticated session (read-only path, heading, and betas panel markers; "
            "does not click Opret, Gem, or other write actions)."
        ),
    )(ui_settings_beta_open)
    server.tool(
        name="ui_settings_subscription_open",
        description=(
            "Open the Billy subscription settings (Indstillinger / Abonnement) empty "
            "panel for the authenticated session (read-only path, heading, and empty-"
            "panel classification; does not click Opgrader, Skift abonnement, Betal, "
            "Køb, Gem, or other write actions)."
        ),
    )(ui_settings_subscription_open)
    register_bootstrap_read_tools(server, client)
    register_reference_reads(server, client)
    register_catalog_read_tools(server, client)
    register_contact_read_tools(server, client)
    register_invoice_read_tools(server, client)
    register_invoice_log_read_tools(server, client)
    register_bill_read_tools(server, client)
    register_daybook_transaction_read_tools(server, client)
    register_line_read_tools(server, client)
    register_contact_person_read_tools(server, client)
    register_daybook_read_tools(server, client)
    register_account_read_tools(server, client)
    register_file_attachment_read_tools(server, client)
    register_file_upload_tools(server, client, configuration, confirmations)
    register_invoice_email_delivery_write_tools(server, client, configuration, confirmations)
    register_geo_read_tools(server, client)
    register_tax_read_tools(server, client)
    register_bank_read_tools(server, client)
    register_balance_invoice_extension_read_tools(server, client)
    register_ledger_user_read_tools(server, client)
    register_contact_write_tools(server, client, write_protocol)
    register_contact_person_write_tools(server, client, write_protocol)
    register_catalog_write_tools(server, client, write_protocol)
    register_daybook_write_tools(server, client, write_protocol)
    register_account_write_tools(server, client, write_protocol)
    register_daybook_balance_account_write_tools(server, client, write_protocol)
    register_daybook_transaction_write_tools(server, client, write_protocol)
    register_daybook_transaction_line_write_tools(server, client, write_protocol)
    register_invoice_write_tools(server, client, write_protocol)
    register_invoice_line_write_tools(server, client, write_protocol)
    register_bill_write_tools(server, client, write_protocol)
    register_bill_line_write_tools(server, client, write_protocol)
    register_tax_write_tools(server, client, write_protocol)
    register_sales_tax_write_tools(server, client, write_protocol)
    register_sales_tax_account_meta_write_tools(server, client, write_protocol)
    register_attachment_write_tools(server, client, write_protocol)
    register_bank_line_write_tools(server, client, write_protocol)
    register_bank_payment_write_tools(server, client, write_protocol)
    register_sales_tax_payment_write_tools(server, client, write_protocol)
    register_contact_balance_payment_write_tools(server, client, write_protocol)
    register_invoice_late_fee_write_tools(server, client, write_protocol)
    register_invoice_reminder_write_tools(server, client, write_protocol)
    register_organization_write_tools(server, client, write_protocol)
    register_user_write_tools(server, client, write_protocol)
    register_sales_tax_return_write_tools(server, client, write_protocol)
    return server


server = create_server()


def main() -> None:
    """Run the one stdio MCP process."""

    server.run(transport="stdio")
