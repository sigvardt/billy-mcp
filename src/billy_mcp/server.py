"""The Phase 0 FastMCP stdio shell: only real typed coverage tools are exposed."""

from __future__ import annotations

from pathlib import Path

from fastmcp import FastMCP

from billy_mcp.coverage import (
    CoverageLoadError,
    CoverageReport,
    GeneratedCoverageStatus,
    load_coverage_report,
)
from billy_mcp.models import ToolError


def create_server(repository_root: Path | None = None) -> FastMCP:
    """Create a server whose two registered tools are backed by real coverage data."""

    root = repository_root or Path.cwd()
    server = FastMCP("Billy MCP", instructions="Safety-first Billy coverage reporting.")

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
    return server


server = create_server()


def main() -> None:
    """Run the one stdio MCP process."""

    server.run(transport="stdio")
