"""Offline contracts for ticketed Billy invoice email and delivery specials."""

from __future__ import annotations

import asyncio
import json
from collections.abc import Callable
from datetime import UTC, datetime, timedelta
from typing import cast

import httpx
import pytest
from fastmcp import FastMCP
from fastmcp.exceptions import ValidationError as FastMCPValidationError
from pydantic import ValidationError

from billy_mcp.api.invoice_email_delivery_writes import (
    InvoiceDeliveryPreviewInput,
    InvoiceEmailDeliveryExecuteInput,
    InvoiceEmailDeliveryService,
    InvoiceEmailPreviewInput,
    register_invoice_email_delivery_write_tools,
)
from billy_mcp.client import BillyHttpClient
from billy_mcp.config import AppConfig
from billy_mcp.confirmations import ConfirmationBinding, ConfirmationFailure, ConfirmationStore
from billy_mcp.models import StableErrorCode, ToolError
from billy_mcp.redaction import REDACTED

MockHandler = Callable[[httpx.Request], httpx.Response]


class Clock:
    """Controllable clock used only for ticket-expiry assertions."""

    def __init__(self) -> None:
        self.now = datetime(2026, 7, 30, tzinfo=UTC)

    def __call__(self) -> datetime:
        return self.now


def make_server(
    handler: MockHandler,
    *,
    token: str | None = "invoice-email-delivery-test-token",
    confirmations: ConfirmationStore | None = None,
    selected_organization: str | None = "selected-organization",
) -> tuple[FastMCP, list[httpx.Request]]:
    """Create a local FastMCP server over a recording, locked HTTP transport."""

    requests: list[httpx.Request] = []

    def recording_handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        return handler(request)

    client = BillyHttpClient(lambda: token, transport=httpx.MockTransport(recording_handler))
    server = FastMCP("invoice-email-delivery-contract-test")
    register_invoice_email_delivery_write_tools(
        server,
        client,
        AppConfig(selected_organization=selected_organization),
        confirmations or ConfirmationStore(),
    )
    return server, requests


def call_tool(server: FastMCP, tool_name: str, arguments: dict[str, object]) -> dict[str, object]:
    """Call a local typed MCP tool and return its structured payload."""

    result = asyncio.run(server.call_tool(tool_name, arguments))
    structured_content = result.structured_content
    assert isinstance(structured_content, dict)
    payload = structured_content.get("result", structured_content)
    assert isinstance(payload, dict)
    return cast(dict[str, object], payload)


def email_arguments() -> dict[str, object]:
    """Return one innocuous valid invoice-email preview request."""

    return {
        "invoiceId": "invoice-1",
        "contactPersonId": "contact-person-1",
        "emailBody": "Invoice body",
        "emailSubject": "Invoice subject",
    }


def delivery_arguments(*, receiver_id_type: str = "gln") -> dict[str, object]:
    """Return one valid invoice-delivery preview request for either receiver type."""

    arguments: dict[str, object] = {
        "invoiceId": "invoice-1",
        "organizationId": "organization-1",
        "receiverIdType": receiver_id_type,
        "senderUserId": "sender-user-1",
    }
    if receiver_id_type == "gln":
        arguments["receiverGln"] = "5790000000001"
    return arguments


