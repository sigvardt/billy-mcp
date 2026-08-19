"""Ticketed UI invoice write tools. Draft save only; never send, email, or approve."""

from __future__ import annotations

import inspect
from collections.abc import Awaitable
from typing import Literal, Protocol

from fastmcp import FastMCP
from pydantic import BaseModel, ConfigDict, Field, JsonValue

from billy_mcp.browser import BrowserRuntime
from billy_mcp.models import StableErrorCode, ToolError
from billy_mcp.ui_writes.invoices_form import submit_draft_invoice
from billy_mcp.ui_writes.page_flow import FamilyWrite
from billy_mcp.ui_writes.protocol import (
    UiWriteExecuteInput,
    UiWritePrepared,
    UiWritePreviewResult,
    UiWriteProtocol,
)

CREATE_EXECUTE = "ui_invoices_create_execute"
UPDATE_EXECUTE = "ui_invoices_update_execute"
DELETE_EXECUTE = "ui_invoices_delete_execute"
DRAFT_SAVE_CTA = "Gem som kladde"
DRAFT_DELETE_CTA = "Slet"
_FORBIDDEN_TOKENS = ("godkend", "send", "email", "e-mail")
_ALLOWED: frozenset[tuple[str, str]] = frozenset(
    {
        ("draft_create", DRAFT_SAVE_CTA),
        ("draft_update", DRAFT_SAVE_CTA),
        ("draft_delete", DRAFT_DELETE_CTA),
    }
)


class InvoiceCreatePreviewInput(BaseModel):
    """Preview input for one draft invoice create (Gem som kladde)."""

    model_config = ConfigDict(extra="forbid")

    contact_name: str = Field(min_length=1)
    line_description: str = Field(min_length=1)
    product_name: str = Field(min_length=1)
    unit_price: float = Field(gt=0)
    action: str = Field(min_length=1)
    save_cta: str = Field(min_length=1)
    organization_id: str = Field(min_length=1)


class InvoiceUpdatePreviewInput(BaseModel):
    """Preview input for one draft invoice update (Gem som kladde)."""

    model_config = ConfigDict(extra="forbid")

    contact_name: str = Field(min_length=1)
    id: str = ""
    line_description: str = Field(min_length=1)
    unit_price: float = Field(gt=0)
    action: str = Field(min_length=1)
    save_cta: str = Field(min_length=1)
    organization_id: str = Field(min_length=1)


class InvoiceDeletePreviewInput(BaseModel):
    """Preview input for one draft invoice delete (Mere then Slet)."""

    model_config = ConfigDict(extra="forbid")

    contact_name: str = Field(min_length=1)
    id: str = ""
    action: str = Field(min_length=1)
    save_cta: str = Field(min_length=1)
    organization_id: str = Field(min_length=1)


class UiInvoiceExecuteResult(BaseModel):
    """Result of consuming a ticket and invoking the family submitter."""

    model_config = ConfigDict(extra="forbid")

    action: Literal["create", "update", "delete"]
    save_cta: str = Field(min_length=1)
    submitted: bool
    canonical_request: dict[str, JsonValue]
    expected_effect_state: dict[str, JsonValue]


class InvoiceUiSubmitter(Protocol):
    """Performs the bound interface action after the ticket is consumed."""

    def submit(
        self, prepared: UiWritePrepared
    ) -> UiInvoiceExecuteResult | ToolError | Awaitable[UiInvoiceExecuteResult | ToolError]: ...


class UnarmedInvoiceSubmitter:
    """Consumes the ticket contract without clicking Billy chrome."""

    def submit(self, prepared: UiWritePrepared) -> UiInvoiceExecuteResult | ToolError:
        rejected = fail_closed_request(prepared.canonical_request)
        if rejected is not None:
            return rejected
        action = _effect_action(prepared.expected_effect_state)
        save_cta = str(prepared.canonical_request.get("save_cta", ""))
        return UiInvoiceExecuteResult(
            action=action,
            save_cta=save_cta,
            submitted=False,
            canonical_request=prepared.canonical_request,
            expected_effect_state=prepared.expected_effect_state,
        )


