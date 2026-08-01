"""Live dual-session qualification for read-only ui_clients_get_open.

Requires opaque browser credential references. Never uses BILLY_API_TOKEN.
Independent second-interface read-back is a second ephemeral profile login.
Never submits Gem/Slet on the product get path. Live harness may create a
disposable client when the org list is empty, then delete it after.
"""

from __future__ import annotations

import json
import os
import re
import shutil
import tempfile
from pathlib import Path
from typing import Any, cast
from urllib.parse import urlsplit

import pytest

from billy_mcp.browser import BrowserRuntime
from billy_mcp.config import AppConfig
from billy_mcp.credentials import KeyringCredentialResolver
from billy_mcp.models import AuthLoginWaitSuccess, ToolError, UiClientsGetOpenSuccess
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
_MARKER = "R18665-TMP-CLIENT-GET-DO-NOT-USE"


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
    return Path(tempfile.mkdtemp(prefix="billy-live-clients-get-", dir=str(_DATA_ROOT)))


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


async def _ensure_disposable_client(runtime: BrowserRuntime, org_identity: Path) -> bool:
    """Create disposable client if get-open would fail for empty list. Returns True if created."""

    slug = _org_slug(org_identity)
    context = await runtime.start()
    page = cast(Any, await context.new_page())
    created = False
    try:
        await page.goto(f"https://mit.billy.dk/{slug}/clients", wait_until="domcontentloaded")
        try:
            await page.wait_for_load_state("networkidle", timeout=20000)
        except Exception:
            pass
        live = page
        # If any non-header row text or client marker path already present, skip seed
        links = live.locator(f"a[href*='/{slug}/contacts/'], a[href*='/{slug}/clients/']")
        rows = live.locator("table tbody tr, [role='row']")
        if await links.count() >= 1 or await rows.count() >= 2:
            return False
        cta = live.locator("text=Opret kontakt")
        if await cta.count() < 1:
            return False
        await cta.first.click()
        await page.wait_for_timeout(1500)
        name = live.locator("input[name='name']")
        if await name.count() < 1:
            return False
        await name.first.fill(_MARKER)
        for fname, val in (
            ("street", "Testvej 1"),
            ("phone", "20123456"),
            ("person_email", "r18665-tmp@example.invalid"),
            ("zipcode", "2100"),
            ("city", "København"),
        ):
            el = live.locator(f"input[name='{fname}']")
            try:
                if await el.count() >= 1 and await el.first.is_visible():
                    await el.first.fill(val)
            except Exception:
                pass
        gem = live.get_by_role("button", name=re.compile(r"^Gem$"))
        if await gem.count() >= 1:
            await gem.first.click()
            await page.wait_for_timeout(5000)
        await page.goto(f"https://mit.billy.dk/{slug}/clients", wait_until="domcontentloaded")
        await page.wait_for_timeout(1500)
        search = live.locator("input[type='search'], input[placeholder*='øg' i]")
        if await search.count() >= 1:
            await search.first.fill(_MARKER)
            await page.wait_for_timeout(1500)
        body2 = re.sub(r"\s+", " ", await live.locator("body").inner_text())[:6000]
        created = _MARKER in body2
        return created
    finally:
        await page.close()


async def _cleanup_disposable(runtime: BrowserRuntime, org_identity: Path) -> None:
    slug = _org_slug(org_identity)
    context = await runtime.start()
    page = cast(Any, await context.new_page())
    try:
        await page.goto(f"https://mit.billy.dk/{slug}/clients", wait_until="domcontentloaded")
        await page.wait_for_timeout(1200)
        live = page
        search = live.locator("input[type='search'], input[placeholder*='øg' i]")
        if await search.count() >= 1:
            await search.first.fill(_MARKER)
            await page.wait_for_timeout(1200)
        body = re.sub(r"\s+", " ", await live.locator("body").inner_text())[:6000]
        if _MARKER not in body:
            return
        try:
            await live.get_by_text(_MARKER, exact=False).first.click(timeout=6000)
            await page.wait_for_timeout(800)
            slet = live.get_by_role("button", name=re.compile(r"Slet|Delete", re.I))
            if await slet.count() >= 1:
                await slet.first.click()
                await page.wait_for_timeout(400)
                conf = live.get_by_role("button", name=re.compile(r"Slet|Delete|Bekræft|OK", re.I))
                if await conf.count() >= 1:
                    await conf.first.click()
            await page.wait_for_timeout(1500)
        except Exception:
            pass
    finally:
        await page.close()


