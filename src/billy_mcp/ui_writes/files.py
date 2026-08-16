"""Ticketed UI file write tools. Filled by the files write child."""

from __future__ import annotations

from fastmcp import FastMCP

from billy_mcp.ui_writes.protocol import UiWriteProtocol


def register_ui_file_write_tools(server: FastMCP, protocol: UiWriteProtocol) -> None:
    """Register UI file preview/execute tools when the family lands."""

    del server, protocol
