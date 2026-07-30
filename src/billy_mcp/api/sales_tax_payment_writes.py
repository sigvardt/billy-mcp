"""Ticketed FastMCP tools for singular Billy sales-tax-payment writes."""

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


class _SalesTaxPaymentWritePreviewInput(BaseModel):
    """Forbid undeclared outer fields while preserving opaque payment JSON."""

    model_config = ConfigDict(extra="forbid")


class SalesTaxPaymentCreatePreviewInput(_SalesTaxPaymentWritePreviewInput):
    """Input for previewing creation of one Billy sales-tax payment."""

    salesTaxPayment: dict[str, JsonValue]


class SalesTaxPaymentUpdatePreviewInput(_SalesTaxPaymentWritePreviewInput):
    """Input for previewing a partial update to one Billy sales-tax payment."""

    id: str = Field(min_length=1)
    salesTaxPayment: dict[str, JsonValue]

    @model_validator(mode="after")
    def sales_tax_payment_id_matches_route_id(self) -> SalesTaxPaymentUpdatePreviewInput:
        """Keep an optional body identifier aligned with the route."""

        if "id" in self.salesTaxPayment and self.salesTaxPayment["id"] != self.id:
            raise ValueError("salesTaxPayment.id must match id")
        return self


def register_sales_tax_payment_write_tools(
    server: FastMCP,
    client: BillyHttpClient,
    write_protocol: WriteProtocolService,
) -> None:
    """Register exactly the four frozen sales-tax-payment create/update tools."""

    del client

    def api_sales_tax_payments_create_preview(
        salesTaxPayment: dict[str, JsonValue],
    ) -> WritePreviewResult:
        """Preview creation of one Billy sales-tax payment without a mutation."""

        input = SalesTaxPaymentCreatePreviewInput(salesTaxPayment=salesTaxPayment)
        return write_protocol.preview(
            _sales_tax_payment_specification(
                execute_tool_name="api_sales_tax_payments_create_execute",
                method=WriteMethod.POST,
                payload=input.salesTaxPayment,
                resource_id=None,
            )
        )

    def api_sales_tax_payments_create_execute(
        confirmation_ticket: str = Field(min_length=1),
    ) -> WriteExecutionResult | ToolError:
        """Execute the exact sales-tax-payment creation in a ticket."""

        return write_protocol.execute(
            WriteExecuteInput(confirmation_ticket=confirmation_ticket),
            execute_tool_name="api_sales_tax_payments_create_execute",
        )

    def api_sales_tax_payments_update_preview(
        salesTaxPayment: dict[str, JsonValue],
        id: str = Field(min_length=1),
    ) -> WritePreviewResult:
        """Preview a partial update to one Billy sales-tax payment without a mutation."""

        input = SalesTaxPaymentUpdatePreviewInput(id=id, salesTaxPayment=salesTaxPayment)
        return write_protocol.preview(
            _sales_tax_payment_specification(
                execute_tool_name="api_sales_tax_payments_update_execute",
                method=WriteMethod.PUT,
                payload=input.salesTaxPayment,
                resource_id=input.id,
            )
        )

    def api_sales_tax_payments_update_execute(
        confirmation_ticket: str = Field(min_length=1),
    ) -> WriteExecutionResult | ToolError:
        """Execute the exact sales-tax-payment update in a ticket."""

        return write_protocol.execute(
            WriteExecuteInput(confirmation_ticket=confirmation_ticket),
            execute_tool_name="api_sales_tax_payments_update_execute",
        )

    server.tool(
        name="api_sales_tax_payments_create_preview",
        description="Preview creation of one Billy sales-tax payment without a mutation.",
    )(api_sales_tax_payments_create_preview)
    server.tool(
        name="api_sales_tax_payments_create_execute",
        description="Execute a previewed Billy sales-tax-payment creation with its ticket.",
    )(api_sales_tax_payments_create_execute)
    server.tool(
        name="api_sales_tax_payments_update_preview",
        description="Preview a partial update to one Billy sales-tax payment without a mutation.",
    )(api_sales_tax_payments_update_preview)
    server.tool(
        name="api_sales_tax_payments_update_execute",
        description="Execute a previewed Billy sales-tax-payment update with its ticket.",
    )(api_sales_tax_payments_update_execute)


def _sales_tax_payment_specification(
    *,
    execute_tool_name: str,
    method: WriteMethod,
    payload: dict[str, JsonValue],
    resource_id: str | None,
) -> WriteOperationSpec:
    """Build the server-known shape for one singular sales-tax-payment write."""

    action = {WriteMethod.POST: "create", WriteMethod.PUT: "update"}[method]
    expected_effect_state: dict[str, JsonValue] = {
        "action": action,
        "resource": "salesTaxPayment",
    }
    if resource_id is not None:
        expected_effect_state["id"] = resource_id
    return WriteOperationSpec(
        execute_tool_name=execute_tool_name,
        method=method,
        collection_path="/salesTaxPayments",
        singular_root="salesTaxPayment",
        plural_root="salesTaxPayments",
        additional_plural_roots=(),
        payload=payload,
        resource_id=resource_id,
        organization_id=None,
        summary=f"{action.capitalize()} one Billy sales-tax payment.",
        expected_effect_state=expected_effect_state,
    )
