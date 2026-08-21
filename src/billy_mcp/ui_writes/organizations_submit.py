"""Exact company-phone fill, Gem ændringer click, and input read-back."""

from __future__ import annotations

import asyncio
import re
from urllib.parse import urlsplit

from billy_mcp.browser import BrowserRuntime, LoginPage
from billy_mcp.models import StableErrorCode, ToolError
from billy_mcp.ui_writes.organizations_phone import (
    PHONE_INPUT_NAME,
    SAVE_LABEL,
    named_input_matches,
)
from billy_mcp.ui_writes.page_flow import BILLY_ORIGIN

_PHONE_LOCATOR = f"input[name='{PHONE_INPUT_NAME}']"


def _org_slug_from_live_url(url: str) -> str | None:
    path = urlsplit(url).path or ""
    parts = [part for part in path.split("/") if part]
    if parts and parts[0] not in {"login"}:
        return parts[0]
    return None


async def _session_slug(page: LoginPage) -> str | None:
    if not page.url or page.url == "about:blank":
        await page.goto(f"{BILLY_ORIGIN}/", wait_until="domcontentloaded")
    return _org_slug_from_live_url(page.url)


async def _wait_settings_idle(page: LoginPage) -> None:
    try:
        await page.wait_for_load_state("networkidle", timeout=20000)
    except (TimeoutError, RuntimeError):
        pass
    await asyncio.sleep(0.5)


async def fill_phone_input(page: LoginPage, phone: str) -> ToolError | None:
    """Fill the proved company phone input, including exact empty."""

    field = page.locator(_PHONE_LOCATOR)
    if await field.count() < 1:
        return ToolError(
            code=StableErrorCode.UI_CHANGED,
            message="Billy company phone input is not visible.",
        )
    await field.first.fill(phone)
    return None


async def click_exact_gem_aendringer(page: LoginPage) -> ToolError | None:
    """Click the exact Gem ændringer control when the visible count is 1."""

    pattern = re.compile(rf"^{re.escape(SAVE_LABEL)}$")
    role = page.get_by_role("button", name=pattern)
    count = await role.count()
    target = role
    if count != 1:
        text = page.get_by_text(SAVE_LABEL, exact=True)
        count = await text.count()
        target = text
    if count != 1:
        return ToolError(
            code=StableErrorCode.UI_CHANGED,
            message="Billy company save control is not unique.",
        )
    await target.first.click()
    return None


async def prove_phone_input_on_fresh_page(
    runtime: BrowserRuntime,
    *,
    organization_id: str,
    expected: str,
) -> ToolError | None:
    """Prove input[name=phone] on an independent session. Never page text."""

    try:
        context = await runtime.start()
        page = await context.new_page()
    except (OSError, RuntimeError, AssertionError):
        return ToolError(
            code=StableErrorCode.BILLY_ERROR,
            message="Billy interface read-back could not start the browser.",
        )
    try:
        bound = organization_id.strip()
        slug = await _session_slug(page)
        if slug is None and bound:
            await page.goto(
                f"{BILLY_ORIGIN}/{bound}/settings",
                wait_until="domcontentloaded",
            )
            slug = _org_slug_from_live_url(page.url)
        if slug is None:
            return ToolError(
                code=StableErrorCode.ORGANIZATION_REQUIRED,
                message="Billy organisation slug is not available for the UI write.",
            )
        if bound and slug != bound:
            return ToolError(
                code=StableErrorCode.CONFIRMATION_MISMATCH,
                message="Live Billy organisation does not match the confirmation ticket.",
            )
        await page.goto(
            f"{BILLY_ORIGIN}/{slug}/settings",
            wait_until="domcontentloaded",
        )
        await _wait_settings_idle(page)
        field = page.locator(_PHONE_LOCATOR)
        if await field.count() < 1:
            return ToolError(
                code=StableErrorCode.UI_CHANGED,
                message="Billy company phone input is not visible.",
            )
        actual = await field.first.input_value()
        if not named_input_matches(expected, actual):
            return ToolError(
                code=StableErrorCode.NOT_FOUND,
                message="Independent interface read-back did not prove the expected change.",
            )
        return None
    finally:
        await page.close()


async def perform_company_phone_write(
    runtime: BrowserRuntime,
    *,
    organization_id: str,
    phone: str,
    readback_runtime: BrowserRuntime,
) -> ToolError | None:
    """Fill phone, click exact Gem ændringer, prove the input on a second session."""

    try:
        context = await runtime.start()
        page = await context.new_page()
    except (OSError, RuntimeError, AssertionError):
        return ToolError(
            code=StableErrorCode.BILLY_ERROR,
            message="Billy interface write could not start the browser.",
        )
    try:
        bound = organization_id.strip()
        if not bound:
            return ToolError(
                code=StableErrorCode.ORGANIZATION_REQUIRED,
                message="A proven Billy organisation id is required.",
            )
        slug = await _session_slug(page)
        if slug is None:
            await page.goto(
                f"{BILLY_ORIGIN}/{bound}/settings",
                wait_until="domcontentloaded",
            )
            slug = _org_slug_from_live_url(page.url)
        if slug is None:
            return ToolError(
                code=StableErrorCode.ORGANIZATION_REQUIRED,
                message="Billy organisation slug is not available for the UI write.",
            )
        if slug != bound:
            return ToolError(
                code=StableErrorCode.CONFIRMATION_MISMATCH,
                message="Live Billy organisation does not match the confirmation ticket.",
            )
        await page.goto(
            f"{BILLY_ORIGIN}/{slug}/settings",
            wait_until="domcontentloaded",
        )
        await _wait_settings_idle(page)
        failed = await fill_phone_input(page, phone)
        if failed is not None:
            return failed
        failed = await click_exact_gem_aendringer(page)
        if failed is not None:
            return failed
        await _wait_settings_idle(page)
        return await prove_phone_input_on_fresh_page(
            readback_runtime,
            organization_id=bound,
            expected=phone,
        )
    finally:
        await page.close()
