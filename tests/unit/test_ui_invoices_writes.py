"""Offline FastMCP ticket contract for UI invoice draft writes."""

from __future__ import annotations

import asyncio
import json
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Literal, cast

import pytest
from fastmcp import FastMCP
from fastmcp.exceptions import ValidationError as FastMcpValidationError
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
        "product_name": "MCP-UI-PRD-acme",
        "unit_price": 1.0,
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
            "product_name",
            "unit_price",
            "action",
            "save_cta",
            "organization_id",
        },
        "ui_invoices_create_execute": {"confirmation_ticket"},
        "ui_invoices_update_preview": {
            "contact_name",
            "id",
            "line_description",
            "unit_price",
            "action",
            "save_cta",
            "organization_id",
        },
        "ui_invoices_update_execute": {"confirmation_ticket"},
        "ui_invoices_delete_preview": {
            "contact_name",
            "id",
            "action",
            "save_cta",
            "organization_id",
        },
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
                "contact_name": "MCP-UI-INV-acme",
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
                "contact_name": "MCP-UI-INV-acme",
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
                "contact_name": "",
                "id": "inv-1",
                "line_description": "line",
                "action": "draft_update",
                "save_cta": DRAFT_SAVE_CTA,
            },
        ),
        (
            InvoiceDeletePreviewInput,
            {
                "contact_name": "",
                "id": "inv-1",
                "action": "draft_delete",
                "save_cta": DRAFT_DELETE_CTA,
            },
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


def test_create_preview_rejects_unpriced_line() -> None:
    """Owner 1F1B34F8: draft create must reject a missing or non-positive unit price."""

    server, recorder, _ = make_server()

    unpriced = _create_args()
    del unpriced["unit_price"]
    with pytest.raises(ValidationError):
        InvoiceCreatePreviewInput.model_validate(unpriced)
    with pytest.raises(ValidationError):
        InvoiceCreatePreviewInput.model_validate(_create_args(unit_price=0))
    with pytest.raises(ValidationError):
        InvoiceCreatePreviewInput.model_validate(_create_args(unit_price=-1))
    with pytest.raises(ValidationError):
        InvoiceUpdatePreviewInput.model_validate(
            {
                "contact_name": "MCP-UI-INV-acme",
                "id": "inv-1",
                "line_description": "line",
                "action": "draft_update",
                "save_cta": DRAFT_SAVE_CTA,
                "organization_id": "org-test",
                "unit_price": 0,
            }
        )

    try:
        missing = call_tool(server, "ui_invoices_create_preview", unpriced)
    except (ValidationError, FastMcpValidationError, TypeError, ValueError):
        missing = {"code": StableErrorCode.VALIDATION_ERROR}
    assert missing.get("code") == StableErrorCode.VALIDATION_ERROR
    assert recorder.submissions == []
    assert not missing.get("confirmation_ticket")


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
        "product_name": "MCP-UI-PRD-acme",
        "unit_price": 1.0,
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
                "contact_name": "MCP-UI-INV-acme",
                "id": "inv-1",
                "line_description": "line",
                "unit_price": 1.0,
                "action": "send",
                "save_cta": "Godkend og send",
                "organization_id": "org-test",
            },
        ),
        (
            "ui_invoices_delete_preview",
            {
                "contact_name": "MCP-UI-INV-acme",
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
            "contact_name": "MCP-UI-INV-acme",
            "id": "inv-1",
            "line_description": "MCP-UI-INV line",
            "unit_price": 1.0,
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
            "contact_name": "MCP-UI-INV-acme",
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


def test_bind_kunde_picks_existing_option_from_vaelg_kunde() -> None:
    """Owner EC676F84: open Vælg kunde and pick the existing customer. No Opret ny."""

    bind = Path("src/billy_mcp/ui_writes/invoices_form_bind.py").read_text(encoding="utf-8")
    start = bind.index("async def bind_kunde")
    helper = bind.index("async def _vaelg_kunde_textbox")
    end = bind.index("\nasync def ", helper + 1)
    body = bind[start:end]
    assert "Vælg kunde" in body
    assert "_vaelg_kunde_textbox" in body
    assert "_click_scoped_option" in body
    assert "_click_scoped_footer" not in body
    assert "portal_create_footer" not in body
    option_idx = body.index("_click_scoped_option")
    type_idx = body.index("_type_kunde")
    assert option_idx < type_idx


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
    """Given live contact chrome, When binding Kunde, Then pick existing option only."""

    source = Path("src/billy_mcp/ui_writes/invoices_form_bind.py").read_text(encoding="utf-8")
    assert "input[name='contact']" in source
    assert "Vælg kunde" in source
    assert "[data-testid='input-wrapper']" in source
    assert "filter(" in source
    assert "_click_scoped_option" in source
    assert "async def _click_scoped_footer" not in source


def test_live_invoice_writes_is_not_a_contacts_slot_stub() -> None:
    """Given the live invoice writes file, Then it drives FastMCP CUD, not the old hold."""

    source = Path("tests/live/test_ui_invoices_writes.py").read_text(encoding="utf-8")
    assert "30D194C8" not in source
    assert "test_ui_invoices_create_update_delete_via_call_tool" in source
    assert "create_server" in source
    assert "ui_invoices_update_preview" in source
    assert "LEFTOVER_INVOICE_CONTACTS" in source
    assert "Godkend" in source
    assert "pending_review" in source


def test_live_invoice_cud_confirms_customer_before_invoice_preview() -> None:
    """Owner 59A3A933: leftover list row is proved before FastMCP update."""

    source = Path("tests/live/test_ui_invoices_writes.py").read_text(encoding="utf-8")
    start = source.index("async def test_ui_invoices_create_update_delete_via_call_tool")
    end = source.index("\nasync def ", start + 1)
    body = source[start:end]
    list_idx = body.index('await _list_has_name(observer, slug, "invoices", UPDATE_CONTACT')
    update_idx = body.index("ui_invoices_update_preview")
    assert list_idx < update_idx
    assert "asyncio.sleep(2)" not in body[list_idx:update_idx]
    assert "leftover draft" in body


def test_priced_line_fill_uses_enhedspris_label() -> None:
    """Owner 1F1B34F8: fill Enhedspris after bind. Never Opret ny product."""

    bind = Path("src/billy_mcp/ui_writes/invoices_form_bind.py").read_text(encoding="utf-8")
    form = Path("src/billy_mcp/ui_writes/invoices_form.py").read_text(encoding="utf-8")
    assert "async def fill_priced_line" in bind
    assert "Enhedspris" in bind
    assert "Antal" in bind
    assert "Vælg produkt" in bind
    start = bind.index("async def fill_priced_line")
    assert "Opret ny" in bind[start:]
    assert "fill_priced_line" in form
    create = form[form.index("async def _create_draft") : form.index("async def _update_draft")]
    assert "fill_priced_line" in create
    assert "unit_price" in create


def test_invoice_create_opens_new_page_before_bind() -> None:
    """Owner 9310BC17 / 32662804: never reuse the bootstrap page for draft writes."""

    form = Path("src/billy_mcp/ui_writes/invoices_form.py").read_text(encoding="utf-8")
    start = form.index("async def submit_draft_invoice")
    create = form.index("async def _create_draft")
    submit = form[start:create]
    body = form[create : form.index("async def _update_draft")]
    slug_idx = submit.index("slug != bound")
    run_idx = submit.index("_run_action")
    chunk = submit[slug_idx:run_idx]
    assert "new_page" in chunk
    assert "page.close" in chunk
    assert 'if action == "create":' not in chunk
    assert "bind_kunde" in body
    assert "invoices/new" in body


def test_invoice_create_readback_uses_contact_tag() -> None:
    """Invoice list shows the customer tag, not Evt. beskrivelse."""

    form = Path("src/billy_mcp/ui_writes/invoices_form.py").read_text(encoding="utf-8")
    start = form.index("marker =")
    chunk = form[start : start + 80]
    assert "unique_tag" in chunk
    assert "allow_search=False" in form
    assert "visible_body=True" in form
    assert "line_description if action" not in form


def test_create_preview_rejects_missing_product_name() -> None:
    """Official invoiceLines.product is required. Create preview must name it."""

    server, recorder, _ = make_server()

    missing = _create_args()
    del missing["product_name"]
    with pytest.raises(ValidationError):
        InvoiceCreatePreviewInput.model_validate(missing)
    with pytest.raises(ValidationError):
        InvoiceCreatePreviewInput.model_validate(_create_args(product_name=""))
    try:
        preview = call_tool(server, "ui_invoices_create_preview", missing)
    except (ValidationError, FastMcpValidationError, TypeError, ValueError):
        preview = {"code": StableErrorCode.VALIDATION_ERROR}
    assert preview.get("code") == StableErrorCode.VALIDATION_ERROR
    assert recorder.submissions == []
    assert not preview.get("confirmation_ticket")


def test_bind_existing_product_requires_exact_tag() -> None:
    """Missing Vælg produkt or a first-option pick is not a bind."""

    bind = Path("src/billy_mcp/ui_writes/invoices_form_bind.py").read_text(encoding="utf-8")
    start = bind.index("async def _bind_existing_product")
    body = bind[start:]
    assert "product_name" in body
    assert "return None" not in body.split("async def ", 1)[0]
    assert "first" not in body or "Opret ny" in body
    assert "exact" in body or "unique_tag" in body or "product_name" in body
    assert body.split("return ", 1)[0]
    assert "UI_CHANGED" in body
    assert "Opret ny" in body
    assert "options.nth" not in body


def test_live_invoice_cud_seeds_product_before_preview() -> None:
    """Leftover sweep names owner tags and updates before delete."""

    source = Path("tests/live/test_ui_invoices_writes.py").read_text(encoding="utf-8")
    start = source.index("async def test_ui_invoices_create_update_delete_via_call_tool")
    end = source.index("\nasync def ", start + 1)
    body = source[start:end]
    assert "UPDATE_CONTACT" in body
    update = body.index("ui_invoices_update_preview")
    delete = body.index("ui_invoices_delete_preview")
    product_delete = body.index("ui_products_delete_preview")
    assert update < delete < product_delete
    assert "contact_name" in body[update : update + 400]
    assert "_row_enhedspris" in body
    assert "price_is(shown, 2.0)" in body
    assert body.index("_row_enhedspris") < delete
    assert "for leftover_id in await _invoice_ids" not in body


def test_bind_kunde_clicks_chevron_before_type() -> None:
    """Owner 9310BC17: open the chevron, then pick the exact tag. Type is fallback."""

    bind = Path("src/billy_mcp/ui_writes/invoices_form_bind.py").read_text(encoding="utf-8")
    start = bind.index("async def bind_kunde")
    helper_at = bind.index("async def _click_kunde_chevron")
    end = bind.index("async def _vaelg_kunde_textbox")
    body = bind[start:helper_at]
    helper = bind[helper_at:end]
    assert "_click_kunde_chevron" in body
    assert "chevron_offset_from_box" in helper
    assert "dropdown-icon" in helper
    assert "len(visible) != 1" in bind
    assert "_click_scoped_option" in body
    assert body.index("_click_kunde_chevron") < body.index("_type_kunde")
    assert body.index("_click_scoped_option") < body.index("_type_kunde")
    assert "_click_scoped_footer" not in body


def _live_unbound_after_type() -> dict[str, object]:
    return {
        "phase": "after_type",
        "field_name": "contact",
        "field_role": None,
        "aria_expanded": None,
        "value_len": 19,
        "tag_len": 19,
        "search_trigger": False,
        "clear_trigger": False,
        "trigger_count": 0,
        "page_search_count": 0,
        "wrapper_count": 0,
        "alt_list_count": 0,
        "existing_index": None,
        "create_index": None,
        "option_role_count": 0,
        "items": [
            {
                "has_opret": False,
                "has_tag": False,
                "has_empty": False,
                "has_create_footer": False,
                "visible": False,
                "short": True,
            },
            {
                "has_opret": False,
                "has_tag": False,
                "has_empty": False,
                "has_create_footer": False,
                "visible": False,
                "short": True,
            },
        ],
    }


def _live_dummy_after_type() -> dict[str, object]:
    """Current owner dump after_type: 15-char dummy, not MCP-UI-INV- + 8 hex."""

    payload = _live_unbound_after_type()
    payload["value_len"] = 15
    payload["tag_len"] = 15
    return payload


def test_typed_contact_dump_is_not_a_kunde_bind() -> None:
    """Given the live after-type dump, When judging bind, Then typed contact is unbound."""

    from billy_mcp.ui_writes.invoices_kunde import kunde_phase_is_bound, named_kunde_opener

    assert kunde_phase_is_bound(_live_unbound_after_type()) is False
    assert (
        named_kunde_opener(
            {
                "sibling_search": False,
                "uncle_search": False,
                "combobox_count": 0,
                "contact_id_count": 0,
                "placeholder_present": True,
                "field_name": "contact",
            }
        )
        is None
    )


def test_dummy_15_char_after_type_is_not_existing_customer_observation() -> None:
    """Given the 15-char dummy dump, When judging observation, Then it is not existing-customer."""

    from billy_mcp.ui_writes.invoices_kunde import (
        after_type_is_existing_customer_observation,
        kunde_phase_is_bound,
    )

    dummy = _live_dummy_after_type()
    existing_tag = "MCP-UI-INV-DEADBEEF"
    assert len(existing_tag) == 19
    assert dummy["tag_len"] == 15
    assert kunde_phase_is_bound(dummy) is False
    assert after_type_is_existing_customer_observation(dummy, existing_tag) is False
    assert after_type_is_existing_customer_observation(dummy, "short-dummy-15x") is False
    matched = dict(dummy)
    matched["value_len"] = 19
    matched["tag_len"] = 19
    assert after_type_is_existing_customer_observation(matched, existing_tag) is True
    assert kunde_phase_is_bound(matched) is False


def test_bind_does_not_press_extra_keys_on_unbound_contact() -> None:
    """Given the live dump, When binding, Then extra keys on contact are gone."""

    source = Path("src/billy_mcp/ui_writes/invoices_form_bind.py").read_text(encoding="utf-8")
    assert "Alt+ArrowDown" not in source
    assert 'press("Enter")' not in source
    assert "_click_field_once" in source


def test_opener_dump_writes_to_tmp_not_owner_file(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Given a unit opener dump, When writing, Then the owner kunde file is untouched."""

    from billy_mcp.ui_writes import invoices_form_observe

    owner = tmp_path / "inspect-live-invoices-kunde.json"
    opener = tmp_path / "inspect-live-invoices-kunde-opener.json"
    monkeypatch.setattr(invoices_form_observe, "KUNDE_CHROME_DUMP", owner)
    monkeypatch.setattr(invoices_form_observe, "KUNDE_OPENER_DUMP", opener)
    payload = {
        "parent_testid": "input-wrapper",
        "parent_class_tokens": ["ds-input"],
        "sibling_search": False,
        "uncle_search": False,
        "kunde_label_count": 1,
        "contact_id_count": 0,
        "combobox_count": 0,
        "placeholder_present": False,
        "named_opener": None,
    }
    invoices_form_observe.dump_kunde_opener(payload)
    assert opener.is_file()
    assert not owner.exists()
    written = opener.read_text(encoding="utf-8")
    assert "parent_testid" in written
    assert "named_opener" in written
    assert "MCP-UI-INV" not in written


def test_placeholder_flags_are_non_pii() -> None:
    """Given a placeholder string, When flagging, Then raw text is not stored."""

    from billy_mcp.ui_writes.invoices_kunde import named_kunde_opener, placeholder_flags

    flags = placeholder_flags("Vælg kunde")
    assert flags["has_kunde"] is True
    assert flags["has_vaelg"] is True
    assert flags["has_soeg"] is False
    assert "Vælg" not in str(flags)
    assert (
        named_kunde_opener(
            {
                "sibling_search": False,
                "uncle_search": False,
                "combobox_count": 0,
                "contact_id_count": 0,
                "power_select_trigger_count": 0,
                "placeholder_present": True,
                "placeholder_flags": flags,
            }
        )
        is None
    )
    assert named_kunde_opener({"power_select_trigger_count": 1}) == "power_select_trigger"


def test_opener_observe_records_ancestors_and_placeholder_flags() -> None:
    """Given the opener helper, Then it records ancestors and placeholder flags."""

    source = Path("src/billy_mcp/ui_writes/invoices_form_observe.py").read_text(encoding="utf-8")
    assert "ancestor_class_tokens" in source
    assert "placeholder_flags" in source
    assert "power_select_trigger_count" in source
    assert "ember-power-select-trigger" in source


def _live_opener_payload() -> dict[str, object]:
    """Pre-ownership live opener dump. Named opener is still null after recapture."""

    return {
        "parent_testid": None,
        "parent_class_tokens": ["ember-view"],
        "ancestor_class_tokens": [["ember-view"], [], []],
        "sibling_search": False,
        "uncle_search": False,
        "sibling_caret": False,
        "uncle_caret": False,
        "kunde_label_count": 0,
        "contact_id_count": 0,
        "combobox_count": 0,
        "power_select_trigger_count": 0,
        "placeholder_present": True,
        "placeholder_flags": {
            "has_kunde": True,
            "has_customer": False,
            "has_vaelg": True,
            "has_soeg": False,
            "has_select": False,
        },
        "field_name": "contact",
        "named_opener": None,
    }


def test_live_opener_payload_missing_5e1edfb4_keys() -> None:
    """Given the live opener dump, When checking keys, Then 5E1EDFB4 fields are missing."""

    from billy_mcp.ui_writes.invoices_form_observe import empty_ownership
    from billy_mcp.ui_writes.invoices_kunde import (
        REQUIRED_OPENER_DUMP_KEYS,
        named_kunde_opener,
        opener_dump_missing_keys,
    )

    payload = _live_opener_payload()
    assert opener_dump_missing_keys(payload) == list(REQUIRED_OPENER_DUMP_KEYS)
    assert named_kunde_opener(payload) is None
    complete = {**payload, **empty_ownership()}
    assert opener_dump_missing_keys(complete) == []
    assert named_kunde_opener(complete) is None


def test_opener_observe_records_5e1edfb4_ownership_keys() -> None:
    """Given the opener helper, Then it walks owners to FORM and records hit target."""

    source = Path("src/billy_mcp/ui_writes/invoices_form_observe.py").read_text(encoding="utf-8")
    assert "owners" in source
    assert "elementFromPoint" in source
    assert 'tag === "FORM"' in source
    assert "pointer_events" in source
    assert "missing_keys" in source


def _live_widget_payload() -> dict[str, object]:
    """Current live opener input plus after_type keys. Widget contract is absent."""

    payload = _live_opener_payload()
    payload["input"] = {
        "tag": "INPUT",
        "type": "text",
        "has_id": True,
        "has_autocomplete": True,
        "disabled": False,
        "readonly": False,
        "aria_names": [],
    }
    payload.update(_live_unbound_after_type())
    return payload


def test_live_dumps_miss_51e18e60_widget_contract_keys() -> None:
    """Given current live dumps, When checking widget keys, Then 51E18E60 fields are missing."""

    from billy_mcp.ui_writes.invoices_kunde import (
        REQUIRED_WIDGET_CONTRACT_KEYS,
        widget_contract_missing_keys,
    )

    payload = _live_widget_payload()
    assert widget_contract_missing_keys(payload) == list(REQUIRED_WIDGET_CONTRACT_KEYS)
    live_input = payload["input"]
    assert isinstance(live_input, dict)
    assert "autocomplete_token" not in live_input
    assert "list_present" not in live_input
    assert "datalist_count" not in payload
    assert "field_shot" not in payload


def test_complete_widget_contract_has_no_missing_keys() -> None:
    """Given a filled widget dump, When checking keys, Then none are missing."""

    from billy_mcp.ui_writes.invoices_kunde import (
        autocomplete_token,
        empty_widget_contract,
        widget_contract_missing_keys,
        widget_named_action,
    )

    payload = _live_widget_payload()
    payload.update(empty_widget_contract())
    live_input = payload["input"]
    assert isinstance(live_input, dict)
    input_map: dict[str, object] = dict(cast(dict[str, object], live_input))
    input_map["autocomplete_token"] = autocomplete_token("off")
    input_map["list_present"] = False
    payload["input"] = input_map
    assert widget_contract_missing_keys(payload) == []
    assert autocomplete_token("") == "empty"
    assert autocomplete_token("OFF") == "off"
    assert autocomplete_token("section-name") == "other"
    assert widget_named_action(payload) is None
    payload["datalist_option_count"] = 2
    assert widget_named_action(payload) == "datalist_option"


def test_observe_records_51e18e60_widget_contract_keys() -> None:
    """Given the observe helper, Then it records the widget-contract keys."""

    source = Path("src/billy_mcp/ui_writes/invoices_form_observe.py").read_text(encoding="utf-8")
    assert "autocomplete_token" in source
    assert "list_present" in source
    assert "datalist_count" in source
    assert "visible_input_count" in source
    assert "a11y_snapshot" in source
    assert "field_shot" in source
    assert "GET /v2/contacts" in source


def _live_chevron_payload() -> dict[str, object]:
    """Current live opener plus after_click. A3AB03C3 right-edge keys are absent."""

    payload = _live_widget_payload()
    payload["phase"] = "after_click"
    payload["value_len"] = 0
    payload["element_from_point"] = {
        "tag": "INPUT",
        "class_tokens": ["ember-text-field", "ember-view"],
        "name": "contact",
        "testid": None,
    }
    payload["box"] = {"x": 65, "y": 121, "w": 250, "h": 40}
    return payload


def test_live_dumps_miss_a3ab03c3_chevron_hit_keys() -> None:
    """Given current live dumps, When checking chevron keys, Then A3AB03C3 fields are missing."""

    from billy_mcp.ui_writes.invoices_kunde import (
        REQUIRED_CHEVRON_HIT_KEYS,
        chevron_hit_missing_keys,
    )

    payload = _live_chevron_payload()
    assert chevron_hit_missing_keys(payload) == list(REQUIRED_CHEVRON_HIT_KEYS)
    assert "right_edge_offset" not in payload
    assert "right_edge_element_from_point" not in payload
    assert "right_edge_same_input" not in payload
    assert "appearance_token" not in payload
    assert "background_image_kind" not in payload
    assert "before_content_kind" not in payload
    assert "after_content_kind" not in payload
    assert "input_child_count" not in payload


def test_complete_chevron_hit_has_no_missing_keys() -> None:
    """Given a filled chevron dump, When checking keys, Then none are missing."""

    from billy_mcp.ui_writes.invoices_kunde import (
        appearance_token,
        background_image_kind,
        chevron_hit_missing_keys,
        chevron_offset_from_box,
        empty_chevron_hit,
        pseudo_content_kind,
        right_edge_click_offset,
        right_edge_is_proved_input,
    )

    payload = _live_chevron_payload()
    payload.update(empty_chevron_hit())
    payload["right_edge_offset"] = chevron_offset_from_box(250, 40)
    payload["right_edge_element_from_point"] = {
        "tag": "INPUT",
        "class_tokens": ["ember-text-field"],
        "name": "contact",
        "testid": None,
    }
    payload["right_edge_same_input"] = True
    payload["appearance_token"] = appearance_token("textfield")
    payload["background_image_kind"] = background_image_kind("none")
    payload["before_content_kind"] = pseudo_content_kind("none")
    payload["after_content_kind"] = pseudo_content_kind('""')
    payload["input_child_count"] = 0
    assert chevron_hit_missing_keys(payload) == []
    assert appearance_token("") == "none"
    assert appearance_token("AUTO") == "auto"
    assert appearance_token("menulist") == "other"
    assert background_image_kind("url(https://example.invalid/x.png)") == "url"
    assert background_image_kind("linear-gradient(red, blue)") == "gradient"
    assert pseudo_content_kind(None) == "none"
    assert right_edge_is_proved_input(payload) is True
    assert right_edge_click_offset(payload) == {"dx": 242, "dy": 20}
    payload["right_edge_same_input"] = False
    assert right_edge_click_offset(payload) is None


def test_observe_records_a3ab03c3_chevron_hit_keys() -> None:
    """Given the observe helper, Then it records the chevron-hit keys."""

    source = Path("src/billy_mcp/ui_writes/invoices_form_observe.py").read_text(encoding="utf-8")
    assert "right_edge_offset" in source
    assert "right_edge_element_from_point" in source
    assert "right_edge_same_input" in source
    assert "appearance_token" in source
    assert "background_image_kind" in source
    assert "before_content_kind" in source
    assert "after_content_kind" in source
    assert "input_child_count" in source
    bind = Path("src/billy_mcp/ui_writes/invoices_form_bind.py").read_text(encoding="utf-8")
    assert 'position={"x": offset["dx"], "y": offset["dy"]}' in bind
    assert "capture_kunde_chevron_hit_dump" in bind


def _live_trace_opener_payload() -> dict[str, object]:
    """Current live opener. 8EFD0EAD trace keys are absent."""

    return _live_chevron_payload()


def _live_trace_after_click_payload() -> dict[str, object]:
    """Current overlay after_click. Has portal counts, not the trace keys."""

    payload = _live_chevron_payload()
    payload["phase"] = "after_click"
    payload["portal_count"] = 2
    payload["option_role_count"] = 0
    payload["value_len"] = 0
    return payload


def test_live_dumps_miss_8efd0ead_trace_keys() -> None:
    """Given current live dumps, When checking trace keys, Then 8EFD0EAD fields are missing."""

    from billy_mcp.ui_writes.invoices_kunde import (
        REQUIRED_KUNDE_TRACE_KEYS,
        kunde_trace_missing_keys,
    )

    opener = _live_trace_opener_payload()
    after_click = _live_trace_after_click_payload()
    opener_missing = kunde_trace_missing_keys(opener)
    click_missing = kunde_trace_missing_keys(after_click)
    assert opener_missing == [
        "listener_attached_before_form",
        "requests",
        "console_categories",
        "portal_inserted",
        "portal_count",
        "active_element",
    ]
    assert set(opener_missing).issubset(REQUIRED_KUNDE_TRACE_KEYS)
    assert "listener_attached_before_form" in click_missing
    assert "requests" in click_missing
    assert "console_categories" in click_missing
    assert "portal_inserted" in click_missing
    assert "active_element" in click_missing
    assert "portal_count" not in click_missing
    assert "option_role_count" not in click_missing
    assert "listener_attached_before_form" not in opener
    assert "requests" not in after_click
    assert "active_element" not in after_click


def test_complete_kunde_trace_has_no_missing_keys() -> None:
    """Given a filled trace dump, When checking keys, Then none are missing."""

    from billy_mcp.ui_writes.invoices_kunde import (
        kunde_trace_missing_keys,
        kunde_trace_names_next_action,
        name_token,
        request_path_class,
        request_url_class,
    )
    from billy_mcp.ui_writes.invoices_kunde_trace import empty_kunde_trace

    payload = _live_trace_after_click_payload()
    payload.update(empty_kunde_trace())
    payload["portal_count"] = 2
    payload["option_role_count"] = 0
    assert kunde_trace_missing_keys(payload) == []
    assert request_path_class("/v2/contacts?q=x") == "contacts"
    assert request_path_class("/v2/invoices") == "invoices"
    assert request_path_class("/v2/products") == "other_v2"
    assert request_path_class("/app/bootstrap") == "other_same_origin"
    assert request_url_class("https://evil.example/v2/contacts") == "denied"
    assert request_url_class("https://api.billysbilling.com/v2/contacts") == "contacts"
    assert name_token("contact") == "contact"
    assert name_token("contactId") == "contactId"
    assert name_token(None) == "empty"
    assert name_token("secret") == "other"
    assert kunde_trace_names_next_action(payload) is False
    payload["requests"] = [
        {"method": "GET", "path_class": "contacts", "status": 200, "timing_ms": 12}
    ]
    assert kunde_trace_names_next_action(payload) is True
    payload["requests"] = []
    payload["portal_inserted"] = True
    assert kunde_trace_names_next_action(payload) is True


def test_observe_records_8efd0ead_trace_keys() -> None:
    """Given the observe helper, Then it records the tagged-flow trace keys."""

    source = Path("src/billy_mcp/ui_writes/invoices_form_observe.py").read_text(encoding="utf-8")
    assert "watch_kunde_trace" in source
    assert "listener_attached_before_form" in source
    assert "console_categories" in source
    assert "portal_inserted" in source
    bind = Path("src/billy_mcp/ui_writes/invoices_form_bind.py").read_text(encoding="utf-8")
    assert "capture_kunde_tagged_trace" in bind
    assert "watch_kunde_trace" in bind


def _live_event_phase_payload(*, value_len: int) -> dict[str, object]:
    """Current live tagged-trace phase flags. 4A5CD1E7 event keys are absent."""

    payload = _live_trace_after_click_payload()
    payload["listener_attached_before_form"] = True
    payload["console_categories"] = {"script": 23, "pageerror": 1, "other": 8}
    payload["portal_inserted"] = False
    payload["value_len"] = value_len
    payload["active_element"] = {
        "tag": "INPUT",
        "name_token": "contact",
        "aria_expanded_present": False,
    }
    return payload


def test_live_dumps_miss_4a5cd1e7_event_keys() -> None:
    """Given current live dumps, When checking event keys, Then 4A5CD1E7 fields are missing."""

    from billy_mcp.ui_writes.invoices_kunde import (
        REQUIRED_KUNDE_EVENT_KEYS,
        kunde_event_missing_keys,
    )

    at_rest = _live_event_phase_payload(value_len=0)
    after_click = _live_event_phase_payload(value_len=0)
    after_type = _live_event_phase_payload(value_len=19)
    expected = [
        "event_counts",
        "console_delta",
        "errors",
        "pageerror_unrelated_at_rest",
    ]
    assert kunde_event_missing_keys(at_rest) == expected
    assert kunde_event_missing_keys(after_click) == expected
    assert kunde_event_missing_keys(after_type) == expected
    assert set(expected).issubset(REQUIRED_KUNDE_EVENT_KEYS)
    assert "event_counts" not in at_rest
    assert "console_delta" not in after_click
    assert "errors" not in after_type
    assert "pageerror_unrelated_at_rest" not in after_type


def test_complete_kunde_event_has_no_missing_keys() -> None:
    """Given a filled event dump, When checking keys, Then none are missing."""

    from billy_mcp.ui_writes.invoices_kunde_events import (
        empty_kunde_event,
        error_class_token,
        event_names_change_gap,
        event_sequence_is_wrong,
        fingerprint_for,
        kunde_event_missing_keys,
        pageerror_unrelated_at_rest,
        source_class_token,
    )

    payload = _live_event_phase_payload(value_len=19)
    payload.update(empty_kunde_event())
    assert kunde_event_missing_keys(payload) == []
    assert error_class_token("TypeError") == "TypeError"
    assert error_class_token("WeirdError") == "other"
    assert source_class_token("https://mit.billy.dk/assets/app.js") == "same_origin"
    assert source_class_token("https://evil.example/x.js") == "unknown"
    digest = fingerprint_for(
        "TypeError",
        "same_origin",
        "Cannot read STR of HEX",
    )
    assert len(digest) == 16
    assert all(char in "0123456789abcdef" for char in digest)
    assert "secret" not in digest
    assert pageerror_unrelated_at_rest(rest_pageerror=1, click_delta=0, type_delta=0)
    assert pageerror_unrelated_at_rest(rest_pageerror=1, click_delta=0, type_delta=1) is False
    assert event_sequence_is_wrong({"keydown": 0, "input": 0}) is True
    assert event_sequence_is_wrong({"keydown": 19, "input": 19}) is False
    assert event_names_change_gap({"input": 19, "change": 0}, contacts=False) is True
    assert event_names_change_gap({"input": 19, "change": 1}, contacts=False) is False
    live_after_type = {
        "focus": 0,
        "input": 19,
        "change": 0,
        "keydown": 19,
        "keyup": 19,
    }
    assert event_names_change_gap(live_after_type, contacts=False) is True


def test_sink_snapshot_phase_is_scoped() -> None:
    """Given console and event totals, When snapshot_phase runs, Then deltas are that phase only."""

    from billy_mcp.ui_writes.invoices_form_observe import KundeTraceSink

    sink = KundeTraceSink()
    sink.note_page_error(RuntimeError("boot https://mit.billy.dk/x HEXDEAD"))
    rest = sink.snapshot_phase(
        "at_rest",
        {"focus": 0, "input": 0, "change": 0, "keydown": 0, "keyup": 0},
    )
    sink.note_console("error", RuntimeError("later"))
    click = sink.snapshot_phase(
        "after_click",
        {"focus": 1, "input": 0, "change": 0, "keydown": 0, "keyup": 0},
    )
    typed = sink.snapshot_phase(
        "after_type",
        {"focus": 1, "input": 19, "change": 0, "keydown": 19, "keyup": 19},
    )
    assert rest["console_delta"] == {"script": 0, "pageerror": 1, "other": 0}
    assert click["console_delta"] == {"script": 1, "pageerror": 0, "other": 0}
    assert typed["event_counts"] == {
        "focus": 0,
        "input": 19,
        "change": 0,
        "keydown": 19,
        "keyup": 19,
    }
    encoded = json.dumps(rest)
    assert '"phase": "at_rest"' in encoded
    assert '"error_class": "other"' in encoded
    assert "HEXDEAD" not in encoded
    assert "https://" not in encoded


def test_observe_records_4a5cd1e7_event_keys() -> None:
    """Given the observe helper, Then it records the event-causality keys."""

    source = Path("src/billy_mcp/ui_writes/invoices_form_observe.py").read_text(encoding="utf-8")
    assert "install_kunde_event_listeners" in source
    assert "snapshot_phase" in source
    assert "attach_kunde_event" in source
    bind = Path("src/billy_mcp/ui_writes/invoices_form_bind.py").read_text(encoding="utf-8")
    assert "capture_kunde_event_trace" in bind
    assert "install_kunde_event_listeners" in bind
    assert "event_names_change_gap" in bind
    assert 'dispatch_event("change")' in bind


def test_trace_sink_keeps_contacts_when_cap_is_full() -> None:
    """Given a full sink, When a contacts row arrives, Then an other row is evicted."""

    from billy_mcp.ui_writes.invoices_form_observe import KundeTraceSink
    from billy_mcp.ui_writes.invoices_kunde_trace import TRACE_REQUEST_CAP

    sink = KundeTraceSink()
    for index in range(TRACE_REQUEST_CAP):
        sink.note_response(
            index,
            "GET",
            "https://mit.billy.dk/assets/app.js",
            200,
        )
    assert len(sink.requests) == TRACE_REQUEST_CAP
    sink.note_response(
        TRACE_REQUEST_CAP + 1,
        "GET",
        "https://api.billysbilling.com/v2/contacts",
        200,
    )
    classes = [row.get("path_class") for row in sink.requests]
    assert "contacts" in classes
    assert len(sink.requests) == TRACE_REQUEST_CAP


def test_update_and_delete_preview_require_contact_name() -> None:
    """Owner 59A3A933: update/delete tickets name the visible list row."""

    server, recorder, _ = make_server()
    missing_update: dict[str, object] = {
        "id": "inv-1",
        "line_description": "line",
        "unit_price": 1.0,
        "action": "draft_update",
        "save_cta": DRAFT_SAVE_CTA,
        "organization_id": "org-test",
    }
    missing_delete: dict[str, object] = {
        "id": "inv-1",
        "action": "draft_delete",
        "save_cta": DRAFT_DELETE_CTA,
        "organization_id": "org-test",
    }
    with pytest.raises(ValidationError):
        InvoiceUpdatePreviewInput.model_validate(missing_update)
    with pytest.raises(ValidationError):
        InvoiceUpdatePreviewInput.model_validate({**missing_update, "contact_name": ""})
    with pytest.raises(ValidationError):
        InvoiceDeletePreviewInput.model_validate(missing_delete)
    with pytest.raises(ValidationError):
        InvoiceDeletePreviewInput.model_validate({**missing_delete, "contact_name": ""})
    try:
        preview = call_tool(server, "ui_invoices_update_preview", missing_update)
    except (ValidationError, FastMcpValidationError, TypeError, ValueError):
        preview = {"code": StableErrorCode.VALIDATION_ERROR}
    assert preview.get("code") == StableErrorCode.VALIDATION_ERROR
    assert recorder.submissions == []
    assert not preview.get("confirmation_ticket")


def test_persist_hit_rejects_put_request_without_status() -> None:
    """Parent DECEA79B: a header PUT /v2/invoices 2xx is not line-price persist."""

    from billy_mcp.ui_writes.invoices_form_page import persist_hit

    assert persist_hit("PUT  https://api.billysbilling.com/v2/invoices/abc", "PUT") is False
    assert persist_hit("PUT 200 https://api.billysbilling.com/v2/invoices/abc", "PUT") is False
    assert persist_hit("PUT 201 https://api.billysbilling.com/v2/invoices/abc", "PUT") is False
    assert persist_hit("PUT 200 https://api.billysbilling.com/v2/invoiceLines/abc", "PUT") is True
    assert persist_hit("PUT 201 https://api.billysbilling.com/v2/invoiceLines/abc", "PUT") is True
    assert persist_hit("PUT 422 https://api.billysbilling.com/v2/invoiceLines/abc", "PUT") is False
    assert (
        persist_hit("PUT 200 https://api.billysbilling.com/v2/invoices/abc/emails", "PUT") is False
    )


def test_invoice_save_hit_accepts_spa_header_put() -> None:
    """Owner 32662804: SPA draft save is PUT /v2/invoices/:id. Fresh Enhedspris is persist."""

    from billy_mcp.ui_writes.invoices_form_page import invoice_save_hit, persist_hit

    assert invoice_save_hit("PUT 200 https://api.billysbilling.com/v2/invoices/abc") is True
    assert persist_hit("PUT 200 https://api.billysbilling.com/v2/invoices/abc", "PUT") is False
    assert invoice_save_hit("PUT 200 https://api.billysbilling.com/v2/invoiceLines/abc") is True
    assert invoice_save_hit("PUT 200 https://api.billysbilling.com/v2/invoices/abc/emails") is False
    assert invoice_save_hit("PUT 422 https://api.billysbilling.com/v2/invoices/abc") is False
    assert persist_hit("POST  https://api.billysbilling.com/v2/invoices", "PUT") is False
    assert persist_hit("POST 200 https://api.billysbilling.com/v2/invoices", "POST") is True


def test_watch_invoice_response_ignores_request_without_status() -> None:
    """A request line with no status must not enter the persist watch list."""

    from billy_mcp.ui_writes.invoices_form_page import watch_invoice_response

    class _Request:
        url = "https://api.billysbilling.com/v2/invoiceLines/abc"
        method = "PUT"
        status = ""
        request = None

    class _Response:
        url = "https://api.billysbilling.com/v2/invoiceLines/abc"
        method = "PUT"
        status = 200
        request = _Request()

    class _HeaderPut:
        url = "https://api.billysbilling.com/v2/invoices/abc"
        method = "PUT"
        status = 200
        request = _Request()

    seen: list[str] = []
    watch_invoice_response(_Request(), seen)
    assert seen == []
    watch_invoice_response(_Response(), seen)
    assert seen == ["PUT 200 https://api.billysbilling.com/v2/invoiceLines/abc"]
    watch_invoice_response(_HeaderPut(), seen)
    assert seen == [
        "PUT 200 https://api.billysbilling.com/v2/invoiceLines/abc",
        "PUT 200 https://api.billysbilling.com/v2/invoices/abc",
    ]


def test_invoice_id_from_payload_reads_first_invoice_id() -> None:
    """Create persist reads invoices.0.id and ignores other JSON shapes."""

    from billy_mcp.ui_writes.invoices_form_page import invoice_id_from_payload

    assert invoice_id_from_payload({"invoices": [{"id": "03dvBZm9QHuYt8jGMM8TNw"}]}) == (
        "03dvBZm9QHuYt8jGMM8TNw"
    )
    assert invoice_id_from_payload({"invoices": []}) is None
    assert invoice_id_from_payload({"invoices": [{"name": "no-id"}]}) is None
    assert invoice_id_from_payload("not-json-object") is None


def test_update_execute_proves_fresh_enhedspris() -> None:
    """Independent update read-back must open the row and read Enhedspris."""

    form = Path("src/billy_mcp/ui_writes/invoices_form.py").read_text(encoding="utf-8")
    submit = form[
        form.index("async def submit_draft_invoice") : form.index("async def _run_action")
    ]
    update = form[form.index("async def _update_draft") :]
    assert "prove_fresh_unit_price" in submit
    assert 'action == "update"' in submit
    assert 'page.on("request"' not in update
    assert 'wait_persist(seen, method="POST")' not in update
    price = Path("src/billy_mcp/ui_writes/invoices_form_price.py").read_text(encoding="utf-8")
    commit = price[
        price.index("async def commit_unit_price") : price.index("async def prove_fresh")
    ]
    assert 'await field.fill("")' not in commit
    assert "danish_price" in commit
    assert "str(int(unit_price))" not in commit
    fill_idx = commit.index("await field.fill(")
    tab_idx = commit.index('await field.press("Tab")')
    assert fill_idx < tab_idx
    assert "await field.input_value()" in commit
    assert commit.index("await field.input_value()") < tab_idx


def test_invoice_delete_captures_post_slet_before_confirm() -> None:
    """Owner 4EAEAFFD: capture post-Slet state. Do not wait for Ja, slet."""

    delete = Path("src/billy_mcp/ui_writes/invoices_form_delete.py").read_text(encoding="utf-8")
    body = delete[delete.index("async def delete_draft_invoice") :]
    assert "_click_unique_mere" in body
    assert "_click_slet" in body
    assert "capture_post_slet" in body
    assert "_click_last_more" not in delete
    assert 'page.on("request"' not in body
    mere_idx = body.index("_click_unique_mere")
    slet_idx = body.index("_click_slet")
    capture_idx = body.index("capture_post_slet")
    assert mere_idx < slet_idx < capture_idx
    before_capture = body[:capture_idx]
    assert "_click_confirm" not in before_capture
    assert "CONFIRM_DELETE" not in before_capture
    assert "Ja, slet" not in before_capture
    assert "xpath=ancestor::a[1]" in delete
    dump_src = "\n".join(
        Path(path).read_text(encoding="utf-8")
        for path in (
            "src/billy_mcp/ui_writes/invoices_form_delete.py",
            "src/billy_mcp/ui_writes/invoices_form_delete_dump.py",
        )
        if Path(path).is_file()
    )
    assert "inspect-live-invoices-post-slet.json" in dump_src
    assert "heading_token" in dump_src
    assert "hit_tag" in dump_src
    assert "delete_seen" in dump_src
    assert "navigated" in dump_src
    assert '"candidates"' in dump_src or "candidates" in dump_src
    for key in ("role", "labels", "geometry", "z_index", "active_contained"):
        assert key in dump_src
    assert "alertdialog" in dump_src
    assert "aria-modal" in dump_src
    assert "button_labels" not in dump_src.split("async def delete_draft_invoice")[-1]


def test_invoice_delete_clicks_ja_slet_faktura_after_capture() -> None:
    """Owner D2FD1919: after the dump, click exact Ja, slet faktura."""

    page = Path("src/billy_mcp/ui_writes/invoices_form_page.py").read_text(encoding="utf-8")
    delete = Path("src/billy_mcp/ui_writes/invoices_form_delete.py").read_text(encoding="utf-8")
    body = delete[delete.index("async def delete_draft_invoice") :]
    after = body[body.index("capture_post_slet") :]
    assert 'CONFIRM_DELETE = "Ja, slet faktura"' in page
    assert "CONFIRM_DELETE" in after
    assert "click_exact" in after
    assert 'wait_persist(seen, method="DELETE")' in after
    assert 'click_exact(page, "Ja, slet")' not in after
    assert 'CONFIRM_DELETE = "Ja, slet"\n' not in page


def test_post_slet_path_and_labels_are_allowlisted() -> None:
    """Post-Slet dump stores tokens, never org slugs or customer text."""

    from billy_mcp.ui_writes.invoices_form_delete import (
        allowlisted_label,
        heading_token,
        path_class_from_url,
    )

    assert path_class_from_url(
        "https://mit.billy.dk/acme/invoices/03dvBZm9QHuYt8jGMM8TNw/edit"
    ) == ("invoices_edit")
    assert path_class_from_url("https://mit.billy.dk/acme/invoices") == "invoices"
    assert path_class_from_url("https://mit.billy.dk/login") == "other"
    assert heading_token("Rediger fakturakladde") == "rediger_fakturakladde"
    assert heading_token("") == "none"
    assert heading_token("MCP-UI-INV-6CDB396B") == "other"
    assert allowlisted_label("Ja, slet") == "ja, slet"
    assert allowlisted_label("Ja, slet faktura") == "ja, slet faktura"
    assert allowlisted_label("Slet") == "slet"
    assert allowlisted_label("MCP-UI-INV-6CDB396B") == "other"


def test_overlay_candidate_parses_scoped_keys() -> None:
    """Owner E8EA9823: each overlay row has role, labels, geometry, z-index."""

    from billy_mcp.ui_writes.invoices_form_delete_dump import OverlayCandidate

    row = OverlayCandidate.model_validate(
        {
            "role": "dialog",
            "labels": ["ja, slet", "annuller"],
            "geometry": {"x": 10, "y": 20, "w": 300, "h": 120},
            "z_index": 40,
            "active_contained": True,
        }
    )
    assert row.role == "dialog"
    assert row.labels == ["ja, slet", "annuller"]
    assert row.geometry.w == 300
    assert row.z_index == 40
    assert row.active_contained is True


def test_price_is_two_accepts_danish_decimals() -> None:
    """Fresh read-back of Enhedspris 2,00 must match ticket unit_price 2."""

    from billy_mcp.ui_writes.invoices_form_bind import price_is
    from billy_mcp.ui_writes.invoices_form_price import danish_price

    assert price_is("2,00", 2.0) is True
    assert price_is("2", 2.0) is True
    assert price_is("1,00", 2.0) is False
    assert price_is("", 2.0) is False
    assert danish_price(2.0) == "2,00"
    assert danish_price(1.0) == "1,00"
    bind = Path("src/billy_mcp/ui_writes/invoices_form_bind.py").read_text(encoding="utf-8")
    start = bind.index("async def unit_price_field")
    end = bind.index("async def _fill_labeled", start)
    body = bind[start:end]
    assert "UNIT_PRICE_SELECTORS" in body
    assert "input[name='unitPrice'][placeholder='Enhedspris']" in bind
    assert "\"input[name='unitPrice']\"" not in bind
    assert "\"input[name*='unitPrice']\"" not in bind
    bind = Path("src/billy_mcp/ui_writes/invoices_form_bind.py").read_text(encoding="utf-8")
    start = bind.index("async def fill_priced_line")
    end = bind.index("\ndef price_is", start)
    fill = bind[start:end]
    assert "commit_unit_price" in fill
    price = Path("src/billy_mcp/ui_writes/invoices_form_price.py").read_text(encoding="utf-8")
    assert "return str(int(unit_price))" not in bind
    assert "str(int(unit_price))" not in price
    assert 'f"{unit_price:.2f}".replace(".", ",")' in price


def test_unit_price_field_binds_exact_enhedspris_input() -> None:
    """Owner F1A2EFC2: only name=unitPrice placeholder=Enhedspris."""

    bind = Path("src/billy_mcp/ui_writes/invoices_form_bind.py").read_text(encoding="utf-8")
    start = bind.index("async def unit_price_field")
    end = bind.index("async def _fill_labeled", start)
    body = bind[start:end]
    assert "input[name='unitPrice'][placeholder='Enhedspris']" in bind
    assert "following::input" not in body
    assert "get_by_label" not in body
    assert "get_by_text" not in body
    assert "get_by_role" not in body
    assert "frames" not in body
    assert "\"input[name='unitPrice']\"" not in bind


def test_commit_unit_price_fills_danish_once_on_bound_locator() -> None:
    """Fill 2,00 once on the bound locator. Do not re-resolve a steal node."""

    price = Path("src/billy_mcp/ui_writes/invoices_form_price.py").read_text(encoding="utf-8")
    commit = price[
        price.index("async def commit_unit_price") : price.index("async def prove_fresh")
    ]
    assert "danish_price(unit_price)" in commit
    assert "str(int(unit_price))" not in commit
    assert "press_sequentially" not in commit
    assert "read_unit_price" not in commit
    assert "await field.fill(" in commit
    assert "await field.input_value()" in commit
    fill_idx = commit.index("await field.fill(")
    read_idx = commit.index("await field.input_value()")
    tab_idx = commit.index('await field.press("Tab")')
    assert fill_idx < read_idx < tab_idx


def test_fill_priced_line_does_not_guess_line_reveal() -> None:
    """Owner 3D5A9B9C: do not click a product tag or guessed row to invent Enhedspris."""

    bind = Path("src/billy_mcp/ui_writes/invoices_form_bind.py").read_text(encoding="utf-8")
    fill = bind[bind.index("async def fill_priced_line") : bind.index("\ndef price_is")]
    assert "reveal_line_editor" not in bind
    assert "_visible_line_product" not in bind
    assert "reveal_line_editor" not in fill
    missing = bind[
        bind.index("async def enhedspris_missing_details") : bind.index(
            "async def unit_price_field"
        )
    ]
    assert '"heading"' in missing
    assert '"exact_count"' in missing
    assert '"product_text_count"' in missing
    assert '"input_count"' in missing


def test_edit_url_opened_rejects_list_and_create() -> None:
    """List /invoices and /invoices/new are not an edit open."""

    from billy_mcp.ui_writes.invoices_form_row import edit_url_opened

    assert edit_url_opened("https://mit.billy.dk/org/invoices") is False
    assert edit_url_opened("https://mit.billy.dk/org/invoices/new") is False
    assert edit_url_opened("https://mit.billy.dk/org/invoices/03dvBZm9QHuYt8jGMM8TNw/edit") is True


def test_update_and_delete_open_list_row() -> None:
    """Owner 59A3A933: open the exact li[role=row]. Do not goto a POST id."""

    form = Path("src/billy_mcp/ui_writes/invoices_form.py").read_text(encoding="utf-8")
    row = Path("src/billy_mcp/ui_writes/invoices_form_row.py")
    helpers = form
    if row.is_file():
        helpers = f"{form}\n{row.read_text(encoding='utf-8')}"
    update = form[form.index("async def _update_draft") :]
    delete = Path("src/billy_mcp/ui_writes/invoices_form_delete.py").read_text(encoding="utf-8")
    assert "li[role=row]" in helpers
    assert "open_invoice_row" in update
    assert "open_invoice_row" in delete
    assert 'f"{BILLY_ORIGIN}/{slug}/invoices/{invoice_id}/edit"' not in update
    assert 'f"{BILLY_ORIGIN}/{slug}/invoices/{invoice_id}/edit"' not in delete


def test_live_leftover_sweep_uses_owner_contact_tags() -> None:
    """Owner 59A3A933: leftover sweep names the six customer tags, not href scrape."""

    source = Path("tests/live/test_ui_invoices_writes.py").read_text(encoding="utf-8")
    start = source.index("async def test_ui_invoices_create_update_delete_via_call_tool")
    end = source.index("\nasync def ", start + 1)
    body = source[start:end]
    for tag in (
        "MCP-UI-INV-6CDB396B",
        "MCP-UI-INV-F1784522",
        "MCP-UI-INV-B05A4C85",
        "MCP-UI-INV-A45B734E",
        "MCP-UI-INV-2B8A4FA2",
        "MCP-UI-INV-DD4158B1",
    ):
        assert tag in source
        assert tag in body or "LEFTOVER_INVOICE_CONTACTS" in source
    assert "contact_name" in body
    assert "for leftover_id in await _invoice_ids" not in body
