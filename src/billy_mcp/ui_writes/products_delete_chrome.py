"""Product list and inventory delete-chrome keys.

Never stores source, URLs, locators, ids, or product names.
"""

from __future__ import annotations

import json
import re
from collections.abc import Mapping
from pathlib import Path
from typing import Final, Literal, Protocol, cast
from urllib.parse import urlsplit

from billy_mcp.ui_writes.invoices_form_page import write_json

DeleteChromeKey = Literal[
    "products_path_class",
    "products_heading_token",
    "products_mere_open",
    "products_mere_slet_count",
    "products_mere_slet_produkt_count",
    "inventory_path_class",
    "inventory_heading_token",
    "inventory_slet_count",
    "inventory_slet_produkt_count",
    "save_cta_token",
    "create_form_open",
    "name_field_visible",
    "proved_delete_path",
    "missing_keys",
]
ProductsPathClass = Literal["products", "other"]
InventoryPathClass = Literal["inventory", "other"]
ProductsHeadingToken = Literal["produkter", "other", "none"]
InventoryHeadingToken = Literal["lagermodul", "other", "none"]
SaveCtaToken = Literal["gem", "other", "none"]
ProvedDeletePath = Literal[
    "products_mere_slet",
    "products_mere_slet_produkt",
    "inventory_slet",
    "inventory_slet_produkt",
    "none",
]

REQUIRED_PRODUCTS_DELETE_CHROME_KEYS: Final[tuple[DeleteChromeKey, ...]] = (
    "products_path_class",
    "products_heading_token",
    "products_mere_open",
    "products_mere_slet_count",
    "products_mere_slet_produkt_count",
    "inventory_path_class",
    "inventory_heading_token",
    "inventory_slet_count",
    "inventory_slet_produkt_count",
    "save_cta_token",
    "create_form_open",
    "name_field_visible",
    "proved_delete_path",
    "missing_keys",
)
PRODUCTS_PATH_CLASSES: Final[frozenset[str]] = frozenset({"products", "other"})
INVENTORY_PATH_CLASSES: Final[frozenset[str]] = frozenset({"inventory", "other"})
PRODUCTS_HEADINGS: Final[frozenset[str]] = frozenset({"produkter", "other", "none"})
INVENTORY_HEADINGS: Final[frozenset[str]] = frozenset({"lagermodul", "other", "none"})
SAVE_CTA_TOKENS: Final[frozenset[str]] = frozenset({"gem", "other", "none"})
PROVED_DELETE_PATHS: Final[frozenset[str]] = frozenset(
    {
        "products_mere_slet",
        "products_mere_slet_produkt",
        "inventory_slet",
        "inventory_slet_produkt",
        "none",
    }
)
_PRODUCTS_PATH = re.compile(r"^/[^/]+/products/?$")
_INVENTORY_PATH = re.compile(r"^/[^/]+/inventory/?$")
_MERE = "Mere"
_SLET = "Slet"
_SLET_PRODUKT = "Slet produkt"
_GEM = "Gem"
_OPRET = "Opret produkt"
_PRODUKTER = "Produkter"
_LAGERMODUL = "Lagermodul"
PRODUCTS_DELETE_CHROME_DUMP: Final = (
    Path.home() / ".local" / "share" / "billy-mcp" / "inspect-live-products-delete-chrome.json"
)


class _CountLocator(Protocol):
    @property
    def first(self) -> _CountLocator: ...

    async def count(self) -> int: ...

    async def is_visible(self) -> bool: ...

    async def click(self) -> None: ...

    async def inner_text(self) -> str: ...


class _CountPage(Protocol):
    @property
    def url(self) -> str: ...

    def locator(self, selector: str) -> _CountLocator: ...

    def get_by_role(self, role: str, **kwargs: object) -> _CountLocator: ...

    def get_by_text(self, text: str, **kwargs: object) -> _CountLocator: ...


def _int_count(raw: object) -> int:
    return raw if isinstance(raw, int) and raw >= 0 else 0


def products_path_class_token(raw: object) -> ProductsPathClass:
    return "products" if raw == "products" else "other"


def inventory_path_class_token(raw: object) -> InventoryPathClass:
    return "inventory" if raw == "inventory" else "other"


def products_heading_token(raw: object) -> ProductsHeadingToken:
    if raw == "produkter":
        return "produkter"
    if raw == "other":
        return "other"
    return "none"


def inventory_heading_token(raw: object) -> InventoryHeadingToken:
    if raw == "lagermodul":
        return "lagermodul"
    if raw == "other":
        return "other"
    return "none"


def save_cta_token(raw: object) -> SaveCtaToken:
    if raw == "gem":
        return "gem"
    if raw == "other":
        return "other"
    return "none"


def proved_delete_path_token(raw: object) -> ProvedDeletePath:
    if raw in {
        "products_mere_slet",
        "products_mere_slet_produkt",
        "inventory_slet",
        "inventory_slet_produkt",
    }:
        return cast(ProvedDeletePath, raw)
    return "none"


