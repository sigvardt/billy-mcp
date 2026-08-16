"""Ticketed UI product write tools. Filled by the products write child."""

from __future__ import annotations

from fastmcp import FastMCP

from billy_mcp.ui_writes.protocol import UiWriteProtocol


def register_ui_product_write_tools(server: FastMCP, protocol: UiWriteProtocol) -> None:
    """Register UI product preview/execute tools when the family lands."""

    del server, protocol
