"""Live MCP qualification for ticketed UI draft bill create, update, and delete.

Requires opaque browser credential references. Never uses BILLY_API_TOKEN.
Pass proof is FastMCP call_tool on create_server. Independent read-back is a
second session. Cleanup is proved on a third fresh session.
Never pays, approves, pulls, or uploads a bill.
"""

from __future__ import annotations

import asyncio
import atexit
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
from billy_mcp.ui_writes import bills_form
from billy_mcp.ui_writes.page_flow import exact_name_in_text
from billy_mcp.vision_evidence import (
    is_outside_repository,
    owner_only_frame_dir,
    write_vision_record,
)

pytestmark = pytest.mark.live

_REPO_ROOT = Path(__file__).resolve().parents[2]
_DATA_ROOT = Path.home() / ".local" / "share" / "billy-mcp"
_VISION_RECORD = _REPO_ROOT / "tmp" / "vision-records" / "ui_bills_writes.json"
_BLOCKER_PATH = (
    _REPO_ROOT / ".fractal" / "main.billy_complete" / "tmp" / "live-bills-writes-blocker.txt"
)
_BILL_ID_RE = re.compile(r"/bills/([^/]+)(?:/edit)?$")


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
        "Live MCP bill writes blocked: BILLY_BROWSER_PRIMARY_REFERENCE and "
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
    path = Path(tempfile.mkdtemp(prefix="billy-live-bills-", dir=str(_DATA_ROOT)))
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


async def _open_named_list(page: Any, slug: str, path: str, name: str) -> None:
    await page.goto(f"https://mit.billy.dk/{slug}/{path}", wait_until="domcontentloaded")
    try:
        await page.wait_for_load_state("networkidle", timeout=20000)
    except Exception:
        pass
    search = page.locator("input[type='search'], input[placeholder*='øg' i]")
    if await search.count() >= 1:
        await search.first.fill(name)
        await asyncio.sleep(1.5)


async def _list_has_name(runtime: BrowserRuntime, slug: str, name: str) -> bool:
    context = await runtime.start()
    page = cast(Any, await context.new_page())
    try:
        await _open_named_list(page, slug, "bills", name)
        body = await page.locator("body").inner_text()
        return exact_name_in_text(body, name)
    finally:
        await page.close()


async def _suppliers_has_name(runtime: BrowserRuntime, slug: str, name: str) -> bool:
    context = await runtime.start()
    page = cast(Any, await context.new_page())
    try:
        await _open_named_list(page, slug, "suppliers", name)
        body = await page.locator("body").inner_text()
        return exact_name_in_text(body, name)
    finally:
        await page.close()


async def _bill_id_for_tag(runtime: BrowserRuntime, slug: str, name: str) -> str | None:
    context = await runtime.start()
    page = cast(Any, await context.new_page())
    try:
        await _open_named_list(page, slug, "bills", name)
        links = page.locator("a[href*='/bills/']")
        for index in range(await links.count()):
            href = await links.nth(index).get_attribute("href")
            if not isinstance(href, str) or not href:
                continue
            href_path = str(urlsplit(href).path)
            found = _BILL_ID_RE.search(href_path)
            if found is None:
                continue
            bill_id = found.group(1)
            if bill_id in {"new", "empty", "new-credit-note"}:
                continue
            return bill_id
        match = page.get_by_text(name, exact=True)
        if await match.count() < 1:
            return None
        await match.first.click()
        try:
            await page.wait_for_load_state("domcontentloaded", timeout=15000)
        except Exception:
            pass
        path = str(urlsplit(str(page.url)).path)
        found = _BILL_ID_RE.search(path)
        if found is None:
            return None
        bill_id = found.group(1)
        if bill_id in {"new", "empty"}:
            return None
        return bill_id
    finally:
        await page.close()


async def _capture(runtime: BrowserRuntime, slug: str, destination: Path, name: str) -> None:
    context = await runtime.start()
    page = cast(Any, await context.new_page())
    try:
        await _open_named_list(page, slug, "bills", name)
        await page.screenshot(path=str(destination), full_page=False)
        assert destination.is_file() and destination.stat().st_size > 0
    finally:
        await page.close()


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


async def _delete_tagged(
    server: FastMCP,
    runtime: BrowserRuntime,
    slug: str,
    name: str,
    bill_id: str | None,
) -> None:
    resolved = bill_id or await _bill_id_for_tag(runtime, slug, name)
    if not resolved:
        return
    preview = await _call(
        server,
        "ui_bills_delete_preview",
        {"id": resolved, "unique_tag": name, "organization_id": slug},
    )
    if preview.get("code"):
        return
    await _call(
        server,
        "ui_bills_delete_execute",
        {"confirmation_ticket": preview["confirmation_ticket"]},
    )


