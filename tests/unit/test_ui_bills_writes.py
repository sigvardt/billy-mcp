"""FastMCP ticket contract for UI bill preview and execute tools."""

from __future__ import annotations

import json
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import cast

import anyio
import pytest
from fastmcp import FastMCP
from pydantic import ValidationError

from billy_mcp.confirmations import MAX_TICKET_TTL, ConfirmationStore
from billy_mcp.models import StableErrorCode
from billy_mcp.ui_writes.bills import (
    LIVE_SLOT_BLOCKER_MESSAGE,
    BillUiCreatePreviewInput,
    BillUiDeletePreviewInput,
    BillUiUpdatePreviewInput,
    RecordingBillUiSubmitter,
    register_ui_bill_write_tools,
)
from billy_mcp.ui_writes.protocol import UiWriteExecuteInput, UiWriteProtocol


class Clock:
    """Controllable clock for confirmation expiry tests."""

    def __init__(self) -> None:
        self.now = datetime(2026, 8, 16, tzinfo=UTC)

    def __call__(self) -> datetime:
        return self.now


def make_server(
    *,
    clock: Clock | None = None,
    submitter: RecordingBillUiSubmitter | None = None,
) -> tuple[FastMCP, RecordingBillUiSubmitter | None]:
    server = FastMCP("ui-bills-write-contract-test")
    protocol = UiWriteProtocol(ConfirmationStore(clock=clock or Clock()))
    register_ui_bill_write_tools(server, protocol, submitter)
    return server, submitter


def call_tool(server: FastMCP, tool_name: str, arguments: dict[str, str]) -> dict[str, object]:
    result = anyio.run(server.call_tool, tool_name, arguments)
    structured_content = result.structured_content
    assert isinstance(structured_content, dict)
    payload = structured_content.get("result", structured_content)
    assert isinstance(payload, dict)
    return cast(dict[str, object], payload)


def test_registers_exactly_six_flat_typed_ui_bill_write_tools() -> None:
    server, _ = make_server()
    by_name = {tool.name: tool for tool in anyio.run(server.list_tools)}
    expected_properties = {
        "ui_bills_create_preview": {"unique_tag", "organization_id"},
        "ui_bills_create_execute": {"confirmation_ticket"},
        "ui_bills_update_preview": {"id", "unique_tag", "organization_id"},
        "ui_bills_update_execute": {"confirmation_ticket"},
        "ui_bills_delete_preview": {"id", "unique_tag", "organization_id"},
        "ui_bills_delete_execute": {"confirmation_ticket"},
    }
    assert set(by_name) == set(expected_properties)
    for name, fields in expected_properties.items():
        schema = by_name[name].parameters
        properties = cast(dict[str, dict[str, object]], schema["properties"])
        assert schema["additionalProperties"] is False
        assert set(properties) == fields
        assert "input" not in properties
        for field in fields:
            assert properties[field]["minLength"] == 1


@pytest.mark.parametrize(
    ("input_model", "payload"),
    [
        (BillUiCreatePreviewInput, {"unique_tag": "tag-1", "payment": True}),
        (BillUiCreatePreviewInput, {"unique_tag": ""}),
        (BillUiUpdatePreviewInput, {"id": "bill-1", "unique_tag": "tag-1", "approve": True}),
        (BillUiUpdatePreviewInput, {"id": "", "unique_tag": "tag-1"}),
        (BillUiDeletePreviewInput, {"id": "bill-1", "unique_tag": "tag-1", "email": True}),
        (BillUiDeletePreviewInput, {"id": "bill-1", "unique_tag": ""}),
        (UiWriteExecuteInput, {"confirmation_ticket": "ticket", "unique_tag": "x"}),
        (UiWriteExecuteInput, {"confirmation_ticket": ""}),
    ],
)
def test_preview_and_execute_inputs_forbid_extras_and_empty_values(
    input_model: type[BillUiCreatePreviewInput]
    | type[BillUiUpdatePreviewInput]
    | type[BillUiDeletePreviewInput]
    | type[UiWriteExecuteInput],
    payload: dict[str, object],
) -> None:
    with pytest.raises(ValidationError):
        input_model.model_validate(payload)


def test_preview_does_not_submit() -> None:
    recorder = RecordingBillUiSubmitter()
    server, _ = make_server(submitter=recorder)
    preview = call_tool(
        server,
        "ui_bills_create_preview",
        {"unique_tag": "MCP-BILL-CREATE-1", "organization_id": "org-test"},
    )
    assert preview["confirmation_ticket"]
    assert preview["canonical_request"] == {
        "action": "create",
        "resource": "bill",
        "unique_tag": "MCP-BILL-CREATE-1",
        "draft_only": True,
    }
    assert preview["expected_effect_state"] == {
        "action": "create",
        "resource": "bill",
        "draft_only": True,
    }
    assert recorder.submissions == []