def test_registers_exactly_four_flat_typed_special_tools() -> None:
    server, _ = make_server(lambda request: httpx.Response(200, json={}))

    by_name = {tool.name: tool for tool in asyncio.run(server.list_tools())}
    expected_properties = {
        "api_invoices_send_email_preview": {
            "invoiceId",
            "contactPersonId",
            "emailBody",
            "emailSubject",
            "copyToUserId",
        },
        "api_invoices_send_email_execute": {"confirmation_ticket"},
        "api_invoice_deliveries_create_preview": {
            "invoiceId",
            "organizationId",
            "receiverIdType",
            "senderUserId",
            "receiverGln",
            "orderReference",
        },
        "api_invoice_deliveries_create_execute": {"confirmation_ticket"},
    }

    assert set(by_name) == set(expected_properties)
    assert not {
        name
        for name in by_name
        if any(forbidden in name for forbidden in ("list", "get", "update", "delete", "webhook"))
    }
    for name, fields in expected_properties.items():
        schema = by_name[name].parameters
        properties = cast(dict[str, dict[str, object]], schema["properties"])
        assert schema["additionalProperties"] is False
        assert set(properties) == fields
        assert "input" not in properties
        assert not {
            field
            for field in properties
            if field in {"approval", "destination_url", "emailAddress", "receiverCvr"}
        }
    assert (
        by_name["api_invoices_send_email_execute"].parameters["properties"]["confirmation_ticket"][
            "minLength"
        ]
        == 1
    )


@pytest.mark.parametrize(
    ("input_model", "payload"),
    [
        (InvoiceEmailPreviewInput, {**email_arguments(), "unknown": True}),
        (InvoiceEmailPreviewInput, {**email_arguments(), "invoiceId": 1}),
        (InvoiceEmailPreviewInput, {**email_arguments(), "emailBody": "  "}),
        (InvoiceEmailPreviewInput, {**email_arguments(), "copyToUserId": "  "}),
        (InvoiceDeliveryPreviewInput, {**delivery_arguments(), "unknown": True}),
        (InvoiceDeliveryPreviewInput, {**delivery_arguments(), "organizationId": 1}),
        (InvoiceDeliveryPreviewInput, {**delivery_arguments(), "receiverGln": "123"}),
        (
            InvoiceDeliveryPreviewInput,
            {**delivery_arguments(receiver_id_type="cvr"), "receiverGln": "5790000000001"},
        ),
        (InvoiceDeliveryPreviewInput, {**delivery_arguments(), "receiverIdType": "other"}),
        (InvoiceEmailDeliveryExecuteInput, {"confirmation_ticket": "ticket", "invoiceId": "x"}),
        (InvoiceEmailDeliveryExecuteInput, {"confirmation_ticket": "  "}),
    ],
)
def test_input_models_are_strict_and_reject_invalid_or_undeclared_values(
    input_model: type[InvoiceEmailPreviewInput]
    | type[InvoiceDeliveryPreviewInput]
    | type[InvoiceEmailDeliveryExecuteInput],
    payload: dict[str, object],
) -> None:
    with pytest.raises(ValidationError):
        input_model.model_validate(payload)


@pytest.mark.parametrize(
    ("tool_name", "arguments"),
    [
        ("api_invoices_send_email_preview", {**email_arguments(), "emailBody": 1}),
        ("api_invoices_send_email_preview", {**email_arguments(), "unknown": True}),
        ("api_invoice_deliveries_create_preview", {**delivery_arguments(), "receiverGln": 1}),
        ("api_invoice_deliveries_create_preview", {**delivery_arguments(), "unknown": True}),
        ("api_invoices_send_email_execute", {"confirmation_ticket": 1}),
        ("api_invoice_deliveries_create_execute", {"confirmation_ticket": 1}),
    ],
)
def test_registered_tools_reject_non_strict_or_extra_input_before_http(
    tool_name: str, arguments: dict[str, object]
) -> None:
    server, requests = make_server(
        lambda request: pytest.fail(
            f"invalid input made HTTP request: {request.method} {request.url}"
        )
    )

    with pytest.raises(FastMCPValidationError):
        call_tool(server, tool_name, arguments)

    assert requests == []


