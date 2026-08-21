"""Customer-detail Opret faktura prebind keys.

Never stores source, URLs, locators, ids, query values, or customer names.
"""

from __future__ import annotations

import asyncio
import json
import re
from collections.abc import Mapping
from pathlib import Path
from typing import Final, Literal, Protocol, cast
from urllib.parse import parse_qsl, urlsplit

from billy_mcp.ui_writes.invoices_form_page import write_json

PrebindKey = Literal[
    "detail_path_class",
    "tagged_name_visible",
    "exact_ret_count",
    "exact_opret_faktura_role",
    "exact_opret_faktura_count",
    "href_path_class",
    "href_query_token_class",
    "clicked_opret_faktura",
    "destination_heading_token",
    "contact_input_value_len",
    "contact_input_matches_tag",
    "unique_normal_action",
    "proved_prebind",
    "missing_keys",
]
DetailPathClass = Literal["contacts_customer", "other"]
OpretRole = Literal["button", "link", "none"]
HrefPathClass = Literal["invoices_new", "invoices_new_with_query", "other", "none"]
HrefQueryTokenClass = Literal["contact", "none", "other"]
HeadingToken = Literal["opret_faktura", "other", "none"]
ProvedPrebind = Literal["customer_detail_opret_faktura", "none"]

REQUIRED_CUSTOMER_DETAIL_PREBIND_KEYS: Final[tuple[PrebindKey, ...]] = (
    "detail_path_class",
    "tagged_name_visible",
    "exact_ret_count",
    "exact_opret_faktura_role",
    "exact_opret_faktura_count",
    "href_path_class",
    "href_query_token_class",
    "clicked_opret_faktura",
    "destination_heading_token",
    "contact_input_value_len",
    "contact_input_matches_tag",
    "unique_normal_action",
    "proved_prebind",
    "missing_keys",
)
DETAIL_PATH_CLASSES: Final[frozenset[str]] = frozenset({"contacts_customer", "other"})
OPRET_ROLES: Final[frozenset[str]] = frozenset({"button", "link", "none"})
HREF_PATH_CLASSES: Final[frozenset[str]] = frozenset(
    {"invoices_new", "invoices_new_with_query", "other", "none"}
)
HREF_QUERY_CLASSES: Final[frozenset[str]] = frozenset({"contact", "none", "other"})
HEADING_TOKENS: Final[frozenset[str]] = frozenset({"opret_faktura", "other", "none"})
PROVED_TOKENS: Final[frozenset[str]] = frozenset({"customer_detail_opret_faktura", "none"})
CONTACT_QUERY_NAMES: Final[frozenset[str]] = frozenset({"contact", "contactid", "contact_id"})
_INVOICES_NEW = re.compile(r"^/[^/]+/invoices/new/?$")
_CONTACTS_CUSTOMER = re.compile(r"/contacts/[^/]+/customer/?$")
_OPRET = "Opret faktura"
_RET = "Ret"
_MERE = "Mere"
CUSTOMER_DETAIL_PREBIND_DUMP: Final = (
    Path.home()
    / ".local"
    / "share"
    / "billy-mcp"
    / "inspect-live-invoices-customer-detail-prebind.json"
)


class _CountLocator(Protocol):
    @property
    def first(self) -> _CountLocator: ...

    async def count(self) -> int: ...

    async def is_visible(self) -> bool: ...

    async def click(self) -> None: ...

    async def inner_text(self) -> str: ...

    async def get_attribute(self, name: str) -> str | None: ...

    async def input_value(self) -> str: ...


class _CountPage(Protocol):
    @property
    def url(self) -> str: ...

    def locator(self, selector: str) -> _CountLocator: ...

    def get_by_role(self, role: str, **kwargs: object) -> _CountLocator: ...

    def get_by_text(self, text: str, **kwargs: object) -> _CountLocator: ...


def _int_count(raw: object) -> int:
    return raw if isinstance(raw, int) and raw >= 0 else 0


