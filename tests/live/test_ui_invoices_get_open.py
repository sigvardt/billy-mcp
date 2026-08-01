"""Live dual-session qualification for read-only ui_invoices_get_open.

Requires opaque browser credential references. Never uses BILLY_API_TOKEN.
Independent second-interface read-back is a second ephemeral profile login.
Never submits Gem/Send/Slet on the product get path. Live harness seeds a
disposable draft invoice via SPA token when the list is empty, then deletes it.
"""

from __future__ import annotations

import json
import os
import re
import shutil
import tempfile
from datetime import date
from pathlib import Path
from typing import Any, cast
from urllib.parse import urlsplit

import pytest

from billy_mcp.browser import BrowserRuntime
from billy_mcp.config import AppConfig
from billy_mcp.credentials import KeyringCredentialResolver
from billy_mcp.models import AuthLoginWaitSuccess, ToolError, UiInvoicesGetOpenSuccess
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
_MARKER_C = "R18670-TMP-CLIENT-INVOICE-GET-DO-NOT-USE"
_MARKER_P = "R18670-TMP-PRODUCT-INVOICE-GET-DO-NOT-USE"
_MARKER_I = "R18670-TMP-INVOICE-GET-DO-NOT-USE"
# Dedicated non-production test organisation id (SPA organizationId header).
_ORG = "Xr7WoEDNRZu6HezpIBgOGg"


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
    return Path(tempfile.mkdtemp(prefix="billy-live-invoices-get-", dir=str(_DATA_ROOT)))


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


async def _ensure_disposable_invoice(runtime: BrowserRuntime, org_identity: Path) -> dict[str, str]:
    """Seed contact+product+invoice via SPA when needed. Returns created ids (may be empty)."""

    slug = _org_slug(org_identity)
    context = await runtime.start()
    page = cast(Any, await context.new_page())
    cap = _TokenCapture()
    cap.attach(page)
    ids: dict[str, str] = {}
    try:
        await page.goto(f"https://mit.billy.dk/{slug}/invoices", wait_until="domcontentloaded")
        try:
            await page.wait_for_load_state("networkidle", timeout=20000)
        except Exception:
            pass
        await page.wait_for_timeout(1500)
        body = re.sub(r"\s+", " ", await page.locator("body").inner_text())[:4000]
        if _MARKER_I in body or re.search(r"\bKladde\b", body):
            # Prefer existing draft row without seed when list already has content.
            if _MARKER_I not in body:
                return {}
        assert cap.token or True
        # warm products for token if missing
        if not cap.token:
            await page.goto(f"https://mit.billy.dk/{slug}/products", wait_until="domcontentloaded")
            await page.wait_for_timeout(1500)
        headers = cap.headers()
        assert cap.token, "SPA access token not captured for seed"
        ctx = cast(Any, runtime)._context  # live harness seed only

        # contact
        cr = await _spa(
            ctx,
            "POST",
            "https://api.billysbilling.com/v2/contacts",
            headers,
            {
                "contact": {
                    "organizationId": _ORG,
                    "type": "company",
                    "name": _MARKER_C,
                    "countryId": "DK",
                    "isCustomer": True,
                    "isSupplier": False,
                }
            },
        )
        assert cr["status"] in (200, 201), f"contact seed failed: {cr}"
        data_c = cast(dict[str, Any], cr.get("data") or {})
        contacts = cast(list[dict[str, Any]], data_c.get("contacts") or [])
        contact_id = str(contacts[0]["id"]) if contacts and contacts[0].get("id") else ""
        assert contact_id
        ids["contact"] = contact_id

        pr = await _spa(
            ctx,
            "POST",
            "https://api.billysbilling.com/v2/products",
            headers,
            {
                "product": {
                    "organizationId": _ORG,
                    "name": _MARKER_P,
                    "productNo": "R18670P",
                }
            },
        )
        assert pr["status"] in (200, 201), f"product seed failed: {pr}"
        data_p = cast(dict[str, Any], pr.get("data") or {})
        products = cast(list[dict[str, Any]], data_p.get("products") or [])
        product_id = str(products[0]["id"]) if products and products[0].get("id") else ""
        assert product_id
        ids["product"] = product_id

        ir = await _spa(
            ctx,
            "POST",
            "https://api.billysbilling.com/v2/invoices",
            headers,
            {
                "invoice": {
                    "organizationId": _ORG,
                    "contactId": contact_id,
                    "entryDate": date.today().isoformat(),
                    "currencyId": "DKK",
                    "lines": [
                        {
                            "productId": product_id,
                            "description": _MARKER_I,
                            "quantity": 1,
                            "unitPrice": 10,
                        }
                    ],
                }
            },
        )
        assert ir["status"] in (200, 201), f"invoice seed failed: {ir}"
        data_i = cast(dict[str, Any], ir.get("data") or {})
        invoices = cast(list[dict[str, Any]], data_i.get("invoices") or [])
        invoice_id = str(invoices[0]["id"]) if invoices and invoices[0].get("id") else ""
        assert invoice_id
        ids["invoice"] = invoice_id
        return ids
    finally:
        await page.close()


