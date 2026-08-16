"""Live-slot blocker for UI bill writes. Not a skipped submit."""

from __future__ import annotations

from typing import cast

import anyio
from fastmcp import FastMCP

from billy_mcp.confirmations import ConfirmationStore
from billy_mcp.models import StableErrorCode
from billy_mcp.ui_writes.bills import LIVE_SLOT_BLOCKER_MESSAGE, register_ui_bill_write_tools
from billy_mcp.ui_writes.protocol import UiWriteProtocol


def _server() -> FastMCP:
    server = FastMCP("ui-bills-write-live-slot-blocker")
    register_ui_bill_write_tools(server, UiWriteProtocol(ConfirmationStore()))
    return server


def _call(server: FastMCP, tool_name: str, arguments: dict[str, str]) -> dict[str, object]:
    result = anyio.run(server.call_tool, tool_name, arguments)
    structured_content = result.structured_content
    assert isinstance(structured_content, dict)
    payload = structured_content.get("result", structured_content)
    assert isinstance(payload, dict)
    return cast(dict[str, object], payload)


def test_live_submit_refused_until_root_slot() -> None:
    """Preview issues a ticket. Execute refuses live submit. No browser, no HTTP."""

    assert "BrowserRuntime" not in globals()
    server = _server()
    preview = _call(server, "ui_bills_create_preview", {"unique_tag": "MCP-BILL-LIVE-BLOCK"})
    ticket = cast(str, preview["confirmation_ticket"])
    assert ticket
    blocked = _call(server, "ui_bills_create_execute", {"confirmation_ticket": ticket})
    assert blocked["code"] == StableErrorCode.VALIDATION_ERROR
    message = cast(str, blocked["message"])
    assert "9F2EC46E" in message
    assert "Contacts" in message
    assert LIVE_SLOT_BLOCKER_MESSAGE == message
