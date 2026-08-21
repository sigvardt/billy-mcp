"""Owner leftover MCP-UI-PRD tags and visible-list sweep helpers."""

from __future__ import annotations

import re
from collections.abc import Awaitable, Callable
from typing import Any

from billy_mcp.browser import BrowserRuntime

PRD_TAG = re.compile(r"MCP-UI-PRD-[0-9A-F]{8}")
OWNER_LEFTOVERS = (
    "MCP-UI-PRD-C0082FCA",
    "MCP-UI-PRD-2A0968A4",
    "MCP-UI-PRD-773A4D76",
    "MCP-UI-PRD-0116A3D1",
    "MCP-UI-PRD-9A032275",
    "MCP-UI-PRD-22679129",
    "MCP-UI-PRD-2647389E",
)

OpenNamedList = Callable[[Any, str, str], Awaitable[None]]


async def visible_prd_tags(
    runtime: BrowserRuntime,
    slug: str,
    open_named_list: OpenNamedList,
) -> list[str]:
    """Return unique visible MCP-UI-PRD tags on /products."""

    context = await runtime.start()
    page = await context.new_page()
    try:
        await open_named_list(page, slug, "products")
        body = await page.locator("body").inner_text()
        return list(dict.fromkeys(PRD_TAG.findall(body)))
    finally:
        await page.close()
