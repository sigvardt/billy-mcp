"""Open one invoice list row by exact visible customer text."""

from __future__ import annotations

import asyncio
from urllib.parse import urlsplit

from billy_mcp.models import StableErrorCode, ToolError
from billy_mcp.ui_writes.invoices_form_page import Locator, Page
from billy_mcp.ui_writes.page_flow import BILLY_ORIGIN

try:
    from playwright.async_api import TimeoutError as PlaywrightTimeoutError
except ImportError:
    PlaywrightTimeoutError = TimeoutError

ROW_SELECTOR = "li[role=row]"
_ROW_ANCESTORS = (
    "xpath=ancestor::li[@role='row'][1]",
    "xpath=ancestor::*[@role='row'][1]",
    "xpath=ancestor::*[@data-cy='table-item'][1]",
)
_CLICK_TIMEOUT = 2000


def edit_url_opened(url: str) -> bool:
    """True when the page is a draft invoice edit route, not the list or create form."""

    path = url.split("?", 1)[0].rstrip("/")
    return "/invoices/" in path and path.endswith("/edit")


async def open_invoice_row(page: Page, slug: str, contact_name: str) -> ToolError | None:
    """Click the exact customer row on /invoices. Do not goto a POST id."""

    tag = contact_name.strip()
    if not tag:
        return ToolError(
            code=StableErrorCode.VALIDATION_ERROR,
            message="Invoice update and delete require the visible customer name.",
        )
    await page.goto(f"{BILLY_ORIGIN}/{slug}/invoices", wait_until="domcontentloaded")
    try:
        await page.wait_for_load_state("networkidle")
    except (TimeoutError, RuntimeError):
        pass
    labels = page.get_by_text(tag, exact=True)
    for index in range(await labels.count()):
        label = labels.nth(index)
        if not await label.is_visible():
            continue
        if await _open_from_target(page, label):
            return None
        for ancestor in _ROW_ANCESTORS:
            row = label.locator(ancestor)
            try:
                if await row.count() < 1:
                    continue
            except PlaywrightTimeoutError:
                continue
            if await _open_from_target(page, row.first):
                return None
        return ToolError(
            code=StableErrorCode.UI_CHANGED,
            message="Invoice row click did not open the draft edit page.",
            details={"contact_name": tag, "path": urlsplit(page.url).path},
        )
    return ToolError(
        code=StableErrorCode.UI_CHANGED,
        message="Billy invoice list does not show that customer row.",
        details={"contact_name": tag, "row": ROW_SELECTOR},
    )


async def _open_from_target(page: Page, target: Locator) -> bool:
    clicked = await _click_invoice_target(page, target)
    if not clicked:
        return False
    return await _wait_for_edit_form(page)


async def _click_invoice_target(page: Page, target: Locator) -> bool:
    try:
        box = await target.bounding_box(timeout=_CLICK_TIMEOUT)
    except (PlaywrightTimeoutError, TimeoutError, RuntimeError, TypeError):
        box = None
    if box is None:
        try:
            await target.click(timeout=_CLICK_TIMEOUT)
        except (PlaywrightTimeoutError, TimeoutError, RuntimeError, TypeError):
            return False
        return True
    x = float(box["x"]) + float(box["width"]) / 2
    y = float(box["y"]) + float(box["height"]) / 2
    await page.mouse.click(x, y)
    return True


async def _wait_for_edit_form(page: Page) -> bool:
    for _ in range(40):
        if edit_url_opened(page.url):
            try:
                await page.wait_for_load_state("networkidle")
            except (TimeoutError, RuntimeError):
                pass
            return True
        await asyncio.sleep(0.25)
    return False
