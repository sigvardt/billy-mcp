"""Integration tests for shared tickets across bill write modules."""

from __future__ import annotations

import asyncio
from typing import cast

import httpx
from fastmcp import FastMCP

from billy_mcp.api.bill_line_writes import register_bill_line_write_tools
from billy_mcp.api.bill_writes import register_bill_write_tools
from billy_mcp.api.write_protocol import WriteProtocolService
from billy_mcp.client import BillyHttpClient
from billy_mcp.confirmations import ConfirmationStore
from billy_mcp.models import StableErrorCode


def call_tool(server: FastMCP, tool_name: str, arguments: dict[str, object]) -> dict[str, object]:
    """Call one typed MCP tool and return its structured payload."""

    result = asyncio.run(server.call_tool(tool_name, arguments))
    structured_content = result.structured_content
    assert isinstance(structured_content, dict)
    payload = structured_content.get("result", structured_content)
    assert isinstance(payload, dict)
    return cast(dict[str, object], payload)


def test_shared_service_rejects_cross_module_executors_without_consuming_tickets() -> None:
    """A ticket remains usable only by its exact bill or bill-line executor."""

    requests: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        if request.url.path == "/v2/bills":
            return httpx.Response(200, json={"bills": [{"id": "bill-1"}]})
        if request.url.path == "/v2/billLines":
            return httpx.Response(200, json={"billLines": [{"id": "line-1"}]})
        raise AssertionError(f"unexpected request: {request.method} {request.url}")

    client = BillyHttpClient(
        lambda: "cross-executor-test-token",
        transport=httpx.MockTransport(handler),
    )
    server = FastMCP("bill-cross-executor-test")
    write_protocol = WriteProtocolService(client, ConfirmationStore())
    register_bill_write_tools(server, client, write_protocol)
    register_bill_line_write_tools(server, client, write_protocol)

    bill_preview = call_tool(
        server,
        "api_bills_create_preview",
        {"bill": {"contactId": "contact-1"}},
    )
    line_mismatch = call_tool(
        server,
        "api_bill_lines_delete_execute",
        {"confirmation_ticket": bill_preview["confirmation_ticket"]},
    )
    assert line_mismatch["code"] == StableErrorCode.CONFIRMATION_MISMATCH
    assert requests == []

    bill_execution = call_tool(
        server,
        "api_bills_create_execute",
        {"confirmation_ticket": bill_preview["confirmation_ticket"]},
    )
    assert bill_execution["changed_records"] == {"bills": [{"id": "bill-1"}]}
    assert len(requests) == 1

    line_preview = call_tool(
        server,
        "api_bill_lines_create_preview",
        {"billLine": {"accountId": "account-1", "amount": 100, "billId": "bill-1"}},
    )
    bill_mismatch = call_tool(
        server,
        "api_bills_delete_execute",
        {"confirmation_ticket": line_preview["confirmation_ticket"]},
    )
    assert bill_mismatch["code"] == StableErrorCode.CONFIRMATION_MISMATCH
    assert len(requests) == 1

    line_execution = call_tool(
        server,
        "api_bill_lines_create_execute",
        {"confirmation_ticket": line_preview["confirmation_ticket"]},
    )
    assert line_execution["changed_records"] == {"billLines": [{"id": "line-1"}]}
    assert len(requests) == 2