def test_execute_submits_once_and_replay_is_consumed() -> None:
    recorder = RecordingBillUiSubmitter()
    server, _ = make_server(submitter=recorder)
    preview = call_tool(
        server,
        "ui_bills_create_preview",
        {"unique_tag": "MCP-BILL-CREATE-2", "organization_id": "org-test"},
    )
    ticket = cast(str, preview["confirmation_ticket"])
    first = call_tool(server, "ui_bills_create_execute", {"confirmation_ticket": ticket})
    replay = call_tool(server, "ui_bills_create_execute", {"confirmation_ticket": ticket})
    assert first == {
        "submitted": True,
        "action": "create",
        "unique_tag": "MCP-BILL-CREATE-2",
    }
    assert replay["code"] == StableErrorCode.CONFIRMATION_CONSUMED
    assert len(recorder.submissions) == 1
    assert recorder.submissions[0].canonical_request["unique_tag"] == "MCP-BILL-CREATE-2"


def test_wrong_tool_and_tampered_ticket_do_not_submit() -> None:
    recorder = RecordingBillUiSubmitter()
    server, _ = make_server(submitter=recorder)
    preview = call_tool(
        server,
        "ui_bills_create_preview",
        {"unique_tag": "MCP-BILL-CREATE-3", "organization_id": "org-test"},
    )
    ticket = cast(str, preview["confirmation_ticket"])
    tampered = call_tool(
        server,
        "ui_bills_create_execute",
        {"confirmation_ticket": f"{ticket}x"},
    )
    wrong_tool = call_tool(
        server,
        "ui_bills_update_execute",
        {"confirmation_ticket": ticket},
    )
    assert tampered["code"] == StableErrorCode.CONFIRMATION_INVALID
    assert wrong_tool["code"] == StableErrorCode.CONFIRMATION_MISMATCH
    assert recorder.submissions == []


def test_expired_ticket_does_not_submit() -> None:
    clock = Clock()
    recorder = RecordingBillUiSubmitter()
    server, _ = make_server(clock=clock, submitter=recorder)
    preview = call_tool(
        server,
        "ui_bills_update_preview",
        {"id": "bill-draft-1", "unique_tag": "MCP-BILL-UPDATE-1", "organization_id": "org-test"},
    )
    assert preview["canonical_request"] == {
        "action": "update",
        "resource": "bill",
        "unique_tag": "MCP-BILL-UPDATE-1",
        "draft_only": True,
        "id": "bill-draft-1",
    }
    clock.now = clock.now + MAX_TICKET_TTL + timedelta(seconds=1)
    expired = call_tool(
        server,
        "ui_bills_update_execute",
        {"confirmation_ticket": cast(str, preview["confirmation_ticket"])},
    )
    assert expired["code"] == StableErrorCode.CONFIRMATION_EXPIRED
    assert recorder.submissions == []


def test_default_submitter_blocks_live_slot_without_http() -> None:
    server, submitter = make_server()
    assert submitter is None
    preview = call_tool(
        server,
        "ui_bills_delete_preview",
        {"id": "bill-draft-2", "unique_tag": "MCP-BILL-DELETE-1", "organization_id": "org-test"},
    )
    request = preview["canonical_request"]
    assert isinstance(request, dict)
    assert request["id"] == "bill-draft-2"
    assert request["draft_only"] is True
    blocked = call_tool(
        server,
        "ui_bills_delete_execute",
        {"confirmation_ticket": cast(str, preview["confirmation_ticket"])},
    )
    assert blocked["code"] == StableErrorCode.VALIDATION_ERROR
    assert LIVE_SLOT_BLOCKER_MESSAGE in cast(str, blocked["message"])


def test_draft_bill_line_description_uses_bill_line_field() -> None:
    from billy_mcp.ui_writes.bills_form import (
        BILL_DATE,
        DRAFT_SAVE,
        LINE_AMOUNT,
        LINE_DESCRIPTION,
        UPDATE_SAVE,
        VENDOR,
    )
    from billy_mcp.ui_writes.bills_vendor import VENDOR_INPUT_SELECTORS

    assert LINE_DESCRIPTION == "input[name='billLines.0.description']"
    assert VENDOR == VENDOR_INPUT_SELECTORS[0]
    assert VENDOR == "input[name='vendor']"
    assert BILL_DATE == "input[name='billDate']"
    assert LINE_AMOUNT == "input[name='billLines.0.inclVatAmount']"
    assert DRAFT_SAVE == "Gem som kladde"
    assert UPDATE_SAVE == "Opdater"


