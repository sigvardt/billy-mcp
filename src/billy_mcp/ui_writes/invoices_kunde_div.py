"""Invoice Kunde right-edge DIV ownership flags (9F777B8F). Never stores ids or names."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Final, cast

REQUIRED_DIV_OWNERSHIP_KEYS: Final[tuple[str, ...]] = (
    "right_edge_elements_from_point_stack",
    "hit_box",
    "hit_pointer_events",
    "hit_role",
    "hit_name_present",
    "hit_testid",
    "hit_class_tokens",
    "hit_direct_parent",
    "hit_contained_by_input",
    "hit_contains_input",
    "hit_shares_smallest_wrapper",
    "smallest_wrapper",
    "nearest_clickable_ancestor",
)
_HIT_BOX_KEYS: Final[tuple[str, ...]] = ("x", "y", "w", "h")
_PARENT_KEYS: Final[tuple[str, ...]] = (
    "tag",
    "class_tokens",
    "role",
    "name_present",
    "testid",
    "contains_contact_input",
)
_WRAPPER_KEYS: Final[tuple[str, ...]] = (
    "tag",
    "class_tokens",
    "contact_input_count",
    "child_input_count",
)
_ANCESTOR_KEYS: Final[tuple[str, ...]] = (
    "tag",
    "role",
    "name_present",
    "testid",
    "is_contact_input",
)
_POINTER_EVENTS: Final[frozenset[str]] = frozenset({"auto", "none"})


def pointer_events_token(raw: str | None) -> str:
    """Allowlisted pointer-events. Never stores an unknown raw value."""

    compact = (raw or "").strip().casefold()
    if compact in _POINTER_EVENTS:
        return compact
    if compact == "":
        return "none"
    return "other"


def _as_str_map(value: object) -> dict[str, object] | None:
    if not isinstance(value, dict):
        return None
    return dict(cast(dict[str, object], value))


def _mapping_has_keys(value: object, keys: tuple[str, ...]) -> bool:
    parsed = _as_str_map(value)
    if parsed is None:
        return False
    return all(key in parsed for key in keys)


def _key_is_present(payload: Mapping[str, object], key: str) -> bool:
    match key:
        case "right_edge_elements_from_point_stack":
            return isinstance(payload.get(key), list)
        case "hit_box":
            hit_box = payload.get(key)
            if key not in payload:
                return False
            return hit_box is None or _mapping_has_keys(hit_box, _HIT_BOX_KEYS)
        case "hit_direct_parent":
            return _mapping_has_keys(payload.get(key), _PARENT_KEYS)
        case "smallest_wrapper":
            return _mapping_has_keys(payload.get(key), _WRAPPER_KEYS)
        case "nearest_clickable_ancestor":
            return _mapping_has_keys(payload.get(key), _ANCESTOR_KEYS)
        case (
            "hit_pointer_events"
            | "hit_role"
            | "hit_name_present"
            | "hit_testid"
            | "hit_class_tokens"
            | "hit_contained_by_input"
            | "hit_contains_input"
            | "hit_shares_smallest_wrapper"
        ):
            return key in payload
        case unreachable:
            raise RuntimeError(f"unknown DIV ownership key: {unreachable}")


def div_ownership_missing_keys(payload: Mapping[str, object]) -> list[str]:
    """Keys 9F777B8F requires that this opener dump does not record."""

    return [key for key in REQUIRED_DIV_OWNERSHIP_KEYS if not _key_is_present(payload, key)]


def empty_div_ownership() -> dict[str, object]:
    """Structurally complete 9F777B8F keys when evaluate is unavailable."""

    return {
        "right_edge_elements_from_point_stack": [],
        "hit_box": None,
        "hit_pointer_events": "none",
        "hit_role": None,
        "hit_name_present": False,
        "hit_testid": None,
        "hit_class_tokens": [],
        "hit_direct_parent": {
            "tag": None,
            "class_tokens": [],
            "role": None,
            "name_present": False,
            "testid": None,
            "contains_contact_input": False,
        },
        "hit_contained_by_input": False,
        "hit_contains_input": False,
        "hit_shares_smallest_wrapper": False,
        "smallest_wrapper": {
            "tag": None,
            "class_tokens": [],
            "contact_input_count": 0,
            "child_input_count": 0,
        },
        "nearest_clickable_ancestor": {
            "tag": None,
            "role": None,
            "name_present": False,
            "testid": None,
            "is_contact_input": False,
        },
    }


def _stack_has_contact_input(stack: object) -> bool:
    if not isinstance(stack, Sequence) or isinstance(stack, (str, bytes)):
        return False
    rows = cast(Sequence[object], stack)
    for raw_item in rows:
        item = _as_str_map(raw_item)
        if item is None:
            continue
        if item.get("tag") == "INPUT" and item.get("name") == "contact":
            return True
    return False


def div_belongs_to_kunde_control(payload: Mapping[str, object]) -> bool:
    """True only when the nameless DIV is proved to share the Kunde control."""

    if payload.get("hit_shares_smallest_wrapper") is not True:
        return False
    wrapper = _as_str_map(payload.get("smallest_wrapper"))
    if wrapper is None:
        return False
    if wrapper.get("contact_input_count") != 1:
        return False
    if payload.get("hit_contains_input") is True:
        return True
    if _stack_has_contact_input(payload.get("right_edge_elements_from_point_stack")):
        return True
    ancestor = _as_str_map(payload.get("nearest_clickable_ancestor"))
    return ancestor is not None and ancestor.get("is_contact_input") is True


def ownership_click_point(payload: Mapping[str, object]) -> dict[str, int] | None:
    """Viewport x/y for one mouse click. None when the ownership gate is closed."""

    if not div_belongs_to_kunde_control(payload):
        return None
    box = _as_str_map(payload.get("box"))
    offset = _as_str_map(payload.get("right_edge_offset"))
    if box is None or offset is None:
        return None
    x = box.get("x")
    y = box.get("y")
    dx = offset.get("dx")
    dy = offset.get("dy")
    if not isinstance(x, int) or not isinstance(y, int):
        return None
    if not isinstance(dx, int) or not isinstance(dy, int):
        return None
    if dx < 0 or dy < 0:
        return None
    return {"x": x + dx, "y": y + dy}
