"""Given the live Ember dump, When checking fiber keys, Then they are missing."""

from __future__ import annotations

from pathlib import Path
from typing import Final

_LIVE_EMBER: Final[dict[str, object]] = {
    "unique_normal_action": False,
    "property_rows": [],
    "method_name_tokens": [],
}
_REQUIRED: Final[list[str]] = [
    "fiber_key_class",
    "wrapper_fiber_key_class",
    "type_token",
    "prop_rows",
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
    "host_class",
    "unique_fiber_host",
    "unique_normal_action",
    "unique_normal_action_token",
    "kunde_fiber_missing_keys",
]


def test_live_ember_dump_misses_fiber_keys() -> None:
    """Given the current Ember dump, When checking fiber keys, Then they are missing."""

    from billy_mcp.ui_writes.invoices_kunde_fiber import (
        REQUIRED_KUNDE_FIBER_KEYS,
        kunde_fiber_missing_keys,
    )

    missing = kunde_fiber_missing_keys(_LIVE_EMBER)
    assert missing == _REQUIRED
    assert set(_REQUIRED).issubset(REQUIRED_KUNDE_FIBER_KEYS)
    for key in _REQUIRED:
        if key in {"method_name_tokens", "unique_normal_action"}:
            continue
        assert key not in _LIVE_EMBER


def test_complete_fiber_dump_has_no_missing_keys(tmp_path: Path) -> None:
    """Given a filled fiber dump, When checking keys, Then none are missing."""

    from billy_mcp.ui_writes.invoices_kunde_fiber import (
        apply_kunde_fiber_dump,
        empty_kunde_fiber,
        kunde_fiber_missing_keys,
        unique_normal_action_from,
    )

    payload = empty_kunde_fiber()
    assert kunde_fiber_missing_keys(payload) == []
    assert unique_normal_action_from(payload) is False
    applied = apply_kunde_fiber_dump(payload, dump_path=tmp_path / "fiber.json")
    assert applied["unique_normal_action"] is False
    assert applied["code"] == "UI_CHANGED"
    assert (tmp_path / "fiber.json").is_file()


def test_unique_normal_action_needs_action_and_unused_host() -> None:
    """Given one named action without an unused host, When checking, Then it is false."""

    from billy_mcp.ui_writes.invoices_kunde_fiber import (
        apply_kunde_fiber_dump,
        empty_kunde_fiber,
        unique_normal_action_from,
    )

    payload = empty_kunde_fiber()
    payload["method_name_tokens"] = ["onOpen"]
    payload["unique_fiber_host"] = False
    assert unique_normal_action_from(payload) is False
    applied = apply_kunde_fiber_dump(payload)
    assert applied["named_open_action"] == "onOpen"
    assert applied["unique_normal_action"] is False
    assert applied["unique_normal_action_token"] == "none"
    payload["named_open_action"] = "onOpen"
    payload["unique_fiber_host"] = True
    assert unique_normal_action_from(payload) is True
    applied = apply_kunde_fiber_dump(payload)
    assert applied["unique_normal_action"] is True
    assert applied["unique_normal_action_token"] == "onOpen"


def test_fiber_rows_reject_raw_values() -> None:
    """Given a fiber dump, When encoded, Then raw names and URLs are absent."""

    from billy_mcp.ui_writes.invoices_kunde_fiber import (
        empty_kunde_fiber,
        fiber_dump_json,
        sanitize_prop_row,
    )

    payload = empty_kunde_fiber()
    payload["prop_rows"] = [
        sanitize_prop_row(
            {
                "name": "contactId",
                "type": "string",
                "value": "do-not-store",
            }
        )
    ]
    encoded = fiber_dump_json(payload)
    assert "https://" not in encoded
    assert "mit.billy.dk" not in encoded
    assert "MCP-UI" not in encoded
    assert "do-not-store" not in encoded
    assert "__reactFiber$" not in encoded
    assert "ember123" not in encoded


def test_fiber_key_and_type_tokens() -> None:
    """Given internal names, When classifying, Then only allowlisted tokens remain."""

    from billy_mcp.ui_writes.invoices_kunde_fiber import fiber_key_class, type_token

    assert fiber_key_class("__reactFiber$abc") == "react_fiber"
    assert fiber_key_class("__reactInternalInstance$1") == "react_internal"
    assert fiber_key_class("__reactProps$x") == "react_props"
    assert fiber_key_class("id") == "none"
    assert type_token("PickerField") == "picker"
    assert type_token("ContactSelect") == "select"
    assert type_token("") == "none"


def test_delivered_fiber_dump_requires_complete_keys(tmp_path: Path) -> None:
    """Given a complete dump file, When checking delivery, Then it is delivered."""

    from billy_mcp.ui_writes.invoices_kunde_fiber import (
        apply_kunde_fiber_dump,
        empty_kunde_fiber,
        fiber_dump_is_delivered,
    )

    missing = tmp_path / "missing.json"
    assert fiber_dump_is_delivered(missing) is False
    path = tmp_path / "delivered.json"
    apply_kunde_fiber_dump(empty_kunde_fiber(), dump_path=path)
    assert fiber_dump_is_delivered(path) is True


def test_fiber_capture_is_read_only() -> None:
    """Given the live capture, When reading source, Then it does not click or invoke."""

    from billy_mcp.ui_writes import invoices_form_bind, invoices_kunde_fiber_inspect

    bind = Path(invoices_form_bind.__file__).read_text(encoding="utf-8")
    start = bind.index("async def capture_kunde_fiber")
    end = bind.index("async def apply_named_control_action")
    inspect = Path(invoices_kunde_fiber_inspect.__file__).read_text(encoding="utf-8")
    body = bind[start:end]
    assert "Runtime.getProperties" in inspect
    assert "callFunctionOn" not in inspect
    assert "Ember.View" not in inspect
    assert "Ember.get(" not in inspect
    assert ".click(" not in body
    assert ".click(" not in inspect
    assert "_type_kunde" not in body
    assert "press_sequentially" not in body
    assert "get_by_role" not in inspect