@pytest.mark.asyncio
async def test_ui_bills_create_update_delete_via_call_tool(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Create, update, and delete one tagged draft bill through create_server."""

    _require_live_credentials()
    tag = f"MCP-UI-B-{secrets.token_hex(4).upper()}"
    updated = f"{tag}-U"
    profile = _temp_profile()
    observer_profile = _temp_profile()
    cleanup_profile = _temp_profile()
    monkeypatch.setenv("BILLY_BROWSER_PROFILE", str(profile))
    monkeypatch.delenv("BILLY_ORGANIZATION_ID", raising=False)
    frame_dir = owner_only_frame_dir()
    server: FastMCP | None = None
    extra: BrowserRuntime | None = None
    slug = ""
    bill_id: str | None = None

    try:
        assert is_outside_repository(frame_dir, _REPO_ROOT)
        monkeypatch.setattr(bills_form, "CREATE_FORM_FRAME", frame_dir / "01b_create_form.png")
        server = create_server(_REPO_ROOT)
        slug = await _login(server)
        observer = BrowserRuntime(
            observer_profile,
            credential_references=AppConfig.from_environment().browser_credentials,
            credential_resolver=KeyringCredentialResolver(),
        )
        extra = observer
        await _ready_session(observer, slug)
        await _capture(observer, slug, frame_dir / "01_before.png", tag)
        assert await _list_has_name(observer, slug, tag) is False

        preview_create = await _call(
            server,
            "ui_bills_create_preview",
            {"unique_tag": tag, "organization_id": slug},
        )
        created_result = await _call(
            server,
            "ui_bills_create_execute",
            {"confirmation_ticket": preview_create["confirmation_ticket"]},
        )
        if created_result.get("code"):
            _record_blocker(f"create execute failed: {created_result}")
            pytest.fail(f"create execute failed: {created_result}")
        assert created_result["submitted"] is True
        await _capture(observer, slug, frame_dir / "02_after_create.png", tag)
        assert await _list_has_name(observer, slug, tag) is True
        bill_id = await _bill_id_for_tag(observer, slug, tag)
        if not bill_id:
            _record_blocker("independent bills list did not yield an edit id")
            pytest.fail("independent bills list did not yield an edit id")

        preview_update = await _call(
            server,
            "ui_bills_update_preview",
            {"id": bill_id, "unique_tag": updated, "organization_id": slug},
        )
        updated_result = await _call(
            server,
            "ui_bills_update_execute",
            {"confirmation_ticket": preview_update["confirmation_ticket"]},
        )
        if updated_result.get("code"):
            _record_blocker(f"update execute failed: {updated_result}")
            pytest.fail(f"update execute failed: {updated_result}")
        assert updated_result["submitted"] is True
        await _capture(observer, slug, frame_dir / "03_after_update.png", updated)
        assert await _list_has_name(observer, slug, updated) is True
        assert await _list_has_name(observer, slug, tag) is False

        preview_delete = await _call(
            server,
            "ui_bills_delete_preview",
            {"id": bill_id, "unique_tag": updated, "organization_id": slug},
        )
        deleted_result = await _call(
            server,
            "ui_bills_delete_execute",
            {"confirmation_ticket": preview_delete["confirmation_ticket"]},
        )
        if deleted_result.get("code"):
            _record_blocker(f"delete execute failed: {deleted_result}")
            pytest.fail(f"delete execute failed: {deleted_result}")
        assert deleted_result["submitted"] is True
        await _capture(observer, slug, frame_dir / "04_after_delete.png", updated)
        await observer.close()
        extra = None
        cleanup = BrowserRuntime(
            cleanup_profile,
            credential_references=AppConfig.from_environment().browser_credentials,
            credential_resolver=KeyringCredentialResolver(),
        )
        extra = cleanup
        await _ready_session(cleanup, slug)
        assert await _list_has_name(cleanup, slug, updated) is False
        assert await _list_has_name(cleanup, slug, tag) is False
        assert await _suppliers_has_name(cleanup, slug, updated) is False
        assert await _suppliers_has_name(cleanup, slug, tag) is False

        write_vision_record(
            _VISION_RECORD,
            workflow_ref="ui.parity.bills.create",
            assertion_refs=[
                "tests/live/test_ui_bills_writes.py::"
                "test_ui_bills_create_update_delete_via_call_tool",
                "create_server_call_tool_create_update_delete",
                "independent_readback_session",
                "third_session_cleanup",
            ],
            second_interface_ref="create_server_readback_plus_third_profile",
            reviewer_verdict="pending_review",
            purge_verified=False,
            author="live_test",
            run_id=frame_dir.name.removeprefix("run-"),
        )
    finally:
        if server is not None and slug:
            leftovers = ((tag, bill_id), (updated, bill_id))
            observer_for_cleanup = extra
            for leftover_name, leftover_id in leftovers:
                try:
                    await _delete_tagged(
                        server,
                        observer_for_cleanup
                        or BrowserRuntime(
                            cleanup_profile,
                            credential_references=AppConfig.from_environment().browser_credentials,
                            credential_resolver=KeyringCredentialResolver(),
                        ),
                        slug,
                        leftover_name,
                        leftover_id,
                    )
                except Exception:
                    _record_blocker(
                        f"Cleanup delete failed for leftover tagged bill {leftover_name}."
                    )
                try:
                    preview = await _call(
                        server,
                        "ui_clients_delete_preview",
                        {"name": leftover_name, "organization_id": slug},
                    )
                    if not preview.get("code"):
                        await _call(
                            server,
                            "ui_clients_delete_execute",
                            {"confirmation_ticket": preview["confirmation_ticket"]},
                        )
                except Exception:
                    _record_blocker(
                        f"Cleanup delete failed for leftover tagged vendor {leftover_name}."
                    )
        if extra is not None:
            try:
                await extra.close()
            except Exception:
                pass
        _purge_registered_profiles()
