"""Ticketed FastMCP tools for singular Billy sales-tax-return updates."""

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


class _SalesTaxReturnWritePreviewInput(BaseModel):
    """Forbid undeclared outer fields while preserving opaque return JSON."""

    model_config = ConfigDict(extra="forbid")


class SalesTaxReturnUpdatePreviewInput(_SalesTaxReturnWritePreviewInput):
    """Input for previewing an update to one Billy sales-tax return."""

    id: str = Field(min_length=1)
    salesTaxReturn: dict[str, JsonValue]

    @model_validator(mode="after")
    def sales_tax_return_id_matches_route_id(self) -> SalesTaxReturnUpdatePreviewInput:
        """Keep an optional body identifier aligned with the route."""

        if "id" in self.salesTaxReturn and self.salesTaxReturn["id"] != self.id:
            raise ValueError("salesTaxReturn.id must match id")
        return self


def register_sales_tax_return_write_tools(
    server: FastMCP,
    client: BillyHttpClient,
    write_protocol: WriteProtocolService,
) -> None:
    """Register exactly the two frozen sales-tax-return update tools."""

    del client

    def api_sales_tax_returns_update_preview(
        salesTaxReturn: dict[str, JsonValue],
        id: str = Field(min_length=1),
    ) -> WritePreviewResult:
        """Preview an update to one Billy sales-tax return without a mutation."""

        input = SalesTaxReturnUpdatePreviewInput(id=id, salesTaxReturn=salesTaxReturn)
        return write_protocol.preview(
            _sales_tax_return_update_specification(
                payload=input.salesTaxReturn,
                resource_id=input.id,
            )
        )

    def api_sales_tax_returns_update_execute(
        confirmation_ticket: str = Field(min_length=1),
    ) -> WriteExecutionResult | ToolError:
        """Execute the exact sales-tax-return update in a ticket."""

        return write_protocol.execute(
            WriteExecuteInput(confirmation_ticket=confirmation_ticket),
            execute_tool_name="api_sales_tax_returns_update_execute",
        )

    server.tool(
        name="api_sales_tax_returns_update_preview",
        description="Preview an update to one Billy sales-tax return without a mutation.",
    )(api_sales_tax_returns_update_preview)
    server.tool(
        name="api_sales_tax_returns_update_execute",
        description="Execute a previewed Billy sales-tax-return update with its ticket.",
    )(api_sales_tax_returns_update_execute)


def _sales_tax_return_update_specification(
    *, payload: dict[str, JsonValue], resource_id: str
) -> WriteOperationSpec:
    """Build the server-known shape for one singular sales-tax-return update."""

    return WriteOperationSpec(
        execute_tool_name="api_sales_tax_returns_update_execute",
        method=WriteMethod.PUT,
        collection_path="/salesTaxReturns",
        singular_root="salesTaxReturn",
        plural_root="salesTaxReturns",
        additional_plural_roots=(),
        payload=payload,
        resource_id=resource_id,
        organization_id=None,
        summary="Update one Billy sales-tax return.",
        expected_effect_state={
            "action": "update",
            "resource": "salesTaxReturn",
            "id": resource_id,
        },
    )
