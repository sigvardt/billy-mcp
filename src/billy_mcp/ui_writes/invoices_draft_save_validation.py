"""Exact Gem som kladde validation-open keys on invoices/new.

Never stores source, URLs, locators, ids, or customer names.
"""

from __future__ import annotations

import asyncio
import json
import re
from collections.abc import Mapping
from pathlib import Path
from typing import Final, Literal, Protocol, cast
from urllib.parse import urlsplit

from billy_mcp.ui_writes.invoices_form_page import write_json

DraftSaveKey = Literal[
    "validation_message_present",
    "ingen_kontakter_count",
    "opret_ny_count",
    "option_role_count",
    "gem_clicked",
    "invoice_persisted",
    "proved_bind",
    "missing_keys",
]
ProvedBind = Literal["draft_save_validation_existing_option", "none"]

REQUIRED_DRAFT_SAVE_VALIDATION_KEYS: Final[tuple[DraftSaveKey, ...]] = (
    "validation_message_present",
    "ingen_kontakter_count",
    "opret_ny_count",
    "option_role_count",
    "gem_clicked",
    "invoice_persisted",
    "proved_bind",
    "missing_keys",
)
PROVED_BIND_TOKENS: Final[frozenset[str]] = frozenset(
    {"draft_save_validation_existing_option", "none"}
)
_VALIDATION = "Dette felt skal udfyldes."
_INGEN = "Ingen kontakter fundet."
_OPRET_NY = "Opret ny"
_GEM = "Gem som kladde"
_CREATE_PATH = re.compile(r"^/[^/]+/invoices/new/?$")
DRAFT_SAVE_VALIDATION_DUMP: Final = (
    Path.home()
    / ".local"
    / "share"
    / "billy-mcp"
    / "inspect-live-invoices-draft-save-validation.json"
)


class _CountLocator(Protocol):
    @property
    def first(self) -> _CountLocator: ...

    async def count(self) -> int: ...

    async def is_visible(self) -> bool: ...

    async def click(self) -> None: ...


class _CountPage(Protocol):
    @property
    def url(self) -> str: ...

    def get_by_role(self, role: str, **kwargs: object) -> _CountLocator: ...

    def get_by_text(self, text: str, **kwargs: object) -> _CountLocator: ...


def _int_count(raw: object) -> int:
    return raw if isinstance(raw, int) and raw >= 0 else 0


def proved_bind_token(raw: object) -> ProvedBind:
    if raw == "draft_save_validation_existing_option":
        return "draft_save_validation_existing_option"
    return "none"


def list_or_validation_open(payload: Mapping[str, object]) -> bool:
    """True when official validation copy or a customer-list signal is present.

    Page-wide **Opret ny** is not enough. Official shot 1 has that label on
    the sidebar, so `opret_ny_count` alone is not a proved list open.
    """

    if payload.get("validation_message_present") is True:
        return True
    if _int_count(payload.get("ingen_kontakter_count")) > 0:
        return True
    return _int_count(payload.get("option_role_count")) > 0


def proved_bind_from(payload: Mapping[str, object]) -> ProvedBind:
    if payload.get("gem_clicked") is not True:
        return "none"
    if payload.get("invoice_persisted") is True:
        return "none"
    if not list_or_validation_open(payload):
        return "none"
    if payload.get("proved_bind") != "draft_save_validation_existing_option":
        return "none"
    return "draft_save_validation_existing_option"


def _key_is_present(payload: Mapping[str, object], key: DraftSaveKey) -> bool:
    value = payload.get(key)
    match key:
        case "ingen_kontakter_count" | "opret_ny_count" | "option_role_count":
            return isinstance(value, int) and value >= 0
        case "validation_message_present" | "gem_clicked" | "invoice_persisted":
            return isinstance(value, bool)
        case "proved_bind":
            return value in PROVED_BIND_TOKENS
        case "missing_keys":
            return isinstance(value, list)


def draft_save_validation_missing_keys(payload: Mapping[str, object]) -> list[str]:
    """Keys the validation-open dump requires that this payload does not record."""

    if "validation_message_present" not in payload:
        return list(REQUIRED_DRAFT_SAVE_VALIDATION_KEYS)
    return [key for key in REQUIRED_DRAFT_SAVE_VALIDATION_KEYS if not _key_is_present(payload, key)]


