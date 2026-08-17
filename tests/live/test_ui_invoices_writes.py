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
