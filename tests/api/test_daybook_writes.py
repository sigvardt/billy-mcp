"""Contract tests for the ticketed singular Billy daybook write tools."""

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

from billy_mcp.api.daybook_writes import (
    DaybookCreatePreviewInput,
    DaybookDeletePreviewInput,
    DaybookUpdatePreviewInput,
    register_daybook_write_tools,
)
from billy_mcp.api.write_protocol import WriteExecuteInput, WriteProtocolService
from billy_mcp.client import BillyHttpClient
from billy_mcp.confirmations import ConfirmationStore
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
    token: str | None = "daybook-write-test-token",
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
    server = FastMCP("daybook-write-contract-test")
    register_daybook_write_tools(
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


def test_registers_exactly_six_flat_typed_daybook_write_tools() -> None:
    server, _ = make_server(lambda request: httpx.Response(200, json={}))

    by_name = {tool.name: tool for tool in asyncio.run(server.list_tools())}

    assert set(by_name) == {
        "api_daybooks_create_preview",
        "api_daybooks_create_execute",
        "api_daybooks_update_preview",
        "api_daybooks_update_execute",
        "api_daybooks_delete_preview",
        "api_daybooks_delete_execute",
    }
    expected_properties = {
        "api_daybooks_create_preview": {"daybook"},
        "api_daybooks_create_execute": {"confirmation_ticket"},
        "api_daybooks_update_preview": {"daybook", "id"},
        "api_daybooks_update_execute": {"confirmation_ticket"},
        "api_daybooks_delete_preview": {"id"},
        "api_daybooks_delete_execute": {"confirmation_ticket"},
    }
    for name, fields in expected_properties.items():
        schema = by_name[name].parameters
        properties = cast(dict[str, object], schema["properties"])
        assert schema["additionalProperties"] is False
        assert set(properties) == fields
        assert "input" not in properties

    for name, field in (
        ("api_daybooks_update_preview", "id"),
        ("api_daybooks_delete_preview", "id"),
        ("api_daybooks_create_execute", "confirmation_ticket"),
        ("api_daybooks_update_execute", "confirmation_ticket"),
        ("api_daybooks_delete_execute", "confirmation_ticket"),
    ):
        schema = by_name[name].parameters
        properties = cast(dict[str, dict[str, object]], schema["properties"])
        assert properties[field]["minLength"] == 1


@pytest.mark.parametrize(
    ("input_model", "payload"),
    [
        (DaybookCreatePreviewInput, {"daybook": {}, "unexpected": True}),
        (DaybookUpdatePreviewInput, {"id": "daybook-1", "daybook": {}, "unexpected": True}),
        (DaybookDeletePreviewInput, {"id": "daybook-1", "unexpected": True}),
        (DaybookUpdatePreviewInput, {"id": "", "daybook": {}}),
        (DaybookDeletePreviewInput, {"id": ""}),
        (WriteExecuteInput, {"confirmation_ticket": "ticket", "daybook": {}}),
    ],
)
def test_outer_inputs_forbid_extra_fields_and_empty_ids(
    input_model: type[DaybookCreatePreviewInput]
    | type[DaybookUpdatePreviewInput]
    | type[DaybookDeletePreviewInput]
    | type[WriteExecuteInput],
    payload: dict[str, object],
) -> None:
    with pytest.raises(ValidationError):
        input_model.model_validate(payload)


@pytest.mark.parametrize(
    ("tool_name", "arguments", "expected_request"),
    [
        (
            "api_daybooks_create_preview",
            {"daybook": {"unresolvedField": {"rank": 2}}},
            {"daybook": {"unresolvedField": {"rank": 2}}},
        ),
        (
            "api_daybooks_update_preview",
            {"id": "daybook-1", "daybook": {"customField": {"rank": 2}}},
            {"daybook": {"customField": {"rank": 2}}},
        ),
        (
            "api_daybooks_delete_preview",
            {"id": "daybook-1"},
            {"id": "daybook-1"},
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
        "action": tool_name.removeprefix("api_daybooks_").removesuffix("_preview"),
        "resource": "daybook",
        **({"id": arguments["id"]} if "id" in arguments else {}),
    }
    assert isinstance(preview["confirmation_ticket"], str)


@pytest.mark.parametrize(
    ("preview_name", "execute_name", "arguments", "response", "method", "path", "body"),
    [
        (
            "api_daybooks_create_preview",
            "api_daybooks_create_execute",
            {"daybook": {"name": "Sales", "isTransactionSummaryEnabled": True}},
            {"daybooks": [{"id": "daybook-1"}]},
            "POST",
            "/v2/daybooks",
            {"daybook": {"name": "Sales", "isTransactionSummaryEnabled": True}},
        ),
        (
            "api_daybooks_update_preview",
            "api_daybooks_update_execute",
            {"id": "daybook /?", "daybook": {"name": "General"}},
            {"daybooks": [{"id": "daybook /?"}]},
            "PUT",
            "/v2/daybooks/daybook%20%2F%3F",
            {"daybook": {"name": "General"}},
        ),
        (
            "api_daybooks_delete_preview",
            "api_daybooks_delete_execute",
            {"id": "daybook /?"},
            {"meta": {"deletedRecords": {"daybooks": ["daybook /?"]}}},
            "DELETE",
            "/v2/daybooks/daybook%20%2F%3F",
            None,
        ),
    ],
)
def test_execute_sends_exact_singular_daybook_cud_shapes_once(
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
            "deleted_records": {"daybooks": ["daybook /?"]},
        }
    else:
        assert json.loads(request.content) == body
        assert execution["changed_records"] == response
        assert execution["deleted_records"] is None


def test_invalid_expired_and_replayed_tickets_fail_without_extra_writes() -> None:
    clock = Clock()
    server, requests = make_server(
        lambda request: httpx.Response(200, json={"daybooks": [{"id": "daybook-1"}]}),
        confirmations=ConfirmationStore(clock),
    )

    invalid = call_tool(
        server,
        "api_daybooks_create_execute",
        {"confirmation_ticket": "not-a-daybook-ticket"},
    )
    assert invalid["code"] == StableErrorCode.CONFIRMATION_INVALID

    expired_preview = call_tool(
        server,
        "api_daybooks_create_preview",
        {"daybook": {"name": "Sales"}},
    )
    clock.now += timedelta(minutes=6)
    expired = call_tool(
        server,
        "api_daybooks_create_execute",
        {"confirmation_ticket": expired_preview["confirmation_ticket"]},
    )
    assert expired["code"] == StableErrorCode.CONFIRMATION_EXPIRED

    replay_preview = call_tool(
        server,
        "api_daybooks_create_preview",
        {"daybook": {"name": "Sales"}},
    )
    first = call_tool(
        server,
        "api_daybooks_create_execute",
        {"confirmation_ticket": replay_preview["confirmation_ticket"]},
    )
    replayed = call_tool(
        server,
        "api_daybooks_create_execute",
        {"confirmation_ticket": replay_preview["confirmation_ticket"]},
    )

    assert first["changed_records"] == {"daybooks": [{"id": "daybook-1"}]}
    assert replayed["code"] == StableErrorCode.CONFIRMATION_CONSUMED
    assert len(requests) == 1


def test_empty_token_returns_typed_auth_error_without_network_activity() -> None:
    server, requests = make_server(
        lambda request: pytest.fail(f"missing token attempted HTTP request: {request.url}"),
        token="",
    )

    preview = call_tool(
        server,
        "api_daybooks_create_preview",
        {"daybook": {"name": "Sales"}},
    )
    error = call_tool(
        server,
        "api_daybooks_create_execute",
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
            "api_daybooks_create_preview",
            {"daybook": {"name": "Sales"}},
            "api_daybooks_create_execute",
            StableErrorCode.AUTH_REQUIRED,
        ),
        (
            404,
            {"errorCode": "RECORD_NOT_FOUND"},
            "api_daybooks_update_preview",
            {"id": "missing-daybook", "daybook": {"name": "Sales"}},
            "api_daybooks_update_execute",
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

    preview = call_tool(server, "api_daybooks_delete_preview", {"id": "daybook-1"})
    execution = call_tool(
        server,
        "api_daybooks_delete_execute",
        {"confirmation_ticket": preview["confirmation_ticket"]},
    )

    assert execution == {"changed_records": {}, "deleted_records": None}
