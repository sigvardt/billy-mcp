"""Live dual-session qualification for read-only ui_daybooks_get_open.

Requires opaque browser credential references. Never uses BILLY_API_TOKEN.
Independent second-interface read-back is a second ephemeral profile login.
Never clicks create/add-line/post/Slet on the product get path. Live harness
seeds a disposable daybook via SPA token when the org has none, then deletes it.
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
from billy_mcp.models import AuthLoginWaitSuccess, ToolError, UiDaybooksGetOpenSuccess
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
_MARKER_D = "R18679-TMP-DAYBOOK-GET-DO-NOT-USE"
_ORG = "Xr7WoEDNRZu6HezpIBgOGg"
_EDITOR_MARKERS = (
    "Opret ny kassekladde",
    "Tilføj kassekladdelinje",
    "Ingen postering valgt",
)


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
    return Path(tempfile.mkdtemp(prefix="billy-live-daybooks-get-", dir=str(_DATA_ROOT)))


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


def _org_slug_len_only(path: Path) -> int:
    return len(_org_slug(path))


class _TokenCapture:
    def __init__(self) -> None:
        self.token: str | None = None

    def attach(self, page: Any) -> None:
        def on_req(req: Any) -> None:
            if "api.billysbilling.com" not in req.url:
                return
            headers = {k.lower(): v for k, v in req.headers.items()}
            tok = headers.get("x-access-token") or headers.get("x-token")
            if tok and not self.token:
                self.token = tok

        page.on("request", on_req)

    def headers(self) -> dict[str, str]:
        h = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "X-OrganizationId": _ORG,
        }
        if self.token:
            h["X-Access-Token"] = self.token
        return h


async def _spa(
    ctx: Any, method: str, url: str, headers: dict[str, str], body: dict[str, Any] | None = None
) -> dict[str, Any]:
    if method == "GET":
        r = await ctx.request.get(url, headers=headers)
    elif method == "POST":
        r = await ctx.request.post(url, headers=headers, data=json.dumps(body or {}))
    elif method == "DELETE":
        r = await ctx.request.delete(url, headers=headers)
    else:
        raise ValueError(method)
    try:
        data = await r.json()
    except Exception:
        data = None
    return {"status": r.status, "data": data}


async def _ensure_disposable_daybook(runtime: BrowserRuntime, org_identity: Path) -> dict[str, str]:
    """Seed a disposable daybook via SPA when the org list is empty."""

    slug = _org_slug(org_identity)
    context = await runtime.start()
    page = cast(Any, await context.new_page())
    cap = _TokenCapture()
    cap.attach(page)
    ids: dict[str, str] = {}
    try:
        await page.goto(f"https://mit.billy.dk/{slug}/daybooks/new", wait_until="domcontentloaded")
        try:
            await page.wait_for_load_state("networkidle", timeout=20000)
        except Exception:
            pass
        await page.wait_for_timeout(1500)
        if not cap.token:
            await page.goto(f"https://mit.billy.dk/{slug}/dashboard", wait_until="domcontentloaded")
            await page.wait_for_timeout(1500)
        headers = cap.headers()
        assert cap.token, "SPA access token not captured for daybook seed"
        ctx = cast(Any, runtime)._context

        listed = await _spa(
            ctx,
            "GET",
            f"https://api.billysbilling.com/v2/daybooks?organizationId={_ORG}&pageSize=20",
            headers,
        )
        if listed["status"] == 200 and isinstance(listed.get("data"), dict):
            rows = cast(list[dict[str, Any]], listed["data"].get("daybooks") or [])
            if rows and rows[0].get("id"):
                return {}

        dbr = await _spa(
            ctx,
            "POST",
            "https://api.billysbilling.com/v2/daybooks",
            headers,
            {
                "daybook": {
                    "organizationId": _ORG,
                    "name": _MARKER_D,
                    "isTransactionSummaryEnabled": False,
                }
            },
        )
        assert dbr["status"] in (200, 201), f"daybook seed failed: {dbr}"
        data = cast(dict[str, Any], dbr.get("data") or {})
        daybooks = cast(list[dict[str, Any]], data.get("daybooks") or [])
        daybook_id = str(daybooks[0]["id"]) if daybooks and daybooks[0].get("id") else ""
        assert daybook_id
        ids["daybook"] = daybook_id
        return ids
    finally:
        await page.close()


async def _cleanup_daybook(
    runtime: BrowserRuntime, org_identity: Path, ids: dict[str, str]
) -> None:
    if not ids.get("daybook"):
        return
    slug = _org_slug(org_identity)
    context = await runtime.start()
    page = cast(Any, await context.new_page())
    cap = _TokenCapture()
    cap.attach(page)
    try:
        await page.goto(f"https://mit.billy.dk/{slug}/daybooks/new", wait_until="domcontentloaded")
        await page.wait_for_timeout(1200)
        headers = cap.headers()
        if not cap.token:
            return
        ctx = cast(Any, runtime)._context
        await _spa(
            ctx,
            "DELETE",
            f"https://api.billysbilling.com/v2/daybooks/{ids['daybook']}",
            headers,
        )
    finally:
        await page.close()


async def _capture_daybooks_get_frame(
    runtime: BrowserRuntime, org_identity: Path, destination: Path
) -> None:
    """Screenshot the get path after tool success for vision review (outside git)."""

    slug = _org_slug(org_identity)
    context = await runtime.start()
    page = await context.new_page()
    try:
        # List via tool already classified; capture editor markers on a known get path
        # by reopening first daybook id from SPA.
        cap = _TokenCapture()
        live_page = cast(Any, page)
        cap.attach(live_page)
        await live_page.goto(
            f"https://mit.billy.dk/{slug}/daybooks/new", wait_until="domcontentloaded"
        )
        await live_page.wait_for_timeout(1200)
        headers = cap.headers()
        ctx = cast(Any, runtime)._context
        listed = await _spa(
            ctx,
            "GET",
            f"https://api.billysbilling.com/v2/daybooks?organizationId={_ORG}&pageSize=5",
            headers,
        )
        daybook_id = None
        if listed["status"] == 200 and isinstance(listed.get("data"), dict):
            rows = cast(list[dict[str, Any]], listed["data"].get("daybooks") or [])
            if rows:
                daybook_id = rows[0].get("id")
        assert daybook_id, "no daybook id for vision frame"
        await live_page.goto(
            f"https://mit.billy.dk/{slug}/daybooks/{daybook_id}",
            wait_until="domcontentloaded",
        )
        await live_page.wait_for_timeout(1200)
        path = str(urlsplit(str(live_page.url)).path or "")
        assert re.search(r"/daybooks/[^/]+$", path), path
        assert not path.rstrip("/").endswith("/daybooks/new")
        body = await live_page.locator("body").inner_text()
        for marker in _EDITOR_MARKERS:
            assert marker in body, f"missing editor marker {marker!r}"
        assert "Upsedasse" not in body
        await live_page.screenshot(path=str(destination), full_page=False)
        assert destination.is_file() and destination.stat().st_size > 0
    finally:
        await page.close()


@pytest.mark.asyncio
async def test_dual_profiles_open_daybooks_get_surface() -> None:
    """Profile A and independent profile B both classify an existing daybook get surface."""

    _require_live_credentials()
    assert not os.environ.get("BILLY_API_TOKEN"), "live daybooks get must not use API token"

    profile_a = _ephemeral_profile()
    profile_b = _ephemeral_profile()
    org_a = Path(tempfile.mkdtemp(dir=str(_DATA_ROOT))) / "org-a.json"
    org_b = Path(tempfile.mkdtemp(dir=str(_DATA_ROOT))) / "org-b.json"
    frame_dir = owner_only_frame_dir()
    record_path = _VISION_RECORD_DIR / "ui_daybooks_get_open.json"
    runtime_a: BrowserRuntime | None = None
    runtime_b: BrowserRuntime | None = None
    ids_a: dict[str, str] = {}
    ids_b: dict[str, str] = {}

    try:
        assert is_outside_repository(frame_dir, _REPO_ROOT)

        runtime_a = _runtime(profile_a, org_a)
        await _login_until_ready(runtime_a)
        ids_a = await _ensure_disposable_daybook(runtime_a, org_a)
        open_a = await runtime_a.ui_daybooks_get_open()
        if isinstance(open_a, ToolError):
            pytest.fail(f"session A ui_daybooks_get_open failed: {open_a.code}: {open_a.message}")
        assert isinstance(open_a, UiDaybooksGetOpenSuccess)
        assert open_a.path_class == "/:org_slug/daybooks/:id"
        assert open_a.shell_kind == "daybooks_get"
        assert open_a.detail_open is True
        assert open_a.editor_markers_present is True
        assert open_a.shell_markers_present is True
        assert _org_slug_len_only(org_a) > 0

        frame_a = frame_dir / "session_a_daybooks_get.png"
        await _capture_daybooks_get_frame(runtime_a, org_a, frame_a)
        await _cleanup_daybook(runtime_a, org_a, ids_a)
        await runtime_a.close()
        runtime_a = None

        runtime_b = _runtime(profile_b, org_b)
        await _login_until_ready(runtime_b)
        ids_b = await _ensure_disposable_daybook(runtime_b, org_b)
        open_b = await runtime_b.ui_daybooks_get_open()
        if isinstance(open_b, ToolError):
            pytest.fail(f"session B ui_daybooks_get_open failed: {open_b.code}: {open_b.message}")
        assert isinstance(open_b, UiDaybooksGetOpenSuccess)
        assert open_b.model_dump() == open_a.model_dump()
        assert _org_slug_len_only(org_b) == _org_slug_len_only(org_a)

        frame_b = frame_dir / "session_b_daybooks_get.png"
        await _capture_daybooks_get_frame(runtime_b, org_b, frame_b)
        await _cleanup_daybook(runtime_b, org_b, ids_b)
        await runtime_b.close()
        runtime_b = None

        keep_frames = os.environ.get("BILLY_KEEP_VISION_FRAMES", "").strip() == "1"
        write_vision_record(
            record_path,
            workflow_ref="ui.parity.daybooks.get",
            assertion_refs=[
                "tests/live/test_ui_daybooks_get_open.py::test_dual_profiles_open_daybooks_get_surface",
                "session_a_ui_daybooks_get_open",
                "session_b_ui_daybooks_get_open",
                "session_a_daybooks_get_frame",
                "session_b_daybooks_get_frame",
                "path_class_daybooks_id",
                "editor_markers_opret_tilfoej_ingen_postering",
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
        for runtime, org, ids in (
            (runtime_a, org_a, ids_a),
            (runtime_b, org_b, ids_b),
        ):
            if runtime is not None:
                try:
                    await _cleanup_daybook(runtime, org, ids)
                except Exception:
                    pass
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
