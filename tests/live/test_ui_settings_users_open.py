"""Live dual-session qualification for read-only ui_settings_users_open.

Indstillinger Brugere (org users) panel at /:org_slug/settings via hub open +
observe-only side-nav click Brugere (research131).

Requires opaque browser credential references. Never uses BILLY_API_TOKEN.
Independent second-interface read-back is a second ephemeral profile login.
Never clicks Invitér* / Overdrag* / Gem* / Opret* (research131 freeze).
"""

from __future__ import annotations

import json
import os
import shutil
import tempfile
from pathlib import Path
from typing import Any, cast
from urllib.parse import urlsplit

import pytest

from billy_mcp.browser import BrowserRuntime
from billy_mcp.config import AppConfig
from billy_mcp.credentials import KeyringCredentialResolver
from billy_mcp.models import AuthLoginWaitSuccess, ToolError, UiSettingsUsersOpenSuccess
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
_VISION_RECORD_DIR = _REPO_ROOT / ".fractal" / "main.billy_complete" / "tmp" / "vision-records"


def _credentials_configured() -> bool:
    return bool(
        os.environ.get("BILLY_BROWSER_PRIMARY_REFERENCE", "").strip()
        and os.environ.get("BILLY_BROWSER_SECONDARY_REFERENCE", "").strip()
    )


def _require_live_credentials() -> None:
    if not _credentials_configured():
        pytest.skip("Billy browser credential references are not configured")


def _ephemeral_profile() -> Path:
    _DATA_ROOT.mkdir(parents=True, exist_ok=True)
    return Path(tempfile.mkdtemp(prefix="billy-live-settings-users-", dir=str(_DATA_ROOT)))


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


def _org_slug_len_only(path: Path) -> int:
    payload = json.loads(path.read_text(encoding="utf-8"))
    slug = payload.get("org_slug")
    assert isinstance(slug, str) and slug
    return len(slug)


async def _capture_settings_users_frame(
    runtime: BrowserRuntime,
    org_identity: Path,
    destination: Path,
) -> None:
    """Screenshot Indstillinger Brugere surface for vision (never write CTAs)."""

    payload = json.loads(org_identity.read_text(encoding="utf-8"))
    slug = payload.get("org_slug")
    assert isinstance(slug, str) and slug
    context = await runtime.start()
    page = await context.new_page()
    try:
        await page.goto(
            f"https://mit.billy.dk/{slug}/settings",
            wait_until="domcontentloaded",
        )
        try:
            await page.wait_for_load_state("networkidle", timeout=20000)
        except Exception:
            pass
        live_page = cast(Any, page)
        # Observe-only Brugere nav click (same contract as product tool).
        loc = live_page.get_by_text("Brugere", exact=True)
        count = await loc.count()
        clicked = False
        for i in range(min(count, 8)):
            el = loc.nth(i)
            try:
                if not await el.is_visible():
                    continue
                await el.click(timeout=3000)
                clicked = True
                break
            except Exception:
                continue
        assert clicked, "vision frame must click Brugere side-nav"
        try:
            await page.wait_for_load_state("networkidle", timeout=15000)
        except Exception:
            pass
        path = urlsplit(page.url).path or ""
        assert path.rstrip("/").endswith("/settings"), "vision frame must be settings hub"
        body = await live_page.locator("body").inner_text()
        assert "Indstillinger" in body
        assert "Brugere" in body
        assert "Revisorer og bogholdere" in body
        assert "Upsedasse" not in body
        # Company default markers should not both define the active panel.
        assert not (
            "Navn og adresse" in body
            and "Kontaktinformation" in body
            and "Revisorer og bogholdere" not in body
        )
        # Do not assert person emails/phones/names into the test record.
        await live_page.screenshot(path=str(destination), full_page=False)
        assert destination.is_file() and destination.stat().st_size > 0
    finally:
        await page.close()


