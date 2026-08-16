"""Live-marked fail-closed proof for UI ledger writes.

This is not an unsafe skip. Execute is defined as ticket consume plus refuse
mutation until root grants a live slot and injects a submitter. FastMCP
`call_tool` is the qualification path. BrowserRuntime is not used.
"""

from __future__ import annotations

import asyncio

import pytest
from fastmcp import FastMCP

from billy_mcp.confirmations import ConfirmationStore
from billy_mcp.ui_writes.ledger import LEDGER_SUBMIT_BLOCKER, register_ui_ledger_write_tools
from billy_mcp.ui_writes.protocol import UiWriteProtocol

pytestmark = pytest.mark.live


def _server() -> FastMCP:
    server = FastMCP("ui-ledger-write-live-blocker")
    register_ui_ledger_write_tools(server, UiWriteProtocol(ConfirmationStore()))
    return server


def _call(server: FastMCP, tool_name: str, arguments: dict[str, object]) -> dict[str, object]:
    result = asyncio.run(server.call_tool(tool_name, arguments))
    structured_content = result.structured_content
    assert isinstance(structured_content, dict)
    payload = structured_content.get("result", structured_content)
    assert isinstance(payload, dict)
    return payload


def test_live_daybook_create_execute_is_fail_closed_not_an_unsafe_skip() -> None:
    server = _server()
    preview = _call(
        server,
        "ui_daybooks_create_preview",
        {"name": "MCP-LEDGER-LIVE-BLOCKER"},
    )
    execution = _call(
        server,
        "ui_daybooks_create_execute",
        {"confirmation_ticket": preview["confirmation_ticket"]},
    )

    assert execution["submitted"] is False
    assert execution["blocker"] == LEDGER_SUBMIT_BLOCKER
    assert "7696B03D" in LEDGER_SUBMIT_BLOCKER
    assert "no browser or HTTP submitter" in LEDGER_SUBMIT_BLOCKER
    assert "BrowserRuntime" not in repr(execution)
