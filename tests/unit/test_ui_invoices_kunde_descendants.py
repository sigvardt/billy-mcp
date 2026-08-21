"""Given the live post-click dump, When checking descendant keys, Then they are missing."""

from __future__ import annotations

from pathlib import Path
from typing import Final

_LIVE_POST_CLICK: Final[dict[str, object]] = {
    "click_target": "pickerfield",
    "changed_node_count": 0,
    "baseline_hidden_subtree_count": 2,
}
_REQUIRED: Final[list[str]] = [
    "wrapper_tag",
    "visible_descendant_count",
    "descendants",
    "unique_target",
    "unique_target_category",
    "wrapper_handler_guard",
    "kunde_descendant_missing_keys",
]


def test_live_post_click_misses_e87b6aef_descendant_keys() -> None:
    """Given the current post-click dump, When checking descendant keys, Then they are missing."""

    from billy_mcp.ui_writes.invoices_kunde_descendants import (
        REQUIRED_KUNDE_DESCENDANT_KEYS,
        kunde_descendant_missing_keys,
    )

    missing = kunde_descendant_missing_keys(_LIVE_POST_CLICK)
    assert missing == _REQUIRED
    assert set(_REQUIRED).issubset(REQUIRED_KUNDE_DESCENDANT_KEYS)
    for key in _REQUIRED:
        assert key not in _LIVE_POST_CLICK


def test_complete_descendant_dump_has_no_missing_keys(tmp_path: Path) -> None:
    """Given a filled descendant dump, When checking keys, Then none are missing."""

    from billy_mcp.ui_writes.invoices_kunde_descendants import (
        apply_kunde_descendant_dump,
        empty_kunde_descendants,
        kunde_descendant_missing_keys,
        unique_target_from_descendants,
    )

    payload = empty_kunde_descendants()
    assert kunde_descendant_missing_keys(payload) == []
    assert unique_target_from_descendants(payload) is False
    applied = apply_kunde_descendant_dump(payload, dump_path=tmp_path / "descendants.json")
    assert applied["unique_target"] is False
    assert applied["code"] == "UI_CHANGED"
    assert (tmp_path / "descendants.json").is_file()


def test_unique_target_requires_one_unused_toggle() -> None:
    """Given one unused toggle, When checking unique_target, Then it is true."""

    from billy_mcp.ui_writes.invoices_kunde_descendants import (
        empty_kunde_descendants,
        unique_target_from_descendants,
    )

    payload = empty_kunde_descendants()
    payload["descendants"] = [
        {
            "tag_category": "input",
            "role": "none",
            "visible": True,
            "interactive": True,
            "class_token_categories": ["text-field"],
            "data_attr_names": [],
            "box": {"dx": 0.0, "dy": 0.0, "w": 210.0, "h": 40.0},
            "pointer_events": "auto",
            "listener_types": ["keydown"],
        },
        {
            "tag_category": "div",
            "role": "none",
            "visible": True,
            "interactive": True,
            "class_token_categories": ["other"],
            "data_attr_names": [],
            "box": {"dx": 242.0, "dy": 0.0, "w": 40.0, "h": 40.0},
            "pointer_events": "auto",
            "listener_types": [],
        },
        {
            "tag_category": "button",
            "role": "button",
            "visible": True,
            "interactive": True,
            "class_token_categories": ["toggle"],
            "data_attr_names": ["data-cy"],
            "box": {"dx": 10.0, "dy": 0.0, "w": 16.0, "h": 16.0},
            "pointer_events": "auto",
            "listener_types": ["click"],
        },
    ]
    assert unique_target_from_descendants(payload) is True


