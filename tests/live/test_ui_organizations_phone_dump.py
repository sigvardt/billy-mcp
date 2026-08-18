"""Live inspect: company settings phone field and exact Gem ændringer.

Read-only. Never clicks Gem ændringer. Never changes company settings.
"""

from __future__ import annotations

import asyncio
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
from billy_mcp.ui_writes.organizations_phone_dump import (
    ORGANIZATIONS_PHONE_DUMP,
    REQUIRED_ORGANIZATIONS_PHONE_DUMP_KEYS,
    apply_organizations_phone_dump,
    inspect_organizations_phone_chrome,
    organizations_phone_dump_is_delivered,
    organizations_phone_dump_missing_keys,
    persist_allowed_from,
)
from billy_mcp.ui_writes.page_flow import BILLY_ORIGIN

pytestmark = pytest.mark.live

_REPO_ROOT = Path(__file__).resolve().parents[2]
_EGRESS = _REPO_ROOT / "coverage" / "browser_egress.yaml"
_DATA_ROOT = Path.home() / ".local" / "share" / "billy-mcp"
_BLOCKER_PATH = (
    _REPO_ROOT / ".fractal" / "main.billy_complete" / "tmp" / "live-organizations-phone-blocker.txt"
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
        "Live organization phone dump blocked: BILLY_BROWSER_PRIMARY_REFERENCE and "
        "BILLY_BROWSER_SECONDARY_REFERENCE are not both set."
    )
    _record_blocker(reason)
    pytest.skip(reason)


def _runtime(profile: Path) -> BrowserRuntime:
    configuration = AppConfig.from_environment()
    return BrowserRuntime(
        profile,
        egress_manifest_path=_EGRESS,
        credential_references=configuration.browser_credentials,
        credential_resolver=KeyringCredentialResolver(),
    )


async def _login_until_ready(runtime: BrowserRuntime) -> str:
    start = await runtime.auth_login_start()
    if isinstance(start, ToolError) and start.code != "UI_CHANGED":
        _record_blocker(f"auth_login_start failed: {start.code}")
        pytest.fail(f"auth_login_start failed: {start.code}")
    wait = await runtime.auth_login_wait()
    if isinstance(wait, ToolError):
        _record_blocker(f"auth_login_wait failed: {wait.code}")
        pytest.fail(f"auth_login_wait failed: {wait.code}: {wait.message}")
    assert isinstance(wait, AuthLoginWaitSuccess)
    if wait.status != "READY":
        wait = await runtime.auth_login_wait()
    assert isinstance(wait, AuthLoginWaitSuccess)
    if wait.status != "READY":
        _record_blocker(f"auth_login_wait not READY: {wait.status}")
        pytest.fail(f"auth_login_wait not READY: {wait.status}")
    slug = wait.organization_id
    if not isinstance(slug, str) or not slug.strip():
        _record_blocker("READY omitted organization_id")
        pytest.fail("READY omitted organization_id")
    return slug


async def _goto(page: Any, slug: str, path: str) -> None:
    await page.goto(f"{BILLY_ORIGIN}/{slug}/{path}", wait_until="domcontentloaded")
    try:
        await page.wait_for_load_state("networkidle", timeout=20000)
    except (TimeoutError, RuntimeError):
        pass
    await asyncio.sleep(0.5)


def _assert_dump_clean(payload: dict[str, object], *, require_code: bool = False) -> None:
    assert organizations_phone_dump_missing_keys(payload) == []
    assert set(REQUIRED_ORGANIZATIONS_PHONE_DUMP_KEYS) <= set(payload)
    encoded = json.dumps({"result": payload})
    assert "https://" not in encoded
    assert "function(" not in encoded
    assert "confirmation_ticket" not in encoded
    assert "+4500" not in encoded
    if require_code and payload.get("proved_phone_only") is not True:
        assert payload.get("code") == "UI_CHANGED"


@pytest.mark.asyncio
async def test_ui_organizations_phone_dump() -> None:
    """Inspect the company phone field. Do not save."""

    _require_live_credentials()
    assert not os.environ.get("BILLY_API_TOKEN"), "phone dump must not use API token"
    if organizations_phone_dump_is_delivered():
        written = json.loads(ORGANIZATIONS_PHONE_DUMP.read_text(encoding="utf-8"))
        _assert_dump_clean(written)
        text = ORGANIZATIONS_PHONE_DUMP.read_text(encoding="utf-8")
        assert "https://" not in text
        assert "+4500" not in text
        if written.get("proved_phone_only") is True:
            _record_blocker(
                "phone dump already delivered; persist lives in "
                "test_ui_organizations_writes.py. No remake."
            )
        return

    _DATA_ROOT.mkdir(parents=True, exist_ok=True)
    profile = Path(tempfile.mkdtemp(prefix="billy-live-org-phone-", dir=str(_DATA_ROOT)))
    runtime: BrowserRuntime | None = None
    page: Any = None
    try:
        runtime = _runtime(profile)
        slug = await _login_until_ready(runtime)
        context = await runtime.start()
        page = cast(Any, await context.new_page())
        await _goto(page, slug, "settings")
        inspected = await inspect_organizations_phone_chrome(page)
        result = apply_organizations_phone_dump(inspected)
        _assert_dump_clean(result, require_code=True)
        assert ORGANIZATIONS_PHONE_DUMP.is_file()
        written = json.loads(ORGANIZATIONS_PHONE_DUMP.read_text(encoding="utf-8"))
        _assert_dump_clean(written)
        if persist_allowed_from(result):
            _record_blocker(
                "phone-only surface proved with restorable original; persist half not run"
            )
        elif result.get("proved_phone_only") is True:
            _record_blocker(
                "phone-only surface proved; original phone empty or unreadable; "
                "restore ticket cannot bind a blank value. No submit."
            )
    finally:
        if page is not None:
            await page.close()
        if runtime is not None:
            await runtime.close()
        shutil.rmtree(profile, ignore_errors=True)
        shutil.rmtree(profile.with_name(f"{profile.name}-readback"), ignore_errors=True)
