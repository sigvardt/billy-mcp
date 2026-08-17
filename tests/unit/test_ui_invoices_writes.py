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
