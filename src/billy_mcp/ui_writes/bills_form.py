"""Bounded Billy draft-bill form actions. Never pays, approves, pulls, or uploads."""

from __future__ import annotations

import asyncio
import json
from collections.abc import Callable
from datetime import date
from pathlib import Path
from typing import Protocol, cast
from urllib.parse import urlsplit

from billy_mcp.browser import BrowserRuntime
from billy_mcp.models import StableErrorCode, ToolError
from billy_mcp.ui_writes.bills_vendor import (
    DROPDOWN_SELECTORS,
    VENDOR_INPUT_SELECTORS,
    VENDOR_LABEL,
    create_vendor_labels,
    dump_vendor_chrome,
    pre_submit_dump_path,
)
from billy_mcp.ui_writes.page_flow import BILLY_ORIGIN, prove_text_on_fresh_page

PRE_SUBMIT_DUMP = (
    Path.home() / ".local" / "share" / "billy-mcp" / "inspect-live-bills-presubmit.json"
)
CREATE_PRE_SUBMIT_DUMP = (
    Path.home() / ".local" / "share" / "billy-mcp" / "inspect-live-bills-create-presubmit.json"
)
CREATE_FORM_FRAME: Path | None = None
_PERSIST_DUMP = Path.home() / ".local" / "share" / "billy-mcp" / "inspect-live-bills-persist.json"

LINE_DESCRIPTION = "input[name='billLines.0.description']"
VENDOR = VENDOR_INPUT_SELECTORS[0]
BILL_DATE = "input[name='billDate']"
LINE_AMOUNT = "input[name='billLines.0.inclVatAmount']"
DRAFT_SAVE = "Gem som kladde"
UPDATE_SAVE = "Opdater"
DELETE = "Slet"
FORBIDDEN_CTAS = (
    "Godkend",
    "Registrer betaling",
    "Træk",
    "Upload fil",
    "Send",
    "Email",
)
_OK_STATUS = frozenset({"200", "201", "204"})


class _Locator(Protocol):
    @property
    def first(self) -> _Locator: ...

    async def count(self) -> int: ...

    async def is_visible(self) -> bool: ...

    async def click(self, **kwargs: object) -> None: ...

    async def fill(self, value: str) -> None: ...

    async def press(self, key: str) -> None: ...

    async def input_value(self) -> str: ...

    async def get_attribute(self, name: str) -> str | None: ...

    def nth(self, index: int) -> _Locator: ...

    def get_by_role(self, role: str, **kwargs: object) -> _Locator: ...

    def get_by_text(self, text: str, **kwargs: object) -> _Locator: ...

    def locator(self, selector: str) -> _Locator: ...

    @property
    def last(self) -> _Locator: ...


class _Page(Protocol):
    @property
    def url(self) -> str: ...

    def locator(self, selector: str) -> _Locator: ...

    def get_by_role(self, role: str, **kwargs: object) -> _Locator: ...

    def get_by_label(self, text: str, **kwargs: object) -> _Locator: ...

    def get_by_text(self, text: str, **kwargs: object) -> _Locator: ...

    def on(self, event: str, handler: object) -> None: ...

    @property
    def keyboard(self) -> object: ...

    async def goto(self, url: str, wait_until: str = "domcontentloaded") -> object: ...

    async def wait_for_load_state(self, state: str, timeout: float | None = None) -> None: ...

    async def screenshot(self, **kwargs: object) -> object: ...

    async def close(self) -> None: ...


def is_persist_hit(item: str, *, method: str) -> bool:
    """True when watched traffic is the exact persist method on /v2/bills."""

    parts = item.split(" ", 2)
    if len(parts) < 3:
        return False
    used, status, path = parts[0], parts[1], parts[2]
    if used != method or status not in _OK_STATUS:
        return False
    if method == "PUT":
        return path.startswith("/v2/bills/")
    if method == "DELETE":
        return path.startswith("/v2/bills/")
    return path.rstrip("/") == "/v2/bills" or path.startswith("/v2/bills/")


def created_bill_id(seen: list[str], bodies: dict[str, object] | None = None) -> str | None:
    """Return the id from a POST persist, never from a later GET."""

    for item in seen:
        parts = item.split(" ", 2)
        if len(parts) < 3 or parts[0] != "POST" or parts[1] not in _OK_STATUS:
            continue
        path = parts[2]
        if path.startswith("/v2/bills/"):
            bill_id = path[len("/v2/bills/") :].split("/", 1)[0]
            if bill_id:
                return bill_id
        body = (bodies or {}).get(item)
        found = _bill_id_from_body(body)
        if found:
            return found
    return None


