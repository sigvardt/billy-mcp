"""Product list archive-filter contract keys.

Never stores source, URLs, locators, ids, or product names.
Never clicks list menus, create, save, or archive.
"""

from __future__ import annotations

import json
import re
from collections.abc import Mapping
from pathlib import Path
from typing import Final, Literal, Protocol, cast

from billy_mcp.ui_writes.invoices_form_page import write_json
from billy_mcp.ui_writes.products_delete_chrome import (
    classify_products_heading,
    classify_products_path,
    products_heading_token,
    products_path_class_token,
)

ArchiveListKey = Literal[
    "products_path_class",
    "products_heading_token",
    "search_control_visible",
    "vis_arkiverede_count",
    "arkiverede_count",
    "skjul_arkiverede_count",
    "archived_filter_token",
    "unique_restore_readback",
    "proved_bind",
    "missing_keys",
]
ProductsPathClass = Literal["products", "other"]
ProductsHeadingToken = Literal["produkter", "other", "none"]
ArchivedFilterToken = Literal["vis_arkiverede", "arkiverede", "skjul_arkiverede", "none"]
UniqueRestoreReadback = Literal["show_archived_filter", "none"]
ProvedBind = Literal["none"]

REQUIRED_PRODUCTS_ARCHIVE_LIST_KEYS: Final[tuple[ArchiveListKey, ...]] = (
    "products_path_class",
    "products_heading_token",
    "search_control_visible",
    "vis_arkiverede_count",
    "arkiverede_count",
    "skjul_arkiverede_count",
    "archived_filter_token",
    "unique_restore_readback",
    "proved_bind",
    "missing_keys",
)
PRODUCTS_PATH_CLASSES: Final[frozenset[str]] = frozenset({"products", "other"})
PRODUCTS_HEADINGS: Final[frozenset[str]] = frozenset({"produkter", "other", "none"})
ARCHIVED_FILTER_TOKENS: Final[frozenset[str]] = frozenset(
    {"vis_arkiverede", "arkiverede", "skjul_arkiverede", "none"}
)
UNIQUE_RESTORE_READBACKS: Final[frozenset[str]] = frozenset({"show_archived_filter", "none"})
PROVED_BINDS: Final[frozenset[str]] = frozenset({"none"})
_VIS = "Vis arkiverede"
_ARK = "Arkiverede"
_SKJUL = "Skjul arkiverede"
_SEARCH = "[data-cy='search-button']"
PRODUCTS_ARCHIVE_LIST_DUMP: Final = (
    Path.home() / ".local" / "share" / "billy-mcp" / "inspect-live-products-archive-list.json"
)


class _CountLocator(Protocol):
    @property
    def first(self) -> _CountLocator: ...

    async def count(self) -> int: ...

    async def is_visible(self) -> bool: ...

    async def inner_text(self) -> str: ...


class _CountPage(Protocol):
    @property
    def url(self) -> str: ...

    def locator(self, selector: str) -> _CountLocator: ...

    def get_by_role(self, role: str, **kwargs: object) -> _CountLocator: ...

    def get_by_text(self, text: str, **kwargs: object) -> _CountLocator: ...


def _int_count(raw: object) -> int:
    return raw if isinstance(raw, int) and raw >= 0 else 0


def archived_filter_token_from(payload: Mapping[str, object]) -> ArchivedFilterToken:
    counts: dict[ArchivedFilterToken, int] = {
        "vis_arkiverede": _int_count(payload.get("vis_arkiverede_count")),
        "arkiverede": _int_count(payload.get("arkiverede_count")),
        "skjul_arkiverede": _int_count(payload.get("skjul_arkiverede_count")),
    }
    ones: list[ArchivedFilterToken] = [key for key, value in counts.items() if value == 1]
    zeros: list[ArchivedFilterToken] = [key for key, value in counts.items() if value == 0]
    if len(ones) == 1 and len(zeros) == 2:
        return ones[0]
    return "none"


def unique_restore_readback_from(payload: Mapping[str, object]) -> UniqueRestoreReadback:
    return "show_archived_filter" if archived_filter_token_from(payload) != "none" else "none"


def _key_is_present(payload: Mapping[str, object], key: ArchiveListKey) -> bool:
    value = payload.get(key)
    match key:
        case "products_path_class":
            return value in PRODUCTS_PATH_CLASSES
        case "products_heading_token":
            return value in PRODUCTS_HEADINGS
        case "search_control_visible":
            return isinstance(value, bool)
        case "vis_arkiverede_count" | "arkiverede_count" | "skjul_arkiverede_count":
            return isinstance(value, int) and value >= 0
        case "archived_filter_token":
            return value in ARCHIVED_FILTER_TOKENS
        case "unique_restore_readback":
            return value in UNIQUE_RESTORE_READBACKS
        case "proved_bind":
            return value in PROVED_BINDS
        case "missing_keys":
            return isinstance(value, list)


