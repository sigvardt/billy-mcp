"""Invoice Kunde listener-contract keys (28C8FBC8).

Never stores source, URLs, locators, ids, or customer values.
"""

from __future__ import annotations

import json
from collections.abc import Mapping
from pathlib import Path
from typing import Final, Literal, cast

from billy_mcp.ui_writes.invoices_form_page import write_json
from billy_mcp.ui_writes.invoices_kunde_control import EVENT_TYPE_TOKENS, event_type_token
from billy_mcp.ui_writes.invoices_kunde_listener_source import (
    ACTION_TOKENS,
    KEY_CATEGORIES,
    PROPERTY_CATEGORIES,
    ActionToken,
    accepted_key_category_from,
    invoked_action_token_from,
    property_categories_from,
)

ListenerKey = Literal[
    "rows",
    "unique_normal_action",
    "unique_normal_action_token",
    "kunde_listener_missing_keys",
]
PhaseToken = Literal["capture", "bubble"]
TargetCategory = Literal["input", "overlay", "pickerfield", "ancestor", "other"]

REQUIRED_KUNDE_LISTENER_KEYS: Final[tuple[ListenerKey, ...]] = (
    "rows",
    "unique_normal_action",
    "unique_normal_action_token",
    "kunde_listener_missing_keys",
)
ROW_KEYS: Final[tuple[str, ...]] = (
    "event_type",
    "phase",
    "target_category",
    "event_property_categories",
    "accepted_key_category",
    "invoked_action_token",
)
PHASE_TOKENS: Final[frozenset[str]] = frozenset({"capture", "bubble"})
TARGET_CATEGORIES: Final[frozenset[str]] = frozenset(
    {"input", "overlay", "pickerfield", "ancestor", "other"}
)
POINTER_TYPES: Final[frozenset[str]] = frozenset(
    {"click", "pointerdown", "pointerup", "mousedown", "mouseup"}
)
KEYBOARD_TYPES: Final[frozenset[str]] = frozenset({"keydown", "keyup"})
ROW_CAP: Final = 16
KUNDE_LISTENER_DUMP: Final = (
    Path.home() / ".local" / "share" / "billy-mcp" / "inspect-live-invoices-kunde-listeners.json"
)


def as_str_map(value: object) -> dict[str, object] | None:
    if not isinstance(value, dict):
        return None
    return cast(dict[str, object], value)


def phase_token(use_capture: object) -> PhaseToken:
    return "capture" if use_capture is True else "bubble"


def target_category_token(raw: object) -> TargetCategory:
    if isinstance(raw, str) and raw in TARGET_CATEGORIES and raw != "other":
        return cast(TargetCategory, raw)
    return "other"


def sanitize_listener_row(raw: Mapping[str, object]) -> dict[str, object]:
    """Allowlisted listener-contract row."""

    properties_raw = raw.get("event_property_categories")
    properties: list[str] = []
    if isinstance(properties_raw, list):
        for item in cast(list[object], properties_raw):
            if isinstance(item, str) and item in PROPERTY_CATEGORIES and item not in properties:
                properties.append(item)
    properties.sort()
    key = raw.get("accepted_key_category")
    action = raw.get("invoked_action_token")
    event_raw = raw.get("event_type")
    event_name = event_raw if isinstance(event_raw, str) else None
    return {
        "event_type": event_type_token(event_name),
        "phase": phase_token(raw.get("phase") == "capture" or raw.get("useCapture") is True),
        "target_category": target_category_token(raw.get("target_category")),
        "event_property_categories": properties,
        "accepted_key_category": key if key in KEY_CATEGORIES else "none",
        "invoked_action_token": action if action in ACTION_TOKENS else "none",
    }


def _row_is_present(value: object) -> bool:
    row = as_str_map(value)
    if row is None or any(key not in row for key in ROW_KEYS):
        return False
    if row.get("event_type") not in EVENT_TYPE_TOKENS:
        return False
    if row.get("phase") not in PHASE_TOKENS:
        return False
    if row.get("target_category") not in TARGET_CATEGORIES:
        return False
    props = row.get("event_property_categories")
    if not isinstance(props, list):
        return False
    for item in cast(list[object], props):
        if not isinstance(item, str) or item not in PROPERTY_CATEGORIES:
            return False
    if row.get("accepted_key_category") not in KEY_CATEGORIES:
        return False
    return row.get("invoked_action_token") in ACTION_TOKENS


def _rows_are_present(value: object) -> bool:
    if not isinstance(value, list):
        return False
    rows = cast(list[object], value)
    if len(rows) > ROW_CAP:
        return False
    return all(_row_is_present(item) for item in rows)