def refuse_non_draft_cta(name: str) -> ToolError | None:
    """Refuse booking, pay, pull, upload, and email controls."""

    if name in FORBIDDEN_CTAS:
        return ToolError(
            code=StableErrorCode.VALIDATION_ERROR,
            message="Billy bill writes refuse booking, payment, pull, upload, and email.",
            details={"cta": name},
        )
    return None


def dump_pre_submit(
    *,
    url: str,
    unique_tag: str,
    vendor: str,
    bill_date: str,
    line_amount: str,
    draft_cta: str,
    vendor_bind: str = "",
) -> None:
    """Write the parent-required pre-submit field dump outside git."""

    destination = pre_submit_dump_path(
        draft_cta, create_path=CREATE_PRE_SUBMIT_DUMP, update_path=PRE_SUBMIT_DUMP
    )
    _write_json(
        destination,
        {
            "url": url,
            "unique_tag": unique_tag,
            "vendor": vendor,
            "date": bill_date,
            "line_amount": line_amount,
            "draft_cta": draft_cta,
            "vendor_bind": vendor_bind,
        },
    )


async def submit_draft_bill(
    runtime: BrowserRuntime,
    *,
    action: str,
    unique_tag: str,
    organization_id: str,
    bill_id: str,
    readback_runtime: BrowserRuntime,
) -> ToolError | None:
    """Create, update, or delete one tagged draft bill, then prove it independently."""

    page: _Page | None = None
    try:
        bound = organization_id.strip()
        if not bound:
            return ToolError(
                code=StableErrorCode.ORGANIZATION_REQUIRED,
                message="A proven Billy organisation id is required.",
            )
        context = await runtime.start()
        page = cast(_Page, await context.new_page())
        await page.goto(f"{BILLY_ORIGIN}/", wait_until="domcontentloaded")
        await _settle(page)
        slug = _slug_from(page.url)
        if slug is None and _is_org_less_root(page.url):
            await page.goto(f"{BILLY_ORIGIN}/{bound}/bills", wait_until="domcontentloaded")
            await _settle(page)
            slug = _slug_from(page.url)
        if slug is None:
            return ToolError(
                code=StableErrorCode.ORGANIZATION_REQUIRED,
                message="Billy organisation slug is not available for the UI write.",
            )
        if slug != bound:
            return ToolError(
                code=StableErrorCode.CONFIRMATION_MISMATCH,
                message="Live Billy organisation does not match the confirmation ticket.",
            )
        if action == "create":
            failed = await _create_draft(page, slug, unique_tag)
        elif action == "update":
            failed = await _update_draft(page, slug, bill_id, unique_tag)
        else:
            failed = await _delete_draft(page, slug, bill_id)
        if failed is not None:
            return failed
        return await prove_text_on_fresh_page(
            readback_runtime,
            organization_id=bound,
            path="bills",
            text=unique_tag,
            absent=action == "delete",
        )
    except Exception as exc:
        return ToolError(
            code=StableErrorCode.BILLY_ERROR,
            message="Billy interface bill write could not be completed.",
            details={"error": type(exc).__name__},
        )
    finally:
        if page is not None:
            try:
                await page.close()
            except Exception:
                pass


async def _create_draft(page: _Page, slug: str, unique_tag: str) -> ToolError | None:
    await page.goto(f"{BILLY_ORIGIN}/{slug}/bills/new", wait_until="domcontentloaded")
    await _settle(page)
    filled = await _fill_draft_fields(page, unique_tag)
    if isinstance(filled, ToolError):
        return filled
    blocked = await _prepare_draft_click(page, unique_tag, filled, DRAFT_SAVE)
    if blocked is not None:
        return blocked
    seen, bodies = _watch_bill_traffic(page)
    if not await _click_exact_button(page, DRAFT_SAVE):
        return ToolError(
            code=StableErrorCode.UI_CHANGED,
            message="Billy draft save control is not visible.",
        )
    failed = await _wait_for_bill_write(seen, method="POST")
    _dump_persist(page, unique_tag, failed, seen)
    if failed is not None:
        return failed
    created = created_bill_id(seen, bodies)
    if created is None:
        created = await _created_bill_id_from_responses(seen, bodies)
    if created is None:
        return ToolError(
            code=StableErrorCode.BILLY_ERROR,
            message="Billy draft bill write did not return an id.",
            details={"watched": list(seen)},
        )
    await page.goto(f"{BILLY_ORIGIN}/{slug}/bills/{created}/edit", wait_until="domcontentloaded")
    await _settle(page)
    field = page.locator(LINE_DESCRIPTION)
    if await field.count() < 1 or (await field.first.input_value()) != unique_tag:
        return ToolError(
            code=StableErrorCode.UI_CHANGED,
            message="Billy saved bill did not keep the line description.",
        )
    return None