def classify_products_path(url: object) -> ProductsPathClass:
    """Return products only for /:org/products. Never store the URL."""

    if not isinstance(url, str) or not url:
        return "other"
    return "products" if _PRODUCTS_PATH.match(urlsplit(url).path or "") else "other"


def classify_inventory_path(url: object) -> InventoryPathClass:
    """Return inventory only for /:org/inventory. Never store the URL."""

    if not isinstance(url, str) or not url:
        return "other"
    return "inventory" if _INVENTORY_PATH.match(urlsplit(url).path or "") else "other"


def classify_products_heading(text: object) -> ProductsHeadingToken:
    if not isinstance(text, str) or not text.strip():
        return "none"
    return "produkter" if text.strip() == _PRODUKTER else "other"


def classify_inventory_heading(text: object) -> InventoryHeadingToken:
    if not isinstance(text, str) or not text.strip():
        return "none"
    return "lagermodul" if text.strip() == _LAGERMODUL else "other"


def classify_save_cta(text: object) -> SaveCtaToken:
    if not isinstance(text, str) or not text.strip():
        return "none"
    return "gem" if text.strip() == _GEM else "other"


def proved_delete_path_from(payload: Mapping[str, object]) -> ProvedDeletePath:
    """Return the first unique exact-count-1 delete path. Else none."""

    candidates: tuple[tuple[str, ProvedDeletePath], ...] = (
        ("products_mere_slet_count", "products_mere_slet"),
        ("products_mere_slet_produkt_count", "products_mere_slet_produkt"),
        ("inventory_slet_count", "inventory_slet"),
        ("inventory_slet_produkt_count", "inventory_slet_produkt"),
    )
    matched: list[ProvedDeletePath] = [token for key, token in candidates if payload.get(key) == 1]
    if len(matched) != 1:
        return "none"
    return matched[0]


def _key_is_present(payload: Mapping[str, object], key: DeleteChromeKey) -> bool:
    value = payload.get(key)
    match key:
        case "products_path_class":
            return value in PRODUCTS_PATH_CLASSES
        case "inventory_path_class":
            return value in INVENTORY_PATH_CLASSES
        case "products_heading_token":
            return value in PRODUCTS_HEADINGS
        case "inventory_heading_token":
            return value in INVENTORY_HEADINGS
        case "products_mere_open" | "create_form_open" | "name_field_visible":
            return isinstance(value, bool)
        case (
            "products_mere_slet_count"
            | "products_mere_slet_produkt_count"
            | "inventory_slet_count"
            | "inventory_slet_produkt_count"
        ):
            return isinstance(value, int) and value >= 0
        case "save_cta_token":
            return value in SAVE_CTA_TOKENS
        case "proved_delete_path":
            return value in PROVED_DELETE_PATHS
        case "missing_keys":
            return isinstance(value, list)


def products_delete_chrome_missing_keys(payload: Mapping[str, object]) -> list[str]:
    """Keys the delete-chrome dump requires that this payload does not record."""

    if "products_path_class" not in payload:
        return list(REQUIRED_PRODUCTS_DELETE_CHROME_KEYS)
    return [
        key for key in REQUIRED_PRODUCTS_DELETE_CHROME_KEYS if not _key_is_present(payload, key)
    ]


