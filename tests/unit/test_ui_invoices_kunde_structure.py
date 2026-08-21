"""Given the live listener dump, When checking structure keys, Then they are missing."""

from __future__ import annotations

from pathlib import Path
from typing import Final

_LIVE_LISTENERS: Final[dict[str, object]] = {
    "rows": [
        {
            "event_type": "keydown",
            "phase": "bubble",
            "target_category": "input",
            "event_property_categories": [],
            "accepted_key_category": "none",
            "invoked_action_token": "none",
        },
        {
            "event_type": "click",
            "phase": "bubble",
            "target_category": "pickerfield",
            "event_property_categories": [],
            "accepted_key_category": "none",
            "invoked_action_token": "none",
        },
    ],
    "unique_normal_action": False,
    "unique_normal_action_token": "none",
    "kunde_listener_missing_keys": [],
}
_REQUIRED: Final[list[str]] = [
    "kunde_input_name_token",
    "bills_input_name_token",
    "kunde_wrapper_family",
    "bills_wrapper_family",
    "kunde_wrapper_data_attr_names",
    "kunde_search_trigger",
    "bills_search_trigger",
    "kunde_overlay_present",
    "kunde_list_host",
    "bills_list_host",
    "kunde_option_role_count",
    "bills_option_role_count",
    "same_family",
    "transferable_action",
    "unique_normal_action",
    "proved_kunde_bind",
    "proved_bills_bind",
    "kunde_structure_missing_keys",
]


def test_live_listener_dump_misses_structure_keys() -> None:
    """Given the current listener dump, When checking structure keys, Then they are missing."""

    from billy_mcp.ui_writes.invoices_kunde_structure import (
        REQUIRED_KUNDE_STRUCTURE_KEYS,
        kunde_structure_missing_keys,
    )

    missing = kunde_structure_missing_keys(_LIVE_LISTENERS)
    assert missing == _REQUIRED
    assert set(_REQUIRED).issubset(REQUIRED_KUNDE_STRUCTURE_KEYS)
    for key in _REQUIRED:
        if key == "unique_normal_action":
            continue
        assert key not in _LIVE_LISTENERS


def test_complete_structure_dump_has_no_missing_keys(tmp_path: Path) -> None:
    """Given a filled compare dump, When checking keys, Then none are missing."""

    from billy_mcp.ui_writes.invoices_kunde_structure import (
        apply_kunde_structure_dump,
        empty_kunde_structure,
        kunde_structure_missing_keys,
        unique_normal_action_from,
    )

    payload = empty_kunde_structure()
    assert kunde_structure_missing_keys(payload) == []
    assert unique_normal_action_from(payload) is False
    applied = apply_kunde_structure_dump(payload, dump_path=tmp_path / "structure.json")
    assert applied["unique_normal_action"] is False
    assert applied["same_family"] is False
    assert applied["transferable_action"] == "none"
    assert applied["code"] == "UI_CHANGED"
    assert (tmp_path / "structure.json").is_file()


def test_same_family_requires_bills_chrome_on_both(tmp_path: Path) -> None:
    """Given pickerfield versus input-wrapper, When comparing, Then families differ."""

    from billy_mcp.ui_writes.invoices_kunde_structure import (
        apply_kunde_structure_dump,
        empty_kunde_structure,
        same_family_from,
        transferable_action_from,
    )

    payload = empty_kunde_structure()
    payload["kunde_wrapper_family"] = "pickerfield"
    payload["bills_wrapper_family"] = "input_wrapper"
    payload["kunde_search_trigger"] = False
    payload["bills_search_trigger"] = True
    payload["kunde_list_host"] = "none"
    payload["bills_list_host"] = "ds_dropdown_portal"
    assert same_family_from(payload) is False
    assert transferable_action_from(payload) == "none"
    applied = apply_kunde_structure_dump(payload, dump_path=tmp_path / "diff.json")
    assert applied["same_family"] is False
    assert applied["transferable_action"] == "none"
    assert applied["unique_normal_action"] is False


def test_transferable_action_needs_unused_bills_host(tmp_path: Path) -> None:
    """Given invoice input-wrapper plus search and portal, Then it is transferable."""

    from billy_mcp.ui_writes.invoices_kunde_structure import (
        apply_kunde_structure_dump,
        empty_kunde_structure,
        transferable_action_from,
        unique_normal_action_from,
    )

    payload = empty_kunde_structure()
    payload["kunde_wrapper_family"] = "input_wrapper"
    payload["bills_wrapper_family"] = "input_wrapper"
    payload["kunde_search_trigger"] = True
    payload["bills_search_trigger"] = True
    payload["kunde_list_host"] = "ds_dropdown_portal"
    payload["bills_list_host"] = "ds_dropdown_portal"
    assert transferable_action_from(payload) == "portal_option"
    assert unique_normal_action_from(payload) is True
    applied = apply_kunde_structure_dump(payload, dump_path=tmp_path / "same.json")
    assert applied["same_family"] is True
    assert applied["transferable_action"] == "portal_option"
    assert applied["unique_normal_action"] is True
    assert "code" not in applied


