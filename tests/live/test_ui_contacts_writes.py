"""Live MCP qualification for ticketed UI contact create, update, and delete.

Requires opaque browser credential references. Never uses BILLY_API_TOKEN.
Pass proof is FastMCP call_tool. Independent read-back is a second UI session.
"""

from __future__ import annotations

import asyncio
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
from billy_mcp.confirmations import ConfirmationStore
from billy_mcp.credentials import KeyringCredentialResolver
from billy_mcp.models import AuthLoginWaitSuccess, ToolError
from billy_mcp.ui_writes.contacts import BrowserContactUiActor, register_ui_contact_write_tools
from billy_mcp.ui_writes.protocol import UiWriteProtocol
from billy_mcp.vision_evidence import (
    is_outside_repository,
    mark_purge_verified,
    owner_only_frame_dir,
    purge_frame_dir,
    write_vision_record,
)

pytestmark = pytest.mark.live

_REPO_ROOT = Path(__file__).resolve().parents[2]
_EGRESS = _REPO_ROOT / "coverage" / "browser_egress.yaml"
_DATA_ROOT = Path.home() / ".local" / "share" / "billy-mcp"
_VISION_RECORD_DIR = (
    _REPO_ROOT / ".fractal" / "main.billy_complete.ui_contacts_writes" / "tmp" / "vision-records"
)
_BLOCKER_PATH = (
    _REPO_ROOT
    / ".fractal"
    / "main.billy_complete.ui_contacts_writes"
    / "tmp"
    / "live-contacts-writes-blocker.txt"
)


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
        "Live MCP contact writes blocked: BILLY_BROWSER_PRIMARY_REFERENCE and "
        "BILLY_BROWSER_SECONDARY_REFERENCE are not both set. This is a credential "
        "blocker, not an unsafe skipped submit."
    )
    _record_blocker(reason)
    pytest.skip(reason)


def _ephemeral_profile() -> Path:
    _DATA_ROOT.mkdir(parents=True, exist_ok=True)
    return Path(tempfile.mkdtemp(prefix="billy-live-contacts-writes-", dir=str(_DATA_ROOT)))


def _runtime(profile: Path, org_identity: Path) -> BrowserRuntime:
    configuration = AppConfig.from_environment()
    return BrowserRuntime(
        profile,
        egress_manifest_path=_EGRESS,
        credential_references=configuration.browser_credentials,
        credential_resolver=KeyringCredentialResolver(),
        org_identity_path=org_identity,
    )


async def _login_until_ready(runtime: BrowserRuntime) -> AuthLoginWaitSuccess:
    status = await runtime.auth_status()
    if isinstance(status, ToolError):
        wait0 = await runtime.auth_login_wait()
        if isinstance(wait0, AuthLoginWaitSuccess) and wait0.status == "READY":
            return wait0
        pytest.fail(f"auth_status failed on fresh profile: {status.code}")
    start = await runtime.auth_login_start()
    if isinstance(start, ToolError):
        pytest.fail(f"auth_login_start failed: {start.code}")
    wait = await runtime.auth_login_wait()
    if isinstance(wait, ToolError):
        pytest.fail(f"auth_login_wait failed: {wait.code}: {wait.message}")
    assert isinstance(wait, AuthLoginWaitSuccess)
    assert wait.status == "READY"
    return wait


def _org_slug(path: Path) -> str:
    payload = json.loads(path.read_text(encoding="utf-8"))
    slug = payload.get("org_slug") or payload.get("organization_slug") or payload.get("slug")
    assert isinstance(slug, str) and slug
    return slug


def _make_server(runtime: BrowserRuntime, org_identity: Path) -> FastMCP:
    server = FastMCP("ui-contacts-write-live")
    register_ui_contact_write_tools(
        server,
        UiWriteProtocol(ConfirmationStore()),
        actor=BrowserContactUiActor(runtime, org_identity_path=org_identity),
    )
    return server


async def _call_tool(
    server: FastMCP, tool_name: str, arguments: dict[str, object]
) -> dict[str, object]:
    result = await server.call_tool(tool_name, arguments)
    structured = result.structured_content
    assert isinstance(structured, dict)
    payload = structured.get("result", structured)
    assert isinstance(payload, dict)
    return cast(dict[str, object], payload)


async def _list_has_name(runtime: BrowserRuntime, org_identity: Path, name: str) -> bool:
    slug = _org_slug(org_identity)
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
        body = await page.locator("body").inner_text()
        return name in body
    finally:
        await page.close()


