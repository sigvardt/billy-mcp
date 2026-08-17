"""Offline FastMCP ticket contract for UI invoice draft writes."""

from __future__ import annotations

import asyncio
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Literal, cast

import pytest
from fastmcp import FastMCP
from pydantic import JsonValue, ValidationError

from billy_mcp.confirmations import MAX_TICKET_TTL, ConfirmationBinding, ConfirmationStore
from billy_mcp.models import StableErrorCode
from billy_mcp.ui_writes.invoices import (
    CREATE_EXECUTE,
    DRAFT_DELETE_CTA,
    DRAFT_SAVE_CTA,
    InvoiceCreatePreviewInput,
    InvoiceDeletePreviewInput,
    InvoiceUpdatePreviewInput,
    UiInvoiceExecuteResult,
    invoice_family_write,
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


def test_fill_named_contact_is_not_a_kunde_bind() -> None:
    """Given the invoice form helper, When creating, Then generic contact fill is gone."""

    form = Path("src/billy_mcp/ui_writes/invoices_form.py").read_text(encoding="utf-8")
    bind = Path("src/billy_mcp/ui_writes/invoices_form_bind.py").read_text(encoding="utf-8")
    assert "_fill_named" not in form
    assert "_fill_named" not in bind
    assert "bind_kunde" in form
    assert "input[name='contact']" in bind


def _create_prepared() -> UiWritePrepared:
    request: dict[str, JsonValue] = {
        "action": "draft_create",
        "save_cta": DRAFT_SAVE_CTA,
        "contact_name": "MCP-UI-INV-x",
        "line_description": "MCP-UI-INV-x line",
    }
    return UiWritePrepared(
        binding=ConfirmationBinding(
            tool="ui_invoices_create_execute",
            organization_id="org-test",
            target="invoices",
            request=request,
            expected_effect_state={"action": "create"},
        ),
        canonical_request=request,
        expected_effect_state={"action": "create", "save_cta": DRAFT_SAVE_CTA},
        summary="Create one Billy invoice draft in the interface.",
    )


def test_invoice_create_does_not_fill_generic_contact() -> None:
    """Given a draft create ticket, When mapping the write, Then contact is not a name fill."""

    write = invoice_family_write(_create_prepared(), "create")

    assert all(field_name != "contact" for field_name, _ in write.fills)


def test_kunde_existing_option_beats_create_footer() -> None:
    """Given an exact Kunde option and a create footer, When picking, Then existing wins."""

    from billy_mcp.ui_writes.invoices_kunde import (
        pick_kunde_create_index,
        pick_kunde_existing_option_index,
        portal_list_item_flags,
    )

    tag = "MCP-UI-INV-x"
    items = [
        portal_list_item_flags("hidden", tag),
        portal_list_item_flags(tag, tag),
        portal_list_item_flags(f'Ingen resultater\n\nOpret "{tag}"', tag),
    ]
    items[0]["visible"] = False
    items[1]["has_empty"] = False
    items[1]["has_create_footer"] = True
    items[1]["has_opret"] = True

    assert pick_kunde_existing_option_index(items) == 1
    assert pick_kunde_create_index(items) == 2
    assert pick_kunde_existing_option_index(items) != pick_kunde_create_index(items)


def test_kunde_field_prefers_wrapper_input() -> None:
    """Given the bind helper, Then it looks inside the Kunde input-wrapper first."""

    source = Path("src/billy_mcp/ui_writes/invoices_form_bind.py").read_text(encoding="utf-8")
    observe = Path("src/billy_mcp/ui_writes/invoices_form_observe.py").read_text(encoding="utf-8")
    assert "[data-testid='input-wrapper']" in source
    assert "input[name='contact']" in source
    assert "dump_kunde_phases" in observe
    assert "after_type" in observe


def test_kunde_bind_scopes_search_to_contact_wrapper() -> None:
    """Given live contact chrome, When binding Kunde, Then search is wrapper-scoped."""

    source = Path("src/billy_mcp/ui_writes/invoices_form_bind.py").read_text(encoding="utf-8")
    observe_path = Path("src/billy_mcp/ui_writes/invoices_form_observe.py")
    observe = observe_path.read_text(encoding="utf-8") if observe_path.is_file() else ""
    combined = f"{source}\n{observe}"
    assert "input[name='contact']" in source
    assert "filter(" in source
    assert "[data-testid='search']" in source
    assert "after_click" in combined
    assert "search_trigger" in combined
    assert "page.get_by_text(unique_tag" not in source


def test_live_invoice_writes_is_not_a_contacts_slot_stub() -> None:
    """Given the live invoice writes file, Then it drives FastMCP CUD, not the old hold."""

    source = Path("tests/live/test_ui_invoices_writes.py").read_text(encoding="utf-8")
    assert "30D194C8" not in source
    assert "test_ui_invoices_create_update_delete_via_call_tool" in source
    assert "create_server" in source
    assert "ui_invoices_create_preview" in source
    assert "ui_clients_create_preview" in source
    assert "Godkend" in source
    assert "pending_review" in source