def detail_path_class_token(raw: object) -> DetailPathClass:
    return "contacts_customer" if raw == "contacts_customer" else "other"


def opret_role_token(raw: object) -> OpretRole:
    if raw == "button":
        return "button"
    if raw == "link":
        return "link"
    return "none"


def href_path_class_token(raw: object) -> HrefPathClass:
    if raw == "invoices_new":
        return "invoices_new"
    if raw == "invoices_new_with_query":
        return "invoices_new_with_query"
    if raw == "other":
        return "other"
    return "none"


def href_query_token_class_token(raw: object) -> HrefQueryTokenClass:
    if raw == "contact":
        return "contact"
    if raw == "other":
        return "other"
    return "none"


def heading_token(raw: object) -> HeadingToken:
    if raw == "opret_faktura":
        return "opret_faktura"
    if raw == "other":
        return "other"
    return "none"


def proved_prebind_token(raw: object) -> ProvedPrebind:
    if raw == "customer_detail_opret_faktura":
        return "customer_detail_opret_faktura"
    return "none"


def classify_detail_path(url: object) -> DetailPathClass:
    """Return contacts_customer only for /contacts/:id/customer. Never store the URL."""

    if not isinstance(url, str) or not url:
        return "other"
    path = urlsplit(url).path or ""
    return "contacts_customer" if _CONTACTS_CUSTOMER.search(path) else "other"


def classify_href(href: object) -> tuple[HrefPathClass, HrefQueryTokenClass]:
    """Classify an invoice-create href. Never persist the href or query values."""

    if not isinstance(href, str) or not href.strip():
        return "none", "none"
    parsed = urlsplit(href)
    path = parsed.path or ""
    query = parsed.query or ""
    if not _INVOICES_NEW.match(path):
        return "other", _query_token_class(query)
    if query:
        return "invoices_new_with_query", _query_token_class(query)
    return "invoices_new", "none"


def _query_token_class(query: str) -> HrefQueryTokenClass:
    names = {key.lower() for key, _value in parse_qsl(query, keep_blank_values=True)}
    if names & CONTACT_QUERY_NAMES:
        return "contact"
    if names:
        return "other"
    return "none"


def classify_heading(text: object) -> HeadingToken:
    if not isinstance(text, str) or not text.strip():
        return "none"
    return "opret_faktura" if text.strip() == _OPRET else "other"


def unique_normal_action_from(payload: Mapping[str, object]) -> bool:
    return payload.get("exact_opret_faktura_count") == 1


def proved_prebind_from(payload: Mapping[str, object]) -> ProvedPrebind:
    if payload.get("unique_normal_action") is not True:
        return "none"
    if payload.get("destination_heading_token") != "opret_faktura":
        return "none"
    if payload.get("contact_input_matches_tag") is not True:
        return "none"
    return "customer_detail_opret_faktura"


def _key_is_present(payload: Mapping[str, object], key: PrebindKey) -> bool:
    value = payload.get(key)
    match key:
        case "detail_path_class":
            return value in DETAIL_PATH_CLASSES
        case (
            "tagged_name_visible"
            | "clicked_opret_faktura"
            | "contact_input_matches_tag"
            | "unique_normal_action"
        ):
            return isinstance(value, bool)
        case "exact_ret_count" | "exact_opret_faktura_count" | "contact_input_value_len":
            return isinstance(value, int) and value >= 0
        case "exact_opret_faktura_role":
            return value in OPRET_ROLES
        case "href_path_class":
            return value in HREF_PATH_CLASSES
        case "href_query_token_class":
            return value in HREF_QUERY_CLASSES
        case "destination_heading_token":
            return value in HEADING_TOKENS
        case "proved_prebind":
            return value in PROVED_TOKENS
        case "missing_keys":
            return isinstance(value, list)


