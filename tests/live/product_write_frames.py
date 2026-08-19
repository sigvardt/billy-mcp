"""Owner-only products-list screenshots for live write qualification."""

from __future__ import annotations

from pathlib import Path

from billy_mcp.browser import BrowserRuntime, LoginPage
from billy_mcp.ui_writes.page_flow import exact_name_in_text


async def capture_products_list(runtime: BrowserRuntime, slug: str, destination: Path) -> None:
    """Screenshot /products in this session. Fail if the file is missing or empty."""

    context = await runtime.start()
    page = await context.new_page()
    try:
        await open_named_list(page, slug, "products")
        capture = getattr(page, "screenshot", None)
        assert capture is not None
        await capture(path=str(destination), full_page=False)
        assert destination.is_file() and destination.stat().st_size > 0
    finally:
        await page.close()


async def open_named_list(page: LoginPage, slug: str, path: str) -> None:
    """Open /:slug/:path and wait for network idle when the SPA settles."""

    await page.goto(f"https://mit.billy.dk/{slug}/{path}", wait_until="domcontentloaded")
    try:
        await page.wait_for_load_state("networkidle", timeout=20000)
    except TimeoutError:
        pass


async def list_has_name(runtime: BrowserRuntime, slug: str, name: str) -> bool:
    """True when the tagged name is visible on /products or /inventory."""

    context = await runtime.start()
    page = await context.new_page()
    try:
        for path in ("products", "inventory"):
            await open_named_list(page, slug, path)
            body = await page.locator("body").inner_text()
            if exact_name_in_text(body, name):
                return True
            search = page.locator("input[type='search'], input[placeholder*='øg' i]")
            if await search.count() >= 1:
                await search.first.fill(name)
                body = await page.locator("body").inner_text()
                if exact_name_in_text(body, name):
                    return True
        return False
    finally:
        await page.close()
