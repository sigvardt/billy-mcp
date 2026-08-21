"""One FastMCP login sequence for the write profile and the independent read-back profile."""

from __future__ import annotations

from billy_mcp.browser import AuthLoginService
from billy_mcp.models import (
    AuthLoginStartSuccess,
    AuthLoginWaitSuccess,
    StableErrorCode,
    ToolError,
)

_RETRYABLE = {StableErrorCode.UI_CHANGED, StableErrorCode.AUTH_REQUIRED}


class DualSessionLogin:
    """Drive write then read-back login with the same configured references."""

    def __init__(self, write: AuthLoginService, readback: AuthLoginService) -> None:
        self._write = write
        self._readback = readback

    async def auth_login_start(self) -> AuthLoginStartSuccess | ToolError:
        return await self._write.auth_login_start()

    async def auth_login_wait(self) -> AuthLoginWaitSuccess | ToolError:
        write = await self._ready_write()
        if isinstance(write, ToolError) or write.status == "AUTH_REQUIRED":
            return write
        return await self._prove_readback(write)

    async def _ready_write(self) -> AuthLoginWaitSuccess | ToolError:
        observed = await self._write.auth_login_wait()
        if isinstance(observed, AuthLoginWaitSuccess) and observed.status == "READY":
            return observed
        if isinstance(observed, ToolError) and observed.code not in _RETRYABLE:
            return observed
        started = await self._write.auth_login_start()
        if isinstance(started, ToolError) and started.code != StableErrorCode.UI_CHANGED:
            return started
        after_start = await self._write.auth_login_wait()
        if isinstance(after_start, ToolError) and after_start.code == StableErrorCode.UI_CHANGED:
            return await self._write.auth_login_wait()
        return after_start

    async def _prove_readback(
        self, write: AuthLoginWaitSuccess
    ) -> AuthLoginWaitSuccess | ToolError:
        observed = await self._ensure_readback_ready(await self._readback.auth_login_wait())
        if isinstance(observed, ToolError):
            return observed
        if observed.status == "AUTH_REQUIRED":
            return ToolError(
                code=StableErrorCode.ORGANIZATION_REQUIRED,
                message="Billy organisation slug is not available for the UI write.",
            )
        if observed.organization_id != write.organization_id:
            return ToolError(
                code=StableErrorCode.CONFIRMATION_MISMATCH,
                message="Live Billy organisation does not match the confirmation ticket.",
            )
        return write

    async def _ensure_readback_ready(
        self, observed: AuthLoginWaitSuccess | ToolError
    ) -> AuthLoginWaitSuccess | ToolError:
        if isinstance(observed, ToolError) or observed.status == "READY":
            return observed
        started = await self._readback.auth_login_start()
        if isinstance(started, ToolError):
            return ToolError(
                code=StableErrorCode.ORGANIZATION_REQUIRED,
                message="Billy organisation slug is not available for the UI write.",
            )
        return await self._readback.auth_login_wait()
