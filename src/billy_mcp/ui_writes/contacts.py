"""Ticketed UI contact create, update, and delete tools."""

from __future__ import annotations

import asyncio
import json
import re
from collections.abc import Awaitable, Callable
from pathlib import Path
from typing import Protocol, cast
from urllib.parse import urlsplit

from fastmcp import FastMCP
from pydantic import BaseModel, ConfigDict, Field, JsonValue

from billy_mcp.browser import BrowserRuntime
from billy_mcp.models import StableErrorCode, ToolError
from billy_mcp.ui_writes.browser_submit import default_browser_runtime
from billy_mcp.ui_writes.page_flow import prove_text_on_fresh_page
from billy_mcp.ui_writes.protocol import (
    UiWriteExecuteInput,
    UiWritePreviewResult,
    UiWriteProtocol,
)

_RET = re.compile(r"^Ret$")
_SEARCH = "input[type='search'], input[placeholder*='øg' i]"
_NAME = "input[name='name']"
_OPTIONAL_FIELDS = (
    ("street", "Testvej 1"),
    ("zipcode", "2100"),
    ("city", "København"),
)


class ClientsCreatePreviewInput(BaseModel):
    """Flat preview input for creating one customer in the Billy interface."""

    model_config = ConfigDict(extra="forbid")

    name: str = Field(min_length=1)
    organization_id: str = Field(min_length=1)


class ClientsUpdatePreviewInput(BaseModel):
    """Flat preview input for renaming one customer in the Billy interface."""

    model_config = ConfigDict(extra="forbid")

    name: str = Field(min_length=1)
    new_name: str = Field(min_length=1)
    organization_id: str = Field(min_length=1)


class ClientsDeletePreviewInput(BaseModel):
    """Flat preview input for deleting one customer in the Billy interface."""

    model_config = ConfigDict(extra="forbid")

    name: str = Field(min_length=1)
    organization_id: str = Field(min_length=1)


class UiContactWriteResult(BaseModel):
    """Result of a consumed ticket after the bound interface action runs once."""

    model_config = ConfigDict(extra="forbid")

    summary: str = Field(min_length=1)
    canonical_request: dict[str, JsonValue]
    expected_effect_state: dict[str, JsonValue]
    submitted: bool = True


class ContactUiActor(Protocol):
    """Submits the exact previewed interface action. Preview must never call this."""

    def submit_create(
        self, request: dict[str, JsonValue], organization_id: str = ""
    ) -> Awaitable[object]: ...

    def submit_update(
        self, request: dict[str, JsonValue], organization_id: str = ""
    ) -> Awaitable[object]: ...

    def submit_delete(
        self, request: dict[str, JsonValue], organization_id: str = ""
    ) -> Awaitable[object]: ...


class _Locator(Protocol):
    @property
    def first(self) -> _Locator: ...

    def nth(self, index: int) -> _Locator: ...

    async def count(self) -> int: ...

    async def is_visible(self) -> bool: ...

    async def click(self) -> None: ...

    async def fill(self, value: str) -> None: ...

    async def inner_text(self) -> str: ...

    async def evaluate(self, expression: str) -> object: ...

    async def press(self, key: str) -> None: ...

    async def press_sequentially(self, text: str) -> None: ...


class _Page(Protocol):
    @property
    def url(self) -> str: ...

    async def goto(self, url: str, *, wait_until: str) -> object: ...

    def locator(self, selector: str) -> _Locator: ...

    def get_by_role(self, role: str, *, name: re.Pattern[str]) -> _Locator: ...

    def get_by_text(self, text: str, *, exact: bool = False) -> _Locator: ...

    async def close(self) -> None: ...

    async def wait_for_load_state(self, state: str, *, timeout: float | None = None) -> None: ...


