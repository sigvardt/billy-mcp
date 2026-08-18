"""Company-settings phone-field dump keys.

Never stores source, URLs, locators, ids, or phone values.
"""

from __future__ import annotations

import json
import re
from collections.abc import Mapping
from pathlib import Path
from typing import Final, Literal, Protocol, cast
from urllib.parse import urlsplit

from billy_mcp.ui_writes.invoices_form_page import write_json

PhoneDumpKey = Literal[
    "settings_path_class",
    "heading_token",
    "company_panel_markers_present",
    "phone_field_visible",
    "phone_input_name_class",
    "phone_value_len",
    "save_cta_token",
    "save_cta_count",
    "forbidden_surface_token",
    "proved_phone_only",
    "missing_keys",
]
SettingsPathClass = Literal["settings", "other"]
HeadingToken = Literal["indstillinger", "other", "none"]
PhoneInputNameClass = Literal["phone", "other", "none"]
SaveCtaToken = Literal["gem_aendringer", "other", "none"]
ForbiddenSurfaceToken = Literal["users", "access", "tokens", "subscription", "vat", "none"]

REQUIRED_ORGANIZATIONS_PHONE_DUMP_KEYS: Final[tuple[PhoneDumpKey, ...]] = (
    "settings_path_class",
    "heading_token",
    "company_panel_markers_present",
    "phone_field_visible",
    "phone_input_name_class",
    "phone_value_len",
    "save_cta_token",
    "save_cta_count",
    "forbidden_surface_token",
    "proved_phone_only",
    "missing_keys",
)
SETTINGS_PATH_CLASSES: Final[frozenset[str]] = frozenset({"settings", "other"})
HEADING_TOKENS: Final[frozenset[str]] = frozenset({"indstillinger", "other", "none"})
PHONE_INPUT_NAME_CLASSES: Final[frozenset[str]] = frozenset({"phone", "other", "none"})
SAVE_CTA_TOKENS: Final[frozenset[str]] = frozenset({"gem_aendringer", "other", "none"})
FORBIDDEN_SURFACE_TOKENS: Final[frozenset[str]] = frozenset(
    {"users", "access", "tokens", "subscription", "vat", "none"}
)
_SETTINGS_LEAF = re.compile(r"^/[^/]+/settings/?$")
_SETTINGS_NESTED = re.compile(r"^/[^/]+/settings/([^/]+)")
_INDSTILLINGER = "Indstillinger"
_GEM_AENDRINGER = "Gem ændringer"
_NAVN_OG_ADRESSE = "Navn og adresse"
_KONTAKTINFORMATION = "Kontaktinformation"
_USERS_MARKER = "Revisorer og bogholdere"
_ACCESS_MARKER = "Adgangsnøgler"
_SUBSCRIPTION_MARKER = "Abonnement"
_VAT_MARKER = "Momssatser"
_FORBIDDEN_SEGMENTS: Final[dict[str, ForbiddenSurfaceToken]] = {
    "users": "users",
    "brugere": "users",
    "access": "access",
    "access_token": "access",
    "access-token": "access",
    "adgangsnogler": "tokens",
    "tokens": "tokens",
    "subscription": "subscription",
    "abonnement": "subscription",
    "vat": "vat",
    "moms": "vat",
    "momssatser": "vat",
}
ORGANIZATIONS_PHONE_DUMP: Final = (
    Path.home() / ".local" / "share" / "billy-mcp" / "inspect-live-organizations-phone.json"
)


class _CountLocator(Protocol):
    @property
    def first(self) -> _CountLocator: ...

    async def count(self) -> int: ...

    async def is_visible(self) -> bool: ...

    async def inner_text(self) -> str: ...

    async def input_value(self) -> str: ...

    async def get_attribute(self, name: str) -> str | None: ...


class _CountPage(Protocol):
    @property
    def url(self) -> str: ...

    def locator(self, selector: str) -> _CountLocator: ...

    def get_by_role(self, role: str, **kwargs: object) -> _CountLocator: ...

    def get_by_text(self, text: str, **kwargs: object) -> _CountLocator: ...


def _int_count(raw: object) -> int:
    return raw if isinstance(raw, int) and raw >= 0 else 0


def settings_path_class_token(raw: object) -> SettingsPathClass:
    return "settings" if raw == "settings" else "other"


def heading_token(raw: object) -> HeadingToken:
    if raw == "indstillinger":
        return "indstillinger"
    if raw == "other":
        return "other"
    return "none"


def phone_input_name_token(raw: object) -> PhoneInputNameClass:
    if raw == "phone":
        return "phone"
    if raw == "other":
        return "other"
    return "none"


def save_cta_token(raw: object) -> SaveCtaToken:
    if raw == "gem_aendringer":
        return "gem_aendringer"
    if raw == "other":
        return "other"
    return "none"