class BrowserInvoiceSubmitter:
    """Default production submitter. Draft save only. Enters BrowserRuntime first."""

    def __init__(
        self,
        runtime: BrowserRuntime,
        readback_runtime: BrowserRuntime | None = None,
    ) -> None:
        self._runtime = runtime
        self._readback_runtime = readback_runtime or runtime.independent_readback_runtime()

    async def submit(self, prepared: UiWritePrepared) -> UiInvoiceExecuteResult | ToolError:
        rejected = fail_closed_request(prepared.canonical_request)
        if rejected is not None:
            return rejected
        action = _effect_action(prepared.expected_effect_state)
        save_cta = str(prepared.canonical_request.get("save_cta", ""))
        request = prepared.canonical_request
        failed = await submit_draft_invoice(
            self._runtime,
            action=action,
            unique_tag=str(request.get("contact_name") or request.get("line_description") or ""),
            contact_name=str(request.get("contact_name") or ""),
            line_description=str(request.get("line_description") or ""),
            product_name=str(request.get("product_name") or ""),
            unit_price=_request_unit_price(request),
            organization_id=str(prepared.binding.organization_id or ""),
            invoice_id=str(request.get("id") or ""),
            readback_runtime=self._readback_runtime,
        )
        if failed is not None:
            return failed
        return UiInvoiceExecuteResult(
            action=action,
            save_cta=save_cta,
            submitted=True,
            canonical_request=prepared.canonical_request,
            expected_effect_state=prepared.expected_effect_state,
        )


def fail_closed_request(request: dict[str, JsonValue]) -> ToolError | None:
    """Reject send, email, approve, or any non-draft CTA."""

    action = str(request.get("action", ""))
    save_cta = str(request.get("save_cta", ""))
    return fail_closed(action, save_cta)


def fail_closed(action: str, save_cta: str) -> ToolError | None:
    """Reject anything that is not draft create/update or draft delete."""

    if (action, save_cta) not in _ALLOWED:
        return ToolError(
            code=StableErrorCode.VALIDATION_ERROR,
            message="Invoice UI writes accept draft save or draft delete only.",
            details={"action": action, "save_cta": save_cta},
        )
    blob = f"{action} {save_cta}".casefold()
    if any(token in blob for token in _FORBIDDEN_TOKENS):
        return ToolError(
            code=StableErrorCode.VALIDATION_ERROR,
            message="Invoice UI writes refuse send, email, and Godkend.",
            details={"action": action, "save_cta": save_cta},
        )
    return None


def invoice_family_write(
    prepared: UiWritePrepared, action: Literal["create", "update", "delete"]
) -> FamilyWrite:
    request = prepared.canonical_request
    invoice_id = str(request.get("id") or "")
    line_description = str(request.get("line_description") or invoice_id)
    match action:
        case "create":
            return FamilyWrite(
                write_path="invoices/new",
                fills=(("description", line_description),),
                clicks=(DRAFT_SAVE_CTA,),
                readback_path="invoices",
                readback_text=line_description,
            )
        case "update":
            return FamilyWrite(
                write_path=f"invoices/{invoice_id}/edit",
                fills=(("description", line_description),),
                clicks=(DRAFT_SAVE_CTA,),
                readback_path="invoices",
                readback_text=line_description,
            )
        case "delete":
            return FamilyWrite(
                write_path=f"invoices/{invoice_id}/edit",
                fills=(),
                clicks=("Mere", DRAFT_DELETE_CTA),
                readback_path="invoices",
                readback_text=invoice_id,
                readback_absent=True,
            )


