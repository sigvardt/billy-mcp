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

_CLIENTS_CREATE_CTA = "Opret kontakt"
_GEM = re.compile(r"^Gem$")
_RET = re.compile(r"^Ret$")
_MERE = re.compile(r"^Mere$")
_SLET = re.compile(r"Slet kontakt", re.I)
_CONFIRM = re.compile(r"^(Slet|Delete|Bekræft|OK)$", re.I)
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

    def submit_create(self, request: dict[str, JsonValue]) -> Awaitable[object]: ...

    def submit_update(self, request: dict[str, JsonValue]) -> Awaitable[object]: ...

    def submit_delete(self, request: dict[str, JsonValue]) -> Awaitable[object]: ...


class _Locator(Protocol):
    @property
    def first(self) -> _Locator: ...

    async def count(self) -> int: ...

    async def is_visible(self) -> bool: ...

    async def click(self) -> None: ...

    async def fill(self, value: str) -> None: ...


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

    def __init__(self, runtime: BrowserRuntime, *, org_identity_path: Path | None = None) -> None:
        self._runtime = runtime
        self._org_identity_path = org_identity_path or (
            Path.home() / ".local" / "share" / "billy-mcp" / "ui-org-identity.json"
        )

    async def submit_create(self, request: dict[str, JsonValue]) -> object:
        name = _require_name(request, "name")
        return await self._with_page(_create_customer, name, readback_text=name)

    async def submit_update(self, request: dict[str, JsonValue]) -> object:
        new_name = _require_name(request, "new_name")
        return await self._with_page(
            _update_customer,
            _require_name(request, "name"),
            new_name,
            readback_text=new_name,
        )

    async def submit_delete(self, request: dict[str, JsonValue]) -> object:
        name = _require_name(request, "name")
        return await self._with_page(
            _delete_customer,
            name,
            readback_text=name,
            readback_absent=True,
        )

    async def _with_page(
        self,
        work: Callable[..., Awaitable[object]],
        *args: str,
        readback_text: str,
        readback_absent: bool = False,
    ) -> object:
        page: _Page | None = None
        try:
            context = await self._runtime.start()
            page = cast(_Page, await context.new_page())
            await page.goto("https://mit.billy.dk/", wait_until="domcontentloaded")
            await _settle(page)
            slug = _slug_from(page.url, self._org_identity_path)
            if slug is None:
                return ToolError(
                    code=StableErrorCode.ORGANIZATION_REQUIRED,
                    message="Billy organisation slug is not available for the UI write.",
                )
            submitted = await work(page, slug, *args)
            if isinstance(submitted, ToolError):
                return submitted
            proved = await prove_text_on_fresh_page(
                context,
                path="clients",
                text=readback_text,
                absent=readback_absent,
            )
            if proved is not None:
                return proved
            return submitted
        except Exception:
            return ToolError(
                code=StableErrorCode.BILLY_ERROR,
                message="Billy interface contact write could not be completed.",
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
) -> None:
    """Register the six UI contact preview and execute tools."""

    bound: ContactUiActor | None = actor

    def _actor() -> ContactUiActor:
        nonlocal bound
        if bound is None:
            bound = BrowserContactUiActor(runtime or default_browser_runtime())
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
    if method_name == "submit_create":
        submitted = await actor.submit_create(prepared.canonical_request)
    elif method_name == "submit_update":
        submitted = await actor.submit_update(prepared.canonical_request)
    elif method_name == "submit_delete":
        submitted = await actor.submit_delete(prepared.canonical_request)
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


def _slug_from(url: str, identity_path: Path) -> str | None:
    path = urlsplit(url).path or ""
    parts = [part for part in path.split("/") if part]
    if parts and parts[0] not in {"login", ""}:
        return parts[0]
    try:
        payload = json.loads(identity_path.read_text(encoding="utf-8"))
    except Exception:
        return None
    slug = payload.get("org_slug")
    if isinstance(slug, str) and slug and "/" not in slug and slug != "login":
        return slug
    return None


async def _settle(page: _Page) -> None:
    try:
        await page.wait_for_load_state("networkidle", timeout=15000)
    except Exception:
        pass


async def _goto_clients(page: _Page, slug: str) -> None:
    await page.goto(f"https://mit.billy.dk/{slug}/clients", wait_until="domcontentloaded")
    await _settle(page)


async def _click_named(page: _Page, pattern: re.Pattern[str]) -> bool:
    button = page.get_by_role("button", name=pattern)
    if await button.count() >= 1 and await button.first.is_visible():
        await button.first.click()
        await _settle(page)
        return True
    text = page.locator(f"text={pattern.pattern.strip('^$')}")
    try:
        if await text.count() >= 1 and await text.first.is_visible():
            await text.first.click()
            await _settle(page)
            return True
    except Exception:
        return False
    return False


async def _fill_name(page: _Page, value: str) -> bool:
    field = page.locator(_NAME)
    if await field.count() < 1:
        return False
    await field.first.fill(value)
    return True


async def _search_name(page: _Page, name: str) -> None:
    search = page.locator(_SEARCH)
    if await search.count() >= 1:
        await search.first.fill(name)
        await asyncio.sleep(1)


async def _open_named_customer(page: _Page, name: str) -> bool:
    await _search_name(page, name)
    match = page.get_by_text(name, exact=False)
    if await match.count() < 1:
        return False
    await match.first.click()
    await _settle(page)
    return True


async def _create_customer(page: _Page, slug: str, name: str) -> object:
    await _goto_clients(page, slug)
    cta = page.locator(f"text={_CLIENTS_CREATE_CTA}")
    if await cta.count() < 1:
        return ToolError(
            code=StableErrorCode.UI_CHANGED,
            message="Billy create-customer control is not visible.",
        )
    await cta.first.click()
    await _settle(page)
    if not await _fill_name(page, name):
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
    if not await _click_named(page, _GEM):
        return ToolError(
            code=StableErrorCode.UI_CHANGED,
            message="Billy save control is not visible.",
        )
    await asyncio.sleep(2)
    return {"ok": True}


async def _update_customer(page: _Page, slug: str, name: str, new_name: str) -> object:
    await _goto_clients(page, slug)
    if not await _open_named_customer(page, name):
        return ToolError(
            code=StableErrorCode.NOT_FOUND,
            message="Billy customer was not found for update.",
        )
    if not await _click_named(page, _RET):
        return ToolError(
            code=StableErrorCode.UI_CHANGED,
            message="Billy edit control is not visible.",
        )
    if not await _fill_name(page, new_name):
        return ToolError(
            code=StableErrorCode.UI_CHANGED,
            message="Billy customer name field is not visible.",
        )
    if not await _click_named(page, _GEM):
        return ToolError(
            code=StableErrorCode.UI_CHANGED,
            message="Billy save control is not visible.",
        )
    await asyncio.sleep(2)
    return {"ok": True}


async def _delete_customer(page: _Page, slug: str, name: str) -> object:
    await _goto_clients(page, slug)
    if not await _open_named_customer(page, name):
        return ToolError(
            code=StableErrorCode.NOT_FOUND,
            message="Billy customer was not found for delete.",
        )
    await _click_named(page, _MERE)
    if not await _click_named(page, _SLET):
        return ToolError(
            code=StableErrorCode.UI_CHANGED,
            message="Billy delete-customer control is not visible.",
        )
    await _click_named(page, _CONFIRM)
    await asyncio.sleep(2)
    return {"ok": True}
