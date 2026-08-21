"""Commit and independently prove invoice Enhedspris. A fill is not persist."""

from __future__ import annotations

from typing import cast

from billy_mcp.browser import BrowserRuntime
from billy_mcp.models import StableErrorCode, ToolError
from billy_mcp.ui_writes.invoices_form_bind import (
    enhedspris_missing_details,
    price_is,
    read_unit_price,
    unit_price_field,
)
from billy_mcp.ui_writes.invoices_form_page import Page
from billy_mcp.ui_writes.invoices_form_row import open_invoice_row


def danish_price(unit_price: float) -> str:
    """Billy line prices show a comma decimal, including whole kroner."""

    return f"{unit_price:.2f}".replace(".", ",")


async def commit_unit_price(page: Page, unit_price: float) -> ToolError | None:
    """Fill Enhedspris 2,00 once on the evidenced locator. Do not re-resolve."""

    field = await unit_price_field(page)
    if field is None:
        return ToolError(
            code=StableErrorCode.UI_CHANGED,
            message="Billy invoice unit price field is not visible.",
            details=await enhedspris_missing_details(page),
        )
    text = danish_price(unit_price)
    await field.fill(text)
    try:
        shown = await field.input_value()
    except (TimeoutError, RuntimeError):
        shown = ""
    if shown != text:
        return ToolError(
            code=StableErrorCode.UI_CHANGED,
            message="Billy invoice unit price did not keep the filled value.",
            details={"shown_len": len(shown)},
        )
    try:
        await field.press("Tab")
    except (TimeoutError, RuntimeError, AttributeError):
        pass
    try:
        shown = await field.input_value()
    except (TimeoutError, RuntimeError):
        shown = ""
    if shown != text:
        return ToolError(
            code=StableErrorCode.UI_CHANGED,
            message="Billy invoice unit price did not keep the filled value.",
            details={"shown_len": len(shown)},
        )
    return None


async def prove_fresh_unit_price(
    runtime: BrowserRuntime,
    slug: str,
    contact_name: str,
    unit_price: float,
) -> ToolError | None:
    """Open the leftover row in a second session and prove Enhedspris."""

    context = await runtime.start()
    page = cast(Page, await context.new_page())
    try:
        failed = await open_invoice_row(page, slug, contact_name)
        if failed is not None:
            return failed
        shown = await read_unit_price(page)
        if price_is(shown, unit_price):
            return None
        return ToolError(
            code=StableErrorCode.UI_CHANGED,
            message="Billy invoice unit price did not persist.",
            details={"shown_len": len(shown)},
        )
    finally:
        await page.close()