def empty_draft_save_validation() -> dict[str, object]:
    """Structurally complete validation-open keys before a live inspect."""

    return {
        "validation_message_present": False,
        "ingen_kontakter_count": 0,
        "opret_ny_count": 0,
        "option_role_count": 0,
        "gem_clicked": False,
        "invoice_persisted": False,
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
        if await locator.first.is_visible():
            return total
    except Exception:
        return 0
    return 0


async def _exact_role_count(page: _CountPage, role: str, label: str) -> int:
    return await _visible_count(page.get_by_role(role, name=re.compile(rf"^{re.escape(label)}$")))


def _create_path_open(page: _CountPage) -> bool:
    try:
        path = urlsplit(page.url).path
    except Exception:
        return False
    return bool(_CREATE_PATH.match(path))


def apply_draft_save_validation_dump(
    payload: Mapping[str, object],
    *,
    dump_path: Path | None = None,
) -> dict[str, object]:
    """Copy allowlisted keys and write the owner-only summary."""

    result = empty_draft_save_validation()
    result["validation_message_present"] = payload.get("validation_message_present") is True
    result["ingen_kontakter_count"] = _int_count(payload.get("ingen_kontakter_count"))
    result["opret_ny_count"] = _int_count(payload.get("opret_ny_count"))
    result["option_role_count"] = _int_count(payload.get("option_role_count"))
    result["gem_clicked"] = payload.get("gem_clicked") is True
    result["invoice_persisted"] = payload.get("invoice_persisted") is True
    result["proved_bind"] = proved_bind_from(
        {
            "gem_clicked": result["gem_clicked"],
            "invoice_persisted": result["invoice_persisted"],
            "validation_message_present": result["validation_message_present"],
            "ingen_kontakter_count": result["ingen_kontakter_count"],
            "opret_ny_count": result["opret_ny_count"],
            "option_role_count": result["option_role_count"],
            "proved_bind": payload.get("proved_bind"),
        }
    )
    result["missing_keys"] = draft_save_validation_missing_keys(result)
    if result["proved_bind"] == "none":
        result["code"] = "UI_CHANGED"
        result["message"] = "Billy invoice create has no proved draft-save validation bind."
    summary = {key: result.get(key) for key in REQUIRED_DRAFT_SAVE_VALIDATION_KEYS}
    write_json(dump_path or DRAFT_SAVE_VALIDATION_DUMP, summary)
    return result


async def _count_open_list(page: _CountPage) -> dict[str, object]:
    payload: dict[str, object] = {}
    payload["validation_message_present"] = (
        await _visible_count(page.get_by_text(_VALIDATION, exact=True))
    ) > 0
    payload["ingen_kontakter_count"] = await _visible_count(page.get_by_text(_INGEN, exact=True))
    opret = await _exact_role_count(page, "button", _OPRET_NY)
    if opret == 0:
        opret = await _visible_count(page.get_by_text(_OPRET_NY, exact=True))
    payload["opret_ny_count"] = opret
    payload["option_role_count"] = await _visible_count(page.get_by_role("option"))
    return payload


async def _unique_tagged_option(page: _CountPage, tag: str) -> bool:
    if not tag or "MCP-UI-INV-" not in tag or len(tag) != 19:
        return False
    options = page.get_by_role("option", name=re.compile(rf"^{re.escape(tag)}$"))
    if await _visible_count(options) == 1:
        return True
    return await _visible_count(page.get_by_text(tag, exact=True)) == 1


async def capture_draft_save_validation(
    page: _CountPage,
    *,
    tag: str,
    dump_path: Path | None = None,
) -> dict[str, object]:
    """Count official validation-open after one Gem som kladde click. Do not save."""

    payload = empty_draft_save_validation()
    rest = await _count_open_list(page)
    payload.update(rest)
    gem = page.get_by_role("button", name=re.compile(rf"^{re.escape(_GEM)}$"))
    gem_count = await _visible_count(gem)
    if gem_count == 1:
        try:
            if await gem.first.is_visible():
                await gem.first.click()
                payload["gem_clicked"] = True
                await asyncio.sleep(0.5)
        except Exception:
            payload["gem_clicked"] = False
    if payload["gem_clicked"] is True:
        after = await _count_open_list(page)
        payload.update(after)
        payload["invoice_persisted"] = not _create_path_open(page)
        if (
            payload["invoice_persisted"] is False
            and list_or_validation_open(payload)
            and await _unique_tagged_option(page, tag)
        ):
            payload["proved_bind"] = "draft_save_validation_existing_option"
    return apply_draft_save_validation_dump(payload, dump_path=dump_path)


def draft_save_validation_dump_is_delivered(path: Path | None = None) -> bool:
    """True when the owner dump already recorded the validation inspect."""

    target = path or DRAFT_SAVE_VALIDATION_DUMP
    if not target.is_file():
        return False
    try:
        raw = json.loads(target.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return False
    if not isinstance(raw, dict):
        return False
    return draft_save_validation_missing_keys(cast(dict[str, object], raw)) == []


def draft_save_validation_dump_json(payload: Mapping[str, object]) -> str:
    """Stable JSON for leak checks. Never includes source or URLs."""

    return json.dumps(dict(payload), sort_keys=True)


__all__ = [
    "DRAFT_SAVE_VALIDATION_DUMP",
    "REQUIRED_DRAFT_SAVE_VALIDATION_KEYS",
    "apply_draft_save_validation_dump",
    "capture_draft_save_validation",
    "draft_save_validation_dump_is_delivered",
    "draft_save_validation_dump_json",
    "draft_save_validation_missing_keys",
    "empty_draft_save_validation",
    "list_or_validation_open",
    "proved_bind_from",
]