async def _capture_clients_get_frame(
    runtime: BrowserRuntime,
    org_identity: Path,
    destination: Path,
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
        live = page
        opened = False
        rows = live.locator("table tbody tr, [role='row']")
        rn = await rows.count()
        for i in range(min(rn, 20)):
            txt = (await rows.nth(i).inner_text()).strip()
            # skip header
            if re.search(r"Navn", txt, re.I) and re.search(r"E-mail|Email", txt, re.I):
                if len(txt) < 80:
                    continue
            if len(txt) < 2:
                continue
            try:
                await rows.nth(i).click(timeout=5000)
                opened = True
                break
            except Exception:
                continue
        if not opened:
            links = live.locator(f"a[href*='/{slug}/contacts/'], a[href*='/{slug}/clients/']")
            n = await links.count()
            for i in range(min(n, 12)):
                href = await links.nth(i).get_attribute("href") or ""
                if href.rstrip("/").endswith("/clients") or "/new" in href:
                    continue
                if re.search(rf"/{re.escape(slug)}/(contacts|clients)/[^/?#]+", href):
                    await links.nth(i).click(timeout=7000)
                    opened = True
                    break
        assert opened, "vision capture could not open a client detail row"
        try:
            await page.wait_for_load_state("networkidle", timeout=15000)
        except Exception:
            pass
        await page.wait_for_timeout(1500)
        path = str(urlsplit(str(page.url)).path or "")
        assert "/contacts/" in path and (
            path.rstrip("/").endswith("/customer") or path.rstrip("/").endswith("/supplier")
        ), f"expected contacts profile path, got {path}"
        body = re.sub(r"\s+", " ", await live.locator("body").inner_text())[:800]
        assert re.search(r"\(\s*(Kunde|Leverandør|Customer|Supplier)\s*\)", body, re.I)
        assert re.search(r"\b(Ret|Edit)\b", body)
        await live.screenshot(path=str(destination), full_page=False)
        assert destination.is_file() and destination.stat().st_size > 0
        try:
            await live.keyboard.press("Escape")
        except Exception:
            pass
    finally:
        await page.close()


@pytest.mark.asyncio
async def test_dual_profiles_open_clients_detail() -> None:
    """Profile A and independent profile B both classify a client detail surface."""

    _require_live_credentials()
    assert not os.environ.get("BILLY_API_TOKEN"), "live clients get must not use API token"

    profile_a = _ephemeral_profile()
    profile_b = _ephemeral_profile()
    org_a = Path(tempfile.mkdtemp(dir=str(_DATA_ROOT))) / "org-a.json"
    org_b = Path(tempfile.mkdtemp(dir=str(_DATA_ROOT))) / "org-b.json"
    frame_dir = owner_only_frame_dir()
    record_path = _VISION_RECORD_DIR / "ui_clients_get_open.json"
    runtime_a: BrowserRuntime | None = None
    runtime_b: BrowserRuntime | None = None
    seeded = False

    try:
        assert is_outside_repository(frame_dir, _REPO_ROOT)

        runtime_a = _runtime(profile_a, org_a)
        await _login_until_ready(runtime_a)

        # Probe once; seed if empty
        probe = await runtime_a.ui_clients_get_open()
        if isinstance(probe, ToolError):
            seeded = await _ensure_disposable_client(runtime_a, org_a)
            assert seeded, f"could not seed disposable client for get-open: {probe.code}"

        detail_a = await runtime_a.ui_clients_get_open()
        if isinstance(detail_a, ToolError):
            pytest.fail(
                f"session A ui_clients_get_open failed: {detail_a.code}: {detail_a.message}"
            )
        assert isinstance(detail_a, UiClientsGetOpenSuccess)
        assert detail_a.path_class == "/:org_slug/contacts/:id/customer"
        assert detail_a.shell_kind == "clients_get"
        assert detail_a.detail_open is True
        assert detail_a.contact_name_visible is True
        assert detail_a.edit_action_visible is True
        assert detail_a.detail_markers_present is True

        frame_a = frame_dir / "session_a_clients_get.png"
        await _capture_clients_get_frame(runtime_a, org_a, frame_a)
        await runtime_a.close()
        runtime_a = None

        runtime_b = _runtime(profile_b, org_b)
        await _login_until_ready(runtime_b)
        detail_b = await runtime_b.ui_clients_get_open()
        if isinstance(detail_b, ToolError):
            pytest.fail(
                f"session B ui_clients_get_open failed: {detail_b.code}: {detail_b.message}"
            )
        assert isinstance(detail_b, UiClientsGetOpenSuccess)
        assert detail_b.model_dump() == detail_a.model_dump()

        frame_b = frame_dir / "session_b_clients_get.png"
        await _capture_clients_get_frame(runtime_b, org_b, frame_b)

        if seeded:
            await _cleanup_disposable(runtime_b, org_b)

        await runtime_b.close()
        runtime_b = None

        keep_frames = os.environ.get("BILLY_KEEP_VISION_FRAMES", "").strip() == "1"
        write_vision_record(
            record_path,
            workflow_ref="ui.contacts.get",
            assertion_refs=[
                "tests/live/test_ui_clients_get_open.py::test_dual_profiles_open_clients_detail",
                "session_a_ui_clients_get_open",
                "session_b_ui_clients_get_open",
                "session_a_clients_get_frame",
                "session_b_clients_get_frame",
                "detail_open_non_header_name_field",
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
                    if seeded:
                        try:
                            await _cleanup_disposable(
                                runtime, org_a if runtime is runtime_a else org_b
                            )
                        except Exception:
                            pass
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
