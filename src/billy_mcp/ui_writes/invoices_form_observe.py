"""Non-PII Kunde chrome dumps. Never stores the tag or credentials."""

from __future__ import annotations

from pathlib import Path
from typing import Final

from billy_mcp.ui_writes.invoices_form_page import Locator, Page, write_json
from billy_mcp.ui_writes.invoices_kunde import (
    pick_kunde_create_index,
    pick_kunde_existing_option_index,
    portal_list_item_flags,
)

KUNDE_CHROME_DUMP: Final = (
    Path.home() / ".local" / "share" / "billy-mcp" / "inspect-live-invoices-kunde.json"
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
