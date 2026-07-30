"""Contract tests for ticketed singular Billy invoice-reminder create tools."""

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

from billy_mcp.api.invoice_reminder_writes import (
    InvoiceReminderCreatePreviewInput,
    register_invoice_reminder_write_tools,
)
from billy_mcp.api.write_protocol import WriteExecuteInput, WriteProtocolService
from billy_mcp.client import BillyHttpClient
from billy_mcp.confirmations import ConfirmationStore
from billy_mcp.models import StableErrorCode, ToolError

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
    token: str | None = "invoice-reminder-write-test-token",
    confirmations: ConfirmationStore | None = None,
) -> tuple[FastMCP, list[httpx.Request], WriteProtocolService]:
    """Create a fully local FastMCP server with a recording locked client."""

    requests: list[httpx.Request] = []

    def recording_handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        return handler(request)

    client = BillyHttpClient(lambda: token, transport=httpx.MockTransport(recording_handler))
    write_protocol = WriteProtocolService(client, confirmations or ConfirmationStore())
    server = FastMCP("invoice-reminder-write-contract-test")
    register_invoice_reminder_write_tools(server, client, write_protocol)
    return server, requests, write_protocol


def call_tool(server: FastMCP, tool_name: str, arguments: dict[str, object]) -> dict[str, object]:
    """Call a typed tool and return its structured payload."""

    result = asyncio.run(server.call_tool(tool_name, arguments))
    structured_content = result.structured_content
    assert isinstance(structured_content, dict)
    payload = structured_content.get("result", structured_content)
    assert isinstance(payload, dict)
    return cast(dict[str, object], payload)


def test_registers_exactly_two_flat_typed_invoice_reminder_create_tools() -> None:
    server, _, _ = make_server(lambda request: httpx.Response(200, json={}))

    by_name = {tool.name: tool for tool in asyncio.run(server.list_tools())}
    expected_properties = {
        "api_invoice_reminders_create_preview": {"invoiceReminder"},
        "api_invoice_reminders_create_execute": {"confirmation_ticket"},
    }
    assert set(by_name) == set(expected_properties)
    assert not {
        name
        for name in by_name
        if any(forbidden in name for forbidden in ("update", "delete", "bulk"))
    }
    for name, fields in expected_properties.items():
        schema = by_name[name].parameters
        properties = cast(dict[str, dict[str, object]], schema["properties"])
        assert schema["additionalProperties"] is False
        assert set(properties) == fields
        assert "input" not in properties
    assert (
        by_name["api_invoice_reminders_create_execute"].parameters["properties"][
            "confirmation_ticket"
        ]["minLength"]
        == 1
    )


@pytest.mark.parametrize(
    "payload",
    [
        {},
        {"invoiceReminder": {}, "extra": True},
    ],
)
def test_preview_input_rejects_missing_or_undeclared_outer_fields(
    payload: dict[str, object],
) -> None:
    with pytest.raises(ValidationError):
        InvoiceReminderCreatePreviewInput.model_validate(payload)


@pytest.mark.parametrize(
    "payload",
    [
        {"confirmation_ticket": "ticket", "invoiceReminder": {}},
        {"confirmation_ticket": ""},
    ],
)
def test_execute_input_is_ticket_only_and_nonempty(payload: dict[str, object]) -> None:
    with pytest.raises(ValidationError):
        WriteExecuteInput.model_validate(payload)


def test_opaque_invoice_reminder_preserves_unknown_inner_values() -> None:
    input = InvoiceReminderCreatePreviewInput.model_validate(
        {
            "invoiceReminder": {
                "futureField": {"rank": 2, "nested": ["untyped", True]},
                "anotherUnknownField": None,
            }
        }
    )

    assert input.invoiceReminder["futureField"] == {
        "rank": 2,
        "nested": ["untyped", True],
    }
    assert input.invoiceReminder["anotherUnknownField"] is None


def test_preview_is_mutation_free_and_binds_the_exact_invoice_reminder_request() -> None:
    server, requests, _ = make_server(
        lambda request: pytest.fail(f"preview made HTTP request: {request.method} {request.url}")
    )
    request: dict[str, object] = {"invoiceReminder": {"unknown": {"rank": 2}}}

    preview = call_tool(server, "api_invoice_reminders_create_preview", request)

    assert requests == []
    assert preview["canonical_request"] == request
    assert preview["expected_effect_state"] == {
        "action": "create",
        "resource": "invoiceReminder",
    }


def test_execute_sends_one_exact_invoice_reminder_post_and_maps_only_declared_root() -> None:
    response = {
        "invoiceReminders": [{"id": "invoice-reminder-1"}],
        "invoices": [{"id": "invoice-1"}],
    }
    server, requests, _ = make_server(lambda request: httpx.Response(200, json=response))
    request: dict[str, object] = {"invoiceReminder": {"unknown": {"rank": 2}}}

    preview = call_tool(server, "api_invoice_reminders_create_preview", request)
    execution = call_tool(
        server,
        "api_invoice_reminders_create_execute",
        {"confirmation_ticket": preview["confirmation_ticket"]},
    )

    assert len(requests) == 1
    sent_request = requests[0]
    assert sent_request.method == "POST"
    assert sent_request.url.raw_path.decode() == "/v2/invoiceReminders"
    assert json.loads(sent_request.content) == request
    assert execution == {
        "changed_records": {"invoiceReminders": [{"id": "invoice-reminder-1"}]},
        "deleted_records": None,
    }
    assert "invoices" not in cast(dict[str, object], execution["changed_records"])