class BrowserContactUiActor:
    """Drive create, update, and delete on a logged-in Billy interface session."""

    def __init__(
        self,
        runtime: BrowserRuntime,
        *,
        readback_runtime: BrowserRuntime | None = None,
        org_identity_path: Path | None = None,
    ) -> None:
        self._runtime = runtime
        self._readback_runtime = readback_runtime or runtime.independent_readback_runtime()
        self._org_identity_path = org_identity_path or (
            Path.home() / ".local" / "share" / "billy-mcp" / "ui-org-identity.json"
        )

    async def submit_create(
        self, request: dict[str, JsonValue], organization_id: str = ""
    ) -> object:
        name = _require_name(request, "name")
        return await self._with_page(
            _create_customer, name, organization_id=organization_id, readback_text=name
        )

    async def submit_update(
        self, request: dict[str, JsonValue], organization_id: str = ""
    ) -> object:
        new_name = _require_name(request, "new_name")
        return await self._with_page(
            _update_customer,
            _require_name(request, "name"),
            new_name,
            organization_id=organization_id,
            readback_text=new_name,
        )

    async def submit_delete(
        self, request: dict[str, JsonValue], organization_id: str = ""
    ) -> object:
        name = _require_name(request, "name")
        return await self._with_page(
            _delete_customer,
            name,
            organization_id=organization_id,
            readback_text=name,
            readback_absent=True,
        )

    async def _with_page(
        self,
        work: Callable[..., Awaitable[object]],
        *args: str,
        organization_id: str,
        readback_text: str,
        readback_absent: bool = False,
    ) -> object:
        page: _Page | None = None
        try:
            bound = organization_id.strip()
            if not bound:
                return ToolError(
                    code=StableErrorCode.ORGANIZATION_REQUIRED,
                    message="A proven Billy organisation id is required.",
                )
            context = await self._runtime.start()
            page = cast(_Page, await context.new_page())
            await page.goto("https://mit.billy.dk/", wait_until="domcontentloaded")
            await _settle(page)
            slug = _slug_from(page.url)
            if slug is None and _is_org_less_root(page.url):
                await page.goto(
                    f"https://mit.billy.dk/{bound}/clients", wait_until="domcontentloaded"
                )
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
            submitted = await work(page, slug, *args)
            if isinstance(submitted, ToolError):
                return submitted
            proved = await prove_text_on_fresh_page(
                self._readback_runtime,
                organization_id=bound,
                path="clients",
                text=readback_text,
                absent=readback_absent,
            )
            if proved is not None:
                return proved
            return submitted
        except Exception as exc:
            return ToolError(
                code=StableErrorCode.BILLY_ERROR,
                message="Billy interface contact write could not be completed.",
                details={"error": type(exc).__name__},
            )
        finally:
            if page is not None:
                try:
                    await page.close()
                except Exception:
                    pass