@pytest.mark.asyncio
async def test_dual_profiles_open_settings_users_shell() -> None:
    """Dual profiles classify the Indstillinger Brugere settings panel."""

    _require_live_credentials()
    assert not os.environ.get("BILLY_API_TOKEN"), "live settings users shell must not use API token"

    profile_a = _ephemeral_profile()
    profile_b = _ephemeral_profile()
    org_a = Path(tempfile.mkdtemp(dir=str(_DATA_ROOT))) / "org-a.json"
    org_b = Path(tempfile.mkdtemp(dir=str(_DATA_ROOT))) / "org-b.json"
    frame_dir = owner_only_frame_dir()
    record_path = _VISION_RECORD_DIR / "ui_settings_users_open.json"
    runtime_a: BrowserRuntime | None = None
    runtime_b: BrowserRuntime | None = None

    try:
        assert is_outside_repository(frame_dir, _REPO_ROOT)

        runtime_a = _runtime(profile_a, org_a)
        await _login_until_ready(runtime_a)
        open_a = await runtime_a.ui_settings_users_open()
        if isinstance(open_a, ToolError):
            pytest.fail(f"session A ui_settings_users_open failed: {open_a.code}: {open_a.message}")
        assert isinstance(open_a, UiSettingsUsersOpenSuccess)
        assert open_a.path_class == "/:org_slug/settings"
        assert open_a.heading == "Indstillinger"
        assert open_a.shell_kind == "settings_users"
        assert open_a.users_panel_markers_present is True
        assert _org_slug_len_only(org_a) > 0

        frame_a = frame_dir / "session_a_settings_users.png"
        await _capture_settings_users_frame(runtime_a, org_a, frame_a)
        await runtime_a.close()
        runtime_a = None

        runtime_b = _runtime(profile_b, org_b)
        await _login_until_ready(runtime_b)
        open_b = await runtime_b.ui_settings_users_open()
        if isinstance(open_b, ToolError):
            pytest.fail(f"session B ui_settings_users_open failed: {open_b.code}: {open_b.message}")
        assert isinstance(open_b, UiSettingsUsersOpenSuccess)
        assert open_b.model_dump() == open_a.model_dump()
        assert _org_slug_len_only(org_b) == _org_slug_len_only(org_a)

        frame_b = frame_dir / "session_b_settings_users.png"
        await _capture_settings_users_frame(runtime_b, org_b, frame_b)
        await runtime_b.close()
        runtime_b = None

        keep_frames = os.environ.get("BILLY_KEEP_VISION_FRAMES", "").strip() == "1"
        write_vision_record(
            record_path,
            workflow_ref="ui.discovery.settings_users",
            assertion_refs=[
                "tests/live/test_ui_settings_users_open.py::test_dual_profiles_open_settings_users_shell",
                "session_a_ui_settings_users_open",
                "session_b_ui_settings_users_open",
                "session_a_settings_users_frame",
                "session_b_settings_users_frame",
                "settings_users_path_settings",
            ],
            second_interface_ref="fresh_profile_b_full_login",
            reviewer_verdict="accept",
            purge_verified=False,
        )
        if keep_frames:
            hold = _DATA_ROOT / "vision-hold" / frame_dir.name
            hold.parent.mkdir(parents=True, exist_ok=True)
            if hold.exists():
                shutil.rmtree(hold, ignore_errors=True)
            shutil.copytree(frame_dir, hold)
    finally:
        for runtime in (runtime_a, runtime_b):
            if runtime is not None:
                try:
                    await runtime.close()
                except Exception:
                    pass
        if os.environ.get("BILLY_KEEP_VISION_FRAMES", "").strip() != "1":
            purged = purge_frame_dir(frame_dir)
            assert purged is True
            if record_path.exists():
                mark_purge_verified(record_path)
        shutil.rmtree(profile_a, ignore_errors=True)
        shutil.rmtree(profile_b, ignore_errors=True)
        for path in (org_a, org_b):
            if path.exists():
                path.unlink(missing_ok=True)
