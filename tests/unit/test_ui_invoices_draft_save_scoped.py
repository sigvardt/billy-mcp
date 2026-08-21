"""Given an empty dump, When checking scoped draft-save keys, Then they are missing."""

from __future__ import annotations

from pathlib import Path
from typing import Final

_REQUIRED: Final[list[str]] = [
    "gem_clicked",
    "invoice_persisted",
    "contact_input_present",
    "pickerfield_present",
    "active_element_category",
    "mutation_owned_count",
    "scoped_rows",
    "unique_action",
    "unique_action_owned_by_picker",
    "proved_bind",
    "missing_keys",
]


def test_empty_dump_misses_draft_save_scoped_keys() -> None:
    """Given an empty dump, When checking keys, Then the research set is missing."""

    from billy_mcp.ui_writes.invoices_draft_save_scoped import (
        REQUIRED_DRAFT_SAVE_SCOPED_KEYS,
        draft_save_scoped_missing_keys,
    )

    missing = draft_save_scoped_missing_keys({})
    assert missing == _REQUIRED
    assert list(REQUIRED_DRAFT_SAVE_SCOPED_KEYS) == _REQUIRED


def test_complete_empty_dump_is_ui_changed(tmp_path: Path) -> None:
    """Given a filled empty dump, When applied, Then bind stays none."""

    from billy_mcp.ui_writes.invoices_draft_save_scoped import (
        apply_draft_save_scoped_dump,
        draft_save_scoped_missing_keys,
        empty_draft_save_scoped,
    )

    payload = empty_draft_save_scoped()
    assert draft_save_scoped_missing_keys(payload) == []
    applied = apply_draft_save_scoped_dump(payload, dump_path=tmp_path / "empty.json")
    assert applied["proved_bind"] == "none"
    assert applied["unique_action"] == "none"
    assert applied["code"] == "UI_CHANGED"
    assert (tmp_path / "empty.json").is_file()


def test_inline_opret_ny_is_not_a_proved_bind() -> None:
    """Given a picker-owned Opret ny, When deriving bind, Then it is none."""

    from billy_mcp.ui_writes.invoices_draft_save_scoped import proved_bind_from

    payload = {
        "gem_clicked": True,
        "invoice_persisted": False,
        "unique_action": "inline_opret_ny",
        "unique_action_owned_by_picker": True,
        "proved_bind": "draft_save_scoped_existing_option",
    }
    assert proved_bind_from(payload) == "none"


def test_proved_bind_needs_owned_existing_option() -> None:
    """Given a click without an owned option, When deriving bind, Then it is none."""

    from billy_mcp.ui_writes.invoices_draft_save_scoped import proved_bind_from

    assert (
        proved_bind_from(
            {
                "gem_clicked": True,
                "invoice_persisted": False,
                "unique_action": "none",
                "unique_action_owned_by_picker": False,
                "proved_bind": "draft_save_scoped_existing_option",
            }
        )
        == "none"
    )


def test_proved_bind_rejects_persisted_invoice() -> None:
    """Given a persisted invoice, When deriving bind, Then it is none."""

    from billy_mcp.ui_writes.invoices_draft_save_scoped import proved_bind_from

    assert (
        proved_bind_from(
            {
                "gem_clicked": True,
                "invoice_persisted": True,
                "unique_action": "existing_option",
                "unique_action_owned_by_picker": True,
                "proved_bind": "draft_save_scoped_existing_option",
            }
        )
        == "none"
    )


def test_proved_bind_accepts_owned_existing_option(tmp_path: Path) -> None:
    """Given a scoped existing-option pick, Then bind is proved."""

    from billy_mcp.ui_writes.invoices_draft_save_scoped import (
        apply_draft_save_scoped_dump,
        empty_draft_save_scoped,
    )

    payload = empty_draft_save_scoped()
    payload["gem_clicked"] = True
    payload["contact_input_present"] = True
    payload["pickerfield_present"] = True
    payload["unique_action"] = "existing_option"
    payload["unique_action_owned_by_picker"] = True
    payload["proved_bind"] = "draft_save_scoped_existing_option"
    applied = apply_draft_save_scoped_dump(payload, dump_path=tmp_path / "proved.json")
    assert applied["proved_bind"] == "draft_save_scoped_existing_option"
    assert "code" not in applied


