"""Invoice Kunde versus bills Leverandør structure-compare keys.

Never stores source, URLs, locators, ids, or customer values.
"""

from __future__ import annotations

import json
from collections.abc import Mapping
from pathlib import Path
from typing import Final, Literal, Protocol, cast

from billy_mcp.ui_writes.bills_vendor import VENDOR_CHROME_DUMP, VENDOR_WRAPPER_DUMP
from billy_mcp.ui_writes.invoices_form_page import write_json
from billy_mcp.ui_writes.invoices_kunde_control import KUNDE_CONTROL_DUMP
from billy_mcp.ui_writes.invoices_kunde_descendants import KUNDE_DESCENDANT_DUMP
from billy_mcp.ui_writes.invoices_kunde_post_click import KUNDE_POST_CLICK_DUMP

StructureKey = Literal[
    "kunde_input_name_token",
    "bills_input_name_token",
    "kunde_wrapper_family",
    "bills_wrapper_family",
    "kunde_wrapper_data_attr_names",
    "kunde_search_trigger",
    "bills_search_trigger",
    "kunde_overlay_present",
    "kunde_list_host",
    "bills_list_host",
    "kunde_option_role_count",
    "bills_option_role_count",
    "same_family",
    "transferable_action",
    "unique_normal_action",
    "proved_kunde_bind",
    "proved_bills_bind",
    "kunde_structure_missing_keys",
]
InputNameToken = Literal["contact", "vendor", "other"]
WrapperFamily = Literal["pickerfield", "input_wrapper", "other"]
ListHost = Literal["ds_dropdown_portal", "ds_dropdown", "role_listbox", "none"]
TransferableAction = Literal["search_open", "portal_option", "none"]
BindToken = Literal["scoped_existing_option", "none"]

REQUIRED_KUNDE_STRUCTURE_KEYS: Final[tuple[StructureKey, ...]] = (
    "kunde_input_name_token",
    "bills_input_name_token",
    "kunde_wrapper_family",
    "bills_wrapper_family",
    "kunde_wrapper_data_attr_names",
    "kunde_search_trigger",
    "bills_search_trigger",
    "kunde_overlay_present",
    "kunde_list_host",
    "bills_list_host",
    "kunde_option_role_count",
    "bills_option_role_count",
    "same_family",
    "transferable_action",
    "unique_normal_action",
    "proved_kunde_bind",
    "proved_bills_bind",
    "kunde_structure_missing_keys",
)
INPUT_NAME_TOKENS: Final[frozenset[str]] = frozenset({"contact", "vendor", "other"})
WRAPPER_FAMILIES: Final[frozenset[str]] = frozenset({"pickerfield", "input_wrapper", "other"})
LIST_HOSTS: Final[frozenset[str]] = frozenset(
    {"ds_dropdown_portal", "ds_dropdown", "role_listbox", "none"}
)
TRANSFERABLE_ACTIONS: Final[frozenset[str]] = frozenset({"search_open", "portal_option", "none"})
BIND_TOKENS: Final[frozenset[str]] = frozenset({"scoped_existing_option", "none"})
DATA_ATTR_CAP: Final = 16
KUNDE_STRUCTURE_DUMP: Final = (
    Path.home() / ".local" / "share" / "billy-mcp" / "inspect-live-invoices-kunde-structure.json"
)
BILLS_DROPDOWN_DUMP: Final = (
    Path.home() / ".local" / "share" / "billy-mcp" / "inspect-live-bills-dropdown.json"
)


class _CountLocator(Protocol):
    def locator(self, selector: str) -> _CountLocator: ...

    def filter(self, *, has: object = ...) -> _CountLocator: ...

    async def count(self) -> int: ...


class _CountPage(Protocol):
    def locator(self, selector: str) -> _CountLocator: ...


def as_str_map(value: object) -> dict[str, object] | None:
    if not isinstance(value, dict):
        return None
    return cast(dict[str, object], value)


def input_name_token(raw: object) -> InputNameToken:
    if raw == "contact":
        return "contact"
    if raw == "vendor":
        return "vendor"
    return "other"


def wrapper_family_token(raw: object) -> WrapperFamily:
    if raw == "pickerfield":
        return "pickerfield"
    if raw == "input_wrapper":
        return "input_wrapper"
    return "other"


def list_host_token(raw: object) -> ListHost:
    if isinstance(raw, str) and raw in LIST_HOSTS and raw != "none":
        return cast(ListHost, raw)
    return "none"


def transferable_action_token(raw: object) -> TransferableAction:
    if raw == "search_open":
        return "search_open"
    if raw == "portal_option":
        return "portal_option"
    return "none"


