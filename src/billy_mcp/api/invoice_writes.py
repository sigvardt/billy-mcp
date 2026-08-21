"""Ticketed FastMCP tools for documented singular Billy invoice writes."""

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


class _InvoiceWritePreviewInput(BaseModel):
    """Base model that forbids undeclared fields around an opaque invoice payload."""

    model_config = ConfigDict(extra="forbid")


class InvoiceCreatePreviewInput(_InvoiceWritePreviewInput):
    """Input for previewing creation of one Billy invoice."""

    invoice: dict[str, JsonValue]


class InvoiceUpdatePreviewInput(_InvoiceWritePreviewInput):
    """Input for previewing an update to one Billy invoice."""

    id: str = Field(min_length=1)
    invoice: dict[str, JsonValue]

    @model_validator(mode="after")
    def invoice_id_matches_route_id(self) -> InvoiceUpdatePreviewInput:
        """Keep an optional invoice-body identifier aligned with the target route."""

        if "id" in self.invoice and self.invoice["id"] != self.id:
            raise ValueError("invoice.id must match id")
        return self


class InvoiceDeletePreviewInput(_InvoiceWritePreviewInput):
    """Input for previewing deletion of one Billy invoice."""

    id: str = Field(min_length=1)


def register_invoice_write_tools(
    server: FastMCP,
    client: BillyHttpClient,
    write_protocol: WriteProtocolService,
) -> None:
    """Register exactly the six frozen ticketed parent-invoice write tools."""

    del client

    def api_invoices_create_preview(invoice: dict[str, JsonValue]) -> WritePreviewResult:
        """Preview creation of one Billy invoice without a mutation."""

        input = InvoiceCreatePreviewInput(invoice=invoice)
        return write_protocol.preview(
            _invoice_spec(
                execute_tool_name="api_invoices_create_execute",
                method=WriteMethod.POST,
                payload=input.invoice,
                resource_id=None,
                summary="Create one Billy invoice.",
                expected_effect_state={"action": "create", "resource": "invoice"},
            )
        )

    def api_invoices_create_execute(
        confirmation_ticket: str = Field(min_length=1),
    ) -> WriteExecutionResult | ToolError:
        """Execute the exact invoice creation in a confirmation ticket."""

        return write_protocol.execute(
            WriteExecuteInput(confirmation_ticket=confirmation_ticket),
            execute_tool_name="api_invoices_create_execute",
        )

    def api_invoices_update_preview(
        invoice: dict[str, JsonValue],
        id: str = Field(min_length=1),
    ) -> WritePreviewResult:
        """Preview an update to one Billy invoice without a mutation."""

        input = InvoiceUpdatePreviewInput(id=id, invoice=invoice)
        return write_protocol.preview(
            _invoice_spec(
                execute_tool_name="api_invoices_update_execute",
                method=WriteMethod.PUT,
                payload=input.invoice,
                resource_id=input.id,
                summary="Update one Billy invoice.",
                expected_effect_state={
                    "action": "update",
                    "resource": "invoice",
                    "id": input.id,
                },
            )
        )

    def api_invoices_update_execute(
        confirmation_ticket: str = Field(min_length=1),
    ) -> WriteExecutionResult | ToolError:
        """Execute the exact invoice update in a confirmation ticket."""

        return write_protocol.execute(
            WriteExecuteInput(confirmation_ticket=confirmation_ticket),
            execute_tool_name="api_invoices_update_execute",
        )

    def api_invoices_delete_preview(id: str = Field(min_length=1)) -> WritePreviewResult:
        """Preview deletion of one Billy invoice without a mutation."""

        input = InvoiceDeletePreviewInput(id=id)
        return write_protocol.preview(
            _invoice_spec(
                execute_tool_name="api_invoices_delete_execute",
                method=WriteMethod.DELETE,
                payload=None,
                resource_id=input.id,
                summary="Delete one Billy invoice.",
                expected_effect_state={
                    "action": "delete",
                    "resource": "invoice",
                    "id": input.id,
                },
            )
        )

    def api_invoices_delete_execute(
        confirmation_ticket: str = Field(min_length=1),
    ) -> WriteExecutionResult | ToolError:
        """Execute the exact invoice deletion in a confirmation ticket."""

        return write_protocol.execute(
            WriteExecuteInput(confirmation_ticket=confirmation_ticket),
            execute_tool_name="api_invoices_delete_execute",
        )

    server.tool(
        name="api_invoices_create_preview",
        description="Preview creation of one Billy invoice without a mutation.",
    )(api_invoices_create_preview)
    server.tool(
        name="api_invoices_create_execute",
        description="Execute a previewed Billy invoice creation with its ticket.",
    )(api_invoices_create_execute)
    server.tool(
        name="api_invoices_update_preview",
        description="Preview an update to one Billy invoice without a mutation.",
    )(api_invoices_update_preview)
    server.tool(
        name="api_invoices_update_execute",
        description="Execute a previewed Billy invoice update with its ticket.",
    )(api_invoices_update_execute)
    server.tool(
        name="api_invoices_delete_preview",
        description="Preview deletion of one Billy invoice without a mutation.",
    )(api_invoices_delete_preview)
    server.tool(
        name="api_invoices_delete_execute",
        description="Execute a previewed Billy invoice deletion with its ticket.",
    )(api_invoices_delete_execute)


def _invoice_spec(
    *,
    execute_tool_name: str,
    method: WriteMethod,
    payload: dict[str, JsonValue] | None,
    resource_id: str | None,
    summary: str,
    expected_effect_state: dict[str, JsonValue],
) -> WriteOperationSpec:
    """Build the server-known operation shape for one parent-invoice CUD preview."""

    return WriteOperationSpec(
        execute_tool_name=execute_tool_name,
        method=method,
        collection_path="/invoices",
        singular_root="invoice",
        plural_root="invoices",
        additional_plural_roots=(),
        payload=payload,
        resource_id=resource_id,
        organization_id=None,
        summary=summary,
        expected_effect_state=expected_effect_state,
    )