def test_unique_action_prefers_owned_option() -> None:
    """Given one picker-owned option, When deriving action, Then it is existing_option."""

    from billy_mcp.ui_writes.invoices_draft_save_scoped import unique_action_from

    rows = [
        {
            "tag": "LI",
            "role": "option",
            "visible": True,
            "interactive": True,
            "exact_match": "option",
            "box": {"dx": 0, "dy": 40, "w": 200, "h": 24},
            "z_index": "auto",
            "ownership_path": ["list", "pickerfield"],
            "is_mutation_owned": True,
        }
    ]
    action, owned = unique_action_from(rows)
    assert action == "existing_option"
    assert owned is True


def test_unique_action_inline_opret_ny_when_owned() -> None:
    """Given one picker-owned Opret ny and no option, Then action is inline_opret_ny."""

    from billy_mcp.ui_writes.invoices_draft_save_scoped import unique_action_from

    rows = [
        {
            "tag": "BUTTON",
            "role": "button",
            "visible": True,
            "interactive": True,
            "exact_match": "opret_ny",
            "box": {"dx": 8, "dy": 72, "w": 180, "h": 28},
            "z_index": "auto",
            "ownership_path": ["list", "pickerfield"],
            "is_mutation_owned": True,
        }
    ]
    action, owned = unique_action_from(rows)
    assert action == "inline_opret_ny"
    assert owned is True


def test_sidebar_opret_ny_is_not_owned() -> None:
    """Given a nav Opret ny, When deriving action, Then it is none."""

    from billy_mcp.ui_writes.invoices_draft_save_scoped import unique_action_from

    rows = [
        {
            "tag": "BUTTON",
            "role": "button",
            "visible": True,
            "interactive": True,
            "exact_match": "opret_ny",
            "box": {"dx": -240, "dy": -80, "w": 120, "h": 32},
            "z_index": "auto",
            "ownership_path": ["nav"],
            "is_mutation_owned": False,
        }
    ]
    action, owned = unique_action_from(rows)
    assert action == "none"
    assert owned is False


def test_delivered_dump_requires_complete_keys(tmp_path: Path) -> None:
    """Given a complete dump file, When checking delivery, Then it is delivered."""

    from billy_mcp.ui_writes.invoices_draft_save_scoped import (
        apply_draft_save_scoped_dump,
        draft_save_scoped_dump_is_delivered,
        empty_draft_save_scoped,
    )

    missing = tmp_path / "missing.json"
    assert draft_save_scoped_dump_is_delivered(missing) is False
    path = tmp_path / "delivered.json"
    apply_draft_save_scoped_dump(empty_draft_save_scoped(), dump_path=path)
    assert draft_save_scoped_dump_is_delivered(path) is True


def test_dump_json_has_no_secrets() -> None:
    """Given a dump payload, When encoded, Then no URL or customer tag remains."""

    from billy_mcp.ui_writes.invoices_draft_save_scoped import (
        draft_save_scoped_dump_json,
        empty_draft_save_scoped,
    )

    encoded = draft_save_scoped_dump_json(empty_draft_save_scoped())
    assert "https://" not in encoded
    assert "MCP-UI-INV-" not in encoded
    assert "Gem som kladde" not in encoded
    assert "Dette felt" not in encoded
    assert "Opret ny" not in encoded
    assert "opret_ny_count" not in encoded


def test_helper_has_no_closed_inspectors() -> None:
    """Given the helper, When reading source, Then closed inspectors stay closed."""

    from billy_mcp.ui_writes import invoices_draft_save_scoped

    body = Path(invoices_draft_save_scoped.__file__).read_text(encoding="utf-8")
    assert "getEventListeners" not in body
    assert "getScriptSource" not in body
    assert "Ember.View" not in body
    assert "__reactFiber" not in body
    assert "press_sequentially" not in body
    assert "callFunctionOn" not in body
    assert "page.goto" not in body
    assert "force=True" not in body
    assert "inspect-live-invoices-vaelg-kunde" not in body
    assert "inspect-live-invoices-draft-save-validation.json" not in body
    assert "get_by_text" not in body
    assert "roots.push(document.body)" not in body
    assert "observe(document.body" not in body
    from billy_mcp.ui_writes.invoices_draft_save_scoped import ROW_CAP

    assert ROW_CAP == 16
