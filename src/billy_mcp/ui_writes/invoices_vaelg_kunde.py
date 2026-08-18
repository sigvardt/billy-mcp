"""Exact Vælg kunde named-control keys on invoices/new.

Never stores source, URLs, locators, ids, or customer names.
"""

from __future__ import annotations

import asyncio
import json
import re
from collections.abc import Mapping
from pathlib import Path
from typing import Final, Literal, Protocol, cast

from billy_mcp.ui_writes.invoices_form_page import write_json

VaelgKey = Literal[
    "vaelg_kunde_button_count",
    "vaelg_kunde_link_count",
    "vaelg_kunde_other_count",
    "unique_vaelg_kunde",
    "hit_is_contact_input",
    "clicked",
    "opret_ny_count",
    "option_role_count",
    "proved_bind",
    "missing_keys",
]
ProvedBind = Literal["vaelg_kunde_existing_option", "none"]

REQUIRED_VAELG_KUNDE_KEYS: Final[tuple[VaelgKey, ...]] = (
    "vaelg_kunde_button_count",
    "vaelg_kunde_link_count",
    "vaelg_kunde_other_count",
    "unique_vaelg_kunde",
    "hit_is_contact_input",
    "clicked",
    "opret_ny_count",
    "option_role_count",
    "proved_bind",
    "missing_keys",
)
PROVED_BIND_TOKENS: Final[frozenset[str]] = frozenset({"vaelg_kunde_existing_option", "none"})
_VAELG = "Vælg kunde"
_OPRET_NY = "Opret ny"
VAELG_KUNDE_DUMP: Final = (
    Path.home() / ".local" / "share" / "billy-mcp" / "inspect-live-invoices-vaelg-kunde.json"
)


class _CountLocator(Protocol):
    @property
    def first(self) -> _CountLocator: ...

    async def count(self) -> int: ...

    async def is_visible(self) -> bool: ...

    async def click(self) -> None: ...

    async def get_attribute(self, name: str) -> str | None: ...


class _CountPage(Protocol):
    def locator(self, selector: str) -> _CountLocator: ...

    def get_by_role(self, role: str, **kwargs: object) -> _CountLocator: ...

    def get_by_text(self, text: str, **kwargs: object) -> _CountLocator: ...


def _int_count(raw: object) -> int:
    return raw if isinstance(raw, int) and raw >= 0 else 0


def proved_bind_token(raw: object) -> ProvedBind:
    if raw == "vaelg_kunde_existing_option":
        return "vaelg_kunde_existing_option"
    return "none"


def unique_vaelg_kunde_from(payload: Mapping[str, object]) -> bool:
    """True only when exactly one named control exists and it is not the contact input."""

    if payload.get("hit_is_contact_input") is True:
        return False
    button = _int_count(payload.get("vaelg_kunde_button_count"))
    link = _int_count(payload.get("vaelg_kunde_link_count"))
    other = _int_count(payload.get("vaelg_kunde_other_count"))
    return button + link + other == 1


def proved_bind_from(payload: Mapping[str, object]) -> ProvedBind:
    if payload.get("unique_vaelg_kunde") is not True:
        return "none"
    if payload.get("clicked") is not True:
        return "none"
    if payload.get("proved_bind") != "vaelg_kunde_existing_option":
        return "none"
    return "vaelg_kunde_existing_option"


def _key_is_present(payload: Mapping[str, object], key: VaelgKey) -> bool:
    value = payload.get(key)
    match key:
        case (
            "vaelg_kunde_button_count"
            | "vaelg_kunde_link_count"
            | "vaelg_kunde_other_count"
            | "opret_ny_count"
            | "option_role_count"
        ):
            return isinstance(value, int) and value >= 0
        case "unique_vaelg_kunde" | "hit_is_contact_input" | "clicked":
            return isinstance(value, bool)
        case "proved_bind":
            return value in PROVED_BIND_TOKENS
        case "missing_keys":
            return isinstance(value, list)


def vaelg_kunde_missing_keys(payload: Mapping[str, object]) -> list[str]:
    """Keys the rest dump requires that this payload does not record."""

    if "vaelg_kunde_button_count" not in payload:
        return list(REQUIRED_VAELG_KUNDE_KEYS)
    return [key for key in REQUIRED_VAELG_KUNDE_KEYS if not _key_is_present(payload, key)]


