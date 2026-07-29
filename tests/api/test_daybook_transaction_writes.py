"""Contract tests for ticketed singular Billy daybook-transaction write tools."""

from __future__ import annotations

import asyncio
import json
from collections.abc import Callable
from datetime import UTC, datetime, timedelta
from typing import cast

import httpx
import pytest
from fastmcp import FastMCP
from pydantic import ValidationError

from billy_mcp.api.daybook_transaction_writes import (
    DaybookTransactionCreatePreviewInput,
    DaybookTransactionDeletePreviewInput,
    DaybookTransactionUpdatePreviewInput,
    register_daybook_transaction_write_tools,
)
from billy_mcp.api.write_protocol import (
    WriteExecuteInput,
    WriteMethod,
    WriteOperationSpec,
    WriteProtocolService,
    confirmation_binding_for,
)
from billy_mcp.client import BillyHttpClient
from billy_mcp.confirmations import ConfirmationFailure, ConfirmationStore
from billy_mcp.models import StableErrorCode

MockHandler = Callable[[httpx.Request], httpx.Response]


class Clock:
    """Controllable confirmation clock used only by local ticket-expiry tests."""

    def __init__(self) -> None:
        self.now = datetime(2026, 7, 29, tzinfo=UTC)

    def __call__(self) -> datetime:
        return self.now


def make_server(
    handler: MockHandler,
    *,
    token: str | None = "daybook-transaction-write-test-token",
    confirmations: ConfirmationStore | None = None,
) -> tuple[FastMCP, list[httpx.Request]]:
    """Create a fully local FastMCP server with a recording locked client."""

    requests: list[httpx.Request] = []

    def recording_handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        return handler(request)

    client = BillyHttpClient(
        lambda: token,
        transport=httpx.MockTransport(recording_handler),
    )
    server = FastMCP("daybook-transaction-write-contract-test")
    register_daybook_transaction_write_tools(
        server,
        client,
        WriteProtocolService(client, confirmations or ConfirmationStore()),
    )
    return server, requests


def call_tool(server: FastMCP, tool_name: str, arguments: dict[str, object]) -> dict[str, object]:
    """Call one typed tool with its direct MCP argument object."""

    result = asyncio.run(server.call_tool(tool_name, arguments))
    structured_content = result.structured_content
    assert isinstance(structured_content, dict)
    structured_result = structured_content.get("result", structured_content)
    assert isinstance(structured_result, dict)
    return cast(dict[str, object], structured_result)


def test_registers_exactly_six_flat_typed_daybook_transaction_write_tools() -> None:
    server, _ = make_server(lambda request: httpx.Response(200, json={}))

    by_name = {tool.name: tool for tool in asyncio.run(server.list_tools())}

    assert set(by_name) == {
        "api_daybook_transactions_create_preview",
        "api_daybook_transactions_create_execute",
        "api_daybook_transactions_update_preview",
        "api_daybook_transactions_update_execute",
        "api_daybook_transactions_delete_preview",
        "api_daybook_transactions_delete_execute",
    }
    expected_properties = {
        "api_daybook_transactions_create_preview": {"daybookTransaction"},
        "api_daybook_transactions_create_execute": {"confirmation_ticket"},
        "api_daybook_transactions_update_preview": {"daybookTransaction", "id"},
        "api_daybook_transactions_update_execute": {"confirmation_ticket"},
        "api_daybook_transactions_delete_preview": {"id"},
        "api_daybook_transactions_delete_execute": {"confirmation_ticket"},
    }
    for name, fields in expected_properties.items():
        schema = by_name[name].parameters
        properties = cast(dict[str, object], schema["properties"])
        assert schema["additionalProperties"] is False
        assert set(properties) == fields
        assert "input" not in properties

    for name, field in (
        ("api_daybook_transactions_update_preview", "id"),
        ("api_daybook_transactions_delete_preview", "id"),
        ("api_daybook_transactions_create_execute", "confirmation_ticket"),
        ("api_daybook_transactions_update_execute", "confirmation_ticket"),
        ("api_daybook_transactions_delete_execute", "confirmation_ticket"),
    ):
        schema = by_name[name].parameters
        properties = cast(dict[str, dict[str, object]], schema["properties"])
        assert properties[field]["minLength"] == 1


