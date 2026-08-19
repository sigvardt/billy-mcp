"""Delete one leftover invoice draft from the edit page."""

from __future__ import annotations

import asyncio

from billy_mcp.models import StableErrorCode, ToolError
from billy_mcp.ui_writes.invoices_form_page import (
    CONFIRM_DELETE,
    DELETE,
    MORE,
    Locator,
    Page,
    click_exact,
    persist_hit,
    visible_button,
    wait_persist,
    watch_invoice_response,
)
from billy_mcp.ui_writes.invoices_form_row import open_invoice_row


async def delete_draft_invoice(page: Page, slug: str, contact_name: str) -> ToolError | None:
    """Open the list row, then unique Mere / exact Slet / Ja, slet. Wait for DELETE."""

    opened = await open_invoice_row(page, slug, contact_name)
    if opened is not None:
        return opened
    seen: list[str] = []

    def _watch_delete(event: object) -> None:
        watch_invoice_response(event, seen)

    page.on("response", _watch_delete)
    more = await _click_unique_mere(page)
    if more is not None:
        return more
    slet = await _click_unique_text(page, DELETE)
    if slet is not None:
        return slet
    confirm = await _click_confirm(page, seen)
    if confirm is not None:
        return confirm
    return await wait_persist(seen, method="DELETE")


async def _click_unique_mere(page: Page) -> ToolError | None:
    """Owner 70DB45E6: visible Mere button count is 1. Do not pick a decoy."""

    meres = page.get_by_role("button", name=MORE, exact=True)
    visible: list[Locator] = []
    for index in range(await meres.count()):
        target = meres.nth(index)
        if await target.is_visible():
            visible.append(target)
    if len(visible) != 1:
        return ToolError(
            code=StableErrorCode.UI_CHANGED,
            message="Billy Mere control is not unique.",
            details={"mere_count": len(visible)},
        )
    await visible[0].click()
    return None


async def _click_unique_text(page: Page, label: str) -> ToolError | None:
    """Click the unique visible exact text. Owner 70DB45E6: Slet count is 1 after Mere."""

    for _ in range(20):
        hits: list[Locator] = []
        labels = page.get_by_text(label, exact=True)
        for index in range(await labels.count()):
            target = labels.nth(index)
            if await target.is_visible():
                hits.append(target)
        if len(hits) == 1:
            await hits[0].click()
            return None
        await asyncio.sleep(0.25)
    return ToolError(
        code=StableErrorCode.UI_CHANGED,
        message=f"Billy control {label} is not unique.",
    )


async def _click_confirm(page: Page, seen: list[str]) -> ToolError | None:
    """Wait for Ja, slet or an already-finished DELETE. Timing miss is not missing chrome."""

    for _ in range(40):
        if any(persist_hit(item, "DELETE") for item in seen):
            return None
        if await visible_button(page, CONFIRM_DELETE):
            return await click_exact(page, CONFIRM_DELETE)
        text = page.get_by_text(CONFIRM_DELETE, exact=True)
        if await text.count() >= 1 and await text.first.is_visible():
            return await click_exact(page, CONFIRM_DELETE)
        await asyncio.sleep(0.25)
    if any(persist_hit(item, "DELETE") for item in seen):
        return None
    return ToolError(
        code=StableErrorCode.UI_CHANGED,
        message="Billy Ja, slet control is not visible.",
    )