def register_ui_contact_write_tools(
    server: FastMCP,
    protocol: UiWriteProtocol,
    actor: ContactUiActor | None = None,
    runtime: BrowserRuntime | None = None,
    readback_runtime: BrowserRuntime | None = None,
) -> None:
    """Register the six UI contact preview and execute tools."""

    bound: ContactUiActor | None = actor

    def _actor() -> ContactUiActor:
        nonlocal bound
        if bound is None:
            write = runtime or default_browser_runtime()
            bound = BrowserContactUiActor(write, readback_runtime=readback_runtime)
        return bound

    def ui_clients_create_preview(
        name: str = Field(min_length=1),
        organization_id: str = Field(min_length=1),
    ) -> UiWritePreviewResult | ToolError:
        """Preview creating one Billy customer. Does not submit."""

        parsed = ClientsCreatePreviewInput(name=name, organization_id=organization_id)
        return protocol.preview(
            execute_tool_name="ui_clients_create_execute",
            organization_id=parsed.organization_id,
            target="clients",
            canonical_request={"action": "create", "name": parsed.name},
            expected_effect_state={"action": "create", "resource": "contact"},
            summary="Create one Billy customer in the interface.",
        )

    async def ui_clients_create_execute(
        confirmation_ticket: str = Field(min_length=1),
    ) -> UiContactWriteResult | ToolError:
        """Execute the previewed customer create exactly once."""

        return await _execute(
            protocol,
            _actor(),
            confirmation_ticket,
            "ui_clients_create_execute",
            "submit_create",
        )

    def ui_clients_update_preview(
        name: str = Field(min_length=1),
        new_name: str = Field(min_length=1),
        organization_id: str = Field(min_length=1),
    ) -> UiWritePreviewResult | ToolError:
        """Preview renaming one Billy customer. Does not submit."""

        parsed = ClientsUpdatePreviewInput(
            name=name, new_name=new_name, organization_id=organization_id
        )
        return protocol.preview(
            execute_tool_name="ui_clients_update_execute",
            organization_id=parsed.organization_id,
            target="clients",
            canonical_request={
                "action": "update",
                "name": parsed.name,
                "new_name": parsed.new_name,
            },
            expected_effect_state={
                "action": "update",
                "resource": "contact",
                "name": name,
                "new_name": new_name,
            },
            summary="Update one Billy customer in the interface.",
        )

    async def ui_clients_update_execute(
        confirmation_ticket: str = Field(min_length=1),
    ) -> UiContactWriteResult | ToolError:
        """Execute the previewed customer update exactly once."""

        return await _execute(
            protocol,
            _actor(),
            confirmation_ticket,
            "ui_clients_update_execute",
            "submit_update",
        )

    def ui_clients_delete_preview(
        name: str = Field(min_length=1),
        organization_id: str = Field(min_length=1),
    ) -> UiWritePreviewResult | ToolError:
        """Preview deleting one Billy customer. Does not submit."""

        parsed = ClientsDeletePreviewInput(name=name, organization_id=organization_id)
        return protocol.preview(
            execute_tool_name="ui_clients_delete_execute",
            organization_id=parsed.organization_id,
            target="clients",
            canonical_request={"action": "delete", "name": parsed.name},
            expected_effect_state={"action": "delete", "resource": "contact", "name": name},
            summary="Delete one Billy customer in the interface.",
        )

    async def ui_clients_delete_execute(
        confirmation_ticket: str = Field(min_length=1),
    ) -> UiContactWriteResult | ToolError:
        """Execute the previewed customer delete exactly once."""

        return await _execute(
            protocol,
            _actor(),
            confirmation_ticket,
            "ui_clients_delete_execute",
            "submit_delete",
        )

    server.tool(
        name="ui_clients_create_preview",
        description="Preview creating one Billy customer without submitting the form.",
    )(ui_clients_create_preview)
    server.tool(
        name="ui_clients_create_execute",
        description="Execute a previewed Billy customer create with its confirmation ticket.",
    )(ui_clients_create_execute)
    server.tool(
        name="ui_clients_update_preview",
        description="Preview renaming one Billy customer without submitting the form.",
    )(ui_clients_update_preview)
    server.tool(
        name="ui_clients_update_execute",
        description="Execute a previewed Billy customer update with its confirmation ticket.",
    )(ui_clients_update_execute)
    server.tool(
        name="ui_clients_delete_preview",
        description="Preview deleting one Billy customer without confirming deletion.",
    )(ui_clients_delete_preview)
    server.tool(
        name="ui_clients_delete_execute",
        description="Execute a previewed Billy customer delete with its confirmation ticket.",
    )(ui_clients_delete_execute)


async def _execute(
    protocol: UiWriteProtocol,
    actor: ContactUiActor,
    confirmation_ticket: str,
    execute_tool_name: str,
    method_name: str,
) -> UiContactWriteResult | ToolError:
    prepared = protocol.consume(
        UiWriteExecuteInput(confirmation_ticket=confirmation_ticket),
        execute_tool_name=execute_tool_name,
    )
    if isinstance(prepared, ToolError):
        return prepared
    organization_id = str(prepared.binding.organization_id or "")
    if method_name == "submit_create":
        submitted = await actor.submit_create(
            prepared.canonical_request, organization_id=organization_id
        )
    elif method_name == "submit_update":
        submitted = await actor.submit_update(
            prepared.canonical_request, organization_id=organization_id
        )
    elif method_name == "submit_delete":
        submitted = await actor.submit_delete(
            prepared.canonical_request, organization_id=organization_id
        )
    else:
        return ToolError(
            code=StableErrorCode.VALIDATION_ERROR,
            message="Unknown UI contact execute action.",
        )
    if isinstance(submitted, ToolError):
        return submitted
    return UiContactWriteResult(
        summary=prepared.summary,
        canonical_request=prepared.canonical_request,
        expected_effect_state=prepared.expected_effect_state,
        submitted=True,
    )


def _require_name(request: dict[str, JsonValue], key: str) -> str:
    value = request.get(key)
    if not isinstance(value, str) or not value:
        raise ValueError(f"canonical request missing {key}")
    return value


def _slug_from(url: str) -> str | None:
    """Return the live URL org slug only. Never fall back to a stored identity file."""

    path = urlsplit(url).path or ""
    parts = [part for part in path.split("/") if part]
    if parts and parts[0] not in {"login", ""}:
        return parts[0]
    return None