@pytest.mark.parametrize(
    ("input_model", "payload"),
    [
        (DaybookTransactionCreatePreviewInput, {"daybookTransaction": {}, "extra": True}),
        (
            DaybookTransactionUpdatePreviewInput,
            {"id": "transaction-1", "daybookTransaction": {}, "extra": True},
        ),
        (DaybookTransactionDeletePreviewInput, {"id": "transaction-1", "extra": True}),
        (DaybookTransactionUpdatePreviewInput, {"id": "", "daybookTransaction": {}}),
        (DaybookTransactionDeletePreviewInput, {"id": ""}),
        (WriteExecuteInput, {"confirmation_ticket": "ticket", "daybookTransaction": {}}),
    ],
)
def test_outer_inputs_forbid_extra_fields_and_empty_ids(
    input_model: type[DaybookTransactionCreatePreviewInput]
    | type[DaybookTransactionUpdatePreviewInput]
    | type[DaybookTransactionDeletePreviewInput]
    | type[WriteExecuteInput],
    payload: dict[str, object],
) -> None:
    with pytest.raises(ValidationError):
        input_model.model_validate(payload)


@pytest.mark.parametrize(
    ("tool_name", "arguments", "expected_request"),
    [
        (
            "api_daybook_transactions_create_preview",
            {"daybookTransaction": {"unresolvedField": {"rank": 2}}},
            {"daybookTransaction": {"unresolvedField": {"rank": 2}}},
        ),
        (
            "api_daybook_transactions_update_preview",
            {
                "id": "transaction-1",
                "daybookTransaction": {"customField": {"rank": 2}},
            },
            {"daybookTransaction": {"customField": {"rank": 2}}},
        ),
        (
            "api_daybook_transactions_delete_preview",
            {"id": "transaction-1"},
            {"id": "transaction-1"},
        ),
    ],
)
def test_previews_are_mutation_free_and_bind_the_exact_canonical_request(
    tool_name: str,
    arguments: dict[str, object],
    expected_request: dict[str, object],
) -> None:
    server, requests = make_server(
        lambda request: pytest.fail(f"preview made an HTTP request: {request.method} {request.url}")
    )

    preview = call_tool(server, tool_name, arguments)

    assert requests == []
    assert preview["canonical_request"] == expected_request
    assert preview["expected_effect_state"] == {
        "action": tool_name.removeprefix("api_daybook_transactions_").removesuffix("_preview"),
        "resource": "daybookTransaction",
        **({"id": arguments["id"]} if "id" in arguments else {}),
    }
    assert isinstance(preview["confirmation_ticket"], str)