def bind_token(raw: object) -> BindToken:
    if raw in {"scoped_existing_option", "scoped:existing_option"}:
        return "scoped_existing_option"
    return "none"


def sanitize_data_attr_names(raw: object) -> list[str]:
    names: list[str] = []
    if not isinstance(raw, list):
        return names
    for item in cast(list[object], raw):
        if not isinstance(item, str) or not item.startswith("data-"):
            continue
        if item not in names:
            names.append(item)
        if len(names) >= DATA_ATTR_CAP:
            break
    names.sort()
    return names


def _int_count(raw: object) -> int:
    return raw if isinstance(raw, int) and raw >= 0 else 0


def _key_is_present(payload: Mapping[str, object], key: StructureKey) -> bool:
    value = payload.get(key)
    match key:
        case "kunde_input_name_token" | "bills_input_name_token":
            return value in INPUT_NAME_TOKENS
        case "kunde_wrapper_family" | "bills_wrapper_family":
            return value in WRAPPER_FAMILIES
        case "kunde_wrapper_data_attr_names":
            return isinstance(value, list) and all(
                isinstance(item, str) and item.startswith("data-")
                for item in cast(list[object], value)
            )
        case (
            "kunde_search_trigger"
            | "bills_search_trigger"
            | "kunde_overlay_present"
            | "same_family"
            | "unique_normal_action"
        ):
            return isinstance(value, bool)
        case "kunde_list_host" | "bills_list_host":
            return value in LIST_HOSTS
        case "kunde_option_role_count" | "bills_option_role_count":
            return isinstance(value, int) and value >= 0
        case "transferable_action":
            return value in TRANSFERABLE_ACTIONS
        case "proved_kunde_bind" | "proved_bills_bind":
            return value in BIND_TOKENS
        case "kunde_structure_missing_keys":
            return isinstance(value, list)


def kunde_structure_missing_keys(payload: Mapping[str, object]) -> list[str]:
    """Keys the structure compare requires that this dump does not record."""

    if "kunde_input_name_token" not in payload:
        return list(REQUIRED_KUNDE_STRUCTURE_KEYS)
    return [key for key in REQUIRED_KUNDE_STRUCTURE_KEYS if not _key_is_present(payload, key)]


def empty_kunde_structure() -> dict[str, object]:
    """Structurally complete compare keys before a dump map."""

    return {
        "kunde_input_name_token": "other",
        "bills_input_name_token": "other",
        "kunde_wrapper_family": "other",
        "bills_wrapper_family": "other",
        "kunde_wrapper_data_attr_names": [],
        "kunde_search_trigger": False,
        "bills_search_trigger": False,
        "kunde_overlay_present": False,
        "kunde_list_host": "none",
        "bills_list_host": "none",
        "kunde_option_role_count": 0,
        "bills_option_role_count": 0,
        "same_family": False,
        "transferable_action": "none",
        "unique_normal_action": False,
        "proved_kunde_bind": "none",
        "proved_bills_bind": "none",
        "kunde_structure_missing_keys": [],
    }


def same_family_from(payload: Mapping[str, object]) -> bool:
    """True only when both sides are input-wrapper + search + portal list."""

    return (
        payload.get("kunde_wrapper_family") == "input_wrapper"
        and payload.get("bills_wrapper_family") == "input_wrapper"
        and payload.get("kunde_search_trigger") is True
        and payload.get("bills_search_trigger") is True
        and payload.get("kunde_list_host") == "ds_dropdown_portal"
        and payload.get("bills_list_host") == "ds_dropdown_portal"
    )


def transferable_action_from(payload: Mapping[str, object]) -> TransferableAction:
    """Non-none only when the invoice rest host is an unused bills-family picker."""

    if payload.get("kunde_wrapper_family") != "input_wrapper":
        return "none"
    if payload.get("kunde_search_trigger") is not True:
        return "none"
    if payload.get("kunde_list_host") == "ds_dropdown_portal":
        return "portal_option"
    return "search_open"


def unique_normal_action_from(payload: Mapping[str, object]) -> bool:
    return same_family_from(payload) and transferable_action_from(payload) != "none"


def _load_json(path: Path) -> dict[str, object] | None:
    if not path.is_file():
        return None
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    return as_str_map(raw)


def _wrapper_family_from_tokens(tokens: object) -> WrapperFamily:
    if not isinstance(tokens, list):
        return "other"
    compact = {item for item in cast(list[object], tokens) if isinstance(item, str)}
    if "pickerfield" in compact:
        return "pickerfield"
    if "input-wrapper" in compact:
        return "input_wrapper"
    return "other"


