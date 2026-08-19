"""Live inspect: scoped Gem som kladde capture on invoices/new.

Creates one tagged customer through FastMCP, opens create, clicks Gem som
kladde once, and records contact-owned rows only. Never Godkend, Send, or email.
"""

from __future__ import annotations

import asyncio
import atexit
import json
import os
import re
import secrets
import shutil
import tempfile
from pathlib import Path
from typing import Any, cast
from urllib.parse import urlsplit

import pytest
from fastmcp import FastMCP

from billy_mcp.browser import BrowserRuntime
from billy_mcp.config import AppConfig
from billy_mcp.credentials import KeyringCredentialResolver
from billy_mcp.models import AuthLoginWaitSuccess, StableErrorCode, ToolError
from billy_mcp.server import create_server
from billy_mcp.ui_writes.invoices_draft_save_scoped import (
    DRAFT_SAVE_SCOPED_DUMP,
    REQUIRED_DRAFT_SAVE_SCOPED_KEYS,
    capture_draft_save_scoped,
    draft_save_scoped_dump_is_delivered,
    draft_save_scoped_missing_keys,
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
    / "live-invoices-draft-save-scoped-blocker.txt"
)
_REGISTERED_PROFILES: list[Path] = []
_INVOICE_ID = re.compile(r"^/[^/]+/invoices/([^/]+)/?$")


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
        "Live scoped draft-save inspect blocked: BILLY_BROWSER_PRIMARY_REFERENCE and "
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
        if isinstance(started, ToolError) and started.code != StableErrorCode.UI_CHANGED:
            pytest.fail(f"session login start failed: {started.code}")
        waited = await runtime.auth_login_wait()
    if isinstance(waited, ToolError):
        pytest.fail(f"session login failed: {waited.code}")
    assert isinstance(waited, AuthLoginWaitSuccess)
    assert waited.status == "READY"
    if waited.organization_id != slug:
        pytest.fail("observer organization did not match the FastMCP session")


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


def _invoice_id_from(url: str) -> str | None:
    path = urlsplit(url).path
    match = _INVOICE_ID.match(path)
    if match is None:
        return None
    token = match.group(1)
    if token == "new":
        return None
    return token


def _assert_dump_clean(payload: dict[str, object], *, require_code: bool = False) -> None:
    assert draft_save_scoped_missing_keys(payload) == []
    assert set(REQUIRED_DRAFT_SAVE_SCOPED_KEYS) <= set(payload)
    assert "opret_ny_count" not in payload
    encoded = json.dumps({"result": payload})
    assert "https://" not in encoded
    assert "function(" not in encoded
    assert "confirmation_ticket" not in encoded
    assert "MCP-UI-INV-" not in encoded
    if require_code and payload.get("proved_bind") == "none":
        assert payload.get("code") == "UI_CHANGED"


@pytest.mark.asyncio
async def test_ui_invoices_draft_save_scoped(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Click Gem som kladde once and record contact-owned rows. Do not Godkend."""

    _require_live_credentials()
    assert not os.environ.get("BILLY_API_TOKEN"), "scoped dump must not use API token"
    if draft_save_scoped_dump_is_delivered():
        written = json.loads(DRAFT_SAVE_SCOPED_DUMP.read_text(encoding="utf-8"))
        _assert_dump_clean(written)
        text = DRAFT_SAVE_SCOPED_DUMP.read_text(encoding="utf-8")
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
    leftover_invoice: str | None = None

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
        opened = await _call(server, "ui_invoices_create_open")
        if opened.get("code"):
            _record_blocker(f"ui_invoices_create_open failed: {opened}")
            pytest.fail(f"ui_invoices_create_open failed: {opened}")
        assert opened.get("path_class") == "/:org_slug/invoices/new"
        context = await observer.start()
        page = cast(Any, await context.new_page())
        await page.goto(f"{BILLY_ORIGIN}/{slug}/invoices/new", wait_until="domcontentloaded")
        try:
            await page.wait_for_load_state("networkidle", timeout=20000)
        except (TimeoutError, RuntimeError):
            pass
        result = await capture_draft_save_scoped(page, tag=tag)
        leftover_invoice = _invoice_id_from(page.url)
        _assert_dump_clean(result, require_code=True)
        assert DRAFT_SAVE_SCOPED_DUMP.is_file()
        written = json.loads(DRAFT_SAVE_SCOPED_DUMP.read_text(encoding="utf-8"))
        _assert_dump_clean(written)
        if result.get("gem_clicked") is True and result.get("invoice_persisted") is True:
            assert leftover_invoice is not None
        if leftover_invoice is not None:
            preview_invoice = await _call(
                server,
                "ui_invoices_delete_preview",
                {
                    "contact_name": tag,
                    "id": leftover_invoice,
                    "action": "draft_delete",
                    "save_cta": "Slet",
                    "organization_id": slug,
                },
            )
            deleted_invoice = await _call(
                server,
                "ui_invoices_delete_execute",
                {"confirmation_ticket": preview_invoice["confirmation_ticket"]},
            )
            if deleted_invoice.get("code"):
                _record_blocker(f"invoice delete failed: {deleted_invoice}")
                pytest.fail(f"invoice delete failed: {deleted_invoice}")
            leftover_invoice = None
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
        assert await _clients_has_name(observer, slug, tag) is False
        await observer.close()
        extra = None
        cleanup = BrowserRuntime(
            cleanup_profile,
            credential_references=AppConfig.from_environment().browser_credentials,
            credential_resolver=KeyringCredentialResolver(),
        )
        extra = cleanup
        try:
            await _ready_session(cleanup, slug)
        except Exception:
            _record_blocker("cleanup session login UI_CHANGED after dump and delete")
            extra = None
            await cleanup.close()
        else:
            assert await _clients_has_name(cleanup, slug, tag) is False
    finally:
        if page is not None:
            await page.close()
        if server is not None and slug:
            if leftover_invoice is not None:
                try:
                    preview_invoice = await _call(
                        server,
                        "ui_invoices_delete_preview",
                        {
                            "id": leftover_invoice,
                            "action": "draft_delete",
                            "save_cta": "Slet",
                            "organization_id": slug,
                        },
                    )
                    await _call(
                        server,
                        "ui_invoices_delete_execute",
                        {"confirmation_ticket": preview_invoice["confirmation_ticket"]},
                    )
                except Exception:
                    _record_blocker("Cleanup delete failed for leftover draft invoice.")
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
                _record_blocker("Cleanup delete failed for leftover tagged contact.")
        if extra is not None:
            await extra.close()
        if server is not None:
            close = getattr(server, "close", None)
            if callable(close):
                maybe = close()
                if asyncio.iscoroutine(maybe):
                    await maybe
        _purge_registered_profiles()