@pytest.mark.parametrize(
    ("preview_name", "execute_name", "arguments", "response", "method", "path", "body"),
    [
        (
            "api_daybook_transactions_create_preview",
            "api_daybook_transactions_create_execute",
            {"daybookTransaction": {"entryDate": "2026-07-29", "description": "Sales"}},
            {"daybookTransactions": [{"id": "transaction-1"}]},
            "POST",
            "/v2/daybookTransactions",
            {"daybookTransaction": {"entryDate": "2026-07-29", "description": "Sales"}},
        ),
        (
            "api_daybook_transactions_update_preview",
            "api_daybook_transactions_update_execute",
            {"id": "transaction /?", "daybookTransaction": {"description": "Corrected"}},
            {"daybookTransactions": [{"id": "transaction /?"}]},
            "PUT",
            "/v2/daybookTransactions/transaction%20%2F%3F",
            {"daybookTransaction": {"description": "Corrected"}},
        ),
        (
            "api_daybook_transactions_delete_preview",
            "api_daybook_transactions_delete_execute",
            {"id": "transaction /?"},
            {"meta": {"deletedRecords": {"daybookTransactions": ["transaction /?"]}}},
            "DELETE",
            "/v2/daybookTransactions/transaction%20%2F%3F",
            None,
        ),
    ],
)
def test_execute_sends_exact_singular_daybook_transaction_cud_shapes_once(
    preview_name: str,
    execute_name: str,
    arguments: dict[str, object],
    response: dict[str, object],
    method: str,
    path: str,
    body: dict[str, object] | None,
) -> None:
    server, requests = make_server(lambda request: httpx.Response(200, json=response))

    preview = call_tool(server, preview_name, arguments)
    execution = call_tool(
        server,
        execute_name,
        {"confirmation_ticket": preview["confirmation_ticket"]},
    )

    assert len(requests) == 1
    request = requests[0]
    assert request.method == method
    assert request.url.raw_path.decode() == path
    if body is None:
        assert request.content == b""
        assert execution == {
            "changed_records": {},
            "deleted_records": {"daybookTransactions": ["transaction /?"]},
        }
    else:
        assert json.loads(request.content) == body
        assert execution["changed_records"] == response
        assert execution["deleted_records"] is None


def test_tampered_expired_and_replayed_tickets_fail_without_extra_writes() -> None:
    clock = Clock()
    server, requests = make_server(
        lambda request: httpx.Response(
            200,
            json={"daybookTransactions": [{"id": "transaction-1"}]},
        ),
        confirmations=ConfirmationStore(clock),
    )

    preview = call_tool(
        server,
        "api_daybook_transactions_create_preview",
        {"daybookTransaction": {"entryDate": "2026-07-29"}},
    )
    ticket = preview["confirmation_ticket"]
    assert isinstance(ticket, str)
    tampered = call_tool(
        server,
        "api_daybook_transactions_create_execute",
        {"confirmation_ticket": f"{ticket}x"},
    )
    assert tampered["code"] == StableErrorCode.CONFIRMATION_INVALID
    assert requests == []

    clock.now += timedelta(minutes=6)
    expired = call_tool(
        server,
        "api_daybook_transactions_create_execute",
        {"confirmation_ticket": ticket},
    )
    assert expired["code"] == StableErrorCode.CONFIRMATION_EXPIRED
    assert requests == []

    replay_preview = call_tool(
        server,
        "api_daybook_transactions_create_preview",
        {"daybookTransaction": {"entryDate": "2026-07-29"}},
    )
    replay_ticket = replay_preview["confirmation_ticket"]
    assert isinstance(replay_ticket, str)
    first = call_tool(
        server,
        "api_daybook_transactions_create_execute",
        {"confirmation_ticket": replay_ticket},
    )
    replayed = call_tool(
        server,
        "api_daybook_transactions_create_execute",
        {"confirmation_ticket": replay_ticket},
    )

    assert first["changed_records"] == {"daybookTransactions": [{"id": "transaction-1"}]}
    assert replayed["code"] == StableErrorCode.CONFIRMATION_CONSUMED
    assert len(requests) == 1


def test_daybook_transaction_ticket_rejects_a_different_executor_in_the_same_module() -> None:
    server, requests = make_server(
        lambda request: httpx.Response(
            200,
            json={"daybookTransactions": [{"id": "transaction-1"}]},
        ),
    )

    preview = call_tool(
        server,
        "api_daybook_transactions_create_preview",
        {"daybookTransaction": {"entryDate": "2026-07-29"}},
    )
    wrong_executor = call_tool(
        server,
        "api_daybook_transactions_delete_execute",
        {"confirmation_ticket": preview["confirmation_ticket"]},
    )

    assert wrong_executor["code"] == StableErrorCode.CONFIRMATION_MISMATCH
    assert requests == []

    correct_executor = call_tool(
        server,
        "api_daybook_transactions_create_execute",
        {"confirmation_ticket": preview["confirmation_ticket"]},
    )
    assert correct_executor["changed_records"] == {"daybookTransactions": [{"id": "transaction-1"}]}
    assert len(requests) == 1