async def _update_draft(page: _Page, slug: str, bill_id: str, unique_tag: str) -> ToolError | None:
    if not bill_id:
        return ToolError(
            code=StableErrorCode.VALIDATION_ERROR,
            message="A Billy bill id is required for update.",
        )
    await page.goto(f"{BILLY_ORIGIN}/{slug}/bills/{bill_id}/edit", wait_until="domcontentloaded")
    await _settle(page)
    filled = await _fill_draft_fields(page, unique_tag)
    if isinstance(filled, ToolError):
        return filled
    blocked = await _prepare_draft_click(page, unique_tag, filled, UPDATE_SAVE)
    if blocked is not None:
        return blocked
    return await _save_draft(page, button=UPDATE_SAVE, method="PUT")


async def _delete_draft(page: _Page, slug: str, bill_id: str) -> ToolError | None:
    if not bill_id:
        return ToolError(
            code=StableErrorCode.VALIDATION_ERROR,
            message="A Billy bill id is required for delete.",
        )
    await page.goto(f"{BILLY_ORIGIN}/{slug}/bills/{bill_id}/edit", wait_until="domcontentloaded")
    await _settle(page)
    if not await _slet_visible(page):
        await page.goto(f"{BILLY_ORIGIN}/{slug}/bills/{bill_id}", wait_until="domcontentloaded")
        await _settle(page)
    blocked = refuse_non_draft_cta(DELETE)
    if blocked is not None:
        return blocked
    seen, _bodies = _watch_bill_traffic(page)
    if not await _click_exact_button(page, DELETE):
        return ToolError(
            code=StableErrorCode.UI_CHANGED,
            message="Billy bill delete control is not visible.",
        )
    await _settle(page)
    if not await _click_modal_slet(page):
        return ToolError(
            code=StableErrorCode.UI_CHANGED,
            message="Billy bill delete confirm is not visible.",
        )
    return await _wait_for_bill_write(seen, method="DELETE")


async def _prepare_draft_click(
    page: _Page,
    unique_tag: str,
    filled: dict[str, str],
    cta: str,
) -> ToolError | None:
    blocked = refuse_non_draft_cta(cta)
    if blocked is not None:
        return blocked
    dump_pre_submit(
        url=page.url,
        unique_tag=unique_tag,
        vendor=filled["vendor"],
        bill_date=filled["date"],
        line_amount=filled["line_amount"],
        draft_cta=cta,
        vendor_bind=filled.get("vendor_bind", ""),
    )
    await _capture_create_form(page, cta)
    if not await _button_visible(page, cta):
        return ToolError(
            code=StableErrorCode.UI_CHANGED,
            message="Billy draft save control is not visible.",
        )
    return None


async def _save_draft(
    page: _Page, *, button: str = DRAFT_SAVE, method: str = "POST"
) -> ToolError | None:
    seen, _bodies = _watch_bill_traffic(page)
    if not await _click_exact_button(page, button):
        return ToolError(
            code=StableErrorCode.UI_CHANGED,
            message="Billy draft save control is not visible.",
        )
    failed = await _wait_for_bill_write(seen, method=method)
    _dump_persist(page, "save", failed, seen)
    return failed


def dates_match(actual: str, wanted: str) -> bool:
    """True when Billy date chrome matches the intended day."""

    return actual.replace(".", "-").replace("/", "-") == wanted.replace(".", "-").replace("/", "-")


