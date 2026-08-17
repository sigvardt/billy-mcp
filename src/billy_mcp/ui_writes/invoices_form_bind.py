"""Kunde bind and line fill for draft invoice writes."""

from __future__ import annotations

import asyncio

from billy_mcp.models import StableErrorCode, ToolError
from billy_mcp.ui_writes.invoices_form_observe import (
    ALT_LIST_SELECTORS,
    dump_kunde_chrome,
    dump_kunde_opener,
    dump_kunde_phases,
    observe_kunde,
    observe_kunde_opener,
    portal_items,
)
from billy_mcp.ui_writes.invoices_form_page import Locator, Page
from billy_mcp.ui_writes.invoices_kunde import (
    KUNDE_INPUT_SELECTORS,
    KUNDE_LABEL,
    kunde_phase_is_bound,
    pick_kunde_create_index,
    pick_kunde_existing_option_index,
    portal_create_footer_label,
)

LINE_SELECTORS = (
    "textarea[name='invoiceLines.0.description']",
    "input[name='invoiceLines.0.description']",
    "textarea[name='description']",
    "input[name='description']",
)


async def bind_kunde(page: Page, unique_tag: str) -> str | ToolError:
    """Bind an existing Kunde option. Create footer is last resort."""

    field = await kunde_field(page)
    if field is None:
        await dump_kunde_chrome(page)
        return ToolError(
            code=StableErrorCode.UI_CHANGED,
            message="Billy Kunde control is not visible.",
        )
    opener = await observe_kunde_opener(page, field)
    dump_kunde_opener(opener)
    named = opener.get("named_opener")
    if not isinstance(named, str) or not named:
        return ToolError(
            code=StableErrorCode.UI_CHANGED,
            message="Billy Kunde opener is not visible.",
        )
    type_target = await _click_named_opener(page, field, named)
    if type_target is None:
        return ToolError(
            code=StableErrorCode.UI_CHANGED,
            message="Billy Kunde opener is not visible.",
        )
    wrapper = kunde_wrapper(page)
    after_click = await observe_kunde(page, field, unique_tag, phase="after_click", wrapper=wrapper)
    await _type_kunde(type_target, unique_tag)
    items = await _wait_options(page, unique_tag, wrapper)
    after_type = await observe_kunde(page, field, unique_tag, phase="after_type", wrapper=wrapper)
    dump_kunde_phases(after_click, after_type)
    if not kunde_phase_is_bound(after_type):
        return ToolError(
            code=StableErrorCode.UI_CHANGED,
            message="Billy Kunde existing option is not visible.",
        )
    if pick_kunde_existing_option_index(items) is not None:
        if await _click_scoped_option(page, unique_tag):
            return "scoped:existing_option"
    if pick_kunde_create_index(items) is not None:
        if await _click_scoped_footer(page, unique_tag):
            return "scoped:portal_footer"
    return ToolError(
        code=StableErrorCode.UI_CHANGED,
        message="Billy Kunde existing option is not visible.",
    )


async def _click_named_opener(page: Page, field: Locator, named: str) -> Locator | None:
    """Click the dump-named opener. The contact text field is not an opener."""

    parent = field.locator("xpath=..")
    uncle = parent.locator("xpath=..")
    targets: dict[str, Locator] = {
        "sibling_search": parent.locator("[data-testid='search']"),
        "uncle_search": uncle.locator("[data-testid='search']"),
        "combobox": page.locator("[role='combobox']"),
        "contact_id": page.locator("input[name='contactId']"),
        "power_select_trigger": page.locator(".ember-power-select-trigger"),
    }
    target = targets.get(named)
    if target is None:
        return None
    if await target.count() < 1 or not await target.first.is_visible():
        return None
    await target.first.click()
    await asyncio.sleep(0.3)
    return target.first


def kunde_wrapper(page: Page) -> Locator:
    """Return the input-wrapper that owns input[name=contact]."""

    return page.locator("[data-testid='input-wrapper']").filter(
        has=page.locator("input[name='contact']")
    )


async def kunde_field(page: Page) -> Locator | None:
    """Return the live-proved typeable Kunde input."""

    field = page.locator("input[name='contact']")
    if await field.count() >= 1 and await field.first.is_visible():
        return field.first
    labeled = page.get_by_label(KUNDE_LABEL, exact=True)
    if await labeled.count() >= 1 and await labeled.first.is_visible():
        inner = labeled.locator("input:not([type='hidden'])")
        if await inner.count() >= 1 and await inner.first.is_visible():
            return inner.first
        return labeled.first
    for selector in KUNDE_INPUT_SELECTORS:
        field = page.locator(selector)
        if await field.count() >= 1 and await field.first.is_visible():
            return field.first
    return None


async def _type_kunde(field: Locator, unique_tag: str) -> None:
    sequential = getattr(field, "press_sequentially", None)
    if sequential is not None:
        try:
            await sequential(unique_tag, delay=50)
        except TypeError:
            await sequential(unique_tag)
    else:
        await field.fill(unique_tag)
    await asyncio.sleep(0.5)


async def _wait_options(page: Page, unique_tag: str, wrapper: Locator) -> list[dict[str, bool]]:
    combined: list[dict[str, bool]] = []
    for _ in range(16):
        items = await portal_items(page, unique_tag)
        wrapper_items = await portal_items(
            page, unique_tag, root=wrapper.locator(".ds-dropdown-list")
        )
        alt_items: list[dict[str, bool]] = []
        for selector in ALT_LIST_SELECTORS:
            alt_items.extend(await portal_items(page, unique_tag, root=page.locator(selector)))
        combined = [*wrapper_items, *alt_items, *items]
        if any(
            item.get("visible") and (item.get("has_tag") or item.get("has_create_footer"))
            for item in combined
        ):
            return combined
        await asyncio.sleep(0.25)
    return combined


async def _click_scoped_option(page: Page, unique_tag: str) -> bool:
    footer_label = portal_create_footer_label(unique_tag)
    for selector in (
        ".ds-dropdown-list.ds-moved-with-portal",
        ".ds-dropdown-list",
        *ALT_LIST_SELECTORS,
    ):
        lists = page.locator(selector)
        for index in range(min(await lists.count(), 9)):
            root = lists.nth(index)
            option = root.get_by_text(unique_tag, exact=True)
            footer = root.get_by_text(footer_label, exact=True)
            if await option.count() < 1 or not await option.first.is_visible():
                continue
            if await footer.count() >= 1 and await footer.first.is_visible():
                continue
            await option.first.click()
            return True
    return False


async def _click_scoped_footer(page: Page, unique_tag: str) -> bool:
    label = portal_create_footer_label(unique_tag)
    for selector in (
        ".ds-dropdown-list.ds-moved-with-portal",
        ".ds-dropdown-list",
        *ALT_LIST_SELECTORS,
    ):
        lists = page.locator(selector)
        for index in range(min(await lists.count(), 9)):
            footer = lists.nth(index).get_by_text(label, exact=True)
            if await footer.count() < 1:
                continue
            await footer.first.click()
            return True
    return False


async def fill_line(page: Page, value: str) -> str | None:
    """Fill the first visible invoice line description."""

    for selector in LINE_SELECTORS:
        field = page.locator(selector)
        if await field.count() < 1:
            continue
        target = field.first
        if not await target.is_visible():
            continue
        await target.fill(value)
        return value
    return None