def test_create_persist_counts_only_post_not_put() -> None:
    from billy_mcp.ui_writes.bills_form import created_bill_id, is_persist_hit

    watched = [
        "GET 200 /v2/bills/from-get",
        "PUT 200 /v2/bills/from-put",
        "POST 200 /v2/bills",
    ]
    assert is_persist_hit("POST 200 /v2/bills", method="POST")
    assert not is_persist_hit("PUT 200 /v2/bills/from-put", method="POST")
    assert not is_persist_hit("GET 200 /v2/bills/from-get", method="POST")
    assert (
        created_bill_id(watched, bodies={"POST 200 /v2/bills": {"bills": [{"id": "from-post"}]}})
        == "from-post"
    )
    assert created_bill_id(watched) is None


def test_update_persist_requires_put_on_bill_id() -> None:
    from billy_mcp.ui_writes.bills_form import is_persist_hit

    assert is_persist_hit("PUT 200 /v2/bills/abc", method="PUT")
    assert not is_persist_hit("PUT 200 /v2/bills", method="PUT")
    assert not is_persist_hit("POST 200 /v2/bills", method="PUT")
    assert is_persist_hit("DELETE 204 /v2/bills/abc", method="DELETE")


def test_date_and_amount_match_billy_chrome() -> None:
    from billy_mcp.ui_writes.bills_form import amounts_match, dates_match

    assert dates_match("17.08.2026", "17-08-2026")
    assert dates_match("17-08-2026", "17-08-2026")
    assert not dates_match("16.08.2026", "17-08-2026")
    assert amounts_match("1,00", "1")
    assert amounts_match("1.00", "1")
    assert amounts_match("1", "1")
    assert not amounts_match("0,00", "1")


def test_refuse_booking_pay_and_email_ctas() -> None:
    from billy_mcp.ui_writes.bills_form import FORBIDDEN_CTAS, refuse_non_draft_cta

    for name in FORBIDDEN_CTAS:
        failed = refuse_non_draft_cta(name)
        assert failed is not None
        assert failed.code == StableErrorCode.VALIDATION_ERROR
    assert refuse_non_draft_cta("Gem som kladde") is None
    assert refuse_non_draft_cta("Opdater") is None
    assert refuse_non_draft_cta("Slet") is None


