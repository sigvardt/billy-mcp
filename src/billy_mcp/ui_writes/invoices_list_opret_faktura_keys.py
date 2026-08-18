"""Allowlisted tokens for the invoice-list Opret faktura dump."""

from __future__ import annotations

import json
import re
from collections.abc import Mapping
from pathlib import Path
from typing import Final, Literal, cast
from urllib.parse import urlsplit

from billy_mcp.ui_writes.invoices_form_page import write_json

ListCtaKey = Literal[
    "list_path_class",
    "exact_list_opret_faktura_count",
    "list_opret_faktura_role",
    "clicked_list_opret_faktura",
    "destination_path_class",
    "destination_query_token_class",
    "destination_heading_token",
    "contact_input_present",
    "contact_input_value_len",
    "contact_input_matches_tag",
    "option_role_count",
    "aria_expanded_token",
    "unique_action",
    "proved_bind",
    "missing_keys",
]
ListPathClass = Literal["invoices", "invoices_empty", "other"]
UniqueAction = Literal["existing_option", "none"]
ProvedBind = Literal["list_cta_existing_option", "list_cta_prebound", "none"]

REQUIRED_LIST_OPRET_FAKTURA_KEYS: Final[tuple[ListCtaKey, ...]] = (
    "list_path_class",
    "exact_list_opret_faktura_count",
    "list_opret_faktura_role",
    "clicked_list_opret_faktura",
    "destination_path_class",
    "destination_query_token_class",
    "destination_heading_token",
    "contact_input_present",
    "contact_input_value_len",
    "contact_input_matches_tag",
    "option_role_count",
    "aria_expanded_token",
    "unique_action",
    "proved_bind",
    "missing_keys",
)
LIST_PATH_CLASSES: Final[frozenset[str]] = frozenset({"invoices", "invoices_empty", "other"})
OPRET_ROLES: Final[frozenset[str]] = frozenset({"button", "link", "none"})
DEST_PATH_CLASSES: Final[frozenset[str]] = frozenset(
    {"invoices_new", "invoices_new_with_query", "other", "none"}
)
QUERY_CLASSES: Final[frozenset[str]] = frozenset({"contact", "none", "other"})
HEADING_TOKENS: Final[frozenset[str]] = frozenset({"opret_faktura", "other", "none"})
ARIA_TOKENS: Final[frozenset[str]] = frozenset({"true", "false", "missing"})
UNIQUE_ACTIONS: Final[frozenset[str]] = frozenset({"existing_option", "none"})
PROVED_BINDS: Final[frozenset[str]] = frozenset(
    {"list_cta_existing_option", "list_cta_prebound", "none"}
)
LIST_OPRET_FAKTURA_DUMP: Final = (
    Path.home() / ".local" / "share" / "billy-mcp" / "inspect-live-invoices-list-opret-faktura.json"
)
_INVOICES_EMPTY = r"^/[^/]+/invoices/empty/?$"
_INVOICES_LIST = r"^/[^/]+/invoices/?$"


def classify_list_path(url: object) -> ListPathClass:
    """Return invoices or invoices_empty. Never store the URL."""

    if not isinstance(url, str) or not url:
        return "other"
    path = urlsplit(url).path or ""
    if re.match(_INVOICES_EMPTY, path):
        return "invoices_empty"
    if re.match(_INVOICES_LIST, path):
        return "invoices"
    return "other"


def unique_action_from(payload: Mapping[str, object]) -> UniqueAction:
    return "existing_option" if payload.get("option_role_count") == 1 else "none"


def proved_bind_from(payload: Mapping[str, object]) -> ProvedBind:
    if payload.get("contact_input_matches_tag") is True:
        return "list_cta_prebound"
    if payload.get("unique_action") == "existing_option":
        return "list_cta_existing_option"
    return "none"


def _int_count(raw: object) -> int:
    return raw if isinstance(raw, int) and raw >= 0 else 0


def _token(raw: object, allowed: frozenset[str], default: str) -> str:
    if isinstance(raw, str) and raw in allowed:
        return raw
    return default