def _overlay_present(descendants: object) -> bool:
    if not isinstance(descendants, list):
        return False
    for item in cast(list[object], descendants):
        row = as_str_map(item)
        if row is None:
            continue
        box = as_str_map(row.get("box"))
        if box is None:
            continue
        if box.get("dx") == 242.0 and box.get("w") == 40.0 and box.get("h") == 40.0:
            return True
    return False


def _list_host_from_counts(*, portal: int, dropdown: int, options: int) -> ListHost:
    if portal > 0:
        return "ds_dropdown_portal"
    if dropdown > 0:
        return "ds_dropdown"
    if options > 0:
        return "role_listbox"
    return "none"


def map_existing_dumps(
    *,
    control_path: Path | None = None,
    descendant_path: Path | None = None,
    listener_path: Path | None = None,
    post_click_path: Path | None = None,
    bills_vendor_path: Path | None = None,
    bills_wrapper_path: Path | None = None,
    bills_dropdown_path: Path | None = None,
) -> dict[str, object]:
    """Map already delivered owner dumps. Does not remake them."""

    del listener_path
    result = empty_kunde_structure()
    control = _load_json(control_path or KUNDE_CONTROL_DUMP)
    if control is not None:
        family = _wrapper_family_from_tokens(control.get("wrapper_class_tokens"))
        result["kunde_wrapper_family"] = family
        if family == "pickerfield":
            result["kunde_input_name_token"] = "contact"
        result["kunde_wrapper_data_attr_names"] = sanitize_data_attr_names(
            control.get("wrapper_data_attr_names")
        )
        result["kunde_option_role_count"] = _int_count(control.get("action_option_role_count"))
    descendants = _load_json(descendant_path or KUNDE_DESCENDANT_DUMP)
    if descendants is not None:
        result["kunde_overlay_present"] = _overlay_present(descendants.get("descendants"))
    post_click = _load_json(post_click_path or KUNDE_POST_CLICK_DUMP)
    if post_click is not None and _int_count(post_click.get("changed_node_count")) == 0:
        result["kunde_list_host"] = "none"
    vendor = _load_json(bills_vendor_path or VENDOR_CHROME_DUMP)
    if vendor is not None:
        names = vendor.get("input_names")
        if isinstance(names, list) and "vendor" in names:
            result["bills_input_name_token"] = "vendor"
        result["proved_bills_bind"] = bind_token(vendor.get("chosen"))
    wrapper = _load_json(bills_wrapper_path or VENDOR_WRAPPER_DUMP)
    if wrapper is not None:
        after_click = as_str_map(wrapper.get("after_click")) or {}
        after_type = as_str_map(wrapper.get("after_type")) or {}
        result["bills_search_trigger"] = after_click.get("search_trigger") is True
        if after_click.get("input_name") == "vendor" or after_type.get("input_name") == "vendor":
            result["bills_input_name_token"] = "vendor"
            result["bills_wrapper_family"] = "input_wrapper"
        portal = as_str_map(after_click.get("portal_list")) or as_str_map(
            after_type.get("portal_list")
        )
        portal_count = _int_count(portal.get("count")) if portal is not None else 0
        result["bills_list_host"] = _list_host_from_counts(
            portal=portal_count, dropdown=0, options=0
        )
    dropdown = _load_json(bills_dropdown_path or BILLS_DROPDOWN_DUMP)
    if dropdown is not None:
        result["bills_option_role_count"] = _int_count(dropdown.get("option"))
    result["kunde_search_trigger"] = "data-testid" in cast(
        list[object], result["kunde_wrapper_data_attr_names"]
    )
    return result


def merge_rest_counts(
    payload: Mapping[str, object], counts: Mapping[str, object]
) -> dict[str, object]:
    """Merge allowlisted rest-page counts onto a dump map. No click."""

    result = dict(payload)
    if _int_count(counts.get("contact_input_n")) >= 1:
        result["kunde_input_name_token"] = "contact"
    if _int_count(counts.get("pickerfield_n")) >= 1:
        result["kunde_wrapper_family"] = "pickerfield"
    elif _int_count(counts.get("contact_wrapper_n")) >= 1:
        result["kunde_wrapper_family"] = "input_wrapper"
    if _int_count(counts.get("kunde_search_n")) >= 1:
        result["kunde_search_trigger"] = True
    result["kunde_option_role_count"] = _int_count(counts.get("option_n"))
    result["kunde_list_host"] = _list_host_from_counts(
        portal=_int_count(counts.get("portal_n")),
        dropdown=_int_count(counts.get("dropdown_n")),
        options=_int_count(counts.get("option_n")),
    )
    return result


async def _safe_count(node: _CountLocator) -> int:
    try:
        return await node.count()
    except Exception:
        return 0


