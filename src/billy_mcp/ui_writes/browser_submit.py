"""Shared BrowserRuntime entry for default UI write submitters."""

from __future__ import annotations

from typing import Protocol

from billy_mcp.browser import BrowserRuntime
from billy_mcp.config import AppConfig
from billy_mcp.models import StableErrorCode, ToolError


class StartedBrowserContext(Protocol):
    """The persistent Playwright context returned by BrowserRuntime.start."""

    async def new_page(self) -> object: ...


def default_browser_runtime() -> BrowserRuntime:
    """Build the MCP-owned runtime used when create_server did not pass one."""

    configuration = AppConfig.from_environment()
    return BrowserRuntime(
        configuration.browser_profile,
        credential_references=configuration.browser_credentials,
    )


async def enter_browser_runtime(runtime: BrowserRuntime) -> StartedBrowserContext | ToolError:
    """Open the persistent headless context. Preview must never call this."""

    try:
        return await runtime.start()
    except OSError:
        return ToolError(
            code=StableErrorCode.BILLY_ERROR,
            message="Billy interface write could not start the browser.",
        )