def products_archive_list_missing_keys(payload: Mapping[str, object]) -> list[str]:
    """Keys the archive-list dump requires that this payload does not record."""

    if "products_path_class" not in payload:
        return list(REQUIRED_PRODUCTS_ARCHIVE_LIST_KEYS)
    return [key for key in REQUIRED_PRODUCTS_ARCHIVE_LIST_KEYS if not _key_is_present(payload, key)]


def empty_products_archive_list() -> dict[str, object]:
    """Structurally complete archive-list keys before a live inspect."""

    return {
        "products_path_class": "other",
        "products_heading_token": "none",
        "search_control_visible": False,
        "vis_arkiverede_count": 0,
        "arkiverede_count": 0,
        "skjul_arkiverede_count": 0,
        "archived_filter_token": "none",
        "unique_restore_readback": "none",
        "proved_bind": "none",
        "missing_keys": [],
    }


async def _visible_count(locator: _CountLocator) -> int:
    try:
        total = await locator.count()
    except Exception:
        return 0
    if total < 1:
        return 0
    try:
        if total == 1:
            return 1 if await locator.first.is_visible() else 0
    except Exception:
        return 0
    return total


async def _exact_role_count(page: _CountPage, role: str, label: str) -> int:
    return await _visible_count(page.get_by_role(role, name=re.compile(rf"^{re.escape(label)}$")))


async def _exact_text_count(page: _CountPage, label: str) -> int:
    return await _visible_count(page.get_by_text(label, exact=True))


async def _label_count(page: _CountPage, label: str) -> int:
    for role in ("button", "checkbox", "tab"):
        counted = await _exact_role_count(page, role, label)
        if counted:
            return counted
    return await _exact_text_count(page, label)


def apply_products_archive_list_dump(
    payload: Mapping[str, object],
    *,
    dump_path: Path | None = None,
) -> dict[str, object]:
    """Copy allowlisted keys and write the owner-only summary."""

    result = empty_products_archive_list()
    result["products_path_class"] = products_path_class_token(payload.get("products_path_class"))
    result["products_heading_token"] = products_heading_token(payload.get("products_heading_token"))
    result["search_control_visible"] = payload.get("search_control_visible") is True
    result["vis_arkiverede_count"] = _int_count(payload.get("vis_arkiverede_count"))
    result["arkiverede_count"] = _int_count(payload.get("arkiverede_count"))
    result["skjul_arkiverede_count"] = _int_count(payload.get("skjul_arkiverede_count"))
    result["archived_filter_token"] = archived_filter_token_from(result)
    result["unique_restore_readback"] = unique_restore_readback_from(result)
    result["proved_bind"] = "none"
    result["missing_keys"] = products_archive_list_missing_keys(result)
    if result["unique_restore_readback"] == "none":
        result["code"] = "UI_CHANGED"
        result["message"] = "Billy product list has no unique archived-filter restore path."
    summary = {key: result.get(key) for key in REQUIRED_PRODUCTS_ARCHIVE_LIST_KEYS}
    write_json(dump_path or PRODUCTS_ARCHIVE_LIST_DUMP, summary)
    return result


async def inspect_products_archive_list(page: _CountPage) -> dict[str, object]:
    """Classify list archive chrome. Count only. Never click a control."""

    search = page.locator(_SEARCH)
    search_visible = False
    try:
        search_visible = await search.count() >= 1 and await search.first.is_visible()
    except Exception:
        search_visible = False
    return {
        "products_path_class": classify_products_path(page.url),
        "products_heading_token": classify_products_heading(await _heading_text(page)),
        "search_control_visible": search_visible,
        "vis_arkiverede_count": await _label_count(page, _VIS),
        "arkiverede_count": await _label_count(page, _ARK),
        "skjul_arkiverede_count": await _label_count(page, _SKJUL),
    }


async def _heading_text(page: _CountPage) -> str:
    heading = page.locator("h1")
    try:
        if await heading.count() < 1:
            return ""
        return (await heading.first.inner_text()).strip()
    except Exception:
        return ""


def products_archive_list_dump_is_delivered(path: Path | None = None) -> bool:
    """True when the owner dump already recorded the archive-list inspect."""

    target = path or PRODUCTS_ARCHIVE_LIST_DUMP
    if not target.is_file():
        return False
    try:
        raw = json.loads(target.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return False
    if not isinstance(raw, dict):
        return False
    return products_archive_list_missing_keys(cast(dict[str, object], raw)) == []


def products_archive_list_dump_json(payload: Mapping[str, object]) -> str:
    """Stable JSON for leak checks. Never includes source or URLs."""

    return json.dumps(dict(payload), sort_keys=True)


__all__ = [
    "PRODUCTS_ARCHIVE_LIST_DUMP",
    "REQUIRED_PRODUCTS_ARCHIVE_LIST_KEYS",
    "apply_products_archive_list_dump",
    "archived_filter_token_from",
    "empty_products_archive_list",
    "inspect_products_archive_list",
    "products_archive_list_dump_is_delivered",
    "products_archive_list_dump_json",
    "products_archive_list_missing_keys",
    "unique_restore_readback_from",
]
