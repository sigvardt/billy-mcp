"""Given the live control dump, When checking post-click keys, Then 07600147 fields are missing."""

from __future__ import annotations

from pathlib import Path
from typing import Final

_LIVE_CONTROL: Final[dict[str, object]] = {
    "named_next_action_token": "click_open",
    "action_option_role_count": 0,
}
_REQUIRED: Final[list[str]] = [
    "baseline_input_tag",
    "baseline_wrapper_class_categories",
    "baseline_hidden_subtree_count",
    "click_target",
    "click_count",
    "changed_node_count",
    "changed_nodes",
    "exact_match_count",
    "exact_match_target",
    "kunde_post_click_missing_keys",
]


def test_live_control_misses_07600147_post_click_keys() -> None:
    """Given the current control dump, When checking post-click keys, Then they are missing."""

    from billy_mcp.ui_writes.invoices_kunde_post_click import (
        REQUIRED_KUNDE_POST_CLICK_KEYS,
        kunde_post_click_missing_keys,
    )

    missing = kunde_post_click_missing_keys(_LIVE_CONTROL)
    assert missing == _REQUIRED
    assert set(_REQUIRED).issubset(REQUIRED_KUNDE_POST_CLICK_KEYS)
    for key in _REQUIRED:
        assert key not in _LIVE_CONTROL


def test_complete_post_click_has_no_missing_keys(tmp_path: Path) -> None:
    """Given a filled post-click dump, When checking keys, Then none are missing."""

    from billy_mcp.ui_writes.invoices_kunde_post_click import (
        apply_kunde_post_click_dump,
        empty_kunde_post_click,
        exact_match_target_from_post_click,
        kunde_post_click_missing_keys,
        text_hash_for,
    )

    payload = empty_kunde_post_click()
    assert kunde_post_click_missing_keys(payload) == []
    digest = text_hash_for("MCP-UI-INV-DEADBEEF")
    assert len(digest) == 16
    assert all(char in "0123456789abcdef" for char in digest)
    named = exact_match_target_from_post_click(payload)
    assert named is False
    match_one = empty_kunde_post_click()
    match_one["changed_node_count"] = 1
    match_one["exact_match_count"] = 1
    match_one["changed_nodes"] = [
        {
            "tag": "DIV",
            "role": "option",
            "visible": True,
            "interactive": True,
            "class_token_categories": ["option"],
            "data_attr_names": [],
            "text_len": 19,
            "text_hash": digest,
            "text_exact_match": True,
            "box": {"w": 10.0, "h": 10.0},
            "z_index": "auto",
            "ownership_path": [{"tag": "DIV", "role": "listbox"}],
            "ax_name_hash": digest,
            "ax_name_exact_match": True,
        }
    ]
    assert exact_match_target_from_post_click(match_one) is True
    applied = apply_kunde_post_click_dump(match_one, dump_path=tmp_path / "post-click.json")
    assert applied["exact_match_target"] is True
    assert "MCP-UI" not in str(applied)
    assert (tmp_path / "post-click.json").is_file()


def test_post_click_rows_reject_raw_text() -> None:
    """Given a changed node, When encoded, Then raw names and URLs are absent."""

    from billy_mcp.ui_writes.invoices_kunde_post_click import (
        empty_kunde_post_click,
        post_click_dump_json,
    )

    payload = empty_kunde_post_click()
    payload["changed_nodes"] = [
        {
            "tag": "DIV",
            "role": "none",
            "visible": True,
            "interactive": False,
            "class_token_categories": ["other"],
            "data_attr_names": ["data-cy"],
            "text_len": 0,
            "text_hash": "",
            "text_exact_match": False,
            "box": None,
            "z_index": "auto",
            "ownership_path": [],
            "ax_name_hash": "",
            "ax_name_exact_match": False,
        }
    ]
    encoded = post_click_dump_json(payload)
    assert "https://" not in encoded
    assert "mit.billy.dk" not in encoded
    assert "MCP-UI" not in encoded


def test_delivered_dump_requires_one_wrapper_click(tmp_path: Path) -> None:
    """Given a complete dump, When click_count is 1, Then it is delivered."""

    from billy_mcp.ui_writes.invoices_kunde_post_click import (
        apply_kunde_post_click_dump,
        empty_kunde_post_click,
        post_click_dump_is_delivered,
    )

    missing = tmp_path / "missing.json"
    assert post_click_dump_is_delivered(missing) is False
    empty_path = tmp_path / "empty.json"
    apply_kunde_post_click_dump(empty_kunde_post_click(), dump_path=empty_path)
    assert post_click_dump_is_delivered(empty_path) is False
    clicked = empty_kunde_post_click()
    clicked["click_count"] = 1
    clicked_path = tmp_path / "clicked.json"
    apply_kunde_post_click_dump(clicked, dump_path=clicked_path)
    assert post_click_dump_is_delivered(clicked_path) is True


def test_live_shaped_zero_changed_nodes_is_ui_changed() -> None:
    """Given the recaptured post-click dump, When no node matches, Then UI_CHANGED."""

    from billy_mcp.ui_writes.invoices_kunde_post_click import (
        apply_kunde_post_click_dump,
        empty_kunde_post_click,
        exact_match_target_from_post_click,
    )

    payload = empty_kunde_post_click()
    payload["baseline_wrapper_class_categories"] = [
        "ember-view",
        "other",
        "pickerfield",
        "super-field",
        "text-field",
    ]
    payload["baseline_hidden_subtree_count"] = 2
    payload["click_count"] = 1
    applied = apply_kunde_post_click_dump(payload)
    assert applied["exact_match_count"] == 0
    assert applied["exact_match_target"] is False
    assert exact_match_target_from_post_click(applied) is False
    assert applied["code"] == "UI_CHANGED"


def test_capture_clicks_pickerfield_once() -> None:
    """Given the live capture, When reading source, Then it clicks pickerfield once."""

    from billy_mcp.ui_writes import invoices_form_bind

    source = Path(invoices_form_bind.__file__).read_text(encoding="utf-8")
    start = source.index("async def capture_kunde_post_click")
    end = source.index("async def capture_kunde_widget_dump")
    body = source[start:end]
    assert "pickerfield" in body
    assert "_type_kunde" not in body
    assert "press_sequentially" not in body
    assert 'get_by_role("option")' not in body
    assert "MutationObserver" in body or "mutation" in body.lower()
