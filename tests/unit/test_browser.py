from __future__ import annotations

import asyncio
from pathlib import Path
from typing import cast

from billy_mcp.browser import (
    BrowserEgressPolicy,
    BrowserRuntime,
    PersistentContext,
    RouteHandler,
)


class FakeRequest:
    def __init__(self, url: str) -> None:
        self.url = url


class FakeRoute:
    def __init__(self, url: str) -> None:
        self.request = FakeRequest(url)
        self.action = ""

    async def continue_(self) -> None:
        self.action = "continued"

    async def abort(self, error_code: str | None = None) -> None:
        self.action = f"aborted:{error_code}"


class FakeContext:
    def __init__(self) -> None:
        self.pattern = ""
        self.handler: RouteHandler | None = None
        self.closed = False

    async def route(self, url: str, handler: RouteHandler) -> None:
        self.pattern = url
        self.handler = handler

    async def close(self) -> None:
        self.closed = True


async def invoke_handler(handler: RouteHandler, route: FakeRoute) -> None:
    await handler(route)


def test_browser_forces_headless_and_denies_unknown_egress() -> None:
    context = FakeContext()
    launch_arguments: dict[str, object] = {}

    async def launcher(profile_path: str, **kwargs: bool) -> PersistentContext:
        launch_arguments["profile_path"] = profile_path
        launch_arguments.update(kwargs)
        return cast(PersistentContext, context)

    runtime = BrowserRuntime(
        profile_path=Path("/tmp/billy-profile"),
        policy=BrowserEgressPolicy(["mit.billy.dk"]),
        launcher=launcher,
    )
    asyncio.run(runtime.start())

    assert launch_arguments["headless"] is True
    assert launch_arguments["accept_downloads"] is False
    assert context.pattern == "**/*"
    assert callable(context.handler)

    allowed = FakeRoute("https://mit.billy.dk/")
    wrong_port = FakeRoute("https://mit.billy.dk:444/")
    denied = FakeRoute("https://analytics.example/")
    handler = context.handler
    assert handler is not None
    asyncio.run(invoke_handler(handler, allowed))
    asyncio.run(invoke_handler(handler, wrong_port))
    asyncio.run(invoke_handler(handler, denied))

    assert allowed.action == "continued"
    assert wrong_port.action == "aborted:blockedbyclient"
    assert denied.action == "aborted:blockedbyclient"
