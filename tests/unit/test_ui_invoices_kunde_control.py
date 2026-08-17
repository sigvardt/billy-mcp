"""Given the live opener dump, When checking control keys, Then 452E0773 fields are missing."""

from __future__ import annotations

from pathlib import Path
from typing import Final

_LIVE_OPENER: Final[dict[str, object]] = {
    "smallest_wrapper": {
        "tag": "DIV",
        "class_tokens": ["ember-view"],
        "contact_input_count": 1,
        "child_input_count": 1,
    },
    "named_opener": None,
}
_REQUIRED: Final[list[str]] = [
    "input_listener_types",
    "wrapper_listener_types",
    "input_listeners",
    "wrapper_listeners",
    "wrapper_data_attr_names",
    "wrapper_class_tokens",
    "binding_script",
    "named_next_action",
    "named_next_action_token",
]


def test_live_opener_misses_452e0773_control_keys() -> None:
    """Given the current live opener, When checking control keys, Then they are missing."""

    from billy_mcp.ui_writes.invoices_kunde_control import (
        REQUIRED_KUNDE_CONTROL_KEYS,
        kunde_control_missing_keys,
    )

    missing = kunde_control_missing_keys(_LIVE_OPENER)
    assert missing == _REQUIRED
    assert set(_REQUIRED).issubset(REQUIRED_KUNDE_CONTROL_KEYS)
    for key in _REQUIRED:
        assert key not in _LIVE_OPENER


def test_complete_control_has_no_missing_keys(tmp_path: Path) -> None:
    """Given a filled control dump, When checking keys, Then none are missing."""

    from billy_mcp.ui_writes.invoices_kunde_control import (
        apply_kunde_control_dump,
        binding_token_class,
        empty_kunde_control,
        event_type_token,
        kunde_control_missing_keys,
        named_next_action_from_control,
        sanitize_script_basename,
        script_hash_for,
    )

    payload = empty_kunde_control()
    assert kunde_control_missing_keys(payload) == []
    assert event_type_token("click") == "click"
    assert event_type_token("weird") == "other"
    assert sanitize_script_basename("https://mit.billy.dk/assets/app.abcdef12.js?x=1") == (
        "app.:id.js"
    )
    assert sanitize_script_basename("https://mit.billy.dk/org/invoices/new") == "inline"
    assert sanitize_script_basename("") == "inline"
    digest = script_hash_for("app.:id.js")
    assert len(digest) == 16
    assert all(char in "0123456789abcdef" for char in digest)
    assert binding_token_class("input[name=contact]") == "name_selector"
    assert binding_token_class('name:"contact"') == "name_quoted_contact"
    assert binding_token_class("name=contact") == "name_eq_contact"
    assert binding_token_class("contactId: x") == "contact_id"
    assert binding_token_class("unrelated") == "none"
    named, token = named_next_action_from_control(payload)
    assert named is False
    assert token == "none"
    click_open = empty_kunde_control()
    click_open["input_listener_types"] = ["click"]
    click_open["binding_script"] = {
        "basename": "app.js",
        "hash": "0123456789abcdef",
        "line": 1,
        "column": 0,
        "token_class": "name_selector",
    }
    named, token = named_next_action_from_control(click_open)
    assert named is True
    assert token == "click_open"
    applied = apply_kunde_control_dump(click_open, dump_path=tmp_path / "control.json")
    assert applied["named_next_action"] is True
    assert "http" not in str(applied)
    assert "contactId: x" not in str(applied)
    assert (tmp_path / "control.json").is_file()


def test_control_rows_reject_urls_and_source() -> None:
    """Given a listener row, When encoded, Then URLs and source text are absent."""

    from billy_mcp.ui_writes.invoices_kunde_control import (
        control_dump_json,
        empty_kunde_control,
    )

    payload = empty_kunde_control()
    payload["input_listeners"] = [
        {
            "type": "click",
            "capture": False,
            "script_basename": "app.:id.js",
            "script_hash": "0123456789abcdef",
            "line": 10,
            "column": 2,
        }
    ]
    payload["input_listener_types"] = ["click"]
    encoded = control_dump_json(payload)
    assert "https://" not in encoded
    assert "mit.billy.dk" not in encoded
    assert "function" not in encoded
    assert "MCP-UI" not in encoded


def test_live_shaped_wrapper_click_is_click_open() -> None:
    """Given the recaptured listener shape, When classifying, Then the action is click_open."""

    from billy_mcp.ui_writes.invoices_kunde_control import (
        empty_kunde_control,
        named_next_action_from_control,
    )

    payload = empty_kunde_control()
    payload["input_listener_types"] = ["keydown", "focus", "blur", "other", "mouseup"]
    payload["wrapper_listener_types"] = ["other", "click"]
    payload["binding_script"] = {
        "basename": "react-web-components.:id.js",
        "hash": "0123456789abcdef",
        "line": 3,
        "column": 0,
        "token_class": "name_quoted_contact",
    }
    named, token = named_next_action_from_control(payload)
    assert named is True
    assert token == "click_open"


def test_control_capture_does_not_type_or_click() -> None:
    """Given the bind capture, When reading source, Then it does not type or click."""

    from billy_mcp.ui_writes import invoices_form_bind

    source = Path(invoices_form_bind.__file__).read_text(encoding="utf-8")
    start = source.index("async def capture_kunde_control_contract")
    end = source.index("async def capture_kunde_widget_dump")
    body = source[start:end]
    assert "_type_kunde" not in body
    assert "mouse.click" not in body
    assert "press_sequentially" not in body
    assert "inspect_kunde_control" in body


def test_named_action_clicks_pickerfield_not_overlay() -> None:
    """Given click_open, When reading the action helper, Then it targets pickerfield."""

    from billy_mcp.ui_writes import invoices_form_bind

    source = Path(invoices_form_bind.__file__).read_text(encoding="utf-8")
    start = source.index("async def apply_named_control_action")
    end = source.index("async def capture_kunde_widget_dump")
    body = source[start:end]
    assert "pickerfield" in body
    assert "307" not in body
    assert "press_sequentially" not in body
    assert "_type_kunde" not in body