def test_pre_submit_dump_includes_tag_vendor_date_amount_and_draft_cta(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from billy_mcp.ui_writes import bills_form

    dump = tmp_path / "pre-submit.json"
    monkeypatch.setattr(bills_form, "CREATE_PRE_SUBMIT_DUMP", dump)
    monkeypatch.setattr(bills_form, "PRE_SUBMIT_DUMP", tmp_path / "update.json")
    bills_form.dump_pre_submit(
        url="https://mit.billy.dk/org-test/bills/new",
        unique_tag="MCP-UI-B-TEST",
        vendor="MCP-UI-B-TEST",
        bill_date="17-08-2026",
        line_amount="1",
        draft_cta="Gem som kladde",
    )
    payload = json.loads(dump.read_text(encoding="utf-8"))
    assert payload["unique_tag"] == "MCP-UI-B-TEST"
    assert payload["vendor"] == "MCP-UI-B-TEST"
    assert payload["date"] == "17-08-2026"
    assert payload["line_amount"] == "1"
    assert payload["draft_cta"] == "Gem som kladde"
    assert payload["url"].endswith("/bills/new")


def test_create_pre_submit_dump_survives_update_dump(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from billy_mcp.ui_writes import bills_form

    create_dump = tmp_path / "create.json"
    update_dump = tmp_path / "update.json"
    monkeypatch.setattr(bills_form, "CREATE_PRE_SUBMIT_DUMP", create_dump)
    monkeypatch.setattr(bills_form, "PRE_SUBMIT_DUMP", update_dump)
    bills_form.dump_pre_submit(
        url="https://mit.billy.dk/org-test/bills/new",
        unique_tag="MCP-UI-B-TEST",
        vendor="MCP-UI-B-TEST",
        bill_date="17.08.2026",
        line_amount="1",
        draft_cta="Gem som kladde",
        vendor_bind="label:Leverandør:option",
    )
    bills_form.dump_pre_submit(
        url="https://mit.billy.dk/org-test/bills/id/edit",
        unique_tag="MCP-UI-B-TEST-U",
        vendor="MCP-UI-B-TEST-U",
        bill_date="17.08.2026",
        line_amount="1",
        draft_cta="Opdater",
        vendor_bind="label:Leverandør:option",
    )
    created = json.loads(create_dump.read_text(encoding="utf-8"))
    updated = json.loads(update_dump.read_text(encoding="utf-8"))
    assert created["unique_tag"] == "MCP-UI-B-TEST"
    assert created["draft_cta"] == "Gem som kladde"
    assert created["vendor_bind"] == "label:Leverandør:option"
    assert updated["unique_tag"] == "MCP-UI-B-TEST-U"
    assert updated["draft_cta"] == "Opdater"


def test_vendor_bind_rejects_typed_only() -> None:
    from billy_mcp.ui_writes.bills_vendor import vendor_bind_is_complete

    assert vendor_bind_is_complete(option_clicked=True, enter_selected=False)
    assert vendor_bind_is_complete(option_clicked=False, enter_selected=True)
    assert not vendor_bind_is_complete(option_clicked=False, enter_selected=False)


def test_vendor_selectors_are_the_observed_vendor_field() -> None:
    from billy_mcp.ui_writes.bills_vendor import VENDOR_INPUT_SELECTORS, VENDOR_LABEL

    assert VENDOR_INPUT_SELECTORS == ("input[name='vendor']",)
    assert VENDOR_LABEL == "Leverandør"
    assert "input[name='contact']" not in VENDOR_INPUT_SELECTORS


def test_create_vendor_option_accepts_opret_leverandor() -> None:
    from billy_mcp.ui_writes.bills_vendor import is_create_vendor_option

    tag = "MCP-UI-B-TEST"
    assert is_create_vendor_option("Opret leverandør", tag)
    assert is_create_vendor_option(f'Opret "{tag}"', tag)
    assert not is_create_vendor_option("Opret kontakt", tag)
    assert not is_create_vendor_option(f'Opret "{tag}-U"', tag)


def test_vendor_chrome_dump_is_non_pii(tmp_path: Path) -> None:
    from billy_mcp.ui_writes.bills_vendor import dump_vendor_chrome

    dump = tmp_path / "vendor.json"
    dump_vendor_chrome(
        names=["contact", "entryDate"],
        chosen="input[name='contact']",
        destination=dump,
    )
    payload = json.loads(dump.read_text(encoding="utf-8"))
    assert payload["input_names"] == ["contact", "entryDate"]
    assert payload["chosen"] == "input[name='contact']"


def test_live_bills_test_does_not_seed_customer() -> None:
    source = Path("tests/live/test_ui_bills_writes.py").read_text(encoding="utf-8")
    assert "ui_clients_create_preview" not in source
    assert "ui_clients_create_execute" not in source


def test_vendor_option_targets_stay_inside_dropdown() -> None:
    from billy_mcp.ui_writes.bills_vendor import (
        DROPDOWN_SELECTORS,
        vendor_option_click_targets,
    )

    tag = "MCP-UI-B-TEST"
    targets = vendor_option_click_targets(tag)
    roots = {root for root, _text in targets}
    texts = {text for _root, text in targets}
    assert set(DROPDOWN_SELECTORS) <= roots
    assert tag in texts
    assert f'Opret "{tag}"' in texts
    assert "Opret leverandør" in texts
    assert all(root in DROPDOWN_SELECTORS for root, _text in targets)


def test_dropdown_create_row_requires_opret_and_tag() -> None:
    from billy_mcp.ui_writes.bills_vendor import dropdown_create_row_matches

    tag = "MCP-UI-B-TEST"
    assert dropdown_create_row_matches(f'Opret "{tag}"', tag)
    assert dropdown_create_row_matches(f"Opret {tag}", tag)
    assert not dropdown_create_row_matches(tag, tag)
    assert not dropdown_create_row_matches("Opret leverandør", tag)
    assert not dropdown_create_row_matches("Ingen resultater", tag)


def test_choose_vendor_source_has_no_page_wide_tag_click() -> None:
    source = Path("src/billy_mcp/ui_writes/bills_form.py").read_text(encoding="utf-8")
    assert "page.get_by_text(unique_tag" not in source
    assert "page.get_by_text(label" not in source
    assert "evaluate(" not in source
    assert "input[name='contact']" not in source


def test_scoped_wrapper_dump_is_non_pii(tmp_path: Path) -> None:
    from billy_mcp.ui_writes.bills_vendor import dump_scoped_vendor_wrapper

    dump = tmp_path / "wrapper.json"
    dump_scoped_vendor_wrapper(
        {
            "after_click": {"phase": "after_click", "input_name": "vendor", "value_len": 0},
            "after_type": {
                "phase": "after_type",
                "input_name": "vendor",
                "value_len": 17,
                "wrapper_list": {"has_opret": False},
            },
        },
        destination=dump,
    )
    payload = json.loads(dump.read_text(encoding="utf-8"))
    assert payload["after_type"]["input_name"] == "vendor"
    assert "MCP-" not in dump.read_text(encoding="utf-8")


def test_unit_dump_helpers_accept_tmp_path(tmp_path: Path) -> None:
    from billy_mcp.ui_writes.bills_vendor import dump_vendor_chrome

    dump = tmp_path / "vendor.json"
    dump_vendor_chrome(names=["vendor"], chosen="option", destination=dump)
    assert dump.is_file()
    assert not str(dump).startswith(str(Path.home() / ".local" / "share" / "billy-mcp"))
