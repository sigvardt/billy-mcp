"""Delete one leftover invoice draft from the edit page."""

from __future__ import annotations

import asyncio

from billy_mcp.models import StableErrorCode, ToolError
from billy_mcp.ui_writes.invoices_form_delete_dump import (
    POST_SLET_DUMP,
    allowlisted_label,
    capture_post_slet,
    heading_token,
    path_class_from_url,
    ui_path,
)
from billy_mcp.ui_writes.invoices_form_page import (
    DELETE,
    MORE,
    Locator,
    Page,
    wait_persist,
    watch_invoice_response,
)
from billy_mcp.ui_writes.invoices_form_row import open_invoice_row

__all__ = [
    "POST_SLET_DUMP",
    "allowlisted_label",
    "delete_draft_invoice",
    "heading_token",
    "path_class_from_url",
]


async def delete_draft_invoice(page: Page, slug: str, contact_name: str) -> ToolError | None:
    """Open the list row, unique Mere, exact Slet, then capture post-Slet state."""

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
    start_path = ui_path(page.url)
    hit_tag, slet = await _click_slet(page)
    if slet is not None:
        return slet
    dump = await capture_post_slet(page, seen, start_path, hit_tag)
    if dump["delete_seen"] is True:
        return await wait_persist(seen, method="DELETE")
    return ToolError(
        code=StableErrorCode.UI_CHANGED,
        message="Billy invoice delete confirm is not named.",
        details=dump,
    )


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


async def _click_slet(page: Page) -> tuple[str, ToolError | None]:
    """Click the A ancestor of unique Slet text. Else the unique text."""

    for _ in range(20):
        texts = await _visible_named(page.get_by_text(DELETE, exact=True))
        if len(texts) == 1:
            ancestor = texts[0].locator("xpath=ancestor::a[1]")
            if await ancestor.count() == 1 and await ancestor.first.is_visible():
                await ancestor.first.click()
                return "a", None
            await texts[0].click()
            return "span", None
        await asyncio.sleep(0.25)
    return "none", ToolError(
        code=StableErrorCode.UI_CHANGED,
        message="Billy Slet control is not unique.",
    )


async def _visible_named(labels: Locator) -> list[Locator]:
    """Visible locators for one exact name."""

    hits: list[Locator] = []
    for index in range(await labels.count()):
        target = labels.nth(index)
        if await target.is_visible():
            hits.append(target)
    return hits
