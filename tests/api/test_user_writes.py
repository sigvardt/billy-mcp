"""Contract tests for ticketed singular Billy user update tools."""

from __future__ import annotations

import asyncio
import json
import logging
from collections.abc import Callable
from datetime import UTC, datetime, timedelta
from typing import cast

import httpx
import pytest
from fastmcp import FastMCP
from pydantic import ValidationError

from billy_mcp.api.user_writes import UserUpdatePreviewInput, register_user_write_tools
from billy_mcp.api.write_protocol import WriteExecuteInput, WriteProtocolService
from billy_mcp.client import BillyHttpClient
from billy_mcp.confirmations import ConfirmationStore
from billy_mcp.models import StableErrorCode

MockHandler = Callable[[httpx.Request], httpx.Response]


class Clock:
    """Controllable clock used only by local confirmation-expiry tests."""

    def __init__(self) -> None:
        self.now = datetime(2026, 7, 30, tzinfo=UTC)

    def __call__(self) -> datetime:
        return self.now


def make_server(
    handler: MockHandler,
    *,
    token: str | None = "user-write-test-token",
    confirmations: ConfirmationStore | None = None,
) -> tuple[FastMCP, list[httpx.Request]]:
    """Create a fully local FastMCP server with a recording locked client."""

    requests: list[httpx.Request] = []

    def recording_handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        return handler(request)

    client = BillyHttpClient(lambda: token, transport=httpx.MockTransport(recording_handler))
    server = FastMCP("user-write-contract-test")
    register_user_write_tools(
        server,
        client,
        WriteProtocolService(client, confirmations or ConfirmationStore()),
    )
    return server, requests


def call_tool(server: FastMCP, tool_name: str, arguments: dict[str, object]) -> dict[str, object]:
    """Call a typed tool and return its structured payload."""

    result = asyncio.run(server.call_tool(tool_name, arguments))
    structured_content = result.structured_content
    assert isinstance(structured_content, dict)
    payload = structured_content.get("result", structured_content)
    assert isinstance(payload, dict)
    return cast(dict[str, object], payload)


def test_registers_exactly_two_flat_typed_user_update_tools() -> None:
    server, _ = make_server(lambda request: httpx.Response(200, json={}))

    by_name = {tool.name: tool for tool in asyncio.run(server.list_tools())}
    expected_properties = {
        "api_users_update_preview": {"id", "user"},
        "api_users_update_execute": {"confirmation_ticket"},
    }
    assert set(by_name) == set(expected_properties)
    assert not {name for name in by_name if "create" in name or "delete" in name or "bulk" in name}
    for name, fields in expected_properties.items():
        schema = by_name[name].parameters
        properties = cast(dict[str, dict[str, object]], schema["properties"])
        assert schema["additionalProperties"] is False
        assert set(properties) == fields
        assert "input" not in properties
        for field in fields & {"id", "confirmation_ticket"}:
            assert properties[field]["minLength"] == 1


@pytest.mark.parametrize(
    ("input_model", "payload"),
    [
        (UserUpdatePreviewInput, {"id": "user-1", "user": {}, "extra": True}),
        (UserUpdatePreviewInput, {"id": "", "user": {}}),
        (UserUpdatePreviewInput, {"id": "user-1", "user": {"id": "other"}}),
        (WriteExecuteInput, {"confirmation_ticket": "ticket", "user": {}}),
        (WriteExecuteInput, {"confirmation_ticket": ""}),
    ],
)
def test_outer_inputs_forbid_extras_empty_values_and_mismatched_body_ids(
    input_model: type[UserUpdatePreviewInput] | type[WriteExecuteInput],
    payload: dict[str, object],
) -> None:
    with pytest.raises(ValidationError):
        input_model.model_validate(payload)


def test_opaque_user_preserves_unknown_fields_and_matching_inner_id() -> None:
    input = UserUpdatePreviewInput.model_validate(
        {
            "id": "user-1",
            "user": {
                "id": "user-1",
                "futureField": {"rank": 2},
            },
        }
    )

    assert input.user["futureField"] == {"rank": 2}


def test_preview_is_mutation_free_and_binds_the_exact_user_request() -> None:
    server, requests = make_server(
        lambda request: pytest.fail(f"preview made HTTP request: {request.method} {request.url}")
    )

    preview = call_tool(
        server,
        "api_users_update_preview",
        {"id": "user-1", "user": {"futureField": {"rank": 2}}},
    )

    assert requests == []
    assert preview["canonical_request"] == {"user": {"futureField": {"rank": 2}}}
    assert preview["expected_effect_state"] == {
        "action": "update",
        "resource": "user",
        "id": "user-1",
    }


def test_execute_sends_exact_user_write_once_and_maps_only_declared_root() -> None:
    response = {
        "users": [{"id": "user-1"}],
        "organizations": [{"id": "organization-1"}],
    }
    server, requests = make_server(lambda request: httpx.Response(200, json=response))

    preview = call_tool(
        server,
        "api_users_update_preview",
        {"id": "user /?", "user": {"futureField": {"rank": 2}}},
    )
    execution = call_tool(
        server,
        "api_users_update_execute",
        {"confirmation_ticket": preview["confirmation_ticket"]},
    )

    assert len(requests) == 1
    request = requests[0]
    assert request.method == "PUT"
    assert request.url.raw_path.decode() == "/v2/users/user%20%2F%3F"
    assert json.loads(request.content) == {"user": {"futureField": {"rank": 2}}}
    assert execution == {"changed_records": {"users": [{"id": "user-1"}]}, "deleted_records": None}
    assert "organizations" not in cast(dict[str, object], execution["changed_records"])


