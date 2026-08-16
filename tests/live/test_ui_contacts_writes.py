"""Live MCP qualification for ticketed UI contact create, update, and delete.

Requires opaque browser credential references. Never uses BILLY_API_TOKEN.
Pass proof is FastMCP call_tool on create_server. Independent read-back is the
-readback session. Cleanup is proved on a third fresh session.
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
from billy_mcp.vision_evidence import (
    is_outside_repository,
    owner_only_frame_dir,
    write_vision_record,
)

pytestmark = pytest.mark.live

_REPO_ROOT = Path(__file__).resolve().parents[2]
_DATA_ROOT = Path.home() / ".local" / "share" / "billy-mcp"
_VISION_RECORD = _REPO_ROOT / "tmp" / "vision-records" / "ui_contacts_writes.json"
_BLOCKER_PATH = (
    _REPO_ROOT / ".fractal" / "main.billy_complete" / "tmp" / "live-contacts-writes-blocker.txt"
)
_ISOLATE_DUMP = (
    _REPO_ROOT / ".fractal" / "main.billy_complete" / "tmp" / "inspect-live-persist-isolate.json"
)


def _credentials_configured() -> bool:
    return bool(
        os.environ.get("BILLY_BROWSER_PRIMARY_REFERENCE", "").strip()
        and os.environ.get("BILLY_BROWSER_SECONDARY_REFERENCE", "").strip()
    )


def _record_blocker(reason: str) -> None:
    _BLOCKER_PATH.parent.mkdir(parents=True, exist_ok=True)
    _BLOCKER_PATH.write_text(reason.strip() + "\n", encoding="utf-8")


def _write_isolate_dump(payload: object) -> None:
    _ISOLATE_DUMP.parent.mkdir(parents=True, exist_ok=True)
    text = json.dumps(payload, default=str, indent=2)
    if "token" in text.lower() or "password" in text.lower():
        text = json.dumps({"redacted": True}, indent=2)
    _ISOLATE_DUMP.write_text(text[:20000] + "\n", encoding="utf-8")


def _require_live_credentials() -> None:
    if _credentials_configured():
        return
    reason = (
        "Live MCP contact writes blocked: BILLY_BROWSER_PRIMARY_REFERENCE and "
        "BILLY_BROWSER_SECONDARY_REFERENCE are not both set."
    )
    _record_blocker(reason)
    pytest.skip(reason)


_REGISTERED_PROFILES: list[Path] = []


def _purge_registered_profiles() -> None:
    for path in _REGISTERED_PROFILES:
        shutil.rmtree(path, ignore_errors=True)


atexit.register(_purge_registered_profiles)


def _temp_profile() -> Path:
    _DATA_ROOT.mkdir(parents=True, exist_ok=True)
    path = Path(tempfile.mkdtemp(prefix="billy-live-contacts-", dir=str(_DATA_ROOT)))
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
        _record_blocker(f"auth_login_wait not READY: {waited}")
        pytest.fail(f"auth_login_wait not READY: {waited}")
    slug = waited.get("organization_id")
    if not isinstance(slug, str) or not slug.strip():
        _record_blocker("auth_login_wait READY omitted organization_id")
        pytest.fail("READY omitted organization_id")
    return slug


async def _list_has_name(runtime: BrowserRuntime, slug: str, name: str) -> bool:
    context = await runtime.start()
    page = cast(Any, await context.new_page())
    try:
        await page.goto(f"https://mit.billy.dk/{slug}/clients", wait_until="domcontentloaded")
        try:
            await page.wait_for_load_state("networkidle", timeout=20000)
        except Exception:
            pass
        search = page.locator("input[type='search'], input[placeholder*='øg' i]")
        if await search.count() >= 1:
            await search.first.fill(name)
            await asyncio.sleep(1.5)
        exact = page.get_by_text(name, exact=True)
        return await exact.count() >= 1
    finally:
        await page.close()


async def _capture(runtime: BrowserRuntime, slug: str, destination: Path, name: str) -> None:
    context = await runtime.start()
    page = cast(Any, await context.new_page())
    try:
        await page.goto(f"https://mit.billy.dk/{slug}/clients", wait_until="domcontentloaded")
        try:
            await page.wait_for_load_state("networkidle", timeout=20000)
        except Exception:
            pass
        search = page.locator("input[type='search'], input[placeholder*='øg' i]")
        if await search.count() >= 1:
            await search.first.fill(name)
            await asyncio.sleep(1)
        await page.screenshot(path=str(destination), full_page=False)
        assert destination.is_file() and destination.stat().st_size > 0
    finally:
        await page.close()


@pytest.mark.asyncio
async def test_ui_contacts_create_update_delete_via_call_tool(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Create, update, and delete one tagged customer through create_server call_tool."""

    _require_live_credentials()
    tag = f"MCP-UI-C-{secrets.token_hex(4).upper()}"
    updated = f"{tag}-U"
    profile = _temp_profile()
    third_profile = _temp_profile()
    cleanup_profile = _temp_profile()
    monkeypatch.setenv("BILLY_BROWSER_PROFILE", str(profile))
    monkeypatch.delenv("BILLY_ORGANIZATION_ID", raising=False)
    frame_dir = owner_only_frame_dir()
    server: FastMCP | None = None
    third: BrowserRuntime | None = None
    slug = ""

    try:
        assert is_outside_repository(frame_dir, _REPO_ROOT)
        server = create_server(_REPO_ROOT)
        slug = await _login(server)
        observer = BrowserRuntime(
            third_profile,
            credential_references=AppConfig.from_environment().browser_credentials,
            credential_resolver=KeyringCredentialResolver(),
        )
        third = observer
        observer_wait = await observer.auth_login_wait()
        if isinstance(observer_wait, AuthLoginWaitSuccess) and observer_wait.status != "READY":
            started = await observer.auth_login_start()
            if isinstance(started, ToolError):
                pytest.fail(f"observer login start failed: {started.code}")
            observer_wait = await observer.auth_login_wait()
        if isinstance(observer_wait, ToolError):
            pytest.fail(f"observer login failed: {observer_wait.code}")
        assert isinstance(observer_wait, AuthLoginWaitSuccess)
        assert observer_wait.status == "READY"
        assert observer_wait.organization_id == slug
        await _capture(observer, slug, frame_dir / "01_before.png", tag)
        assert await _list_has_name(observer, slug, tag) is False

        preview_create = await _call(
            server, "ui_clients_create_preview", {"name": tag, "organization_id": slug}
        )
        created_result = await _call(
            server,
            "ui_clients_create_execute",
            {"confirmation_ticket": preview_create["confirmation_ticket"]},
        )
        if created_result.get("code"):
            _record_blocker(f"create execute failed: {created_result}")
            pytest.fail(f"create execute failed: {created_result}")
        assert created_result["submitted"] is True
        await _capture(observer, slug, frame_dir / "02_after_create.png", tag)
        assert await _list_has_name(observer, slug, tag) is True

        preview_update = await _call(
            server,
            "ui_clients_update_preview",
            {"name": tag, "new_name": updated, "organization_id": slug},
        )
        updated_result = await _call(
            server,
            "ui_clients_update_execute",
            {"confirmation_ticket": preview_update["confirmation_ticket"]},
        )
        if updated_result.get("code"):
            _write_isolate_dump(updated_result.get("details") or updated_result)
            _record_blocker(f"update execute failed: {updated_result}")
            pytest.fail(f"update execute failed: {updated_result}")
        _write_isolate_dump({"submitted": True, "code": None})
        assert updated_result["submitted"] is True
        await _capture(observer, slug, frame_dir / "03_after_update.png", updated)
        assert await _list_has_name(observer, slug, updated) is True
        assert await _list_has_name(observer, slug, tag) is False

        preview_delete = await _call(
            server, "ui_clients_delete_preview", {"name": updated, "organization_id": slug}
        )
        deleted_result = await _call(
            server,
            "ui_clients_delete_execute",
            {"confirmation_ticket": preview_delete["confirmation_ticket"]},
        )
        if deleted_result.get("code"):
            _record_blocker(f"delete execute failed: {deleted_result}")
            pytest.fail(f"delete execute failed: {deleted_result}")
        assert deleted_result["submitted"] is True
        await _capture(observer, slug, frame_dir / "04_after_delete.png", updated)
        await observer.close()
        third = None
        cleanup = BrowserRuntime(
            cleanup_profile,
            credential_references=AppConfig.from_environment().browser_credentials,
            credential_resolver=KeyringCredentialResolver(),
        )
        third = cleanup
        cleanup_wait = await cleanup.auth_login_wait()
        if isinstance(cleanup_wait, AuthLoginWaitSuccess) and cleanup_wait.status != "READY":
            started = await cleanup.auth_login_start()
            if isinstance(started, ToolError):
                pytest.fail(f"cleanup-session login start failed: {started.code}")
            cleanup_wait = await cleanup.auth_login_wait()
        if isinstance(cleanup_wait, ToolError):
            pytest.fail(f"cleanup-session login failed: {cleanup_wait.code}")
        assert isinstance(cleanup_wait, AuthLoginWaitSuccess)
        assert cleanup_wait.status == "READY"
        assert cleanup_wait.organization_id == slug
        assert await _list_has_name(cleanup, slug, updated) is False
        assert await _list_has_name(cleanup, slug, tag) is False

        write_vision_record(
            _VISION_RECORD,
            workflow_ref="ui.parity.contacts.create",
            assertion_refs=[
                "tests/live/test_ui_contacts_writes.py::"
                "test_ui_contacts_create_update_delete_via_call_tool",
                "create_server_call_tool_create_update_delete",
                "independent_readback_session",
                "third_session_cleanup",
            ],
            second_interface_ref="create_server_readback_plus_third_profile",
            reviewer_verdict="pending_review",
            purge_verified=False,
            author="live_test",
        )
    finally:
        leftovers = {tag, updated}
        if server is not None and slug:
            for leftover in leftovers:
                try:
                    preview = await _call(
                        server,
                        "ui_clients_delete_preview",
                        {"name": leftover, "organization_id": slug},
                    )
                    await _call(
                        server,
                        "ui_clients_delete_execute",
                        {"confirmation_ticket": preview["confirmation_ticket"]},
                    )
                except Exception:
                    _record_blocker(f"Cleanup delete failed for leftover tagged name {leftover}.")
        if third is not None:
            try:
                await third.close()
            except Exception:
                pass
        _purge_registered_profiles()
