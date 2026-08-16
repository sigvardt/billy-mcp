"""Bounded Billy page actions for ticketed UI writes. Not generic browser tools."""

from __future__ import annotations

import asyncio
import re
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urlsplit

from billy_mcp.browser import BrowserRuntime, LoginPage
from billy_mcp.models import StableErrorCode, ToolError

BILLY_ORIGIN: str = "https://mit.billy.dk"
_EXACT_NAME_BOUNDARY = r"[\w-]"


def exact_name_in_text(haystack: str, name: str) -> bool:
    """True when name is a whole token, not a prefix of a longer tagged name."""

    if not name:
        return False
    pattern = re.compile(rf"(?<!{_EXACT_NAME_BOUNDARY}){re.escape(name)}(?!{_EXACT_NAME_BOUNDARY})")
    return pattern.search(haystack) is not None


@dataclass(frozen=True, slots=True)
class FamilyWrite:
    """One family-specific Billy interface write plus its independent read-back."""

    write_path: str
    fills: tuple[tuple[str, str], ...]
    clicks: tuple[str, ...]
    readback_path: str
    readback_text: str
    readback_absent: bool = False
    upload_path: Path | None = None
    pre_clicks: tuple[str, ...] = ()


async def perform_family_write(
    runtime: BrowserRuntime,
    action: FamilyWrite,
    *,
    organization_id: str,
    readback_runtime: BrowserRuntime,
) -> ToolError | None:
    """Navigate, fill, click, then prove the result on a second session."""

    try:
        context = await runtime.start()
        page = await context.new_page()
    except (OSError, RuntimeError, AssertionError):
        return ToolError(
            code=StableErrorCode.BILLY_ERROR,
            message="Billy interface write could not start the browser.",
        )
    try:
        slug = await _session_slug(page)
        if slug is None:
            return ToolError(
                code=StableErrorCode.ORGANIZATION_REQUIRED,
                message="Billy organisation slug is not available for the UI write.",
            )
        bound = organization_id.strip()
        if not bound:
            return ToolError(
                code=StableErrorCode.ORGANIZATION_REQUIRED,
                message="A proven Billy organisation id is required.",
            )
        if slug != bound:
            return ToolError(
                code=StableErrorCode.CONFIRMATION_MISMATCH,
                message="Live Billy organisation does not match the confirmation ticket.",
            )
        await page.goto(
            f"{BILLY_ORIGIN}/{slug}/{action.write_path.lstrip('/')}",
            wait_until="domcontentloaded",
        )
        for label in action.pre_clicks:
            missing = await _click_named(page, label)
            if missing is not None:
                return missing
        for field_name, value in action.fills:
            missing = await _fill_named(page, field_name, value)
            if missing is not None:
                return missing
        if action.upload_path is not None:
            file_input = page.locator("input[type='file']")
            if await file_input.count() < 1:
                return ToolError(
                    code=StableErrorCode.UI_CHANGED,
                    message="Billy file input is not visible.",
                )
            await file_input.first.set_input_files(action.upload_path)
        for label in action.clicks:
            missing = await _click_named(page, label)
            if missing is not None:
                return missing
        return await prove_text_on_fresh_page(
            readback_runtime,
            organization_id=bound,
            path=action.readback_path,
            text=action.readback_text,
            absent=action.readback_absent,
        )
    finally:
        await page.close()


async def prove_text_on_fresh_page(
    runtime: BrowserRuntime,
    *,
    path: str,
    text: str,
    absent: bool = False,
    organization_id: str | None = None,
) -> ToolError | None:
    """Prove a marker on an independent session, never on the write context."""

    try:
        context = await runtime.start()
        page = await context.new_page()
    except (OSError, RuntimeError, AssertionError):
        return ToolError(
            code=StableErrorCode.BILLY_ERROR,
            message="Billy interface read-back could not start the browser.",
        )
    try:
        bound = (organization_id or "").strip()
        slug = await _session_slug(page)
        if slug is None and bound and _is_org_less_root(page.url):
            await page.goto(
                f"{BILLY_ORIGIN}/{bound}/{path.lstrip('/')}",
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
            f"{BILLY_ORIGIN}/{slug}/{path.lstrip('/')}",
            wait_until="domcontentloaded",
        )
        try:
            await page.wait_for_load_state("networkidle", timeout=15000)
        except Exception:
            pass
        search = page.locator("input[type='search'], input[placeholder*='øg' i]")
        if await search.count() >= 1:
            await search.first.fill(text)
            await asyncio.sleep(1.5)
        found = await page.get_by_text(text, exact=True).count()
        if absent:
            if found >= 1:
                return ToolError(
                    code=StableErrorCode.CONFLICT,
                    message="Independent interface read-back still shows the deleted record.",
                )
            return None
        if found < 1:
            return ToolError(
                code=StableErrorCode.NOT_FOUND,
                message="Independent interface read-back did not prove the expected change.",
            )
        return None
    finally:
        await page.close()


def _org_slug_from_live_url(url: str) -> str | None:
    path = urlsplit(url).path or ""
    parts = [part for part in path.split("/") if part]
    if parts and parts[0] not in {"login"}:
        return parts[0]
    return None


def _is_org_less_root(url: str) -> bool:
    path = urlsplit(url).path or ""
    return not [part for part in path.split("/") if part]


async def _session_slug(page: LoginPage) -> str | None:
    if not page.url or page.url == "about:blank":
        await page.goto(f"{BILLY_ORIGIN}/", wait_until="domcontentloaded")
    return _org_slug_from_live_url(page.url)


async def _fill_named(page: LoginPage, field_name: str, value: str) -> ToolError | None:
    field = page.locator(f"input[name='{field_name}']")
    if await field.count() < 1:
        return ToolError(
            code=StableErrorCode.UI_CHANGED,
            message=f"Billy field {field_name} is not visible.",
        )
    await field.first.fill(value)
    return None


async def _click_named(page: LoginPage, label: str) -> ToolError | None:
    control = page.locator(f"text={label}")
    if await control.count() >= 1 and await control.first.is_visible():
        await control.first.click()
        return None
    return ToolError(
        code=StableErrorCode.UI_CHANGED,
        message=f"Billy control {label} is not visible.",
    )