@pytest.mark.parametrize(
    "response",
    [
        {"organizations": [{"id": "organization-1"}]},
        {"users": {"id": "user-1"}},
    ],
)
def test_execute_rejects_missing_or_malformed_required_users_root(
    response: dict[str, object],
) -> None:
    server, _ = make_server(lambda request: httpx.Response(200, json=response))

    preview = call_tool(
        server,
        "api_users_update_preview",
        {"id": "user-1", "user": {"futureField": {"rank": 2}}},
    )
    execution = call_tool(
        server,
        "api_users_update_execute",
        {"confirmation_ticket": preview["confirmation_ticket"]},
    )

    assert execution["code"] == StableErrorCode.VALIDATION_ERROR


def test_tampered_expired_and_replayed_tickets_do_not_make_unexpected_writes() -> None:
    clock = Clock()
    server, requests = make_server(
        lambda request: httpx.Response(200, json={"users": [{"id": "user-1"}]}),
        confirmations=ConfirmationStore(clock),
    )
    preview = call_tool(
        server,
        "api_users_update_preview",
        {"id": "user-1", "user": {"futureField": {"rank": 2}}},
    )
    ticket = cast(str, preview["confirmation_ticket"])

    tampered = call_tool(
        server,
        "api_users_update_execute",
        {"confirmation_ticket": f"{ticket}x"},
    )
    assert tampered["code"] == StableErrorCode.CONFIRMATION_INVALID
    assert requests == []

    expired_preview = call_tool(
        server,
        "api_users_update_preview",
        {"id": "user-2", "user": {"futureField": {"rank": 2}}},
    )
    clock.now += timedelta(minutes=6)
    expired = call_tool(
        server,
        "api_users_update_execute",
        {"confirmation_ticket": expired_preview["confirmation_ticket"]},
    )
    assert expired["code"] == StableErrorCode.CONFIRMATION_EXPIRED
    assert requests == []

    valid_preview = call_tool(
        server,
        "api_users_update_preview",
        {"id": "user-3", "user": {"futureField": {"rank": 2}}},
    )
    first = call_tool(
        server,
        "api_users_update_execute",
        {"confirmation_ticket": valid_preview["confirmation_ticket"]},
    )
    replay = call_tool(
        server,
        "api_users_update_execute",
        {"confirmation_ticket": valid_preview["confirmation_ticket"]},
    )
    assert first["changed_records"] == {"users": [{"id": "user-1"}]}
    assert replay["code"] == StableErrorCode.CONFIRMATION_CONSUMED
    assert len(requests) == 1


@pytest.mark.parametrize(
    ("status", "response", "expected_code"),
    [
        (401, {"errorCode": "AUTHENTICATION_REQUIRED"}, StableErrorCode.AUTH_REQUIRED),
        (404, {"errorCode": "RECORD_NOT_FOUND"}, StableErrorCode.NOT_FOUND),
        (500, {"errorCode": "INTERNAL_SERVER_ERROR"}, StableErrorCode.BILLY_ERROR),
    ],
)
def test_typed_http_errors_propagate_after_one_no_retry_write(
    status: int,
    response: dict[str, str],
    expected_code: StableErrorCode,
) -> None:
    server, requests = make_server(lambda request: httpx.Response(status, json=response))
    preview = call_tool(
        server,
        "api_users_update_preview",
        {"id": "user-1", "user": {"futureField": {"rank": 2}}},
    )
    error = call_tool(
        server,
        "api_users_update_execute",
        {"confirmation_ticket": preview["confirmation_ticket"]},
    )

    assert error["code"] == expected_code
    assert len(requests) == 1


def test_missing_token_returns_typed_auth_required_without_network_activity() -> None:
    server, requests = make_server(
        lambda request: pytest.fail(f"missing token attempted HTTP request: {request.url}"),
        token="",
    )
    preview = call_tool(
        server,
        "api_users_update_preview",
        {"id": "user-1", "user": {"futureField": {"rank": 2}}},
    )
    error = call_tool(
        server,
        "api_users_update_execute",
        {"confirmation_ticket": preview["confirmation_ticket"]},
    )

    assert error["code"] == StableErrorCode.AUTH_REQUIRED
    assert requests == []


def test_sensitive_user_values_are_not_written_to_logs(caplog: pytest.LogCaptureFixture) -> None:
    caplog.set_level(logging.DEBUG)
    server, _ = make_server(lambda request: httpx.Response(200, json={}))
    sensitive_email = "user@example.invalid"
    sensitive_phone = "+4512345678"

    preview = call_tool(
        server,
        "api_users_update_preview",
        {
            "id": "user-1",
            "user": {"email": sensitive_email, "phone": sensitive_phone},
        },
    )

    assert sensitive_email not in caplog.text
    assert sensitive_phone not in caplog.text
    assert cast(str, preview["confirmation_ticket"]) not in caplog.text
