"""Sanitized Kunde pickerfield descendant rows (E87B6AEF)."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Final, Literal, cast

from billy_mcp.ui_writes.invoices_kunde_control import EVENT_TYPE_TOKENS

TagCategory = Literal["input", "div", "button", "span", "svg", "other"]
RoleToken = Literal["option", "listbox", "listitem", "button", "link", "none", "other"]
GuardToken = Literal["input_ignored", "suffix_accepted", "toggle_accepted", "none"]
TargetCategory = Literal["input", "suffix", "toggle", "none"]
PointerToken = Literal["auto", "none", "other"]

TAG_CATEGORIES: Final[frozenset[str]] = frozenset(
    {"input", "div", "button", "span", "svg", "other"}
)
ROLE_TOKENS: Final[frozenset[str]] = frozenset(
    {"option", "listbox", "listitem", "button", "link", "none", "other"}
)
CLASS_CATEGORIES: Final[frozenset[str]] = frozenset(
    {"pickerfield", "ember-view", "text-field", "suffix", "toggle", "other"}
)
GUARD_TOKENS: Final[frozenset[str]] = frozenset(
    {"input_ignored", "suffix_accepted", "toggle_accepted", "none"}
)
TARGET_CATEGORIES: Final[frozenset[str]] = frozenset({"input", "suffix", "toggle", "none"})
POINTER_TOKENS: Final[frozenset[str]] = frozenset({"auto", "none", "other"})
DESCENDANT_ROW_KEYS: Final[tuple[str, ...]] = (
    "tag_category",
    "role",
    "visible",
    "interactive",
    "class_token_categories",
    "data_attr_names",
    "box",
    "pointer_events",
    "listener_types",
)
DESCENDANT_CAP: Final = 16
OVERLAY_MIN_DX: Final = 200.0
OVERLAY_BOX_MIN: Final = 30.0
OVERLAY_BOX_MAX: Final = 50.0


def as_str_map(value: object) -> dict[str, object] | None:
    if not isinstance(value, dict):
        return None
    return cast(dict[str, object], value)


def _tag_category(raw: object) -> TagCategory:
    if not isinstance(raw, str) or raw == "":
        return "other"
    lowered = raw.lower()
    if lowered in TAG_CATEGORIES and lowered != "other":
        return cast(TagCategory, lowered)
    return "other"


def _role_token(raw: object) -> RoleToken:
    if not isinstance(raw, str) or raw == "":
        return "none"
    lowered = raw.lower()
    if lowered in ROLE_TOKENS:
        return cast(RoleToken, lowered)
    return "other"


def _pointer_token(raw: object) -> PointerToken:
    if not isinstance(raw, str) or raw == "":
        return "other"
    lowered = raw.lower()
    if lowered in POINTER_TOKENS:
        return cast(PointerToken, lowered)
    return "other"


def _categories(raw: object) -> list[str]:
    tokens: list[str] = []
    source: Sequence[object] = (
        raw.split()
        if isinstance(raw, str)
        else (cast(list[object], raw) if isinstance(raw, list) else [])
    )
    for item in source:
        if not isinstance(item, str) or item == "":
            continue
        matched = "other"
        lowered = item.lower()
        for allowed in sorted(CLASS_CATEGORIES):
            if allowed != "other" and allowed in lowered:
                matched = allowed
                break
        if matched not in tokens:
            tokens.append(matched)
    tokens.sort()
    return tokens


def _box_of(
    raw_dx: object, raw_dy: object, raw_w: object, raw_h: object
) -> dict[str, float] | None:
    values = (raw_dx, raw_dy, raw_w, raw_h)
    if not all(isinstance(item, (int, float)) for item in values):
        return None
    width = round(float(cast(float, raw_w)), 1)
    height = round(float(cast(float, raw_h)), 1)
    if width <= 0 or height <= 0:
        return None
    return {
        "dx": round(float(cast(float, raw_dx)), 1),
        "dy": round(float(cast(float, raw_dy)), 1),
        "w": width,
        "h": height,
    }


def _listener_types(raw: object) -> list[str]:
    if not isinstance(raw, list):
        return []
    tokens: list[str] = []
    for item in cast(list[object], raw):
        if not isinstance(item, str) or item == "":
            continue
        token = item if item in EVENT_TYPE_TOKENS else "other"
        if token not in tokens:
            tokens.append(token)
    tokens.sort()
    return tokens


def is_overlay_geometry(box: object) -> bool:
    row = as_str_map(cast(dict[str, object], box)) if isinstance(box, dict) else None
    if row is None:
        return False
    dx = row.get("dx")
    width = row.get("w")
    height = row.get("h")
    if not isinstance(dx, (int, float)) or not isinstance(width, (int, float)):
        return False
    if not isinstance(height, (int, float)) or float(dx) < OVERLAY_MIN_DX:
        return False
    return OVERLAY_BOX_MIN <= float(width) <= OVERLAY_BOX_MAX and (
        OVERLAY_BOX_MIN <= float(height) <= OVERLAY_BOX_MAX
    )


def row_target_category(row: Mapping[str, object]) -> TargetCategory:
    """Map one sanitized descendant to input, suffix, toggle, or none."""

    if row.get("tag_category") == "input":
        return "input"
    categories = row.get("class_token_categories")
    tokens: set[object] = set()
    if isinstance(categories, list):
        tokens = {item for item in cast(list[object], categories)}
    if "toggle" in tokens or row.get("role") == "button" or row.get("tag_category") == "button":
        return "toggle"
    if "suffix" in tokens or is_overlay_geometry(row.get("box")):
        return "suffix"
    return "none"


def sanitize_descendant(raw: Mapping[str, object]) -> dict[str, object]:
    """Allowlisted descendant row. Drops text and attribute values."""

    data_names: list[str] = []
    raw_names = raw.get("data_attr_names")
    if isinstance(raw_names, list):
        for item in cast(list[object], raw_names):
            if isinstance(item, str) and item.startswith("data-"):
                data_names.append(item)
    tag_raw = raw.get("tag_category")
    if not isinstance(tag_raw, str) or tag_raw == "":
        tag_raw = raw.get("tag")
    return {
        "tag_category": _tag_category(tag_raw),
        "role": _role_token(raw.get("role")),
        "visible": raw.get("visible") is True,
        "interactive": raw.get("interactive") is True,
        "class_token_categories": _categories(
            raw.get("class_tokens") or raw.get("class_token_categories")
        ),
        "data_attr_names": data_names,
        "box": _box_of(raw.get("dx"), raw.get("dy"), raw.get("w"), raw.get("h"))
        if "dx" in raw
        else as_str_map(raw.get("box")),
        "pointer_events": _pointer_token(raw.get("pointer_events")),
        "listener_types": _listener_types(raw.get("listener_types")),
    }


def row_is_present(value: object) -> bool:
    row = as_str_map(value)
    if row is None or any(key not in row for key in DESCENDANT_ROW_KEYS):
        return False
    if row.get("tag_category") not in TAG_CATEGORIES or row.get("role") not in ROLE_TOKENS:
        return False
    if not isinstance(row.get("visible"), bool) or not isinstance(row.get("interactive"), bool):
        return False
    if row.get("pointer_events") not in POINTER_TOKENS:
        return False
    categories = row.get("class_token_categories")
    names = row.get("data_attr_names")
    types = row.get("listener_types")
    if not isinstance(categories, list) or not isinstance(names, list):
        return False
    if not isinstance(types, list):
        return False
    for item in cast(list[object], categories):
        if isinstance(item, str) and item not in CLASS_CATEGORIES:
            return False
    for item in cast(list[object], types):
        if isinstance(item, str) and item not in EVENT_TYPE_TOKENS:
            return False
    box = row.get("box")
    return box is None or as_str_map(box) is not None


def unused_descendants(rows: Sequence[Mapping[str, object]]) -> list[dict[str, object]]:
    """Visible interactive descendants that are not the input or overlay suffix."""

    unused: list[dict[str, object]] = []
    for item in rows:
        row = dict(item)
        if row.get("visible") is not True or row.get("interactive") is not True:
            continue
        if row_target_category(row) in {"input", "suffix"}:
            continue
        unused.append(row)
    return unused


def unique_target_from_descendants(payload: Mapping[str, object]) -> bool:
    """True only when exactly one unused interactive descendant remains."""

    rows_raw = payload.get("descendants")
    if not isinstance(rows_raw, list):
        return False
    typed = [row for item in cast(list[object], rows_raw) if (row := as_str_map(item)) is not None]
    unused = unused_descendants(typed)
    return len(unused) == 1 and row_target_category(unused[0]) == "toggle"


def wrapper_handler_guard_from_metadata(payload: Mapping[str, object]) -> GuardToken:
    """Return only an allowlisted guard enum. Never reads source text."""

    raw = payload.get("wrapper_handler_guard")
    if isinstance(raw, str) and raw in GUARD_TOKENS:
        return cast(GuardToken, raw)
    return "none"


def classify_handler_source(source: str) -> GuardToken:
    """Classify already-loaded handler text. Caller must discard the source."""

    text = source.lower()
    has_target = "event.target" in text or "e.target" in text
    if not has_target:
        return "none"
    if "toggle" in text:
        return "toggle_accepted"
    if "suffix" in text or "chevron" in text or "caret" in text:
        return "suffix_accepted"
    if "input" in text or "contact" in text:
        return "input_ignored"
    return "none"