@pytest.mark.parametrize(
    "changes",
    [
        {"execute_tool_name": "api_daybook_transactions_other_execute"},
        {"organization_id": "other-organisation"},
        {"resource_id": "other-transaction"},
        {"payload": {"description": "Changed"}},
        {"expected_effect_state": {"action": "other"}},
    ],
)
def test_daybook_transaction_ticket_binding_rejects_every_mutated_operation_field(
    changes: dict[str, object],
) -> None:
    specification = WriteOperationSpec(
        execute_tool_name="api_daybook_transactions_update_execute",
        method=WriteMethod.PUT,
        collection_path="/daybookTransactions",
        singular_root="daybookTransaction",
        plural_root="daybookTransactions",
        payload={"description": "Sales"},
        resource_id="transaction-1",
        organization_id=None,
        summary="Update one Billy daybook transaction.",
        expected_effect_state={
            "action": "update",
            "resource": "daybookTransaction",
            "id": "transaction-1",
        },
    )
    store = ConfirmationStore()
    ticket = store.issue(confirmation_binding_for(specification))
    mismatched = specification.model_copy(update=changes)

    with pytest.raises(ConfirmationFailure) as failure:
        store.consume(ticket.value, confirmation_binding_for(mismatched))

    assert failure.value.error.code is StableErrorCode.CONFIRMATION_MISMATCH


def test_empty_token_returns_typed_auth_error_without_network_activity() -> None:
    server, requests = make_server(
        lambda request: pytest.fail(f"missing token attempted HTTP request: {request.url}"),
        token="",
    )

    preview = call_tool(
        server,
        "api_daybook_transactions_create_preview",
        {"daybookTransaction": {"entryDate": "2026-07-29"}},
    )
    error = call_tool(
        server,
        "api_daybook_transactions_create_execute",
        {"confirmation_ticket": preview["confirmation_ticket"]},
    )

    assert error["code"] == StableErrorCode.AUTH_REQUIRED
    assert requests == []


@pytest.mark.parametrize(
    ("status", "response", "preview_name", "arguments", "execute_name", "expected_code"),
    [
        (
            401,
            {"errorCode": "AUTHENTICATION_REQUIRED"},
            "api_daybook_transactions_create_preview",
            {"daybookTransaction": {"entryDate": "2026-07-29"}},
            "api_daybook_transactions_create_execute",
            StableErrorCode.AUTH_REQUIRED,
        ),
        (
            404,
            {"errorCode": "RECORD_NOT_FOUND"},
            "api_daybook_transactions_update_preview",
            {"id": "missing-transaction", "daybookTransaction": {"description": "Sales"}},
            "api_daybook_transactions_update_execute",
            StableErrorCode.NOT_FOUND,
        ),
    ],
)
def test_typed_authentication_and_not_found_errors_propagate(
    status: int,
    response: dict[str, str],
    preview_name: str,
    arguments: dict[str, object],
    execute_name: str,
    expected_code: StableErrorCode,
) -> None:
    server, requests = make_server(lambda request: httpx.Response(status, json=response))

    preview = call_tool(server, preview_name, arguments)
    error = call_tool(
        server,
        execute_name,
        {"confirmation_ticket": preview["confirmation_ticket"]},
    )

    assert error["code"] == expected_code
    assert len(requests) == 1


def test_absent_optional_deleted_records_are_not_fabricated() -> None:
    server, _ = make_server(lambda request: httpx.Response(200, json={"meta": {}}))

    preview = call_tool(server, "api_daybook_transactions_delete_preview", {"id": "transaction-1"})
    execution = call_tool(
        server,
        "api_daybook_transactions_delete_execute",
        {"confirmation_ticket": preview["confirmation_ticket"]},
    )

    assert execution == {"changed_records": {}, "deleted_records": None}
