"""Offline FastMCP ticket contract for UI invoice draft writes."""

from __future__ import annotations

import asyncio
from datetime import UTC, datetime, timedelta
from typing import Literal, cast

import pytest
from fastmcp import FastMCP
from pydantic import ValidationError

from billy_mcp.confirmations import MAX_TICKET_TTL, ConfirmationStore
from billy_mcp.models import StableErrorCode
from billy_mcp.ui_writes.invoices import (
    CREATE_EXECUTE,
    DRAFT_DELETE_CTA,
    DRAFT_SAVE_CTA,
    InvoiceCreatePreviewInput,
    InvoiceDeletePreviewInput,
    InvoiceUpdatePreviewInput,
    UiInvoiceExecuteResult,
    register_ui_invoice_write_tools,
)
from billy_mcp.ui_writes.protocol import UiWriteExecuteInput, UiWritePrepared, UiWriteProtocol


class Clock:
    """Controllable confirmation clock used only by local ticket-expiry tests."""

    def __init__(self) -> None:
        self.now = datetime(2026, 8, 16, tzinfo=UTC)

    def __call__(self) -> datetime:
        return self.now


class RecordingInvoiceSubmitter:
    """Records execute calls. Never talks to Billy HTTP or a browser."""

    def __init__(self) -> None:
        self.submissions: list[UiWritePrepared] = []

    def submit(self, prepared: UiWritePrepared) -> UiInvoiceExecuteResult:
        self.submissions.append(prepared)
        raw_action = prepared.expected_effect_state["action"]
        if raw_action == "create":
            action: Literal["create", "update", "delete"] = "create"
        elif raw_action == "update":
            action = "update"
        elif raw_action == "delete":
            action = "delete"
        else:
            raise AssertionError(f"unexpected action: {raw_action!r}")
        return UiInvoiceExecuteResult(
            action=action,
            save_cta=str(prepared.canonical_request["save_cta"]),
            submitted=True,
            canonical_request=prepared.canonical_request,
            expected_effect_state=prepared.expected_effect_state,
        )


def make_server(
    *,
    clock: Clock | None = None,
) -> tuple[FastMCP, RecordingInvoiceSubmitter, Clock]:
    """Register the invoice family on a local FastMCP with a recording submitter."""

    active_clock = clock or Clock()
    protocol = UiWriteProtocol(ConfirmationStore(clock=active_clock))
    recorder = RecordingInvoiceSubmitter()
    server = FastMCP("ui-invoice-write-contract-test")
    register_ui_invoice_write_tools(server, protocol, submitter=recorder)
    return server, recorder, active_clock


def call_tool(server: FastMCP, tool_name: str, arguments: dict[str, object]) -> dict[str, object]:
    """Call one typed tool with its direct MCP argument object."""

    result = asyncio.run(server.call_tool(tool_name, arguments))
    structured_content = result.structured_content
    assert isinstance(structured_content, dict)
    structured_result = structured_content.get("result", structured_content)
    assert isinstance(structured_result, dict)
    return cast(dict[str, object], structured_result)


def _create_args(**overrides: object) -> dict[str, object]:
    payload: dict[str, object] = {
        "contact_name": "MCP-UI-INV-acme",
        "line_description": "MCP-UI-INV line",
        "action": "draft_create",
        "save_cta": DRAFT_SAVE_CTA,
        "organization_id": "org-test",
    }
    payload.update(overrides)
    return payload