def _is_org_less_root(url: str) -> bool:
    path = urlsplit(url).path or ""
    parts = [part for part in path.split("/") if part]
    return not parts


async def _settle(page: _Page) -> None:
    try:
        await page.wait_for_load_state("networkidle", timeout=15000)
    except Exception:
        pass


async def _goto_clients(page: _Page, slug: str) -> None:
    await page.goto(f"https://mit.billy.dk/{slug}/clients", wait_until="domcontentloaded")
    await _settle(page)


_NAME_FORM_SAVE_JS = """el => {
  const isGem = (node) => {
    const text = (node.innerText || node.value || node.getAttribute('aria-label') || '')
      .trim().split(/\\n/)[0];
    return text === 'Gem' || text === 'Gem ændringer';
  };
  let root = el.parentElement;
  while (root) {
    const controls = root.querySelectorAll('button, a, [role="button"], input[type="submit"]');
    for (const control of controls) {
      if (!isGem(control)) continue;
      const style = window.getComputedStyle(control);
      const rect = control.getBoundingClientRect();
      if (style.display === 'none' || style.visibility === 'hidden' || rect.width === 0) {
        continue;
      }
      control.click();
      return true;
    }
    root = root.parentElement;
  }
  return false;
}"""


_NAME_FORM_GEM_XPATH = (
    "xpath=//input[@name='name']/ancestor::*[.//*[(self::button or self::a or @role='button')"
    " and normalize-space()='Gem']][1]//*[(self::button or self::a or @role='button')"
    " and normalize-space()='Gem']"
)
_NAME_FORM_GEM_AENDRINGER_XPATH = (
    "xpath=//input[@name='name']/ancestor::*[.//*[(self::button or self::a or @role='button')"
    " and normalize-space()='Gem ændringer']][1]"
    "//*[(self::button or self::a or @role='button') and normalize-space()='Gem ændringer']"
)


async def _click_name_form_save(page: _Page) -> bool:
    """Click the Gem that shares a container with input[name=name]. Skip decoys."""

    save_button = page.locator("button[data-cy='save-button']")
    try:
        if await save_button.count() >= 1 and await save_button.first.is_visible():
            await save_button.first.click()
            await _settle(page)
            return True
    except Exception:
        pass
    for selector in (_NAME_FORM_GEM_XPATH, _NAME_FORM_GEM_AENDRINGER_XPATH):
        locator = page.locator(selector)
        try:
            if await locator.count() >= 1 and await locator.first.is_visible():
                await locator.first.click()
                await _settle(page)
                return True
        except Exception:
            continue
    field = page.locator(_NAME)
    try:
        if await field.count() < 1 or not await field.first.is_visible():
            return False
        clicked = await field.first.evaluate(_NAME_FORM_SAVE_JS)
    except Exception:
        return False
    if clicked:
        await _settle(page)
        return True
    return False


async def _click_dialog_save(page: _Page) -> bool:
    """Click the create-dialog Gem. Never match Gem kommentar via substring."""

    return await _click_exact_label(page, "Gem ændringer") or await _click_exact_label(
        page, "Gem", reverse=True
    )


async def _click_save(page: _Page) -> bool:
    """Click the customer-page save control. Prefer data-cy=save-button."""

    if await _click_name_form_save(page):
        return True
    return await _click_dialog_save(page)


async def _click_visible(
    locator: _Locator, *, settle_page: _Page, settle: bool, reverse: bool = False
) -> bool:
    try:
        count = await locator.count()
        indexes = range(count - 1, -1, -1) if reverse else range(min(count, 8))
        for index in indexes:
            candidate = locator.nth(index)
            if not await candidate.is_visible():
                continue
            await candidate.click()
            if settle:
                await _settle(settle_page)
            return True
    except Exception:
        return False
    return False


async def _click_exact_label(
    page: _Page, label: str, *, settle: bool = True, reverse: bool = False
) -> bool:
    """Click a visible control whose name is exactly label.

    Never substring-match Opret or Gem kommentar.
    """

    pattern = re.compile(rf"^{re.escape(label)}$")
    for role in ("button", "link"):
        if await _click_visible(
            page.get_by_role(role, name=pattern),
            settle_page=page,
            settle=settle,
            reverse=reverse,
        ):
            return True
    return await _click_visible(
        page.get_by_text(label, exact=True),
        settle_page=page,
        settle=settle,
        reverse=reverse,
    )


