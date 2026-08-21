"""Live dual-session qualification for read-only ui_products_import.

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
from urllib.parse import urlsplit

import pytest

from billy_mcp.browser import BrowserRuntime
from billy_mcp.config import AppConfig
from billy_mcp.credentials import KeyringCredentialResolver
from billy_mcp.models import AuthLoginWaitSuccess, ToolError, UiProductsImportSuccess
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
    return Path(tempfile.mkdtemp(prefix="billy-live-products-import-", dir=str(_DATA_ROOT)))


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


async def _capture_products_import_list_frame(
    runtime: BrowserRuntime,
    org_identity: Path,
    destination: Path,
) -> None:
    """Screenshot the products import shell surface for vision review."""

    payload = json.loads(org_identity.read_text(encoding="utf-8"))
    slug = payload.get("org_slug")
    assert isinstance(slug, str) and slug
    context = await runtime.start()
    page = await context.new_page()
    try:
        await page.goto(
            f"https://mit.billy.dk/{slug}/products/import", wait_until="domcontentloaded"
        )
        try:
            await page.wait_for_load_state("networkidle", timeout=20000)
        except Exception:
            pass
        path = urlsplit(page.url).path or ""
        assert path.endswith("/products/import"), (
            "vision frame must be the products import path class"
        )
        live_page = cast(Any, page)
        heading = live_page.locator("h1")
        assert await heading.count() >= 1
        assert (await heading.first.inner_text()).strip() == "Import af produkter"
        create_action = live_page.locator("text=Vælg CSV-fil")
        assert await create_action.count() >= 1 and await create_action.first.is_visible()
        await live_page.screenshot(path=str(destination), full_page=False)
        assert destination.is_file() and destination.stat().st_size > 0
    finally:
        await page.close()


@pytest.mark.asyncio
async def test_dual_profiles_open_products_import_list_shell() -> None:
    """Profile A and independent profile B both classify the products import shell shell."""

    _require_live_credentials()

    profile_a = _ephemeral_profile()
    profile_b = _ephemeral_profile()
    org_a = Path(tempfile.mkdtemp(dir=str(_DATA_ROOT))) / "org-a.json"
    org_b = Path(tempfile.mkdtemp(dir=str(_DATA_ROOT))) / "org-b.json"
    frame_dir = owner_only_frame_dir()
    record_path = _VISION_RECORD_DIR / "ui_products_import.json"
    runtime_a: BrowserRuntime | None = None
    runtime_b: BrowserRuntime | None = None

    try:
        assert is_outside_repository(frame_dir, _REPO_ROOT)

        runtime_a = _runtime(profile_a, org_a)
        await _login_until_ready(runtime_a)
        list_a = await runtime_a.ui_products_import()
        if isinstance(list_a, ToolError):
            pytest.fail(f"session A ui_products_import failed: {list_a.code}: {list_a.message}")
        assert isinstance(list_a, UiProductsImportSuccess)
        assert list_a.path_class == "/:org_slug/products/import"
        assert list_a.heading == "Import af produkter"
        assert list_a.choose_csv_action_visible is True
        assert _org_slug_len_only(org_a) > 0

        frame_a = frame_dir / "session_a_products_import_list.png"
        await _capture_products_import_list_frame(runtime_a, org_a, frame_a)
        await runtime_a.close()
        runtime_a = None

        runtime_b = _runtime(profile_b, org_b)
        await _login_until_ready(runtime_b)
        list_b = await runtime_b.ui_products_import()
        if isinstance(list_b, ToolError):
            pytest.fail(f"session B ui_products_import failed: {list_b.code}: {list_b.message}")
        assert isinstance(list_b, UiProductsImportSuccess)
        assert list_b.model_dump() == list_a.model_dump()
        assert _org_slug_len_only(org_b) == _org_slug_len_only(org_a)

        frame_b = frame_dir / "session_b_products_import_list.png"
        await _capture_products_import_list_frame(runtime_b, org_b, frame_b)
        await runtime_b.close()
        runtime_b = None

        keep_frames = os.environ.get("BILLY_KEEP_VISION_FRAMES", "").strip() == "1"
        write_vision_record(
            record_path,
            workflow_ref="ui.discovery.product_import",
            assertion_refs=[
                "tests/live/test_ui_products_import.py::test_dual_profiles_open_products_import_list_shell",
                "session_a_ui_products_import",
                "session_b_ui_products_import",
                "session_a_products_import_list_frame",
                "session_b_products_import_list_frame",
                "import_surface_h1_import_af_produkter_choose_csv",
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