def empty_vaelg_kunde() -> dict[str, object]:
    """Structurally complete Vælg kunde keys before a live inspect."""

    return {
        "vaelg_kunde_button_count": 0,
        "vaelg_kunde_link_count": 0,
        "vaelg_kunde_other_count": 0,
        "unique_vaelg_kunde": False,
        "hit_is_contact_input": False,
        "clicked": False,
        "opret_ny_count": 0,
        "option_role_count": 0,
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


async def _placeholder_is_vaelg(page: _CountPage) -> bool:
    field = page.locator("input[name='contact']")
    try:
        if await field.count() < 1:
            return False
        raw = await field.first.get_attribute("placeholder")
    except Exception:
        return False
    return isinstance(raw, str) and raw.strip() == _VAELG


def apply_vaelg_kunde_dump(
    payload: Mapping[str, object],
    *,
    dump_path: Path | None = None,
) -> dict[str, object]:
    """Copy allowlisted keys and write the owner-only summary."""

    result = empty_vaelg_kunde()
    result["vaelg_kunde_button_count"] = _int_count(payload.get("vaelg_kunde_button_count"))
    result["vaelg_kunde_link_count"] = _int_count(payload.get("vaelg_kunde_link_count"))
    result["vaelg_kunde_other_count"] = _int_count(payload.get("vaelg_kunde_other_count"))
    result["hit_is_contact_input"] = payload.get("hit_is_contact_input") is True
    result["clicked"] = payload.get("clicked") is True
    result["opret_ny_count"] = _int_count(payload.get("opret_ny_count"))
    result["option_role_count"] = _int_count(payload.get("option_role_count"))
    unique = unique_vaelg_kunde_from(result)
    result["unique_vaelg_kunde"] = unique
    result["proved_bind"] = proved_bind_from(
        {
            "unique_vaelg_kunde": unique,
            "clicked": result["clicked"],
            "proved_bind": payload.get("proved_bind"),
        }
    )
    result["missing_keys"] = vaelg_kunde_missing_keys(result)
    if not unique or result["proved_bind"] == "none":
        result["code"] = "UI_CHANGED"
        result["message"] = "Billy invoice create has no proved Vælg kunde bind."
    summary = {key: result.get(key) for key in REQUIRED_VAELG_KUNDE_KEYS}
    write_json(dump_path or VAELG_KUNDE_DUMP, summary)
    return result


async def capture_vaelg_kunde(
    page: _CountPage,
    *,
    dump_path: Path | None = None,
) -> dict[str, object]:
    """Count exact Vælg kunde on invoices/new. Click only when unique and not the input."""

    payload = empty_vaelg_kunde()
    payload["vaelg_kunde_button_count"] = await _exact_role_count(page, "button", _VAELG)
    payload["vaelg_kunde_link_count"] = await _exact_role_count(page, "link", _VAELG)
    named = _int_count(payload["vaelg_kunde_button_count"]) + _int_count(
        payload["vaelg_kunde_link_count"]
    )
    placeholder = await _placeholder_is_vaelg(page)
    if named == 0 and placeholder:
        payload["hit_is_contact_input"] = True
        payload["vaelg_kunde_other_count"] = 0
    elif named == 0:
        text_hits = await _visible_count(page.get_by_text(_VAELG, exact=True))
        payload["vaelg_kunde_other_count"] = text_hits
        payload["hit_is_contact_input"] = False
    else:
        payload["vaelg_kunde_other_count"] = 0
        payload["hit_is_contact_input"] = False
    unique = unique_vaelg_kunde_from(payload)
    payload["unique_vaelg_kunde"] = unique
    if unique:
        role = "button" if payload["vaelg_kunde_button_count"] == 1 else "link"
        if payload["vaelg_kunde_other_count"] == 1:
            control = page.get_by_text(_VAELG, exact=True)
        else:
            control = page.get_by_role(role, name=re.compile(rf"^{re.escape(_VAELG)}$"))
        try:
            if await control.count() >= 1 and await control.first.is_visible():
                await control.first.click()
                payload["clicked"] = True
                await asyncio.sleep(0.5)
        except Exception:
            payload["clicked"] = False
    if payload["clicked"] is True:
        payload["opret_ny_count"] = await _exact_role_count(page, "button", _OPRET_NY)
        if payload["opret_ny_count"] == 0:
            payload["opret_ny_count"] = await _visible_count(
                page.get_by_text(_OPRET_NY, exact=True)
            )
        payload["option_role_count"] = await _visible_count(page.get_by_role("option"))
    return apply_vaelg_kunde_dump(payload, dump_path=dump_path)


def vaelg_kunde_dump_is_delivered(path: Path | None = None) -> bool:
    """True when the owner dump already recorded the rest inspect."""

    target = path or VAELG_KUNDE_DUMP
    if not target.is_file():
        return False
    try:
        raw = json.loads(target.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return False
    if not isinstance(raw, dict):
        return False
    return vaelg_kunde_missing_keys(cast(dict[str, object], raw)) == []


def vaelg_kunde_dump_json(payload: Mapping[str, object]) -> str:
    """Stable JSON for leak checks. Never includes source or URLs."""

    return json.dumps(dict(payload), sort_keys=True)


__all__ = [
    "REQUIRED_VAELG_KUNDE_KEYS",
    "VAELG_KUNDE_DUMP",
    "apply_vaelg_kunde_dump",
    "capture_vaelg_kunde",
    "empty_vaelg_kunde",
    "proved_bind_from",
    "unique_vaelg_kunde_from",
    "vaelg_kunde_dump_is_delivered",
    "vaelg_kunde_dump_json",
    "vaelg_kunde_missing_keys",
]