async def count_invoice_rest_tokens(page: _CountPage) -> dict[str, int]:
    """Allowlisted rest-page counts on invoices/new. Does not click or type."""

    contact = page.locator("input[name='contact']")
    picker = page.locator(".pickerfield").filter(has=contact)
    wrapper = page.locator("[data-testid='input-wrapper']").filter(has=contact)
    return {
        "contact_input_n": await _safe_count(contact),
        "vendor_input_n": await _safe_count(page.locator("input[name='vendor']")),
        "pickerfield_n": await _safe_count(picker),
        "contact_wrapper_n": await _safe_count(wrapper),
        "kunde_search_n": await _safe_count(picker.locator("[data-testid='search']"))
        + await _safe_count(wrapper.locator("[data-testid='search']")),
        "dropdown_n": await _safe_count(page.locator(".ds-dropdown-list")),
        "portal_n": await _safe_count(page.locator(".ds-dropdown-list.ds-moved-with-portal")),
        "option_n": await _safe_count(page.locator("[role='option']")),
    }


async def capture_kunde_structure(
    page: _CountPage,
    *,
    dump_path: Path | None = None,
) -> dict[str, object]:
    """Map existing dumps and optional rest counts. Does not click or remake dumps."""

    mapped = map_existing_dumps()
    counts = await count_invoice_rest_tokens(page)
    return apply_kunde_structure_dump(merge_rest_counts(mapped, counts), dump_path=dump_path)


def apply_kunde_structure_dump(
    payload: Mapping[str, object],
    *,
    dump_path: Path | None = None,
) -> dict[str, object]:
    """Copy allowlisted keys and write the owner-only summary."""

    result = empty_kunde_structure()
    result["kunde_input_name_token"] = input_name_token(payload.get("kunde_input_name_token"))
    result["bills_input_name_token"] = input_name_token(payload.get("bills_input_name_token"))
    result["kunde_wrapper_family"] = wrapper_family_token(payload.get("kunde_wrapper_family"))
    result["bills_wrapper_family"] = wrapper_family_token(payload.get("bills_wrapper_family"))
    result["kunde_wrapper_data_attr_names"] = sanitize_data_attr_names(
        payload.get("kunde_wrapper_data_attr_names")
    )
    result["kunde_search_trigger"] = payload.get("kunde_search_trigger") is True
    result["bills_search_trigger"] = payload.get("bills_search_trigger") is True
    result["kunde_overlay_present"] = payload.get("kunde_overlay_present") is True
    result["kunde_list_host"] = list_host_token(payload.get("kunde_list_host"))
    result["bills_list_host"] = list_host_token(payload.get("bills_list_host"))
    result["kunde_option_role_count"] = _int_count(payload.get("kunde_option_role_count"))
    result["bills_option_role_count"] = _int_count(payload.get("bills_option_role_count"))
    result["proved_kunde_bind"] = bind_token(payload.get("proved_kunde_bind"))
    result["proved_bills_bind"] = bind_token(payload.get("proved_bills_bind"))
    result["same_family"] = same_family_from(result)
    result["transferable_action"] = transferable_action_from(result)
    unique = unique_normal_action_from(result)
    result["unique_normal_action"] = unique
    result["kunde_structure_missing_keys"] = kunde_structure_missing_keys(result)
    if not unique:
        result["code"] = "UI_CHANGED"
        result["message"] = "Billy Kunde and bills Leverandør chrome families differ."
    summary = {key: result.get(key) for key in REQUIRED_KUNDE_STRUCTURE_KEYS}
    write_json(dump_path or KUNDE_STRUCTURE_DUMP, summary)
    return result


def structure_dump_is_delivered(path: Path | None = None) -> bool:
    """True when the owner dump already recorded the structure compare."""

    target = path or KUNDE_STRUCTURE_DUMP
    if not target.is_file():
        return False
    payload = _load_json(target)
    return payload is not None and kunde_structure_missing_keys(payload) == []


def structure_dump_json(payload: Mapping[str, object]) -> str:
    """Stable JSON for leak checks. Never includes source or URLs."""

    return json.dumps(dict(payload), sort_keys=True)


__all__ = [
    "KUNDE_STRUCTURE_DUMP",
    "REQUIRED_KUNDE_STRUCTURE_KEYS",
    "apply_kunde_structure_dump",
    "as_str_map",
    "capture_kunde_structure",
    "count_invoice_rest_tokens",
    "empty_kunde_structure",
    "kunde_structure_missing_keys",
    "map_existing_dumps",
    "merge_rest_counts",
    "same_family_from",
    "structure_dump_is_delivered",
    "structure_dump_json",
    "transferable_action_from",
    "unique_normal_action_from",
]