def empty_products_delete_chrome() -> dict[str, object]:
    """Structurally complete delete-chrome keys before a live inspect."""

    return {
        "products_path_class": "other",
        "products_heading_token": "none",
        "products_mere_open": False,
        "products_mere_slet_count": 0,
        "products_mere_slet_produkt_count": 0,
        "inventory_path_class": "other",
        "inventory_heading_token": "none",
        "inventory_slet_count": 0,
        "inventory_slet_produkt_count": 0,
        "save_cta_token": "none",
        "create_form_open": False,
        "name_field_visible": False,
        "proved_delete_path": "none",
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


async def _heading_text(page: _CountPage) -> str:
    heading = page.locator("h1")
    try:
        if await heading.count() < 1:
            return ""
        return (await heading.first.inner_text()).strip()
    except Exception:
        return ""


async def click_exact_label(page: _CountPage, label: str) -> bool:
    """Click the unique exact label. Never force. Never run page scripts."""

    button = page.get_by_role("button", name=re.compile(rf"^{re.escape(label)}$"))
    if await _visible_count(button) == 1:
        try:
            await button.first.click()
            return True
        except Exception:
            return False
    text = page.get_by_text(label, exact=True)
    if await _visible_count(text) == 1:
        try:
            await text.first.click()
            return True
        except Exception:
            return False
    return False


def apply_products_delete_chrome_dump(
    payload: Mapping[str, object],
    *,
    dump_path: Path | None = None,
) -> dict[str, object]:
    """Copy allowlisted keys and write the owner-only summary."""

    result = empty_products_delete_chrome()
    result["products_path_class"] = products_path_class_token(payload.get("products_path_class"))
    result["products_heading_token"] = products_heading_token(payload.get("products_heading_token"))
    result["products_mere_open"] = payload.get("products_mere_open") is True
    result["products_mere_slet_count"] = _int_count(payload.get("products_mere_slet_count"))
    result["products_mere_slet_produkt_count"] = _int_count(
        payload.get("products_mere_slet_produkt_count")
    )
    result["inventory_path_class"] = inventory_path_class_token(payload.get("inventory_path_class"))
    result["inventory_heading_token"] = inventory_heading_token(
        payload.get("inventory_heading_token")
    )
    result["inventory_slet_count"] = _int_count(payload.get("inventory_slet_count"))
    result["inventory_slet_produkt_count"] = _int_count(payload.get("inventory_slet_produkt_count"))
    result["save_cta_token"] = save_cta_token(payload.get("save_cta_token"))
    result["create_form_open"] = payload.get("create_form_open") is True
    result["name_field_visible"] = payload.get("name_field_visible") is True
    proved = proved_delete_path_from(result)
    result["proved_delete_path"] = proved
    result["missing_keys"] = products_delete_chrome_missing_keys(result)
    if proved == "none":
        result["code"] = "UI_CHANGED"
        result["message"] = "Billy product chrome has no unique UI delete path."
    summary = {key: result.get(key) for key in REQUIRED_PRODUCTS_DELETE_CHROME_KEYS}
    write_json(dump_path or PRODUCTS_DELETE_CHROME_DUMP, summary)
    return result


async def inspect_products_list_chrome(page: _CountPage) -> dict[str, object]:
    """Count exact Mere delete labels on the current products list page."""

    payload: dict[str, object] = {
        "products_path_class": classify_products_path(page.url),
        "products_heading_token": classify_products_heading(await _heading_text(page)),
        "products_mere_open": False,
        "products_mere_slet_count": 0,
        "products_mere_slet_produkt_count": 0,
    }
    opened = await click_exact_label(page, _MERE)
    payload["products_mere_open"] = opened
    if opened:
        slet = await _exact_role_count(page, "menuitem", _SLET)
        if slet == 0:
            slet = await _exact_text_count(page, _SLET)
        produkt = await _exact_role_count(page, "menuitem", _SLET_PRODUKT)
        if produkt == 0:
            produkt = await _exact_text_count(page, _SLET_PRODUKT)
        payload["products_mere_slet_count"] = slet
        payload["products_mere_slet_produkt_count"] = produkt
    return payload


async def inspect_inventory_chrome(page: _CountPage, *, open_create: bool) -> dict[str, object]:
    """Count exact inventory delete labels. Open create only to classify save CTA."""

    payload: dict[str, object] = {
        "inventory_path_class": classify_inventory_path(page.url),
        "inventory_heading_token": classify_inventory_heading(await _heading_text(page)),
        "inventory_slet_count": await _exact_text_count(page, _SLET),
        "inventory_slet_produkt_count": await _exact_text_count(page, _SLET_PRODUKT),
        "save_cta_token": "none",
        "create_form_open": False,
        "name_field_visible": False,
    }
    if not open_create:
        return payload
    opened = await click_exact_label(page, _OPRET)
    if not opened:
        return payload
    name = page.locator("input[name='name']")
    try:
        payload["name_field_visible"] = await name.count() >= 1 and await name.first.is_visible()
    except Exception:
        payload["name_field_visible"] = False
    payload["create_form_open"] = payload["name_field_visible"] is True
    gem = await _exact_role_count(page, "button", _GEM)
    if gem == 0:
        gem = await _exact_text_count(page, _GEM)
    if gem >= 1:
        payload["save_cta_token"] = "gem"
    elif payload["create_form_open"] is True:
        payload["save_cta_token"] = "other"
    return payload


def products_delete_chrome_dump_is_delivered(path: Path | None = None) -> bool:
    """True when the owner dump already recorded the delete-chrome inspect."""

    target = path or PRODUCTS_DELETE_CHROME_DUMP
    if not target.is_file():
        return False
    try:
        raw = json.loads(target.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return False
    if not isinstance(raw, dict):
        return False
    return products_delete_chrome_missing_keys(cast(dict[str, object], raw)) == []


def products_delete_chrome_dump_json(payload: Mapping[str, object]) -> str:
    """Stable JSON for leak checks. Never includes source or URLs."""

    return json.dumps(dict(payload), sort_keys=True)


__all__ = [
    "PRODUCTS_DELETE_CHROME_DUMP",
    "REQUIRED_PRODUCTS_DELETE_CHROME_KEYS",
    "apply_products_delete_chrome_dump",
    "classify_inventory_heading",
    "classify_inventory_path",
    "classify_products_heading",
    "classify_products_path",
    "classify_save_cta",
    "click_exact_label",
    "empty_products_delete_chrome",
    "inspect_inventory_chrome",
    "inspect_products_list_chrome",
    "products_delete_chrome_dump_is_delivered",
    "products_delete_chrome_dump_json",
    "products_delete_chrome_missing_keys",
    "proved_delete_path_from",
]
