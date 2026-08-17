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
from urllib.parse import urlsplit

import pytest
from fastmcp import FastMCP

from billy_mcp.browser import BrowserRuntime
from billy_mcp.config import AppConfig
from billy_mcp.credentials import KeyringCredentialResolver
from billy_mcp.models import AuthLoginWaitSuccess, StableErrorCode, ToolError
from billy_mcp.server import create_server
from billy_mcp.ui_writes import invoices_form
from billy_mcp.ui_writes.invoices_form_page import CREATE_PERSIST_DUMP
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
_INVOICE_ID_RE = re.compile(r"/invoices/([^/]+)(?:/edit)?$")
_LEFTOVER_CONTACT_RE = re.compile(r"MCP-UI-INV-[0-9A-F]{8}")
_REGISTERED_PROFILES: list[Path] = []


def _credentials_configured() -> bool:
    return bool(
        os.environ.get("BILLY_BROWSER_PRIMARY_REFERENCE", "").strip()
        and os.environ.get("BILLY_BROWSER_SECONDARY_REFERENCE", "").strip()
    )


def _watched_rows(raw: object) -> list[str]:
    if not isinstance(raw, dict):
        return []
    typed = cast(dict[str, object], raw)
    watched = typed.get("watched")
    if not isinstance(watched, list):
        return []
    rows: list[str] = []
    for item in cast(list[object], watched):
        if isinstance(item, str):
            rows.append(item)
    return rows


def _record_blocker(reason: str) -> None:
    _BLOCKER_PATH.parent.mkdir(parents=True, exist_ok=True)
    _BLOCKER_PATH.write_text(reason.strip() + "\n", encoding="utf-8")


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


async def _open_named_list(page: Any, slug: str, path: str, name: str) -> None:
    await page.goto(f"https://mit.billy.dk/{slug}/{path}", wait_until="domcontentloaded")
    search = page.locator("input[type='search'], input[placeholder*='øg' i]")
    if await search.count() >= 1:
        await search.first.fill(name)


async def _list_has_name(runtime: BrowserRuntime, slug: str, path: str, name: str) -> bool:
    context = await runtime.start()
    page = cast(Any, await context.new_page())
    try:
        await _open_named_list(page, slug, path, name)
        body = await page.locator("body").inner_text()
        return exact_name_in_text(body, name)
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


async def _invoice_id_for_tag(runtime: BrowserRuntime, slug: str, name: str) -> str | None:
    context = await runtime.start()
    page = cast(Any, await context.new_page())
    try:
        await _open_named_list(page, slug, "invoices", name)
        links = page.locator("a[href*='/invoices/']")
        for index in range(await links.count()):
            href = await links.nth(index).get_attribute("href")
            if not isinstance(href, str) or not href:
                continue
            found = _INVOICE_ID_RE.search(str(urlsplit(href).path))
            if found is None or found.group(1) in {"new", "empty"}:
                continue
            return found.group(1)
        return None
    finally:
        await page.close()


async def _capture(runtime: BrowserRuntime, slug: str, destination: Path, name: str) -> None:
    context = await runtime.start()
    page = cast(Any, await context.new_page())
    try:
        await _open_named_list(page, slug, "invoices", name)
        await page.screenshot(path=str(destination), full_page=False)
        assert destination.is_file() and destination.stat().st_size > 0
    finally:
        await page.close()