def test_registers_exactly_six_flat_typed_invoice_ui_write_tools() -> None:
    server, _, _ = make_server()
    by_name = {tool.name: tool for tool in asyncio.run(server.list_tools())}

    assert set(by_name) == {
        "ui_invoices_create_preview",
        "ui_invoices_create_execute",
        "ui_invoices_update_preview",
        "ui_invoices_update_execute",
        "ui_invoices_delete_preview",
        "ui_invoices_delete_execute",
    }
    expected_properties = {
        "ui_invoices_create_preview": {
            "contact_name",
            "line_description",
            "action",
            "save_cta",
            "organization_id",
        },
        "ui_invoices_create_execute": {"confirmation_ticket"},
        "ui_invoices_update_preview": {
            "id",
            "line_description",
            "action",
            "save_cta",
            "organization_id",
        },
        "ui_invoices_update_execute": {"confirmation_ticket"},
        "ui_invoices_delete_preview": {"id", "action", "save_cta", "organization_id"},
        "ui_invoices_delete_execute": {"confirmation_ticket"},
    }
    for name, fields in expected_properties.items():
        schema = by_name[name].parameters
        properties = cast(dict[str, object], schema["properties"])
        assert schema["additionalProperties"] is False
        assert set(properties) == fields
        assert "input" not in properties

    for name in (
        "ui_invoices_create_execute",
        "ui_invoices_update_execute",
        "ui_invoices_delete_execute",
    ):
        schema = by_name[name].parameters
        properties = cast(dict[str, dict[str, object]], schema["properties"])
        assert properties["confirmation_ticket"]["minLength"] == 1


@pytest.mark.parametrize(
    ("input_model", "payload"),
    [
        (
            InvoiceCreatePreviewInput,
            {
                "contact_name": "MCP-UI-INV-acme",
                "line_description": "line",
                "action": "draft_create",
                "save_cta": DRAFT_SAVE_CTA,
                "extra": True,
            },
        ),
        (
            InvoiceUpdatePreviewInput,
            {
                "id": "inv-1",
                "line_description": "line",
                "action": "draft_update",
                "save_cta": DRAFT_SAVE_CTA,
                "extra": True,
            },
        ),
        (
            InvoiceDeletePreviewInput,
            {
                "id": "inv-1",
                "action": "draft_delete",
                "save_cta": DRAFT_DELETE_CTA,
                "extra": True,
            },
        ),
        (UiWriteExecuteInput, {"confirmation_ticket": "ticket", "invoice": {}}),
        (
            InvoiceCreatePreviewInput,
            {
                "contact_name": "",
                "line_description": "line",
                "action": "draft_create",
                "save_cta": DRAFT_SAVE_CTA,
            },
        ),
        (
            InvoiceUpdatePreviewInput,
            {
                "id": "",
                "line_description": "line",
                "action": "draft_update",
                "save_cta": DRAFT_SAVE_CTA,
            },
        ),
        (
            InvoiceDeletePreviewInput,
            {"id": "", "action": "draft_delete", "save_cta": DRAFT_DELETE_CTA},
        ),
    ],
)
def test_outer_inputs_forbid_extra_fields_and_empty_ids(
    input_model: type[InvoiceCreatePreviewInput]
    | type[InvoiceUpdatePreviewInput]
    | type[InvoiceDeletePreviewInput]
    | type[UiWriteExecuteInput],
    payload: dict[str, object],
) -> None:
    with pytest.raises(ValidationError):
        input_model.model_validate(payload)


def test_preview_does_not_submit() -> None:
    server, recorder, _ = make_server()

    preview = call_tool(server, "ui_invoices_create_preview", _create_args())

    assert isinstance(preview["confirmation_ticket"], str)
    assert preview["confirmation_ticket"]
    assert preview["canonical_request"] == {
        "action": "draft_create",
        "save_cta": DRAFT_SAVE_CTA,
        "contact_name": "MCP-UI-INV-acme",
        "line_description": "MCP-UI-INV line",
        "organization_id": "org-test",
    }
    assert recorder.submissions == []


def test_create_execute_once_then_replay_is_consumed() -> None:
    server, recorder, _ = make_server()
    preview = call_tool(server, "ui_invoices_create_preview", _create_args())
    ticket = preview["confirmation_ticket"]
    assert isinstance(ticket, str)

    first = call_tool(server, CREATE_EXECUTE, {"confirmation_ticket": ticket})
    replay = call_tool(server, CREATE_EXECUTE, {"confirmation_ticket": ticket})

    assert first["submitted"] is True
    assert first["action"] == "create"
    assert first["save_cta"] == DRAFT_SAVE_CTA
    assert len(recorder.submissions) == 1
    assert replay["code"] == StableErrorCode.CONFIRMATION_CONSUMED
    assert len(recorder.submissions) == 1


