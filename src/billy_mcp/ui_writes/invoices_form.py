"""Bounded Billy draft-invoice form actions. Never sends, emails, or Godkend."""

from __future__ import annotations

from pathlib import Path
from typing import cast
from urllib.parse import urlsplit

from billy_mcp.browser import BrowserRuntime
from billy_mcp.models import StableErrorCode, ToolError
from billy_mcp.ui_writes.invoices_form_bind import bind_kunde, fill_line
from billy_mcp.ui_writes.invoices_form_page import (
    CONFIRM_DELETE,
    DELETE,
    DRAFT_SAVE,
    MORE,
    UPDATE_SAVE,
    Page,
    click_exact,
    slug_from,
    visible_button,
    wait_persist,
    watch_invoice_response,
    write_json,
)
from billy_mcp.ui_writes.page_flow import BILLY_ORIGIN, prove_text_on_fresh_page

CREATE_PRE_SUBMIT_DUMP = (
    Path.home() / ".local" / "share" / "billy-mcp" / "inspect-live-invoices-create-presubmit.json"
)


async def submit_draft_invoice(
    runtime: BrowserRuntime,
    *,
    action: str,
    unique_tag: str,
    contact_name: str,
    line_description: str,
    organization_id: str,
    invoice_id: str,
    readback_runtime: BrowserRuntime,
) -> ToolError | None:
    """Create, update, or delete one tagged draft invoice, then prove it independently."""

    page: Page | None = None
    try:
        bound = organization_id.strip()
        if not bound:
            return ToolError(
                code=StableErrorCode.ORGANIZATION_REQUIRED,
                message="A proven Billy organisation id is required.",
            )
        context = await runtime.start()
        page = cast(Page, await context.new_page())
        await page.goto(f"{BILLY_ORIGIN}/", wait_until="domcontentloaded")
        slug = slug_from(page.url)
        if slug is None:
            await page.goto(f"{BILLY_ORIGIN}/{bound}/invoices", wait_until="domcontentloaded")
            slug = slug_from(page.url)
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
        assert page is not None
        failed = await _run_action(
            page,
            slug=slug,
            action=action,
            contact_name=contact_name,
            line_description=line_description,
            invoice_id=invoice_id,
        )
        if failed is not None:
            return failed
        marker = line_description if action != "delete" else unique_tag
        return await prove_text_on_fresh_page(
            readback_runtime,
            organization_id=bound,
            path="invoices",
            text=marker,
            absent=action == "delete",
        )
    except (OSError, RuntimeError, AssertionError, TimeoutError) as exc:
        return ToolError(
            code=StableErrorCode.BILLY_ERROR,
            message="Billy interface invoice write could not be completed.",
            details={"error": type(exc).__name__},
        )
    finally:
        if page is not None:
            await page.close()


async def _run_action(
    page: Page,
    *,
    slug: str,
    action: str,
    contact_name: str,
    line_description: str,
    invoice_id: str,
) -> ToolError | None:
    match action:
        case "create":
            return await _create_draft(page, slug, contact_name, line_description)
        case "update":
            return await _update_draft(page, slug, invoice_id, line_description)
        case "delete":
            return await _delete_draft(page, slug, invoice_id)
        case unreachable:
            return ToolError(
                code=StableErrorCode.VALIDATION_ERROR,
                message="Invoice UI writes accept draft create, update, or delete only.",
                details={"action": unreachable},
            )


async def _create_draft(
    page: Page, slug: str, contact_name: str, line_description: str
) -> ToolError | None:
    await page.goto(f"{BILLY_ORIGIN}/{slug}/invoices/new", wait_until="domcontentloaded")
    try:
        await page.wait_for_load_state("networkidle")
    except (TimeoutError, RuntimeError):
        pass
    bind = await bind_kunde(page, contact_name)
    if isinstance(bind, ToolError):
        return bind
    if await fill_line(page, line_description) is None:
        return ToolError(
            code=StableErrorCode.UI_CHANGED,
            message="Billy invoice line description field is not visible.",
        )
    write_json(
        CREATE_PRE_SUBMIT_DUMP,
        {
            "path": urlsplit(page.url).path,
            "unique_tag": contact_name,
            "customer": contact_name,
            "line_description": line_description,
            "draft_cta": DRAFT_SAVE,
            "vendor_bind": bind,
        },
    )
    seen: list[str] = []

    def _watch_create(event: object) -> None:
        watch_invoice_response(event, seen)

    page.on("response", _watch_create)
    clicked = await click_exact(page, DRAFT_SAVE)
    if clicked is not None:
        return clicked
    return await wait_persist(seen, method="POST")


async def _update_draft(
    page: Page, slug: str, invoice_id: str, line_description: str
) -> ToolError | None:
    await page.goto(
        f"{BILLY_ORIGIN}/{slug}/invoices/{invoice_id}/edit",
        wait_until="domcontentloaded",
    )
    if await fill_line(page, line_description) is None:
        return ToolError(
            code=StableErrorCode.UI_CHANGED,
            message="Billy invoice line description field is not visible.",
        )
    cta = UPDATE_SAVE if await visible_button(page, UPDATE_SAVE) else DRAFT_SAVE
    seen: list[str] = []

    def _watch_update(event: object) -> None:
        watch_invoice_response(event, seen)

    page.on("response", _watch_update)
    clicked = await click_exact(page, cta)
    if clicked is not None:
        return clicked
    put = await wait_persist(seen, method="PUT")
    if put is None:
        return None
    return await wait_persist(seen, method="POST")


async def _delete_draft(page: Page, slug: str, invoice_id: str) -> ToolError | None:
    await page.goto(
        f"{BILLY_ORIGIN}/{slug}/invoices/{invoice_id}/edit",
        wait_until="domcontentloaded",
    )
    more = await click_exact(page, MORE)
    if more is not None:
        return more
    slet = await click_exact(page, DELETE)
    if slet is not None:
        return slet
    if await visible_button(page, CONFIRM_DELETE):
        return await click_exact(page, CONFIRM_DELETE)
    return None
