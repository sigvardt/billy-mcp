"""Live inspect: product list Mere and inventory delete chrome.

Read-only. Never clicks Gem. Never creates a product.
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
from billy_mcp.ui_writes.page_flow import BILLY_ORIGIN
from billy_mcp.ui_writes.products_delete_chrome import (
    PRODUCTS_DELETE_CHROME_DUMP,
    REQUIRED_PRODUCTS_DELETE_CHROME_KEYS,
    apply_products_delete_chrome_dump,
    inspect_inventory_chrome,
    inspect_products_list_chrome,
    products_delete_chrome_dump_is_delivered,
    products_delete_chrome_missing_keys,
)

pytestmark = pytest.mark.live

_REPO_ROOT = Path(__file__).resolve().parents[2]
_EGRESS = _REPO_ROOT / "coverage" / "browser_egress.yaml"
_DATA_ROOT = Path.home() / ".local" / "share" / "billy-mcp"
_BLOCKER_PATH = (
    _REPO_ROOT
    / ".fractal"
    / "main.billy_complete"
    / "tmp"
    / "live-products-delete-chrome-blocker.txt"
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
        "Live product delete-chrome blocked: BILLY_BROWSER_PRIMARY_REFERENCE and "
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
    assert products_delete_chrome_missing_keys(payload) == []
    assert set(REQUIRED_PRODUCTS_DELETE_CHROME_KEYS) <= set(payload)
    encoded = json.dumps({"result": payload})
    assert "https://" not in encoded
    assert "function(" not in encoded
    assert "confirmation_ticket" not in encoded
    assert "MCP-TEST-PRODUCT-" not in encoded
    if require_code and payload.get("proved_delete_path") == "none":
        assert payload.get("code") == "UI_CHANGED"


@pytest.mark.asyncio
async def test_ui_products_delete_chrome() -> None:
    """Inspect exact Slet chrome on products Mere and inventory. Do not save."""

    _require_live_credentials()
    assert not os.environ.get("BILLY_API_TOKEN"), "delete-chrome dump must not use API token"
    if products_delete_chrome_dump_is_delivered():
        written = json.loads(PRODUCTS_DELETE_CHROME_DUMP.read_text(encoding="utf-8"))
        _assert_dump_clean(written)
        text = PRODUCTS_DELETE_CHROME_DUMP.read_text(encoding="utf-8")
        assert "https://" not in text
        assert "MCP-TEST-PRODUCT-" not in text
        return

    _DATA_ROOT.mkdir(parents=True, exist_ok=True)
    profile = Path(tempfile.mkdtemp(prefix="billy-live-products-chrome-", dir=str(_DATA_ROOT)))
    runtime: BrowserRuntime | None = None
    page: Any = None
    try:
        runtime = _runtime(profile)
        slug = await _login_until_ready(runtime)
        context = await runtime.start()
        page = cast(Any, await context.new_page())
        await _goto(page, slug, "products")
        list_part = await inspect_products_list_chrome(page)
        try:
            await page.keyboard.press("Escape")
        except Exception:
            pass
        await _goto(page, slug, "inventory")
        inventory_part = await inspect_inventory_chrome(page, open_create=True)
        try:
            await page.keyboard.press("Escape")
        except Exception:
            pass
        result = apply_products_delete_chrome_dump({**list_part, **inventory_part})
        _assert_dump_clean(result, require_code=True)
        assert PRODUCTS_DELETE_CHROME_DUMP.is_file()
        written = json.loads(PRODUCTS_DELETE_CHROME_DUMP.read_text(encoding="utf-8"))
        _assert_dump_clean(written)
        if result.get("proved_delete_path") != "none":
            _record_blocker("new product delete chrome appeared; persist half not run in dump pass")
    finally:
        if page is not None:
            await page.close()
        if runtime is not None:
            await runtime.close()
        shutil.rmtree(profile, ignore_errors=True)
        shutil.rmtree(profile.with_name(f"{profile.name}-readback"), ignore_errors=True)
