"""Live dual-session READY qualification for shared Billy auth tools.

Requires opaque browser credential references. Never uses BILLY_API_TOKEN.
Independent second-interface read-back is a second ephemeral profile login.
"""

from __future__ import annotations

import json
import os
import shutil
import tempfile
from pathlib import Path
from typing import Any, cast

import pytest

from billy_mcp.browser import BrowserRuntime
from billy_mcp.config import AppConfig
from billy_mcp.credentials import KeyringCredentialResolver
from billy_mcp.models import AuthLoginWaitSuccess, ToolError
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
    return Path(tempfile.mkdtemp(prefix="billy-live-auth-", dir=str(_DATA_ROOT)))


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
        # Already-authenticated residual state is not expected on a fresh profile.
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


def _org_slug_meta(path: Path) -> dict[str, object]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    slug = payload.get("org_slug")
    assert isinstance(slug, str) and slug
    # Never return the slug value to callers that might print it.
    return {
        "source": payload.get("source"),
        "slug_len": len(slug),
        "slug_fingerprint": hash(slug),
    }


@pytest.mark.asyncio
async def test_dual_independent_profiles_reach_ready_and_restore_with_remember() -> None:
    """Profile A and independent profile B both READY; A restores after close."""

    _require_live_credentials()
    # Live auth must not invoke the API client or depend on BILLY_API_TOKEN.
    # The token may still be present in the operator environment for unrelated
    # offline work; its presence alone is not a failure (IR residual R1).

    profile_a = _ephemeral_profile()
    profile_b = _ephemeral_profile()
    org_a = Path(tempfile.mkdtemp(dir=str(_DATA_ROOT))) / "org-a.json"
    org_b = Path(tempfile.mkdtemp(dir=str(_DATA_ROOT))) / "org-b.json"
    frame_dir = owner_only_frame_dir()
    record_path = _VISION_RECORD_DIR / "auth_login_ready.json"
    runtime_a: BrowserRuntime | None = None
    runtime_b: BrowserRuntime | None = None
    runtime_restore: BrowserRuntime | None = None

    try:
        assert is_outside_repository(frame_dir, _REPO_ROOT)

        runtime_a = _runtime(profile_a, org_a)
        await _login_until_ready(runtime_a)
        assert org_a.exists()
        meta_a = _org_slug_meta(org_a)

        # Capture READY shell frame outside the repository (session A).
        context_a = await runtime_a.start()
        page_a = await context_a.new_page()
        try:
            await page_a.goto("https://mit.billy.dk/", wait_until="domcontentloaded")
            frame_a = frame_dir / "session_a_ready.png"
            await cast(Any, page_a).screenshot(path=str(frame_a), full_page=False)
            assert frame_a.is_file() and frame_a.stat().st_size > 0
        finally:
            await page_a.close()
        await runtime_a.close()
        runtime_a = None

        # Independent second interface: full login on a fresh profile.
        runtime_b = _runtime(profile_b, org_b)
        await _login_until_ready(runtime_b)
        assert org_b.exists()
        meta_b = _org_slug_meta(org_b)
        assert meta_a["slug_len"] == meta_b["slug_len"]
        assert meta_a["slug_fingerprint"] == meta_b["slug_fingerprint"]

        context_b = await runtime_b.start()
        page_b = await context_b.new_page()
        try:
            await page_b.goto("https://mit.billy.dk/", wait_until="domcontentloaded")
            frame_b = frame_dir / "session_b_ready.png"
            await cast(Any, page_b).screenshot(path=str(frame_b), full_page=False)
            assert frame_b.is_file() and frame_b.stat().st_size > 0
        finally:
            await page_b.close()
        await runtime_b.close()
        runtime_b = None

        # Same-profile restore after process close (requires product remember check).
        runtime_restore = _runtime(
            profile_a, Path(tempfile.mkdtemp(dir=str(_DATA_ROOT))) / "org-r.json"
        )
        restore_wait = await runtime_restore.auth_login_wait()
        if isinstance(restore_wait, ToolError):
            pytest.fail(f"restore auth_login_wait failed: {restore_wait.code}")
        assert restore_wait.status == "READY"
        await runtime_restore.close()
        runtime_restore = None

        write_vision_record(
            record_path,
            workflow_ref="auth.login.ready",
            assertion_refs=[
                "tests/live/test_auth_dual_session.py::test_dual_independent_profiles_reach_ready_and_restore_with_remember",
                "session_a_wait_READY",
                "session_b_wait_READY",
                "session_a_restore_wait_READY",
            ],
            second_interface_ref="fresh_profile_b_full_login",
            reviewer_verdict="pending_review",
            purge_verified=False,
        )
    finally:
        for runtime in (runtime_a, runtime_b, runtime_restore):
            if runtime is not None:
                try:
                    await runtime.close()
                except Exception:
                    pass
        purged = purge_frame_dir(frame_dir)
        assert purged is True
        if record_path.exists():
            mark_purge_verified(record_path)
        shutil.rmtree(profile_a, ignore_errors=True)
        shutil.rmtree(profile_b, ignore_errors=True)
        for path in (org_a, org_b):
            if path.exists():
                path.unlink(missing_ok=True)