def forbidden_surface_token(raw: object) -> ForbiddenSurfaceToken:
    if raw in FORBIDDEN_SURFACE_TOKENS and raw != "none":
        return cast(ForbiddenSurfaceToken, raw)
    return "none"


def classify_settings_path(url: object) -> SettingsPathClass:
    """Return settings only for /:org/settings. Never store the URL."""

    if not isinstance(url, str) or not url:
        return "other"
    return "settings" if _SETTINGS_LEAF.match(urlsplit(url).path or "") else "other"


def classify_heading(text: object) -> HeadingToken:
    if not isinstance(text, str) or not text.strip():
        return "none"
    return "indstillinger" if text.strip() == _INDSTILLINGER else "other"


def classify_save_cta(text: object) -> SaveCtaToken:
    if not isinstance(text, str) or not text.strip():
        return "none"
    return "gem_aendringer" if text.strip() == _GEM_AENDRINGER else "other"


def classify_phone_input_name(name: object) -> PhoneInputNameClass:
    if not isinstance(name, str) or not name.strip():
        return "none"
    return "phone" if name.strip() == "phone" else "other"


def classify_forbidden_surface(url: object) -> ForbiddenSurfaceToken:
    """Return a forbidden panel from a nested settings path. Never store the URL."""

    if not isinstance(url, str) or not url:
        return "none"
    match = _SETTINGS_NESTED.match(urlsplit(url).path or "")
    if match is None:
        return "none"
    return _FORBIDDEN_SEGMENTS.get(match.group(1).casefold(), "none")


def save_cta_token_from_count(count: int) -> SaveCtaToken:
    if count == 1:
        return "gem_aendringer"
    if count > 1:
        return "other"
    return "none"


def proved_phone_only_from(payload: Mapping[str, object]) -> bool:
    """True only when every phone-only gate holds."""

    return (
        payload.get("settings_path_class") == "settings"
        and payload.get("heading_token") == "indstillinger"
        and payload.get("company_panel_markers_present") is True
        and payload.get("phone_input_name_class") == "phone"
        and payload.get("save_cta_token") == "gem_aendringer"
        and payload.get("save_cta_count") == 1
        and payload.get("forbidden_surface_token") == "none"
    )


def persist_allowed_from(payload: Mapping[str, object]) -> bool:
    """True only when the surface is proved and a restore ticket can bind."""

    return proved_phone_only_from(payload) and _int_count(payload.get("phone_value_len")) > 0


def _key_is_present(payload: Mapping[str, object], key: PhoneDumpKey) -> bool:
    value = payload.get(key)
    match key:
        case "settings_path_class":
            return value in SETTINGS_PATH_CLASSES
        case "heading_token":
            return value in HEADING_TOKENS
        case "company_panel_markers_present" | "phone_field_visible" | "proved_phone_only":
            return isinstance(value, bool)
        case "phone_input_name_class":
            return value in PHONE_INPUT_NAME_CLASSES
        case "phone_value_len" | "save_cta_count":
            return isinstance(value, int) and value >= 0
        case "save_cta_token":
            return value in SAVE_CTA_TOKENS
        case "forbidden_surface_token":
            return value in FORBIDDEN_SURFACE_TOKENS
        case "missing_keys":
            return isinstance(value, list)


def organizations_phone_dump_missing_keys(payload: Mapping[str, object]) -> list[str]:
    """Keys the phone dump requires that this payload does not record."""

    if "settings_path_class" not in payload:
        return list(REQUIRED_ORGANIZATIONS_PHONE_DUMP_KEYS)
    return [
        key for key in REQUIRED_ORGANIZATIONS_PHONE_DUMP_KEYS if not _key_is_present(payload, key)
    ]