def amounts_match(actual: str, wanted: str) -> bool:
    """True when a Danish or plain amount equals the intended number."""

    def parse(raw: str) -> float | None:
        cleaned = raw.strip().replace(" ", "").replace("\xa0", "")
        if not cleaned:
            return None
        if "," in cleaned and "." in cleaned:
            cleaned = cleaned.replace(".", "").replace(",", ".")
        elif "," in cleaned:
            cleaned = cleaned.replace(",", ".")
        try:
            return float(cleaned)
        except ValueError:
            return None

    left = parse(actual)
    right = parse(wanted)
    return left is not None and right is not None and left == right


async def _type_into(page: _Page, selector: str, value: str, *, tab: bool) -> str | None:
    field = page.locator(selector)
    if await field.count() < 1 or not await field.first.is_visible():
        return None
    target = field.first
    try:
        await target.click()
        keyboard = getattr(page, "keyboard", None)
        if keyboard is not None:
            press = getattr(keyboard, "press", None)
            typed = getattr(keyboard, "type", None)
            if press is not None:
                await press("Meta+A")
            if typed is not None:
                await typed(value)
            else:
                await target.fill(value)
        else:
            await target.fill(value)
        if tab:
            await target.press("Tab")
        await asyncio.sleep(0.3)
    except Exception:
        return None
    return await target.input_value()


async def _fill_vendor(page: _Page, unique_tag: str) -> str | None:
    names = await _visible_input_names(page)
    labeled = await _type_labeled(page, VENDOR_LABEL, unique_tag)
    if labeled is not None:
        bind = await _finish_vendor_bind(page, unique_tag)
        if bind is not None:
            chosen = f"label:{VENDOR_LABEL}:{bind}"
            dump_vendor_chrome(names=names, chosen=chosen)
            return chosen
    for selector in VENDOR_INPUT_SELECTORS:
        typed = await _type_into(page, selector, unique_tag, tab=False)
        if typed is None:
            continue
        bind = await _finish_vendor_bind(page, unique_tag)
        if bind is not None:
            chosen = f"{selector}:{bind}"
            dump_vendor_chrome(names=names, chosen=chosen)
            return chosen
    dump_vendor_chrome(names=names, chosen=None)
    return None


async def _finish_vendor_bind(page: _Page, unique_tag: str) -> str | None:
    if await _wait_for_vendor_option(page, unique_tag):
        return "option"
    keyboard = getattr(page, "keyboard", None)
    if keyboard is not None and getattr(keyboard, "press", None) is not None:
        try:
            await keyboard.press("Enter")
        except Exception:
            pass
        if await _wait_for_vendor_option(page, unique_tag):
            return "enter"
    return None


async def _wait_for_vendor_option(page: _Page, unique_tag: str) -> bool:
    for _ in range(6):
        if await _choose_vendor_option(page, unique_tag):
            return True
        await asyncio.sleep(0.2)
    return False


async def _visible_input_names(page: _Page) -> list[str]:
    names: list[str] = []
    fields = page.locator("input")
    try:
        count = await fields.count()
    except Exception:
        return names
    for index in range(min(count, 40)):
        try:
            name = await fields.nth(index).get_attribute("name")
        except Exception:
            continue
        if isinstance(name, str) and name and name not in names:
            names.append(name)
    return names


async def _choose_vendor_option(page: _Page, unique_tag: str) -> bool:
    for root in DROPDOWN_SELECTORS:
        existing = page.locator(root).get_by_text(unique_tag, exact=True)
        try:
            if await existing.count() >= 1 and await existing.first.is_visible():
                await existing.first.click(timeout=5000)
                return True
        except Exception:
            continue
    existing = page.get_by_text(unique_tag, exact=True)
    try:
        if await existing.count() >= 1 and await existing.first.is_visible():
            await existing.first.click(timeout=5000)
            return True
    except Exception:
        pass
    for label in create_vendor_labels(unique_tag):
        create = page.get_by_text(label, exact=True)
        try:
            if await create.count() >= 1 and await create.first.is_visible():
                await create.first.click(timeout=5000)
                return await _confirm_new_vendor_modal(page, unique_tag)
        except Exception:
            continue
    return False


