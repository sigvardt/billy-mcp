"""Scoped product table-item delete and unfiltered row absence."""

from __future__ import annotations

import asyncio
from typing import Final

from billy_mcp.browser import BrowserRuntime, LoginPage
from billy_mcp.models import StableErrorCode, ToolError
from billy_mcp.ui_writes.page_flow import BILLY_ORIGIN, require_matching_org_slug

CONFIRM: Final = "Ja, slet"
DELETE_ICON: Final = "[data-cy='delete-icon']"
TABLE_ITEM: Final = "[data-cy='table-item']"
LIST_PATHS: Final = ("products", "inventory")


async def delete_tagged_row(
    page: LoginPage,
    *,
    organization_id: str,
    path: str,
    tag: str,
) -> bool:
    """Click the tagged row delete-icon and confirm. True when both clicks ran."""

    await page.goto(
        f"{BILLY_ORIGIN}/{organization_id}/{path}",
        wait_until="domcontentloaded",
    )
    try:
        await page.wait_for_load_state("networkidle", timeout=15000)
    except TimeoutError:
        pass
    match = page.get_by_text(tag, exact=True)
    if await match.count() < 1:
        return False
    row = page.locator(TABLE_ITEM).filter(has=match)
    if await row.count() < 1:
        return False
    await row.first.hover()
    icon = row.locator(DELETE_ICON)
    if await icon.count() < 1 or not await icon.first.is_visible():
        return False
    try:
        await icon.first.click(timeout=5000)
    except Exception as exc:
        if type(exc).__name__ != "TimeoutError":
            raise
        return False
    confirm = page.get_by_role("button", name=CONFIRM, exact=True)
    if await confirm.count() < 1:
        confirm = page.get_by_text(CONFIRM, exact=True)
    if await confirm.count() < 1 or not await confirm.first.is_visible():
        return False
    await confirm.first.click()
    await _wait_row_gone(page, tag)
    return True


async def prove_unfiltered_row_absent(
    runtime: BrowserRuntime,
    *,
    organization_id: str,
    tag: str,
) -> ToolError | None:
    """Fresh /products. Absence is no visible table-item with the exact tag."""

    try:
        context = await runtime.start()
        page = await context.new_page()
    except (OSError, RuntimeError, AssertionError):
        return ToolError(
            code=StableErrorCode.BILLY_ERROR,
            message="Billy interface read-back could not start the browser.",
        )
    try:
        slug = await require_matching_org_slug(page, organization_id, "products")
        if isinstance(slug, ToolError):
            return slug
        await page.goto(
            f"{BILLY_ORIGIN}/{slug}/products",
            wait_until="domcontentloaded",
        )
        try:
            await page.wait_for_load_state("networkidle", timeout=15000)
        except TimeoutError:
            pass
        if await _visible_tagged_rows(page, tag) >= 1:
            return ToolError(
                code=StableErrorCode.CONFLICT,
                message="Independent interface read-back still shows the deleted record.",
            )
        return None
    finally:
        await page.close()


async def _wait_row_gone(page: LoginPage, tag: str) -> None:
    """Wait briefly for the write-page row to leave after Ja, slet."""

    for _ in range(20):
        if await _visible_tagged_rows(page, tag) < 1:
            return
        await asyncio.sleep(0.25)


async def _visible_tagged_rows(page: LoginPage, tag: str) -> int:
    """Count visible table-item rows that contain the exact tag."""

    match = page.get_by_text(tag, exact=True)
    rows = page.locator(TABLE_ITEM).filter(has=match)
    visible = 0
    for index in range(await rows.count()):
        if await rows.nth(index).is_visible():
            visible += 1
    return visible
