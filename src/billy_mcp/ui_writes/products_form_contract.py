"""Official product create-dialog contract keys.

Never stores source, URLs, locators, ids, or product names.
"""

from __future__ import annotations

import json
import re
from collections.abc import Mapping
from pathlib import Path
from typing import Final, Literal, Protocol, cast

from billy_mcp.ui_writes.invoices_form_page import write_json
from billy_mcp.ui_writes.products_delete_chrome import (
    classify_inventory_heading,
    classify_inventory_path,
    click_exact_label,
    inventory_heading_token,
    inventory_path_class_token,
)

FormContractKey = Literal[
    "inventory_path_class",
    "inventory_heading_token",
    "create_form_open",
    "dialog_heading_token",
    "name_field_visible",
    "gem_produkt_count",
    "gem_count",
    "save_cta_token",
    "arkiveret_count",
    "cleanup_token",
    "unique_cleanup_path",
    "proved_submit",
    "missing_keys",
]
InventoryPathClass = Literal["inventory", "other"]
InventoryHeadingToken = Literal["lagermodul", "other", "none"]
DialogHeadingToken = Literal["opret_produkt", "ret_produkt", "other", "none"]
SaveCtaToken = Literal["gem_produkt", "gem", "other", "none"]
CleanupToken = Literal["archive_checkbox", "none"]
UniqueCleanupPath = Literal["archive_checkbox", "none"]
ProvedSubmit = Literal["gem_produkt", "none"]

