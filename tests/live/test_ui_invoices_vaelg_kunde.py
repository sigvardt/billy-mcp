"""Live rest inspect: exact Vælg kunde named control on invoices/new.

Opens create through FastMCP. Counts exact Vælg kunde. Clicks only when the
control is unique and is not the contact input. Never Godkend, Send, or email.
"""

from __future__ import annotations

import asyncio
import atexit
import json
import os
import shutil
import tempfile
from pathlib import Path
from typing import Any, cast

import pytest
from fastmcp import FastMCP

from billy_mcp.browser import BrowserRuntime
from billy_mcp.config import AppConfig
from billy_mcp.credentials import KeyringCredentialResolver
from billy_mcp.models import AuthLoginWaitSuccess, StableErrorCode, ToolError
from billy_mcp.server import create_server
from billy_mcp.ui_writes.invoices_vaelg_kunde import (
    REQUIRED_VAELG_KUNDE_KEYS,
    VAELG_KUNDE_DUMP,
    capture_vaelg_kunde,
    vaelg_kunde_dump_is_delivered,
    vaelg_kunde_missing_keys,
)
from billy_mcp.ui_writes.page_flow import BILLY_ORIGIN

pytestmark = pytest.mark.live

_REPO_ROOT = Path(__file__).resolve().parents[2]
_DATA_ROOT = Path.home() / ".local" / "share" / "billy-mcp"
_BLOCKER_PATH = (
    _REPO_ROOT
    / ".fractal"
    / "main.billy_complete"
    / "tmp"
    / "live-invoices-vaelg-kunde-blocker.txt"
)
_REGISTERED_PROFILES: list[Path] = []


def _credentials_configured() -> bool:
    return bool(
        os.environ.get("BILLY_BROWSER_PRIMARY_REFERENCE", "").strip()
        and os.environ.get("BILLY_BROWSER_SECONDARY_REFERENCE", "").strip()
    )


def _record_blocker(reason: str) -> None:
    _BLOCKER_PATH.parent.mkdir(parents=True, exist_ok=True)
    _BLOCKER_PATH.write_text(reason.strip() + "\n", encoding="utf-8")


def _require_live_credentials() -> None:
    if _credentials_configured():
        return
    reason = (
        "Live Vælg kunde inspect blocked: BILLY_BROWSER_PRIMARY_REFERENCE and "
        "BILLY_BROWSER_SECONDARY_REFERENCE are not both set."
    )
    _record_blocker(reason)
    pytest.skip(reason)


def _purge_registered_profiles() -> None:
    for path in _REGISTERED_PROFILES:
        shutil.rmtree(path, ignore_errors=True)


atexit.register(_purge_registered_profiles)


def _temp_profile() -> Path:
    _DATA_ROOT.mkdir(parents=True, exist_ok=True)
    path = Path(tempfile.mkdtemp(prefix="billy-live-invoices-", dir=str(_DATA_ROOT)))
    _REGISTERED_PROFILES.append(path)
    _REGISTERED_PROFILES.append(path.with_name(f"{path.name}-readback"))
    return path


async def _call(
    server: FastMCP, tool_name: str, arguments: dict[str, object] | None = None
) -> dict[str, object]:
    result = await server.call_tool(tool_name, arguments or {})
    structured = result.structured_content
    assert isinstance(structured, dict)
    payload = structured.get("result", structured)
    assert isinstance(payload, dict)
    return cast(dict[str, object], payload)


async def _login(server: FastMCP) -> str:
    started = await _call(server, "auth_login_start")
    if started.get("code") and started.get("code") != StableErrorCode.UI_CHANGED:
        _record_blocker(f"auth_login_start failed: {started}")
        pytest.fail(f"auth_login_start failed: {started}")
    waited = await _call(server, "auth_login_wait")
    if waited.get("code") == StableErrorCode.AUTH_INTERACTION_REQUIRED:
        _record_blocker(f"AUTH_INTERACTION_REQUIRED: {waited}")
        pytest.fail(f"non-automatable challenge: {waited}")
    if waited.get("status") != "READY":
        waited = await _call(server, "auth_login_wait")
    if waited.get("status") != "READY":
        _record_blocker(f"auth_login_wait not READY: {waited}")
        pytest.fail(f"auth_login_wait not READY: {waited}")
    slug = waited.get("organization_id")
    if not isinstance(slug, str) or not slug.strip():
        _record_blocker("auth_login_wait READY omitted organization_id")
        pytest.fail("READY omitted organization_id")
    return slug