def _key_is_present(payload: Mapping[str, object], key: ListCtaKey) -> bool:
    value = payload.get(key)
    match key:
        case "list_path_class":
            return value in LIST_PATH_CLASSES
        case "exact_list_opret_faktura_count" | "contact_input_value_len" | "option_role_count":
            return isinstance(value, int) and value >= 0
        case "list_opret_faktura_role":
            return value in OPRET_ROLES
        case "clicked_list_opret_faktura" | "contact_input_present" | "contact_input_matches_tag":
            return isinstance(value, bool)
        case "destination_path_class":
            return value in DEST_PATH_CLASSES
        case "destination_query_token_class":
            return value in QUERY_CLASSES
        case "destination_heading_token":
            return value in HEADING_TOKENS
        case "aria_expanded_token":
            return value in ARIA_TOKENS
        case "unique_action":
            return value in UNIQUE_ACTIONS
        case "proved_bind":
            return value in PROVED_BINDS
        case "missing_keys":
            return isinstance(value, list)


def list_opret_faktura_missing_keys(payload: Mapping[str, object]) -> list[str]:
    """Keys the list-CTA dump requires that this payload does not record."""

    if "list_path_class" not in payload:
        return list(REQUIRED_LIST_OPRET_FAKTURA_KEYS)
    return [key for key in REQUIRED_LIST_OPRET_FAKTURA_KEYS if not _key_is_present(payload, key)]


def empty_list_opret_faktura() -> dict[str, object]:
    """Structurally complete list-CTA keys before a live inspect."""

    return {
        "list_path_class": "other",
        "exact_list_opret_faktura_count": 0,
        "list_opret_faktura_role": "none",
        "clicked_list_opret_faktura": False,
        "destination_path_class": "none",
        "destination_query_token_class": "none",
        "destination_heading_token": "none",
        "contact_input_present": False,
        "contact_input_value_len": 0,
        "contact_input_matches_tag": False,
        "option_role_count": 0,
        "aria_expanded_token": "missing",
        "unique_action": "none",
        "proved_bind": "none",
        "missing_keys": [],
    }


def apply_list_opret_faktura_dump(
    payload: Mapping[str, object],
    *,
    dump_path: Path | None = None,
) -> dict[str, object]:
    """Copy allowlisted keys and write the owner-only summary."""

    result = empty_list_opret_faktura()
    result["list_path_class"] = _token(payload.get("list_path_class"), LIST_PATH_CLASSES, "other")
    result["exact_list_opret_faktura_count"] = _int_count(
        payload.get("exact_list_opret_faktura_count")
    )
    result["list_opret_faktura_role"] = _token(
        payload.get("list_opret_faktura_role"), OPRET_ROLES, "none"
    )
    result["clicked_list_opret_faktura"] = payload.get("clicked_list_opret_faktura") is True
    result["destination_path_class"] = _token(
        payload.get("destination_path_class"), DEST_PATH_CLASSES, "none"
    )
    result["destination_query_token_class"] = _token(
        payload.get("destination_query_token_class"), QUERY_CLASSES, "none"
    )
    result["destination_heading_token"] = _token(
        payload.get("destination_heading_token"), HEADING_TOKENS, "none"
    )
    result["contact_input_present"] = payload.get("contact_input_present") is True
    result["contact_input_value_len"] = _int_count(payload.get("contact_input_value_len"))
    result["contact_input_matches_tag"] = payload.get("contact_input_matches_tag") is True
    result["option_role_count"] = _int_count(payload.get("option_role_count"))
    result["aria_expanded_token"] = _token(
        payload.get("aria_expanded_token"), ARIA_TOKENS, "missing"
    )
    result["unique_action"] = unique_action_from(result)
    result["proved_bind"] = proved_bind_from(result)
    result["missing_keys"] = list_opret_faktura_missing_keys(result)
    if result["proved_bind"] == "none":
        result["code"] = "UI_CHANGED"
        result["message"] = "Billy invoice list Opret faktura did not bind an existing customer."
    summary = {key: result.get(key) for key in REQUIRED_LIST_OPRET_FAKTURA_KEYS}
    write_json(dump_path or LIST_OPRET_FAKTURA_DUMP, summary)
    return result


def list_opret_faktura_dump_is_delivered(path: Path | None = None) -> bool:
    """True when the owner dump already recorded the list-CTA inspect."""

    target = path or LIST_OPRET_FAKTURA_DUMP
    if not target.is_file():
        return False
    try:
        raw = json.loads(target.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return False
    if not isinstance(raw, dict):
        return False
    return list_opret_faktura_missing_keys(cast(dict[str, object], raw)) == []


def list_opret_faktura_dump_json(payload: Mapping[str, object]) -> str:
    """Stable JSON for leak checks. Never includes source or URLs."""

    return json.dumps(dict(payload), sort_keys=True)
