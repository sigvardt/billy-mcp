"""Given an empty dump, When checking draft-save validation keys, Then they are missing."""

from __future__ import annotations

from pathlib import Path
from typing import Final

_REQUIRED: Final[list[str]] = [
    "validation_message_present",
    "ingen_kontakter_count",
    "opret_ny_count",
    "option_role_count",
    "gem_clicked",
    "invoice_persisted",
    "proved_bind",
    "missing_keys",
]


def test_empty_dump_misses_draft_save_validation_keys() -> None:
    """Given an empty dump, When checking keys, Then the research set is missing."""

    from billy_mcp.ui_writes.invoices_draft_save_validation import (
        REQUIRED_DRAFT_SAVE_VALIDATION_KEYS,
        draft_save_validation_missing_keys,
    )

    missing = draft_save_validation_missing_keys({})
    assert missing == _REQUIRED
    assert list(REQUIRED_DRAFT_SAVE_VALIDATION_KEYS) == _REQUIRED


def test_complete_empty_dump_is_ui_changed(tmp_path: Path) -> None:
    """Given a filled empty dump, When applied, Then bind stays none."""

    from billy_mcp.ui_writes.invoices_draft_save_validation import (
        apply_draft_save_validation_dump,
        draft_save_validation_missing_keys,
        empty_draft_save_validation,
        list_or_validation_open,
    )

    payload = empty_draft_save_validation()
    assert draft_save_validation_missing_keys(payload) == []
    assert list_or_validation_open(payload) is False
    applied = apply_draft_save_validation_dump(payload, dump_path=tmp_path / "empty.json")
    assert applied["proved_bind"] == "none"
    assert applied["code"] == "UI_CHANGED"
    assert (tmp_path / "empty.json").is_file()


def test_page_wide_opret_ny_is_not_a_proved_list_open() -> None:
    """Given only Opret ny, When checking list-open, Then it is false."""

    from billy_mcp.ui_writes.invoices_draft_save_validation import (
        list_or_validation_open,
        proved_bind_from,
    )

    payload = {
        "gem_clicked": True,
        "invoice_persisted": False,
        "validation_message_present": False,
        "ingen_kontakter_count": 0,
        "opret_ny_count": 1,
        "option_role_count": 0,
        "proved_bind": "draft_save_validation_existing_option",
    }
    assert list_or_validation_open(payload) is False
    assert proved_bind_from(payload) == "none"


def test_proved_bind_needs_click_and_open_list() -> None:
    """Given a click without an open list, When deriving bind, Then it is none."""

    from billy_mcp.ui_writes.invoices_draft_save_validation import proved_bind_from

    assert (
        proved_bind_from(
            {
                "gem_clicked": True,
                "invoice_persisted": False,
                "validation_message_present": False,
                "ingen_kontakter_count": 0,
                "opret_ny_count": 0,
                "option_role_count": 0,
                "proved_bind": "draft_save_validation_existing_option",
            }
        )
        == "none"
    )


def test_proved_bind_rejects_persisted_invoice() -> None:
    """Given a persisted invoice, When deriving bind, Then it is none."""

    from billy_mcp.ui_writes.invoices_draft_save_validation import proved_bind_from

    assert (
        proved_bind_from(
            {
                "gem_clicked": True,
                "invoice_persisted": True,
                "validation_message_present": True,
                "option_role_count": 1,
                "proved_bind": "draft_save_validation_existing_option",
            }
        )
        == "none"
    )


def test_proved_bind_accepts_existing_option_after_validation(tmp_path: Path) -> None:
    """Given a validation-open existing-option pick, Then bind is proved."""

    from billy_mcp.ui_writes.invoices_draft_save_validation import (
        apply_draft_save_validation_dump,
        empty_draft_save_validation,
    )

    payload = empty_draft_save_validation()
    payload["gem_clicked"] = True
    payload["validation_message_present"] = True
    payload["option_role_count"] = 1
    payload["proved_bind"] = "draft_save_validation_existing_option"
    applied = apply_draft_save_validation_dump(payload, dump_path=tmp_path / "proved.json")
    assert applied["proved_bind"] == "draft_save_validation_existing_option"
    assert "code" not in applied


def test_delivered_dump_requires_complete_keys(tmp_path: Path) -> None:
    """Given a complete dump file, When checking delivery, Then it is delivered."""

    from billy_mcp.ui_writes.invoices_draft_save_validation import (
        apply_draft_save_validation_dump,
        draft_save_validation_dump_is_delivered,
        empty_draft_save_validation,
    )

    missing = tmp_path / "missing.json"
    assert draft_save_validation_dump_is_delivered(missing) is False
    path = tmp_path / "delivered.json"
    apply_draft_save_validation_dump(empty_draft_save_validation(), dump_path=path)
    assert draft_save_validation_dump_is_delivered(path) is True


def test_dump_json_has_no_secrets() -> None:
    """Given a dump payload, When encoded, Then no URL or customer tag remains."""

    from billy_mcp.ui_writes.invoices_draft_save_validation import (
        draft_save_validation_dump_json,
        empty_draft_save_validation,
    )

    encoded = draft_save_validation_dump_json(empty_draft_save_validation())
    assert "https://" not in encoded
    assert "MCP-UI-INV-" not in encoded
    assert "Gem som kladde" not in encoded
    assert "Dette felt" not in encoded


def test_helper_has_no_closed_inspectors() -> None:
    """Given the helper, When reading source, Then closed inspectors stay closed."""

    from billy_mcp.ui_writes import invoices_draft_save_validation

    body = Path(invoices_draft_save_validation.__file__).read_text(encoding="utf-8")
    assert "getEventListeners" not in body
    assert "getScriptSource" not in body
    assert "Ember.View" not in body
    assert "__reactFiber" not in body
    assert "press_sequentially" not in body
    assert "callFunctionOn" not in body
    assert "page.goto" not in body
    assert "page.evaluate" not in body
    assert "force=True" not in body
    assert "inspect-live-invoices-vaelg-kunde" not in body
