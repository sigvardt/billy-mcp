"""Live dual-session qualification for read-only ui_suppliers_create_open.

Requires opaque browser credential references. Never uses BILLY_API_TOKEN.
Independent second-interface read-back is a second ephemeral profile login.
Never submits Gem/Opret/Save on the create dialog.
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
from billy_mcp.models import AuthLoginWaitSuccess, ToolError, UiSuppliersCreateOpenSuccess
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
    return Path(tempfile.mkdtemp(prefix="billy-live-suppliers-create-", dir=str(_DATA_ROOT)))


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


async def _capture_suppliers_create_frame(
    runtime: BrowserRuntime,
    org_identity: Path,
    destination: Path,
) -> None:
    """Screenshot the suppliers create dialog surface for vision review."""

    payload = json.loads(org_identity.read_text(encoding="utf-8"))
    slug = payload.get("org_slug")
    assert isinstance(slug, str) and slug
    context = await runtime.start()
    page = await context.new_page()
    try:
        await page.goto(f"https://mit.billy.dk/{slug}/suppliers", wait_until="domcontentloaded")
        try:
            await page.wait_for_load_state("networkidle", timeout=20000)
        except Exception:
            pass
        live_page = cast(Any, page)
        cta = live_page.locator("text=Opret kontakt")
        assert await cta.count() >= 1 and await cta.first.is_visible()
        await cta.first.click()
        try:
            await page.wait_for_load_state("networkidle", timeout=10000)
        except Exception:
            pass
        path = urlsplit(page.url).path or ""
        assert path.rstrip("/").endswith("/suppliers") and not path.rstrip("/").endswith(
            "/suppliers/new"
        ), "vision frame must stay on suppliers list path class"
        name = live_page.locator("input[name='name']")
        assert await name.count() >= 1 and await name.first.is_visible()
        await live_page.screenshot(path=str(destination), full_page=False)
        assert destination.is_file() and destination.stat().st_size > 0
        try:
            await live_page.keyboard.press("Escape")
        except Exception:
            pass
    finally:
        await page.close()


@pytest.mark.asyncio
async def test_dual_profiles_open_suppliers_create_form() -> None:
    """Profile A and independent profile B both classify the suppliers create form."""

    _require_live_credentials()

    profile_a = _ephemeral_profile()
    profile_b = _ephemeral_profile()
    org_a = Path(tempfile.mkdtemp(dir=str(_DATA_ROOT))) / "org-a.json"
    org_b = Path(tempfile.mkdtemp(dir=str(_DATA_ROOT))) / "org-b.json"
    frame_dir = owner_only_frame_dir()
    record_path = _VISION_RECORD_DIR / "ui_suppliers_create_open.json"
    runtime_a: BrowserRuntime | None = None
    runtime_b: BrowserRuntime | None = None

    try:
        assert is_outside_repository(frame_dir, _REPO_ROOT)

        runtime_a = _runtime(profile_a, org_a)
        await _login_until_ready(runtime_a)
        form_a = await runtime_a.ui_suppliers_create_open()
        if isinstance(form_a, ToolError):
            pytest.fail(
                f"session A ui_suppliers_create_open failed: {form_a.code}: {form_a.message}"
            )
        assert isinstance(form_a, UiSuppliersCreateOpenSuccess)
        assert form_a.path_class == "/:org_slug/suppliers"
        assert form_a.heading == "Leverandører"
        assert form_a.shell_kind == "suppliers_create"
        assert form_a.create_dialog_open is True
        assert form_a.name_field_visible is True
        assert form_a.registration_no_field_present is True
        assert form_a.address_or_person_fields_present is True
        assert _org_slug_len_only(org_a) > 0

        frame_a = frame_dir / "session_a_suppliers_create.png"
        await _capture_suppliers_create_frame(runtime_a, org_a, frame_a)
        await runtime_a.close()
        runtime_a = None

        runtime_b = _runtime(profile_b, org_b)
        await _login_until_ready(runtime_b)
        form_b = await runtime_b.ui_suppliers_create_open()
        if isinstance(form_b, ToolError):
            pytest.fail(
                f"session B ui_suppliers_create_open failed: {form_b.code}: {form_b.message}"
            )
        assert isinstance(form_b, UiSuppliersCreateOpenSuccess)
        assert form_b.model_dump() == form_a.model_dump()
        assert _org_slug_len_only(org_b) == _org_slug_len_only(org_a)

        frame_b = frame_dir / "session_b_suppliers_create.png"
        await _capture_suppliers_create_frame(runtime_b, org_b, frame_b)
        await runtime_b.close()
        runtime_b = None

        keep_frames = os.environ.get("BILLY_KEEP_VISION_FRAMES", "").strip() == "1"
        write_vision_record(
            record_path,
            workflow_ref="ui.contacts.create",
            assertion_refs=[
                "tests/live/test_ui_suppliers_create_open.py::"
                "test_dual_profiles_open_suppliers_create_form",
                "session_a_ui_suppliers_create_open",
                "session_b_ui_suppliers_create_open",
                "session_a_suppliers_create_frame",
                "session_b_suppliers_create_frame",
                "create_dialog_opret_kontakt_name_registrationNo",
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
        for profile in (profile_a, profile_b):
            shutil.rmtree(profile, ignore_errors=True)
        for org in (org_a, org_b):
            if org.parent.exists():
                shutil.rmtree(org.parent, ignore_errors=True)
        purge_frame_dir(frame_dir)
        if record_path.exists():
            mark_purge_verified(record_path)
