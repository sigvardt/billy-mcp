"""Contract tests for the ticketed contact-person write tools."""

from __future__ import annotations

import asyncio
import json
from datetime import UTC, datetime, timedelta
from typing import cast

import httpx
import pytest
from fastmcp import FastMCP
from pydantic import ValidationError

from billy_mcp.api.contact_person_writes import (
    ContactPersonCreatePreviewInput,
    ContactPersonDeletePreviewInput,
    ContactPersonUpdatePreviewInput,
    register_contact_person_write_tools,
)
from billy_mcp.api.write_protocol import WriteExecuteInput, WriteProtocolService
from billy_mcp.client import BillyHttpClient
from billy_mcp.confirmations import ConfirmationStore


class Clock:
    """Controllable confirmation clock used only by local ticket-expiry tests."""

    def __init__(self) -> None:
        self.now = datetime(2026, 7, 29, tzinfo=UTC)

    def __call__(self) -> datetime:
        return self.now


def make_client(handler: httpx.MockTransport) -> BillyHttpClient:
    """Create a locked token-backed client with no real network transport."""

    return BillyHttpClient(lambda: "test-token", transport=handler)


def registered_tools(
    handler: httpx.MockTransport,
    *,
    confirmations: ConfirmationStore | None = None,
) -> tuple[FastMCP, list[httpx.Request]]:
    """Register the module against a local transport and retain observed requests."""

    requests: list[httpx.Request] = []

    def recording_handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        return cast(httpx.Response, handler.handler(request))

    client = make_client(httpx.MockTransport(recording_handler))
    server = FastMCP("contact-person-writes-test")
    register_contact_person_write_tools(
        server,
        client,
        WriteProtocolService(client, confirmations or ConfirmationStore()),
    )
    return server, requests


def invoke(server: FastMCP, name: str, arguments: dict[str, object]) -> dict[str, object]:
    """Call one registered tool and return its structured result payload."""

    result = asyncio.run(server.call_tool(name, arguments))
    assert isinstance(result.structured_content, dict)
    structured_content = cast(dict[str, object], result.structured_content)
    payload = structured_content.get("result", structured_content)
    assert isinstance(payload, dict)
    return cast(dict[str, object], payload)


def test_registers_exactly_six_tools_with_strict_preview_and_ticket_only_execute_inputs() -> None:
    server, _ = registered_tools(httpx.MockTransport(lambda request: httpx.Response(200, json={})))

    tools = {tool.name: tool for tool in asyncio.run(server.list_tools())}
    assert set(tools) == {
        "api_contact_persons_create_preview",
        "api_contact_persons_create_execute",
        "api_contact_persons_update_preview",
        "api_contact_persons_update_execute",
        "api_contact_persons_delete_preview",
        "api_contact_persons_delete_execute",
    }
    assert set(tools["api_contact_persons_create_preview"].parameters["properties"]) == {
        "contactPerson"
    }
    assert set(tools["api_contact_persons_update_preview"].parameters["properties"]) == {
        "id",
        "contactPerson",
    }
    assert (
        tools["api_contact_persons_update_preview"].parameters["properties"]["id"]["minLength"] == 1
    )
    assert set(tools["api_contact_persons_delete_preview"].parameters["properties"]) == {"id"}
    for name in (
        "api_contact_persons_create_execute",
        "api_contact_persons_update_execute",
        "api_contact_persons_delete_execute",
    ):
        assert set(tools[name].parameters["properties"]) == {"confirmation_ticket"}
        assert tools[name].parameters["additionalProperties"] is False

    with pytest.raises(ValidationError):
        ContactPersonCreatePreviewInput.model_validate(
            {"contactPerson": {"contactId": "contact-1"}, "unexpected": True}
        )
    with pytest.raises(ValidationError):
        ContactPersonUpdatePreviewInput.model_validate(
            {"id": "person-1", "contactPerson": {}, "unexpected": True}
        )
    with pytest.raises(ValidationError):
        ContactPersonDeletePreviewInput.model_validate({"id": "person-1", "unexpected": True})
    with pytest.raises(ValidationError):
        WriteExecuteInput.model_validate(
            {"confirmation_ticket": "ticket", "contactPerson": {"label": "Ada"}}
        )


@pytest.mark.parametrize(
    ("name", "arguments", "expected_request"),
    [
        (
            "api_contact_persons_create_preview",
            {"contactPerson": {"contactId": "contact-1", "label": "Ada"}},
            {"contactPerson": {"contactId": "contact-1", "label": "Ada"}},
        ),
        (
            "api_contact_persons_update_preview",
            {"id": "person /?", "contactPerson": {"label": "Ada"}},
            {"contactPerson": {"label": "Ada"}},
        ),
        (
            "api_contact_persons_delete_preview",
            {"id": "person /?"},
            {"id": "person /?"},
        ),
    ],
)
def test_previews_are_mutation_free_and_bind_the_exact_canonical_request(
    name: str, arguments: dict[str, object], expected_request: dict[str, object]
) -> None:
    server, requests = registered_tools(
        httpx.MockTransport(lambda request: httpx.Response(200, json={}))
    )

    preview = invoke(server, name, arguments)

    assert requests == []
    assert preview["canonical_request"] == expected_request
    expected_effect_state = preview["expected_effect_state"]
    assert isinstance(expected_effect_state, dict)
    assert expected_effect_state["resource"] == "contactPerson"
    assert isinstance(preview["confirmation_ticket"], str)


