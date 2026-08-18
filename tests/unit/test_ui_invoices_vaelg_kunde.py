"""Given an empty dump, When checking Vælg kunde keys, Then they are missing."""

from __future__ import annotations

from pathlib import Path
from typing import Final

_REQUIRED: Final[list[str]] = [
    "vaelg_kunde_button_count",
    "vaelg_kunde_link_count",
    "vaelg_kunde_other_count",
    "unique_vaelg_kunde",
    "hit_is_contact_input",
    "clicked",
    "opret_ny_count",
    "option_role_count",
    "proved_bind",
    "missing_keys",
]


def test_empty_dump_misses_vaelg_kunde_keys() -> None:
    """Given an empty dump, When checking keys, Then the research set is missing."""

    from billy_mcp.ui_writes.invoices_vaelg_kunde import (
        REQUIRED_VAELG_KUNDE_KEYS,
        vaelg_kunde_missing_keys,
    )

    missing = vaelg_kunde_missing_keys({})
    assert missing == _REQUIRED
    assert list(REQUIRED_VAELG_KUNDE_KEYS) == _REQUIRED


def test_complete_empty_dump_is_ui_changed(tmp_path: Path) -> None:
    """Given a filled empty dump, When applied, Then bind stays none."""

    from billy_mcp.ui_writes.invoices_vaelg_kunde import (
        apply_vaelg_kunde_dump,
        empty_vaelg_kunde,
        unique_vaelg_kunde_from,
        vaelg_kunde_missing_keys,
    )

    payload = empty_vaelg_kunde()
    assert vaelg_kunde_missing_keys(payload) == []
    assert unique_vaelg_kunde_from(payload) is False
    applied = apply_vaelg_kunde_dump(payload, dump_path=tmp_path / "empty.json")
    assert applied["unique_vaelg_kunde"] is False
    assert applied["proved_bind"] == "none"
    assert applied["code"] == "UI_CHANGED"
    assert (tmp_path / "empty.json").is_file()


def test_placeholder_input_is_not_unique() -> None:
    """Given only the contact input placeholder, When deriving unique, Then it is false."""

    from billy_mcp.ui_writes.invoices_vaelg_kunde import unique_vaelg_kunde_from

    assert (
        unique_vaelg_kunde_from(
            {
                "vaelg_kunde_button_count": 0,
                "vaelg_kunde_link_count": 0,
                "vaelg_kunde_other_count": 0,
                "hit_is_contact_input": True,
            }
        )
        is False
    )


def test_one_button_is_unique_when_not_the_input() -> None:
    """Given one Vælg kunde button that is not the input, Then unique is true."""

    from billy_mcp.ui_writes.invoices_vaelg_kunde import unique_vaelg_kunde_from

    assert (
        unique_vaelg_kunde_from(
            {
                "vaelg_kunde_button_count": 1,
                "vaelg_kunde_link_count": 0,
                "vaelg_kunde_other_count": 0,
                "hit_is_contact_input": False,
            }
        )
        is True
    )


def test_proved_bind_needs_click_and_existing_option(tmp_path: Path) -> None:
    """Given a unique click without an existing-option pick, Then bind stays none."""

    from billy_mcp.ui_writes.invoices_vaelg_kunde import (
        apply_vaelg_kunde_dump,
        empty_vaelg_kunde,
        proved_bind_from,
    )

    payload = empty_vaelg_kunde()
    payload["vaelg_kunde_button_count"] = 1
    payload["clicked"] = True
    payload["option_role_count"] = 2
    assert proved_bind_from({**payload, "unique_vaelg_kunde": True}) == "none"
    applied = apply_vaelg_kunde_dump(payload, dump_path=tmp_path / "clicked.json")
    assert applied["unique_vaelg_kunde"] is True
    assert applied["proved_bind"] == "none"
    assert applied["code"] == "UI_CHANGED"


def test_proved_bind_accepts_existing_option_after_click(tmp_path: Path) -> None:
    """Given a unique click and an existing-option pick, Then bind is proved."""

    from billy_mcp.ui_writes.invoices_vaelg_kunde import apply_vaelg_kunde_dump, empty_vaelg_kunde

    payload = empty_vaelg_kunde()
    payload["vaelg_kunde_button_count"] = 1
    payload["clicked"] = True
    payload["proved_bind"] = "vaelg_kunde_existing_option"
    applied = apply_vaelg_kunde_dump(payload, dump_path=tmp_path / "proved.json")
    assert applied["unique_vaelg_kunde"] is True
    assert applied["proved_bind"] == "vaelg_kunde_existing_option"
    assert "code" not in applied


def test_delivered_dump_requires_complete_keys(tmp_path: Path) -> None:
    """Given a complete dump file, When checking delivery, Then it is delivered."""

    from billy_mcp.ui_writes.invoices_vaelg_kunde import (
        apply_vaelg_kunde_dump,
        empty_vaelg_kunde,
        vaelg_kunde_dump_is_delivered,
    )

    missing = tmp_path / "missing.json"
    assert vaelg_kunde_dump_is_delivered(missing) is False
    path = tmp_path / "delivered.json"
    apply_vaelg_kunde_dump(empty_vaelg_kunde(), dump_path=path)
    assert vaelg_kunde_dump_is_delivered(path) is True


def test_dump_json_has_no_secrets() -> None:
    """Given a dump payload, When encoded, Then no URL or customer tag remains."""

    from billy_mcp.ui_writes.invoices_vaelg_kunde import empty_vaelg_kunde, vaelg_kunde_dump_json

    encoded = vaelg_kunde_dump_json(empty_vaelg_kunde())
    assert "https://" not in encoded
    assert "MCP-UI-INV-" not in encoded
    assert "Vælg kunde" not in encoded


def test_helper_has_no_closed_inspectors() -> None:
    """Given the helper, When reading source, Then closed inspectors stay closed."""

    from billy_mcp.ui_writes import invoices_vaelg_kunde

    body = Path(invoices_vaelg_kunde.__file__).read_text(encoding="utf-8")
    assert "getEventListeners" not in body
    assert "getScriptSource" not in body
    assert "Ember.View" not in body
    assert "__reactFiber" not in body
    assert "press_sequentially" not in body
    assert "callFunctionOn" not in body
    assert "page.goto" not in body
    assert "page.evaluate" not in body
    assert "force=True" not in body
