"""Bounded Billy draft-bill form actions. Never pays, approves, pulls, or uploads."""

from __future__ import annotations

import asyncio
import json
import os
from collections.abc import Callable
from datetime import date
from pathlib import Path
from typing import Protocol, cast
from urllib.parse import urlsplit

from billy_mcp.browser import BrowserRuntime
from billy_mcp.models import StableErrorCode, ToolError
from billy_mcp.ui_writes.bills_vendor import (
    CREATE_VENDOR_LABEL,
    PORTAL_FOOTER_WRAPPER,
    VENDOR_CLEAR,
    VENDOR_INPUT_SELECTORS,
    VENDOR_LABEL,
    VENDOR_SEARCH_TOGGLE,
    dump_date_chrome,
    dump_leftover_portal,
    dump_scoped_vendor_wrapper,
    dump_vendor_chrome,
    leftover_close_action,
    leftover_close_after_existing_option,
    leftover_footer_means_bound,
    leftover_inspect_record,
    leftover_portal_kind,
    pick_portal_create_index,
    pick_portal_existing_option_index,
    portal_create_footer_label,
    portal_list_item_flags,
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
CREATE_PERSIST_DUMP = (
    Path.home() / ".local" / "share" / "billy-mcp" / "inspect-live-bills-create-persist.json"
)
SAVE_DUMP = Path.home() / ".local" / "share" / "billy-mcp" / "inspect-live-bills-save.json"
DRAFT_SAVE_HIT = "draft-save"
_HIT_JS = """([x, y, expected]) => {
  const el = document.elementFromPoint(x, y);
  if (!el) return null;
  const button = el.closest("button");
  if (button) {
    const text = (button.innerText || button.textContent || "").replace(/\\s+/g, " ").trim();
    if (text === expected) return "draft-save";
  }
  const raw = typeof el.className === "string" ? el.className : "";
  const tokens = raw.split(/\\s+/).filter(Boolean).slice(0, 4);
  return tokens.length ? `${el.tagName}.${tokens.join(".")}` : el.tagName;
}"""

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

    async def is_disabled(self) -> bool: ...

    async def bounding_box(self) -> dict[str, float] | None: ...

    async def fill(self, value: str) -> None: ...

    async def press(self, key: str) -> None: ...

    async def press_sequentially(self, text: str) -> None: ...

    async def input_value(self) -> str: ...

    async def inner_text(self) -> str: ...

    async def get_attribute(self, name: str) -> str | None: ...

    def nth(self, index: int) -> _Locator: ...

    def get_by_role(self, role: str, **kwargs: object) -> _Locator: ...

    def get_by_text(self, text: str, **kwargs: object) -> _Locator: ...

    def locator(self, selector: str) -> _Locator: ...

    def filter(self, **kwargs: object) -> _Locator: ...

    @property
    def last(self) -> _Locator: ...


class _SaveButton(Protocol):
    @property
    def first(self) -> _SaveButton: ...

    async def count(self) -> int: ...

    async def is_visible(self) -> bool: ...

    async def is_disabled(self) -> bool: ...

    async def bounding_box(self) -> dict[str, float] | None: ...


class _SavePage(Protocol):
    def get_by_role(self, role: str, **kwargs: object) -> _SaveButton: ...

    async def evaluate(self, expression: str, arg: object | None = None) -> object: ...

    @property
    def mouse(self) -> object: ...


class _Page(Protocol):
    @property
    def url(self) -> str: ...

    def locator(self, selector: str) -> _Locator: ...

    def get_by_role(self, role: str, **kwargs: object) -> _Locator: ...

    def get_by_label(self, text: str, **kwargs: object) -> _Locator: ...

    def get_by_text(self, text: str, **kwargs: object) -> _Locator: ...

    def on(self, event: str, handler: object) -> None: ...

    async def evaluate(self, expression: str, arg: object | None = None) -> object: ...

    @property
    def keyboard(self) -> object: ...

    @property
    def mouse(self) -> object: ...

    async def goto(self, url: str, wait_until: str = "domcontentloaded") -> object: ...

    async def wait_for_load_state(self, state: str, timeout: float | None = None) -> None: ...

    async def screenshot(self, **kwargs: object) -> object: ...

    async def close(self) -> None: ...


def locator_force_click_is_persist_proof() -> bool:
    """A force=True locator click is never persist proof."""

    return False


def save_delivery_blocked(
    *,
    visible: bool,
    disabled: bool | None,
    box: object,
    hit_target: str | None,
    expected_hit: str = DRAFT_SAVE_HIT,
) -> bool:
    """True when the draft save control must not be clicked."""

    return (not visible) or bool(disabled) or box is None or hit_target != expected_hit


def leftover_portal_covers_save(hit_target: str | None) -> bool:
    """True when elementFromPoint on save is a leftover portal list."""

    if not hit_target or "ds-moved-with-portal" not in hit_target:
        return False
    if "DropzoneFullScreenWrapper" in hit_target:
        return False
    return True


def portal_overlay_gone(*, count: int, any_visible: bool) -> bool:
    """True when leftover portal lists are absent or hidden."""

    return count < 1 or not any_visible


def record_bill_watch_item(
    *,
    kind: str,
    method: str,
    path: str,
    status: str | None = None,
    failure: str | None = None,
) -> str | None:
    """Format one bills request, response, or abort. Ignore other paths."""

    del failure
    if "/v2/bills" not in path:
        return None
    if kind == "response":
        return f"{method} {status} {path}"
    if kind == "failed":
        return f"{method} FAILED {path}"
    return f"{method} REQUEST {path}"


def dump_save_delivery(payload: dict[str, object], *, destination: Path | None = None) -> None:
    """Write a non-PII save-button dump outside git."""

    path = destination if destination is not None else SAVE_DUMP
    current = os.environ.get("PYTEST_CURRENT_TEST", "")
    if destination is None and current and "/live/" not in current.replace("\\", "/"):
        return
    _write_json(
        path,
        {
            "visible": payload.get("visible"),
            "disabled": payload.get("disabled"),
            "hit_target": payload.get("hit_target"),
            "pointer": payload.get("pointer"),
            "blocked": payload.get("blocked"),
            "cta": payload.get("cta"),
        },
    )


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


async def inspect_draft_save(page: _SavePage, name: str) -> dict[str, object]:
    """Observe the exact draft save button. Never clicks."""

    blocked_cta = refuse_non_draft_cta(name)
    if blocked_cta is not None:
        return {
            "visible": False,
            "disabled": None,
            "box": None,
            "center": None,
            "hit_target": None,
            "blocked": True,
            "pointer": False,
            "cta": name,
        }
    control = page.get_by_role("button", name=name, exact=True).first
    visible = await control.count() >= 1 and await control.is_visible()
    disabled = await control.is_disabled() if visible else None
    box = await control.bounding_box() if visible else None
    center: list[float] | None = None
    hit: str | None = None
    if isinstance(box, dict):
        center = [
            float(box["x"]) + float(box["width"]) / 2,
            float(box["y"]) + float(box["height"]) / 2,
        ]
        raw = await page.evaluate(_HIT_JS, [center[0], center[1], name])
        hit = raw if isinstance(raw, str) else None
    return {
        "visible": visible,
        "disabled": disabled,
        "box": box,
        "center": center,
        "hit_target": hit,
        "blocked": save_delivery_blocked(
            visible=visible, disabled=disabled, box=box, hit_target=hit
        ),
        "pointer": False,
        "cta": name,
    }


async def pointer_click_draft_save(
    page: _SavePage, name: str, *, destination: Path | None = None
) -> dict[str, object]:
    """Click the exact draft save center with the real mouse. Never force-click."""

    delivery = await inspect_draft_save(page, name)
    for _ in range(30):
        hit = delivery.get("hit_target")
        hit_name = hit if isinstance(hit, str) else None
        if not leftover_portal_covers_save(hit_name):
            break
        await asyncio.sleep(0.2)
        delivery = await inspect_draft_save(page, name)
    dump_save_delivery(delivery, destination=destination)
    if delivery.get("blocked"):
        return delivery
    raw_center = delivery.get("center")
    points = cast(list[object], raw_center) if isinstance(raw_center, list) else []
    if len(points) != 2:
        delivery["blocked"] = True
        dump_save_delivery(delivery, destination=destination)
        return delivery
    first = points[0]
    second = points[1]
    if not isinstance(first, (int, float)) or not isinstance(second, (int, float)):
        delivery["blocked"] = True
        dump_save_delivery(delivery, destination=destination)
        return delivery
    click = getattr(page.mouse, "click", None)
    if click is None:
        delivery["blocked"] = True
        dump_save_delivery(delivery, destination=destination)
        return delivery
    await click(float(first), float(second))
    delivery["pointer"] = True
    dump_save_delivery(delivery, destination=destination)
    return delivery


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
    leftover = await _close_leftover_portal(page, unique_tag)
    if leftover.get("blocked"):
        return ToolError(
            code=StableErrorCode.UI_CHANGED,
            message="Billy draft save control is not pointer-reachable.",
            details={"source": "leftover_portal", "leftover": leftover},
        )
    seen, bodies, requests = _watch_bill_traffic(page)
    delivery = await pointer_click_draft_save(page, DRAFT_SAVE)
    if delivery.get("blocked") or not delivery.get("pointer"):
        return ToolError(
            code=StableErrorCode.UI_CHANGED,
            message="Billy draft save control is not pointer-reachable.",
            details={
                "visible": delivery.get("visible"),
                "disabled": delivery.get("disabled"),
                "hit_target": delivery.get("hit_target"),
                "pointer": delivery.get("pointer"),
            },
        )
    failed = await _wait_for_bill_write(seen, method="POST")
    _dump_persist(page, unique_tag, failed, seen, requests, destination=CREATE_PERSIST_DUMP)
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
    filled = await _fill_draft_fields(page, unique_tag, bind_vendor=False)
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
    seen, _bodies, _requests = _watch_bill_traffic(page)
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
    leftover = await _close_leftover_portal(page, "save")
    if leftover.get("blocked"):
        return ToolError(
            code=StableErrorCode.UI_CHANGED,
            message="Billy draft save control is not pointer-reachable.",
            details={"source": "leftover_portal", "leftover": leftover},
        )
    seen, _bodies, requests = _watch_bill_traffic(page)
    delivery = await pointer_click_draft_save(page, button)
    if delivery.get("blocked") or not delivery.get("pointer"):
        return ToolError(
            code=StableErrorCode.UI_CHANGED,
            message="Billy draft save control is not pointer-reachable.",
            details={
                "visible": delivery.get("visible"),
                "disabled": delivery.get("disabled"),
                "hit_target": delivery.get("hit_target"),
                "pointer": delivery.get("pointer"),
            },
        )
    failed = await _wait_for_bill_write(seen, method=method)
    _dump_persist(page, "save", failed, seen, requests)
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


async def _type_into(
    page: _Page,
    selector: str,
    value: str,
    *,
    tab: bool,
    click_first: bool = True,
) -> str | None:
    field = page.locator(selector)
    if await field.count() < 1:
        return None
    target = field.first
    try:
        if click_first:
            visible = await target.is_visible()
            await target.click(force=not visible)
        await target.fill(value)
        if tab:
            await target.press("Tab")
        await asyncio.sleep(0.3)
    except Exception:
        return None
    return await target.input_value()


async def _fill_vendor(page: _Page, unique_tag: str) -> str | None:
    field = await _scoped_vendor_field(page)
    if field is None:
        dump_vendor_chrome(names=[], chosen=None)
        dump_scoped_vendor_wrapper({"phase": "missing", "input_name": None})
        return None
    try:
        await field.click()
    except Exception:
        dump_vendor_chrome(names=["vendor"], chosen=None)
        return None
    after_click = await _observe_vendor_wrapper(page, field, unique_tag, phase="after_click")
    typed = await _type_vendor_field(field, unique_tag)
    after_type = await _observe_vendor_wrapper(page, field, unique_tag, phase="after_type")
    dump_scoped_vendor_wrapper({"after_click": after_click, "after_type": after_type})
    if typed is None or unique_tag not in typed:
        dump_vendor_chrome(names=["vendor"], chosen=None)
        return None
    bind = await _bind_from_scoped_lists(page, unique_tag, after_type)
    dump_vendor_chrome(names=["vendor"], chosen=bind)
    return bind


async def _safe_attr(field: _Locator, name: str) -> str | None:
    try:
        value = await field.get_attribute(name)
    except Exception:
        return None
    return value if isinstance(value, str) and value else None


async def _safe_count(node: _Locator) -> int:
    try:
        return await node.count()
    except Exception:
        return 0


async def _scoped_vendor_field(page: _Page) -> _Locator | None:
    labeled = page.get_by_label(VENDOR_LABEL, exact=True)
    try:
        if await labeled.count() >= 1 and await labeled.first.is_visible():
            return labeled.first
    except Exception:
        pass
    field = page.locator("input[name='vendor']")
    try:
        if await field.count() >= 1 and await field.first.is_visible():
            return field.first
    except Exception:
        return None
    return None


async def _type_vendor_field(field: _Locator, unique_tag: str) -> str | None:
    try:
        await field.fill("")
        sequential = getattr(field, "press_sequentially", None)
        if sequential is not None:
            await sequential(unique_tag)
        else:
            await field.fill(unique_tag)
        await asyncio.sleep(0.5)
        return await field.input_value()
    except Exception:
        return None


async def _observe_vendor_wrapper(
    page: _Page, field: _Locator, unique_tag: str, *, phase: str
) -> dict[str, object]:
    name = await _safe_attr(field, "name")
    placeholder = await _safe_attr(field, "placeholder")
    value_len = 0
    try:
        value_len = len(await field.input_value())
    except Exception:
        value_len = -1
    wrapper = page.locator("[data-testid='input-wrapper']").filter(
        has=page.locator("input[name='vendor']")
    )
    search_n = await _safe_count(wrapper.locator("[data-testid='search']"))
    clear_n = await _safe_count(wrapper.locator("[data-testid='circleX']"))
    wrapper_list = await _list_snapshot(wrapper.locator(".ds-dropdown-list"), unique_tag)
    portal_list = await _list_snapshot(
        page.locator(".ds-dropdown-list.ds-moved-with-portal"), unique_tag
    )
    return {
        "phase": phase,
        "input_name": name,
        "has_placeholder": bool(placeholder),
        "value_len": value_len,
        "search_trigger": search_n > 0,
        "clear_trigger": clear_n > 0,
        "wrapper_list": wrapper_list,
        "portal_list": portal_list,
    }


async def _list_snapshot(node: _Locator, unique_tag: str) -> dict[str, object]:
    try:
        count = await node.count()
    except Exception:
        return {
            "count": 0,
            "has_opret": False,
            "has_tag": False,
            "items": [],
        }
    items: list[dict[str, bool]] = []
    has_opret = False
    has_tag = False
    for index in range(min(count, 9)):
        item = node.nth(index)
        try:
            text = (await item.inner_text()).strip()
            visible = await item.is_visible()
        except Exception:
            items.append(
                {
                    "has_opret": False,
                    "has_tag": False,
                    "has_empty": False,
                    "has_create_footer": False,
                    "visible": False,
                    "short": True,
                }
            )
            continue
        flags = portal_list_item_flags(text, unique_tag)
        flags["visible"] = visible
        items.append(flags)
        if flags["has_opret"]:
            has_opret = True
        if flags["has_tag"]:
            has_tag = True
    return {
        "count": count,
        "has_opret": has_opret,
        "has_tag": has_tag,
        "items": items,
    }


async def _bind_from_scoped_lists(
    page: _Page, unique_tag: str, observation: dict[str, object]
) -> str | None:
    portal = page.locator(".ds-dropdown-list.ds-moved-with-portal")
    portal_list = observation.get("portal_list")
    items: list[dict[str, object]] = []
    if isinstance(portal_list, dict):
        typed_portal = cast(dict[str, object], portal_list)
        maybe_items: object = typed_portal["items"] if "items" in typed_portal else []
        if isinstance(maybe_items, list):
            typed_items = cast(list[object], maybe_items)
            items = [item for item in typed_items if isinstance(item, dict)]
    existing = pick_portal_existing_option_index(items)
    if existing is not None:
        if await _click_portal_existing_option(page, portal.nth(existing), unique_tag):
            return "scoped:existing_option"
    index = pick_portal_create_index(items)
    if index is not None:
        if await _click_portal_create_footer(page, portal.nth(index), unique_tag):
            return "scoped:portal_footer"
    wrapper = page.locator("[data-testid='input-wrapper']").filter(
        has=page.locator("input[name='vendor']")
    )
    wrapper_list = observation.get("wrapper_list")
    if _snapshot_has_option(wrapper_list):
        if await _click_scoped_create_or_tag(
            page, wrapper.locator(".ds-dropdown-list"), unique_tag
        ):
            return "scoped:option"
    return None


def _snapshot_has_option(snapshot: object) -> bool:
    if not isinstance(snapshot, dict):
        return False
    typed = cast(dict[str, object], snapshot)
    return typed.get("has_create_footer") is True or typed.get("has_opret") is True


async def _click_portal_existing_option(page: _Page, list_root: _Locator, unique_tag: str) -> bool:
    option = list_root.get_by_text(unique_tag, exact=True)
    footer = list_root.get_by_text(portal_create_footer_label(unique_tag), exact=True)
    try:
        if await option.count() < 1 or not await option.first.is_visible():
            return False
        if await footer.count() >= 1:
            footer_box = await footer.first.bounding_box()
            option_box = await option.first.bounding_box()
            if footer_box is not None and option_box is not None:
                same = (
                    abs(float(footer_box["x"]) - float(option_box["x"])) < 1
                    and abs(float(footer_box["y"]) - float(option_box["y"])) < 1
                )
                if same:
                    return False
        await option.first.click(timeout=5000)
        await asyncio.sleep(0.3)
        return True
    except Exception:
        return False


async def _click_portal_create_footer(page: _Page, list_root: _Locator, unique_tag: str) -> bool:
    label = portal_create_footer_label(unique_tag)
    targets = (
        list_root.locator(PORTAL_FOOTER_WRAPPER),
        list_root.get_by_text(label, exact=True),
    )
    clicked = False
    for option in targets:
        try:
            if await option.count() < 1:
                continue
            await option.first.click(force=True, timeout=5000)
            clicked = True
            break
        except Exception:
            continue
    if not clicked:
        return False
    if await _confirm_new_vendor_modal(page, unique_tag, require_modal=True):
        return True
    try:
        leftover_count = await list_root.get_by_text(label, exact=True).count()
    except Exception:
        return leftover_footer_means_bound(leftover_count=None, count_failed=True)
    return leftover_footer_means_bound(leftover_count=leftover_count, count_failed=False)


async def _click_scoped_create_or_tag(page: _Page, root: _Locator, unique_tag: str) -> bool:
    try:
        count = await root.count()
    except Exception:
        return False
    if count < 1:
        return False
    return await _click_portal_create_footer(page, root.first, unique_tag)


async def _type_labeled(page: _Page, label: str, value: str) -> str | None:
    field = page.get_by_label(label, exact=True)
    try:
        if await field.count() < 1:
            return None
        target = field.first
        if not await target.is_visible():
            return None
        await target.click()
        await target.fill(value)
        await asyncio.sleep(0.3)
        return await target.input_value()
    except Exception:
        return None


async def _confirm_new_vendor_modal(
    page: _Page, unique_tag: str, *, require_modal: bool = False
) -> bool:
    modal = page.locator("div[class*='ModalWrapper'], [role='dialog']")
    save = modal.get_by_role("button", name="Gem", exact=True)
    for _ in range(20):
        if await save.count() >= 1 and await save.first.is_visible():
            break
        await asyncio.sleep(0.2)
    else:
        return not require_modal
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


async def _wait_vendor_dialog_gone(page: _Page) -> None:
    modal = page.locator("div[class*='ModalWrapper'], [role='dialog']")
    for _ in range(30):
        try:
            if await modal.count() < 1:
                return
            if not await modal.first.is_visible():
                return
        except Exception:
            return
        await asyncio.sleep(0.2)


def _leftover_kind(record: dict[str, object]) -> str | None:
    kind = record.get("kind")
    return kind if isinstance(kind, str) else None


async def _observe_leftover_portal(page: _Page, unique_tag: str) -> dict[str, object]:
    wrapper = page.locator("[data-testid='input-wrapper']").filter(
        has=page.locator("input[name='vendor']")
    )
    search_n = await _safe_count(wrapper.locator(VENDOR_SEARCH_TOGGLE))
    clear_n = await _safe_count(wrapper.locator(VENDOR_CLEAR))
    snapshot = await _list_snapshot(
        page.locator(".ds-dropdown-list.ds-moved-with-portal"), unique_tag
    )
    visible_count = 0
    has_opret = False
    has_empty = False
    maybe_items: object = snapshot.get("items")
    if isinstance(maybe_items, list):
        for raw in cast(list[object], maybe_items):
            if not isinstance(raw, dict):
                continue
            item = cast(dict[str, object], raw)
            if item.get("visible") is not True:
                continue
            visible_count += 1
            if item.get("has_opret") is True:
                has_opret = True
            if item.get("has_empty") is True:
                has_empty = True
    modal_heading = await _visible_create_vendor_modal(page)
    kind = leftover_portal_kind(
        visible=visible_count > 0,
        has_opret=has_opret,
        has_empty=has_empty,
        has_modal_heading=modal_heading,
    )
    record = leftover_inspect_record(
        kind=kind,
        visible_count=visible_count,
        has_opret=has_opret,
        has_empty=has_empty,
        search_trigger=search_n > 0,
        clear_trigger=clear_n > 0,
    )
    dump_leftover_portal(record)
    return record


async def _visible_create_vendor_modal(page: _Page) -> bool:
    modal = page.locator("div[class*='ModalWrapper'], [role='dialog']")
    try:
        count = await modal.count()
    except Exception:
        return False
    for index in range(min(count, 9)):
        node = modal.nth(index)
        try:
            if not await node.is_visible():
                continue
            heading = node.get_by_text(CREATE_VENDOR_LABEL, exact=True)
            if await heading.count() >= 1 and await heading.first.is_visible():
                return True
        except Exception:
            continue
    return False


async def _click_visible_create_vendor_gem(page: _Page) -> bool:
    modal = page.locator("div[class*='ModalWrapper'], [role='dialog']")
    try:
        count = await modal.count()
    except Exception:
        return False
    for index in range(min(count, 9)):
        node = modal.nth(index)
        try:
            if not await node.is_visible():
                continue
            heading = node.get_by_text(CREATE_VENDOR_LABEL, exact=True)
            if await heading.count() < 1 or not await heading.first.is_visible():
                continue
            save = node.get_by_role("button", name="Gem", exact=True)
            if await save.count() < 1 or not await save.first.is_visible():
                return False
            await save.first.click(timeout=5000)
            return True
        except Exception:
            continue
    return False


async def _click_vendor_search_toggle(page: _Page) -> bool:
    wrapper = page.locator("[data-testid='input-wrapper']").filter(
        has=page.locator("input[name='vendor']")
    )
    toggle = wrapper.locator(VENDOR_SEARCH_TOGGLE)
    try:
        if await toggle.count() < 1 or not await toggle.first.is_visible():
            return False
        await toggle.first.click(timeout=5000)
        return True
    except Exception:
        return False


async def _close_leftover_portal(page: _Page, unique_tag: str) -> dict[str, object]:
    observed = await _observe_leftover_portal(page, unique_tag)
    action = leftover_close_action(_leftover_kind(observed))
    if action is None:
        observed["blocked"] = False
        return observed
    closed = False
    if action == "search_toggle":
        closed = await _click_vendor_search_toggle(page)
    elif action == "modal_gem":
        closed = await _click_visible_create_vendor_gem(page)
    if not closed:
        observed["blocked"] = True
        observed["close_failed"] = True
        dump_leftover_portal(observed)
        return observed
    if action == "modal_gem":
        for _ in range(24):
            if not await _visible_create_vendor_modal(page):
                break
            await asyncio.sleep(0.25)
    else:
        await asyncio.sleep(0.3)
    after = await _observe_leftover_portal(page, unique_tag)
    after["closed"] = action
    delivery = await inspect_draft_save(page, DRAFT_SAVE)
    hit = delivery.get("hit_target")
    hit_name = hit if isinstance(hit, str) else None
    if leftover_portal_covers_save(hit_name):
        after["blocked"] = True
        after["hit_target"] = hit_name
        dump_leftover_portal(after)
        return after
    after["blocked"] = False
    after["hit_target"] = hit_name
    dump_leftover_portal(after)
    return after


async def _observe_date_field(page: _Page) -> dict[str, object]:
    field = page.locator(BILL_DATE)
    count = 0
    visible = False
    name: str | None = None
    value_len = -1
    for _ in range(20):
        try:
            count = await field.count()
            if count >= 1:
                visible = await field.first.is_visible()
                name = await field.first.get_attribute("name")
                try:
                    value_len = len(await field.first.input_value())
                except Exception:
                    value_len = -1
                break
        except Exception:
            count = 0
        await asyncio.sleep(0.2)
    return {
        "count": count,
        "visible": visible,
        "name": name,
        "value_len": value_len,
    }


async def _fill_named(
    page: _Page,
    selector: str,
    value: str,
    *,
    matches: Callable[[str, str], bool] | None = None,
    click_first: bool = True,
) -> str | None:
    current = await _type_into(page, selector, value, tab=True, click_first=click_first)
    if current is None:
        return None
    ok = current == value if matches is None else matches(current, value)
    return current if ok else None


async def _fill_draft_fields(
    page: _Page, unique_tag: str, *, bind_vendor: bool = True
) -> dict[str, str] | ToolError:
    bill_date = date.today().strftime("%d.%m.%Y")
    amount = "1"
    vendor_bind = "kept"
    if bind_vendor:
        vendor_bind = await _fill_vendor(page, unique_tag)
        if vendor_bind is None:
            return ToolError(
                code=StableErrorCode.UI_CHANGED,
                message="Billy bill draft fields are not visible.",
                details={"field": "vendor", "source": "scoped_leverandor_wrapper"},
            )
        await _wait_vendor_dialog_gone(page)
        if vendor_bind == "scoped:existing_option":
            leftover_close_after_existing_option()
        else:
            leftover = await _close_leftover_portal(page, unique_tag)
            if leftover.get("blocked"):
                return ToolError(
                    code=StableErrorCode.UI_CHANGED,
                    message="Billy leftover Leverandør portal has no safe close.",
                    details={"source": "leftover_portal", "leftover": leftover},
                )
    date_obs = await _observe_date_field(page)
    dump_date_chrome(date_obs)
    if date_obs.get("count", 0) == 0:
        return ToolError(
            code=StableErrorCode.UI_CHANGED,
            message="Billy bill draft fields are not visible.",
            details={"field": "date", "selector": BILL_DATE, "observation": date_obs},
        )
    actual_date = await _fill_named(
        page, BILL_DATE, bill_date, matches=dates_match, click_first=False
    )
    after_fill = await _observe_date_field(page)
    dump_date_chrome({"before": date_obs, "after_fill": after_fill, "wanted_len": len(bill_date)})
    if actual_date is None:
        actual_date = await _type_labeled(page, "Bilagsdato", bill_date)
        if actual_date is not None and not dates_match(actual_date, bill_date):
            actual_date = None
    if actual_date is None:
        return ToolError(
            code=StableErrorCode.UI_CHANGED,
            message="Billy bill draft fields are not visible.",
            details={"field": "date", "selector": BILL_DATE, "observation": after_fill},
        )
    actual_amount = await _fill_named(
        page, LINE_AMOUNT, amount, matches=amounts_match, click_first=False
    )
    if actual_amount is None:
        return ToolError(
            code=StableErrorCode.UI_CHANGED,
            message="Billy bill draft fields are not visible.",
            details={"field": "line_amount", "selector": LINE_AMOUNT},
        )
    actual_desc = await _fill_named(page, LINE_DESCRIPTION, unique_tag, click_first=False)
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


def _event_url(event: object) -> str:
    url = str(getattr(event, "url", "") or "")
    if url:
        return url
    request = getattr(event, "request", event)
    return str(getattr(request, "url", "") or "")


def _event_method(event: object) -> str:
    request = getattr(event, "request", event)
    return str(getattr(request, "method", "") or getattr(event, "method", "") or "")


def _event_path(event: object) -> str:
    url = _event_url(event)
    if "api.billysbilling.com" not in url:
        return ""
    return urlsplit(url).path


def _event_failure(event: object) -> str:
    failure = getattr(event, "failure", "")
    if callable(failure):
        try:
            failure = failure()
        except Exception:
            failure = "failed"
    return str(failure or "failed")


def _watch_bill_traffic(page: _Page) -> tuple[list[str], dict[str, object], list[str]]:
    seen: list[str] = []
    bodies: dict[str, object] = {}
    requests: list[str] = []

    def _on_request(event: object) -> None:
        item = record_bill_watch_item(
            kind="request", method=_event_method(event), path=_event_path(event)
        )
        if item is not None:
            requests.append(item)

    def _on_response(event: object) -> None:
        item = record_bill_watch_item(
            kind="response",
            method=_event_method(event),
            path=_event_path(event),
            status=str(getattr(event, "status", "") or ""),
        )
        if item is not None:
            seen.append(item)
            bodies[item] = event

    def _on_failed(event: object) -> None:
        item = record_bill_watch_item(
            kind="failed",
            method=_event_method(event),
            path=_event_path(event),
            failure=_event_failure(event),
        )
        if item is not None:
            requests.append(item)
            seen.append(item)

    page.on("request", _on_request)
    page.on("response", _on_response)
    page.on("requestfailed", _on_failed)
    return seen, bodies, requests


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


def persist_dump_path(*, create: bool) -> Path:
    """Keep the create POST persist dump off the later PUT/DELETE overwrite path."""

    if create:
        return CREATE_PERSIST_DUMP
    return _PERSIST_DUMP


def _dump_persist(
    page: _Page,
    unique_tag: str,
    failed: ToolError | None,
    seen: list[str] | None = None,
    requests: list[str] | None = None,
    *,
    destination: Path | None = None,
) -> None:
    path = destination if destination is not None else _PERSIST_DUMP
    _write_json(
        path,
        {
            "url": page.url,
            "tag_len": len(unique_tag),
            "failed_code": None if failed is None else failed.code,
            "failed_details": None if failed is None else failed.details,
            "watched": list(seen or []),
            "requests": list(requests or []),
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
