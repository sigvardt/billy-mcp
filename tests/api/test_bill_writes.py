"""Contract tests for ticketed singular Billy parent-bill write tools."""

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

from billy_mcp.api.bill_writes import (
    BillCreatePreviewInput,
    BillDeletePreviewInput,
    BillUpdatePreviewInput,
    register_bill_write_tools,
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
    token: str | None = "bill-write-test-token",
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
    server = FastMCP("bill-write-contract-test")
    register_bill_write_tools(
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


def test_registers_exactly_six_flat_typed_bill_write_tools() -> None:
    server, _ = make_server(lambda request: httpx.Response(200, json={}))

    by_name = {tool.name: tool for tool in asyncio.run(server.list_tools())}

    assert set(by_name) == {
        "api_bills_create_preview",
        "api_bills_create_execute",
        "api_bills_update_preview",
        "api_bills_update_execute",
        "api_bills_delete_preview",
        "api_bills_delete_execute",
    }
    expected_properties = {
        "api_bills_create_preview": {"bill"},
        "api_bills_create_execute": {"confirmation_ticket"},
        "api_bills_update_preview": {"id", "bill"},
        "api_bills_update_execute": {"confirmation_ticket"},
        "api_bills_delete_preview": {"id"},
        "api_bills_delete_execute": {"confirmation_ticket"},
    }
    for name, fields in expected_properties.items():
        schema = by_name[name].parameters
        properties = cast(dict[str, object], schema["properties"])
        assert schema["additionalProperties"] is False
        assert set(properties) == fields
        assert "input" not in properties

    for name, field in (
        ("api_bills_update_preview", "id"),
        ("api_bills_delete_preview", "id"),
        ("api_bills_create_execute", "confirmation_ticket"),
        ("api_bills_update_execute", "confirmation_ticket"),
        ("api_bills_delete_execute", "confirmation_ticket"),
    ):
        schema = by_name[name].parameters
        properties = cast(dict[str, dict[str, object]], schema["properties"])
        assert properties[field]["minLength"] == 1


@pytest.mark.parametrize(
    ("input_model", "payload"),
    [
        (BillCreatePreviewInput, {"bill": {}, "extra": True}),
        (BillUpdatePreviewInput, {"id": "bill-1", "bill": {}, "extra": True}),
        (BillDeletePreviewInput, {"id": "bill-1", "extra": True}),
        (BillUpdatePreviewInput, {"id": "", "bill": {}}),
        (BillDeletePreviewInput, {"id": ""}),
        (BillUpdatePreviewInput, {"id": "bill-1", "bill": {"id": "other"}}),
        (WriteExecuteInput, {"confirmation_ticket": "ticket", "bill": {}}),
    ],
)
def test_outer_inputs_forbid_extra_fields_empty_ids_and_mismatched_body_ids(
    input_model: type[BillCreatePreviewInput]
    | type[BillUpdatePreviewInput]
    | type[BillDeletePreviewInput]
    | type[WriteExecuteInput],
    payload: dict[str, object],
) -> None:
    with pytest.raises(ValidationError):
        input_model.model_validate(payload)


def test_update_allows_an_opaque_bill_body_id_when_it_matches_the_route() -> None:
    input = BillUpdatePreviewInput.model_validate(
        {"id": "bill-1", "bill": {"id": "bill-1", "unknown": {"rank": 2}}}
    )

    assert input.bill["unknown"] == {"rank": 2}


@pytest.mark.parametrize(
    ("tool_name", "arguments", "expected_request"),
    [
        (
            "api_bills_create_preview",
            {"bill": {"unresolvedField": {"rank": 2}}},
            {"bill": {"unresolvedField": {"rank": 2}}},
        ),
        (
            "api_bills_update_preview",
            {"id": "bill-1", "bill": {"customField": {"rank": 2}}},
            {"bill": {"customField": {"rank": 2}}},
        ),
        (
            "api_bills_delete_preview",
            {"id": "bill-1"},
            {"id": "bill-1"},
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
        "action": tool_name.removeprefix("api_bills_").removesuffix("_preview"),
        "resource": "bill",
        **({"id": arguments["id"]} if "id" in arguments else {}),
    }
    assert isinstance(preview["confirmation_ticket"], str)


@pytest.mark.parametrize(
    ("preview_name", "execute_name", "arguments", "response", "method", "path", "body"),
    [
        (
            "api_bills_create_preview",
            "api_bills_create_execute",
            {"bill": {"unrecognisedBillField": {"rank": 2}}},
            {"bills": [{"id": "bill-1"}]},
            "POST",
            "/v2/bills",
            {"bill": {"unrecognisedBillField": {"rank": 2}}},
        ),
        (
            "api_bills_update_preview",
            "api_bills_update_execute",
            {"id": "bill /?", "bill": {"description": "Corrected"}},
            {"bills": [{"id": "bill /?"}]},
            "PUT",
            "/v2/bills/bill%20%2F%3F",
            {"bill": {"description": "Corrected"}},
        ),
        (
            "api_bills_delete_preview",
            "api_bills_delete_execute",
            {"id": "bill /?"},
            {"meta": {"deletedRecords": {"bills": ["bill /?"]}}},
            "DELETE",
            "/v2/bills/bill%20%2F%3F",
            None,
        ),
    ],
)
def test_execute_sends_exact_singular_bill_cud_shapes_once(
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
            "deleted_records": {"bills": ["bill /?"]},
        }
    else:
        assert json.loads(request.content) == body
        assert execution["changed_records"] == response
        assert execution["deleted_records"] is None


def test_tampered_expired_and_replayed_tickets_fail_without_extra_writes() -> None:
    clock = Clock()
    server, requests = make_server(
        lambda request: httpx.Response(200, json={"bills": [{"id": "bill-1"}]}),
        confirmations=ConfirmationStore(clock),
    )

    preview = call_tool(
        server,
        "api_bills_create_preview",
        {"bill": {"unrecognisedBillField": {"rank": 2}}},
    )
    ticket = preview["confirmation_ticket"]
    assert isinstance(ticket, str)
    tampered = call_tool(
        server,
        "api_bills_create_execute",
        {"confirmation_ticket": f"{ticket}x"},
    )
    assert tampered["code"] == StableErrorCode.CONFIRMATION_INVALID
    assert requests == []

    clock.now += timedelta(minutes=6)
    expired = call_tool(
        server,
        "api_bills_create_execute",
        {"confirmation_ticket": ticket},
    )
    assert expired["code"] == StableErrorCode.CONFIRMATION_EXPIRED
    assert requests == []

    replay_preview = call_tool(
        server,
        "api_bills_create_preview",
        {"bill": {"unrecognisedBillField": {"rank": 2}}},
    )
    replay_ticket = replay_preview["confirmation_ticket"]
    assert isinstance(replay_ticket, str)
    first = call_tool(
        server,
        "api_bills_create_execute",
        {"confirmation_ticket": replay_ticket},
    )
    replayed = call_tool(
        server,
        "api_bills_create_execute",
        {"confirmation_ticket": replay_ticket},
    )

    assert first["changed_records"] == {"bills": [{"id": "bill-1"}]}
    assert replayed["code"] == StableErrorCode.CONFIRMATION_CONSUMED
    assert len(requests) == 1


def test_bill_ticket_rejects_a_different_executor_in_the_same_module_before_http() -> None:
    server, requests = make_server(
        lambda request: httpx.Response(200, json={"bills": [{"id": "bill-1"}]}),
    )

    preview = call_tool(
        server,
        "api_bills_create_preview",
        {"bill": {"unrecognisedBillField": {"rank": 2}}},
    )
    wrong_executor = call_tool(
        server,
        "api_bills_delete_execute",
        {"confirmation_ticket": preview["confirmation_ticket"]},
    )

    assert wrong_executor["code"] == StableErrorCode.CONFIRMATION_MISMATCH
    assert requests == []

    correct_executor = call_tool(
        server,
        "api_bills_create_execute",
        {"confirmation_ticket": preview["confirmation_ticket"]},
    )
    assert correct_executor["changed_records"] == {"bills": [{"id": "bill-1"}]}
    assert len(requests) == 1


@pytest.mark.parametrize(
    "changes",
    [
        {"execute_tool_name": "api_bills_other_execute"},
        {"organization_id": "other-organisation"},
        {"resource_id": "other-bill"},
        {"payload": {"description": "Changed"}},
        {"expected_effect_state": {"action": "other"}},
    ],
)
def test_bill_ticket_binding_rejects_every_mutated_operation_field(
    changes: dict[str, object],
) -> None:
    specification = WriteOperationSpec(
        execute_tool_name="api_bills_update_execute",
        method=WriteMethod.PUT,
        collection_path="/bills",
        singular_root="bill",
        plural_root="bills",
        payload={"description": "Sales"},
        resource_id="bill-1",
        organization_id=None,
        summary="Update one Billy bill.",
        expected_effect_state={"action": "update", "resource": "bill", "id": "bill-1"},
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
        "api_bills_create_preview",
        {"bill": {"unrecognisedBillField": {"rank": 2}}},
    )
    error = call_tool(
        server,
        "api_bills_create_execute",
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
            "api_bills_create_preview",
            {"bill": {"unrecognisedBillField": {"rank": 2}}},
            "api_bills_create_execute",
            StableErrorCode.AUTH_REQUIRED,
        ),
        (
            404,
            {"errorCode": "RECORD_NOT_FOUND"},
            "api_bills_update_preview",
            {"id": "missing-bill", "bill": {"description": "Sales"}},
            "api_bills_update_execute",
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


def test_write_failure_is_not_retried() -> None:
    server, requests = make_server(
        lambda request: httpx.Response(500, json={"errorCode": "INTERNAL_SERVER_ERROR"})
    )

    preview = call_tool(
        server,
        "api_bills_create_preview",
        {"bill": {"unrecognisedBillField": {"rank": 2}}},
    )
    error = call_tool(
        server,
        "api_bills_create_execute",
        {"confirmation_ticket": preview["confirmation_ticket"]},
    )

    assert error["code"] == StableErrorCode.BILLY_ERROR
    assert len(requests) == 1


def test_absent_optional_deleted_records_are_not_fabricated() -> None:
    server, _ = make_server(lambda request: httpx.Response(200, json={"meta": {}}))

    preview = call_tool(server, "api_bills_delete_preview", {"id": "bill-1"})
    execution = call_tool(
        server,
        "api_bills_delete_execute",
        {"confirmation_ticket": preview["confirmation_ticket"]},
    )

    assert execution == {"changed_records": {}, "deleted_records": None}