def register_ui_invoice_write_tools(
    server: FastMCP,
    protocol: UiWriteProtocol,
    submitter: InvoiceUiSubmitter | None = None,
    runtime: BrowserRuntime | None = None,
    readback_runtime: BrowserRuntime | None = None,
) -> None:
    """Register UI invoice preview and execute tools. Preview writes nothing."""

    if submitter is not None:
        active: InvoiceUiSubmitter = submitter
    elif runtime is not None:
        active = BrowserInvoiceSubmitter(runtime, readback_runtime)
    else:
        active = UnarmedInvoiceSubmitter()

    def ui_invoices_create_preview(
        contact_name: str = Field(min_length=1),
        line_description: str = Field(min_length=1),
        product_name: str = Field(min_length=1),
        unit_price: float = Field(gt=0),
        action: str = Field(min_length=1),
        save_cta: str = Field(min_length=1),
        organization_id: str = Field(min_length=1),
    ) -> UiWritePreviewResult | ToolError:
        """Preview one draft invoice create. Does not click Gem som kladde."""

        payload = InvoiceCreatePreviewInput(
            contact_name=contact_name,
            line_description=line_description,
            product_name=product_name,
            unit_price=unit_price,
            action=action,
            save_cta=save_cta,
            organization_id=organization_id,
        )
        rejected = fail_closed(payload.action, payload.save_cta)
        if rejected is not None:
            return rejected
        request = _create_request(payload)
        return protocol.preview(
            execute_tool_name=CREATE_EXECUTE,
            organization_id=payload.organization_id,
            target="invoices",
            canonical_request=request,
            expected_effect_state=_effect("create", payload.save_cta),
            summary="Create one Billy invoice draft in the interface.",
        )

    async def ui_invoices_create_execute(
        confirmation_ticket: str = Field(min_length=1),
    ) -> UiInvoiceExecuteResult | ToolError:
        """Execute the exact previewed draft invoice create."""

        return await _execute(protocol, active, confirmation_ticket, CREATE_EXECUTE)

    def ui_invoices_update_preview(
        contact_name: str = Field(min_length=1),
        line_description: str = Field(min_length=1),
        unit_price: float = Field(gt=0),
        action: str = Field(min_length=1),
        save_cta: str = Field(min_length=1),
        organization_id: str = Field(min_length=1),
        id: str = "",
    ) -> UiWritePreviewResult | ToolError:
        """Preview one draft invoice update. Does not click Gem som kladde."""

        payload = InvoiceUpdatePreviewInput(
            contact_name=contact_name,
            id=id,
            line_description=line_description,
            unit_price=unit_price,
            action=action,
            save_cta=save_cta,
            organization_id=organization_id,
        )
        rejected = fail_closed(payload.action, payload.save_cta)
        if rejected is not None:
            return rejected
        request = _update_request(payload)
        return protocol.preview(
            execute_tool_name=UPDATE_EXECUTE,
            organization_id=payload.organization_id,
            target=payload.contact_name,
            canonical_request=request,
            expected_effect_state=_effect("update", payload.save_cta, payload.contact_name),
            summary="Update one Billy invoice draft in the interface.",
        )

    async def ui_invoices_update_execute(
        confirmation_ticket: str = Field(min_length=1),
    ) -> UiInvoiceExecuteResult | ToolError:
        """Execute the exact previewed draft invoice update."""

        return await _execute(protocol, active, confirmation_ticket, UPDATE_EXECUTE)

    def ui_invoices_delete_preview(
        contact_name: str = Field(min_length=1),
        action: str = Field(min_length=1),
        save_cta: str = Field(min_length=1),
        organization_id: str = Field(min_length=1),
        id: str = "",
    ) -> UiWritePreviewResult | ToolError:
        """Preview one draft invoice delete. Does not confirm Slet."""

        payload = InvoiceDeletePreviewInput(
            contact_name=contact_name,
            id=id,
            action=action,
            save_cta=save_cta,
            organization_id=organization_id,
        )
        rejected = fail_closed(payload.action, payload.save_cta)
        if rejected is not None:
            return rejected
        request = _delete_request(payload)
        return protocol.preview(
            execute_tool_name=DELETE_EXECUTE,
            organization_id=payload.organization_id,
            target=payload.contact_name,
            canonical_request=request,
            expected_effect_state=_effect("delete", payload.save_cta, payload.contact_name),
            summary="Delete one Billy invoice draft in the interface.",
        )

    async def ui_invoices_delete_execute(
        confirmation_ticket: str = Field(min_length=1),
    ) -> UiInvoiceExecuteResult | ToolError:
        """Execute the exact previewed draft invoice delete."""

        return await _execute(protocol, active, confirmation_ticket, DELETE_EXECUTE)

    server.tool(
        name="ui_invoices_create_preview",
        description="Preview one Billy invoice draft create without submitting.",
    )(ui_invoices_create_preview)
    server.tool(
        name="ui_invoices_create_execute",
        description="Execute a previewed Billy invoice draft create with its ticket.",
    )(ui_invoices_create_execute)
    server.tool(
        name="ui_invoices_update_preview",
        description="Preview one Billy invoice draft update without submitting.",
    )(ui_invoices_update_preview)
    server.tool(
        name="ui_invoices_update_execute",
        description="Execute a previewed Billy invoice draft update with its ticket.",
    )(ui_invoices_update_execute)
    server.tool(
        name="ui_invoices_delete_preview",
        description="Preview one Billy invoice draft delete without confirming Slet.",
    )(ui_invoices_delete_preview)
    server.tool(
        name="ui_invoices_delete_execute",
        description="Execute a previewed Billy invoice draft delete with its ticket.",
    )(ui_invoices_delete_execute)


