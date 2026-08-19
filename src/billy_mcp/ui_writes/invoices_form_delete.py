"""Delete one leftover invoice draft from the edit page."""

from __future__ import annotations

import asyncio

from billy_mcp.models import ToolError
from billy_mcp.ui_writes.invoices_form_page import (
    CONFIRM_DELETE,
    DELETE,
    MORE,
    Page,
    click_exact,
    visible_button,
    wait_persist,
    watch_invoice_response,
)
from billy_mcp.ui_writes.invoices_form_row import open_invoice_row


async def delete_draft_invoice(page: Page, slug: str, contact_name: str) -> ToolError | None:
    """Open the list row, then Mere / Slet / Ja, slet. Wait for DELETE."""

    opened = await open_invoice_row(page, slug, contact_name)
    if opened is not None:
        return opened
    seen: list[str] = []

    def _watch_delete(event: object) -> None:
        watch_invoice_response(event, seen)

    page.on("response", _watch_delete)
    page.on("request", _watch_delete)
    more = await _click_last_more(page)
    if more is not None:
        return more
    for _ in range(20):
        menu = page.get_by_role("menuitem", name=DELETE, exact=True)
        if await menu.count() >= 1 and await menu.first.is_visible():
            await menu.first.click()
            break
        if await visible_button(page, DELETE):
            slet = await click_exact(page, DELETE)
            if slet is not None:
                return slet
            break
        await asyncio.sleep(0.25)
    else:
        slet = await click_exact(page, DELETE)
        if slet is not None:
            return slet
    if await visible_button(page, CONFIRM_DELETE):
        confirmed = await click_exact(page, CONFIRM_DELETE)
        if confirmed is not None:
            return confirmed
    return await wait_persist(seen, method="DELETE")


async def _click_last_more(page: Page) -> ToolError | None:
    """Click the last visible Mere. The first is often page chrome."""

    meres = page.get_by_role("button", name=MORE, exact=True)
    count = await meres.count()
    for index in range(count - 1, -1, -1):
        target = meres.nth(index)
        if await target.is_visible():
            await target.click()
            return None
    return await click_exact(page, MORE)
