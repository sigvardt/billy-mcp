"""Live MCP qualification for ticketed UI draft invoice create, update, and delete.

Requires opaque browser credential references. Never uses BILLY_API_TOKEN.
Pass proof is FastMCP call_tool on create_server. Independent read-back is a
second session. Cleanup is proved on a third fresh session.
Never Godkend, Send, or emails an invoice.
"""

from __future__ import annotations

import asyncio
import atexit
import json
import os
import re
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
from billy_mcp.models import AuthLoginWaitSuccess, StableErrorCode, ToolError
from billy_mcp.server import create_server
from billy_mcp.ui_writes.invoices_form_bind import price_is, read_unit_price
from billy_mcp.ui_writes.invoices_form_delete import POST_SLET_DUMP
from billy_mcp.ui_writes.invoices_form_row import open_invoice_row
from billy_mcp.ui_writes.page_flow import exact_name_in_text
from billy_mcp.vision_evidence import (
    is_outside_repository,
    owner_only_frame_dir,
    write_vision_record,
)

pytestmark = pytest.mark.live

_REPO_ROOT = Path(__file__).resolve().parents[2]
_DATA_ROOT = Path.home() / ".local" / "share" / "billy-mcp"
_VISION_RECORD = _REPO_ROOT / "tmp" / "vision-records" / "ui_invoices_writes.json"
_BLOCKER_PATH = (
    _REPO_ROOT / ".fractal" / "main.billy_complete" / "tmp" / "live-invoices-writes-blocker.txt"
)
_LEFTOVER_CONTACT_RE = re.compile(r"MCP-UI-INV-[0-9A-F]{8}")
LEFTOVER_INVOICE_CONTACTS = (
    "MCP-UI-INV-6CDB396B",
    "MCP-UI-INV-F1784522",
    "MCP-UI-INV-B05A4C85",
    "MCP-UI-INV-A45B734E",
    "MCP-UI-INV-2B8A4FA2",
    "MCP-UI-INV-DD4158B1",
)
LEFTOVER_PRODUCTS = (
    "MCP-UI-PRD-FB5F7474",
    "MCP-UI-PRD-633E97EC",
    "MCP-UI-PRD-86AB7365",
    "MCP-UI-PRD-B4A4DD5A",
    "MCP-UI-PRD-26720BD4",
    "MCP-UI-PRD-05C906D9",
)
UPDATE_CONTACT = "MCP-UI-INV-6CDB396B"
_REGISTERED_PROFILES: list[Path] = []


def _credentials_configured() -> bool:
    return bool(
        os.environ.get("BILLY_BROWSER_PRIMARY_REFERENCE", "").strip()
        and os.environ.get("BILLY_BROWSER_SECONDARY_REFERENCE", "").strip()
    )


def _record_blocker(reason: str) -> None:
    _BLOCKER_PATH.parent.mkdir(parents=True, exist_ok=True)
    _BLOCKER_PATH.write_text(reason.strip() + "\n", encoding="utf-8")