def test_structure_dump_rejects_raw_values() -> None:
    """Given a compare dump, When encoded, Then source and URLs are absent."""

    from billy_mcp.ui_writes.invoices_kunde_structure import (
        empty_kunde_structure,
        sanitize_data_attr_names,
        structure_dump_json,
    )

    payload = empty_kunde_structure()
    payload["kunde_wrapper_data_attr_names"] = sanitize_data_attr_names(
        ["data-cy", "https://mit.billy.dk/do-not-store", "id"]
    )
    encoded = structure_dump_json(payload)
    assert payload["kunde_wrapper_data_attr_names"] == ["data-cy"]
    assert "https://" not in encoded
    assert "mit.billy.dk" not in encoded
    assert "do-not-store" not in encoded


def test_delivered_structure_dump_requires_complete_keys(tmp_path: Path) -> None:
    """Given a complete dump file, When checking delivery, Then it is delivered."""

    from billy_mcp.ui_writes.invoices_kunde_structure import (
        apply_kunde_structure_dump,
        empty_kunde_structure,
        structure_dump_is_delivered,
    )

    missing = tmp_path / "missing.json"
    assert structure_dump_is_delivered(missing) is False
    path = tmp_path / "delivered.json"
    apply_kunde_structure_dump(empty_kunde_structure(), dump_path=path)
    assert structure_dump_is_delivered(path) is True


def test_map_existing_dumps_uses_inline_fixtures(tmp_path: Path) -> None:
    """Given fixture dumps, When mapping, Then compare keys stay sanitized."""

    from billy_mcp.ui_writes.invoices_kunde_structure import (
        apply_kunde_structure_dump,
        map_existing_dumps,
    )

    control = tmp_path / "control.json"
    descendants = tmp_path / "descendants.json"
    post_click = tmp_path / "post.json"
    vendor = tmp_path / "vendor.json"
    wrapper = tmp_path / "wrapper.json"
    dropdown = tmp_path / "dropdown.json"
    control.write_text(
        '{"wrapper_class_tokens":["ember-view","pickerfield"],'
        '"wrapper_data_attr_names":["data-cy"],"action_option_role_count":0}',
        encoding="utf-8",
    )
    descendants.write_text(
        '{"descendants":[{"box":{"dx":242.0,"dy":0.0,"w":40.0,"h":40.0}}]}',
        encoding="utf-8",
    )
    post_click.write_text('{"changed_node_count":0}', encoding="utf-8")
    vendor.write_text(
        '{"input_names":["vendor"],"chosen":"scoped:existing_option"}',
        encoding="utf-8",
    )
    wrapper.write_text(
        '{"after_click":{"input_name":"vendor","search_trigger":true,"portal_list":{"count":9}}}',
        encoding="utf-8",
    )
    dropdown.write_text('{"option":0}', encoding="utf-8")
    mapped = map_existing_dumps(
        control_path=control,
        descendant_path=descendants,
        post_click_path=post_click,
        bills_vendor_path=vendor,
        bills_wrapper_path=wrapper,
        bills_dropdown_path=dropdown,
    )
    applied = apply_kunde_structure_dump(mapped, dump_path=tmp_path / "out.json")
    assert applied["kunde_input_name_token"] == "contact"
    assert applied["bills_input_name_token"] == "vendor"
    assert applied["kunde_wrapper_family"] == "pickerfield"
    assert applied["bills_wrapper_family"] == "input_wrapper"
    assert applied["kunde_wrapper_data_attr_names"] == ["data-cy"]
    assert applied["kunde_search_trigger"] is False
    assert applied["bills_search_trigger"] is True
    assert applied["kunde_overlay_present"] is True
    assert applied["kunde_list_host"] == "none"
    assert applied["bills_list_host"] == "ds_dropdown_portal"
    assert applied["same_family"] is False
    assert applied["transferable_action"] == "none"
    assert applied["proved_bills_bind"] == "scoped_existing_option"
    assert applied["proved_kunde_bind"] == "none"
    assert applied["code"] == "UI_CHANGED"


def test_structure_capture_is_read_only() -> None:
    """Given the compare helper, When reading source, Then it does not click or inspect."""

    from billy_mcp.ui_writes import invoices_kunde_structure

    body = Path(invoices_kunde_structure.__file__).read_text(encoding="utf-8")
    assert "getEventListeners" not in body
    assert "getScriptSource" not in body
    assert "Ember.View" not in body
    assert "__reactFiber" not in body
    assert ".click(" not in body
    assert "press_sequentially" not in body
    assert "callFunctionOn" not in body
