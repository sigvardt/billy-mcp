"""Bounded Billy draft-invoice form actions. Never sends, emails, or Godkend."""

from __future__ import annotations

import asyncio
import os
from pathlib import Path
from typing import cast
from urllib.parse import urlsplit

from billy_mcp.browser import BrowserRuntime
from billy_mcp.models import StableErrorCode, ToolError
from billy_mcp.ui_writes.invoices_form_bind import (
    bind_kunde,
    fill_priced_line,
    kunde_field,
    price_is,
    read_unit_price,
)
from billy_mcp.ui_writes.invoices_form_delete import delete_draft_invoice
from billy_mcp.ui_writes.invoices_form_page import (
    CREATE_PERSIST_DUMP,
    DRAFT_SAVE,
    UPDATE_SAVE,
    Page,
    click_exact,
    persist_created_invoice_id,
    slug_from,
    visible_button,
    wait_persist,
    watch_invoice_response,
    write_json,
)
from billy_mcp.ui_writes.invoices_form_price import prove_fresh_unit_price
from billy_mcp.ui_writes.invoices_form_row import open_invoice_row
from billy_mcp.ui_writes.page_flow import BILLY_ORIGIN, prove_text_on_fresh_page
from billy_mcp.vision_evidence import allowed_vision_frame_dir

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
    product_name: str,
    unit_price: float,
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
        await page.close()
        page = cast(Page, await context.new_page())
        failed = await _run_action(
            page,
            slug=slug,
            action=action,
            contact_name=contact_name,
            line_description=line_description,
            product_name=product_name,
            unit_price=unit_price,
            invoice_id=invoice_id,
        )
        if failed is not None:
            return failed
        if action == "update":
            return await prove_fresh_unit_price(readback_runtime, bound, contact_name, unit_price)
        marker = unique_tag
        return await prove_text_on_fresh_page(
            readback_runtime,
            organization_id=bound,
            path="invoices",
            text=marker,
            absent=action == "delete",
            allow_search=False,
            visible_body=True,
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
    product_name: str,
    unit_price: float,
    invoice_id: str,
) -> ToolError | None:
    match action:
        case "create":
            return await _create_draft(
                page, slug, contact_name, line_description, product_name, unit_price
            )
        case "update":
            return await _update_draft(page, slug, contact_name, line_description, unit_price)
        case "delete":
            return await delete_draft_invoice(page, slug, contact_name)
        case unreachable:
            return ToolError(
                code=StableErrorCode.VALIDATION_ERROR,
                message="Invoice UI writes accept draft create, update, or delete only.",
                details={"action": unreachable},
            )


