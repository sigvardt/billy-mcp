"""The Billy FastMCP stdio shell with real coverage and read-only API tools."""

from __future__ import annotations

from pathlib import Path

from fastmcp import FastMCP

from billy_mcp.api.bill_reads import register_bill_read_tools
from billy_mcp.api.bootstrap_reads import register_bootstrap_read_tools
from billy_mcp.api.catalog_reads import register_catalog_read_tools
from billy_mcp.api.contact_reads import register_contact_read_tools
from billy_mcp.api.daybook_transaction_reads import register_daybook_transaction_read_tools
from billy_mcp.api.invoice_reads import register_invoice_read_tools
from billy_mcp.api.reference_reads import register_reference_reads
from billy_mcp.client import BillyHttpClient
from billy_mcp.config import AppConfig
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
    server = FastMCP(
        "Billy MCP",
        instructions="Safety-first Billy coverage reporting and documented read-only API access.",
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
    return server


server = create_server()


def main() -> None:
    """Run the one stdio MCP process."""

    server.run(transport="stdio")
