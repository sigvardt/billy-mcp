"""Browser actor for ticketed Billy product create."""

from __future__ import annotations

import asyncio

from pydantic import JsonValue

from billy_mcp.browser import BrowserRuntime, LoginControl, LoginPage
from billy_mcp.models import StableErrorCode, ToolError
from billy_mcp.ui_writes.page_flow import (
    BILLY_ORIGIN,
    prove_text_on_fresh_page,
    require_matching_org_slug,
)

_OPRET: str = "Opret produkt"
_OPRET_LIST: str = "Opret produkter"
_GEM: str = "Gem produkt"
_PRICE_LABEL: str = "Enhedspris"
_HEADING: str = "Produkter"


class BrowserProductSubmitter:
    def __init__(
        self,
        runtime: BrowserRuntime,
        readback_runtime: BrowserRuntime | None = None,
    ) -> None:
        self._runtime = runtime
        self._readback_runtime = readback_runtime or runtime.independent_readback_runtime()

    async def submit_create(
        self,
        request: dict[str, JsonValue],
        organization_id: str = "",
    ) -> object:
        name = str(request.get("name") or "")
        price_text = _price_text(request.get("unitPrice"))
        bound = organization_id.strip()
        if not name or not price_text or not bound:
            return ToolError(
                code=StableErrorCode.VALIDATION_ERROR,
                message="Product create requires a name, unit price, and organisation.",
            )
        try:
            context = await self._runtime.start()
            page = await context.new_page()
        except (OSError, RuntimeError, AssertionError):
            return ToolError(
                code=StableErrorCode.BILLY_ERROR,
                message="Billy interface write could not start the browser.",
            )
        try:
            filled = await _fill_and_save(page, organization_id=bound, name=name, price=price_text)
            if isinstance(filled, ToolError):
                return filled
        finally:
            await page.close()
        proved = await prove_text_on_fresh_page(
            self._readback_runtime,
            organization_id=bound,
            path="products",
            text=name,
            allow_search=False,
            visible_body=True,
        )
        if isinstance(proved, ToolError) and proved.code == StableErrorCode.NOT_FOUND:
            return await prove_text_on_fresh_page(
                self._readback_runtime,
                organization_id=bound,
                path="inventory",
                text=name,
                allow_search=False,
                visible_body=True,
            )
        return proved


async def _fill_and_save(
    page: LoginPage, *, organization_id: str, name: str, price: str
) -> ToolError | None:
    """Open /products create, fill name and Enhedspris, then Gem produkt."""

    slug = await require_matching_org_slug(page, organization_id, "products")
    if isinstance(slug, ToolError):
        return slug
    await page.goto(
        f"{BILLY_ORIGIN}/{slug}/products",
        wait_until="domcontentloaded",
    )
    await _settle(page)
    if not await _wait_heading(page):
        return ToolError(
            code=StableErrorCode.UI_CHANGED,
            message="Billy Produkter heading is not visible.",
        )
    if not await _click_visible(page, _OPRET_LIST):
        if not await _click_visible(page, _OPRET):
            return ToolError(
                code=StableErrorCode.UI_CHANGED,
                message="Billy control Opret produkter is not visible.",
            )
    await _settle(page)
    name_field = page.locator("input[name='name']")
    if not await _wait_visible(name_field):
        if not await _click_visible(page, _OPRET):
            return ToolError(
                code=StableErrorCode.UI_CHANGED,
                message="Billy control Opret produkt is not visible.",
            )
        await _settle(page)
        name_field = page.locator("input[name='name']")
        if not await _wait_visible(name_field):
            return ToolError(
                code=StableErrorCode.UI_CHANGED,
                message="Billy field name is not visible.",
            )
    await name_field.first.fill(name)
    await name_field.first.press("Tab")
    if not await _fill_price(page, price):
        return ToolError(
            code=StableErrorCode.UI_CHANGED,
            message="Billy field Enhedspris is not visible.",
        )
    await asyncio.sleep(0.3)
    if not await _click_visible(page, _GEM):
        return ToolError(
            code=StableErrorCode.UI_CHANGED,
            message="Billy control Gem produkt is not visible.",
        )
    leftover = await _wait_create_dialog_closed(page)
    if leftover is not None:
        return ToolError(
            code=StableErrorCode.UI_CHANGED,
            message=f"Billy product create dialog stayed open after Gem produkt: {leftover}",
        )
    await page.goto(
        f"{BILLY_ORIGIN}/{slug}/products",
        wait_until="domcontentloaded",
    )
    await _settle(page)
    return None


