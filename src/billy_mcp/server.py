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
    UiInvoicesListService,
    UiProductsListService,
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
    UiInvoicesListInput,
    UiInvoicesListSuccess,
    UiProductsListInput,
    UiProductsListSuccess,
)


def create_server(
    repository_root: Path | None = None,
    *,
    auth_status_checker: AuthStatusChecker | None = None,
    auth_login_service: AuthLoginService | None = None,
    ui_invoices_list_service: UiInvoicesListService | None = None,
    ui_products_list_service: UiProductsListService | None = None,
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
    products_list_service = ui_products_list_service or browser
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

    async def ui_products_list() -> UiProductsListSuccess | ToolError:
        """Observe the authenticated Billy products list shell without writes."""

        UiProductsListInput()
        return await products_list_service.ui_products_list()

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
        name="ui_products_list",
        description=(
            "Open the Billy products list shell for the authenticated session "
            "(read-only path and heading classification)."
        ),
    )(ui_products_list)
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