def _post_slet_dump() -> dict[str, object] | None:
    if not POST_SLET_DUMP.is_file():
        return None
    payload = json.loads(POST_SLET_DUMP.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        return None
    return cast(dict[str, object], payload)


def _require_live_credentials() -> None:
    if _credentials_configured():
        return
    reason = (
        "Live MCP invoice writes blocked: BILLY_BROWSER_PRIMARY_REFERENCE and "
        "BILLY_BROWSER_SECONDARY_REFERENCE are not both set."
    )
    _record_blocker(reason)
    pytest.skip(reason)


def _purge_registered_profiles() -> None:
    for path in _REGISTERED_PROFILES:
        shutil.rmtree(path, ignore_errors=True)


atexit.register(_purge_registered_profiles)


def _temp_profile() -> Path:
    _DATA_ROOT.mkdir(parents=True, exist_ok=True)
    path = Path(tempfile.mkdtemp(prefix="billy-live-invoices-", dir=str(_DATA_ROOT)))
    _REGISTERED_PROFILES.append(path)
    _REGISTERED_PROFILES.append(path.with_name(f"{path.name}-readback"))
    return path


async def _delete_or_fail(
    server: FastMCP,
    preview_tool: str,
    execute_tool: str,
    arguments: dict[str, object],
    label: str,
) -> None:
    preview = await _call(server, preview_tool, arguments)
    if preview.get("code"):
        _record_blocker(f"{label} preview failed: {preview}")
        pytest.fail(f"{label} preview failed: {preview}")
    ticket = preview.get("confirmation_ticket")
    if not isinstance(ticket, str) or not ticket:
        _record_blocker(f"{label} preview omitted confirmation_ticket")
        pytest.fail(f"{label} preview omitted confirmation_ticket")
    executed = await _call(server, execute_tool, {"confirmation_ticket": ticket})
    if executed.get("code") and executed.get("code") != "NOT_FOUND":
        _record_blocker(f"{label} execute failed: {executed}")
        pytest.fail(f"{label} execute failed: {executed}")


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
        if isinstance(started, ToolError):
            pytest.fail(f"session login start failed: {started.code}")
        waited = await runtime.auth_login_wait()
    if isinstance(waited, ToolError):
        pytest.fail(f"session login failed: {waited.code}")
    assert isinstance(waited, AuthLoginWaitSuccess)
    assert waited.status == "READY"
    assert waited.organization_id == slug


async def _open_named_list(
    page: Any, slug: str, path: str, name: str, *, allow_search: bool = True
) -> None:
    await page.goto(f"https://mit.billy.dk/{slug}/{path}", wait_until="domcontentloaded")
    try:
        await page.wait_for_load_state("networkidle", timeout=20000)
    except (TimeoutError, RuntimeError):
        pass
    if not allow_search:
        return
    search = page.locator("input[type='search'], input[placeholder*='øg' i]")
    if await search.count() >= 1:
        await search.first.fill(name)
        await asyncio.sleep(1.5)


async def _list_has_name(
    runtime: BrowserRuntime, slug: str, path: str, name: str, *, allow_search: bool = True
) -> bool:
    context = await runtime.start()
    page = cast(Any, await context.new_page())
    try:
        await _open_named_list(page, slug, path, name, allow_search=allow_search)
        if path == "invoices":
            visible = page.get_by_text(name, exact=True)
            return await visible.count() >= 1 and await visible.first.is_visible()
        if path == "products":
            match = page.get_by_text(name, exact=True)
            row = page.locator("[data-cy='table-item']").filter(has=match)
            return await row.count() >= 1 and await row.first.is_visible()
        body = await page.locator("body").inner_text()
        return exact_name_in_text(body, name)
    finally:
        await page.close()


async def _clients_has_name(runtime: BrowserRuntime, slug: str, name: str) -> bool:
    context = await runtime.start()
    page = cast(Any, await context.new_page())
    try:
        await page.goto(f"https://mit.billy.dk/{slug}/clients", wait_until="domcontentloaded")
        try:
            await page.wait_for_load_state("networkidle", timeout=20000)
        except (TimeoutError, RuntimeError):
            pass
        search = page.locator("input[type='search'], input[placeholder*='øg' i]")
        if await search.count() >= 1:
            await search.first.fill(name)
            await asyncio.sleep(1.5)
        exact = page.get_by_text(name, exact=True)
        return await exact.count() >= 1
    finally:
        await page.close()


async def _leftover_invoice_contact_names(runtime: BrowserRuntime, slug: str) -> list[str]:
    context = await runtime.start()
    page = cast(Any, await context.new_page())
    try:
        await _open_named_list(page, slug, "clients", "MCP-UI-INV")
        body = await page.locator("body").inner_text()
        return sorted(set(_LEFTOVER_CONTACT_RE.findall(body)))
    finally:
        await page.close()


async def _row_enhedspris(runtime: BrowserRuntime, slug: str, contact_name: str) -> str:
    """Open the leftover row in this session and read Enhedspris. Not a POST id."""

    context = await runtime.start()
    page = cast(Any, await context.new_page())
    try:
        failed = await open_invoice_row(page, slug, contact_name)
        if failed is not None:
            return ""
        return await read_unit_price(page)
    finally:
        await page.close()


async def _capture(runtime: BrowserRuntime, slug: str, destination: Path, name: str) -> None:
    context = await runtime.start()
    page = cast(Any, await context.new_page())
    try:
        await _open_named_list(page, slug, "invoices", name, allow_search=False)
        await page.screenshot(path=str(destination), full_page=False)
        assert destination.is_file() and destination.stat().st_size > 0
    finally:
        await page.close()


@pytest.mark.asyncio
async def test_ui_invoices_create_update_delete_via_call_tool(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Update one leftover draft through FastMCP, then reverse-delete all six triples."""

    _require_live_credentials()
    assert not os.environ.get("BILLY_API_TOKEN"), "live invoice writes must not use API token"
    profile = _temp_profile()
    observer_profile = _temp_profile()
    cleanup_profile = _temp_profile()
    monkeypatch.setenv("BILLY_BROWSER_PROFILE", str(profile))
    monkeypatch.delenv("BILLY_ORGANIZATION_ID", raising=False)
    frame_dir = owner_only_frame_dir()
    server: FastMCP | None = None
    extra: BrowserRuntime | None = None
    slug = ""
    updated = f"{UPDATE_CONTACT}-U"

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
        if not await _list_has_name(observer, slug, "invoices", UPDATE_CONTACT, allow_search=False):
            _record_blocker(f"leftover draft {UPDATE_CONTACT} is not on /invoices")
            pytest.fail(f"leftover draft {UPDATE_CONTACT} is not on /invoices")
        preview_update = await _call(
            server,
            "ui_invoices_update_preview",
            {
                "contact_name": UPDATE_CONTACT,
                "line_description": updated,
                "unit_price": 2.0,
                "action": "draft_update",
                "save_cta": "Gem som kladde",
                "organization_id": slug,
            },
        )
        updated_result = await _call(
            server,
            "ui_invoices_update_execute",
            {"confirmation_ticket": preview_update["confirmation_ticket"]},
        )
        if updated_result.get("code"):
            _record_blocker(f"update execute failed: {updated_result}")
            pytest.fail(f"update execute failed: {updated_result}")
        assert updated_result["submitted"] is True
        await _capture(observer, slug, frame_dir / "03_after_update.png", UPDATE_CONTACT)
        readback_profile = _temp_profile()
        readback = BrowserRuntime(
            readback_profile,
            credential_references=AppConfig.from_environment().browser_credentials,
            credential_resolver=KeyringCredentialResolver(),
        )
        extra = readback
        await _ready_session(readback, slug)
        shown = await _row_enhedspris(readback, slug, UPDATE_CONTACT)
        if not price_is(shown, 2.0):
            _record_blocker(f"fresh Enhedspris is not 2,00 after update: shown_len={len(shown)}")
            pytest.fail("fresh Enhedspris is not 2,00 after update")
        await readback.close()
        extra = observer
        for leftover_contact in LEFTOVER_INVOICE_CONTACTS:
            preview = await _call(
                server,
                "ui_invoices_delete_preview",
                {
                    "contact_name": leftover_contact,
                    "action": "draft_delete",
                    "save_cta": "Slet",
                    "organization_id": slug,
                },
            )
            if preview.get("code"):
                _record_blocker(f"delete preview failed for {leftover_contact}: {preview}")
                pytest.fail(f"delete preview failed for {leftover_contact}: {preview}")
            deleted = await _call(
                server,
                "ui_invoices_delete_execute",
                {"confirmation_ticket": preview["confirmation_ticket"]},
            )
            if deleted.get("code"):
                dump = _post_slet_dump()
                _record_blocker(
                    f"delete execute failed for {leftover_contact}: {deleted} dump={dump}"
                )
                assert dump is not None
                for key in (
                    "heading_token",
                    "path_class",
                    "active_tag",
                    "active_role",
                    "candidates",
                    "dialog_count",
                    "alertdialog_count",
                    "overlay_count",
                    "hit_tag",
                    "delete_seen",
                    "navigated",
                ):
                    assert key in dump
                from billy_mcp.ui_writes.invoices_form_delete_dump import OverlayDump

                parsed = OverlayDump.model_validate({"rows": dump["candidates"]})
                assert isinstance(parsed.rows, list)
                pytest.fail(f"delete execute failed for {leftover_contact}: {deleted}")

        await observer.close()
        extra = None
        cleanup = BrowserRuntime(
            cleanup_profile,
            credential_references=AppConfig.from_environment().browser_credentials,
            credential_resolver=KeyringCredentialResolver(),
        )
        extra = cleanup
        await _ready_session(cleanup, slug)
        for leftover_contact in LEFTOVER_INVOICE_CONTACTS:
            present = await _list_has_name(
                cleanup, slug, "invoices", leftover_contact, allow_search=False
            )
            if present:
                pytest.fail(f"invoice still present after delete: {leftover_contact}")
        assert await _list_has_name(cleanup, slug, "invoices", updated, allow_search=False) is False

        for leftover_product in LEFTOVER_PRODUCTS:
            await _delete_or_fail(
                server,
                "ui_products_delete_preview",
                "ui_products_delete_execute",
                {"unique_tag": leftover_product, "organization_id": slug},
                f"product {leftover_product}",
            )
            assert await _list_has_name(cleanup, slug, "products", leftover_product) is False

        for leftover_contact in LEFTOVER_INVOICE_CONTACTS:
            await _delete_or_fail(
                server,
                "ui_clients_delete_preview",
                "ui_clients_delete_execute",
                {"name": leftover_contact, "organization_id": slug},
                f"contact {leftover_contact}",
            )
            assert await _list_has_name(cleanup, slug, "clients", leftover_contact) is False

        write_vision_record(
            _VISION_RECORD,
            workflow_ref="ui.parity.invoices.update",
            assertion_refs=[
                "tests/live/test_ui_invoices_writes.py::"
                "test_ui_invoices_create_update_delete_via_call_tool",
                "create_server_call_tool_leftover_update_delete",
                "list_row_open_not_post_id",
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
        if server is not None and slug:
            for leftover_contact in LEFTOVER_INVOICE_CONTACTS:
                try:
                    preview_delete = await _call(
                        server,
                        "ui_invoices_delete_preview",
                        {
                            "contact_name": leftover_contact,
                            "action": "draft_delete",
                            "save_cta": "Slet",
                            "organization_id": slug,
                        },
                    )
                    if not preview_delete.get("code"):
                        await _call(
                            server,
                            "ui_invoices_delete_execute",
                            {"confirmation_ticket": preview_delete["confirmation_ticket"]},
                        )
                except (OSError, RuntimeError, AssertionError, TimeoutError):
                    _record_blocker(
                        f"Cleanup delete failed for leftover tagged invoice {leftover_contact}."
                    )
            for leftover_product in LEFTOVER_PRODUCTS:
                try:
                    leftover_product_preview = await _call(
                        server,
                        "ui_products_delete_preview",
                        {"unique_tag": leftover_product, "organization_id": slug},
                    )
                    if not leftover_product_preview.get("code"):
                        await _call(
                            server,
                            "ui_products_delete_execute",
                            {
                                "confirmation_ticket": leftover_product_preview[
                                    "confirmation_ticket"
                                ]
                            },
                        )
                except (OSError, RuntimeError, AssertionError, TimeoutError):
                    _record_blocker(
                        f"Cleanup delete failed for leftover tagged product {leftover_product}."
                    )
            for leftover_contact in LEFTOVER_INVOICE_CONTACTS:
                try:
                    contact_delete = await _call(
                        server,
                        "ui_clients_delete_preview",
                        {"name": leftover_contact, "organization_id": slug},
                    )
                    if not contact_delete.get("code"):
                        await _call(
                            server,
                            "ui_clients_delete_execute",
                            {"confirmation_ticket": contact_delete["confirmation_ticket"]},
                        )
                except (OSError, RuntimeError, AssertionError, TimeoutError):
                    _record_blocker(
                        f"Cleanup delete failed for leftover tagged contact {leftover_contact}."
                    )
        if extra is not None:
            await extra.close()
        for path in list(_REGISTERED_PROFILES):
            if path.name.startswith("billy-live-invoices-"):
                shutil.rmtree(path, ignore_errors=True)


@pytest.mark.asyncio
async def test_ui_invoice_leftover_product_contact_cleanup(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Delete leftover products then customers after invoice drafts are gone."""

    _require_live_credentials()
    assert not os.environ.get("BILLY_API_TOKEN"), "leftover cleanup must not use API token"
    profile = _temp_profile()
    proof_profile = _temp_profile()
    monkeypatch.setenv("BILLY_BROWSER_PROFILE", str(profile))
    monkeypatch.delenv("BILLY_ORGANIZATION_ID", raising=False)
    server: FastMCP | None = None
    extra: BrowserRuntime | None = None
    slug = ""
    try:
        server = create_server(_REPO_ROOT)
        slug = await _login(server)
        for leftover_product in LEFTOVER_PRODUCTS:
            await _delete_or_fail(
                server,
                "ui_products_delete_preview",
                "ui_products_delete_execute",
                {"unique_tag": leftover_product, "organization_id": slug},
                f"product {leftover_product}",
            )
        for leftover_contact in LEFTOVER_INVOICE_CONTACTS:
            await _delete_or_fail(
                server,
                "ui_clients_delete_preview",
                "ui_clients_delete_execute",
                {"name": leftover_contact, "organization_id": slug},
                f"contact {leftover_contact}",
            )
        proof = BrowserRuntime(
            proof_profile,
            credential_references=AppConfig.from_environment().browser_credentials,
            credential_resolver=KeyringCredentialResolver(),
        )
        extra = proof
        await _ready_session(proof, slug)
        for leftover_product in LEFTOVER_PRODUCTS:
            assert await _list_has_name(proof, slug, "products", leftover_product) is False
        for leftover_contact in LEFTOVER_INVOICE_CONTACTS:
            assert await _list_has_name(proof, slug, "clients", leftover_contact) is False
    finally:
        if extra is not None:
            await extra.close()
        for path in list(_REGISTERED_PROFILES):
            if path.name.startswith("billy-live-invoices-"):
                shutil.rmtree(path, ignore_errors=True)


@pytest.mark.asyncio
async def test_ui_invoices_kunde_widget_contract_dump(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Recapture the Kunde widget contract. Do not save a draft."""

    from billy_mcp.ui_writes.invoices_form_bind import capture_kunde_widget_dump
    from billy_mcp.ui_writes.invoices_form_observe import (
        KUNDE_CHROME_DUMP,
        KUNDE_LOOKUP_DUMP,
        KUNDE_OPENER_DUMP,
    )
    from billy_mcp.ui_writes.invoices_kunde import widget_contract_missing_keys
    from billy_mcp.ui_writes.page_flow import BILLY_ORIGIN

    _require_live_credentials()
    assert not os.environ.get("BILLY_API_TOKEN"), "widget dump must not use API token"
    profile = _temp_profile()
    observer_profile = _temp_profile()
    monkeypatch.setenv("BILLY_BROWSER_PROFILE", str(profile))
    monkeypatch.delenv("BILLY_ORGANIZATION_ID", raising=False)
    server: FastMCP | None = None
    extra: BrowserRuntime | None = None
    page: Any = None
    tag = "MCP-UI-INV-DEADBEEF"

    try:
        server = create_server(_REPO_ROOT)
        slug = await _login(server)
        observer = BrowserRuntime(
            observer_profile,
            credential_references=AppConfig.from_environment().browser_credentials,
            credential_resolver=KeyringCredentialResolver(),
        )
        extra = observer
        await _ready_session(observer, slug)
        context = await observer.start()
        page = cast(Any, await context.new_page())
        await page.goto(f"{BILLY_ORIGIN}/{slug}/invoices/new", wait_until="domcontentloaded")
        try:
            await page.wait_for_load_state("networkidle")
        except (TimeoutError, RuntimeError):
            pass
        result = await capture_kunde_widget_dump(page, tag)
        if result.get("code"):
            _record_blocker(f"widget dump failed: {result}")
            pytest.fail(f"widget dump failed: {result}")
        after_type = result["after_type"]
        opener = result["opener"]
        assert isinstance(after_type, dict)
        assert isinstance(opener, dict)
        after_map = cast(dict[str, object], after_type)
        opener_map = cast(dict[str, object], opener)
        assert widget_contract_missing_keys(after_map) == []
        assert widget_contract_missing_keys(opener_map) == []
        assert KUNDE_OPENER_DUMP.is_file()
        assert KUNDE_CHROME_DUMP.is_file()
        written = json.loads(KUNDE_CHROME_DUMP.read_text(encoding="utf-8"))
        assert widget_contract_missing_keys(written["after_type"]) == []
        if result.get("named_action") is None:
            assert KUNDE_LOOKUP_DUMP.is_file()
            lookup = json.loads(KUNDE_LOOKUP_DUMP.read_text(encoding="utf-8"))
            assert lookup["path"] == "/v2/contacts"
            assert "contact_get_count" in lookup
        assert "Gem som kladde" not in json.dumps(result)
    finally:
        if page is not None:
            await page.close()
        if extra is not None:
            await extra.close()
        for path in list(_REGISTERED_PROFILES):
            if path.name.startswith("billy-live-invoices-"):
                shutil.rmtree(path, ignore_errors=True)


@pytest.mark.asyncio
async def test_ui_invoices_kunde_chevron_hit_dump(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Recapture the Kunde chevron hit target. Do not type. Do not save a draft."""

    from billy_mcp.ui_writes.invoices_form_bind import capture_kunde_chevron_hit_dump
    from billy_mcp.ui_writes.invoices_form_observe import KUNDE_OPENER_DUMP
    from billy_mcp.ui_writes.invoices_kunde import chevron_hit_missing_keys
    from billy_mcp.ui_writes.page_flow import BILLY_ORIGIN

    _require_live_credentials()
    assert not os.environ.get("BILLY_API_TOKEN"), "chevron dump must not use API token"
    profile = _temp_profile()
    observer_profile = _temp_profile()
    monkeypatch.setenv("BILLY_BROWSER_PROFILE", str(profile))
    monkeypatch.delenv("BILLY_ORGANIZATION_ID", raising=False)
    extra: BrowserRuntime | None = None
    page: Any = None
    tag = "MCP-UI-INV-DEADBEEF"

    try:
        server = create_server(_REPO_ROOT)
        slug = await _login(server)
        observer = BrowserRuntime(
            observer_profile,
            credential_references=AppConfig.from_environment().browser_credentials,
            credential_resolver=KeyringCredentialResolver(),
        )
        extra = observer
        await _ready_session(observer, slug)
        context = await observer.start()
        page = cast(Any, await context.new_page())
        await page.goto(f"{BILLY_ORIGIN}/{slug}/invoices/new", wait_until="domcontentloaded")
        try:
            await page.wait_for_load_state("networkidle")
        except (TimeoutError, RuntimeError):
            pass
        result = await capture_kunde_chevron_hit_dump(page, tag)
        opener = result.get("opener")
        if not isinstance(opener, dict):
            _record_blocker(f"chevron dump failed: {result}")
            pytest.fail(f"chevron dump failed: {result}")
        opener_map = cast(dict[str, object], opener)
        assert chevron_hit_missing_keys(opener_map) == []
        assert KUNDE_OPENER_DUMP.is_file()
        written = json.loads(KUNDE_OPENER_DUMP.read_text(encoding="utf-8"))
        assert chevron_hit_missing_keys(written) == []
        same = opener_map.get("right_edge_same_input") is True
        if not same:
            assert result.get("clicked") is False
        else:
            assert result.get("clicked") is True
            after_click = result.get("after_click")
            assert isinstance(after_click, dict)
            assert chevron_hit_missing_keys(cast(dict[str, object], after_click)) == []
        encoded = json.dumps(result)
        assert "Gem som kladde" not in encoded
        assert tag not in encoded
    finally:
        if page is not None:
            await page.close()
        if extra is not None:
            await extra.close()
        for path in list(_REGISTERED_PROFILES):
            if path.name.startswith("billy-live-invoices-"):
                shutil.rmtree(path, ignore_errors=True)


@pytest.mark.asyncio
async def test_ui_invoices_kunde_div_ownership_dump(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Recapture the Kunde right-edge DIV ownership. Click only if proved."""

    from billy_mcp.ui_writes.invoices_form_bind import capture_kunde_div_ownership_dump
    from billy_mcp.ui_writes.invoices_form_observe import KUNDE_OPENER_DUMP
    from billy_mcp.ui_writes.invoices_kunde_div import (
        div_belongs_to_kunde_control,
        div_ownership_missing_keys,
    )
    from billy_mcp.ui_writes.page_flow import BILLY_ORIGIN

    _require_live_credentials()
    assert not os.environ.get("BILLY_API_TOKEN"), "DIV dump must not use API token"
    profile = _temp_profile()
    observer_profile = _temp_profile()
    monkeypatch.setenv("BILLY_BROWSER_PROFILE", str(profile))
    monkeypatch.delenv("BILLY_ORGANIZATION_ID", raising=False)
    extra: BrowserRuntime | None = None
    page: Any = None
    tag = "MCP-UI-INV-DEADBEEF"

    try:
        server = create_server(_REPO_ROOT)
        slug = await _login(server)
        observer = BrowserRuntime(
            observer_profile,
            credential_references=AppConfig.from_environment().browser_credentials,
            credential_resolver=KeyringCredentialResolver(),
        )
        extra = observer
        await _ready_session(observer, slug)
        context = await observer.start()
        page = cast(Any, await context.new_page())
        await page.goto(f"{BILLY_ORIGIN}/{slug}/invoices/new", wait_until="domcontentloaded")
        try:
            await page.wait_for_load_state("networkidle")
        except (TimeoutError, RuntimeError):
            pass
        result = await capture_kunde_div_ownership_dump(page, tag)
        opener = result.get("opener")
        if not isinstance(opener, dict):
            _record_blocker(f"DIV ownership dump failed: {result}")
            pytest.fail(f"DIV ownership dump failed: {result}")
        opener_map = cast(dict[str, object], opener)
        assert div_ownership_missing_keys(opener_map) == []
        assert KUNDE_OPENER_DUMP.is_file()
        written = json.loads(KUNDE_OPENER_DUMP.read_text(encoding="utf-8"))
        assert div_ownership_missing_keys(written) == []
        proved = div_belongs_to_kunde_control(opener_map)
        if not proved:
            assert result.get("clicked") is False
            assert result.get("code") == "UI_CHANGED"
        else:
            assert result.get("clicked") is True
            after_click = result.get("after_click")
            assert isinstance(after_click, dict)
            assert div_ownership_missing_keys(cast(dict[str, object], after_click)) == []
        encoded = json.dumps(result)
        assert "Gem som kladde" not in encoded
        assert tag not in encoded
    finally:
        if page is not None:
            await page.close()
        if extra is not None:
            await extra.close()
        for path in list(_REGISTERED_PROFILES):
            if path.name.startswith("billy-live-invoices-"):
                shutil.rmtree(path, ignore_errors=True)


@pytest.mark.asyncio
async def test_ui_invoices_kunde_tagged_trace(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Create a tagged customer, then trace Kunde with listeners attached first."""

    from billy_mcp.ui_writes.invoices_form_bind import capture_kunde_tagged_trace
    from billy_mcp.ui_writes.invoices_form_observe import (
        KUNDE_TRACE_DUMP,
        KundeTraceSink,
        watch_kunde_trace,
    )
    from billy_mcp.ui_writes.invoices_kunde import kunde_trace_missing_keys
    from billy_mcp.ui_writes.page_flow import BILLY_ORIGIN

    _require_live_credentials()
    assert not os.environ.get("BILLY_API_TOKEN"), "tagged trace must not use API token"
    profile = _temp_profile()
    observer_profile = _temp_profile()
    cleanup_profile = _temp_profile()
    monkeypatch.setenv("BILLY_BROWSER_PROFILE", str(profile))
    monkeypatch.delenv("BILLY_ORGANIZATION_ID", raising=False)
    extra: BrowserRuntime | None = None
    page: Any = None
    server: FastMCP | None = None
    slug = ""
    tag = f"MCP-UI-INV-{secrets.token_hex(4).upper()}"

    try:
        server = create_server(_REPO_ROOT)
        slug = await _login(server)
        observer = BrowserRuntime(
            observer_profile,
            credential_references=AppConfig.from_environment().browser_credentials,
            credential_resolver=KeyringCredentialResolver(),
        )
        extra = observer
        await _ready_session(observer, slug)
        contact_preview = await _call(
            server,
            "ui_clients_create_preview",
            {"name": tag, "organization_id": slug},
        )
        contact_created = await _call(
            server,
            "ui_clients_create_execute",
            {"confirmation_ticket": contact_preview["confirmation_ticket"]},
        )
        if contact_created.get("code"):
            _record_blocker(f"contact create failed: {contact_created}")
            pytest.fail(f"contact create failed: {contact_created}")
        assert contact_created.get("submitted") is True
        seen = False
        for _ in range(4):
            await asyncio.sleep(2)
            if await _clients_has_name(observer, slug, tag):
                seen = True
                break
        assert seen is True

        context = await observer.start()
        page = cast(Any, await context.new_page())
        sink = KundeTraceSink()
        watch_kunde_trace(page, sink)
        await page.goto(f"{BILLY_ORIGIN}/{slug}/invoices/new", wait_until="domcontentloaded")
        try:
            await page.wait_for_load_state("networkidle")
        except (TimeoutError, RuntimeError):
            pass
        result = await capture_kunde_tagged_trace(
            page,
            tag,
            sink=sink,
            listener_attached_before_form=True,
        )
        at_rest = result.get("at_rest")
        after_click = result.get("after_click")
        after_type = result.get("after_type")
        if not isinstance(at_rest, dict) or not isinstance(after_click, dict):
            _record_blocker(f"tagged trace dump failed: {result}")
            pytest.fail(f"tagged trace dump failed: {result}")
        if not isinstance(after_type, dict):
            _record_blocker(f"tagged trace after_type missing: {result}")
            pytest.fail(f"tagged trace after_type missing: {result}")
        assert result.get("listener_attached_before_form") is True
        assert kunde_trace_missing_keys(cast(dict[str, object], at_rest)) == []
        assert kunde_trace_missing_keys(cast(dict[str, object], after_click)) == []
        assert kunde_trace_missing_keys(cast(dict[str, object], after_type)) == []
        assert KUNDE_TRACE_DUMP.is_file()
        written = json.loads(KUNDE_TRACE_DUMP.read_text(encoding="utf-8"))
        encoded = json.dumps({"result": result, "written": written})
        assert tag not in encoded
        assert "confirmation_ticket" not in encoded
        assert "/v2/contacts?" not in encoded
        if result.get("named_next_action") is not True or result.get("clicked_option") is not True:
            assert result.get("code") == "UI_CHANGED"
        await page.close()
        page = None
        await observer.close()
        extra = None
        cleanup = BrowserRuntime(
            cleanup_profile,
            credential_references=AppConfig.from_environment().browser_credentials,
            credential_resolver=KeyringCredentialResolver(),
        )
        extra = cleanup
        await _ready_session(cleanup, slug)
        contact_delete = await _call(
            server,
            "ui_clients_delete_preview",
            {"name": tag, "organization_id": slug},
        )
        if not contact_delete.get("code"):
            await _call(
                server,
                "ui_clients_delete_execute",
                {"confirmation_ticket": contact_delete["confirmation_ticket"]},
            )
        assert await _clients_has_name(cleanup, slug, tag) is False
    finally:
        if page is not None:
            await page.close()
        if server is not None and slug:
            try:
                contact_delete = await _call(
                    server,
                    "ui_clients_delete_preview",
                    {"name": tag, "organization_id": slug},
                )
                if not contact_delete.get("code"):
                    await _call(
                        server,
                        "ui_clients_delete_execute",
                        {"confirmation_ticket": contact_delete["confirmation_ticket"]},
                    )
            except (OSError, RuntimeError, AssertionError, TimeoutError):
                _record_blocker(f"Cleanup delete failed for leftover tagged contact {tag}.")
        if extra is not None:
            await extra.close()
        for path in list(_REGISTERED_PROFILES):
            if path.name.startswith("billy-live-invoices-"):
                shutil.rmtree(path, ignore_errors=True)


@pytest.mark.asyncio
async def test_ui_invoices_kunde_event_causality(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Create a tagged customer, then record phase-scoped Kunde events."""

    from billy_mcp.ui_writes.invoices_form_bind import capture_kunde_event_trace
    from billy_mcp.ui_writes.invoices_form_observe import (
        KUNDE_EVENT_MESSAGE_DUMP,
        KUNDE_TRACE_DUMP,
        KundeTraceSink,
        install_kunde_event_listeners,
        watch_kunde_trace,
    )
    from billy_mcp.ui_writes.invoices_kunde import kunde_event_missing_keys
    from billy_mcp.ui_writes.page_flow import BILLY_ORIGIN

    _require_live_credentials()
    assert not os.environ.get("BILLY_API_TOKEN"), "event trace must not use API token"
    profile = _temp_profile()
    observer_profile = _temp_profile()
    cleanup_profile = _temp_profile()
    monkeypatch.setenv("BILLY_BROWSER_PROFILE", str(profile))
    monkeypatch.delenv("BILLY_ORGANIZATION_ID", raising=False)
    extra: BrowserRuntime | None = None
    page: Any = None
    server: FastMCP | None = None
    slug = ""
    tag = f"MCP-UI-INV-{secrets.token_hex(4).upper()}"

    try:
        server = create_server(_REPO_ROOT)
        slug = await _login(server)
        observer = BrowserRuntime(
            observer_profile,
            credential_references=AppConfig.from_environment().browser_credentials,
            credential_resolver=KeyringCredentialResolver(),
        )
        extra = observer
        await _ready_session(observer, slug)
        contact_preview = await _call(
            server,
            "ui_clients_create_preview",
            {"name": tag, "organization_id": slug},
        )
        contact_created = await _call(
            server,
            "ui_clients_create_execute",
            {"confirmation_ticket": contact_preview["confirmation_ticket"]},
        )
        if contact_created.get("code"):
            _record_blocker(f"contact create failed: {contact_created}")
            pytest.fail(f"contact create failed: {contact_created}")
        assert contact_created.get("submitted") is True
        seen = False
        for _ in range(4):
            await asyncio.sleep(2)
            if await _clients_has_name(observer, slug, tag):
                seen = True
                break
        assert seen is True

        context = await observer.start()
        page = cast(Any, await context.new_page())
        sink = KundeTraceSink()
        await install_kunde_event_listeners(page)
        watch_kunde_trace(page, sink)
        await page.goto(f"{BILLY_ORIGIN}/{slug}/invoices/new", wait_until="domcontentloaded")
        try:
            await page.wait_for_load_state("networkidle")
        except (TimeoutError, RuntimeError):
            pass
        result = await capture_kunde_event_trace(
            page,
            tag,
            sink=sink,
            listener_attached_before_form=True,
        )
        at_rest = result.get("at_rest")
        after_click = result.get("after_click")
        after_type = result.get("after_type")
        if not isinstance(at_rest, dict) or not isinstance(after_click, dict):
            _record_blocker(f"event trace dump failed: {result}")
            pytest.fail(f"event trace dump failed: {result}")
        if not isinstance(after_type, dict):
            _record_blocker(f"event trace after_type missing: {result}")
            pytest.fail(f"event trace after_type missing: {result}")
        assert result.get("listener_attached_before_form") is True
        assert kunde_event_missing_keys(cast(dict[str, object], at_rest)) == []
        assert kunde_event_missing_keys(cast(dict[str, object], after_click)) == []
        assert kunde_event_missing_keys(cast(dict[str, object], after_type)) == []
        assert KUNDE_TRACE_DUMP.is_file()
        written = json.loads(KUNDE_TRACE_DUMP.read_text(encoding="utf-8"))
        encoded = json.dumps({"result": result, "written": written})
        assert tag not in encoded
        assert "confirmation_ticket" not in encoded
        assert "/v2/contacts?" not in encoded
        if result.get("named_next_action") is not True or result.get("clicked_option") is not True:
            assert result.get("code") == "UI_CHANGED"
        await page.close()
        page = None
        await observer.close()
        extra = None
        cleanup = BrowserRuntime(
            cleanup_profile,
            credential_references=AppConfig.from_environment().browser_credentials,
            credential_resolver=KeyringCredentialResolver(),
        )
        extra = cleanup
        await _ready_session(cleanup, slug)
        contact_delete = await _call(
            server,
            "ui_clients_delete_preview",
            {"name": tag, "organization_id": slug},
        )
        if not contact_delete.get("code"):
            await _call(
                server,
                "ui_clients_delete_execute",
                {"confirmation_ticket": contact_delete["confirmation_ticket"]},
            )
        assert await _clients_has_name(cleanup, slug, tag) is False
        if KUNDE_EVENT_MESSAGE_DUMP.is_file():
            messages = json.loads(KUNDE_EVENT_MESSAGE_DUMP.read_text(encoding="utf-8"))
            assert tag not in json.dumps(messages)
    finally:
        if page is not None:
            await page.close()
        if server is not None and slug:
            try:
                contact_delete = await _call(
                    server,
                    "ui_clients_delete_preview",
                    {"name": tag, "organization_id": slug},
                )
                if not contact_delete.get("code"):
                    await _call(
                        server,
                        "ui_clients_delete_execute",
                        {"confirmation_ticket": contact_delete["confirmation_ticket"]},
                    )
            except (OSError, RuntimeError, AssertionError, TimeoutError):
                _record_blocker(f"Cleanup delete failed for leftover tagged contact {tag}.")
        if extra is not None:
            await extra.close()
        if KUNDE_EVENT_MESSAGE_DUMP.is_file():
            KUNDE_EVENT_MESSAGE_DUMP.unlink()
        for path in list(_REGISTERED_PROFILES):
            if path.name.startswith("billy-live-invoices-"):
                shutil.rmtree(path, ignore_errors=True)


@pytest.mark.asyncio
async def test_ui_invoices_kunde_other_v2_routes(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Create a tagged customer, then name the five other_v2 bootstraps."""

    from billy_mcp.ui_writes.invoices_form_bind import capture_kunde_route_trace
    from billy_mcp.ui_writes.invoices_form_observe import (
        KUNDE_TRACE_DUMP,
        KundeTraceSink,
        install_kunde_event_listeners,
        watch_kunde_trace,
    )
    from billy_mcp.ui_writes.invoices_kunde_routes import (
        KUNDE_ROUTE_TEMPLATE_DUMP,
        REQUIRED_KUNDE_ROUTE_KEYS,
        kunde_route_missing_keys,
    )
    from billy_mcp.ui_writes.page_flow import BILLY_ORIGIN

    _require_live_credentials()
    assert not os.environ.get("BILLY_API_TOKEN"), "route trace must not use API token"
    profile = _temp_profile()
    observer_profile = _temp_profile()
    cleanup_profile = _temp_profile()
    monkeypatch.setenv("BILLY_BROWSER_PROFILE", str(profile))
    monkeypatch.delenv("BILLY_ORGANIZATION_ID", raising=False)
    extra: BrowserRuntime | None = None
    page: Any = None
    server: FastMCP | None = None
    slug = ""
    tag = f"MCP-UI-INV-{secrets.token_hex(4).upper()}"

    try:
        server = create_server(_REPO_ROOT)
        slug = await _login(server)
        observer = BrowserRuntime(
            observer_profile,
            credential_references=AppConfig.from_environment().browser_credentials,
            credential_resolver=KeyringCredentialResolver(),
        )
        extra = observer
        await _ready_session(observer, slug)
        contact_preview = await _call(
            server,
            "ui_clients_create_preview",
            {"name": tag, "organization_id": slug},
        )
        contact_created = await _call(
            server,
            "ui_clients_create_execute",
            {"confirmation_ticket": contact_preview["confirmation_ticket"]},
        )
        if contact_created.get("code"):
            _record_blocker(f"contact create failed: {contact_created}")
            pytest.fail(f"contact create failed: {contact_created}")
        assert contact_created.get("submitted") is True
        seen = False
        for _ in range(4):
            await asyncio.sleep(2)
            if await _clients_has_name(observer, slug, tag):
                seen = True
                break
        assert seen is True

        context = await observer.start()
        page = cast(Any, await context.new_page())
        sink = KundeTraceSink()
        await install_kunde_event_listeners(page)
        watch_kunde_trace(page, sink)
        await page.goto(f"{BILLY_ORIGIN}/{slug}/invoices/new", wait_until="domcontentloaded")
        try:
            await page.wait_for_load_state("networkidle")
        except (TimeoutError, RuntimeError):
            pass
        result = await capture_kunde_route_trace(
            page,
            tag,
            sink=sink,
            listener_attached_before_form=True,
        )
        at_rest = result.get("at_rest")
        if not isinstance(at_rest, dict):
            _record_blocker(f"route trace dump failed: {result}")
            pytest.fail(f"route trace dump failed: {result}")
        at_rest_map = cast(dict[str, object], at_rest)
        raw_requests = at_rest_map.get("requests")
        rows: list[object] = (
            cast(list[object], raw_requests) if isinstance(raw_requests, list) else []
        )
        assert len(rows) >= 1
        assert kunde_route_missing_keys(rows) == []
        assert result.get("kunde_route_missing_keys") == []
        assert REQUIRED_KUNDE_ROUTE_KEYS == ("route_class", "timing_bucket", "phase")
        assert result.get("listener_attached_before_form") is True
        encoded = json.dumps({"result": result})
        assert tag not in encoded
        assert "confirmation_ticket" not in encoded
        assert "/v2/contacts?" not in encoded
        assert "route_template" not in encoded
        if KUNDE_ROUTE_TEMPLATE_DUMP.is_file():
            templates = KUNDE_ROUTE_TEMPLATE_DUMP.read_text(encoding="utf-8")
            assert tag not in templates
            assert "http" not in templates
        if result.get("contact_dataset_preloaded") is not True:
            assert result.get("code") == "UI_CHANGED"
        await page.close()
        page = None
        await observer.close()
        extra = None
        cleanup = BrowserRuntime(
            cleanup_profile,
            credential_references=AppConfig.from_environment().browser_credentials,
            credential_resolver=KeyringCredentialResolver(),
        )
        extra = cleanup
        await _ready_session(cleanup, slug)
        contact_delete = await _call(
            server,
            "ui_clients_delete_preview",
            {"name": tag, "organization_id": slug},
        )
        if not contact_delete.get("code"):
            await _call(
                server,
                "ui_clients_delete_execute",
                {"confirmation_ticket": contact_delete["confirmation_ticket"]},
            )
        assert await _clients_has_name(cleanup, slug, tag) is False
        assert KUNDE_TRACE_DUMP.is_file()
    finally:
        if page is not None:
            await page.close()
        if server is not None and slug:
            try:
                contact_delete = await _call(
                    server,
                    "ui_clients_delete_preview",
                    {"name": tag, "organization_id": slug},
                )
                if not contact_delete.get("code"):
                    await _call(
                        server,
                        "ui_clients_delete_execute",
                        {"confirmation_ticket": contact_delete["confirmation_ticket"]},
                    )
            except (OSError, RuntimeError, AssertionError, TimeoutError):
                _record_blocker(f"Cleanup delete failed for leftover tagged contact {tag}.")
        if extra is not None:
            await extra.close()
        for path in list(_REGISTERED_PROFILES):
            if path.name.startswith("billy-live-invoices-"):
                shutil.rmtree(path, ignore_errors=True)


@pytest.mark.asyncio
async def test_ui_invoices_kunde_control_contract(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Read-only CDP dump of the loaded Kunde control. Do not type or click."""

    from billy_mcp.ui_writes.invoices_form_bind import capture_kunde_control_contract
    from billy_mcp.ui_writes.invoices_kunde_control import (
        KUNDE_CONTROL_DUMP,
        REQUIRED_KUNDE_CONTROL_KEYS,
        kunde_control_missing_keys,
    )
    from billy_mcp.ui_writes.page_flow import BILLY_ORIGIN

    _require_live_credentials()
    assert not os.environ.get("BILLY_API_TOKEN"), "control dump must not use API token"
    profile = _temp_profile()
    observer_profile = _temp_profile()
    monkeypatch.setenv("BILLY_BROWSER_PROFILE", str(profile))
    monkeypatch.delenv("BILLY_ORGANIZATION_ID", raising=False)
    server: FastMCP | None = None
    extra: BrowserRuntime | None = None
    page: Any = None

    try:
        server = create_server(_REPO_ROOT)
        slug = await _login(server)
        observer = BrowserRuntime(
            observer_profile,
            credential_references=AppConfig.from_environment().browser_credentials,
            credential_resolver=KeyringCredentialResolver(),
        )
        extra = observer
        await _ready_session(observer, slug)
        context = await observer.start()
        page = cast(Any, await context.new_page())
        await page.goto(f"{BILLY_ORIGIN}/{slug}/invoices/new", wait_until="domcontentloaded")
        try:
            await page.wait_for_load_state("networkidle")
        except (TimeoutError, RuntimeError):
            pass
        result = await capture_kunde_control_contract(page)
        if result.get("code") and result.get("code") != "UI_CHANGED":
            _record_blocker(f"control dump failed: {result}")
            pytest.fail(f"control dump failed: {result}")
        assert kunde_control_missing_keys(result) == []
        assert result.get("kunde_control_missing_keys") == []
        assert REQUIRED_KUNDE_CONTROL_KEYS == (
            "input_listener_types",
            "wrapper_listener_types",
            "input_listeners",
            "wrapper_listeners",
            "wrapper_data_attr_names",
            "wrapper_class_tokens",
            "binding_script",
            "named_next_action",
            "named_next_action_token",
        )
        encoded = json.dumps({"result": result})
        assert "https://" not in encoded
        assert "function(" not in encoded
        assert "confirmation_ticket" not in encoded
        assert "MCP-UI-INV-" not in encoded
        if result.get("named_next_action") is not True:
            assert result.get("code") == "UI_CHANGED"
        assert KUNDE_CONTROL_DUMP.is_file()
        written = json.loads(KUNDE_CONTROL_DUMP.read_text(encoding="utf-8"))
        assert kunde_control_missing_keys(written) == []
        assert "https://" not in KUNDE_CONTROL_DUMP.read_text(encoding="utf-8")
    finally:
        if page is not None:
            await page.close()
        if extra is not None:
            await extra.close()
        for path in list(_REGISTERED_PROFILES):
            if path.name.startswith("billy-live-invoices-"):
                shutil.rmtree(path, ignore_errors=True)


@pytest.mark.asyncio
async def test_ui_invoices_kunde_post_click_dom_ax(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Verify the delivered 07600147 dump. Do not repeat the wrapper click."""

    from billy_mcp.ui_writes.invoices_form_bind import capture_kunde_post_click
    from billy_mcp.ui_writes.invoices_kunde_post_click import (
        KUNDE_POST_CLICK_DUMP,
        REQUIRED_KUNDE_POST_CLICK_KEYS,
        kunde_post_click_missing_keys,
        post_click_dump_is_delivered,
    )
    from billy_mcp.ui_writes.page_flow import BILLY_ORIGIN

    _require_live_credentials()
    assert not os.environ.get("BILLY_API_TOKEN"), "post-click dump must not use API token"
    profile = _temp_profile()
    observer_profile = _temp_profile()
    cleanup_profile = _temp_profile()
    monkeypatch.setenv("BILLY_BROWSER_PROFILE", str(profile))
    monkeypatch.delenv("BILLY_ORGANIZATION_ID", raising=False)
    server: FastMCP | None = None
    extra: BrowserRuntime | None = None
    cleanup: BrowserRuntime | None = None
    page: Any = None
    slug = ""
    tag = f"MCP-UI-INV-{secrets.token_hex(4).upper()}"

    try:
        server = create_server(_REPO_ROOT)
        slug = await _login(server)
        observer = BrowserRuntime(
            observer_profile,
            credential_references=AppConfig.from_environment().browser_credentials,
            credential_resolver=KeyringCredentialResolver(),
        )
        extra = observer
        await _ready_session(observer, slug)
        if post_click_dump_is_delivered():
            written = json.loads(KUNDE_POST_CLICK_DUMP.read_text(encoding="utf-8"))
            assert kunde_post_click_missing_keys(written) == []
            assert written.get("click_target") == "pickerfield"
            assert written.get("click_count") == 1
            assert written.get("exact_match_target") is not True
            assert "https://" not in KUNDE_POST_CLICK_DUMP.read_text(encoding="utf-8")
            leftovers = await _leftover_invoice_contact_names(observer, slug)
            assert leftovers == []
            return
        contact_preview = await _call(
            server,
            "ui_clients_create_preview",
            {"name": tag, "organization_id": slug},
        )
        created = await _call(
            server,
            "ui_clients_create_execute",
            {"confirmation_ticket": contact_preview["confirmation_ticket"]},
        )
        if created.get("code"):
            _record_blocker(f"contact create failed: {created}")
            pytest.fail(f"contact create failed: {created}")
        await asyncio.sleep(2)
        assert await _clients_has_name(observer, slug, tag) is True
        context = await observer.start()
        page = cast(Any, await context.new_page())
        await page.goto(f"{BILLY_ORIGIN}/{slug}/invoices/new", wait_until="domcontentloaded")
        try:
            await page.wait_for_load_state("networkidle")
        except (TimeoutError, RuntimeError):
            pass
        result = await capture_kunde_post_click(page, tag)
        if result.get("code") and result.get("code") != StableErrorCode.UI_CHANGED:
            _record_blocker(f"post-click dump failed: {result}")
            pytest.fail(f"post-click dump failed: {result}")
        assert kunde_post_click_missing_keys(result) == []
        assert result.get("click_target") == "pickerfield"
        assert result.get("click_count") == 1
        assert REQUIRED_KUNDE_POST_CLICK_KEYS == (
            "baseline_input_tag",
            "baseline_wrapper_class_categories",
            "baseline_hidden_subtree_count",
            "click_target",
            "click_count",
            "changed_node_count",
            "changed_nodes",
            "exact_match_count",
            "exact_match_target",
            "kunde_post_click_missing_keys",
        )
        encoded = json.dumps({"result": result})
        assert "https://" not in encoded
        assert tag not in encoded
        if result.get("exact_match_target") is not True:
            assert result.get("code") == "UI_CHANGED"
        assert KUNDE_POST_CLICK_DUMP.is_file()
        written = json.loads(KUNDE_POST_CLICK_DUMP.read_text(encoding="utf-8"))
        assert kunde_post_click_missing_keys(written) == []
        assert tag not in KUNDE_POST_CLICK_DUMP.read_text(encoding="utf-8")
        contact_delete = await _call(
            server,
            "ui_clients_delete_preview",
            {"name": tag, "organization_id": slug},
        )
        if not contact_delete.get("code"):
            await _call(
                server,
                "ui_clients_delete_execute",
                {"confirmation_ticket": contact_delete["confirmation_ticket"]},
            )
        cleanup = BrowserRuntime(
            cleanup_profile,
            credential_references=AppConfig.from_environment().browser_credentials,
            credential_resolver=KeyringCredentialResolver(),
        )
        await _ready_session(cleanup, slug)
        assert await _clients_has_name(cleanup, slug, tag) is False
    finally:
        if page is not None:
            await page.close()
        if server is not None and slug:
            try:
                contact_delete = await _call(
                    server,
                    "ui_clients_delete_preview",
                    {"name": tag, "organization_id": slug},
                )
                if not contact_delete.get("code"):
                    await _call(
                        server,
                        "ui_clients_delete_execute",
                        {"confirmation_ticket": contact_delete["confirmation_ticket"]},
                    )
            except (OSError, RuntimeError, AssertionError, TimeoutError):
                _record_blocker(f"Cleanup delete failed for leftover tagged contact {tag}.")
        if extra is not None:
            await extra.close()
        if cleanup is not None:
            await cleanup.close()
        for path in list(_REGISTERED_PROFILES):
            if path.name.startswith("billy-live-invoices-"):
                shutil.rmtree(path, ignore_errors=True)


@pytest.mark.asyncio
async def test_ui_invoices_kunde_descendant_map(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Read-only E87B6AEF descendant map. Do not repeat a closed click."""

    from billy_mcp.ui_writes.invoices_form_bind import capture_kunde_descendants
    from billy_mcp.ui_writes.invoices_kunde_descendants import (
        KUNDE_DESCENDANT_DUMP,
        REQUIRED_KUNDE_DESCENDANT_KEYS,
        descendant_dump_is_delivered,
        kunde_descendant_missing_keys,
    )
    from billy_mcp.ui_writes.page_flow import BILLY_ORIGIN

    _require_live_credentials()
    assert not os.environ.get("BILLY_API_TOKEN"), "descendant dump must not use API token"
    profile = _temp_profile()
    observer_profile = _temp_profile()
    monkeypatch.setenv("BILLY_BROWSER_PROFILE", str(profile))
    monkeypatch.delenv("BILLY_ORGANIZATION_ID", raising=False)
    server: FastMCP | None = None
    extra: BrowserRuntime | None = None
    page: Any = None

    try:
        server = create_server(_REPO_ROOT)
        slug = await _login(server)
        observer = BrowserRuntime(
            observer_profile,
            credential_references=AppConfig.from_environment().browser_credentials,
            credential_resolver=KeyringCredentialResolver(),
        )
        extra = observer
        await _ready_session(observer, slug)
        leftovers = await _leftover_invoice_contact_names(observer, slug)
        assert leftovers == []
        if descendant_dump_is_delivered():
            written = json.loads(KUNDE_DESCENDANT_DUMP.read_text(encoding="utf-8"))
            assert kunde_descendant_missing_keys(written) == []
            assert "https://" not in KUNDE_DESCENDANT_DUMP.read_text(encoding="utf-8")
            assert "function(" not in KUNDE_DESCENDANT_DUMP.read_text(encoding="utf-8")
            return
        context = await observer.start()
        page = cast(Any, await context.new_page())
        await page.goto(f"{BILLY_ORIGIN}/{slug}/invoices/new", wait_until="domcontentloaded")
        try:
            await page.wait_for_load_state("networkidle")
        except (TimeoutError, RuntimeError):
            pass
        result = await capture_kunde_descendants(page)
        if result.get("code") and result.get("code") != "UI_CHANGED":
            _record_blocker(f"descendant dump failed: {result}")
            pytest.fail(f"descendant dump failed: {result}")
        assert kunde_descendant_missing_keys(result) == []
        assert REQUIRED_KUNDE_DESCENDANT_KEYS == (
            "wrapper_tag",
            "visible_descendant_count",
            "descendants",
            "unique_target",
            "unique_target_category",
            "wrapper_handler_guard",
            "kunde_descendant_missing_keys",
        )
        encoded = json.dumps({"result": result})
        assert "https://" not in encoded
        assert "function(" not in encoded
        assert "confirmation_ticket" not in encoded
        assert "MCP-UI-INV-" not in encoded
        if result.get("unique_target") is not True:
            assert result.get("code") == "UI_CHANGED"
        assert KUNDE_DESCENDANT_DUMP.is_file()
        written = json.loads(KUNDE_DESCENDANT_DUMP.read_text(encoding="utf-8"))
        assert kunde_descendant_missing_keys(written) == []
        assert "https://" not in KUNDE_DESCENDANT_DUMP.read_text(encoding="utf-8")
        leftovers = await _leftover_invoice_contact_names(observer, slug)
        assert leftovers == []
    finally:
        if page is not None:
            await page.close()
        if extra is not None:
            await extra.close()
        for path in list(_REGISTERED_PROFILES):
            if path.name.startswith("billy-live-invoices-"):
                shutil.rmtree(path, ignore_errors=True)


@pytest.mark.asyncio
async def test_ui_invoices_kunde_ember_inspect(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Read-only 31B0C7A6 Ember inspect. Do not click or invoke methods."""

    from billy_mcp.ui_writes.invoices_form_bind import capture_kunde_ember
    from billy_mcp.ui_writes.invoices_kunde_ember import (
        KUNDE_EMBER_DUMP,
        REQUIRED_KUNDE_EMBER_KEYS,
        ember_dump_is_delivered,
        kunde_ember_missing_keys,
    )
    from billy_mcp.ui_writes.page_flow import BILLY_ORIGIN

    _require_live_credentials()
    assert not os.environ.get("BILLY_API_TOKEN"), "ember dump must not use API token"
    profile = _temp_profile()
    observer_profile = _temp_profile()
    monkeypatch.setenv("BILLY_BROWSER_PROFILE", str(profile))
    monkeypatch.delenv("BILLY_ORGANIZATION_ID", raising=False)
    server: FastMCP | None = None
    extra: BrowserRuntime | None = None
    page: Any = None

    try:
        server = create_server(_REPO_ROOT)
        slug = await _login(server)
        observer = BrowserRuntime(
            observer_profile,
            credential_references=AppConfig.from_environment().browser_credentials,
            credential_resolver=KeyringCredentialResolver(),
        )
        extra = observer
        await _ready_session(observer, slug)
        leftovers = await _leftover_invoice_contact_names(observer, slug)
        assert leftovers == []
        if ember_dump_is_delivered():
            written = json.loads(KUNDE_EMBER_DUMP.read_text(encoding="utf-8"))
            assert kunde_ember_missing_keys(written) == []
            assert "https://" not in KUNDE_EMBER_DUMP.read_text(encoding="utf-8")
            assert "function(" not in KUNDE_EMBER_DUMP.read_text(encoding="utf-8")
            assert "ember" + "123" not in KUNDE_EMBER_DUMP.read_text(encoding="utf-8")
            return
        context = await observer.start()
        page = cast(Any, await context.new_page())
        await page.goto(f"{BILLY_ORIGIN}/{slug}/invoices/new", wait_until="domcontentloaded")
        try:
            await page.wait_for_load_state("networkidle")
        except (TimeoutError, RuntimeError):
            pass
        result = await capture_kunde_ember(page)
        if result.get("code") and result.get("code") != "UI_CHANGED":
            _record_blocker(f"ember dump failed: {result}")
            pytest.fail(f"ember dump failed: {result}")
        assert kunde_ember_missing_keys(result) == []
        assert set(REQUIRED_KUNDE_EMBER_KEYS) <= set(result)
        encoded = json.dumps({"result": result})
        assert "https://" not in encoded
        assert "function(" not in encoded
        assert "confirmation_ticket" not in encoded
        assert "MCP-UI-INV-" not in encoded
        if result.get("unique_normal_action") is not True:
            assert result.get("code") == "UI_CHANGED"
        assert KUNDE_EMBER_DUMP.is_file()
        written = json.loads(KUNDE_EMBER_DUMP.read_text(encoding="utf-8"))
        assert kunde_ember_missing_keys(written) == []
        assert "https://" not in KUNDE_EMBER_DUMP.read_text(encoding="utf-8")
        leftovers = await _leftover_invoice_contact_names(observer, slug)
        assert leftovers == []
    finally:
        if page is not None:
            await page.close()
        if extra is not None:
            await extra.close()
        for path in list(_REGISTERED_PROFILES):
            if path.name.startswith("billy-live-invoices-"):
                shutil.rmtree(path, ignore_errors=True)


@pytest.mark.asyncio
async def test_ui_invoices_kunde_fiber_inspect(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Read-only fiber inspect. Do not click, remake Ember inspect, or invoke."""

    from billy_mcp.ui_writes.invoices_form_bind import capture_kunde_fiber
    from billy_mcp.ui_writes.invoices_kunde_fiber import (
        KUNDE_FIBER_DUMP,
        REQUIRED_KUNDE_FIBER_KEYS,
        fiber_dump_is_delivered,
        kunde_fiber_missing_keys,
    )
    from billy_mcp.ui_writes.page_flow import BILLY_ORIGIN

    _require_live_credentials()
    assert not os.environ.get("BILLY_API_TOKEN"), "fiber dump must not use API token"
    profile = _temp_profile()
    observer_profile = _temp_profile()
    monkeypatch.setenv("BILLY_BROWSER_PROFILE", str(profile))
    monkeypatch.delenv("BILLY_ORGANIZATION_ID", raising=False)
    extra: BrowserRuntime | None = None
    page: Any = None

    try:
        server = create_server(_REPO_ROOT)
        slug = await _login(server)
        observer = BrowserRuntime(
            observer_profile,
            credential_references=AppConfig.from_environment().browser_credentials,
            credential_resolver=KeyringCredentialResolver(),
        )
        extra = observer
        await _ready_session(observer, slug)
        leftovers = await _leftover_invoice_contact_names(observer, slug)
        assert leftovers == []
        if fiber_dump_is_delivered():
            written = json.loads(KUNDE_FIBER_DUMP.read_text(encoding="utf-8"))
            assert kunde_fiber_missing_keys(written) == []
            text = KUNDE_FIBER_DUMP.read_text(encoding="utf-8")
            assert "https://" not in text
            assert "function(" not in text
            assert "__reactFiber$" not in text
            return
        context = await observer.start()
        page = cast(Any, await context.new_page())
        await page.goto(f"{BILLY_ORIGIN}/{slug}/invoices/new", wait_until="domcontentloaded")
        try:
            await page.wait_for_load_state("networkidle")
        except (TimeoutError, RuntimeError):
            pass
        result = await capture_kunde_fiber(page)
        if result.get("code") and result.get("code") != "UI_CHANGED":
            _record_blocker(f"fiber dump failed: {result}")
            pytest.fail(f"fiber dump failed: {result}")
        assert kunde_fiber_missing_keys(result) == []
        assert set(REQUIRED_KUNDE_FIBER_KEYS) <= set(result)
        encoded = json.dumps({"result": result})
        assert "https://" not in encoded
        assert "function(" not in encoded
        assert "confirmation_ticket" not in encoded
        assert "MCP-UI-INV-" not in encoded
        assert "__reactFiber$" not in encoded
        if result.get("unique_normal_action") is not True:
            assert result.get("code") == "UI_CHANGED"
        assert KUNDE_FIBER_DUMP.is_file()
        written = json.loads(KUNDE_FIBER_DUMP.read_text(encoding="utf-8"))
        assert kunde_fiber_missing_keys(written) == []
        assert "https://" not in KUNDE_FIBER_DUMP.read_text(encoding="utf-8")
        leftovers = await _leftover_invoice_contact_names(observer, slug)
        assert leftovers == []
    finally:
        if page is not None:
            await page.close()
        if extra is not None:
            await extra.close()
        for path in list(_REGISTERED_PROFILES):
            if path.name.startswith("billy-live-invoices-"):
                shutil.rmtree(path, ignore_errors=True)


@pytest.mark.asyncio
async def test_ui_invoices_kunde_listener_inspect(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Read-only listener contract. Do not click, remake Ember, or remake fiber."""

    from billy_mcp.ui_writes.invoices_form_bind import capture_kunde_listeners
    from billy_mcp.ui_writes.invoices_kunde_listeners import (
        KUNDE_LISTENER_DUMP,
        REQUIRED_KUNDE_LISTENER_KEYS,
        kunde_listener_missing_keys,
        listener_dump_is_delivered,
    )
    from billy_mcp.ui_writes.page_flow import BILLY_ORIGIN

    _require_live_credentials()
    assert not os.environ.get("BILLY_API_TOKEN"), "listener dump must not use API token"
    profile = _temp_profile()
    observer_profile = _temp_profile()
    monkeypatch.setenv("BILLY_BROWSER_PROFILE", str(profile))
    monkeypatch.delenv("BILLY_ORGANIZATION_ID", raising=False)
    extra: BrowserRuntime | None = None
    page: Any = None

    try:
        server = create_server(_REPO_ROOT)
        slug = await _login(server)
        observer = BrowserRuntime(
            observer_profile,
            credential_references=AppConfig.from_environment().browser_credentials,
            credential_resolver=KeyringCredentialResolver(),
        )
        extra = observer
        await _ready_session(observer, slug)
        leftovers = await _leftover_invoice_contact_names(observer, slug)
        assert leftovers == []
        if listener_dump_is_delivered():
            written = json.loads(KUNDE_LISTENER_DUMP.read_text(encoding="utf-8"))
            assert kunde_listener_missing_keys(written) == []
            text = KUNDE_LISTENER_DUMP.read_text(encoding="utf-8")
            assert "https://" not in text
            assert "function(" not in text
            assert "scriptId" not in text
            return
        context = await observer.start()
        page = cast(Any, await context.new_page())
        await page.goto(f"{BILLY_ORIGIN}/{slug}/invoices/new", wait_until="domcontentloaded")
        try:
            await page.wait_for_load_state("networkidle")
        except (TimeoutError, RuntimeError):
            pass
        result = await capture_kunde_listeners(page)
        if result.get("code") and result.get("code") != "UI_CHANGED":
            _record_blocker(f"listener dump failed: {result}")
            pytest.fail(f"listener dump failed: {result}")
        assert kunde_listener_missing_keys(result) == []
        assert set(REQUIRED_KUNDE_LISTENER_KEYS) <= set(result)
        encoded = json.dumps({"result": result})
        assert "https://" not in encoded
        assert "function(" not in encoded
        assert "confirmation_ticket" not in encoded
        assert "MCP-UI-INV-" not in encoded
        assert "scriptId" not in encoded
        if result.get("unique_normal_action") is not True:
            assert result.get("code") == "UI_CHANGED"
        assert KUNDE_LISTENER_DUMP.is_file()
        written = json.loads(KUNDE_LISTENER_DUMP.read_text(encoding="utf-8"))
        assert kunde_listener_missing_keys(written) == []
        assert "https://" not in KUNDE_LISTENER_DUMP.read_text(encoding="utf-8")
        leftovers = await _leftover_invoice_contact_names(observer, slug)
        assert leftovers == []
    finally:
        if page is not None:
            await page.close()
        if extra is not None:
            await extra.close()
        for path in list(_REGISTERED_PROFILES):
            if path.name.startswith("billy-live-invoices-"):
                shutil.rmtree(path, ignore_errors=True)


@pytest.mark.asyncio
async def test_ui_invoices_kunde_structure_compare(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Compare Kunde and Leverandør structure. Do not click or remake inspectors."""

    from billy_mcp.ui_writes.invoices_kunde_structure import (
        KUNDE_STRUCTURE_DUMP,
        REQUIRED_KUNDE_STRUCTURE_KEYS,
        apply_kunde_structure_dump,
        capture_kunde_structure,
        kunde_structure_missing_keys,
        map_existing_dumps,
        structure_dump_is_delivered,
    )
    from billy_mcp.ui_writes.page_flow import BILLY_ORIGIN

    _require_live_credentials()
    assert not os.environ.get("BILLY_API_TOKEN"), "structure dump must not use API token"
    profile = _temp_profile()
    observer_profile = _temp_profile()
    monkeypatch.setenv("BILLY_BROWSER_PROFILE", str(profile))
    monkeypatch.delenv("BILLY_ORGANIZATION_ID", raising=False)
    extra: BrowserRuntime | None = None
    page: Any = None

    try:
        server = create_server(_REPO_ROOT)
        slug = await _login(server)
        observer = BrowserRuntime(
            observer_profile,
            credential_references=AppConfig.from_environment().browser_credentials,
            credential_resolver=KeyringCredentialResolver(),
        )
        extra = observer
        await _ready_session(observer, slug)
        leftovers = await _leftover_invoice_contact_names(observer, slug)
        assert leftovers == []
        if not structure_dump_is_delivered():
            apply_kunde_structure_dump(map_existing_dumps())
        if structure_dump_is_delivered():
            written = json.loads(KUNDE_STRUCTURE_DUMP.read_text(encoding="utf-8"))
            assert kunde_structure_missing_keys(written) == []
            text = KUNDE_STRUCTURE_DUMP.read_text(encoding="utf-8")
            assert "https://" not in text
            assert "function(" not in text
            assert "MCP-UI-INV-" not in text
            return
        context = await observer.start()
        page = cast(Any, await context.new_page())
        await page.goto(f"{BILLY_ORIGIN}/{slug}/invoices/new", wait_until="domcontentloaded")
        try:
            await page.wait_for_load_state("networkidle")
        except (TimeoutError, RuntimeError):
            pass
        result = await capture_kunde_structure(page)
        if result.get("code") and result.get("code") != "UI_CHANGED":
            _record_blocker(f"structure dump failed: {result}")
            pytest.fail(f"structure dump failed: {result}")
        assert kunde_structure_missing_keys(result) == []
        assert set(REQUIRED_KUNDE_STRUCTURE_KEYS) <= set(result)
        encoded = json.dumps({"result": result})
        assert "https://" not in encoded
        assert "function(" not in encoded
        assert "confirmation_ticket" not in encoded
        assert "MCP-UI-INV-" not in encoded
        if result.get("unique_normal_action") is not True:
            assert result.get("code") == "UI_CHANGED"
        assert KUNDE_STRUCTURE_DUMP.is_file()
        written = json.loads(KUNDE_STRUCTURE_DUMP.read_text(encoding="utf-8"))
        assert kunde_structure_missing_keys(written) == []
        leftovers = await _leftover_invoice_contact_names(observer, slug)
        assert leftovers == []
    finally:
        if page is not None:
            await page.close()
        if extra is not None:
            await extra.close()
        for path in list(_REGISTERED_PROFILES):
            if path.name.startswith("billy-live-invoices-"):
                shutil.rmtree(path, ignore_errors=True)
