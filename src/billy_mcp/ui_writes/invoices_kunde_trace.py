"""Invoice Kunde instrumented request/DOM trace (8EFD0EAD). Never stores bodies or IDs."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Final, cast
from urllib.parse import urlsplit

REQUIRED_KUNDE_TRACE_KEYS: Final[tuple[str, ...]] = (
    "listener_attached_before_form",
    "requests",
    "console_categories",
    "portal_inserted",
    "portal_count",
    "option_role_count",
    "active_element",
)
_REQUEST_KEYS: Final[tuple[str, ...]] = ("method", "path_class", "status", "timing_ms")
_CONSOLE_KEYS: Final[tuple[str, ...]] = ("script", "pageerror", "other")
_ACTIVE_KEYS: Final[tuple[str, ...]] = ("tag", "name_token", "aria_expanded_present")
_PATH_CLASSES: Final[frozenset[str]] = frozenset(
    {"contacts", "invoices", "other_v2", "other_same_origin", "denied"}
)
_NAME_TOKENS: Final[frozenset[str]] = frozenset({"contact", "contactId", "empty", "other"})
_ALLOWED_HOSTS: Final[frozenset[str]] = frozenset(
    {"mit.billy.dk", "api.billysbilling.com", "download.billy.dk"}
)
_TRACE_REQUEST_CAP: Final = 32


def request_path_class(path: str) -> str:
    """Map a query-stripped path to an allowlisted class. Never stores the path."""

    cleaned = path.split("?", 1)[0]
    if "/v2/contacts" in cleaned:
        return "contacts"
    if "/v2/invoices" in cleaned:
        return "invoices"
    if "/v2/" in cleaned:
        return "other_v2"
    return "other_same_origin"


def request_url_class(url: str) -> str:
    """Map a full URL to path_class. Hosts outside the Billy allowlist are denied."""

    parsed = urlsplit(url)
    host = parsed.netloc.split("@")[-1].split(":")[0].casefold()
    if host not in _ALLOWED_HOSTS:
        return "denied"
    return request_path_class(parsed.path)


def name_token(raw: str | None) -> str:
    """Allowlisted input name token. Never stores an unknown raw name."""

    if raw is None or raw.strip() == "":
        return "empty"
    if raw in _NAME_TOKENS and raw not in {"empty", "other"}:
        return raw
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


def _requests_are_present(value: object) -> bool:
    if not isinstance(value, list):
        return False
    for item in cast(list[object], value):
        if not _mapping_has_keys(item, _REQUEST_KEYS):
            return False
        row = _as_str_map(item)
        if row is None:
            return False
        path_class = row.get("path_class")
        if path_class not in _PATH_CLASSES:
            return False
    return True


def _key_is_present(payload: Mapping[str, object], key: str) -> bool:
    match key:
        case "listener_attached_before_form":
            return isinstance(payload.get(key), bool)
        case "requests":
            return _requests_are_present(payload.get(key))
        case "console_categories":
            return _mapping_has_keys(payload.get(key), _CONSOLE_KEYS)
        case "portal_inserted":
            return isinstance(payload.get(key), bool)
        case "portal_count" | "option_role_count":
            return isinstance(payload.get(key), int)
        case "active_element":
            active = _as_str_map(payload.get(key))
            if active is None:
                return False
            if not _mapping_has_keys(active, _ACTIVE_KEYS):
                return False
            return active.get("name_token") in _NAME_TOKENS
        case unreachable:
            raise RuntimeError(f"unknown Kunde trace key: {unreachable}")


def kunde_trace_missing_keys(payload: Mapping[str, object]) -> list[str]:
    """Keys 8EFD0EAD requires that this opener or phase dump does not record."""

    return [key for key in REQUIRED_KUNDE_TRACE_KEYS if not _key_is_present(payload, key)]


def empty_kunde_trace() -> dict[str, object]:
    """Structurally complete 8EFD0EAD keys when no listener has run."""

    return {
        "listener_attached_before_form": False,
        "requests": [],
        "console_categories": {"script": 0, "pageerror": 0, "other": 0},
        "portal_inserted": False,
        "portal_count": 0,
        "option_role_count": 0,
        "active_element": {
            "tag": None,
            "name_token": "empty",
            "aria_expanded_present": False,
        },
    }


def kunde_trace_names_next_action(phase: Mapping[str, object]) -> bool:
    """True when the instrumented dump names one normal next action."""

    if phase.get("portal_inserted") is True:
        return True
    option_count = phase.get("option_role_count")
    if isinstance(option_count, int) and option_count > 0:
        return True
    active = _as_str_map(phase.get("active_element"))
    if active is not None and active.get("aria_expanded_present") is True:
        return True
    requests = phase.get("requests")
    if not isinstance(requests, list):
        return False
    for item in cast(list[object], requests):
        row = _as_str_map(item)
        if row is not None and row.get("path_class") == "contacts":
            return True
    return False


def redact_trace_request(
    *, method: str, path_class: str, status: int, timing_ms: int
) -> dict[str, object]:
    """One redacted request row. Never stores URL, query, or body."""

    verb = method.strip().upper() or "OTHER"
    classified = path_class if path_class in _PATH_CLASSES else "denied"
    return {
        "method": verb,
        "path_class": classified,
        "status": max(0, status),
        "timing_ms": max(0, timing_ms),
    }


TRACE_REQUEST_CAP: Final = _TRACE_REQUEST_CAP