REQUIRED_PRODUCTS_FORM_CONTRACT_KEYS: Final[tuple[FormContractKey, ...]] = (
    "inventory_path_class",
    "inventory_heading_token",
    "create_form_open",
    "dialog_heading_token",
    "name_field_visible",
    "gem_produkt_count",
    "gem_count",
    "save_cta_token",
    "arkiveret_count",
    "cleanup_token",
    "unique_cleanup_path",
    "proved_submit",
    "missing_keys",
)
INVENTORY_PATH_CLASSES: Final[frozenset[str]] = frozenset({"inventory", "other"})
INVENTORY_HEADINGS: Final[frozenset[str]] = frozenset({"lagermodul", "other", "none"})
DIALOG_HEADINGS: Final[frozenset[str]] = frozenset(
    {"opret_produkt", "ret_produkt", "other", "none"}
)
SAVE_CTA_TOKENS: Final[frozenset[str]] = frozenset({"gem_produkt", "gem", "other", "none"})
CLEANUP_TOKENS: Final[frozenset[str]] = frozenset({"archive_checkbox", "none"})
UNIQUE_CLEANUP_PATHS: Final[frozenset[str]] = frozenset({"archive_checkbox", "none"})
PROVED_SUBMITS: Final[frozenset[str]] = frozenset({"gem_produkt", "none"})
_OPRET = "Opret produkt"
_RET = "Ret produkt"
_GEM = "Gem"
_GEM_PRODUKT = "Gem produkt"
_ARKIVERET = "Arkiveret (skjul fra lister)"
PRODUCTS_FORM_CONTRACT_DUMP: Final = (
    Path.home() / ".local" / "share" / "billy-mcp" / "inspect-live-products-form-contract.json"
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


def dialog_heading_token(raw: object) -> DialogHeadingToken:
    if raw in {"opret_produkt", "ret_produkt", "other"}:
        return cast(DialogHeadingToken, raw)
    return "none"


def save_cta_token(raw: object) -> SaveCtaToken:
    if raw in {"gem_produkt", "gem", "other"}:
        return cast(SaveCtaToken, raw)
    return "none"


def cleanup_token(raw: object) -> CleanupToken:
    return "archive_checkbox" if raw == "archive_checkbox" else "none"


def unique_cleanup_path_token(raw: object) -> UniqueCleanupPath:
    return "archive_checkbox" if raw == "archive_checkbox" else "none"


def proved_submit_token(raw: object) -> ProvedSubmit:
    return "gem_produkt" if raw == "gem_produkt" else "none"


def classify_dialog_heading(text: object) -> DialogHeadingToken:
    if not isinstance(text, str) or not text.strip():
        return "none"
    stripped = text.strip()
    if stripped == _OPRET:
        return "opret_produkt"
    if stripped == _RET:
        return "ret_produkt"
    return "other"


def classify_save_cta(
    *,
    gem_produkt_count: int,
    gem_count: int,
    create_form_open: bool,
) -> SaveCtaToken:
    if gem_produkt_count == 1:
        return "gem_produkt"
    if gem_count == 1 and gem_produkt_count == 0:
        return "gem"
    if create_form_open:
        return "other"
    return "none"


def classify_dialog_heading_from_counts(*, opret_count: int, ret_count: int) -> DialogHeadingToken:
    if opret_count == 1 and ret_count == 0:
        return "opret_produkt"
    if ret_count == 1 and opret_count == 0:
        return "ret_produkt"
    if opret_count == 0 and ret_count == 0:
        return "none"
    return "other"


def proved_submit_from(payload: Mapping[str, object]) -> ProvedSubmit:
    return "gem_produkt" if payload.get("gem_produkt_count") == 1 else "none"


def unique_cleanup_path_from(payload: Mapping[str, object]) -> UniqueCleanupPath:
    return "archive_checkbox" if payload.get("arkiveret_count") == 1 else "none"


def cleanup_token_from(payload: Mapping[str, object]) -> CleanupToken:
    return unique_cleanup_path_from(payload)


def _key_is_present(payload: Mapping[str, object], key: FormContractKey) -> bool:
    value = payload.get(key)
    match key:
        case "inventory_path_class":
            return value in INVENTORY_PATH_CLASSES
        case "inventory_heading_token":
            return value in INVENTORY_HEADINGS
        case "create_form_open" | "name_field_visible":
            return isinstance(value, bool)
        case "dialog_heading_token":
            return value in DIALOG_HEADINGS
        case "gem_produkt_count" | "gem_count" | "arkiveret_count":
            return isinstance(value, int) and value >= 0
        case "save_cta_token":
            return value in SAVE_CTA_TOKENS
        case "cleanup_token":
            return value in CLEANUP_TOKENS
        case "unique_cleanup_path":
            return value in UNIQUE_CLEANUP_PATHS
        case "proved_submit":
            return value in PROVED_SUBMITS
        case "missing_keys":
            return isinstance(value, list)


def products_form_contract_missing_keys(payload: Mapping[str, object]) -> list[str]:
    """Keys the form-contract dump requires that this payload does not record."""

    if "inventory_path_class" not in payload:
        return list(REQUIRED_PRODUCTS_FORM_CONTRACT_KEYS)
    return [
        key for key in REQUIRED_PRODUCTS_FORM_CONTRACT_KEYS if not _key_is_present(payload, key)
    ]


def empty_products_form_contract() -> dict[str, object]:
    """Structurally complete form-contract keys before a live inspect."""

    return {
        "inventory_path_class": "other",
        "inventory_heading_token": "none",
        "create_form_open": False,
        "dialog_heading_token": "none",
        "name_field_visible": False,
        "gem_produkt_count": 0,
        "gem_count": 0,
        "save_cta_token": "none",
        "arkiveret_count": 0,
        "cleanup_token": "none",
        "unique_cleanup_path": "none",
        "proved_submit": "none",
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


def apply_products_form_contract_dump(
    payload: Mapping[str, object],
    *,
    dump_path: Path | None = None,
) -> dict[str, object]:
    """Copy allowlisted keys and write the owner-only summary."""

    result = empty_products_form_contract()
    result["inventory_path_class"] = inventory_path_class_token(payload.get("inventory_path_class"))
    result["inventory_heading_token"] = inventory_heading_token(
        payload.get("inventory_heading_token")
    )
    result["create_form_open"] = payload.get("create_form_open") is True
    result["dialog_heading_token"] = dialog_heading_token(payload.get("dialog_heading_token"))
    result["name_field_visible"] = payload.get("name_field_visible") is True
    result["gem_produkt_count"] = _int_count(payload.get("gem_produkt_count"))
    result["gem_count"] = _int_count(payload.get("gem_count"))
    result["arkiveret_count"] = _int_count(payload.get("arkiveret_count"))
    result["save_cta_token"] = classify_save_cta(
        gem_produkt_count=int(result["gem_produkt_count"]),
        gem_count=int(result["gem_count"]),
        create_form_open=result["create_form_open"] is True,
    )
    result["unique_cleanup_path"] = unique_cleanup_path_from(result)
    result["cleanup_token"] = cleanup_token_from(result)
    result["proved_submit"] = proved_submit_from(result)
    result["missing_keys"] = products_form_contract_missing_keys(result)
    if result["proved_submit"] == "none" or result["unique_cleanup_path"] == "none":
        result["code"] = "UI_CHANGED"
        result["message"] = "Billy product dialog is not a proved submit-plus-archive path."
    summary = {key: result.get(key) for key in REQUIRED_PRODUCTS_FORM_CONTRACT_KEYS}
    write_json(dump_path or PRODUCTS_FORM_CONTRACT_DUMP, summary)
    return result


async def inspect_products_form_contract(
    page: _CountPage,
    *,
    open_create: bool,
) -> dict[str, object]:
    """Classify official save and archive controls. Never click save or archive."""

    payload: dict[str, object] = {
        "inventory_path_class": classify_inventory_path(page.url),
        "inventory_heading_token": classify_inventory_heading(
            await _heading_text(page),
        ),
        "create_form_open": False,
        "dialog_heading_token": "none",
        "name_field_visible": False,
        "gem_produkt_count": 0,
        "gem_count": 0,
        "arkiveret_count": 0,
    }
    if open_create:
        opened = await click_exact_label(page, _OPRET)
        if opened:
            name = page.locator("input[name='name']")
            try:
                payload["name_field_visible"] = (
                    await name.count() >= 1 and await name.first.is_visible()
                )
            except Exception:
                payload["name_field_visible"] = False
            payload["create_form_open"] = payload["name_field_visible"] is True
    opret_heading = await _exact_role_count(page, "heading", _OPRET)
    ret_heading = await _exact_role_count(page, "heading", _RET)
    payload["dialog_heading_token"] = classify_dialog_heading_from_counts(
        opret_count=opret_heading,
        ret_count=ret_heading,
    )
    gem_produkt = await _exact_role_count(page, "button", _GEM_PRODUKT)
    if gem_produkt == 0:
        gem_produkt = await _exact_text_count(page, _GEM_PRODUKT)
    gem = await _exact_role_count(page, "button", _GEM)
    if gem == 0:
        gem = await _exact_text_count(page, _GEM)
    payload["gem_produkt_count"] = gem_produkt
    payload["gem_count"] = gem
    arkiveret = await _exact_role_count(page, "checkbox", _ARKIVERET)
    if arkiveret == 0:
        arkiveret = await _exact_text_count(page, _ARKIVERET)
    payload["arkiveret_count"] = arkiveret
    return payload


async def _heading_text(page: _CountPage) -> str:
    heading = page.locator("h1")
    try:
        if await heading.count() < 1:
            return ""
        return (await heading.first.inner_text()).strip()
    except Exception:
        return ""


def products_form_contract_dump_is_delivered(path: Path | None = None) -> bool:
    """True when the owner dump already recorded the form-contract inspect."""

    target = path or PRODUCTS_FORM_CONTRACT_DUMP
    if not target.is_file():
        return False
    try:
        raw = json.loads(target.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return False
    if not isinstance(raw, dict):
        return False
    return products_form_contract_missing_keys(cast(dict[str, object], raw)) == []


def products_form_contract_dump_json(payload: Mapping[str, object]) -> str:
    """Stable JSON for leak checks. Never includes source or URLs."""

    return json.dumps(dict(payload), sort_keys=True)


__all__ = [
    "PRODUCTS_FORM_CONTRACT_DUMP",
    "REQUIRED_PRODUCTS_FORM_CONTRACT_KEYS",
    "apply_products_form_contract_dump",
    "classify_dialog_heading",
    "classify_dialog_heading_from_counts",
    "classify_save_cta",
    "empty_products_form_contract",
    "inspect_products_form_contract",
    "products_form_contract_dump_is_delivered",
    "products_form_contract_dump_json",
    "products_form_contract_missing_keys",
    "proved_submit_from",
    "unique_cleanup_path_from",
]