async def _type_labeled(page: _Page, label: str, value: str) -> str | None:
    field = page.get_by_label(label, exact=True)
    try:
        if await field.count() < 1:
            return None
        target = field.first
        if not await target.is_visible():
            return None
        await target.click()
        keyboard = getattr(page, "keyboard", None)
        if keyboard is not None and getattr(keyboard, "type", None) is not None:
            press = getattr(keyboard, "press", None)
            if press is not None:
                await press("Meta+A")
            await keyboard.type(value)
        else:
            await target.fill(value)
        await asyncio.sleep(0.3)
        return await target.input_value()
    except Exception:
        return None


async def _confirm_new_vendor_modal(page: _Page, unique_tag: str) -> bool:
    modal = page.locator("div[class*='ModalWrapper']")
    save = modal.get_by_role("button", name="Gem", exact=True)
    for _ in range(20):
        if await save.count() >= 1 and await save.first.is_visible():
            break
        await asyncio.sleep(0.2)
    else:
        return True
    name_field = modal.locator("input[name='name']")
    if await name_field.count() >= 1:
        current = await name_field.first.input_value()
        if current != unique_tag:
            try:
                await name_field.first.click()
                keyboard = getattr(page, "keyboard", None)
                if keyboard is not None and getattr(keyboard, "type", None) is not None:
                    press = getattr(keyboard, "press", None)
                    if press is not None:
                        await press("Meta+A")
                    await keyboard.type(unique_tag)
                else:
                    await name_field.first.fill(unique_tag)
                await asyncio.sleep(0.2)
            except Exception:
                return False
            if await name_field.first.input_value() != unique_tag:
                return False
    try:
        await save.first.click(force=True, timeout=5000)
    except Exception:
        return False
    for _ in range(24):
        if await save.count() < 1:
            return True
        try:
            if not await save.first.is_visible():
                return True
        except Exception:
            return True
        await asyncio.sleep(0.25)
    return False


async def _fill_named(
    page: _Page,
    selector: str,
    value: str,
    *,
    matches: Callable[[str, str], bool] | None = None,
) -> str | None:
    current = await _type_into(page, selector, value, tab=True)
    if current is None:
        return None
    ok = current == value if matches is None else matches(current, value)
    return current if ok else None


async def _fill_draft_fields(page: _Page, unique_tag: str) -> dict[str, str] | ToolError:
    bill_date = date.today().strftime("%d.%m.%Y")
    amount = "1"
    vendor_bind = await _fill_vendor(page, unique_tag)
    if vendor_bind is None:
        return ToolError(
            code=StableErrorCode.UI_CHANGED,
            message="Billy bill draft fields are not visible.",
            details={"field": "vendor", "selectors": list(VENDOR_INPUT_SELECTORS)},
        )
    actual_date = await _fill_named(page, BILL_DATE, bill_date, matches=dates_match)
    if actual_date is None:
        actual_date = await _type_labeled(page, "Bilagsdato", bill_date)
        if actual_date is not None and not dates_match(actual_date, bill_date):
            actual_date = None
    if actual_date is None:
        return ToolError(
            code=StableErrorCode.UI_CHANGED,
            message="Billy bill draft fields are not visible.",
            details={"field": "date", "selector": BILL_DATE},
        )
    actual_amount = await _fill_named(page, LINE_AMOUNT, amount, matches=amounts_match)
    if actual_amount is None:
        return ToolError(
            code=StableErrorCode.UI_CHANGED,
            message="Billy bill draft fields are not visible.",
            details={"field": "line_amount", "selector": LINE_AMOUNT},
        )
    actual_desc = await _fill_named(page, LINE_DESCRIPTION, unique_tag)
    if actual_desc is None:
        return ToolError(
            code=StableErrorCode.UI_CHANGED,
            message="Billy bill draft fields are not visible.",
            details={"field": "description", "selector": LINE_DESCRIPTION},
        )
    return {
        "vendor": unique_tag,
        "date": actual_date,
        "line_amount": actual_amount,
        "description": actual_desc,
        "vendor_bind": vendor_bind,
    }


async def _button_visible(page: _Page, name: str) -> bool:
    control = page.get_by_role("button", name=name, exact=True)
    return await control.count() >= 1 and await control.first.is_visible()


async def _click_exact_button(page: _Page, name: str) -> bool:
    blocked = refuse_non_draft_cta(name)
    if blocked is not None:
        return False
    if not await _button_visible(page, name):
        return False
    try:
        await page.get_by_role("button", name=name, exact=True).first.click(
            force=True, timeout=5000
        )
    except Exception:
        return False
    return True