def empty_organizations_phone_dump() -> dict[str, object]:
    """Structurally complete phone-dump keys before a live inspect."""

    return {
        "settings_path_class": "other",
        "heading_token": "none",
        "company_panel_markers_present": False,
        "phone_field_visible": False,
        "phone_input_name_class": "none",
        "phone_value_len": 0,
        "save_cta_token": "none",
        "save_cta_count": 0,
        "forbidden_surface_token": "none",
        "proved_phone_only": False,
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


async def _marker_present(page: _CountPage, label: str) -> bool:
    return await _exact_text_count(page, label) >= 1


async def _inspect_forbidden_panel(
    page: _CountPage, *, url_token: ForbiddenSurfaceToken, company_markers: bool
) -> ForbiddenSurfaceToken:
    if url_token != "none":
        return url_token
    if company_markers:
        return "none"
    if await _marker_present(page, _USERS_MARKER):
        return "users"
    if await _marker_present(page, _ACCESS_MARKER):
        return "tokens"
    if await _marker_present(page, _VAT_MARKER):
        return "vat"
    if await _marker_present(page, _SUBSCRIPTION_MARKER):
        return "subscription"
    return "none"


async def _inspect_phone_field(page: _CountPage) -> tuple[bool, PhoneInputNameClass, int]:
    named = page.locator("input[name='phone']")
    try:
        if await named.count() >= 1 and await named.first.is_visible():
            raw = await named.first.input_value()
            return True, "phone", len(raw)
    except Exception:
        return False, "none", 0
    tel = page.locator("input[type='tel']")
    try:
        if await tel.count() >= 1 and await tel.first.is_visible():
            name = await tel.first.get_attribute("name")
            return True, classify_phone_input_name(name or "tel"), 0
    except Exception:
        return False, "none", 0
    return False, "none", 0


def apply_organizations_phone_dump(
    payload: Mapping[str, object],
    *,
    dump_path: Path | None = None,
) -> dict[str, object]:
    """Copy allowlisted keys and write the owner-only summary."""

    result = empty_organizations_phone_dump()
    result["settings_path_class"] = settings_path_class_token(payload.get("settings_path_class"))
    result["heading_token"] = heading_token(payload.get("heading_token"))
    result["company_panel_markers_present"] = payload.get("company_panel_markers_present") is True
    result["phone_field_visible"] = payload.get("phone_field_visible") is True
    result["phone_input_name_class"] = phone_input_name_token(payload.get("phone_input_name_class"))
    result["phone_value_len"] = _int_count(payload.get("phone_value_len"))
    result["save_cta_count"] = _int_count(payload.get("save_cta_count"))
    token = save_cta_token(payload.get("save_cta_token"))
    if token == "none":
        token = save_cta_token_from_count(int(result["save_cta_count"]))
    result["save_cta_token"] = token
    result["forbidden_surface_token"] = forbidden_surface_token(
        payload.get("forbidden_surface_token")
    )
    proved = proved_phone_only_from(result)
    result["proved_phone_only"] = proved
    result["missing_keys"] = organizations_phone_dump_missing_keys(result)
    if not proved:
        result["code"] = "UI_CHANGED"
        result["message"] = "Billy company settings is not a proved phone-only update surface."
    summary = {key: result.get(key) for key in REQUIRED_ORGANIZATIONS_PHONE_DUMP_KEYS}
    write_json(dump_path or ORGANIZATIONS_PHONE_DUMP, summary)
    return result


async def inspect_organizations_phone_chrome(page: _CountPage) -> dict[str, object]:
    """Classify the company phone field and exact Gem ændringer. Do not click."""

    heading = classify_heading(await _heading_text(page))
    company_markers = await _marker_present(page, _NAVN_OG_ADRESSE) and await _marker_present(
        page, _KONTAKTINFORMATION
    )
    visible, name_class, value_len = await _inspect_phone_field(page)
    save_count = await _exact_role_count(page, "button", _GEM_AENDRINGER)
    if save_count == 0:
        save_count = await _exact_text_count(page, _GEM_AENDRINGER)
    url_forbidden = classify_forbidden_surface(page.url)
    forbidden = await _inspect_forbidden_panel(
        page, url_token=url_forbidden, company_markers=company_markers
    )
    payload: dict[str, object] = {
        "settings_path_class": classify_settings_path(page.url),
        "heading_token": heading,
        "company_panel_markers_present": company_markers,
        "phone_field_visible": visible,
        "phone_input_name_class": name_class,
        "phone_value_len": value_len,
        "save_cta_token": save_cta_token_from_count(save_count),
        "save_cta_count": save_count,
        "forbidden_surface_token": forbidden,
    }
    payload["proved_phone_only"] = proved_phone_only_from(payload)
    payload["missing_keys"] = []
    return payload


def organizations_phone_dump_is_delivered(path: Path | None = None) -> bool:
    """True when the owner dump already recorded the phone inspect."""

    target = path or ORGANIZATIONS_PHONE_DUMP
    if not target.is_file():
        return False
    try:
        raw = json.loads(target.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return False
    if not isinstance(raw, dict):
        return False
    return organizations_phone_dump_missing_keys(cast(dict[str, object], raw)) == []


def organizations_phone_dump_json(payload: Mapping[str, object]) -> str:
    """Stable JSON for leak checks. Never includes source or URLs."""

    return json.dumps(dict(payload), sort_keys=True)


__all__ = [
    "ORGANIZATIONS_PHONE_DUMP",
    "REQUIRED_ORGANIZATIONS_PHONE_DUMP_KEYS",
    "apply_organizations_phone_dump",
    "classify_forbidden_surface",
    "classify_heading",
    "classify_phone_input_name",
    "classify_save_cta",
    "classify_settings_path",
    "empty_organizations_phone_dump",
    "inspect_organizations_phone_chrome",
    "organizations_phone_dump_is_delivered",
    "organizations_phone_dump_json",
    "organizations_phone_dump_missing_keys",
    "persist_allowed_from",
    "proved_phone_only_from",
]
