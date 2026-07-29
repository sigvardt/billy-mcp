"""The Billy FastMCP stdio shell with coverage, reads, and ticketed writes."""

from __future__ import annotations

from pathlib import Path

from fastmcp import FastMCP

from billy_mcp.api.account_reads import register_account_read_tools
from billy_mcp.api.account_writes import register_account_write_tools
from billy_mcp.api.balance_invoice_ext_reads import register_balance_invoice_extension_read_tools
from billy_mcp.api.bank_reads import register_bank_read_tools
from billy_mcp.api.bill_line_writes import register_bill_line_write_tools
from billy_mcp.api.bill_reads import register_bill_read_tools
from billy_mcp.api.bill_writes import register_bill_write_tools
from billy_mcp.api.bootstrap_reads import register_bootstrap_read_tools
from billy_mcp.api.catalog_reads import register_catalog_read_tools
from billy_mcp.api.catalog_writes import register_catalog_write_tools
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
from billy_mcp.api.geo_reads import register_geo_read_tools
from billy_mcp.api.invoice_line_writes import register_invoice_line_write_tools
from billy_mcp.api.invoice_reads import register_invoice_read_tools
from billy_mcp.api.invoice_writes import register_invoice_write_tools
from billy_mcp.api.ledger_user_reads import register_ledger_user_read_tools
from billy_mcp.api.line_reads import register_line_read_tools
from billy_mcp.api.reference_reads import register_reference_reads
from billy_mcp.api.sales_tax_writes import register_sales_tax_write_tools
from billy_mcp.api.tax_reads import register_tax_read_tools
from billy_mcp.api.tax_writes import register_tax_write_tools
from billy_mcp.api.write_protocol import WriteProtocolService
from billy_mcp.client import BillyHttpClient
from billy_mcp.config import AppConfig
from billy_mcp.confirmations import ConfirmationStore
from billy_mcp.coverage import (
    CoverageLoadError,
    CoverageReport,
    GeneratedCoverageStatus,
    load_coverage_report,
)
from billy_mcp.models import ToolError


def create_server(repository_root: Path | None = None) -> FastMCP:
    """Create the server with only implemented, typed Billy capabilities."""

    root = repository_root or Path.cwd()
    configuration = AppConfig.from_environment()
    client = BillyHttpClient(configuration.resolve_api_token)
    confirmations = ConfirmationStore()
    write_protocol = WriteProtocolService(client, confirmations)
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

    server.tool(name="coverage_status", description="Read generated Billy MCP coverage status.")(
        coverage_status
    )
    server.tool(name="coverage_report", description="Read typed Billy MCP coverage report rows.")(
        coverage_report
    )
    register_bootstrap_read_tools(server, client)
    register_reference_reads(server, client)
    register_catalog_read_tools(server, client)
    register_contact_read_tools(server, client)
    register_invoice_read_tools(server, client)
    register_bill_read_tools(server, client)
    register_daybook_transaction_read_tools(server, client)
    register_line_read_tools(server, client)
    register_contact_person_read_tools(server, client)
    register_daybook_read_tools(server, client)
    register_account_read_tools(server, client)
    register_file_attachment_read_tools(server, client)
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
    return server


server = create_server()


def main() -> None:
    """Run the one stdio MCP process."""

    server.run(transport="stdio")