async def _click_named(page: _Page, pattern: re.Pattern[str], *, settle: bool = True) -> bool:
    button = page.get_by_role("button", name=pattern)
    try:
        if await button.count() >= 1 and await button.first.is_visible():
            await button.first.click()
            if settle:
                await _settle(page)
            return True
    except Exception:
        pass
    text = page.locator(f"text={pattern.pattern.strip('^$')}")
    try:
        if await text.count() >= 1 and await text.first.is_visible():
            await text.first.click()
            if settle:
                await _settle(page)
            return True
    except Exception:
        return False
    return False


async def _open_edit_name(page: _Page, new_name: str) -> bool:
    """Open Ret once, then fill name. A second Ret click can close the form."""

    if await _fill_name(page, new_name):
        return True
    if not await _click_exact_label(page, "Ret"):
        return False
    return await _fill_name(page, new_name)


async def _confirm_delete_customer(page: _Page) -> bool:
    """Mere, then Slet kontakt, then Ja, slet or Slet. Never click Arkivér."""

    await _settle(page)
    if not await _wait_and_click(page, "Mere"):
        return False
    if not await _wait_and_click(page, "Slet kontakt"):
        return False
    return await _wait_and_click(page, "Ja, slet") or await _wait_and_click(page, "Slet")


async def _delete_chrome_flags(page: _Page) -> dict[str, int]:
    mere = 0
    slet_kontakt = 0
    slet = 0
    try:
        mere = await page.get_by_role("button", name=re.compile(r"^Mere$")).count()
    except Exception:
        mere = -1
    try:
        slet_kontakt = await page.get_by_text("Slet kontakt", exact=True).count()
    except Exception:
        slet_kontakt = -1
    try:
        slet = await page.get_by_role("button", name=re.compile(r"^Slet$")).count()
    except Exception:
        slet = -1
    return {"mere_exact": mere, "slet_kontakt": slet_kontakt, "slet_exact": slet}


async def _wait_and_click(page: _Page, label: str) -> bool:
    for _ in range(20):
        if await _click_exact_label(page, label):
            return True
        await asyncio.sleep(0.25)
    return False


async def _press_name_field(page: _Page, key: str) -> None:
    field = page.locator(_NAME)
    try:
        await field.first.press(key)
    except Exception:
        return


async def _commit_name_field(page: _Page) -> None:
    """Leave the name field so Billy enables the real save control."""

    await _press_name_field(page, "Tab")
    await _settle(page)


async def _fill_name(page: _Page, value: str) -> bool:
    field = page.locator(_NAME)
    try:
        if await field.count() < 1 or not await field.first.is_visible():
            return False
        target = field.first
        await target.click()
        try:
            await target.press("Meta+A")
        except Exception:
            try:
                await target.press("Control+A")
            except Exception:
                await target.fill("")
        try:
            await target.press_sequentially(value)
        except Exception:
            await target.fill(value)
        payload = json.dumps(value)
        await target.evaluate(
            "el => { const value = " + payload + "; const desc = Object.getOwnPropertyDescriptor("
            "window.HTMLInputElement.prototype, 'value');"
            " if (desc && desc.set) { desc.set.call(el, value); }"
            " el.dispatchEvent(new Event('input', {bubbles: true}));"
            " el.dispatchEvent(new Event('change', {bubbles: true}));"
            " const jq = (window.Ember && window.Ember.$) ? window.Ember.$(el)"
            " : (window.jQuery ? window.jQuery(el) : null);"
            " if (jq) { jq.val(value).trigger('input').trigger('change')"
            ".trigger('keyup'); } }"
        )
    except Exception:
        return False
    return True


async def _search_name(page: _Page, name: str) -> None:
    search = page.locator(_SEARCH)
    if await search.count() >= 1:
        await search.first.fill(name)
        await asyncio.sleep(1)


def _is_contact_detail_path(url: str) -> bool:
    path = urlsplit(url).path or ""
    return "/contacts/" in path and "/customer" in path


async def _wait_until_detail(page: _Page) -> bool:
    for _ in range(20):
        if _is_contact_detail_path(page.url):
            return True
        await asyncio.sleep(0.25)
    return _is_contact_detail_path(page.url)


