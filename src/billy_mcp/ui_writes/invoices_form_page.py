"""Page protocol and exact-click helpers for draft invoice writes."""

from __future__ import annotations

import asyncio
import inspect
import json
import re
from pathlib import Path
from typing import Protocol
from urllib.parse import urlsplit

from pydantic import BaseModel, ConfigDict, ValidationError

from billy_mcp.models import StableErrorCode, ToolError

CREATE_PERSIST_DUMP = (
    Path.home() / ".local" / "share" / "billy-mcp" / "inspect-live-invoices-create-persist.json"
)
DRAFT_SAVE = "Gem som kladde"
UPDATE_SAVE = "Opdater"
DELETE = "Slet"
MORE = "Mere"
CONFIRM_DELETE = "Ja, slet faktura"
_OK_STATUS = frozenset({"200", "201", "204"})


class Locator(Protocol):
    @property
    def first(self) -> Locator: ...

    async def count(self) -> int: ...

    async def is_visible(self) -> bool: ...

    async def click(self, **kwargs: object) -> None: ...

    async def fill(self, value: str) -> None: ...

    async def press_sequentially(self, text: str) -> None: ...

    async def dispatch_event(self, event_type: str, **kwargs: object) -> None: ...

    async def press(self, key: str) -> None: ...

    async def inner_text(self) -> str: ...

    async def get_attribute(self, name: str) -> str | None: ...

    async def input_value(self) -> str: ...

    async def bounding_box(self, **kwargs: object) -> dict[str, float] | None: ...

    def nth(self, index: int) -> Locator: ...

    def get_by_text(self, text: str | re.Pattern[str], **kwargs: object) -> Locator: ...

    def locator(self, selector: str) -> Locator: ...

    def filter(self, **kwargs: object) -> Locator: ...


class Mouse(Protocol):
    async def click(self, x: float, y: float) -> None: ...


class Page(Protocol):
    @property
    def url(self) -> str: ...

    @property
    def mouse(self) -> Mouse: ...

    def locator(self, selector: str) -> Locator: ...

    def get_by_label(self, text: str, **kwargs: object) -> Locator: ...

    def get_by_role(self, role: str, **kwargs: object) -> Locator: ...

    def get_by_text(self, text: str | re.Pattern[str], **kwargs: object) -> Locator: ...

    async def goto(self, url: str, **kwargs: object) -> object: ...

    async def wait_for_load_state(self, state: str, **kwargs: object) -> None: ...

    async def close(self) -> None: ...

    def on(self, event: str, handler: object) -> None: ...

    def add_init_script(self, script: str, **kwargs: object) -> object: ...

    async def evaluate(self, expression: str, arg: object = None) -> object: ...


async def click_exact(page: Page, label: str) -> ToolError | None:
    """Click the exact visible button or text. Substring matches are not a click."""

    control = page.get_by_role("button", name=label, exact=True)
    if await control.count() < 1:
        control = page.get_by_text(label, exact=True)
    if await control.count() < 1 or not await control.first.is_visible():
        return ToolError(
            code=StableErrorCode.UI_CHANGED,
            message=f"Billy control {label} is not visible.",
        )
    if await control.first.bounding_box() is None:
        return ToolError(
            code=StableErrorCode.UI_CHANGED,
            message=f"Billy control {label} has no box.",
        )
    await control.first.click()
    return None


async def visible_button(page: Page, label: str) -> bool:
    """True when an exact-named button is visible."""

    control = page.get_by_role("button", name=label, exact=True)
    return await control.count() >= 1 and await control.first.is_visible()


def watch_invoice_response(event: object, seen: list[str]) -> None:
    """Record create POST, SPA invoice PUT, line PUT, and invoice DELETE."""

    url = str(getattr(event, "url", ""))
    method = str(getattr(event, "method", "") or "")
    request = getattr(event, "request", None)
    if request is not None:
        method = str(getattr(request, "method", "") or method)
    raw_status = getattr(event, "status", None)
    if raw_status is None or raw_status == "":
        return
    status = str(raw_status)
    path = urlsplit(url).path
    if method == "POST" and path.rstrip("/").endswith("/v2/invoices"):
        seen.append(f"{method} {status} {url}")
        return
    if method == "PUT" and "/v2/invoiceLines/" in path:
        seen.append(f"{method} {status} {url}")
        return
    if (
        method == "PUT"
        and "/v2/invoices/" in path
        and "/invoiceLines/" not in path
        and "/emails" not in path
    ):
        seen.append(f"{method} {status} {url}")
        return
    if method == "DELETE" and "/v2/invoices/" in path and "/invoiceLines/" not in path:
        seen.append(f"{method} {status} {url}")


