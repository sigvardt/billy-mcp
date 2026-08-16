"""Ticketed UI bill write tools. Filled by the bills write child."""

from __future__ import annotations

from fastmcp import FastMCP

from billy_mcp.ui_writes.protocol import UiWriteProtocol


def register_ui_bill_write_tools(server: FastMCP, protocol: UiWriteProtocol) -> None:
    """Register UI bill preview/execute tools when the family lands."""

    del server, protocol