async def _wait_create_dialog_closed(page: LoginPage) -> str | None:
    """Return visible leftover text when the create dialog does not close."""

    await _settle(page)
    last = "create dialog still open after Gem produkt"
    for _ in range(10):
        leftover = await _create_dialog_leftover(page)
        if leftover is None:
            return None
        last = leftover
        await asyncio.sleep(0.25)
    return last


def leftover_create_dialog_message(*, form_visible: bool, validation: str) -> str | None:
    """Return leftover text only for visible validation. Ember nodes are not failure."""

    del form_visible
    return validation or None


async def _create_dialog_leftover(page: LoginPage) -> str | None:
    heading = page.get_by_role("heading", name=_OPRET, exact=True)
    heading_open = await heading.count() >= 1 and await heading.first.is_visible()
    validation = await _visible_validation(page)
    return leftover_create_dialog_message(form_visible=heading_open, validation=validation)


async def _visible_validation(page: LoginPage) -> str:
    texts: list[str] = []
    for selector in (
        "[role='alert']",
        "[data-cy*='error']",
        "[data-cy*='validation']",
        ".error",
        ".ds-form-error",
        ".help-block",
    ):
        loc = page.locator(selector)
        found = await loc.count()
        for index in range(min(found, 5)):
            item = loc.nth(index)
            if await item.is_visible():
                raw = (await item.inner_text()).strip()
                if raw:
                    texts.append(raw)
    return " ".join(texts)[:400]


async def _fill_price(page: LoginPage, price: str) -> bool:
    labeled = page.get_by_label(_PRICE_LABEL, exact=True)
    if await labeled.count() < 1:
        labeled = page.get_by_label(_PRICE_LABEL)
    if await labeled.count() >= 1 and await labeled.first.is_visible():
        await labeled.first.fill(price)
        await labeled.first.press("Tab")
        return True
    named = page.locator("input[name='unitPrice']")
    if await named.count() >= 1 and await named.first.is_visible():
        await named.first.fill(price)
        await named.first.press("Tab")
        return True
    return False


async def _click_visible(page: LoginPage, label: str) -> bool:
    for _ in range(20):
        button = page.get_by_role("button", name=label, exact=True)
        if await button.count() >= 1 and await button.first.is_visible():
            await button.first.click()
            return True
        text = page.get_by_text(label, exact=True)
        if await text.count() >= 1 and await text.first.is_visible():
            await text.first.click()
            return True
        await asyncio.sleep(0.25)
    return False


async def _wait_heading(page: LoginPage) -> bool:
    for _ in range(20):
        heading = page.locator("h1")
        if await heading.count() >= 1 and await heading.first.is_visible():
            if (await heading.first.inner_text()).strip() == _HEADING:
                return True
        await asyncio.sleep(0.25)
    return False


async def _wait_visible(control: LoginControl) -> bool:
    target = control.first
    for _ in range(20):
        if await target.count() >= 1 and await target.is_visible():
            return True
        await asyncio.sleep(0.25)
    return False


async def _settle(page: LoginPage) -> None:
    try:
        await page.wait_for_load_state("networkidle", timeout=15000)
    except TimeoutError:
        pass


def _price_text(raw: JsonValue | None) -> str:
    """Render a ticket unit price as the Billy form text."""

    if isinstance(raw, bool) or not isinstance(raw, int | float):
        return ""
    if raw == int(raw):
        return str(int(raw))
    return str(raw).replace(".", ",")
