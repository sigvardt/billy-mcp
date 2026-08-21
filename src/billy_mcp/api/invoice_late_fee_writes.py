"""Ticketed FastMCP tools for singular Billy invoice-late-fee writes."""

from __future__ import annotations

from fastmcp import FastMCP
from pydantic import BaseModel, ConfigDict, Field, JsonValue, model_validator

from billy_mcp.api.write_protocol import (
    WriteExecuteInput,
    WriteExecutionResult,
    WriteMethod,
    WriteOperationSpec,
    WritePreviewResult,
    WriteProtocolService,
)
from billy_mcp.client import BillyHttpClient
from billy_mcp.models import ToolError


class _InvoiceLateFeeWritePreviewInput(BaseModel):
    """Forbid undeclared outer fields while preserving opaque late-fee JSON."""

    model_config = ConfigDict(extra="forbid")


class InvoiceLateFeeCreatePreviewInput(_InvoiceLateFeeWritePreviewInput):
    """Input for previewing creation of one Billy invoice late fee."""

    invoiceLateFee: dict[str, JsonValue]


class InvoiceLateFeeUpdatePreviewInput(_InvoiceLateFeeWritePreviewInput):
    """Input for previewing an update to one Billy invoice late fee."""

    id: str = Field(min_length=1)
    invoiceLateFee: dict[str, JsonValue]

    @model_validator(mode="after")
    def invoice_late_fee_id_matches_route_id(self) -> InvoiceLateFeeUpdatePreviewInput:
        """Keep an optional body identifier aligned with the route."""

        if "id" in self.invoiceLateFee and self.invoiceLateFee["id"] != self.id:
            raise ValueError("invoiceLateFee.id must match id")
        return self


def register_invoice_late_fee_write_tools(
    server: FastMCP,
    client: BillyHttpClient,
    write_protocol: WriteProtocolService,
) -> None:
    """Register exactly the four frozen invoice-late-fee create/update tools."""

    del client

    def api_invoice_late_fees_create_preview(
        invoiceLateFee: dict[str, JsonValue],
    ) -> WritePreviewResult:
        """Preview creation of one Billy invoice late fee without a mutation."""

        input = InvoiceLateFeeCreatePreviewInput(invoiceLateFee=invoiceLateFee)
        return write_protocol.preview(
            _invoice_late_fee_specification(
                execute_tool_name="api_invoice_late_fees_create_execute",
                method=WriteMethod.POST,
                payload=input.invoiceLateFee,
                resource_id=None,
            )
        )

    def api_invoice_late_fees_create_execute(
        confirmation_ticket: str = Field(min_length=1),
    ) -> WriteExecutionResult | ToolError:
        """Execute the exact invoice-late-fee creation in a ticket."""

        return write_protocol.execute(
            WriteExecuteInput(confirmation_ticket=confirmation_ticket),
            execute_tool_name="api_invoice_late_fees_create_execute",
        )

    def api_invoice_late_fees_update_preview(
        invoiceLateFee: dict[str, JsonValue],
        id: str = Field(min_length=1),
    ) -> WritePreviewResult:
        """Preview an update to one Billy invoice late fee without a mutation."""

        input = InvoiceLateFeeUpdatePreviewInput(id=id, invoiceLateFee=invoiceLateFee)
        return write_protocol.preview(
            _invoice_late_fee_specification(
                execute_tool_name="api_invoice_late_fees_update_execute",
                method=WriteMethod.PUT,
                payload=input.invoiceLateFee,
                resource_id=input.id,
            )
        )

    def api_invoice_late_fees_update_execute(
        confirmation_ticket: str = Field(min_length=1),
    ) -> WriteExecutionResult | ToolError:
        """Execute the exact invoice-late-fee update in a ticket."""

        return write_protocol.execute(
            WriteExecuteInput(confirmation_ticket=confirmation_ticket),
            execute_tool_name="api_invoice_late_fees_update_execute",
        )

    server.tool(
        name="api_invoice_late_fees_create_preview",
        description="Preview creation of one Billy invoice late fee without a mutation.",
    )(api_invoice_late_fees_create_preview)
    server.tool(
        name="api_invoice_late_fees_create_execute",
        description="Execute a previewed Billy invoice-late-fee creation with its ticket.",
    )(api_invoice_late_fees_create_execute)
    server.tool(
        name="api_invoice_late_fees_update_preview",
        description="Preview an update to one Billy invoice late fee without a mutation.",
    )(api_invoice_late_fees_update_preview)
    server.tool(
        name="api_invoice_late_fees_update_execute",
        description="Execute a previewed Billy invoice-late-fee update with its ticket.",
    )(api_invoice_late_fees_update_execute)


def _invoice_late_fee_specification(
    *,
    execute_tool_name: str,
    method: WriteMethod,
    payload: dict[str, JsonValue],
    resource_id: str | None,
) -> WriteOperationSpec:
    """Build the server-known shape for one singular invoice-late-fee write."""

    action = {WriteMethod.POST: "create", WriteMethod.PUT: "update"}[method]
    expected_effect_state: dict[str, JsonValue] = {
        "action": action,
        "resource": "invoiceLateFee",
    }
    if resource_id is not None:
        expected_effect_state["id"] = resource_id
    return WriteOperationSpec(
        execute_tool_name=execute_tool_name,
        method=method,
        collection_path="/invoiceLateFees",
        singular_root="invoiceLateFee",
        plural_root="invoiceLateFees",
        additional_plural_roots=(),
        payload=payload,
        resource_id=resource_id,
        organization_id=None,
        summary=f"{action.capitalize()} one Billy invoice late fee.",
        expected_effect_state=expected_effect_state,
    )
