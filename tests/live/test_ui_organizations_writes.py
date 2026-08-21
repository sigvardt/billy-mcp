"""Live FastMCP company-phone set plus exact empty restore.

Never uses BILLY_API_TOKEN. Pass proof is create_server call_tool.
Read-back is input[name=phone] on a fresh session. Restore is phone="".
"""

from __future__ import annotations

import asyncio
import os
import secrets
import shutil
from pathlib import Path
from typing import Any, cast

import pytest
from fastmcp import FastMCP

from billy_mcp.browser import BrowserRuntime
from billy_mcp.config import AppConfig
from billy_mcp.credentials import KeyringCredentialResolver
from billy_mcp.models import AuthLoginWaitSuccess, StableErrorCode, ToolError
from billy_mcp.server import create_server
from billy_mcp.ui_writes.organizations_phone import PHONE_INPUT_NAME
from billy_mcp.ui_writes.organizations_submit import fill_phone_input
from billy_mcp.ui_writes.page_flow import BILLY_ORIGIN
from billy_mcp.vision_evidence import (
    is_outside_repository,
    owner_only_frame_dir,
    write_live_pending_unless_accepted,
)

pytestmark = pytest.mark.live

_REPO_ROOT = Path(__file__).resolve().parents[2]
_EGRESS = _REPO_ROOT / "coverage" / "browser_egress.yaml"
_VISION_RECORD = _REPO_ROOT / "tmp" / "vision-records" / "ui_organizations_writes.json"
_BLOCKER_PATH = (
    _REPO_ROOT
    / ".fractal"
    / "main.billy_complete"
    / "tmp"
    / "live-organizations-writes-blocker.txt"
)
_PHONE_LOCATOR = f"input[name='{PHONE_INPUT_NAME}']"


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
        "Live organization phone write blocked: BILLY_BROWSER_PRIMARY_REFERENCE and "
        "BILLY_BROWSER_SECONDARY_REFERENCE are not both set."
    )
    _record_blocker(reason)
    pytest.skip(reason)


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


async def _ready_runtime(profile: Path) -> tuple[BrowserRuntime, str]:
    configuration = AppConfig.from_environment()
    runtime = BrowserRuntime(
        profile,
        egress_manifest_path=_EGRESS,
        credential_references=configuration.browser_credentials,
        credential_resolver=KeyringCredentialResolver(),
    )
    wait = await runtime.auth_login_wait()
    if isinstance(wait, AuthLoginWaitSuccess) and wait.status != "READY":
        started = await runtime.auth_login_start()
        if isinstance(started, ToolError) and started.code != StableErrorCode.UI_CHANGED:
            pytest.fail(f"observer login start failed: {started.code}")
        wait = await runtime.auth_login_wait()
    if isinstance(wait, ToolError) and wait.code == StableErrorCode.UI_CHANGED:
        wait = await runtime.auth_login_wait()
    if isinstance(wait, ToolError):
        pytest.fail(f"observer login failed: {wait.code}")
    assert isinstance(wait, AuthLoginWaitSuccess)
    assert wait.status == "READY"
    assert isinstance(wait.organization_id, str) and wait.organization_id
    return runtime, wait.organization_id


async def _phone_input_value(runtime: BrowserRuntime, slug: str) -> str:
    context = await runtime.start()
    page = cast(Any, await context.new_page())
    try:
        await page.goto(f"{BILLY_ORIGIN}/{slug}/settings", wait_until="domcontentloaded")
        try:
            await page.wait_for_load_state("networkidle", timeout=20000)
        except (TimeoutError, RuntimeError):
            pass
        await asyncio.sleep(0.5)
        field = page.locator(_PHONE_LOCATOR)
        try:
            await field.first.wait_for(state="visible", timeout=15000)
        except (TimeoutError, RuntimeError):
            pytest.fail("Billy company phone input is not visible.")
        if await field.count() < 1:
            pytest.fail("Billy company phone input is not visible.")
        return str(await field.first.input_value())
    finally:
        await page.close()


async def _capture_settings(
    runtime: BrowserRuntime,
    slug: str,
    destination: Path,
    *,
    fill: str | None = None,
) -> None:
    """Write one owner-only settings frame. Never store the phone value."""

    context = await runtime.start()
    page = cast(Any, await context.new_page())
    try:
        await page.goto(f"{BILLY_ORIGIN}/{slug}/settings", wait_until="domcontentloaded")
        try:
            await page.wait_for_load_state("networkidle", timeout=20000)
        except (TimeoutError, RuntimeError):
            pass
        await asyncio.sleep(0.5)
        field = page.locator(_PHONE_LOCATOR)
        try:
            await field.first.wait_for(state="visible", timeout=15000)
        except (TimeoutError, RuntimeError):
            pytest.fail("Billy company phone input is not visible.")
        if fill is not None:
            failed = await fill_phone_input(page, fill)
            if failed is not None:
                pytest.fail(f"before-submit fill failed: {failed.code}")
        await page.screenshot(path=str(destination), full_page=False)
        assert destination.is_file() and destination.stat().st_size > 0
    finally:
        await page.close()