def _key_is_present(payload: Mapping[str, object], key: ListenerKey) -> bool:
    match key:
        case "rows":
            return _rows_are_present(payload.get(key))
        case "unique_normal_action":
            return isinstance(payload.get(key), bool)
        case "unique_normal_action_token":
            return payload.get(key) in ACTION_TOKENS
        case "kunde_listener_missing_keys":
            return isinstance(payload.get(key), list)


def kunde_listener_missing_keys(payload: Mapping[str, object]) -> list[str]:
    """Keys 28C8FBC8 requires that this dump does not record."""

    if "rows" not in payload:
        return list(REQUIRED_KUNDE_LISTENER_KEYS)
    return [key for key in REQUIRED_KUNDE_LISTENER_KEYS if not _key_is_present(payload, key)]


def empty_kunde_listeners() -> dict[str, object]:
    """Structurally complete listener-contract keys before a live inspect."""

    return {
        "rows": [],
        "unique_normal_action": False,
        "unique_normal_action_token": "none",
        "kunde_listener_missing_keys": [],
    }


def _row_is_normal_action(row: Mapping[str, object]) -> bool:
    event_type = row.get("event_type")
    invoke = row.get("invoked_action_token")
    if not isinstance(event_type, str) or invoke not in ACTION_TOKENS or invoke == "none":
        return False
    if event_type in POINTER_TYPES:
        return True
    return event_type in KEYBOARD_TYPES and row.get("accepted_key_category") not in {
        None,
        "none",
    }


def unique_normal_action_from(payload: Mapping[str, object]) -> bool:
    """True only when exactly one pointer or named-key keyboard action is proved."""

    return len(_normal_action_rows(payload)) == 1


def unique_normal_action_token_from(payload: Mapping[str, object]) -> ActionToken:
    rows = _normal_action_rows(payload)
    if len(rows) != 1:
        return "none"
    token = rows[0].get("invoked_action_token")
    if isinstance(token, str) and token in ACTION_TOKENS:
        return cast(ActionToken, token)
    return "none"


def _normal_action_rows(payload: Mapping[str, object]) -> list[Mapping[str, object]]:
    raw = payload.get("rows")
    if not isinstance(raw, list):
        return []
    found: list[Mapping[str, object]] = []
    for item in cast(list[object], raw):
        row = as_str_map(item)
        if row is not None and _row_is_normal_action(row):
            found.append(row)
    return found


def listener_dump_is_delivered(path: Path | None = None) -> bool:
    """True when the owner dump already recorded the listener contract."""

    target = path or KUNDE_LISTENER_DUMP
    if not target.is_file():
        return False
    try:
        raw = json.loads(target.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return False
    payload = as_str_map(raw)
    return payload is not None and kunde_listener_missing_keys(payload) == []


def apply_kunde_listener_dump(
    payload: Mapping[str, object],
    *,
    dump_path: Path | None = None,
) -> dict[str, object]:
    """Copy allowlisted keys and write the owner-only summary."""

    result = empty_kunde_listeners()
    rows: list[dict[str, object]] = []
    raw_rows = payload.get("rows")
    if isinstance(raw_rows, list):
        for item in cast(list[object], raw_rows):
            if len(rows) >= ROW_CAP:
                break
            row = as_str_map(item)
            if row is None:
                continue
            rows.append(sanitize_listener_row(row))
    result["rows"] = rows
    unique = unique_normal_action_from(result)
    result["unique_normal_action"] = unique
    result["unique_normal_action_token"] = unique_normal_action_token_from(result)
    result["kunde_listener_missing_keys"] = kunde_listener_missing_keys(result)
    if not unique:
        result["code"] = "UI_CHANGED"
        result["message"] = "Billy Kunde listener contract has no unique normal action."
    summary = {key: result.get(key) for key in REQUIRED_KUNDE_LISTENER_KEYS}
    if dump_path is not None:
        write_json(dump_path, summary)
    return result


def listener_dump_json(payload: Mapping[str, object]) -> str:
    """Stable JSON for leak checks. Never includes source or URLs."""

    return json.dumps(dict(payload), sort_keys=True)


__all__ = [
    "KUNDE_LISTENER_DUMP",
    "REQUIRED_KUNDE_LISTENER_KEYS",
    "accepted_key_category_from",
    "apply_kunde_listener_dump",
    "as_str_map",
    "empty_kunde_listeners",
    "invoked_action_token_from",
    "kunde_listener_missing_keys",
    "listener_dump_is_delivered",
    "listener_dump_json",
    "phase_token",
    "property_categories_from",
    "sanitize_listener_row",
    "target_category_token",
    "unique_normal_action_from",
]