@pytest.mark.parametrize(
    "response",
    [
        {"invoices": [{"id": "invoice-1"}]},
        {"invoiceReminders": {"id": "invoice-reminder-1"}},
    ],
)
def test_execute_rejects_missing_or_malformed_required_invoice_reminders_root(
    response: dict[str, object],
) -> None:
    server, _, _ = make_server(lambda request: httpx.Response(200, json=response))
    preview = call_tool(
        server,
        "api_invoice_reminders_create_preview",
        {"invoiceReminder": {"futureField": {"rank": 2}}},
    )

    execution = call_tool(
        server,
        "api_invoice_reminders_create_execute",
        {"confirmation_ticket": preview["confirmation_ticket"]},
    )

    assert execution["code"] == StableErrorCode.VALIDATION_ERROR


def test_tamper_wrong_executor_expiry_and_replay_do_not_make_unexpected_writes() -> None:
    clock = Clock()
    server, requests, write_protocol = make_server(
        lambda request: httpx.Response(200, json={"invoiceReminders": [{"id": "reminder-1"}]}),
        confirmations=ConfirmationStore(clock),
    )
    preview = call_tool(
        server,
        "api_invoice_reminders_create_preview",
        {"invoiceReminder": {"futureField": {"rank": 2}}},
    )
    ticket = cast(str, preview["confirmation_ticket"])

    tampered = call_tool(
        server,
        "api_invoice_reminders_create_execute",
        {"confirmation_ticket": f"{ticket}x"},
    )
    wrong_executor = write_protocol.execute(
        WriteExecuteInput(confirmation_ticket=ticket),
        execute_tool_name="api_invoice_reminders_unregistered_execute",
    )
    assert tampered["code"] == StableErrorCode.CONFIRMATION_INVALID
    assert isinstance(wrong_executor, ToolError)
    assert wrong_executor.code == StableErrorCode.CONFIRMATION_MISMATCH
    assert requests == []

    first = call_tool(
        server,
        "api_invoice_reminders_create_execute",
        {"confirmation_ticket": ticket},
    )
    replay = call_tool(
        server,
        "api_invoice_reminders_create_execute",
        {"confirmation_ticket": ticket},
    )
    assert first["changed_records"] == {"invoiceReminders": [{"id": "reminder-1"}]}
    assert replay["code"] == StableErrorCode.CONFIRMATION_CONSUMED
    assert len(requests) == 1

    expired_preview = call_tool(
        server,
        "api_invoice_reminders_create_preview",
        {"invoiceReminder": {"futureField": {"rank": 2}}},
    )
    clock.now += timedelta(minutes=6)
    expired = call_tool(
        server,
        "api_invoice_reminders_create_execute",
        {"confirmation_ticket": expired_preview["confirmation_ticket"]},
    )
    assert expired["code"] == StableErrorCode.CONFIRMATION_EXPIRED
    assert len(requests) == 1


@pytest.mark.parametrize(
    ("status", "response", "expected_code"),
    [
        (401, {"errorCode": "AUTHENTICATION_REQUIRED"}, StableErrorCode.AUTH_REQUIRED),
        (404, {"errorCode": "RECORD_NOT_FOUND"}, StableErrorCode.NOT_FOUND),
    ],
)
def test_typed_http_errors_propagate_after_one_write(
    status: int,
    response: dict[str, str],
    expected_code: StableErrorCode,
) -> None:
    server, requests, _ = make_server(lambda request: httpx.Response(status, json=response))
    preview = call_tool(
        server,
        "api_invoice_reminders_create_preview",
        {"invoiceReminder": {"futureField": {"rank": 2}}},
    )
    error = call_tool(
        server,
        "api_invoice_reminders_create_execute",
        {"confirmation_ticket": preview["confirmation_ticket"]},
    )

    assert error["code"] == expected_code
    assert len(requests) == 1


def test_empty_token_returns_typed_auth_required_without_network_activity() -> None:
    server, requests, _ = make_server(
        lambda request: pytest.fail(f"missing token attempted HTTP request: {request.url}"),
        token="",
    )
    preview = call_tool(
        server,
        "api_invoice_reminders_create_preview",
        {"invoiceReminder": {"futureField": {"rank": 2}}},
    )
    error = call_tool(
        server,
        "api_invoice_reminders_create_execute",
        {"confirmation_ticket": preview["confirmation_ticket"]},
    )

    assert error["code"] == StableErrorCode.AUTH_REQUIRED
    assert requests == []


def test_failed_invoice_reminder_write_is_not_retried() -> None:
    server, requests, _ = make_server(
        lambda request: httpx.Response(500, json={"errorCode": "INTERNAL_SERVER_ERROR"})
    )
    preview = call_tool(
        server,
        "api_invoice_reminders_create_preview",
        {"invoiceReminder": {"futureField": {"rank": 2}}},
    )
    error = call_tool(
        server,
        "api_invoice_reminders_create_execute",
        {"confirmation_ticket": preview["confirmation_ticket"]},
    )

    assert error["code"] == StableErrorCode.BILLY_ERROR
    assert len(requests) == 1