def test_expired_ticket_fails_without_submit() -> None:
    clock = Clock()
    server, recorder, _ = make_server(clock=clock)
    preview = call_tool(server, "ui_invoices_create_preview", _create_args())
    ticket = preview["confirmation_ticket"]
    assert isinstance(ticket, str)

    clock.now = clock.now + MAX_TICKET_TTL + timedelta(seconds=1)
    expired = call_tool(server, CREATE_EXECUTE, {"confirmation_ticket": ticket})

    assert expired["code"] == StableErrorCode.CONFIRMATION_EXPIRED
    assert recorder.submissions == []


def test_wrong_tool_mismatch_then_same_ticket_can_expire() -> None:
    clock = Clock()
    server, recorder, _ = make_server(clock=clock)
    preview = call_tool(server, "ui_invoices_create_preview", _create_args())
    ticket = preview["confirmation_ticket"]
    assert isinstance(ticket, str)

    wrong = call_tool(server, "ui_invoices_delete_execute", {"confirmation_ticket": ticket})
    assert wrong["code"] == StableErrorCode.CONFIRMATION_MISMATCH
    assert recorder.submissions == []

    clock.now = clock.now + MAX_TICKET_TTL + timedelta(seconds=1)
    expired = call_tool(server, CREATE_EXECUTE, {"confirmation_ticket": ticket})
    assert expired["code"] == StableErrorCode.CONFIRMATION_EXPIRED
    assert recorder.submissions == []


@pytest.mark.parametrize(
    ("tool_name", "arguments"),
    [
        (
            "ui_invoices_create_preview",
            _create_args(action="send", save_cta="Send"),
        ),
        (
            "ui_invoices_create_preview",
            _create_args(action="godkend", save_cta="Godkend"),
        ),
        (
            "ui_invoices_create_preview",
            _create_args(action="email", save_cta="Send e-mail"),
        ),
        (
            "ui_invoices_update_preview",
            {
                "id": "inv-1",
                "line_description": "line",
                "action": "send",
                "save_cta": "Godkend og send",
                "organization_id": "org-test",
            },
        ),
        (
            "ui_invoices_delete_preview",
            {
                "id": "inv-1",
                "action": "send",
                "save_cta": "Send",
                "organization_id": "org-test",
            },
        ),
    ],
)
def test_send_email_and_approve_preview_fail_closed(
    tool_name: str,
    arguments: dict[str, object],
) -> None:
    server, recorder, _ = make_server()

    result = call_tool(server, tool_name, arguments)

    assert result["code"] == StableErrorCode.VALIDATION_ERROR
    assert recorder.submissions == []


def test_unarmed_default_submitter_consumes_without_clicking() -> None:
    protocol = UiWriteProtocol(ConfirmationStore())
    server = FastMCP("ui-invoice-unarmed-test")
    register_ui_invoice_write_tools(server, protocol)

    preview = call_tool(server, "ui_invoices_create_preview", _create_args())
    result = call_tool(
        server,
        CREATE_EXECUTE,
        {"confirmation_ticket": preview["confirmation_ticket"]},
    )

    assert result["submitted"] is False
    assert result["action"] == "create"
    assert result["save_cta"] == DRAFT_SAVE_CTA


def test_update_and_delete_draft_execute_once() -> None:
    server, recorder, _ = make_server()

    update_preview = call_tool(
        server,
        "ui_invoices_update_preview",
        {
            "id": "inv-1",
            "line_description": "MCP-UI-INV line",
            "action": "draft_update",
            "save_cta": DRAFT_SAVE_CTA,
            "organization_id": "org-test",
        },
    )
    update = call_tool(
        server,
        "ui_invoices_update_execute",
        {"confirmation_ticket": update_preview["confirmation_ticket"]},
    )
    delete_preview = call_tool(
        server,
        "ui_invoices_delete_preview",
        {
            "id": "inv-1",
            "action": "draft_delete",
            "save_cta": DRAFT_DELETE_CTA,
            "organization_id": "org-test",
        },
    )
    delete = call_tool(
        server,
        "ui_invoices_delete_execute",
        {"confirmation_ticket": delete_preview["confirmation_ticket"]},
    )

    assert update["action"] == "update"
    assert delete["action"] == "delete"
    assert len(recorder.submissions) == 2