async def _create_draft(
    page: Page,
    slug: str,
    contact_name: str,
    line_description: str,
    product_name: str,
    unit_price: float,
) -> ToolError | None:
    await page.goto(f"{BILLY_ORIGIN}/{slug}/invoices/new", wait_until="domcontentloaded")
    try:
        await page.wait_for_load_state("networkidle")
    except (TimeoutError, RuntimeError):
        pass
    bind = await bind_kunde(page, contact_name)
    if isinstance(bind, ToolError):
        return bind
    priced = await fill_priced_line(page, line_description, unit_price, product_name)
    if isinstance(priced, ToolError):
        return priced
    dest = allowed_vision_frame_dir(os.environ.get("BILLY_VISION_FRAME_DIR", ""))
    if dest:
        contact_input = await kunde_field(page)
        contact_value = ""
        if contact_input is not None:
            contact_value = (await contact_input.input_value()).strip()
        if contact_value != contact_name:
            return ToolError(
                code=StableErrorCode.UI_CHANGED,
                message="Filled invoice customer is not visible before submit.",
            )
        product_visible = await page.get_by_text(product_name, exact=True).count() >= 1
        if not product_visible:
            product_input = page.locator("input[name='product'], input[placeholder='Vælg produkt']")
            if await product_input.count() >= 1:
                product_visible = (await product_input.first.input_value()).strip() == product_name
        if not product_visible:
            return ToolError(
                code=StableErrorCode.UI_CHANGED,
                message="Filled invoice product is not visible before submit.",
            )
        shot = Path(dest) / "02_before_submit.png"
        capture = getattr(page, "screenshot", None)
        if capture is None:
            return ToolError(
                code=StableErrorCode.UI_CHANGED,
                message="Filled invoice form frame was not captured before submit.",
            )
        await capture(path=str(shot), full_page=False)
        if not shot.is_file() or shot.stat().st_size <= 0:
            return ToolError(
                code=StableErrorCode.UI_CHANGED,
                message="Filled invoice form frame was not captured before submit.",
            )
        description_ok = False
        fields = page.locator("input:not([type='hidden']), textarea")
        for index in range(min(await fields.count(), 24)):
            node = fields.nth(index)
            try:
                if not await node.is_visible():
                    continue
                if (await node.input_value()).strip() == line_description:
                    description_ok = True
                    break
            except (TimeoutError, RuntimeError):
                continue
        if not description_ok:
            for label in ("Evt. beskrivelse", "Beskrivelse"):
                field = page.get_by_label(label, exact=True)
                if await field.count() < 1:
                    field = page.get_by_label(label)
                if await field.count() < 1:
                    continue
                try:
                    if (await field.first.input_value()).strip() == line_description:
                        description_ok = True
                        break
                except (TimeoutError, RuntimeError):
                    continue
        if not description_ok:
            editables = page.locator("[contenteditable='true']")
            for index in range(min(await editables.count(), 12)):
                node = editables.nth(index)
                try:
                    if not await node.is_visible():
                        continue
                    if (await node.inner_text()).strip() == line_description:
                        description_ok = True
                        break
                except (TimeoutError, RuntimeError):
                    continue
        if not description_ok and await page.get_by_text(line_description, exact=True).count() >= 1:
            description_ok = True
        if line_description.strip() and not description_ok:
            return ToolError(
                code=StableErrorCode.UI_CHANGED,
                message="Filled invoice description is not visible before submit.",
            )
        shown_price = await read_unit_price(page)
        if not price_is(shown_price, unit_price):
            return ToolError(
                code=StableErrorCode.UI_CHANGED,
                message="Filled invoice unit price is not visible before submit.",
            )
    write_json(
        CREATE_PRE_SUBMIT_DUMP,
        {
            "path": urlsplit(page.url).path,
            "unique_tag": contact_name,
            "customer": contact_name,
            "product_name": product_name,
            "line_description": line_description,
            "unit_price": unit_price,
            "draft_cta": DRAFT_SAVE,
            "vendor_bind": bind,
            "product_bind": "scoped:existing_option",
        },
    )
    seen: list[str] = []
    events: list[object] = []

    def _watch_create(event: object) -> None:
        events.append(event)
        watch_invoice_response(event, seen)

    page.on("response", _watch_create)
    clicked = await click_exact(page, DRAFT_SAVE)
    if clicked is not None:
        return clicked
    persisted = await wait_persist(seen, method="POST")
    if persisted is not None:
        return persisted
    invoice_id = await persist_created_invoice_id(events)
    if invoice_id:
        write_json(
            CREATE_PERSIST_DUMP,
            {"watched": list(seen), "method": "POST", "invoice_id": invoice_id},
        )
    return None


async def _update_draft(
    page: Page, slug: str, contact_name: str, line_description: str, unit_price: float
) -> ToolError | None:
    opened = await open_invoice_row(page, slug, contact_name)
    if opened is not None:
        return opened
    seen: list[str] = []

    def _watch_update(event: object) -> None:
        watch_invoice_response(event, seen)

    page.on("response", _watch_update)
    for _ in range(40):
        if await visible_button(page, DRAFT_SAVE) or await visible_button(page, UPDATE_SAVE):
            break
        await asyncio.sleep(0.25)
    priced = await fill_priced_line(page, line_description, unit_price)
    if isinstance(priced, ToolError):
        return priced
    last_error: ToolError | None = None
    for cta in (UPDATE_SAVE, "Gem ændringer", DRAFT_SAVE):
        if not await visible_button(page, cta):
            continue
        clicked = await click_exact(page, cta)
        if clicked is not None:
            return clicked
        put = await wait_persist(seen, method="PUT")
        if put is None:
            return None
        last_error = put
    return last_error or ToolError(
        code=StableErrorCode.UI_CHANGED,
        message="Billy draft invoice save control is not visible.",
    )
