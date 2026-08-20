"""Contract tests for ticketed singular transactions delete."""

from __future__ import annotations

import asyncio
from collections.abc import Callable
from typing import cast

import httpx
import pytest
from fastmcp import FastMCP
from fastmcp.exceptions import ValidationError as FastMcpValidationError
from pydantic import ValidationError

from billy_mcp.api.transaction_writes import (
    TransactionDeletePreviewInput,
    register_transaction_write_tools,
)
from billy_mcp.api.write_protocol import WriteExecuteInput, WriteProtocolService
from billy_mcp.client import BillyHttpClient
from billy_mcp.confirmations import ConfirmationStore

MockHandler = Callable[[httpx.Request], httpx.Response]

DELETE_PREVIEW = "api_transactions_delete_preview"
DELETE_EXECUTE = "api_transactions_delete_execute"


def make_server(
    handler: MockHandler,
    *,
    token: str | None = "transaction-delete-test-token",
    confirmations: ConfirmationStore | None = None,
) -> tuple[FastMCP, list[httpx.Request], WriteProtocolService]:
    """Create a fully local FastMCP server with a recording locked client."""

    requests: list[httpx.Request] = []

    def recording_handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        return handler(request)

    client = BillyHttpClient(lambda: token, transport=httpx.MockTransport(recording_handler))
    protocol = WriteProtocolService(client, confirmations or ConfirmationStore())
    server = FastMCP("transaction-delete-contract-test")
    register_transaction_write_tools(server, client, protocol)
    return server, requests, protocol


def call_tool(server: FastMCP, tool_name: str, arguments: dict[str, object]) -> dict[str, object]:
    """Call one typed tool with its direct MCP argument object."""

    result = asyncio.run(server.call_tool(tool_name, arguments))
    structured_content = result.structured_content
    assert isinstance(structured_content, dict)
    structured_result = structured_content.get("result", structured_content)
    assert isinstance(structured_result, dict)
    return cast(dict[str, object], structured_result)


def test_registers_two_tools_and_delete_preview_is_id_only() -> None:
    server, _, _ = make_server(lambda request: httpx.Response(200, json={}))

    by_name = {tool.name: tool for tool in asyncio.run(server.list_tools())}
    assert set(by_name) == {DELETE_PREVIEW, DELETE_EXECUTE}
    schema = by_name[DELETE_PREVIEW].parameters
    properties = schema["properties"]
    assert schema["additionalProperties"] is False
    assert set(properties) == {"id"}
    assert "input" not in properties
    assert "transaction" not in properties
    assert properties["id"]["minLength"] == 1
    execute_schema = by_name[DELETE_EXECUTE].parameters
    execute_properties = execute_schema["properties"]
    assert execute_schema["additionalProperties"] is False
    assert set(execute_properties) == {"confirmation_ticket"}
    assert execute_properties["confirmation_ticket"]["minLength"] == 1


@pytest.mark.parametrize(
    ("input_model", "payload"),
    [
        (TransactionDeletePreviewInput, {"id": "txn-1", "extra": True}),
        (TransactionDeletePreviewInput, {"id": ""}),
        (TransactionDeletePreviewInput, {"id": "txn-1", "transaction": {"voucherNo": "1"}}),
        (WriteExecuteInput, {"confirmation_ticket": "ticket", "id": "txn-1"}),
    ],
)
def test_delete_inputs_forbid_extras_empty_id_and_nested_payload(
    input_model: type[TransactionDeletePreviewInput] | type[WriteExecuteInput],
    payload: dict[str, object],
) -> None:
    with pytest.raises(ValidationError):
        input_model.model_validate(payload)


@pytest.mark.parametrize(
    "arguments",
    [
        {"id": ""},
        {"id": "txn-1", "extra": True},
        {"id": "txn-1", "transaction": {"voucherNo": "1"}},
    ],
)
def test_delete_preview_rejects_empty_id_extras_and_nested_payload_without_http(
    arguments: dict[str, object],
) -> None:
    server, requests, _ = make_server(
        lambda request: pytest.fail(f"preview made an HTTP request: {request.method} {request.url}")
    )

    with pytest.raises(FastMcpValidationError):
        asyncio.run(server.call_tool(DELETE_PREVIEW, arguments))

    assert requests == []


def test_delete_preview_is_mutation_free_and_binds_id_only() -> None:
    server, requests, _ = make_server(
        lambda request: pytest.fail(f"preview made an HTTP request: {request.method} {request.url}")
    )

    preview = call_tool(server, DELETE_PREVIEW, {"id": "txn-1"})

    assert requests == []
    assert preview["canonical_request"] == {"id": "txn-1"}
    assert preview["expected_effect_state"] == {
        "action": "delete",
        "resource": "transaction",
        "id": "txn-1",
    }
    assert isinstance(preview["confirmation_ticket"], str)