def test_overlay_suffix_is_not_a_unique_target() -> None:
    """Given only input and overlay suffix, When checking unique_target, Then it is false."""

    from billy_mcp.ui_writes.invoices_kunde_descendants import (
        apply_kunde_descendant_dump,
        empty_kunde_descendants,
        unique_target_from_descendants,
    )

    payload = empty_kunde_descendants()
    payload["descendants"] = [
        {
            "tag_category": "input",
            "role": "none",
            "visible": True,
            "interactive": True,
            "class_token_categories": ["text-field"],
            "data_attr_names": [],
            "box": {"dx": 0.0, "dy": 0.0, "w": 210.0, "h": 40.0},
            "pointer_events": "auto",
            "listener_types": ["focus"],
        },
        {
            "tag_category": "div",
            "role": "none",
            "visible": True,
            "interactive": True,
            "class_token_categories": ["other"],
            "data_attr_names": [],
            "box": {"dx": 242.0, "dy": 0.0, "w": 40.0, "h": 40.0},
            "pointer_events": "auto",
            "listener_types": [],
        },
    ]
    assert unique_target_from_descendants(payload) is False
    applied = apply_kunde_descendant_dump(payload)
    assert applied["unique_target"] is False
    assert applied["unique_target_category"] == "none"
    assert applied["code"] == "UI_CHANGED"


def test_handler_guard_classifies_and_discards_source() -> None:
    """Given handler source, When classifying, Then only an allowlisted enum remains."""

    from billy_mcp.ui_writes.invoices_kunde_descendants import (
        classify_handler_source,
        wrapper_handler_guard_from_metadata,
    )

    assert classify_handler_source("function(e){if(e.target.tagName==='INPUT')return;}") == (
        "input_ignored"
    )
    suffix_src = "function(e){if(e.target.classList.contains('suffix'))open();}"
    assert classify_handler_source(suffix_src) == "suffix_accepted"
    assert classify_handler_source("function(){open();}") == "none"
    assert wrapper_handler_guard_from_metadata({"wrapper_handler_guard": "input_ignored"}) == (
        "input_ignored"
    )
    assert wrapper_handler_guard_from_metadata({}) == "none"


def test_descendant_rows_reject_raw_text() -> None:
    """Given a descendant row, When encoded, Then raw names and URLs are absent."""

    from billy_mcp.ui_writes.invoices_kunde_descendants import (
        descendant_dump_json,
        empty_kunde_descendants,
        sanitize_descendant,
    )

    payload = empty_kunde_descendants()
    payload["descendants"] = [
        sanitize_descendant(
            {
                "tag": "INPUT",
                "role": "",
                "visible": True,
                "interactive": True,
                "class_tokens": ["ember-text-field"],
                "data_attr_names": ["data-cy"],
                "dx": 0,
                "dy": 0,
                "w": 210,
                "h": 40,
                "pointer_events": "auto",
                "listener_types": ["keydown"],
            }
        )
    ]
    encoded = descendant_dump_json(payload)
    assert "https://" not in encoded
    assert "mit.billy.dk" not in encoded
    assert "MCP-UI" not in encoded
    assert "function(" not in encoded


def test_delivered_dump_requires_complete_keys(tmp_path: Path) -> None:
    """Given a complete dump file, When checking delivery, Then it is delivered."""

    from billy_mcp.ui_writes.invoices_kunde_descendants import (
        apply_kunde_descendant_dump,
        descendant_dump_is_delivered,
        empty_kunde_descendants,
    )

    missing = tmp_path / "missing.json"
    assert descendant_dump_is_delivered(missing) is False
    path = tmp_path / "delivered.json"
    apply_kunde_descendant_dump(empty_kunde_descendants(), dump_path=path)
    assert descendant_dump_is_delivered(path) is True


def test_capture_is_read_only() -> None:
    """Given the live capture, When reading source, Then it does not click the wrapper."""

    from billy_mcp.ui_writes import invoices_form_bind, invoices_kunde_descendant_inspect

    bind = Path(invoices_form_bind.__file__).read_text(encoding="utf-8")
    start = bind.index("async def capture_kunde_descendants")
    end = bind.index("async def apply_named_control_action")
    body = bind[start:end]
    inspect = Path(invoices_kunde_descendant_inspect.__file__).read_text(encoding="utf-8")
    assert "pickerfield" in inspect
    assert ".click(" not in body
    assert ".click(" not in inspect
    assert "_type_kunde" not in body
    assert "press_sequentially" not in body
    assert "get_by_role" not in body