@pytest.mark.asyncio
async def test_ui_organizations_set_then_clear_via_call_tool(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Set a tagged phone, then restore exact empty, through FastMCP."""

    _require_live_credentials()
    assert not os.environ.get("BILLY_API_TOKEN"), "organization write must not use API token"
    tagged = f"+4500{secrets.token_hex(4)}"
    write_profile = AppConfig.from_environment().browser_profile
    observer_profile = write_profile.with_name(f"{write_profile.name}-readback")
    cleanup_profile = write_profile.with_name(f"{write_profile.name}-org-cleanup")
    monkeypatch.delenv("BILLY_ORGANIZATION_ID", raising=False)
    frame_dir = owner_only_frame_dir()
    server: FastMCP | None = None
    observer: BrowserRuntime | None = None
    cleanup: BrowserRuntime | None = None
    slug = ""

    try:
        assert is_outside_repository(frame_dir, _REPO_ROOT)
        server = create_server(_REPO_ROOT)
        slug = await _login(server)
        observer, observer_slug = await _ready_runtime(observer_profile)
        assert observer_slug == slug
        initial = await _phone_input_value(observer, slug)
        assert initial == ""
        await _capture_settings(observer, slug, frame_dir / "01_initial.png")

        preview_set = await _call(
            server,
            "ui_organizations_update_preview",
            {"phone": tagged, "organization_id": slug},
        )
        set_effect = preview_set["expected_effect_state"]
        assert isinstance(set_effect, dict)
        assert set_effect["phone_action"] == "set"
        await _capture_settings(observer, slug, frame_dir / "02_before_submit.png", fill=tagged)
        set_result = await _call(
            server,
            "ui_organizations_update_execute",
            {"confirmation_ticket": preview_set["confirmation_ticket"]},
        )
        if set_result.get("code") == StableErrorCode.EGRESS_DENIED:
            _record_blocker("EGRESS_DENIED on organization phone set")
            pytest.fail("EGRESS_DENIED on organization phone set")
        if set_result.get("code"):
            _record_blocker(f"set execute failed: {set_result}")
            pytest.fail(f"set execute failed: {set_result}")
        assert set_result["submitted"] is True
        after_set = await _phone_input_value(observer, slug)
        assert after_set == tagged
        await _capture_settings(observer, slug, frame_dir / "03_after_set.png")

        preview_clear = await _call(
            server,
            "ui_organizations_update_preview",
            {"phone": "", "organization_id": slug},
        )
        clear_effect = preview_clear["expected_effect_state"]
        assert isinstance(clear_effect, dict)
        assert clear_effect["phone_action"] == "clear"
        clear_result = await _call(
            server,
            "ui_organizations_update_execute",
            {"confirmation_ticket": preview_clear["confirmation_ticket"]},
        )
        if clear_result.get("code"):
            _record_blocker(f"clear execute failed: {clear_result}")
            pytest.fail(f"clear execute failed: {clear_result}")
        assert clear_result["submitted"] is True
        await observer.close()
        observer = None

        cleanup, cleanup_slug = await _ready_runtime(cleanup_profile)
        assert cleanup_slug == slug
        restored = await _phone_input_value(cleanup, slug)
        if restored != "":
            pytest.fail("CLEANUP_FAILED: company phone was not restored to empty")
        await _capture_settings(cleanup, slug, frame_dir / "04_restored.png")
        assert (frame_dir / "01_initial.png").is_file()
        assert (frame_dir / "02_before_submit.png").is_file()
        assert (frame_dir / "03_after_set.png").is_file()
        assert (frame_dir / "04_restored.png").is_file()
        write_live_pending_unless_accepted(
            _VISION_RECORD,
            workflow_ref="ui.parity.organizations.update",
            assertion_refs=[
                "tests/live/test_ui_organizations_writes.py",
                "input[name=phone]",
            ],
            second_interface_ref="fresh-session-input-name-phone",
            run_id=frame_dir.name.removeprefix("run-"),
        )
    finally:
        if observer is not None:
            await observer.close()
        if cleanup is not None:
            await cleanup.close()
        if cleanup_profile.name.endswith("-org-cleanup"):
            shutil.rmtree(cleanup_profile, ignore_errors=True)
