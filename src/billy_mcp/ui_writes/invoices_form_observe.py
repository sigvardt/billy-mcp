"""Non-PII Kunde chrome dumps. Never stores the tag or credentials."""

from __future__ import annotations

from collections.abc import Mapping
from pathlib import Path
from typing import Final

from billy_mcp.ui_writes.invoices_form_page import Locator, Page, write_json
from billy_mcp.ui_writes.invoices_kunde import (
    named_kunde_opener,
    pick_kunde_create_index,
    pick_kunde_existing_option_index,
    placeholder_flags,
    portal_list_item_flags,
)

KUNDE_CHROME_DUMP: Final = (
    Path.home() / ".local" / "share" / "billy-mcp" / "inspect-live-invoices-kunde.json"
)
KUNDE_OPENER_DUMP: Final = (
    Path.home() / ".local" / "share" / "billy-mcp" / "inspect-live-invoices-kunde-opener.json"
)
ALT_LIST_SELECTORS: Final[tuple[str, ...]] = (
    ".ember-power-select-dropdown",
    ".ember-basic-dropdown-content",
    "[role='listbox']",
)


async def portal_items(
    page: Page, unique_tag: str, *, root: Locator | None = None
) -> list[dict[str, bool]]:
    """Non-PII flags for Kunde dropdown lists."""

    lists = root if root is not None else page.locator(".ds-dropdown-list.ds-moved-with-portal")
    count = await lists.count()
    items: list[dict[str, bool]] = []
    for index in range(min(count, 9)):
        node = lists.nth(index)
        try:
            text = (await node.inner_text()).strip()
            visible = await node.is_visible()
        except (TimeoutError, RuntimeError):
            continue
        flags = portal_list_item_flags(text, unique_tag)
        flags["visible"] = visible
        items.append(flags)
    return items


async def observe_kunde(
    page: Page,
    field: Locator,
    unique_tag: str,
    *,
    phase: str,
    wrapper: Locator | None = None,
) -> dict[str, object]:
    """Flags for one Kunde phase. Never stores the tag."""

    items = await portal_items(page, unique_tag)
    wrapper_items: list[dict[str, bool]] = []
    alt_items: list[dict[str, bool]] = []
    search_n = 0
    clear_n = 0
    trigger_n = 0
    if wrapper is not None:
        wrapper_items = await portal_items(
            page, unique_tag, root=wrapper.locator(".ds-dropdown-list")
        )
        search_n = await wrapper.locator("[data-testid='search']").count()
        clear_n = await wrapper.locator("[data-testid='circleX']").count()
        trigger_n = await wrapper.locator("[class*='trigger'], [class*='caret']").count()
    for selector in ALT_LIST_SELECTORS:
        alt_items.extend(await portal_items(page, unique_tag, root=page.locator(selector)))
    box = await field.bounding_box()
    value_len = -1
    try:
        value_len = len(await field.input_value())
    except (TimeoutError, RuntimeError):
        value_len = -1
    combined = [*wrapper_items, *alt_items, *items]
    return {
        "phase": phase,
        "field_name": await field.get_attribute("name"),
        "field_role": await field.get_attribute("role"),
        "aria_expanded": await field.get_attribute("aria-expanded"),
        "value_len": value_len,
        "tag_len": len(unique_tag),
        "search_trigger": search_n > 0,
        "clear_trigger": clear_n > 0,
        "trigger_count": trigger_n,
        "page_search_count": await page.locator("[data-testid='search']").count(),
        "box": None
        if box is None
        else {
            "w": round(float(box.get("width", 0)), 1),
            "h": round(float(box.get("height", 0)), 1),
        },
        "portal_count": len(items),
        "wrapper_count": len(wrapper_items),
        "alt_list_count": len(alt_items),
        "existing_index": pick_kunde_existing_option_index(combined),
        "create_index": pick_kunde_create_index(combined),
        "option_role_count": await page.locator("[role='option']").count(),
        "items": items,
        "wrapper_items": wrapper_items,
        "alt_items": alt_items,
    }


