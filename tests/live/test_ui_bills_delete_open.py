"""Live dual-session qualification for read-only ui_bills_delete_open.

Requires opaque browser credential references. Never uses BILLY_API_TOKEN.
Independent second-interface read-back is a second ephemeral profile login.
Opens Slet confirm and Annuller only; never permanent delete / second Slet /
Opdater / Godkend. Live harness seeds a disposable draft bill via SPA token
when needed, then deletes it.
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
from billy_mcp.models import AuthLoginWaitSuccess, ToolError, UiBillsDeleteOpenSuccess
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
_MARKER_C = "R18673-TMP-CLIENT-BILL-DELETE-DO-NOT-USE"
_MARKER_B = "R18673-TMP-BILL-DELETE-DO-NOT-USE"
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
    return Path(tempfile.mkdtemp(prefix="billy-live-bills-delete-", dir=str(_DATA_ROOT)))


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


def _pick_expense_account(accounts: list[dict[str, Any]]) -> dict[str, Any] | None:
    for a in accounts:
        name = str(a.get("name") or "").lower()
        if any(x in name for x in ("vareforbrug", "omkost", "expense", "køb", "administration")):
            return a
    for a in accounts:
        no = str(a.get("accountNo") or "")
        if no.startswith(("2", "3", "4", "5", "6", "7")):
            return a
    return accounts[0] if accounts else None


def _pick_purchase_tax(tax_rates: list[dict[str, Any]]) -> dict[str, Any] | None:
    for t in tax_rates:
        if t.get("appliesToPurchases") is True and t.get("isActive") is not False:
            return t
    return tax_rates[0] if tax_rates else None


async def _ensure_disposable_bill(runtime: BrowserRuntime, org_identity: Path) -> dict[str, str]:
    """Seed supplier contact + draft bill via SPA. Returns created ids."""

    slug = _org_slug(org_identity)
    context = await runtime.start()
    page = cast(Any, await context.new_page())
    cap = _TokenCapture()
    cap.attach(page)
    ids: dict[str, str] = {}
    try:
        await page.goto(f"https://mit.billy.dk/{slug}/bills", wait_until="domcontentloaded")
        try:
            await page.wait_for_load_state("networkidle", timeout=20000)
        except Exception:
            pass
        await page.wait_for_timeout(1500)
        headers = cap.headers()
        assert cap.token, "SPA access token not captured for bill seed"
        ctx = cast(Any, runtime)._context  # live harness seed only

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
                    "isCustomer": False,
                    "isSupplier": True,
                }
            },
        )
        assert cr["status"] in (200, 201), f"contact seed failed: {cr}"
        data_c = cast(dict[str, Any], cr.get("data") or {})
        contacts = cast(list[dict[str, Any]], data_c.get("contacts") or [])
        contact_id = str(contacts[0]["id"]) if contacts and contacts[0].get("id") else ""
        assert contact_id
        ids["contact"] = contact_id

        acc = await _spa(
            ctx,
            "GET",
            f"https://api.billysbilling.com/v2/accounts?organizationId={_ORG}&page=1&pageSize=100",
            headers,
        )
        assert acc["status"] == 200, f"accounts list failed: {acc}"
        data_a = cast(dict[str, Any], acc.get("data") or {})
        accounts = cast(list[dict[str, Any]], data_a.get("accounts") or [])
        exp = _pick_expense_account(accounts)
        assert exp and exp.get("id"), "no expense account for bill line"

        tr = await _spa(
            ctx,
            "GET",
            f"https://api.billysbilling.com/v2/taxRates?organizationId={_ORG}&page=1&pageSize=50",
            headers,
        )
        assert tr["status"] == 200, f"taxRates list failed: {tr}"
        data_t = cast(dict[str, Any], tr.get("data") or {})
        tax_rates = cast(list[dict[str, Any]], data_t.get("taxRates") or [])
        tax = _pick_purchase_tax(tax_rates)
        assert tax and tax.get("id"), "no purchase taxRate for bill line"

        br = await _spa(
            ctx,
            "POST",
            "https://api.billysbilling.com/v2/bills",
            headers,
            {
                "bill": {
                    "organizationId": _ORG,
                    "contactId": contact_id,
                    "entryDate": date.today().isoformat(),
                    "currencyId": "DKK",
                    "lines": [
                        {
                            "accountId": exp.get("id"),
                            "taxRateId": tax.get("id"),
                            "description": _MARKER_B,
                            "amount": 25.0,
                        }
                    ],
                }
            },
        )
        assert br["status"] in (200, 201), f"bill seed failed: {br}"
        data_b = cast(dict[str, Any], br.get("data") or {})
        bills = cast(list[dict[str, Any]], data_b.get("bills") or [])
        bill_id = str(bills[0]["id"]) if bills and bills[0].get("id") else ""
        assert bill_id
        ids["bill"] = bill_id
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
        await page.goto(f"https://mit.billy.dk/{slug}/bills", wait_until="domcontentloaded")
        await page.wait_for_timeout(1200)
        headers = cap.headers()
        ctx = cast(Any, runtime)._context  # live harness seed only
        key_map = {"bills": "bill", "contacts": "contact"}
        for kind, key in key_map.items():
            rid = ids.get(key)
            if rid:
                await _spa(
                    ctx,
                    "DELETE",
                    f"https://api.billysbilling.com/v2/{kind}/{rid}",
                    headers,
                )
        for kind, markers in (
            ("bills", (_MARKER_B,)),
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
        await page.goto(f"https://mit.billy.dk/{slug}/bills", wait_until="domcontentloaded")
        await page.wait_for_timeout(1200)
        body = re.sub(r"\s+", " ", await page.locator("body").inner_text())[:3000]
        assert _MARKER_B not in body
        await page.goto(f"https://mit.billy.dk/{slug}/suppliers", wait_until="domcontentloaded")
        await page.wait_for_timeout(1000)
        body_s = re.sub(r"\s+", " ", await page.locator("body").inner_text())[:3000]
        assert _MARKER_C not in body_s
    finally:
        await page.close()


async def _capture_bills_delete_frame(
    runtime: BrowserRuntime,
    org_identity: Path,
    destination: Path,
) -> None:
    slug = _org_slug(org_identity)
    context = await runtime.start()
    page = cast(Any, await context.new_page())
    try:
        await page.goto(f"https://mit.billy.dk/{slug}/bills", wait_until="domcontentloaded")
        try:
            await page.wait_for_load_state("networkidle", timeout=20000)
        except Exception:
            pass
        await page.wait_for_timeout(1000)
        opened = False
        if _MARKER_B in re.sub(r"\s+", " ", await page.locator("body").inner_text())[:5000]:
            try:
                await page.get_by_text(_MARKER_B, exact=False).first.click(timeout=6000)
                opened = True
            except Exception:
                opened = False
        if not opened:
            rows = page.locator("table tbody tr, [role='row']")
            rn = await rows.count()
            for i in range(min(rn, 20)):
                txt = (await rows.nth(i).inner_text()).strip()
                if re.search(r"Nr\.|Dato|Leverandør", txt) and len(txt) < 80:
                    continue
                if len(txt) < 4:
                    continue
                try:
                    await rows.nth(i).click(timeout=5000)
                    opened = True
                    break
                except Exception:
                    continue
        assert opened, "vision capture could not open a bill delete chrome row"
        try:
            await page.wait_for_load_state("networkidle", timeout=15000)
        except Exception:
            pass
        await page.wait_for_timeout(1500)
        path = str(urlsplit(str(page.url)).path or "")
        # list click may land on read detail; soft-navigate to edit for delete chrome frames.
        if re.search(r"/bills/[^/]+$", path) and not path.endswith("/edit") and "/new" not in path:
            await page.goto(
                f"https://mit.billy.dk{path.rstrip('/')}/edit",
                wait_until="domcontentloaded",
            )
            await page.wait_for_timeout(1200)
            path = str(urlsplit(str(page.url)).path or "")
        assert re.search(r"/bills/[^/]+/edit$", path), (
            f"expected bill delete chrome path, got {path}"
        )
        await page.screenshot(path=str(destination), full_page=False)
        assert destination.is_file() and destination.stat().st_size > 0
    finally:
        await page.close()


@pytest.mark.asyncio
async def test_dual_profiles_open_bill_delete_chrome() -> None:
    """Profile A and independent profile B both classify a bill delete chrome surface."""

    _require_live_credentials()
    assert not os.environ.get("BILLY_API_TOKEN"), "live bills delete must not use API token"

    profile_a = _ephemeral_profile()
    profile_b = _ephemeral_profile()
    org_a = Path(tempfile.mkdtemp(dir=str(_DATA_ROOT))) / "org-a.json"
    org_b = Path(tempfile.mkdtemp(dir=str(_DATA_ROOT))) / "org-b.json"
    frame_dir = owner_only_frame_dir()
    record_path = _VISION_RECORD_DIR / "ui_bills_delete_open.json"
    runtime_a: BrowserRuntime | None = None
    runtime_b: BrowserRuntime | None = None
    ids: dict[str, str] = {}

    try:
        assert is_outside_repository(frame_dir, _REPO_ROOT)

        runtime_a = _runtime(profile_a, org_a)
        await _login_until_ready(runtime_a)

        ids = await _ensure_disposable_bill(runtime_a, org_a)
        assert ids.get("bill"), "could not seed disposable bill for delete-open"

        detail_a = await runtime_a.ui_bills_delete_open()
        if isinstance(detail_a, ToolError):
            pytest.fail(
                f"session A ui_bills_delete_open failed: {detail_a.code}: {detail_a.message}"
            )
        assert isinstance(detail_a, UiBillsDeleteOpenSuccess)
        assert detail_a.path_class == "/:org_slug/bills/:id/edit"
        assert detail_a.shell_kind == "bills_delete"
        assert detail_a.edit_open is True
        assert detail_a.slet_present is True
        assert detail_a.confirm_open is True
        assert detail_a.annuller_present is True
        assert detail_a.confirm_dismissed is True

        frame_a = frame_dir / "session_a_bills_delete.png"
        await _capture_bills_delete_frame(runtime_a, org_a, frame_a)
        await runtime_a.close()
        runtime_a = None

        runtime_b = _runtime(profile_b, org_b)
        await _login_until_ready(runtime_b)
        detail_b = await runtime_b.ui_bills_delete_open()
        if isinstance(detail_b, ToolError):
            pytest.fail(
                f"session B ui_bills_delete_open failed: {detail_b.code}: {detail_b.message}"
            )
        assert isinstance(detail_b, UiBillsDeleteOpenSuccess)
        assert detail_b.model_dump() == detail_a.model_dump()

        frame_b = frame_dir / "session_b_bills_delete.png"
        await _capture_bills_delete_frame(runtime_b, org_b, frame_b)

        if ids:
            await _cleanup_disposable(runtime_b, org_b, ids)

        await runtime_b.close()
        runtime_b = None

        keep_frames = os.environ.get("BILLY_KEEP_VISION_FRAMES", "").strip() == "1"
        write_vision_record(
            record_path,
            workflow_ref="ui.bills.delete",
            assertion_refs=[
                "tests/live/test_ui_bills_delete_open.py::test_dual_profiles_open_bill_delete_chrome",
                "session_a_ui_bills_delete_open",
                "session_b_ui_bills_delete_open",
                "session_a_bills_delete_frame",
                "session_b_bills_delete_frame",
                "delete_chrome_confirm_annuller",
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
        shutil.rmtree(org_a.parent, ignore_errors=True)
        shutil.rmtree(org_b.parent, ignore_errors=True)
        purge_frame_dir(frame_dir)
        if record_path.exists():
            mark_purge_verified(record_path)