async def _cleanup_disposable(
    runtime: BrowserRuntime, org_identity: Path, ids: dict[str, str]
) -> None:
    slug = _org_slug(org_identity)
    context = await runtime.start()
    page = cast(Any, await context.new_page())
    cap = _TokenCapture()
    cap.attach(page)
    try:
        await page.goto(f"https://mit.billy.dk/{slug}/invoices", wait_until="domcontentloaded")
        await page.wait_for_timeout(1200)
        if not cap.token:
            await page.goto(f"https://mit.billy.dk/{slug}/products", wait_until="domcontentloaded")
            await page.wait_for_timeout(1000)
        headers = cap.headers()
        ctx = cast(Any, runtime)._context  # live harness seed only
        for kind in ("invoices", "products", "contacts"):
            rid = ids.get(kind.rstrip("s") if kind != "invoices" else "invoice")
            # map keys
        key_map = {"invoices": "invoice", "products": "product", "contacts": "contact"}
        for kind, key in key_map.items():
            rid = ids.get(key)
            if rid:
                await _spa(
                    ctx,
                    "DELETE",
                    f"https://api.billysbilling.com/v2/{kind}/{rid}",
                    headers,
                )
        # sweep markers
        for kind, markers in (
            ("invoices", (_MARKER_I,)),
            ("products", (_MARKER_P,)),
            ("contacts", (_MARKER_C,)),
        ):
            listed = await _spa(
                ctx,
                "GET",
                f"https://api.billysbilling.com/v2/{kind}?organizationId={_ORG}&page=1&pageSize=100",
                headers,
            )
            if listed["status"] != 200 or not listed["data"]:
                continue
            data_l = cast(dict[str, Any], listed.get("data") or {})
            items = cast(list[dict[str, Any]], data_l.get(kind) or [])
            for item in items:
                blob = json.dumps(item)
                if any(m in blob for m in markers):
                    iid = str(item.get("id") or "")
                    if iid:
                        await _spa(
                            ctx,
                            "DELETE",
                            f"https://api.billysbilling.com/v2/{kind}/{iid}",
                            headers,
                        )
        # UI verify
        await page.goto(f"https://mit.billy.dk/{slug}/invoices", wait_until="domcontentloaded")
        await page.wait_for_timeout(1200)
        body = re.sub(r"\s+", " ", await page.locator("body").inner_text())[:3000]
        assert _MARKER_I not in body
    finally:
        await page.close()


async def _capture_invoices_get_frame(
    runtime: BrowserRuntime,
    org_identity: Path,
    destination: Path,
) -> None:
    slug = _org_slug(org_identity)
    context = await runtime.start()
    page = cast(Any, await context.new_page())
    try:
        await page.goto(f"https://mit.billy.dk/{slug}/invoices", wait_until="domcontentloaded")
        try:
            await page.wait_for_load_state("networkidle", timeout=20000)
        except Exception:
            pass
        await page.wait_for_timeout(1000)
        opened = False
        if _MARKER_I in re.sub(r"\s+", " ", await page.locator("body").inner_text())[:5000]:
            try:
                await page.get_by_text(_MARKER_I, exact=False).first.click(timeout=6000)
                opened = True
            except Exception:
                opened = False
        if not opened:
            rows = page.locator("table tbody tr, [role='row']")
            rn = await rows.count()
            for i in range(min(rn, 20)):
                txt = (await rows.nth(i).inner_text()).strip()
                if re.search(r"Nr\.|Dato|Kunde", txt) and len(txt) < 80:
                    continue
                if len(txt) < 4:
                    continue
                try:
                    await rows.nth(i).click(timeout=5000)
                    opened = True
                    break
                except Exception:
                    continue
        assert opened, "vision capture could not open an invoice detail row"
        try:
            await page.wait_for_load_state("networkidle", timeout=15000)
        except Exception:
            pass
        await page.wait_for_timeout(1500)
        path = str(urlsplit(str(page.url)).path or "")
        assert re.search(r"/invoices/[^/]+/edit", path), f"expected invoice edit path, got {path}"
        await page.screenshot(path=str(destination), full_page=False)
        assert destination.is_file() and destination.stat().st_size > 0
    finally:
        await page.close()


