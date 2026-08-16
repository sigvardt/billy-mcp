"""READY must return the live URL slug and login must READY the read-back session."""

from __future__ import annotations

import asyncio
from typing import cast

import pytest
from fastmcp import FastMCP
from pydantic import ValidationError

from billy_mcp.browser import BrowserRuntime
from billy_mcp.models import (
    AuthLoginStartSuccess,
    AuthLoginWaitSuccess,
    StableErrorCode,
)
from billy_mcp.server import create_server


def _call(
    server: FastMCP, tool_name: str, arguments: dict[str, object] | None = None
) -> dict[str, object]:
    result = asyncio.run(server.call_tool(tool_name, arguments or {}))
    assert isinstance(result.structured_content, dict)
    structured = cast(dict[str, object], result.structured_content)
    payload = structured.get("result", structured)
    assert isinstance(payload, dict)
    return cast(dict[str, object], payload)


def _arm_login(
    monkeypatch: pytest.MonkeyPatch,
    *,
    write_status: str,
    write_slug: str | None,
    readback_status: str,
    readback_slug: str | None,
) -> list[str]:
    waits: list[str] = []
    starts: list[str] = []

    async def _wait(self: BrowserRuntime) -> AuthLoginWaitSuccess:
        name = self.profile_path.name
        waits.append(name)
        if name.endswith("-readback"):
            if readback_status == "READY":
                assert readback_slug is not None
                return AuthLoginWaitSuccess(status="READY", organization_id=readback_slug)
            return AuthLoginWaitSuccess(status="AUTH_REQUIRED")
        if write_status == "READY":
            assert write_slug is not None
            return AuthLoginWaitSuccess(status="READY", organization_id=write_slug)
        return AuthLoginWaitSuccess(status="AUTH_REQUIRED")

    async def _start(self: BrowserRuntime) -> AuthLoginStartSuccess:
        starts.append(self.profile_path.name)
        return AuthLoginStartSuccess()

    monkeypatch.setattr(BrowserRuntime, "auth_login_wait", _wait)
    monkeypatch.setattr(BrowserRuntime, "auth_login_start", _start)
    return waits


def test_ready_without_organization_id_is_invalid() -> None:
    with pytest.raises(ValidationError):
        AuthLoginWaitSuccess(status="READY")


def test_auth_login_wait_ready_includes_live_url_slug(monkeypatch: pytest.MonkeyPatch) -> None:
    _arm_login(
        monkeypatch,
        write_status="READY",
        write_slug="test-org-slug",
        readback_status="READY",
        readback_slug="test-org-slug",
    )
    waited = _call(create_server(), "auth_login_wait")
    assert waited == {"status": "READY", "organization_id": "test-org-slug"}


def test_auth_login_wait_logs_in_blank_readback_when_write_is_ready(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    waits = _arm_login(
        monkeypatch,
        write_status="READY",
        write_slug="org-a",
        readback_status="AUTH_REQUIRED",
        readback_slug=None,
    )
    waited = _call(create_server(), "auth_login_wait")
    assert any(name.endswith("-readback") for name in waits)
    assert waited.get("code") == StableErrorCode.ORGANIZATION_REQUIRED


def test_auth_login_wait_refuses_mismatched_readback_org(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _arm_login(
        monkeypatch,
        write_status="READY",
        write_slug="org-a",
        readback_status="READY",
        readback_slug="org-b",
    )
    waited = _call(create_server(), "auth_login_wait")
    assert waited.get("code") == StableErrorCode.CONFIRMATION_MISMATCH
    assert waited.get("status") != "READY"