def customer_detail_prebind_missing_keys(payload: Mapping[str, object]) -> list[str]:
    """Keys the prebind dump requires that this payload does not record."""

    if "detail_path_class" not in payload:
        return list(REQUIRED_CUSTOMER_DETAIL_PREBIND_KEYS)
    return [
        key for key in REQUIRED_CUSTOMER_DETAIL_PREBIND_KEYS if not _key_is_present(payload, key)
    ]


def empty_customer_detail_prebind() -> dict[str, object]:
    """Structurally complete prebind keys before a live inspect."""

    return {
        "detail_path_class": "other",
        "tagged_name_visible": False,
        "exact_ret_count": 0,
        "exact_opret_faktura_role": "none",
        "exact_opret_faktura_count": 0,
        "href_path_class": "none",
        "href_query_token_class": "none",
        "clicked_opret_faktura": False,
        "destination_heading_token": "none",
        "contact_input_value_len": 0,
        "contact_input_matches_tag": False,
        "unique_normal_action": False,
        "proved_prebind": "none",
        "missing_keys": [],
    }


async def _visible_count(locator: _CountLocator) -> int:
    try:
        total = await locator.count()
    except Exception:
        return 0
    visible = 0
    first = locator.first
    if total >= 1:
        try:
            if await first.is_visible():
                visible += 1
        except Exception:
            return 0
    return visible if total == 1 else (visible if total < 1 else total)


async def _exact_role_count(page: _CountPage, role: str, label: str) -> int:
    return await _visible_count(page.get_by_role(role, name=re.compile(rf"^{re.escape(label)}$")))


async def _exact_text_visible(page: _CountPage, label: str) -> bool:
    try:
        locator = page.get_by_text(label, exact=True)
        return await locator.count() >= 1 and await locator.first.is_visible()
    except Exception:
        return False


async def _heading_token(page: _CountPage) -> HeadingToken:
    heading = page.locator("h1")
    try:
        if await heading.count() < 1:
            return "none"
        return classify_heading(await heading.first.inner_text())
    except Exception:
        return "none"


async def _contact_input(page: _CountPage) -> tuple[int, bool, str]:
    field = page.locator("input[name='contact']")
    try:
        if await field.count() < 1:
            return 0, False, ""
        value = await field.first.input_value()
    except Exception:
        return 0, False, ""
    return len(value), False, value


def apply_customer_detail_prebind_dump(
    payload: Mapping[str, object],
    *,
    dump_path: Path | None = None,
) -> dict[str, object]:
    """Copy allowlisted keys and write the owner-only summary."""

    result = empty_customer_detail_prebind()
    result["detail_path_class"] = detail_path_class_token(payload.get("detail_path_class"))
    result["tagged_name_visible"] = payload.get("tagged_name_visible") is True
    result["exact_ret_count"] = _int_count(payload.get("exact_ret_count"))
    result["exact_opret_faktura_role"] = opret_role_token(payload.get("exact_opret_faktura_role"))
    result["exact_opret_faktura_count"] = _int_count(payload.get("exact_opret_faktura_count"))
    result["href_path_class"] = href_path_class_token(payload.get("href_path_class"))
    result["href_query_token_class"] = href_query_token_class_token(
        payload.get("href_query_token_class")
    )
    result["clicked_opret_faktura"] = payload.get("clicked_opret_faktura") is True
    result["destination_heading_token"] = heading_token(payload.get("destination_heading_token"))
    result["contact_input_value_len"] = _int_count(payload.get("contact_input_value_len"))
    result["contact_input_matches_tag"] = payload.get("contact_input_matches_tag") is True
    unique = unique_normal_action_from(result)
    result["unique_normal_action"] = unique
    proved = proved_prebind_from(result)
    result["proved_prebind"] = proved
    result["missing_keys"] = customer_detail_prebind_missing_keys(result)
    if not unique or proved == "none":
        result["code"] = "UI_CHANGED"
        result["message"] = "Billy customer detail has no proved Opret faktura prebind."
    summary = {key: result.get(key) for key in REQUIRED_CUSTOMER_DETAIL_PREBIND_KEYS}
    write_json(dump_path or CUSTOMER_DETAIL_PREBIND_DUMP, summary)
    return result


