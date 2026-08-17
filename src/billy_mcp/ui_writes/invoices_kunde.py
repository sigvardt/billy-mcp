"""Kunde typeahead contract for draft invoice writes.

Official invoice belongs-to is contact/contactId. UI label is Kunde.
"""

from __future__ import annotations

import re
from collections.abc import Mapping, Sequence
from typing import Final, cast

KUNDE_LABEL: Final = "Kunde"
KUNDE_INPUT_SELECTORS: Final[tuple[str, ...]] = (
    "input[name='contactId']",
    "input[name='contact']",
    "[data-cy*='contact' i]",
)
CREATE_KUNDE_LABEL: Final = "Opret kunde"
EXISTING_CUSTOMER_TAG_RE: Final = re.compile(r"^MCP-UI-INV-[0-9A-F]{8}$")
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


def after_type_is_existing_customer_observation(
    phase: Mapping[str, object], unique_tag: str
) -> bool:
    """True when after_type typed a live MCP-UI-INV tag. Not a bind.

    The 15-char dummy dump is not an existing-customer observation.
    """

    if EXISTING_CUSTOMER_TAG_RE.fullmatch(unique_tag) is None:
        return False
    expected = len(unique_tag)
    return phase.get("tag_len") == expected and phase.get("value_len") == expected


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


REQUIRED_OPENER_DUMP_KEYS: Final[tuple[str, ...]] = (
    "input",
    "owners",
    "label",
    "aria",
    "active_element",
    "a11y",
    "box",
    "pointer_events",
    "z_index",
    "element_from_point",
)
REQUIRED_WIDGET_CONTRACT_KEYS: Final[tuple[str, ...]] = (
    "autocomplete_token",
    "list_present",
    "datalist_count",
    "datalist_option_count",
    "visible_input_count",
    "a11y_snapshot",
    "field_shot",
)
_WIDGET_INPUT_KEYS: Final[tuple[str, ...]] = ("autocomplete_token", "list_present")
_A11Y_SNAPSHOT_KEYS: Final[tuple[str, ...]] = (
    "control_count",
    "listbox_present",
    "role_counts",
)
_FIELD_SHOT_KEYS: Final[tuple[str, ...]] = ("present", "bytes", "box")
_AUTOCOMPLETE_TOKENS: Final[frozenset[str]] = frozenset({"on", "off", "name"})


def autocomplete_token(raw: str | None) -> str:
    """Allowlisted autocomplete token. Never stores an unknown raw value."""

    if raw is None or raw.strip() == "":
        return "empty"
    compact = raw.strip().casefold()
    if compact in _AUTOCOMPLETE_TOKENS:
        return compact
    return "other"


def _mapping_has_keys(value: object, keys: tuple[str, ...]) -> bool:
    if not isinstance(value, Mapping):
        return False
    return all(key in value for key in keys)


def widget_contract_missing_keys(payload: Mapping[str, object]) -> list[str]:
    """Keys 51E18E60 requires that this opener or after_type dump does not record."""

    missing: list[str] = []
    raw_input = payload.get("input")
    input_map: Mapping[str, object] = (
        cast(Mapping[str, object], raw_input) if isinstance(raw_input, Mapping) else {}
    )
    for key in _WIDGET_INPUT_KEYS:
        if key not in input_map:
            missing.append(key)
    for key in REQUIRED_WIDGET_CONTRACT_KEYS:
        if key in _WIDGET_INPUT_KEYS:
            continue
        if key == "a11y_snapshot":
            if not _mapping_has_keys(payload.get(key), _A11Y_SNAPSHOT_KEYS):
                missing.append(key)
            continue
        if key == "field_shot":
            if not _mapping_has_keys(payload.get(key), _FIELD_SHOT_KEYS):
                missing.append(key)
            continue
        if key not in payload:
            missing.append(key)
    return missing


def empty_widget_contract() -> dict[str, object]:
    """Structurally complete 51E18E60 widget keys when evaluate is unavailable."""

    return {
        "datalist_count": 0,
        "datalist_option_count": 0,
        "visible_input_count": 0,
        "a11y_snapshot": {
            "control_count": 0,
            "listbox_present": False,
            "role_counts": {},
        },
        "field_shot": {"present": False, "bytes": 0, "box": None},
    }


def widget_named_action(payload: Mapping[str, object]) -> str | None:
    """Name one next action from a complete widget dump. None means lookup-trace."""

    option_count = payload.get("datalist_option_count")
    if isinstance(option_count, int) and option_count > 0:
        return "datalist_option"
    named = payload.get("named_opener")
    if isinstance(named, str) and named:
        return "named_opener"
    aria = payload.get("aria")
    if isinstance(aria, Mapping) and cast(Mapping[str, object], aria).get("autocomplete") is True:
        return "tab_blur"
    snapshot = payload.get("a11y_snapshot")
    if (
        isinstance(snapshot, Mapping)
        and cast(Mapping[str, object], snapshot).get("listbox_present") is True
    ):
        return "tab_blur"
    return None


def opener_dump_missing_keys(opener: Mapping[str, object]) -> list[str]:
    """Keys 5E1EDFB4 requires that this opener dump does not record."""

    return [key for key in REQUIRED_OPENER_DUMP_KEYS if key not in opener]


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
