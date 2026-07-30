"""Contract tests for ticketed singular Billy contact-balance-payment write tools."""

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

from billy_mcp.api.contact_balance_payment_writes import (
    ContactBalancePaymentCreatePreviewInput,
    ContactBalancePaymentUpdatePreviewInput,
    register_contact_balance_payment_write_tools,
)
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
    token: str | None = "contact-balance-payment-write-test-token",
    confirmations: ConfirmationStore | None = None,
) -> tuple[FastMCP, list[httpx.Request]]:
    """Create a fully local FastMCP server with a recording locked client."""

    requests: list[httpx.Request] = []

    def recording_handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        return handler(request)

    client = BillyHttpClient(lambda: token, transport=httpx.MockTransport(recording_handler))
    server = FastMCP("contact-balance-payment-write-contract-test")
    register_contact_balance_payment_write_tools(
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


def test_registers_exactly_four_flat_typed_contact_balance_payment_write_tools() -> None:
    server, _ = make_server(lambda request: httpx.Response(200, json={}))

    by_name = {tool.name: tool for tool in asyncio.run(server.list_tools())}
    expected_properties = {
        "api_contact_balance_payments_create_preview": {"contactBalancePayment"},
        "api_contact_balance_payments_create_execute": {"confirmation_ticket"},
        "api_contact_balance_payments_update_preview": {"id", "contactBalancePayment"},
        "api_contact_balance_payments_update_execute": {"confirmation_ticket"},
    }
    assert set(by_name) == set(expected_properties)
    assert not {name for name in by_name if "delete" in name or "bulk" in name}
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
        (ContactBalancePaymentCreatePreviewInput, {"contactBalancePayment": {}, "extra": True}),
        (
            ContactBalancePaymentUpdatePreviewInput,
            {"id": "payment-1", "contactBalancePayment": {}, "extra": True},
        ),
        (ContactBalancePaymentUpdatePreviewInput, {"id": "", "contactBalancePayment": {}}),
        (
            ContactBalancePaymentUpdatePreviewInput,
            {"id": "payment-1", "contactBalancePayment": {"id": "other"}},
        ),
        (WriteExecuteInput, {"confirmation_ticket": "ticket", "contactBalancePayment": {}}),
        (WriteExecuteInput, {"confirmation_ticket": ""}),
    ],
)
def test_outer_inputs_forbid_extras_empty_values_and_mismatched_body_ids(
    input_model: type[ContactBalancePaymentCreatePreviewInput]
    | type[ContactBalancePaymentUpdatePreviewInput]
    | type[WriteExecuteInput],
    payload: dict[str, object],
) -> None:
    with pytest.raises(ValidationError):
        input_model.model_validate(payload)


def test_opaque_contact_balance_payment_preserves_unknown_fields_and_matching_inner_id() -> None:
    input = ContactBalancePaymentUpdatePreviewInput.model_validate(
        {
            "id": "payment-1",
            "contactBalancePayment": {
                "id": "payment-1",
                "futureField": {"rank": 2},
            },
        }
    )

    assert input.contactBalancePayment["futureField"] == {"rank": 2}


@pytest.mark.parametrize(
    ("tool_name", "arguments", "expected_request", "expected_effect"),
    [
        (
            "api_contact_balance_payments_create_preview",
            {"contactBalancePayment": {"unknown": {"rank": 2}}},
            {"contactBalancePayment": {"unknown": {"rank": 2}}},
            {"action": "create", "resource": "contactBalancePayment"},
        ),
        (
            "api_contact_balance_payments_update_preview",
            {"id": "payment-1", "contactBalancePayment": {"futureField": {"rank": 2}}},
            {"contactBalancePayment": {"futureField": {"rank": 2}}},
            {"action": "update", "resource": "contactBalancePayment", "id": "payment-1"},
        ),
    ],
)
def test_previews_are_mutation_free_and_bind_exact_contact_balance_payment_requests(
    tool_name: str,
    arguments: dict[str, object],
    expected_request: dict[str, object],
    expected_effect: dict[str, object],
) -> None:
    server, requests = make_server(
        lambda request: pytest.fail(f"preview made HTTP request: {request.method} {request.url}")
    )

    preview = call_tool(server, tool_name, arguments)

    assert requests == []
    assert preview["canonical_request"] == expected_request
    assert preview["expected_effect_state"] == expected_effect


