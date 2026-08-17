"""Kunde typeahead contract for draft invoice writes.

Official invoice belongs-to is contact/contactId. UI label is Kunde.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Final

KUNDE_LABEL: Final = "Kunde"
KUNDE_INPUT_SELECTORS: Final[tuple[str, ...]] = (
    "input[name='contactId']",
    "input[name='contact']",
    "[data-cy*='contact' i]",
)
CREATE_KUNDE_LABEL: Final = "Opret kunde"
PORTAL_FOOTER_WRAPPER: Final = "[class*='DropdownFooterWrapper']"
DROPDOWN_SELECTORS: Final[tuple[str, ...]] = (
    ".ds-dropdown-list",
    "[role='listbox']",
    "[role='option']",
)


def portal_create_footer_label(unique_tag: str) -> str:
    """Exact empty-list footer text observed on the contact typeahead."""

    return f'Opret "{unique_tag}"'


def is_create_kunde_option(label: str, unique_tag: str) -> bool:
    """True when a dropdown row creates a customer for this tag."""

    text = label.strip()
    if text == CREATE_KUNDE_LABEL:
        return True
    return text == portal_create_footer_label(unique_tag)


def portal_list_item_flags(text: str, unique_tag: str) -> dict[str, bool]:
    """Non-PII flags for one portal list. Never stores the tag."""

    compact = " ".join(text.split())
    footer = portal_create_footer_label(unique_tag)
    return {
        "has_opret": "Opret" in text,
        "has_tag": unique_tag in text,
        "has_empty": "Ingen resultater" in text,
        "has_create_footer": footer in text,
        "visible": True,
        "short": len(compact) < 200,
    }


def pick_kunde_existing_option_index(items: Sequence[Mapping[str, object]]) -> int | None:
    """Index of a visible existing customer option. Create footer is not this bind."""

    for index, item in enumerate(items):
        if item.get("has_tag") is not True:
            continue
        if item.get("visible") is False:
            continue
        if item.get("short") is False:
            continue
        if item.get("has_empty") is True:
            continue
        return index
    return None


def pick_kunde_create_index(items: Sequence[Mapping[str, object]]) -> int | None:
    """Index of the empty customer list with a create footer. Skip huge ancestors."""

    for index, item in enumerate(items):
        if item.get("has_empty") is not True:
            continue
        if item.get("has_create_footer") is not True:
            continue
        if item.get("short") is False:
            continue
        if item.get("visible") is False:
            continue
        return index
    return None