def test_previews_make_no_http_and_bind_exact_selected_organization_target_and_request() -> None:
    server, requests = make_server(
        lambda request: pytest.fail(f"preview made HTTP request: {request.method} {request.url}")
    )

    email_preview = call_tool(server, "api_invoices_send_email_preview", email_arguments())
    delivery_preview = call_tool(
        server,
        "api_invoice_deliveries_create_preview",
        {**delivery_arguments(), "orderReference": "order-reference-1"},
    )

    assert requests == []
    assert email_preview["canonical_request"] == {
        "invoiceId": "invoice-1",
        "organizationId": "selected-organization",
        "email": {
            "contactPersonId": "contact-person-1",
            "emailBody": "Invoice body",
            "emailSubject": "Invoice subject",
        },
    }
    assert email_preview["expected_effect_state"] == {
        "action": "send_email",
        "resource": "invoice",
        "invoiceId": "invoice-1",
    }
    assert delivery_preview["canonical_request"] == {
        "invoiceDelivery": {
            "invoiceId": "invoice-1",
            "organizationId": "organization-1",
            "receiverIdType": "gln",
            "senderUserId": "sender-user-1",
            "receiverGln": "5790000000001",
            "orderReference": "order-reference-1",
        }
    }
    assert delivery_preview["expected_effect_state"] == {
        "action": "create_invoice_delivery",
        "resource": "invoiceDelivery",
        "invoiceId": "invoice-1",
    }


def test_email_execute_posts_the_exact_nested_body_once_and_omits_unset_copy_to() -> None:
    server, requests = make_server(
        lambda request: httpx.Response(
            200,
            json={
                "changed_records": [
                    {
                        "id": "email-1",
                        "emailBody": "upstream body echo",
                        "emailSubject": "upstream subject echo",
                    }
                ]
            },
        )
    )
    preview = call_tool(server, "api_invoices_send_email_preview", email_arguments())

    execution = call_tool(
        server,
        "api_invoices_send_email_execute",
        {"confirmation_ticket": preview["confirmation_ticket"]},
    )

    assert len(requests) == 1
    request = requests[0]
    assert request.method == "POST"
    assert str(request.url) == "https://api.billysbilling.com/v2/invoices/invoice-1/emails"
    assert json.loads(request.content) == {
        "email": {
            "contactPersonId": "contact-person-1",
            "emailBody": "Invoice body",
            "emailSubject": "Invoice subject",
        }
    }
    records = cast(list[dict[str, object]], execution["changed_records"])
    assert records == [{"id": "email-1", "emailBody": REDACTED, "emailSubject": REDACTED}]


def test_email_execute_includes_only_the_documented_optional_copy_to_user_id() -> None:
    server, requests = make_server(
        lambda request: httpx.Response(200, json={"changed_records": []})
    )
    preview = call_tool(
        server,
        "api_invoices_send_email_preview",
        {**email_arguments(), "copyToUserId": "copy-user-1"},
    )

    call_tool(
        server,
        "api_invoices_send_email_execute",
        {"confirmation_ticket": preview["confirmation_ticket"]},
    )

    assert json.loads(requests[0].content) == {
        "email": {
            "contactPersonId": "contact-person-1",
            "emailBody": "Invoice body",
            "emailSubject": "Invoice subject",
            "copyToUserId": "copy-user-1",
        }
    }


def test_delivery_execute_posts_only_the_collection_route_and_cvr_never_invents_a_value() -> None:
    server, requests = make_server(
        lambda request: httpx.Response(
            200,
            json={"invoiceDelivery": {"id": "delivery-1", "organizationId": "organization-1"}},
        )
    )
    preview = call_tool(
        server,
        "api_invoice_deliveries_create_preview",
        {**delivery_arguments(receiver_id_type="cvr"), "orderReference": "order-reference-1"},
    )

    execution = call_tool(
        server,
        "api_invoice_deliveries_create_execute",
        {"confirmation_ticket": preview["confirmation_ticket"]},
    )

    assert len(requests) == 1
    request = requests[0]
    assert request.method == "POST"
    assert str(request.url) == "https://api.billysbilling.com/v2/invoiceDeliveries"
    assert json.loads(request.content) == {
        "invoiceDelivery": {
            "invoiceId": "invoice-1",
            "organizationId": "organization-1",
            "receiverIdType": "cvr",
            "senderUserId": "sender-user-1",
            "orderReference": "order-reference-1",
        }
    }
    assert execution == {
        "invoiceDelivery": {"id": "delivery-1", "organizationId": "organization-1"}
    }