@pytest.mark.parametrize(
    ("preview_name", "execute_name", "arguments", "method", "path", "body"),
    [
        (
            "api_contact_balance_payments_create_preview",
            "api_contact_balance_payments_create_execute",
            {"contactBalancePayment": {"unknown": {"rank": 2}}},
            "POST",
            "/v2/contactBalancePayments",
            {"contactBalancePayment": {"unknown": {"rank": 2}}},
        ),
        (
            "api_contact_balance_payments_update_preview",
            "api_contact_balance_payments_update_execute",
            {"id": "payment /?", "contactBalancePayment": {"futureField": {"rank": 2}}},
            "PUT",
            "/v2/contactBalancePayments/payment%20%2F%3F",
            {"contactBalancePayment": {"futureField": {"rank": 2}}},
        ),
    ],
)
def test_execute_sends_exact_contact_balance_payment_write_once_and_maps_only_declared_root(
    preview_name: str,
    execute_name: str,
    arguments: dict[str, object],
    method: str,
    path: str,
    body: dict[str, object],
) -> None:
    response = {
        "contactBalancePayments": [{"id": "payment-1"}],
        "bankPayments": [{"id": "bank-1"}],
    }
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
    assert json.loads(request.content) == body
    assert execution == {
        "changed_records": {"contactBalancePayments": [{"id": "payment-1"}]},
        "deleted_records": None,
    }
    assert "bankPayments" not in cast(dict[str, object], execution["changed_records"])


@pytest.mark.parametrize(
    "response",
    [
        {"bankPayments": [{"id": "bank-1"}]},
        {"contactBalancePayments": {"id": "payment-1"}},
    ],
)
def test_execute_rejects_missing_or_malformed_required_contact_balance_payments_root(
    response: dict[str, object],
) -> None:
    server, _ = make_server(lambda request: httpx.Response(200, json=response))

    preview = call_tool(
        server,
        "api_contact_balance_payments_create_preview",
        {"contactBalancePayment": {"futureField": {"rank": 2}}},
    )
    execution = call_tool(
        server,
        "api_contact_balance_payments_create_execute",
        {"confirmation_ticket": preview["confirmation_ticket"]},
    )

    assert execution["code"] == StableErrorCode.VALIDATION_ERROR


def test_tamper_wrong_executor_expiry_and_replay_do_not_make_unexpected_writes() -> None:
    clock = Clock()
    server, requests = make_server(
        lambda request: httpx.Response(200, json={"contactBalancePayments": [{"id": "payment-1"}]}),
        confirmations=ConfirmationStore(clock),
    )
    preview = call_tool(
        server,
        "api_contact_balance_payments_create_preview",
        {"contactBalancePayment": {"futureField": {"rank": 2}}},
    )
    ticket = cast(str, preview["confirmation_ticket"])

    tampered = call_tool(
        server,
        "api_contact_balance_payments_create_execute",
        {"confirmation_ticket": f"{ticket}x"},
    )
    wrong_executor = call_tool(
        server,
        "api_contact_balance_payments_update_execute",
        {"confirmation_ticket": ticket},
    )
    assert tampered["code"] == StableErrorCode.CONFIRMATION_INVALID
    assert wrong_executor["code"] == StableErrorCode.CONFIRMATION_MISMATCH
    assert requests == []

    first = call_tool(
        server,
        "api_contact_balance_payments_create_execute",
        {"confirmation_ticket": ticket},
    )
    replay = call_tool(
        server,
        "api_contact_balance_payments_create_execute",
        {"confirmation_ticket": ticket},
    )
    assert first["changed_records"] == {"contactBalancePayments": [{"id": "payment-1"}]}
    assert replay["code"] == StableErrorCode.CONFIRMATION_CONSUMED
    assert len(requests) == 1

    expired_preview = call_tool(
        server,
        "api_contact_balance_payments_create_preview",
        {"contactBalancePayment": {"futureField": {"rank": 2}}},
    )
    clock.now += timedelta(minutes=6)
    expired = call_tool(
        server,
        "api_contact_balance_payments_create_execute",
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
    server, requests = make_server(lambda request: httpx.Response(status, json=response))
    preview = call_tool(
        server,
        "api_contact_balance_payments_create_preview",
        {"contactBalancePayment": {"futureField": {"rank": 2}}},
    )
    error = call_tool(
        server,
        "api_contact_balance_payments_create_execute",
        {"confirmation_ticket": preview["confirmation_ticket"]},
    )

    assert error["code"] == expected_code
    assert len(requests) == 1


def test_empty_token_returns_typed_auth_required_without_network_activity() -> None:
    server, requests = make_server(
        lambda request: pytest.fail(f"missing token attempted HTTP request: {request.url}"),
        token="",
    )
    preview = call_tool(
        server,
        "api_contact_balance_payments_create_preview",
        {"contactBalancePayment": {"futureField": {"rank": 2}}},
    )
    error = call_tool(
        server,
        "api_contact_balance_payments_create_execute",
        {"confirmation_ticket": preview["confirmation_ticket"]},
    )

    assert error["code"] == StableErrorCode.AUTH_REQUIRED
    assert requests == []


def test_failed_contact_balance_payment_write_is_not_retried() -> None:
    server, requests = make_server(
        lambda request: httpx.Response(500, json={"errorCode": "INTERNAL_SERVER_ERROR"})
    )
    preview = call_tool(
        server,
        "api_contact_balance_payments_create_preview",
        {"contactBalancePayment": {"futureField": {"rank": 2}}},
    )
    error = call_tool(
        server,
        "api_contact_balance_payments_create_execute",
        {"confirmation_ticket": preview["confirmation_ticket"]},
    )

    assert error["code"] == StableErrorCode.BILLY_ERROR
    assert len(requests) == 1
