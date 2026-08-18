"""Given the live control dump, When checking listener keys, Then they are missing."""

from __future__ import annotations

from pathlib import Path
from typing import Final

_LIVE_CONTROL: Final[dict[str, object]] = {
    "named_next_action": True,
    "named_next_action_token": "click_open",
    "input_listener_types": ["keydown", "focus", "blur", "other", "mouseup"],
    "wrapper_listener_types": ["other", "click"],
    "input_listeners": [
        {
            "type": "keydown",
            "capture": False,
            "script_basename": "legacy-core.:id.js",
            "script_hash": "3776c0cf93c331da",
            "line": 1,
            "column": 1193255,
        }
    ],
    "wrapper_listeners": [
        {
            "type": "click",
            "capture": False,
            "script_basename": "legacy-core.:id.js",
            "script_hash": "3776c0cf93c331da",
            "line": 1,
            "column": 1193255,
        }
    ],
}
_REQUIRED: Final[list[str]] = [
    "rows",
    "unique_normal_action",
    "unique_normal_action_token",
    "kunde_listener_missing_keys",
]


def test_live_control_dump_misses_listener_keys() -> None:
    """Given the current control dump, When checking listener keys, Then they are missing."""

    from billy_mcp.ui_writes.invoices_kunde_listeners import (
        REQUIRED_KUNDE_LISTENER_KEYS,
        kunde_listener_missing_keys,
    )

    missing = kunde_listener_missing_keys(_LIVE_CONTROL)
    assert missing == _REQUIRED
    assert set(_REQUIRED).issubset(REQUIRED_KUNDE_LISTENER_KEYS)
    for key in _REQUIRED:
        assert key not in _LIVE_CONTROL


def test_complete_listener_dump_has_no_missing_keys(tmp_path: Path) -> None:
    """Given a filled listener dump, When checking keys, Then none are missing."""

    from billy_mcp.ui_writes.invoices_kunde_listeners import (
        apply_kunde_listener_dump,
        empty_kunde_listeners,
        kunde_listener_missing_keys,
        unique_normal_action_from,
    )

    payload = empty_kunde_listeners()
    assert kunde_listener_missing_keys(payload) == []
    assert unique_normal_action_from(payload) is False
    applied = apply_kunde_listener_dump(payload, dump_path=tmp_path / "listeners.json")
    assert applied["unique_normal_action"] is False
    assert applied["code"] == "UI_CHANGED"
    assert (tmp_path / "listeners.json").is_file()


def test_unique_normal_action_needs_named_invoke() -> None:
    """Given a click without a named invoke, When checking, Then it is not unique."""

    from billy_mcp.ui_writes.invoices_kunde_listeners import (
        apply_kunde_listener_dump,
        empty_kunde_listeners,
        unique_normal_action_from,
    )

    payload = empty_kunde_listeners()
    payload["rows"] = [
        {
            "event_type": "click",
            "phase": "bubble",
            "target_category": "pickerfield",
            "event_property_categories": [],
            "accepted_key_category": "none",
            "invoked_action_token": "none",
        }
    ]
    assert unique_normal_action_from(payload) is False
    applied = apply_kunde_listener_dump(payload)
    assert applied["unique_normal_action"] is False
    assert applied["unique_normal_action_token"] == "none"
    payload["rows"] = [
        {
            "event_type": "click",
            "phase": "bubble",
            "target_category": "pickerfield",
            "event_property_categories": ["target"],
            "accepted_key_category": "none",
            "invoked_action_token": "open",
        }
    ]
    assert unique_normal_action_from(payload) is True
    applied = apply_kunde_listener_dump(payload)
    assert applied["unique_normal_action"] is True
    assert applied["unique_normal_action_token"] == "open"


def test_source_classifiers_use_explicit_tokens_only() -> None:
    """Given a source window, When classifying, Then only explicit tokens remain."""

    from billy_mcp.ui_writes.invoices_kunde_listeners import (
        accepted_key_category_from,
        invoked_action_token_from,
        property_categories_from,
    )

    window = "if (event.key === 'Enter') { this.open(); event.preventDefault(); }"
    assert "key" in property_categories_from(window)
    assert "prevent" in property_categories_from(window)
    assert accepted_key_category_from(window) == "enter"
    assert invoked_action_token_from(window) == "open"
    assert accepted_key_category_from("no keys here") == "none"
    assert invoked_action_token_from("addEventListener('click', fn)") == "none"


def test_listener_rows_reject_raw_values() -> None:
    """Given a listener dump, When encoded, Then source and URLs are absent."""

    from billy_mcp.ui_writes.invoices_kunde_listeners import (
        empty_kunde_listeners,
        listener_dump_json,
        sanitize_listener_row,
    )

    payload = empty_kunde_listeners()
    payload["rows"] = [
        sanitize_listener_row(
            {
                "event_type": "click",
                "phase": "bubble",
                "target_category": "input",
                "event_property_categories": ["key"],
                "accepted_key_category": "enter",
                "invoked_action_token": "open",
                "script_url": "https://mit.billy.dk/do-not-store.js",
            }
        )
    ]
    encoded = listener_dump_json(payload)
    assert "https://" not in encoded
    assert "mit.billy.dk" not in encoded
    assert "do-not-store" not in encoded
    assert "function(" not in encoded


def test_delivered_listener_dump_requires_complete_keys(tmp_path: Path) -> None:
    """Given a complete dump file, When checking delivery, Then it is delivered."""

    from billy_mcp.ui_writes.invoices_kunde_listeners import (
        apply_kunde_listener_dump,
        empty_kunde_listeners,
        listener_dump_is_delivered,
    )

    missing = tmp_path / "missing.json"
    assert listener_dump_is_delivered(missing) is False
    path = tmp_path / "delivered.json"
    apply_kunde_listener_dump(empty_kunde_listeners(), dump_path=path)
    assert listener_dump_is_delivered(path) is True


def test_listener_capture_is_read_only() -> None:
    """Given the live capture, When reading source, Then it does not click or invoke."""

    from billy_mcp.ui_writes import invoices_form_bind, invoices_kunde_listener_inspect

    bind = Path(invoices_form_bind.__file__).read_text(encoding="utf-8")
    start = bind.index("async def capture_kunde_listeners")
    end = bind.index("async def apply_named_control_action")
    inspect = Path(invoices_kunde_listener_inspect.__file__).read_text(encoding="utf-8")
    body = bind[start:end]
    assert "DOMDebugger.getEventListeners" in inspect
    assert "depth" not in inspect
    assert "pierce" not in inspect
    assert "callFunctionOn" not in inspect
    assert "Ember.View" not in inspect
    assert "__reactFiber" not in inspect
    assert ".click(" not in body
    assert ".click(" not in inspect
    assert "_type_kunde" not in body
    assert "press_sequentially" not in body
    assert "get_by_role" not in inspect
