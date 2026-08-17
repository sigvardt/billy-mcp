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


def kunde_phase_is_bound(phase: Mapping[str, object]) -> bool:
    """True only when a visible existing option or create footer exists.

    Typed-only ``input[name=contact]`` is not a bind. Live after-type dumps
    with ``wrapper_count=0`` and hidden decoys stay unbound.
    """

    if phase.get("existing_index") is not None:
        return True
    return phase.get("create_index") is not None


def placeholder_flags(text: str | None) -> dict[str, bool]:
    """Non-PII placeholder tokens. Never stores the raw placeholder."""

    compact = (text or "").casefold()
    return {
        "has_kunde": "kunde" in compact,
        "has_customer": "customer" in compact,
        "has_vaelg": "vælg" in compact or "vaelg" in compact,
        "has_soeg": "søg" in compact or "soeg" in compact,
        "has_select": "select" in compact,
    }


def named_kunde_opener(opener: Mapping[str, object]) -> str | None:
    """Name the first real opener. The contact text field is not one."""

    if opener.get("sibling_search") is True:
        return "sibling_search"
    if opener.get("uncle_search") is True:
        return "uncle_search"
    combobox_count = opener.get("combobox_count")
    if isinstance(combobox_count, int) and combobox_count > 0:
        return "combobox"
    contact_id_count = opener.get("contact_id_count")
    if isinstance(contact_id_count, int) and contact_id_count > 0:
        return "contact_id"
    trigger_count = opener.get("power_select_trigger_count")
    if isinstance(trigger_count, int) and trigger_count > 0:
        return "power_select_trigger"
    return None