async def capture_customer_detail_prebind(
    page: _CountPage,
    *,
    tag: str,
    dump_path: Path | None = None,
) -> dict[str, object]:
    """Inspect exact customer-detail actions. Clicks Opret faktura only when unique."""

    payload = empty_customer_detail_prebind()
    payload["detail_path_class"] = classify_detail_path(page.url)
    payload["tagged_name_visible"] = await _exact_text_visible(page, tag)
    payload["exact_ret_count"] = await _exact_role_count(page, "button", _RET)
    if payload["exact_ret_count"] == 0:
        payload["exact_ret_count"] = 1 if await _exact_text_visible(page, _RET) else 0
    button_count = await _exact_role_count(page, "button", _OPRET)
    link_count = await _exact_role_count(page, "link", _OPRET)
    if button_count == 1 and link_count == 0:
        payload["exact_opret_faktura_role"] = "button"
        payload["exact_opret_faktura_count"] = 1
    elif link_count == 1 and button_count == 0:
        payload["exact_opret_faktura_role"] = "link"
        payload["exact_opret_faktura_count"] = 1
    else:
        payload["exact_opret_faktura_role"] = "none"
        payload["exact_opret_faktura_count"] = button_count + link_count
    href = ""
    if payload["exact_opret_faktura_role"] == "link":
        try:
            href = (
                await page.get_by_role(
                    "link", name=re.compile(rf"^{re.escape(_OPRET)}$")
                ).first.get_attribute("href")
                or ""
            )
        except Exception:
            href = ""
    href_path, href_query = classify_href(href)
    payload["href_path_class"] = href_path
    payload["href_query_token_class"] = href_query
    if payload["exact_opret_faktura_count"] == 1:
        role = str(payload["exact_opret_faktura_role"])
        control = page.get_by_role(role, name=re.compile(rf"^{re.escape(_OPRET)}$"))
        try:
            if await control.count() >= 1 and await control.first.is_visible():
                await control.first.click()
                payload["clicked_opret_faktura"] = True
                await asyncio.sleep(0.5)
        except Exception:
            payload["clicked_opret_faktura"] = False
    if payload["clicked_opret_faktura"] is True:
        payload["destination_heading_token"] = await _heading_token(page)
        value_len, _ignored, value = await _contact_input(page)
        payload["contact_input_value_len"] = value_len
        payload["contact_input_matches_tag"] = value == tag
        del value
    return apply_customer_detail_prebind_dump(payload, dump_path=dump_path)


def customer_detail_prebind_dump_is_delivered(path: Path | None = None) -> bool:
    """True when the owner dump already recorded the prebind inspect."""

    target = path or CUSTOMER_DETAIL_PREBIND_DUMP
    if not target.is_file():
        return False
    try:
        raw = json.loads(target.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return False
    if not isinstance(raw, dict):
        return False
    typed = cast(dict[str, object], raw)
    return customer_detail_prebind_missing_keys(typed) == []


def customer_detail_prebind_dump_json(payload: Mapping[str, object]) -> str:
    """Stable JSON for leak checks. Never includes source or URLs."""

    return json.dumps(dict(payload), sort_keys=True)


__all__ = [
    "CUSTOMER_DETAIL_PREBIND_DUMP",
    "REQUIRED_CUSTOMER_DETAIL_PREBIND_KEYS",
    "apply_customer_detail_prebind_dump",
    "capture_customer_detail_prebind",
    "classify_detail_path",
    "classify_heading",
    "classify_href",
    "customer_detail_prebind_dump_is_delivered",
    "customer_detail_prebind_dump_json",
    "customer_detail_prebind_missing_keys",
    "empty_customer_detail_prebind",
    "proved_prebind_from",
    "unique_normal_action_from",
]