def test_binding_rejects_tool_organization_target_request_and_effect_tampering() -> None:
    client = BillyHttpClient(
        lambda: "token",
        transport=httpx.MockTransport(
            lambda request: httpx.Response(200, json={"changed_records": []})
        ),
    )
    confirmations = ConfirmationStore()
    service = InvoiceEmailDeliveryService(
        client,
        confirmations,
        selected_organization="selected-organization",
    )
    preview = service.preview_email(InvoiceEmailPreviewInput.model_validate(email_arguments()))
    binding = ConfirmationBinding(
        tool="api_invoices_send_email_execute",
        organization_id="selected-organization",
        target="invoice-1",
        request=cast(dict[str, object], preview.canonical_request),
        expected_effect_state=cast(dict[str, object], preview.expected_effect_state),
    )
    bound_ticket = confirmations.issue(binding).value

    for changed_binding in (
        binding.model_copy(update={"tool": "api_other_execute"}),
        binding.model_copy(update={"organization_id": "other-organization"}),
        binding.model_copy(update={"target": "other-invoice"}),
        binding.model_copy(update={"request": {"email": {"emailBody": "other"}}}),
        binding.model_copy(update={"expected_effect_state": {"action": "other"}}),
    ):
        with pytest.raises(ConfirmationFailure) as failure:
            confirmations.consume(bound_ticket, changed_binding)
        assert failure.value.error.code is StableErrorCode.CONFIRMATION_MISMATCH

    success = service.execute_email(
        InvoiceEmailDeliveryExecuteInput(confirmation_ticket=preview.confirmation_ticket),
        execute_tool_name="api_invoices_send_email_execute",
    )
    assert not isinstance(success, ToolError)


def test_wrong_executor_tampering_expiry_and_replay_never_make_extra_posts() -> None:
    clock = Clock()
    server, requests = make_server(
        lambda request: httpx.Response(200, json={"changed_records": []}),
        confirmations=ConfirmationStore(clock),
    )
    preview = call_tool(server, "api_invoices_send_email_preview", email_arguments())
    ticket = cast(str, preview["confirmation_ticket"])

    tampered = call_tool(
        server,
        "api_invoices_send_email_execute",
        {"confirmation_ticket": f"{ticket}x"},
    )
    wrong_executor = call_tool(
        server,
        "api_invoice_deliveries_create_execute",
        {"confirmation_ticket": ticket},
    )
    assert tampered["code"] == StableErrorCode.CONFIRMATION_INVALID
    assert wrong_executor["code"] == StableErrorCode.CONFIRMATION_MISMATCH
    assert requests == []

    first = call_tool(
        server,
        "api_invoices_send_email_execute",
        {"confirmation_ticket": ticket},
    )
    replay = call_tool(
        server,
        "api_invoices_send_email_execute",
        {"confirmation_ticket": ticket},
    )
    assert first == {"changed_records": []}
    assert replay["code"] == StableErrorCode.CONFIRMATION_CONSUMED
    assert len(requests) == 1

    expired_preview = call_tool(server, "api_invoices_send_email_preview", email_arguments())
    clock.now += timedelta(minutes=6)
    expired = call_tool(
        server,
        "api_invoices_send_email_execute",
        {"confirmation_ticket": expired_preview["confirmation_ticket"]},
    )
    assert expired["code"] == StableErrorCode.CONFIRMATION_EXPIRED
    assert len(requests) == 1


