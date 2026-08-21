"""Invoice Kunde React fiber keys.

Never stores raw values, ids, fiber suffixes, source, URLs, or customer text.
"""

from __future__ import annotations

import json
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Final, Literal, cast

from billy_mcp.ui_writes.invoices_form_page import write_json

FiberKey = Literal[
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
FiberKeyClass = Literal["react_fiber", "react_internal", "react_props", "none"]
TypeToken = Literal["picker", "select", "combobox", "autocomplete", "contact", "other", "none"]
HostClass = Literal["input", "overlay", "wrapper", "other", "none"]
ValueType = Literal[
    "undefined",
    "null",
    "boolean",
    "number",
    "string",
    "object",
    "array",
    "function",
    "other",
]
SelectionType = Literal["object", "string", "null", "undefined", "none"]
CollectionType = Literal["array", "object", "none"]
LengthClass = Literal["zero", "nonzero", "unknown"]
OpenStateKey = Literal["isOpen", "opened", "expanded", "isExpanded", "isOpened", "none"]
OpenAction = Literal["open", "toggle", "expand", "onOpen", "none"]
SelectAction = Literal["select", "setValue", "set", "choose", "onSelect", "onChange", "none"]
FilterAction = Literal["filter", "search", "query", "none"]
ActionToken = Literal[
    "open",
    "toggle",
    "expand",
    "onOpen",
    "select",
    "setValue",
    "set",
    "choose",
    "onSelect",
    "onChange",
    "filter",
    "search",
    "query",
    "none",
]

REQUIRED_KUNDE_FIBER_KEYS: Final[tuple[FiberKey, ...]] = (
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
)
PROP_ROW_KEYS: Final[tuple[str, ...]] = ("name_token", "value_type")
SELECTION_TOKENS: Final[frozenset[str]] = frozenset(
    {"contact", "contactId", "value", "selection", "selected", "selectedContact", "model"}
)
COLLECTION_TOKENS: Final[frozenset[str]] = frozenset(
    {"content", "contents", "options", "items", "results", "source", "sources"}
)
OPEN_STATE_TOKENS: Final[frozenset[str]] = frozenset(
    {"isOpen", "opened", "expanded", "isExpanded", "isOpened"}
)
NAME_TOKENS: Final[frozenset[str]] = (
    SELECTION_TOKENS | COLLECTION_TOKENS | OPEN_STATE_TOKENS | {"other"}
)
VALUE_TYPES: Final[frozenset[str]] = frozenset(
    {
        "undefined",
        "null",
        "boolean",
        "number",
        "string",
        "object",
        "array",
        "function",
        "other",
    }
)
METHOD_TOKENS: Final[frozenset[str]] = frozenset(
    {
        "open",
        "close",
        "toggle",
        "expand",
        "collapse",
        "select",
        "setValue",
        "set",
        "choose",
        "filter",
        "search",
        "query",
        "onOpen",
        "onSelect",
        "onChange",
    }
)
OPEN_ACTIONS: Final[frozenset[str]] = frozenset({"open", "toggle", "expand", "onOpen"})
SELECT_ACTIONS: Final[frozenset[str]] = frozenset(
    {"select", "setValue", "set", "choose", "onSelect", "onChange"}
)
FILTER_ACTIONS: Final[frozenset[str]] = frozenset({"filter", "search", "query"})
FIBER_KEY_CLASSES: Final[frozenset[str]] = frozenset(
    {"react_fiber", "react_internal", "react_props", "none"}
)
TYPE_TOKENS: Final[frozenset[str]] = frozenset(
    {"picker", "select", "combobox", "autocomplete", "contact", "other", "none"}
)
HOST_CLASSES: Final[frozenset[str]] = frozenset({"input", "overlay", "wrapper", "other", "none"})
SELECTION_TYPES: Final[frozenset[str]] = frozenset(
    {"object", "string", "null", "undefined", "none"}
)
COLLECTION_TYPES: Final[frozenset[str]] = frozenset({"array", "object", "none"})
LENGTH_CLASSES: Final[frozenset[str]] = frozenset({"zero", "nonzero", "unknown"})
OPEN_STATE_KEYS: Final[frozenset[str]] = OPEN_STATE_TOKENS | {"none"}
PROPERTY_CAP: Final = 16
METHOD_CAP: Final = 16
KUNDE_FIBER_DUMP: Final = (
    Path.home() / ".local" / "share" / "billy-mcp" / "inspect-live-invoices-kunde-fiber.json"
)


def as_str_map(value: object) -> dict[str, object] | None:
    if not isinstance(value, dict):
        return None
    return cast(dict[str, object], value)


def name_token(raw: object) -> str:
    if isinstance(raw, str) and raw in NAME_TOKENS and raw != "other":
        return raw
    return "other"


def value_type_token(raw: object, subtype: object = None) -> ValueType:
    if subtype == "array":
        return "array"
    if subtype == "null":
        return "null"
    if raw == "function":
        return "function"
    if isinstance(raw, str) and raw in VALUE_TYPES and raw != "other":
        return cast(ValueType, raw)
    return "other"


def method_token(raw: object) -> str | None:
    if isinstance(raw, str) and raw in METHOD_TOKENS:
        return raw
    return None


def fiber_key_class(raw: object) -> FiberKeyClass:
    if not isinstance(raw, str) or raw == "":
        return "none"
    if raw.startswith("__reactFiber"):
        return "react_fiber"
    if raw.startswith("__reactInternalInstance"):
        return "react_internal"
    if raw.startswith("__reactProps"):
        return "react_props"
    return "none"


def type_token(raw: object) -> TypeToken:
    if not isinstance(raw, str) or raw == "":
        return "none"
    lowered = raw.replace("-", "_").lower()
    if "picker" in lowered:
        return "picker"
    if "combobox" in lowered:
        return "combobox"
    if "autocomplete" in lowered:
        return "autocomplete"
    if "select" in lowered:
        return "select"
    if "contact" in lowered:
        return "contact"
    return "other"


def sanitize_prop_row(raw: Mapping[str, object]) -> dict[str, object]:
    return {
        "name_token": name_token(raw.get("name_token") or raw.get("name")),
        "value_type": value_type_token(
            raw.get("value_type") or raw.get("type"), raw.get("subtype")
        ),
    }


def _prop_rows_are_present(value: object) -> bool:
    if not isinstance(value, list) or len(cast(list[object], value)) > PROPERTY_CAP:
        return False
    for item in cast(list[object], value):
        row = as_str_map(item)
        if row is None or any(key not in row for key in PROP_ROW_KEYS):
            return False
        if row.get("name_token") not in NAME_TOKENS:
            return False
        if row.get("value_type") not in VALUE_TYPES:
            return False
    return True


def _method_tokens_are_present(value: object) -> bool:
    if not isinstance(value, list) or len(cast(list[object], value)) > METHOD_CAP:
        return False
    seen: set[str] = set()
    for item in cast(list[object], value):
        if not isinstance(item, str) or item not in METHOD_TOKENS or item in seen:
            return False
        seen.add(item)
    return True


def _key_is_present(payload: Mapping[str, object], key: FiberKey) -> bool:
    value = payload.get(key)
    match key:
        case "fiber_key_class" | "wrapper_fiber_key_class":
            return value in FIBER_KEY_CLASSES
        case "type_token":
            return value in TYPE_TOKENS
        case "prop_rows":
            return _prop_rows_are_present(value)
        case "method_name_tokens":
            return _method_tokens_are_present(value)
        case "bound_selection_present" | "candidate_collection_present" | "unique_fiber_host":
            return isinstance(value, bool)
        case "bound_selection_type":
            return value in SELECTION_TYPES
        case "candidate_collection_type":
            return value in COLLECTION_TYPES
        case "candidate_length_class":
            return value in LENGTH_CLASSES
        case "open_state_key":
            return value in OPEN_STATE_KEYS
        case "open_state":
            return key in payload and (value is None or isinstance(value, bool))
        case "named_open_action":
            return value in OPEN_ACTIONS or value == "none"
        case "named_select_action":
            return value in SELECT_ACTIONS or value == "none"
        case "named_filter_action":
            return value in FILTER_ACTIONS or value == "none"
        case "host_class":
            return value in HOST_CLASSES
        case "unique_normal_action":
            return isinstance(value, bool)
        case "unique_normal_action_token":
            return (
                value in OPEN_ACTIONS
                or value in SELECT_ACTIONS
                or value in FILTER_ACTIONS
                or value == "none"
            )
        case "kunde_fiber_missing_keys":
            return isinstance(value, list)


def kunde_fiber_missing_keys(payload: Mapping[str, object]) -> list[str]:
    """Keys the fiber inspect requires that this dump does not record."""

    if payload.get("fiber_key_class") not in FIBER_KEY_CLASSES:
        return list(REQUIRED_KUNDE_FIBER_KEYS)
    return [key for key in REQUIRED_KUNDE_FIBER_KEYS if not _key_is_present(payload, key)]


def empty_kunde_fiber() -> dict[str, object]:
    """Structurally complete fiber keys before a live inspect."""

    return {
        "fiber_key_class": "none",
        "wrapper_fiber_key_class": "none",
        "type_token": "none",
        "prop_rows": [],
        "method_name_tokens": [],
        "bound_selection_present": False,
        "bound_selection_type": "none",
        "candidate_collection_present": False,
        "candidate_collection_type": "none",
        "candidate_length_class": "unknown",
        "open_state_key": "none",
        "open_state": None,
        "named_open_action": "none",
        "named_select_action": "none",
        "named_filter_action": "none",
        "host_class": "none",
        "unique_fiber_host": False,
        "unique_normal_action": False,
        "unique_normal_action_token": "none",
        "kunde_fiber_missing_keys": [],
    }


def named_action_tokens(payload: Mapping[str, object]) -> list[str]:
    tokens: list[str] = []
    for key in ("named_open_action", "named_select_action", "named_filter_action"):
        value = payload.get(key)
        if isinstance(value, str) and value != "none":
            tokens.append(value)
    return tokens


def unique_normal_action_from(payload: Mapping[str, object]) -> bool:
    """True only with one named action and one unused fiber host."""

    tokens = named_action_tokens(payload)
    if len(tokens) != 1:
        return False
    return payload.get("unique_fiber_host") is True


def unique_normal_action_token_from(payload: Mapping[str, object]) -> ActionToken:
    if not unique_normal_action_from(payload):
        return "none"
    token = named_action_tokens(payload)[0]
    if token in OPEN_ACTIONS or token in SELECT_ACTIONS or token in FILTER_ACTIONS:
        return cast(ActionToken, token)
    return "none"


def derive_named_actions(methods: Sequence[str]) -> dict[str, str]:
    open_hit = next((item for item in methods if item in OPEN_ACTIONS), "none")
    select_hit = next((item for item in methods if item in SELECT_ACTIONS), "none")
    filter_hit = next((item for item in methods if item in FILTER_ACTIONS), "none")
    return {
        "named_open_action": open_hit,
        "named_select_action": select_hit,
        "named_filter_action": filter_hit,
    }


def derive_selection(rows: Sequence[Mapping[str, object]]) -> tuple[bool, SelectionType]:
    for row in rows:
        if row.get("name_token") not in SELECTION_TOKENS:
            continue
        raw = row.get("value_type")
        if raw in SELECTION_TYPES and raw != "none":
            return True, cast(SelectionType, raw)
        return True, "none"
    return False, "none"


def derive_collection(
    rows: Sequence[Mapping[str, object]], length_class: object
) -> tuple[bool, CollectionType, LengthClass]:
    length: LengthClass = (
        cast(LengthClass, length_class) if length_class in LENGTH_CLASSES else "unknown"
    )
    for row in rows:
        if row.get("name_token") not in COLLECTION_TOKENS:
            continue
        raw = row.get("value_type")
        if raw in COLLECTION_TYPES and raw != "none":
            return True, cast(CollectionType, raw), length
        return True, "none", length
    return False, "none", "unknown"


def derive_open_state(
    rows: Sequence[Mapping[str, object]], open_state: object
) -> tuple[OpenStateKey, bool | None]:
    state = open_state if isinstance(open_state, bool) else None
    for row in rows:
        token = row.get("name_token")
        if token not in OPEN_STATE_TOKENS:
            continue
        return cast(OpenStateKey, token), state
    return "none", None


def fiber_dump_is_delivered(path: Path | None = None) -> bool:
    """True when the owner dump already recorded the fiber inspect."""

    target = path or KUNDE_FIBER_DUMP
    if not target.is_file():
        return False
    try:
        raw = json.loads(target.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return False
    payload = as_str_map(raw)
    return payload is not None and kunde_fiber_missing_keys(payload) == []


def apply_kunde_fiber_dump(
    payload: Mapping[str, object],
    *,
    dump_path: Path | None = None,
) -> dict[str, object]:
    """Copy allowlisted keys and write the owner-only summary."""

    result = empty_kunde_fiber()
    for key in REQUIRED_KUNDE_FIBER_KEYS:
        if key in payload and key != "kunde_fiber_missing_keys":
            result[key] = payload[key]
    rows_raw = result.get("prop_rows")
    rows: list[dict[str, object]] = []
    if isinstance(rows_raw, list):
        for item in cast(list[object], rows_raw):
            if len(rows) >= PROPERTY_CAP:
                break
            row = as_str_map(item)
            if row is None:
                continue
            rows.append(sanitize_prop_row(row))
    result["prop_rows"] = rows
    methods_raw = result.get("method_name_tokens")
    methods: list[str] = []
    if isinstance(methods_raw, list):
        for item in cast(list[object], methods_raw):
            token = method_token(item)
            if token is None or token in methods:
                continue
            methods.append(token)
            if len(methods) >= METHOD_CAP:
                break
    methods.sort()
    result["method_name_tokens"] = methods
    actions = derive_named_actions(methods)
    if result.get("named_open_action") == "none":
        result["named_open_action"] = actions["named_open_action"]
    if result.get("named_select_action") == "none":
        result["named_select_action"] = actions["named_select_action"]
    if result.get("named_filter_action") == "none":
        result["named_filter_action"] = actions["named_filter_action"]
    present, selection_type = derive_selection(rows)
    if result.get("bound_selection_present") is False:
        result["bound_selection_present"] = present
        result["bound_selection_type"] = selection_type
    collection_present, collection_type, length = derive_collection(
        rows, result.get("candidate_length_class")
    )
    if result.get("candidate_collection_present") is False:
        result["candidate_collection_present"] = collection_present
        result["candidate_collection_type"] = collection_type
        result["candidate_length_class"] = length
    open_key, open_state = derive_open_state(rows, result.get("open_state"))
    if result.get("open_state_key") == "none":
        result["open_state_key"] = open_key
        result["open_state"] = open_state
    if result.get("fiber_key_class") not in FIBER_KEY_CLASSES:
        result["fiber_key_class"] = "none"
    if result.get("wrapper_fiber_key_class") not in FIBER_KEY_CLASSES:
        result["wrapper_fiber_key_class"] = "none"
    if result.get("type_token") not in TYPE_TOKENS:
        result["type_token"] = "none"
    if result.get("host_class") not in HOST_CLASSES:
        result["host_class"] = "none"
    result["unique_fiber_host"] = result.get("unique_fiber_host") is True
    unique = unique_normal_action_from(result)
    result["unique_normal_action"] = unique
    result["unique_normal_action_token"] = unique_normal_action_token_from(result)
    result["kunde_fiber_missing_keys"] = kunde_fiber_missing_keys(result)
    if not unique:
        result["code"] = "UI_CHANGED"
        result["message"] = "Billy Kunde fiber inspect has no unique normal action."
    summary = {key: result.get(key) for key in REQUIRED_KUNDE_FIBER_KEYS}
    if dump_path is not None:
        write_json(dump_path, summary)
    return result


def fiber_dump_json(payload: Mapping[str, object]) -> str:
    """Stable JSON for leak checks. Never includes source or URLs."""

    return json.dumps(dict(payload), sort_keys=True)


__all__ = [
    "KUNDE_FIBER_DUMP",
    "REQUIRED_KUNDE_FIBER_KEYS",
    "apply_kunde_fiber_dump",
    "empty_kunde_fiber",
    "fiber_dump_is_delivered",
    "fiber_dump_json",
    "fiber_key_class",
    "kunde_fiber_missing_keys",
    "method_token",
    "name_token",
    "sanitize_prop_row",
    "type_token",
    "unique_normal_action_from",
    "value_type_token",
]