async def _slet_visible(page: _Page) -> bool:
    if await _button_visible(page, DELETE):
        return True
    link = page.get_by_role("link", name=DELETE, exact=True)
    return await link.count() >= 1 and await link.first.is_visible()


async def _click_modal_slet(page: _Page) -> bool:
    modal = page.locator("[role='dialog'], .ds-moved-with-portal")
    if await modal.count() < 1:
        return await _click_exact_button(page, DELETE)
    control = modal.last.get_by_role("button", name=DELETE, exact=True)
    if await control.count() < 1:
        return False
    try:
        await control.first.click(force=True, timeout=5000)
    except Exception:
        return False
    return True


def _slug_from(url: str) -> str | None:
    parts = [part for part in (urlsplit(url).path or "").split("/") if part]
    if parts and parts[0] not in {"login"}:
        return parts[0]
    return None


def _is_org_less_root(url: str) -> bool:
    return not [part for part in (urlsplit(url).path or "").split("/") if part]


def _watch_bill_traffic(page: _Page) -> tuple[list[str], dict[str, object]]:
    seen: list[str] = []
    bodies: dict[str, object] = {}

    def _on(event: object) -> None:
        url = str(getattr(event, "url", "") or "")
        if "api.billysbilling.com" not in url or "/v2/bills" not in url:
            return
        status = getattr(event, "status", None)
        request = getattr(event, "request", event)
        used = str(getattr(request, "method", "") or getattr(event, "method", "") or "")
        item = f"{used} {status} {urlsplit(url).path}"
        seen.append(item)
        bodies[item] = event

    page.on("response", _on)
    return seen, bodies


async def _created_bill_id_from_responses(seen: list[str], bodies: dict[str, object]) -> str | None:
    for item in seen:
        parts = item.split(" ", 2)
        if len(parts) < 3 or parts[0] != "POST" or parts[1] not in _OK_STATUS:
            continue
        path = parts[2]
        if path.startswith("/v2/bills/"):
            bill_id = path[len("/v2/bills/") :].split("/", 1)[0]
            if bill_id:
                return bill_id
        body = await _response_json(bodies.get(item))
        found = _bill_id_from_body(body)
        if found:
            return found
    return None


async def _response_json(event: object) -> object:
    reader = getattr(event, "json", None)
    if reader is None:
        return None
    try:
        payload = reader()
        if hasattr(payload, "__await__"):
            return await payload
        return payload
    except Exception:
        return None


def _bill_id_from_body(body: object) -> str | None:
    if not isinstance(body, dict):
        return None
    payload = cast(dict[str, object], body)
    bills = payload.get("bills")
    if not isinstance(bills, list) or not bills or not isinstance(bills[0], dict):
        return None
    first = cast(dict[str, object], bills[0])
    ident = first.get("id")
    if isinstance(ident, str) and ident:
        return ident
    return None


async def _wait_for_bill_write(seen: list[str], *, method: str) -> ToolError | None:
    for _ in range(40):
        if any(is_persist_hit(item, method=method) for item in seen):
            return None
        await asyncio.sleep(0.25)
    return ToolError(
        code=StableErrorCode.BILLY_ERROR,
        message="Billy draft bill write did not persist.",
        details={"watched": list(seen)},
    )


def _dump_persist(
    page: _Page, unique_tag: str, failed: ToolError | None, seen: list[str] | None = None
) -> None:
    _write_json(
        _PERSIST_DUMP,
        {
            "url": page.url,
            "tag_len": len(unique_tag),
            "failed_code": None if failed is None else failed.code,
            "failed_details": None if failed is None else failed.details,
            "watched": list(seen or []),
        },
    )


def _write_json(path: Path, payload: object) -> None:
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload, default=str, indent=2) + "\n", encoding="utf-8")
    except OSError:
        return


async def _capture_create_form(page: _Page, cta: str) -> None:
    if cta != DRAFT_SAVE or CREATE_FORM_FRAME is None:
        return
    shot = getattr(page, "screenshot", None)
    if shot is None:
        return
    try:
        await shot(path=str(CREATE_FORM_FRAME), full_page=False)
    except Exception:
        return


async def _settle(page: _Page) -> None:
    try:
        await page.wait_for_load_state("networkidle", timeout=8000)
    except Exception:
        await asyncio.sleep(0.4)