@pytest.mark.asyncio
async def test_ui_invoices_create_update_delete_via_call_tool(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Create, update, and delete one tagged draft invoice through create_server."""

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
    invoice_id: str | None = None
    tag = f"MCP-UI-INV-{secrets.token_hex(4).upper()}"
    line = f"{tag} line"
    updated = f"{tag}-U"

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
        await asyncio.sleep(2)

        preview_create = await _call(
            server,
            "ui_invoices_create_preview",
            {
                "contact_name": tag,
                "line_description": line,
                "action": "draft_create",
                "save_cta": "Gem som kladde",
                "organization_id": slug,
            },
        )
        created_result = await _call(
            server,
            "ui_invoices_create_execute",
            {"confirmation_ticket": preview_create["confirmation_ticket"]},
        )
        if created_result.get("code"):
            _record_blocker(f"create execute failed: {created_result}")
            pytest.fail(f"create execute failed: {created_result}")
        assert created_result["submitted"] is True
        create_dump = json.loads(invoices_form.CREATE_PRE_SUBMIT_DUMP.read_text(encoding="utf-8"))
        assert create_dump["unique_tag"] == tag
        assert create_dump["customer"] == tag
        assert create_dump["line_description"] == line
        assert create_dump["draft_cta"] == "Gem som kladde"
        assert create_dump["vendor_bind"] == "scoped:existing_option"
        persist = json.loads(CREATE_PERSIST_DUMP.read_text(encoding="utf-8"))
        watched_rows = _watched_rows(persist)
        assert any(row.startswith("POST 2") and "/v2/invoices" in row for row in watched_rows)
        await _capture(observer, slug, frame_dir / "02_after_create.png", line)
        assert await _list_has_name(observer, slug, "invoices", line) is True
        invoice_id = await _invoice_id_for_tag(observer, slug, line)
        if not invoice_id:
            _record_blocker("independent invoices list did not yield an edit id")
            pytest.fail("independent invoices list did not yield an edit id")

        preview_update = await _call(
            server,
            "ui_invoices_update_preview",
            {
                "id": invoice_id,
                "line_description": updated,
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
        await _capture(observer, slug, frame_dir / "03_after_update.png", updated)
        assert await _list_has_name(observer, slug, "invoices", updated) is True
        assert await _list_has_name(observer, slug, "invoices", line) is False

        preview_delete = await _call(
            server,
            "ui_invoices_delete_preview",
            {
                "id": invoice_id,
                "action": "draft_delete",
                "save_cta": "Slet",
                "organization_id": slug,
            },
        )
        deleted_result = await _call(
            server,
            "ui_invoices_delete_execute",
            {"confirmation_ticket": preview_delete["confirmation_ticket"]},
        )
        if deleted_result.get("code"):
            _record_blocker(f"delete execute failed: {deleted_result}")
            pytest.fail(f"delete execute failed: {deleted_result}")
        assert deleted_result["submitted"] is True
        await observer.close()
        extra = None
        cleanup = BrowserRuntime(
            cleanup_profile,
            credential_references=AppConfig.from_environment().browser_credentials,
            credential_resolver=KeyringCredentialResolver(),
        )
        extra = cleanup
        await _ready_session(cleanup, slug)
        assert await _list_has_name(cleanup, slug, "invoices", updated) is False
        assert await _list_has_name(cleanup, slug, "invoices", line) is False

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
        assert await _list_has_name(cleanup, slug, "clients", tag) is False

        write_vision_record(
            _VISION_RECORD,
            workflow_ref="ui.parity.invoices.create",
            assertion_refs=[
                "tests/live/test_ui_invoices_writes.py::"
                "test_ui_invoices_create_update_delete_via_call_tool",
                "create_server_call_tool_create_update_delete",
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
            leftover_runtime = extra
            if leftover_runtime is not None:
                try:
                    leftovers = await _leftover_invoice_contact_names(leftover_runtime, slug)
                except (OSError, RuntimeError, AssertionError, TimeoutError):
                    leftovers = []
                for leftover in leftovers:
                    try:
                        preview = await _call(
                            server,
                            "ui_clients_delete_preview",
                            {"name": leftover, "organization_id": slug},
                        )
                        if not preview.get("code"):
                            await _call(
                                server,
                                "ui_clients_delete_execute",
                                {"confirmation_ticket": preview["confirmation_ticket"]},
                            )
                    except (OSError, RuntimeError, AssertionError, TimeoutError):
                        _record_blocker(
                            f"Cleanup delete failed for leftover tagged contact {leftover}."
                        )
            if invoice_id:
                try:
                    preview_delete = await _call(
                        server,
                        "ui_invoices_delete_preview",
                        {
                            "id": invoice_id,
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
                    _record_blocker(f"Cleanup delete failed for leftover tagged invoice {tag}.")
        if extra is not None:
            await extra.close()
        for path in list(_REGISTERED_PROFILES):
            if path.name.startswith("billy-live-invoices-"):
                shutil.rmtree(path, ignore_errors=True)
