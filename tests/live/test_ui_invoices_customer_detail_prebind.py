"""Live inspect: customer-detail Opret faktura prebind.

Creates one tagged customer through FastMCP, opens that detail, and records
allowlisted action tokens only. Never Godkend, Send, or emails an invoice.
"""

from __future__ import annotations

import asyncio
import atexit
import json
import os
import secrets
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
from billy_mcp.ui_writes.invoices_customer_detail_prebind import (
    CUSTOMER_DETAIL_PREBIND_DUMP,
    REQUIRED_CUSTOMER_DETAIL_PREBIND_KEYS,
    capture_customer_detail_prebind,
    customer_detail_prebind_dump_is_delivered,
    customer_detail_prebind_missing_keys,
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
    / "live-invoices-customer-detail-prebind-blocker.txt"
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
        "Live customer-detail prebind blocked: BILLY_BROWSER_PRIMARY_REFERENCE and "
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
    waited = await runtime.auth_login_wait()
    if isinstance(waited, AuthLoginWaitSuccess) and waited.status != "READY":
        started = await runtime.auth_login_start()
        if isinstance(started, ToolError):
            pytest.fail(f"session login start failed: {started.code}")
        waited = await runtime.auth_login_wait()
    if isinstance(waited, ToolError):
        pytest.fail(f"session login failed: {waited.code}")
    assert isinstance(waited, AuthLoginWaitSuccess)
    assert waited.status == "READY"
    assert waited.organization_id == slug


async def _clients_has_name(runtime: BrowserRuntime, slug: str, name: str) -> bool:
    context = await runtime.start()
    page = cast(Any, await context.new_page())
    try:
        await page.goto(f"{BILLY_ORIGIN}/{slug}/clients", wait_until="domcontentloaded")
        try:
            await page.wait_for_load_state("networkidle", timeout=20000)
        except (TimeoutError, RuntimeError):
            pass
        search = page.locator("input[type='search'], input[placeholder*='øg' i]")
        if await search.count() >= 1:
            await search.first.fill(name)
            await asyncio.sleep(1.5)
        exact = page.get_by_text(name, exact=True)
        return await exact.count() >= 1
    finally:
        await page.close()


def _assert_dump_clean(payload: dict[str, object], *, require_code: bool = False) -> None:
    assert customer_detail_prebind_missing_keys(payload) == []
    assert set(REQUIRED_CUSTOMER_DETAIL_PREBIND_KEYS) <= set(payload)
    encoded = json.dumps({"result": payload})
    assert "https://" not in encoded
    assert "function(" not in encoded
    assert "confirmation_ticket" not in encoded
    assert "MCP-UI-INV-" not in encoded
    if require_code and (
        payload.get("unique_normal_action") is not True or payload.get("proved_prebind") == "none"
    ):
        assert payload.get("code") == "UI_CHANGED"


@pytest.mark.asyncio
async def test_ui_invoices_customer_detail_prebind(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Inspect exact Opret faktura on one tagged customer detail. Do not save."""

    from billy_mcp.ui_writes.contacts import goto_clients, open_named_customer

    _require_live_credentials()
    assert not os.environ.get("BILLY_API_TOKEN"), "prebind dump must not use API token"
    if customer_detail_prebind_dump_is_delivered():
        written = json.loads(CUSTOMER_DETAIL_PREBIND_DUMP.read_text(encoding="utf-8"))
        _assert_dump_clean(written)
        text = CUSTOMER_DETAIL_PREBIND_DUMP.read_text(encoding="utf-8")
        assert "https://" not in text
        assert "MCP-UI-INV-" not in text
        return

    tag = f"MCP-UI-INV-{secrets.token_hex(4).upper()}"
    profile = _temp_profile()
    observer_profile = _temp_profile()
    cleanup_profile = _temp_profile()
    monkeypatch.setenv("BILLY_BROWSER_PROFILE", str(profile))
    monkeypatch.delenv("BILLY_ORGANIZATION_ID", raising=False)
    extra: BrowserRuntime | None = None
    page: Any = None
    server: FastMCP | None = None
    slug = ""

    try:
        server = create_server(_REPO_ROOT)
        slug = await _login(server)
        observer = BrowserRuntime(
            observer_profile,
            credential_references=AppConfig.from_environment().browser_credentials,
            credential_resolver=KeyringCredentialResolver(),
        )
        extra = observer
        await _ready_session(observer, slug)
        assert await _clients_has_name(observer, slug, tag) is False
        preview_create = await _call(
            server, "ui_clients_create_preview", {"name": tag, "organization_id": slug}
        )
        created = await _call(
            server,
            "ui_clients_create_execute",
            {"confirmation_ticket": preview_create["confirmation_ticket"]},
        )
        if created.get("code"):
            _record_blocker(f"create execute failed: {created}")
            pytest.fail(f"create execute failed: {created}")
        assert created["submitted"] is True
        seen = False
        for _ in range(12):
            if await _clients_has_name(observer, slug, tag):
                seen = True
                break
            await asyncio.sleep(1)
        if not seen:
            _record_blocker("fresh session did not see the tagged customer")
            pytest.fail("fresh session did not see the tagged customer")
        context = await observer.start()
        page = cast(Any, await context.new_page())
        await goto_clients(page, slug)
        opened = await open_named_customer(page, tag)
        if not opened:
            _record_blocker("named customer detail did not open")
            pytest.fail("named customer detail did not open")
        result = await capture_customer_detail_prebind(page, tag=tag)
        _assert_dump_clean(result, require_code=True)
        assert CUSTOMER_DETAIL_PREBIND_DUMP.is_file()
        written = json.loads(CUSTOMER_DETAIL_PREBIND_DUMP.read_text(encoding="utf-8"))
        _assert_dump_clean(written)
        if result.get("proved_prebind") == "none":
            preview_delete = await _call(
                server, "ui_clients_delete_preview", {"name": tag, "organization_id": slug}
            )
            deleted = await _call(
                server,
                "ui_clients_delete_execute",
                {"confirmation_ticket": preview_delete["confirmation_ticket"]},
            )
            if deleted.get("code"):
                _record_blocker(f"delete execute failed: {deleted}")
                pytest.fail(f"delete execute failed: {deleted}")
            await observer.close()
            extra = None
            cleanup = BrowserRuntime(
                cleanup_profile,
                credential_references=AppConfig.from_environment().browser_credentials,
                credential_resolver=KeyringCredentialResolver(),
            )
            extra = cleanup
            await _ready_session(cleanup, slug)
            assert await _clients_has_name(cleanup, slug, tag) is False
    finally:
        if page is not None:
            await page.close()
        if server is not None and slug:
            try:
                preview = await _call(
                    server,
                    "ui_clients_delete_preview",
                    {"name": tag, "organization_id": slug},
                )
                await _call(
                    server,
                    "ui_clients_delete_execute",
                    {"confirmation_ticket": preview["confirmation_ticket"]},
                )
            except Exception:
                _record_blocker(f"Cleanup delete failed for leftover tagged contact {tag}.")
        if extra is not None:
            await extra.close()
        _purge_registered_profiles()