async def _ready_session(runtime: BrowserRuntime, slug: str) -> None:
    started = await runtime.auth_login_start()
    if isinstance(started, ToolError) and started.code != StableErrorCode.UI_CHANGED:
        pytest.fail(f"session login start failed: {started.code}")
    waited = await runtime.auth_login_wait()
    if isinstance(waited, AuthLoginWaitSuccess) and waited.status != "READY":
        waited = await runtime.auth_login_wait()
    if isinstance(waited, ToolError):
        pytest.fail(f"session login failed: {waited.code}")
    assert isinstance(waited, AuthLoginWaitSuccess)
    assert waited.status == "READY"
    if waited.organization_id != slug:
        pytest.fail("observer organization did not match the FastMCP session")


def _assert_dump_clean(payload: dict[str, object], *, require_code: bool = False) -> None:
    assert vaelg_kunde_missing_keys(payload) == []
    assert set(REQUIRED_VAELG_KUNDE_KEYS) <= set(payload)
    encoded = json.dumps({"result": payload})
    assert "https://" not in encoded
    assert "function(" not in encoded
    assert "confirmation_ticket" not in encoded
    assert "MCP-UI-INV-" not in encoded
    if require_code and (
        payload.get("unique_vaelg_kunde") is not True or payload.get("proved_bind") == "none"
    ):
        assert payload.get("code") == "UI_CHANGED"


@pytest.mark.asyncio
async def test_ui_invoices_vaelg_kunde(monkeypatch: pytest.MonkeyPatch) -> None:
    """Count exact Vælg kunde on invoices/new. Do not save."""

    _require_live_credentials()
    assert not os.environ.get("BILLY_API_TOKEN"), "vaelg kunde dump must not use API token"
    if vaelg_kunde_dump_is_delivered():
        written = json.loads(VAELG_KUNDE_DUMP.read_text(encoding="utf-8"))
        _assert_dump_clean(written)
        text = VAELG_KUNDE_DUMP.read_text(encoding="utf-8")
        assert "https://" not in text
        assert "MCP-UI-INV-" not in text
        return

    profile = _temp_profile()
    observer_profile = _temp_profile()
    monkeypatch.setenv("BILLY_BROWSER_PROFILE", str(profile))
    monkeypatch.delenv("BILLY_ORGANIZATION_ID", raising=False)
    extra: BrowserRuntime | None = None
    page: Any = None
    server: FastMCP | None = None

    try:
        server = create_server(_REPO_ROOT)
        slug = await _login(server)
        opened = await _call(server, "ui_invoices_create_open")
        if opened.get("code"):
            _record_blocker(f"ui_invoices_create_open failed: {opened}")
            pytest.fail(f"ui_invoices_create_open failed: {opened}")
        assert opened.get("path_class") == "/:org_slug/invoices/new"
        observer = BrowserRuntime(
            observer_profile,
            credential_references=AppConfig.from_environment().browser_credentials,
            credential_resolver=KeyringCredentialResolver(),
        )
        extra = observer
        await _ready_session(observer, slug)
        context = await observer.start()
        page = cast(Any, await context.new_page())
        await page.goto(f"{BILLY_ORIGIN}/{slug}/invoices/new", wait_until="domcontentloaded")
        try:
            await page.wait_for_load_state("networkidle", timeout=20000)
        except (TimeoutError, RuntimeError):
            pass
        result = await capture_vaelg_kunde(page)
        _assert_dump_clean(result, require_code=True)
        assert VAELG_KUNDE_DUMP.is_file()
        written = json.loads(VAELG_KUNDE_DUMP.read_text(encoding="utf-8"))
        _assert_dump_clean(written)
        if result.get("clicked") is True:
            assert result.get("unique_vaelg_kunde") is True
            assert result.get("hit_is_contact_input") is False
    finally:
        if page is not None:
            await page.close()
        if extra is not None:
            await extra.close()
        if server is not None:
            close = getattr(server, "close", None)
            if callable(close):
                maybe = close()
                if asyncio.iscoroutine(maybe):
                    await maybe
        _purge_registered_profiles()