def dump_kunde_phases(after_click: dict[str, object], after_type: dict[str, object]) -> None:
    """Write the no-click after-type dump IR asked for."""

    write_json(
        KUNDE_CHROME_DUMP,
        {
            "path_class": "invoices_new",
            "after_click": after_click,
            "after_type": after_type,
        },
    )


def dump_kunde_opener(payload: Mapping[str, object]) -> None:
    """Write non-PII opener chrome to the opener dump, never the owner file."""

    write_json(KUNDE_OPENER_DUMP, dict(payload))


def _class_tokens(raw: str | None) -> list[str]:
    if not raw:
        return []
    return sorted(
        token for token in raw.split() if token.startswith(("ds-", "ember-", "Dropdown", "input"))
    )


async def _safe_count(node: Locator) -> int:
    try:
        return await node.count()
    except (TimeoutError, RuntimeError):
        return 0


async def _safe_attr(node: Locator, name: str) -> str | None:
    try:
        value = await node.get_attribute(name)
    except (TimeoutError, RuntimeError):
        return None
    return value if isinstance(value, str) and value else None


POWER_SELECT_TRIGGER: Final = ".ember-power-select-trigger"


async def observe_kunde_opener(page: Page, field: Locator) -> dict[str, object]:
    """Ancestor and sibling opener flags before any type. Never stores the tag."""

    parent = field.locator("xpath=..")
    uncle = parent.locator("xpath=..")
    grand = uncle.locator("xpath=..")
    sibling_search = await _safe_count(parent.locator("[data-testid='search']"))
    uncle_search = await _safe_count(uncle.locator("[data-testid='search']"))
    sibling_caret = await _safe_count(parent.locator("[class*='trigger'], [class*='caret']"))
    uncle_caret = await _safe_count(uncle.locator("[class*='trigger'], [class*='caret']"))
    ancestor_class_tokens = [
        _class_tokens(await _safe_attr(parent, "class")),
        _class_tokens(await _safe_attr(uncle, "class")),
        _class_tokens(await _safe_attr(grand, "class")),
    ]
    trigger_n = await _safe_count(page.locator(POWER_SELECT_TRIGGER))
    payload: dict[str, object] = {
        "parent_testid": await _safe_attr(parent, "data-testid"),
        "parent_class_tokens": ancestor_class_tokens[0],
        "ancestor_class_tokens": ancestor_class_tokens,
        "sibling_search": sibling_search > 0,
        "uncle_search": uncle_search > 0,
        "sibling_caret": sibling_caret > 0,
        "uncle_caret": uncle_caret > 0,
        "kunde_label_count": await _safe_count(page.get_by_text("Kunde", exact=True)),
        "contact_id_count": await _safe_count(page.locator("input[name='contactId']")),
        "combobox_count": await _safe_count(page.locator("[role='combobox']")),
        "power_select_trigger_count": trigger_n,
        "placeholder_present": bool(await _safe_attr(field, "placeholder")),
        "placeholder_flags": placeholder_flags(await _safe_attr(field, "placeholder")),
        "field_name": await _safe_attr(field, "name"),
    }
    payload["named_opener"] = named_kunde_opener(payload)
    return payload


async def dump_kunde_chrome(page: Page) -> None:
    """Write non-PII invoice-form chrome when Kunde bind fails before a field."""

    names: list[str] = []
    inputs = page.locator("input, textarea, [role='combobox']")
    count = await inputs.count()
    for index in range(min(count, 30)):
        node = inputs.nth(index)
        name = await node.get_attribute("name")
        role = await node.get_attribute("role")
        data_cy = await node.get_attribute("data-cy")
        visible = await node.is_visible()
        names.append(f"name={name or ''} role={role or ''} cy={data_cy or ''} vis={visible}")
    heading = page.locator("h1")
    heading_text = ""
    if await heading.count() >= 1:
        heading_text = (await heading.first.inner_text()).strip()
    kunde_text = page.get_by_text("Kunde", exact=True)
    write_json(
        KUNDE_CHROME_DUMP,
        {
            "path_class": "/:org_slug/invoices/new" if "/invoices/new" in page.url else "other",
            "heading": heading_text,
            "fields": names,
            "kunde_text_count": await kunde_text.count(),
        },
    )