@pytest.mark.parametrize(
    ("tool_name", "preview_name", "arguments", "response"),
    [
        (
            "api_invoices_send_email_execute",
            "api_invoices_send_email_preview",
            email_arguments(),
            {"unexpected": []},
        ),
        (
            "api_invoices_send_email_execute",
            "api_invoices_send_email_preview",
            email_arguments(),
            {"changed_records": {"id": "not-a-list"}},
        ),
        (
            "api_invoice_deliveries_create_execute",
            "api_invoice_deliveries_create_preview",
            delivery_arguments(),
            {"unexpected": {}},
        ),
        (
            "api_invoice_deliveries_create_execute",
            "api_invoice_deliveries_create_preview",
            delivery_arguments(),
            {"invoiceDelivery": []},
        ),
    ],
)
def test_execute_returns_stable_error_for_unknown_or_malformed_success_envelopes(
    tool_name: str,
    preview_name: str,
    arguments: dict[str, object],
    response: dict[str, object],
) -> None:
    server, requests = make_server(lambda request: httpx.Response(200, json=response))
    preview = call_tool(server, preview_name, arguments)

    result = call_tool(server, tool_name, {"confirmation_ticket": preview["confirmation_ticket"]})

    assert result["code"] == StableErrorCode.BILLY_ERROR
    details = cast(dict[str, object], result["details"])
    assert details["expected_root"] in {"changed_records", "invoiceDelivery"}
    assert len(requests) == 1


def test_upstream_errors_redact_email_subject_and_body() -> None:
    secret_subject = "private invoice subject"
    secret_body = "private invoice body"
    server, requests = make_server(
        lambda request: httpx.Response(
            500,
            json={
                "errorCode": "DELIVERY_FAILED",
                "errorMessage": "the private message must not leak",
                "context": {"emailSubject": secret_subject, "emailBody": secret_body},
            },
        )
    )
    preview = call_tool(server, "api_invoices_send_email_preview", email_arguments())

    error = call_tool(
        server,
        "api_invoices_send_email_execute",
        {"confirmation_ticket": preview["confirmation_ticket"]},
    )

    serialised = json.dumps(error)
    assert error["code"] == StableErrorCode.BILLY_ERROR
    assert secret_subject not in serialised
    assert secret_body not in serialised
    details = cast(dict[str, object], error["details"])
    upstream = cast(dict[str, object], details["upstream"])
    assert upstream["context"] == {
        "emailSubject": REDACTED,
        "emailBody": REDACTED,
    }
    assert len(requests) == 1


@pytest.mark.parametrize(
    ("preview_name", "execute_name", "arguments", "response"),
    [
        (
            "api_invoices_send_email_preview",
            "api_invoices_send_email_execute",
            email_arguments(),
            {"errorCode": "TEMPORARY"},
        ),
        (
            "api_invoice_deliveries_create_preview",
            "api_invoice_deliveries_create_execute",
            delivery_arguments(),
            {"errorCode": "TEMPORARY"},
        ),
    ],
)
def test_external_send_uses_locked_base_url_and_is_never_retried(
    preview_name: str,
    execute_name: str,
    arguments: dict[str, object],
    response: dict[str, object],
) -> None:
    server, requests = make_server(lambda request: httpx.Response(503, json=response))
    preview = call_tool(server, preview_name, arguments)

    error = call_tool(server, execute_name, {"confirmation_ticket": preview["confirmation_ticket"]})

    assert error["code"] == StableErrorCode.BILLY_ERROR
    assert len(requests) == 1
    assert str(requests[0].url).startswith("https://api.billysbilling.com/v2/")


def test_missing_token_returns_typed_auth_error_without_network_activity() -> None:
    server, requests = make_server(
        lambda request: pytest.fail(f"missing token attempted HTTP request: {request.url}"),
        token="",
    )
    preview = call_tool(server, "api_invoice_deliveries_create_preview", delivery_arguments())

    error = call_tool(
        server,
        "api_invoice_deliveries_create_execute",
        {"confirmation_ticket": preview["confirmation_ticket"]},
    )

    assert error["code"] == StableErrorCode.AUTH_REQUIRED
    assert requests == []