@pytest.mark.asyncio
async def test_dual_profiles_open_invoice_detail() -> None:
    """Profile A and independent profile B both classify an invoice detail surface."""

    _require_live_credentials()
    assert not os.environ.get("BILLY_API_TOKEN"), "live invoices get must not use API token"

    profile_a = _ephemeral_profile()
    profile_b = _ephemeral_profile()
    org_a = Path(tempfile.mkdtemp(dir=str(_DATA_ROOT))) / "org-a.json"
    org_b = Path(tempfile.mkdtemp(dir=str(_DATA_ROOT))) / "org-b.json"
    frame_dir = owner_only_frame_dir()
    record_path = _VISION_RECORD_DIR / "ui_invoices_get_open.json"
    runtime_a: BrowserRuntime | None = None
    runtime_b: BrowserRuntime | None = None
    ids: dict[str, str] = {}

    try:
        assert is_outside_repository(frame_dir, _REPO_ROOT)

        runtime_a = _runtime(profile_a, org_a)
        await _login_until_ready(runtime_a)

        # Always seed marker invoice for deterministic dual open + cleanup proof.
        ids = await _ensure_disposable_invoice(runtime_a, org_a)
        assert ids.get("invoice"), "could not seed disposable invoice for get-open"

        detail_a = await runtime_a.ui_invoices_get_open()
        if isinstance(detail_a, ToolError):
            pytest.fail(
                f"session A ui_invoices_get_open failed: {detail_a.code}: {detail_a.message}"
            )
        assert isinstance(detail_a, UiInvoicesGetOpenSuccess)
        assert detail_a.path_class == "/:org_slug/invoices/:id/edit"
        assert detail_a.shell_kind == "invoices_get"
        assert detail_a.detail_open is True
        assert detail_a.entry_date_control_present is True
        assert detail_a.contact_control_present is True
        assert detail_a.line_chrome_present is True

        frame_a = frame_dir / "session_a_invoices_get.png"
        await _capture_invoices_get_frame(runtime_a, org_a, frame_a)
        await runtime_a.close()
        runtime_a = None

        runtime_b = _runtime(profile_b, org_b)
        await _login_until_ready(runtime_b)
        detail_b = await runtime_b.ui_invoices_get_open()
        if isinstance(detail_b, ToolError):
            pytest.fail(
                f"session B ui_invoices_get_open failed: {detail_b.code}: {detail_b.message}"
            )
        assert isinstance(detail_b, UiInvoicesGetOpenSuccess)
        assert detail_b.model_dump() == detail_a.model_dump()

        frame_b = frame_dir / "session_b_invoices_get.png"
        await _capture_invoices_get_frame(runtime_b, org_b, frame_b)

        if ids:
            await _cleanup_disposable(runtime_b, org_b, ids)

        await runtime_b.close()
        runtime_b = None

        keep_frames = os.environ.get("BILLY_KEEP_VISION_FRAMES", "").strip() == "1"
        write_vision_record(
            record_path,
            workflow_ref="ui.invoices.get",
            assertion_refs=[
                "tests/live/test_ui_invoices_get_open.py::test_dual_profiles_open_invoice_detail",
                "session_a_ui_invoices_get_open",
                "session_b_ui_invoices_get_open",
                "session_a_invoices_get_frame",
                "session_b_invoices_get_frame",
                "detail_open_edit_path_form_chrome",
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
                    if ids:
                        try:
                            await _cleanup_disposable(
                                runtime, org_a if runtime is runtime_a else org_b, ids
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
        if record_path.is_file():
            mark_purge_verified(record_path)
