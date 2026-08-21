"""Classify already-loaded listener source windows. Never stores the source."""

from __future__ import annotations

import re
from typing import Final, Literal

PropertyCategory = Literal["key", "code", "button", "pointer", "target", "modifier", "prevent"]
KeyCategory = Literal[
    "enter",
    "escape",
    "tab",
    "space",
    "arrow_down",
    "arrow_up",
    "arrow_left",
    "arrow_right",
    "other",
    "none",
]
ActionToken = Literal[
    "open",
    "close",
    "toggle",
    "expand",
    "collapse",
    "select",
    "set_value",
    "send",
    "trigger",
    "show",
    "hide",
    "none",
]

PROPERTY_CATEGORIES: Final[frozenset[str]] = frozenset(
    {"key", "code", "button", "pointer", "target", "modifier", "prevent"}
)
KEY_CATEGORIES: Final[frozenset[str]] = frozenset(
    {
        "enter",
        "escape",
        "tab",
        "space",
        "arrow_down",
        "arrow_up",
        "arrow_left",
        "arrow_right",
        "other",
        "none",
    }
)
ACTION_TOKENS: Final[frozenset[str]] = frozenset(
    {
        "open",
        "close",
        "toggle",
        "expand",
        "collapse",
        "select",
        "set_value",
        "send",
        "trigger",
        "show",
        "hide",
        "none",
    }
)
_KEY_LITERALS: Final[tuple[tuple[str, KeyCategory], ...]] = (
    ("ArrowDown", "arrow_down"),
    ("ArrowUp", "arrow_up"),
    ("ArrowLeft", "arrow_left"),
    ("ArrowRight", "arrow_right"),
    ("Escape", "escape"),
    ("Enter", "enter"),
    ("Spacebar", "space"),
    ("Space", "space"),
    ("Tab", "tab"),
    ('" "', "space"),
    ("' '", "space"),
)
_ACTION_NAMES: Final[tuple[tuple[str, ActionToken], ...]] = (
    ("setValue", "set_value"),
    ("set_value", "set_value"),
    ("collapse", "collapse"),
    ("expand", "expand"),
    ("toggle", "toggle"),
    ("trigger", "trigger"),
    ("select", "select"),
    ("close", "close"),
    ("open", "open"),
    ("send", "send"),
    ("show", "show"),
    ("hide", "hide"),
)
_PROPERTY_MARKERS: Final[tuple[tuple[str, PropertyCategory], ...]] = (
    ("preventDefault", "prevent"),
    ("stopPropagation", "prevent"),
    ("currentTarget", "target"),
    ("pointerType", "pointer"),
    ("clientX", "pointer"),
    ("clientY", "pointer"),
    ("keyCode", "key"),
    ("altKey", "modifier"),
    ("ctrlKey", "modifier"),
    ("metaKey", "modifier"),
    ("shiftKey", "modifier"),
    (".button", "button"),
    (".target", "target"),
    (".which", "key"),
    (".code", "code"),
    (".key", "key"),
)


def property_categories_from(source: str) -> list[str]:
    """Allowlisted event-property categories. Never stores the source."""

    found: list[str] = []
    for marker, token in _PROPERTY_MARKERS:
        if marker in source and token not in found:
            found.append(token)
    found.sort()
    return found


def accepted_key_category_from(source: str) -> KeyCategory:
    """One key category when the window names it explicitly."""

    hits: list[KeyCategory] = []
    for literal, token in _KEY_LITERALS:
        if literal in source and token not in hits:
            hits.append(token)
    if len(hits) == 1:
        return hits[0]
    if len(hits) > 1:
        return "other"
    return "none"


def invoked_action_token_from(source: str) -> ActionToken:
    """Named method or action only. Event type is not an invoke."""

    hits: list[ActionToken] = []
    for name, token in _ACTION_NAMES:
        if re.search(rf"\b{re.escape(name)}\b", source) and token not in hits:
            hits.append(token)
    if len(hits) == 1:
        return hits[0]
    if len(hits) > 1:
        return "none"
    return "none"