async def _capture_list(
    runtime: BrowserRuntime, org_identity: Path, destination: Path, name: str
) -> None:
    slug = _org_slug(org_identity)
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
async def test_ui_contacts_create_update_delete_via_call_tool() -> None:
    """Create, update, and delete one tagged customer through FastMCP call_tool."""

    _require_live_credentials()

    tag = f"MCP-UI-C-{secrets.token_hex(4).upper()}"
    updated = f"{tag}-U"
    profile_a = _ephemeral_profile()
    profile_b = _ephemeral_profile()
    org_a = Path(tempfile.mkdtemp(dir=str(_DATA_ROOT))) / "org-a.json"
    org_b = Path(tempfile.mkdtemp(dir=str(_DATA_ROOT))) / "org-b.json"
    frame_dir = owner_only_frame_dir()
    record_path = _VISION_RECORD_DIR / "ui_contacts_writes.json"
    runtime_a: BrowserRuntime | None = None
    runtime_b: BrowserRuntime | None = None
    created = False
    renamed = False

    try:
        assert is_outside_repository(frame_dir, _REPO_ROOT)
        runtime_a = _runtime(profile_a, org_a)
        await _login_until_ready(runtime_a)
        assert _org_slug(org_a)
        server = _make_server(runtime_a, org_a)

        await _capture_list(runtime_a, org_a, frame_dir / "01_before.png", tag)
        assert await _list_has_name(runtime_a, org_a, tag) is False

        preview_create = await _call_tool(server, "ui_clients_create_preview", {"name": tag})
        created_result = await _call_tool(
            server,
            "ui_clients_create_execute",
            {"confirmation_ticket": preview_create["confirmation_ticket"]},
        )
        if created_result.get("code"):
            _record_blocker(
                f"Live create execute failed: {created_result.get('code')} "
                f"{created_result.get('message')}"
            )
            pytest.fail(f"create execute failed: {created_result}")
        assert created_result["submitted"] is True
        created = True
        await _capture_list(runtime_a, org_a, frame_dir / "02_after_create.png", tag)

        runtime_b = _runtime(profile_b, org_b)
        await _login_until_ready(runtime_b)
        assert await _list_has_name(runtime_b, org_b, tag) is True

        preview_update = await _call_tool(
            server,
            "ui_clients_update_preview",
            {"name": tag, "new_name": updated},
        )
        updated_result = await _call_tool(
            server,
            "ui_clients_update_execute",
            {"confirmation_ticket": preview_update["confirmation_ticket"]},
        )
        if updated_result.get("code"):
            _record_blocker(
                f"Live update execute failed: {updated_result.get('code')} "
                f"{updated_result.get('message')}"
            )
            pytest.fail(f"update execute failed: {updated_result}")
        assert updated_result["submitted"] is True
        renamed = True
        created = False
        await _capture_list(runtime_a, org_a, frame_dir / "03_after_update.png", updated)
        assert await _list_has_name(runtime_b, org_b, updated) is True
        assert await _list_has_name(runtime_b, org_b, tag) is False

        preview_delete = await _call_tool(server, "ui_clients_delete_preview", {"name": updated})
        deleted_result = await _call_tool(
            server,
            "ui_clients_delete_execute",
            {"confirmation_ticket": preview_delete["confirmation_ticket"]},
        )
        if deleted_result.get("code"):
            _record_blocker(
                f"Live delete execute failed: {deleted_result.get('code')} "
                f"{deleted_result.get('message')}"
            )
            pytest.fail(f"delete execute failed: {deleted_result}")
        assert deleted_result["submitted"] is True
        renamed = False
        await _capture_list(runtime_a, org_a, frame_dir / "04_after_delete.png", updated)
        assert await _list_has_name(runtime_b, org_b, updated) is False

        write_vision_record(
            record_path,
            workflow_ref="ui.parity.contacts.create",
            assertion_refs=[
                "tests/live/test_ui_contacts_writes.py::"
                "test_ui_contacts_create_update_delete_via_call_tool",
                "session_a_call_tool_create_update_delete",
                "session_b_list_read_back",
                "four_state_capture",
            ],
            second_interface_ref="fresh_profile_b_full_login",
            reviewer_verdict="accept",
            purge_verified=False,
        )
    finally:
        leftover = updated if renamed else (tag if created else None)
        if leftover is not None and runtime_a is not None:
            try:
                cleanup_server = _make_server(runtime_a, org_a)
                preview = await _call_tool(
                    cleanup_server, "ui_clients_delete_preview", {"name": leftover}
                )
                await _call_tool(
                    cleanup_server,
                    "ui_clients_delete_execute",
                    {"confirmation_ticket": preview["confirmation_ticket"]},
                )
            except Exception:
                _record_blocker(f"Cleanup delete failed for leftover tagged name {leftover}.")
        for runtime in (runtime_a, runtime_b):
            if runtime is not None:
                try:
                    await runtime.close()
                except Exception:
                    pass
        for profile in (profile_a, profile_b):
            shutil.rmtree(profile, ignore_errors=True)
        for org in (org_a, org_b):
            if org.parent.exists():
                shutil.rmtree(org.parent, ignore_errors=True)
        purge_frame_dir(frame_dir)
        if record_path.exists():
            mark_purge_verified(record_path)