async def _execute(
    protocol: UiWriteProtocol,
    submitter: InvoiceUiSubmitter,
    confirmation_ticket: str,
    execute_tool_name: str,
) -> UiInvoiceExecuteResult | ToolError:
    prepared = protocol.consume(
        UiWriteExecuteInput(confirmation_ticket=confirmation_ticket),
        execute_tool_name=execute_tool_name,
    )
    if isinstance(prepared, ToolError):
        return prepared
    rejected = fail_closed_request(prepared.canonical_request)
    if rejected is not None:
        return rejected
    submitted = submitter.submit(prepared)
    if inspect.isawaitable(submitted):
        return await submitted
    return submitted


def _request_unit_price(request: dict[str, JsonValue]) -> float:
    """Read a ticket-bound unit price. Non-numeric values are zero (rejected later)."""

    raw = request.get("unit_price")
    if isinstance(raw, bool):
        return 0.0
    if isinstance(raw, int):
        return float(raw)
    if isinstance(raw, float):
        return raw
    return 0.0


def _create_request(payload: InvoiceCreatePreviewInput) -> dict[str, JsonValue]:
    request: dict[str, JsonValue] = {
        "action": payload.action,
        "save_cta": payload.save_cta,
        "contact_name": payload.contact_name,
        "line_description": payload.line_description,
        "product_name": payload.product_name,
        "unit_price": payload.unit_price,
    }
    request["organization_id"] = payload.organization_id
    return request


def _update_request(payload: InvoiceUpdatePreviewInput) -> dict[str, JsonValue]:
    request: dict[str, JsonValue] = {
        "action": payload.action,
        "save_cta": payload.save_cta,
        "contact_name": payload.contact_name,
        "id": payload.id,
        "line_description": payload.line_description,
        "unit_price": payload.unit_price,
    }
    request["organization_id"] = payload.organization_id
    return request


def _delete_request(payload: InvoiceDeletePreviewInput) -> dict[str, JsonValue]:
    request: dict[str, JsonValue] = {
        "action": payload.action,
        "save_cta": payload.save_cta,
        "contact_name": payload.contact_name,
        "id": payload.id,
    }
    request["organization_id"] = payload.organization_id
    return request


def _effect(action: str, save_cta: str, invoice_id: str | None = None) -> dict[str, JsonValue]:
    state: dict[str, JsonValue] = {
        "action": action,
        "resource": "invoice",
        "save_cta": save_cta,
    }
    if invoice_id is not None:
        state["id"] = invoice_id
    return state


def _effect_action(
    expected_effect_state: dict[str, JsonValue],
) -> Literal["create", "update", "delete"]:
    action = expected_effect_state.get("action")
    if action == "create":
        return "create"
    if action == "update":
        return "update"
    if action == "delete":
        return "delete"
    raise ValueError(f"unsupported invoice UI effect action: {action!r}")