async def persist_created_invoice_id(events: list[object]) -> str | None:
    """Read invoices.0.id from a successful create POST. Stores no other fields."""

    for event in events:
        request = getattr(event, "request", None)
        method = str(getattr(request, "method", "") if request is not None else "")
        url = str(getattr(event, "url", "")).split("?", 1)[0]
        status = str(getattr(event, "status", ""))
        if method != "POST" or not url.endswith("/v2/invoices") or status not in _OK_STATUS:
            continue
        reader = getattr(event, "json", None)
        if reader is None:
            continue
        payload: object = reader()
        if inspect.isawaitable(payload):
            payload = await payload
        found = invoice_id_from_payload(payload)
        if found is not None:
            return found
    return None


class _InvoiceIdRow(BaseModel):
    """One invoices[] row. Extra Billy fields are ignored."""

    model_config = ConfigDict(frozen=True, extra="ignore")

    id: str


class _InvoiceCreateBody(BaseModel):
    """Create POST body. Only invoices[].id is kept."""

    model_config = ConfigDict(frozen=True, extra="ignore")

    invoices: list[_InvoiceIdRow]


def invoice_id_from_payload(payload: object) -> str | None:
    """Parse invoices.0.id from a create POST body."""

    try:
        parsed = _InvoiceCreateBody.model_validate(payload)
    except ValidationError:
        return None
    if not parsed.invoices:
        return None
    found = parsed.invoices[0].id.strip()
    return found or None


def persist_hit(item: str, method: str) -> bool:
    """True only for a named write with a 2xx status on the persist path."""

    if not item.startswith(f"{method} "):
        return False
    parts = item.split()
    if len(parts) < 3:
        return False
    status, url = parts[1], parts[2]
    if status not in _OK_STATUS:
        return False
    path = urlsplit(url).path
    if method == "POST":
        return path.rstrip("/").endswith("/v2/invoices")
    if method == "PUT":
        return "/v2/invoiceLines/" in path
    if method == "DELETE":
        return "/v2/invoices/" in path and "/invoiceLines/" not in path
    return False


def invoice_save_hit(item: str) -> bool:
    """True for a 2xx SPA draft save PUT. Line-price persist is still a fresh session."""

    if not item.startswith("PUT "):
        return False
    parts = item.split()
    if len(parts) < 3:
        return False
    status, url = parts[1], parts[2]
    if status not in _OK_STATUS:
        return False
    path = urlsplit(url).path
    if "/v2/invoiceLines/" in path:
        return True
    return "/v2/invoices/" in path and "/invoiceLines/" not in path and "/emails" not in path


async def wait_persist(seen: list[str], *, method: str) -> ToolError | None:
    """Wait for a 2xx persist XHR of the named method."""

    for _ in range(40):
        if method == "PUT":
            hit = any(invoice_save_hit(item) for item in seen)
        else:
            hit = any(persist_hit(item, method) for item in seen)
        if hit:
            write_json(CREATE_PERSIST_DUMP, {"watched": list(seen), "method": method})
            return None
        await asyncio.sleep(0.25)
    return ToolError(
        code=StableErrorCode.BILLY_ERROR,
        message="Billy draft invoice write did not persist.",
        details={"watched": list(seen), "method": method},
    )


def slug_from(url: str) -> str | None:
    """First path segment of a Billy UI URL, or None on login/root."""

    parts = [part for part in (urlsplit(url).path or "").split("/") if part]
    if parts and parts[0] != "login":
        return parts[0]
    return None


def write_json(path: Path, payload: object) -> None:
    """Best-effort owner-only dump. Swallow filesystem errors."""

    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload, default=str, indent=2) + "\n", encoding="utf-8")
    except OSError:
        return
