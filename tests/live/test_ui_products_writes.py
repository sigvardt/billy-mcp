"""Live MCP qualification for ticketed UI product create and delete.

Requires opaque browser credential references. Never uses BILLY_API_TOKEN.
Pass proof is FastMCP call_tool on create_server. Independent read-back is a
second session. Cleanup is proved on a third fresh session.
Never archives a product. Never API-deletes.
"""

from __future__ import annotations

import atexit
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
from billy_mcp.models import AuthLoginWaitSuccess, StableErrorCode
from billy_mcp.server import create_server
from billy_mcp.ui_writes.page_flow import exact_name_in_text
from billy_mcp.vision_evidence import (
    is_outside_repository,
    owner_only_frame_dir,
    write_vision_record,
)
from tests.live.product_leftover_sweep import OWNER_LEFTOVERS, visible_prd_tags

pytestmark = pytest.mark.live

_REPO_ROOT = Path(__file__).resolve().parents[2]
_DATA_ROOT = Path.home() / ".local" / "share" / "billy-mcp"
_VISION_RECORD = _REPO_ROOT / "tmp" / "vision-records" / "ui_products_writes.json"
_BLOCKER_PATH = (
    _REPO_ROOT / ".fractal" / "main.billy_complete" / "tmp" / "live-products-writes-blocker.txt"
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
        "Live MCP product writes blocked: BILLY_BROWSER_PRIMARY_REFERENCE and "
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
    path = Path(tempfile.mkdtemp(prefix="billy-live-products-", dir=str(_DATA_ROOT)))
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
        if started.__class__.__name__ == "ToolError":
            pytest.fail(f"session login start failed: {started}")
        waited = await runtime.auth_login_wait()
    if waited.__class__.__name__ == "ToolError":
        pytest.fail(f"session login failed: {waited}")
    assert isinstance(waited, AuthLoginWaitSuccess)
    assert waited.status == "READY"
    assert waited.organization_id == slug


async def _open_named_list(page: Any, slug: str, path: str) -> None:
    await page.goto(f"https://mit.billy.dk/{slug}/{path}", wait_until="domcontentloaded")
    try:
        await page.wait_for_load_state("networkidle", timeout=20000)
    except TimeoutError:
        pass


async def _list_has_name(runtime: BrowserRuntime, slug: str, name: str) -> bool:
    context = await runtime.start()
    page = cast(Any, await context.new_page())
    try:
        for path in ("products", "inventory"):
            await _open_named_list(page, slug, path)
            body = await page.locator("body").inner_text()
            if exact_name_in_text(body, name):
                return True
            search = page.locator("input[type='search'], input[placeholder*='øg' i]")
            if await search.count() >= 1:
                await search.first.fill(name)
                body = await page.locator("body").inner_text()
                if exact_name_in_text(body, name):
                    return True
        return False
    finally:
        await page.close()


async def _delete_tagged(server: FastMCP, slug: str, name: str) -> None:
    preview = await _call(
        server,
        "ui_products_delete_preview",
        {"unique_tag": name, "organization_id": slug},
    )
    if preview.get("code"):
        return
    await _call(
        server,
        "ui_products_delete_execute",
        {"confirmation_ticket": preview["confirmation_ticket"]},
    )


@pytest.mark.asyncio
async def test_ui_products_create_delete_via_call_tool(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Create and delete one tagged product through create_server."""

    _require_live_credentials()
    profile = _temp_profile()
    observer_profile = _temp_profile()
    cleanup_profile = _temp_profile()
    monkeypatch.setenv("BILLY_BROWSER_PROFILE", str(profile))
    monkeypatch.delenv("BILLY_ORGANIZATION_ID", raising=False)
    frame_dir = owner_only_frame_dir()
    server: FastMCP | None = None
    extra: BrowserRuntime | None = None
    slug = ""
    tag = ""

    try:
        assert is_outside_repository(frame_dir, _REPO_ROOT)
        server = create_server(_REPO_ROOT)
        slug = await _login(server)
        observer = BrowserRuntime(
            observer_profile,
            credential_references=AppConfig.from_environment().browser_credentials,
            credential_resolver=KeyringCredentialResolver(),
        )
        extra = observer
        await _ready_session(observer, slug)
        for leftover in OWNER_LEFTOVERS:
            if await _list_has_name(observer, slug, leftover):
                await _delete_tagged(server, slug, leftover)
        extras = await visible_prd_tags(observer, slug, _open_named_list)
        for leftover in reversed(extras):
            await _delete_tagged(server, slug, leftover)
        tag = f"MCP-UI-PRD-{secrets.token_hex(4).upper()}"
        assert await _list_has_name(observer, slug, tag) is False

        preview_create = await _call(
            server,
            "ui_products_create_preview",
            {"name": tag, "unitPrice": 1.0, "organization_id": slug},
        )
        created_result = await _call(
            server,
            "ui_products_create_execute",
            {"confirmation_ticket": preview_create["confirmation_ticket"]},
        )
        if created_result.get("code"):
            _record_blocker(f"create execute failed: {created_result}")
            pytest.fail(f"create execute failed: {created_result}")
        assert created_result["submitted"] is True
        assert await _list_has_name(observer, slug, tag) is True

        preview_delete = await _call(
            server,
            "ui_products_delete_preview",
            {"unique_tag": tag, "organization_id": slug},
        )
        deleted_result = await _call(
            server,
            "ui_products_delete_execute",
            {"confirmation_ticket": preview_delete["confirmation_ticket"]},
        )
        if deleted_result.get("code"):
            _record_blocker(f"delete execute failed: {deleted_result}")
            pytest.fail(f"delete execute failed: {deleted_result}")
        assert deleted_result["submitted"] is True
        await observer.close()
        extra = None
        cleanup = BrowserRuntime(
            cleanup_profile,
            credential_references=AppConfig.from_environment().browser_credentials,
            credential_resolver=KeyringCredentialResolver(),
        )
        extra = cleanup
        await _ready_session(cleanup, slug)
        assert await _list_has_name(cleanup, slug, tag) is False
        empty = await cleanup.start()
        empty_page = cast(Any, await empty.new_page())
        try:
            await _open_named_list(empty_page, slug, "products")
            body = await empty_page.locator("body").inner_text()
            assert "Ingen produkter" in body or exact_name_in_text(body, tag) is False
        finally:
            await empty_page.close()

        write_vision_record(
            _VISION_RECORD,
            workflow_ref="ui.parity.products.create",
            assertion_refs=[
                "tests/live/test_ui_products_writes.py::"
                "test_ui_products_create_delete_via_call_tool",
                "create_server_call_tool_create_delete",
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
        if server is not None and slug and tag:
            try:
                await _delete_tagged(server, slug, tag)
            except (OSError, RuntimeError, AssertionError):
                _record_blocker(f"Cleanup delete failed for leftover tagged product {tag}.")
        if extra is not None:
            await extra.close()