@pytest.mark.parametrize(
    ("preview_name", "execute_name", "arguments", "response", "method", "path", "body"),
    [
        (
            "api_contact_persons_create_preview",
            "api_contact_persons_create_execute",
            {"contactPerson": {"contactId": "contact-1", "label": "Ada"}},
            {"contactPersons": [{"id": "person-1"}]},
            "POST",
            "/v2/contactPersons",
            {"contactPerson": {"contactId": "contact-1", "label": "Ada"}},
        ),
        (
            "api_contact_persons_update_preview",
            "api_contact_persons_update_execute",
            {"id": "person /?", "contactPerson": {"label": "Ada"}},
            {"contactPersons": [{"id": "person /?"}]},
            "PUT",
            "/v2/contactPersons/person%20%2F%3F",
            {"contactPerson": {"label": "Ada"}},
        ),
        (
            "api_contact_persons_delete_preview",
            "api_contact_persons_delete_execute",
            {"id": "person /?"},
            {"meta": {"deletedRecords": {"contactPersons": ["person /?"]}}},
            "DELETE",
            "/v2/contactPersons/person%20%2F%3F",
            None,
        ),
    ],
)
def test_execute_sends_exact_singular_cud_shapes_once(
    preview_name: str,
    execute_name: str,
    arguments: dict[str, object],
    response: dict[str, object],
    method: str,
    path: str,
    body: dict[str, object] | None,
) -> None:
    server, requests = registered_tools(
        httpx.MockTransport(lambda request: httpx.Response(200, json=response))
    )
    preview = invoke(server, preview_name, arguments)

    result = invoke(
        server,
        execute_name,
        {"confirmation_ticket": preview["confirmation_ticket"]},
    )

    assert len(requests) == 1
    assert requests[0].method == method
    assert requests[0].url.raw_path.decode() == path
    if body is None:
        assert requests[0].content == b""
        assert result == {
            "changed_records": {},
            "deleted_records": {"contactPersons": ["person /?"]},
        }
    else:
        assert json.loads(requests[0].content) == body
        assert result["changed_records"] == {"contactPersons": response["contactPersons"]}


def test_delete_omits_absent_optional_deleted_records() -> None:
    server, _ = registered_tools(
        httpx.MockTransport(lambda request: httpx.Response(200, json={"meta": {}}))
    )
    preview = invoke(server, "api_contact_persons_delete_preview", {"id": "person-1"})

    result = invoke(
        server,
        "api_contact_persons_delete_execute",
        {"confirmation_ticket": preview["confirmation_ticket"]},
    )

    assert result == {"changed_records": {}, "deleted_records": None}


@pytest.mark.parametrize(
    ("status", "response", "expected_code"),
    [
        (401, {"errorCode": "AUTHENTICATION_REQUIRED"}, "AUTH_REQUIRED"),
        (404, {"errorCode": "RECORD_NOT_FOUND"}, "NOT_FOUND"),
    ],
)
def test_execute_propagates_typed_authentication_and_not_found_errors(
    status: int, response: dict[str, object], expected_code: str
) -> None:
    server, _ = registered_tools(
        httpx.MockTransport(lambda request: httpx.Response(status, json=response))
    )
    preview = invoke(
        server,
        "api_contact_persons_create_preview",
        {"contactPerson": {"contactId": "contact-1"}},
    )

    result = invoke(
        server,
        "api_contact_persons_create_execute",
        {"confirmation_ticket": preview["confirmation_ticket"]},
    )

    assert result["code"] == expected_code


def test_execute_rejects_invalid_expired_and_replayed_tickets_without_extra_writes() -> None:
    clock = Clock()
    store = ConfirmationStore(clock)
    server, requests = registered_tools(
        httpx.MockTransport(lambda request: httpx.Response(200, json={"contactPersons": []})),
        confirmations=store,
    )

    invalid = invoke(
        server,
        "api_contact_persons_create_execute",
        {"confirmation_ticket": "not-a-ticket"},
    )
    assert invalid["code"] == "CONFIRMATION_INVALID"

    expired_preview = invoke(
        server,
        "api_contact_persons_create_preview",
        {"contactPerson": {"contactId": "contact-1"}},
    )
    clock.now += timedelta(minutes=6)
    expired = invoke(
        server,
        "api_contact_persons_create_execute",
        {"confirmation_ticket": expired_preview["confirmation_ticket"]},
    )
    assert expired["code"] == "CONFIRMATION_EXPIRED"

    replay_preview = invoke(
        server,
        "api_contact_persons_create_preview",
        {"contactPerson": {"contactId": "contact-1"}},
    )
    first = invoke(
        server,
        "api_contact_persons_create_execute",
        {"confirmation_ticket": replay_preview["confirmation_ticket"]},
    )
    replayed = invoke(
        server,
        "api_contact_persons_create_execute",
        {"confirmation_ticket": replay_preview["confirmation_ticket"]},
    )

    assert first["changed_records"] == {"contactPersons": []}
    assert replayed["code"] == "CONFIRMATION_CONSUMED"
    assert len(requests) == 1
