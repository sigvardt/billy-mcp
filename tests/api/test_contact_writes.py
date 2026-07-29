"""Contract tests for the ticketed singular Billy contact write tools."""

from __future__ import annotations

import asyncio
import json
from collections.abc import Callable
from datetime import UTC, datetime
from typing import cast

import httpx
import pytest
from fastmcp import FastMCP
from pydantic import ValidationError

from billy_mcp.api.contact_writes import (
    ContactCreatePreviewInput,
    ContactDeletePreviewInput,
    ContactUpdatePreviewInput,
    register_contact_write_tools,
)
from billy_mcp.api.write_protocol import WriteExecuteInput, WriteProtocolService
from billy_mcp.client import BillyHttpClient
from billy_mcp.confirmations import MAX_TICKET_TTL, ConfirmationStore
from billy_mcp.models import StableErrorCode

MockHandler = Callable[[httpx.Request], httpx.Response]


class Clock:
    """Mutable UTC clock for deterministic confirmation-ticket expiry tests."""

    def __init__(self) -> None:
        self.now = datetime(2026, 7, 29, tzinfo=UTC)

    def __call__(self) -> datetime:
        return self.now


def make_server(
    handler: MockHandler,
    *,
    confirmations: ConfirmationStore | None = None,
) -> tuple[FastMCP, list[httpx.Request]]:
    """Create a fully local FastMCP server with a recording locked client."""

    requests: list[httpx.Request] = []

    def recording_handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        return handler(request)

    client = BillyHttpClient(
        lambda: "contact-write-test-token",
        transport=httpx.MockTransport(recording_handler),
    )
    server = FastMCP("contact-write-contract-test")
    register_contact_write_tools(
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


def test_registers_exactly_six_typed_direct_contact_write_tools() -> None:
    server, _ = make_server(lambda request: httpx.Response(200, json={"contacts": []}))

    tools = asyncio.run(server.list_tools())
    by_name = {tool.name: tool for tool in tools}

    assert set(by_name) == {
        "api_contacts_create_preview",
        "api_contacts_create_execute",
        "api_contacts_update_preview",
        "api_contacts_update_execute",
        "api_contacts_delete_preview",
        "api_contacts_delete_execute",
    }
    expected_properties = {
        "api_contacts_create_preview": {"contact"},
        "api_contacts_create_execute": {"confirmation_ticket"},
        "api_contacts_update_preview": {"id", "contact"},
        "api_contacts_update_execute": {"confirmation_ticket"},
        "api_contacts_delete_preview": {"id"},
        "api_contacts_delete_execute": {"confirmation_ticket"},
    }
    for name, fields in expected_properties.items():
        schema = by_name[name].parameters
        properties = cast(dict[str, object], schema["properties"])
        assert schema["additionalProperties"] is False
        assert set(properties) == fields
        assert "input" not in properties

    for name in (
        "api_contacts_create_execute",
        "api_contacts_update_execute",
        "api_contacts_delete_execute",
    ):
        schema = by_name[name].parameters
        properties = cast(dict[str, object], schema["properties"])
        ticket = properties["confirmation_ticket"]
        assert isinstance(ticket, dict)
        assert ticket["minLength"] == 1


@pytest.mark.parametrize(
    ("input_model", "payload"),
    [
        (ContactCreatePreviewInput, {"contact": {}, "unexpected": True}),
        (ContactUpdatePreviewInput, {"id": "contact-1", "contact": {}, "unexpected": True}),
        (ContactDeletePreviewInput, {"id": "contact-1", "unexpected": True}),
        (ContactUpdatePreviewInput, {"id": "", "contact": {}}),
        (ContactDeletePreviewInput, {"id": ""}),
        (WriteExecuteInput, {"confirmation_ticket": "ticket", "contact": {}}),
    ],
)
def test_outer_inputs_forbid_extra_fields_and_empty_ids(
    input_model: type[ContactCreatePreviewInput]
    | type[ContactUpdatePreviewInput]
    | type[ContactDeletePreviewInput]
    | type[WriteExecuteInput],
    payload: dict[str, object],
) -> None:
    with pytest.raises(ValidationError):
        input_model.model_validate(payload)


@pytest.mark.parametrize(
    ("tool_name", "input", "expected_request"),
    [
        (
            "api_contacts_create_preview",
            {"contact": {"name": "Example", "customField": {"order": 2}}},
            {"contact": {"name": "Example", "customField": {"order": 2}}},
        ),
        (
            "api_contacts_update_preview",
            {"id": "contact-1", "contact": {"name": "Replacement"}},
            {"contact": {"name": "Replacement"}},
        ),
        (
            "api_contacts_delete_preview",
            {"id": "contact-1"},
            {"id": "contact-1"},
        ),
    ],
)
def test_previews_issue_tickets_without_any_http_write(
    tool_name: str,
    input: dict[str, object],
    expected_request: dict[str, object],
) -> None:
    server, requests = make_server(
        lambda request: pytest.fail(f"preview made an HTTP request: {request.method} {request.url}")
    )

    preview = call_tool(server, tool_name, input)

    assert requests == []
    assert preview["canonical_request"] == expected_request
    assert isinstance(preview["confirmation_ticket"], str)
    assert preview["confirmation_ticket"]


@pytest.mark.parametrize(
    (
        "preview_tool",
        "execute_tool",
        "preview_input",
        "response",
        "expected_method",
        "expected_path",
        "expected_body",
    ),
    [
        (
            "api_contacts_create_preview",
            "api_contacts_create_execute",
            {"contact": {"name": "Example"}},
            {"contacts": [{"id": "contact-1"}]},
            "POST",
            "/v2/contacts",
            {"contact": {"name": "Example"}},
        ),
        (
            "api_contacts_update_preview",
            "api_contacts_update_execute",
            {"id": "contact /?", "contact": {"name": "Replacement"}},
            {"contacts": [{"id": "contact /?"}]},
            "PUT",
            "/v2/contacts/contact%20%2F%3F",
            {"contact": {"name": "Replacement"}},
        ),
        (
            "api_contacts_delete_preview",
            "api_contacts_delete_execute",
            {"id": "contact /?"},
            {"meta": {"deletedRecords": {"contacts": ["contact /?"]}}},
            "DELETE",
            "/v2/contacts/contact%20%2F%3F",
            None,
        ),
    ],
)
def test_executes_the_exact_singular_contact_cud_request_once(
    preview_tool: str,
    execute_tool: str,
    preview_input: dict[str, object],
    response: dict[str, object],
    expected_method: str,
    expected_path: str,
    expected_body: dict[str, object] | None,
) -> None:
    server, requests = make_server(lambda request: httpx.Response(200, json=response))

    preview = call_tool(server, preview_tool, preview_input)
    execution = call_tool(
        server,
        execute_tool,
        {"confirmation_ticket": preview["confirmation_ticket"]},
    )

    assert len(requests) == 1
    request = requests[0]
    assert request.method == expected_method
    assert request.url.raw_path.decode() == expected_path
    if expected_body is None:
        assert request.content == b""
        assert execution["changed_records"] == {}
        assert execution["deleted_records"] == {"contacts": ["contact /?"]}
    else:
        assert json.loads(request.content) == expected_body
        assert execution["changed_records"] == response
        assert execution["deleted_records"] is None


def test_invalid_and_replayed_tickets_fail_without_another_write() -> None:
    server, requests = make_server(
        lambda request: httpx.Response(200, json={"contacts": [{"id": "contact-1"}]})
    )

    invalid = call_tool(
        server,
        "api_contacts_create_execute",
        {"confirmation_ticket": "not-a-contact-ticket"},
    )
    assert invalid["code"] == StableErrorCode.CONFIRMATION_INVALID
    assert requests == []

    preview = call_tool(
        server,
        "api_contacts_create_preview",
        {"contact": {"name": "Example"}},
    )
    confirmation_ticket = preview["confirmation_ticket"]
    assert isinstance(confirmation_ticket, str)
    first = call_tool(
        server,
        "api_contacts_create_execute",
        {"confirmation_ticket": confirmation_ticket},
    )
    assert first["changed_records"] == {"contacts": [{"id": "contact-1"}]}
    replayed = call_tool(
        server,
        "api_contacts_create_execute",
        {"confirmation_ticket": confirmation_ticket},
    )
    assert replayed["code"] == StableErrorCode.CONFIRMATION_CONSUMED
    assert len(requests) == 1


def test_expired_ticket_fails_without_an_http_write() -> None:
    clock = Clock()
    server, requests = make_server(
        lambda request: httpx.Response(200, json={"contacts": [{"id": "contact-1"}]}),
        confirmations=ConfirmationStore(clock),
    )

    preview = call_tool(
        server,
        "api_contacts_create_preview",
        {"contact": {"name": "Example"}},
    )
    clock.now += MAX_TICKET_TTL
    expired = call_tool(
        server,
        "api_contacts_create_execute",
        {"confirmation_ticket": preview["confirmation_ticket"]},
    )

    assert expired["code"] == StableErrorCode.CONFIRMATION_EXPIRED
    assert requests == []


@pytest.mark.parametrize(
    ("status", "response", "preview_tool", "preview_input", "execute_tool", "expected_code"),
    [
        (
            401,
            {"errorCode": "AUTHENTICATION_REQUIRED"},
            "api_contacts_create_preview",
            {"contact": {"name": "Example"}},
            "api_contacts_create_execute",
            StableErrorCode.AUTH_REQUIRED,
        ),
        (
            404,
            {"errorCode": "RECORD_NOT_FOUND"},
            "api_contacts_update_preview",
            {"id": "missing-contact", "contact": {"name": "Example"}},
            "api_contacts_update_execute",
            StableErrorCode.NOT_FOUND,
        ),
    ],
)
def test_typed_authentication_and_not_found_errors_propagate(
    status: int,
    response: dict[str, str],
    preview_tool: str,
    preview_input: dict[str, object],
    execute_tool: str,
    expected_code: StableErrorCode,
) -> None:
    server, requests = make_server(lambda request: httpx.Response(status, json=response))

    preview = call_tool(server, preview_tool, preview_input)
    error = call_tool(
        server,
        execute_tool,
        {"confirmation_ticket": preview["confirmation_ticket"]},
    )

    assert error["code"] == expected_code
    assert len(requests) == 1


def test_absent_optional_deleted_records_are_not_fabricated() -> None:
    server, _ = make_server(
        lambda request: httpx.Response(200, json={"contacts": [{"id": "contact-1"}]})
    )

    preview = call_tool(
        server,
        "api_contacts_create_preview",
        {"contact": {"name": "Example"}},
    )
    execution = call_tool(
        server,
        "api_contacts_create_execute",
        {"confirmation_ticket": preview["confirmation_ticket"]},
    )

    assert execution["changed_records"] == {"contacts": [{"id": "contact-1"}]}
    assert execution["deleted_records"] is None