async def _open_named_customer(page: _Page, name: str) -> bool:
    """Open the contact row. Never treat the search box value as the row."""

    await _search_name(page, name)
    for _ in range(20):
        row = page.locator(f'table tbody tr:has-text("{name}")')
        try:
            if await row.count() >= 1 and await row.first.is_visible():
                await row.first.click()
                if await _wait_until_detail(page):
                    return True
        except Exception:
            pass
        link = page.locator(f'a:has-text("{name}")')
        try:
            if await link.count() >= 1 and await link.first.is_visible():
                await link.first.click()
                if await _wait_until_detail(page):
                    return True
        except Exception:
            pass
        match = page.get_by_text(name, exact=False)
        count = await match.count()
        for index in range(count - 1, -1, -1):
            candidate = match.nth(index)
            try:
                if not await candidate.is_visible():
                    continue
                await candidate.click()
                if await _wait_until_detail(page):
                    return True
            except Exception:
                continue
        await asyncio.sleep(0.25)
    return False


async def _create_customer(page: _Page, slug: str, name: str) -> object:
    await _goto_clients(page, slug)
    filled = False
    for _ in range(30):
        await _click_named(page, re.compile(r"^Opret kontakt$"), settle=False)
        cta = page.locator("text=Opret kontakt")
        try:
            if await cta.count() >= 1 and await cta.first.is_visible():
                await cta.first.click()
        except Exception:
            pass
        await _settle(page)
        if await _fill_name(page, name):
            filled = True
            break
        await asyncio.sleep(0.2)
    if not filled:
        return ToolError(
            code=StableErrorCode.UI_CHANGED,
            message="Billy customer name field is not visible.",
        )
    for field_name, sample in _OPTIONAL_FIELDS:
        extra = page.locator(f"input[name='{field_name}']")
        try:
            if await extra.count() >= 1 and await extra.first.is_visible():
                await extra.first.fill(sample)
        except Exception:
            continue
    if not await _click_dialog_save(page):
        return ToolError(
            code=StableErrorCode.UI_CHANGED,
            message="Billy save control is not visible.",
        )
    await _settle(page)
    await asyncio.sleep(2)
    return {"ok": True}


async def _update_customer(page: _Page, slug: str, name: str, new_name: str) -> object:
    await _goto_clients(page, slug)
    if not await _open_named_customer(page, name):
        return ToolError(
            code=StableErrorCode.NOT_FOUND,
            message="Billy customer was not found for update.",
        )
    if not await _open_edit_name(page, new_name):
        return ToolError(
            code=StableErrorCode.UI_CHANGED,
            message="Billy customer name field is not visible.",
        )
    await _commit_name_field(page)
    if not await _click_save(page):
        return ToolError(
            code=StableErrorCode.UI_CHANGED,
            message="Billy save control is not visible.",
        )
    await _settle(page)
    await _goto_clients(page, slug)
    for _ in range(8):
        await _search_name(page, new_name)
        if await page.get_by_text(new_name, exact=True).count() >= 1:
            return {"ok": True}
        await asyncio.sleep(0.5)
    return ToolError(
        code=StableErrorCode.NOT_FOUND,
        message="Billy customer rename was not visible on the list after save.",
    )


async def _delete_customer(page: _Page, slug: str, name: str) -> object:
    await _goto_clients(page, slug)
    if not await _open_named_customer(page, name):
        path = urlsplit(page.url).path or ""
        parts = [part for part in path.split("/") if part]
        path_class = "/" if not parts else "/:org_slug/" + "/".join(parts[1:])
        return ToolError(
            code=StableErrorCode.NOT_FOUND,
            message="Billy customer was not found for delete.",
            details={"path_class": path_class},
        )
    if not await _confirm_delete_customer(page):
        path = urlsplit(page.url).path or ""
        parts = [part for part in path.split("/") if part]
        path_class = (
            "/"
            if not parts
            else "/:org_slug/"
            + "/".join(
                "id" if i == 1 and part not in {"contacts", "customer", "clients"} else part
                for i, part in enumerate(parts[1:])
            )
        )
        flags = await _delete_chrome_flags(page)
        return ToolError(
            code=StableErrorCode.UI_CHANGED,
            message="Billy delete-customer control is not visible.",
            details={"path_class": path_class, **flags},
        )
    await asyncio.sleep(2)
    return {"ok": True}
