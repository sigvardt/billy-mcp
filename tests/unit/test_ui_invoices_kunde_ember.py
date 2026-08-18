"""Given the live descendant dump, When checking Ember keys, Then they are missing."""

from __future__ import annotations

from pathlib import Path
from typing import Final

_LIVE_DESCENDANTS: Final[dict[str, object]] = {
    "unique_target": False,
    "wrapper_handler_guard": "none",
    "visible_descendant_count": 2,
}
_REQUIRED: Final[list[str]] = [
    "ember_global_present",
    "view_registry_present",
    "wrapper_ember_id_class",
    "lookup_class",
    "view_present",
    "view_constructor_token",
    "property_rows",
    "method_name_tokens",
    "bound_selection_present",
    "bound_selection_type",
    "candidate_collection_present",
    "candidate_collection_type",
    "candidate_length_class",
    "open_state_key",
    "open_state",
    "named_open_action",
    "named_select_action",
    "named_filter_action",
    "unique_normal_action",
    "unique_normal_action_token",
    "kunde_ember_missing_keys",
]


def test_live_descendant_dump_misses_31b0c7a6_ember_keys() -> None:
    """Given the current descendant dump, When checking Ember keys, Then they are missing."""

    from billy_mcp.ui_writes.invoices_kunde_ember import (
        REQUIRED_KUNDE_EMBER_KEYS,
        kunde_ember_missing_keys,
    )

    missing = kunde_ember_missing_keys(_LIVE_DESCENDANTS)
    assert missing == _REQUIRED
    assert set(_REQUIRED).issubset(REQUIRED_KUNDE_EMBER_KEYS)
    for key in _REQUIRED:
        assert key not in _LIVE_DESCENDANTS


def test_complete_ember_dump_has_no_missing_keys(tmp_path: Path) -> None:
    """Given a filled Ember dump, When checking keys, Then none are missing."""

    from billy_mcp.ui_writes.invoices_kunde_ember import (
        apply_kunde_ember_dump,
        empty_kunde_ember,
        kunde_ember_missing_keys,
        unique_normal_action_from,
    )

    payload = empty_kunde_ember()
    assert kunde_ember_missing_keys(payload) == []
    assert unique_normal_action_from(payload) is False
    applied = apply_kunde_ember_dump(payload, dump_path=tmp_path / "ember.json")
    assert applied["unique_normal_action"] is False
    assert applied["code"] == "UI_CHANGED"
    assert (tmp_path / "ember.json").is_file()


def test_unique_normal_action_needs_action_and_unused_target() -> None:
    """Given one named action without an unused target, When checking, Then it is false."""

    from billy_mcp.ui_writes.invoices_kunde_ember import (
        apply_kunde_ember_dump,
        empty_kunde_ember,
        unique_normal_action_from,
    )

    payload = empty_kunde_ember()
    payload["method_name_tokens"] = ["open"]
    payload["unique_target"] = False
    assert unique_normal_action_from(payload) is False
    applied = apply_kunde_ember_dump(payload)
    assert applied["named_open_action"] == "open"
    assert applied["unique_normal_action"] is False
    assert applied["unique_normal_action_token"] == "none"
    payload["named_open_action"] = "open"
    payload["unique_target"] = True
    assert unique_normal_action_from(payload) is True
    applied = apply_kunde_ember_dump(payload)
    assert applied["unique_normal_action"] is True
    assert applied["unique_normal_action_token"] == "open"


def test_ember_rows_reject_raw_values() -> None:
    """Given an Ember dump, When encoded, Then raw names and URLs are absent."""

    from billy_mcp.ui_writes.invoices_kunde_ember import (
        ember_dump_json,
        empty_kunde_ember,
        sanitize_property_row,
    )

    payload = empty_kunde_ember()
    payload["property_rows"] = [
        sanitize_property_row(
            {
                "name": "contactId",
                "type": "string",
                "value": "do-not-store",
            }
        )
    ]
    encoded = ember_dump_json(payload)
    assert "https://" not in encoded
    assert "mit.billy.dk" not in encoded
    assert "MCP-UI" not in encoded
    assert "do-not-store" not in encoded
    assert "ember123" not in encoded


def test_unknown_public_name_becomes_other(tmp_path: Path) -> None:
    """Given an unknown public name, When sanitizing, Then it is other and kept."""

    from billy_mcp.ui_writes.invoices_kunde_ember import (
        apply_kunde_ember_dump,
        empty_kunde_ember,
        name_token,
        sanitize_property_row,
    )

    assert name_token("element") == "other"
    assert name_token("contactId") == "contactId"
    payload = empty_kunde_ember()
    payload["property_rows"] = [sanitize_property_row({"name": "element", "type": "object"})]
    applied = apply_kunde_ember_dump(payload, dump_path=tmp_path / "other.json")
    assert applied["property_rows"] == [{"name_token": "other", "value_type": "object"}]
    assert applied["unique_normal_action"] is False


def test_delivered_ember_dump_requires_complete_keys(tmp_path: Path) -> None:
    """Given a complete dump file, When checking delivery, Then it is delivered."""

    from billy_mcp.ui_writes.invoices_kunde_ember import (
        apply_kunde_ember_dump,
        ember_dump_is_delivered,
        empty_kunde_ember,
    )

    missing = tmp_path / "missing.json"
    assert ember_dump_is_delivered(missing) is False
    path = tmp_path / "delivered.json"
    apply_kunde_ember_dump(empty_kunde_ember(), dump_path=path)
    assert ember_dump_is_delivered(path) is True


def test_ember_capture_is_read_only() -> None:
    """Given the live capture, When reading source, Then it does not click or invoke."""

    from billy_mcp.ui_writes import invoices_form_bind, invoices_kunde_ember_inspect

    bind = Path(invoices_form_bind.__file__).read_text(encoding="utf-8")
    start = bind.index("async def capture_kunde_ember")
    end = bind.index("async def apply_named_control_action")
    body = bind[start:end]
    inspect = Path(invoices_kunde_ember_inspect.__file__).read_text(encoding="utf-8")
    assert "Runtime.getProperties" in inspect
    assert "callFunctionOn" not in inspect
    assert "Ember.get(" not in inspect
    assert "view.get(" not in inspect.replace("preview.get(", "")
    assert ".click(" not in body
    assert ".click(" not in inspect
    assert "_type_kunde" not in body
    assert "press_sequentially" not in body
    assert "get_by_role" not in body
