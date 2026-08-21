"""Integration tests for shared tickets across daybook transaction write modules."""

from __future__ import annotations

import asyncio
from typing import cast

import httpx
from fastmcp import FastMCP

from billy_mcp.api.daybook_transaction_line_writes import (
    register_daybook_transaction_line_write_tools,
)
from billy_mcp.api.daybook_transaction_writes import register_daybook_transaction_write_tools
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
    """A ticket remains usable only by its exact executor across both registrars."""

    requests: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        if request.url.path == "/v2/daybookTransactions":
            return httpx.Response(200, json={"daybookTransactions": [{"id": "transaction-1"}]})
        if request.url.path == "/v2/daybookTransactionLines":
            return httpx.Response(200, json={"daybookTransactionLines": [{"id": "line-1"}]})
        raise AssertionError(f"unexpected request: {request.method} {request.url}")

    client = BillyHttpClient(
        lambda: "cross-executor-test-token",
        transport=httpx.MockTransport(handler),
    )
    server = FastMCP("daybook-transaction-cross-executor-test")
    write_protocol = WriteProtocolService(client, ConfirmationStore())
    register_daybook_transaction_write_tools(server, client, write_protocol)
    register_daybook_transaction_line_write_tools(server, client, write_protocol)

    transaction_preview = call_tool(
        server,
        "api_daybook_transactions_create_preview",
        {"daybookTransaction": {"entryDate": "2026-07-29"}},
    )
    line_mismatch = call_tool(
        server,
        "api_daybook_transaction_lines_delete_execute",
        {"confirmation_ticket": transaction_preview["confirmation_ticket"]},
    )
    assert line_mismatch["code"] == StableErrorCode.CONFIRMATION_MISMATCH
    assert requests == []

    transaction_execution = call_tool(
        server,
        "api_daybook_transactions_create_execute",
        {"confirmation_ticket": transaction_preview["confirmation_ticket"]},
    )
    assert transaction_execution["changed_records"] == {
        "daybookTransactions": [{"id": "transaction-1"}]
    }
    assert len(requests) == 1

    line_preview = call_tool(
        server,
        "api_daybook_transaction_lines_create_preview",
        {"daybookTransactionLine": {"amount": 100}},
    )
    transaction_mismatch = call_tool(
        server,
        "api_daybook_transactions_delete_execute",
        {"confirmation_ticket": line_preview["confirmation_ticket"]},
    )
    assert transaction_mismatch["code"] == StableErrorCode.CONFIRMATION_MISMATCH
    assert len(requests) == 1

    line_execution = call_tool(
        server,
        "api_daybook_transaction_lines_create_execute",
        {"confirmation_ticket": line_preview["confirmation_ticket"]},
    )
    assert line_execution["changed_records"] == {"daybookTransactionLines": [{"id": "line-1"}]}
    assert len(requests) == 2
