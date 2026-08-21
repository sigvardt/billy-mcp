"""Ticketed FastMCP tools for documented singular Billy tax writes."""

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


class _TaxWritePreviewInput(BaseModel):
    """Base model that forbids undeclared fields around opaque tax payloads."""

    model_config = ConfigDict(extra="forbid", validate_by_alias=True, validate_by_name=True)


class TaxRateCreatePreviewInput(_TaxWritePreviewInput):
    """Input for previewing creation of one Billy tax rate."""

    tax_rate: dict[str, JsonValue] = Field(alias="taxRate", serialization_alias="taxRate")


class TaxRateUpdatePreviewInput(TaxRateCreatePreviewInput):
    """Input for previewing an update to one Billy tax rate."""

    id: str = Field(min_length=1)

    @model_validator(mode="after")
    def tax_rate_id_matches_route_id(self) -> TaxRateUpdatePreviewInput:
        """Keep an optional tax-rate body identifier aligned with its route."""

        if "id" in self.tax_rate and self.tax_rate["id"] != self.id:
            raise ValueError("taxRate.id must match id")
        return self


class TaxRateDeletePreviewInput(_TaxWritePreviewInput):
    """Input for previewing deletion of one Billy tax rate."""

    id: str = Field(min_length=1)


class TaxRateDeductionComponentCreatePreviewInput(_TaxWritePreviewInput):
    """Input for previewing creation of one Billy tax-rate deduction component."""

    tax_rate_deduction_component: dict[str, JsonValue] = Field(
        alias="taxRateDeductionComponent",
        serialization_alias="taxRateDeductionComponent",
    )


class TaxRateDeductionComponentUpdatePreviewInput(TaxRateDeductionComponentCreatePreviewInput):
    """Input for previewing an update to one Billy tax-rate deduction component."""

    id: str = Field(min_length=1)

    @model_validator(mode="after")
    def tax_rate_deduction_component_id_matches_route_id(
        self,
    ) -> TaxRateDeductionComponentUpdatePreviewInput:
        """Keep an optional component-body identifier aligned with its route."""

        if (
            "id" in self.tax_rate_deduction_component
            and self.tax_rate_deduction_component["id"] != self.id
        ):
            raise ValueError("taxRateDeductionComponent.id must match id")
        return self


class TaxRateDeductionComponentDeletePreviewInput(_TaxWritePreviewInput):
    """Input for previewing deletion of one Billy tax-rate deduction component."""

    id: str = Field(min_length=1)


def register_tax_write_tools(
    server: FastMCP,
    client: BillyHttpClient,
    write_protocol: WriteProtocolService,
) -> None:
    """Register exactly the twelve frozen ticketed tax write tools."""

    del client

    def api_tax_rates_create_preview(taxRate: dict[str, JsonValue]) -> WritePreviewResult:
        """Preview creation of one Billy tax rate without a mutation."""

        input = TaxRateCreatePreviewInput(taxRate=taxRate)
        return write_protocol.preview(
            _tax_rate_specification(
                execute_tool_name="api_tax_rates_create_execute",
                method=WriteMethod.POST,
                payload=input.tax_rate,
                resource_id=None,
            )
        )

    def api_tax_rates_create_execute(
        confirmation_ticket: str = Field(min_length=1),
    ) -> WriteExecutionResult | ToolError:
        """Execute the exact tax-rate creation in a confirmation ticket."""

        return write_protocol.execute(
            WriteExecuteInput(confirmation_ticket=confirmation_ticket),
            execute_tool_name="api_tax_rates_create_execute",
        )

    def api_tax_rates_update_preview(
        taxRate: dict[str, JsonValue],
        id: str = Field(min_length=1),
    ) -> WritePreviewResult:
        """Preview an update to one Billy tax rate without a mutation."""

        input = TaxRateUpdatePreviewInput(id=id, taxRate=taxRate)
        return write_protocol.preview(
            _tax_rate_specification(
                execute_tool_name="api_tax_rates_update_execute",
                method=WriteMethod.PUT,
                payload=input.tax_rate,
                resource_id=input.id,
            )
        )

    def api_tax_rates_update_execute(
        confirmation_ticket: str = Field(min_length=1),
    ) -> WriteExecutionResult | ToolError:
        """Execute the exact tax-rate update in a confirmation ticket."""

        return write_protocol.execute(
            WriteExecuteInput(confirmation_ticket=confirmation_ticket),
            execute_tool_name="api_tax_rates_update_execute",
        )

    def api_tax_rates_delete_preview(id: str = Field(min_length=1)) -> WritePreviewResult:
        """Preview deletion of one Billy tax rate without a mutation."""

        input = TaxRateDeletePreviewInput(id=id)
        return write_protocol.preview(
            _tax_rate_specification(
                execute_tool_name="api_tax_rates_delete_execute",
                method=WriteMethod.DELETE,
                payload=None,
                resource_id=input.id,
            )
        )

    def api_tax_rates_delete_execute(
        confirmation_ticket: str = Field(min_length=1),
    ) -> WriteExecutionResult | ToolError:
        """Execute the exact tax-rate deletion in a confirmation ticket."""

        return write_protocol.execute(
            WriteExecuteInput(confirmation_ticket=confirmation_ticket),
            execute_tool_name="api_tax_rates_delete_execute",
        )

    def api_tax_rate_deduction_components_create_preview(
        taxRateDeductionComponent: dict[str, JsonValue],
    ) -> WritePreviewResult:
        """Preview creation of one Billy tax-rate deduction component without a mutation."""

        input = TaxRateDeductionComponentCreatePreviewInput(
            taxRateDeductionComponent=taxRateDeductionComponent
        )
        return write_protocol.preview(
            _tax_rate_deduction_component_specification(
                execute_tool_name="api_tax_rate_deduction_components_create_execute",
                method=WriteMethod.POST,
                payload=input.tax_rate_deduction_component,
                resource_id=None,
            )
        )

    def api_tax_rate_deduction_components_create_execute(
        confirmation_ticket: str = Field(min_length=1),
    ) -> WriteExecutionResult | ToolError:
        """Execute the exact tax-rate deduction-component creation in a ticket."""

        return write_protocol.execute(
            WriteExecuteInput(confirmation_ticket=confirmation_ticket),
            execute_tool_name="api_tax_rate_deduction_components_create_execute",
        )

    def api_tax_rate_deduction_components_update_preview(
        taxRateDeductionComponent: dict[str, JsonValue],
        id: str = Field(min_length=1),
    ) -> WritePreviewResult:
        """Preview an update to one Billy tax-rate deduction component without a mutation."""

        input = TaxRateDeductionComponentUpdatePreviewInput(
            id=id,
            taxRateDeductionComponent=taxRateDeductionComponent,
        )
        return write_protocol.preview(
            _tax_rate_deduction_component_specification(
                execute_tool_name="api_tax_rate_deduction_components_update_execute",
                method=WriteMethod.PUT,
                payload=input.tax_rate_deduction_component,
                resource_id=input.id,
            )
        )

    def api_tax_rate_deduction_components_update_execute(
        confirmation_ticket: str = Field(min_length=1),
    ) -> WriteExecutionResult | ToolError:
        """Execute the exact tax-rate deduction-component update in a ticket."""

        return write_protocol.execute(
            WriteExecuteInput(confirmation_ticket=confirmation_ticket),
            execute_tool_name="api_tax_rate_deduction_components_update_execute",
        )

    def api_tax_rate_deduction_components_delete_preview(
        id: str = Field(min_length=1),
    ) -> WritePreviewResult:
        """Preview deletion of one Billy tax-rate deduction component without a mutation."""

        input = TaxRateDeductionComponentDeletePreviewInput(id=id)
        return write_protocol.preview(
            _tax_rate_deduction_component_specification(
                execute_tool_name="api_tax_rate_deduction_components_delete_execute",
                method=WriteMethod.DELETE,
                payload=None,
                resource_id=input.id,
            )
        )

    def api_tax_rate_deduction_components_delete_execute(
        confirmation_ticket: str = Field(min_length=1),
    ) -> WriteExecutionResult | ToolError:
        """Execute the exact tax-rate deduction-component deletion in a ticket."""

        return write_protocol.execute(
            WriteExecuteInput(confirmation_ticket=confirmation_ticket),
            execute_tool_name="api_tax_rate_deduction_components_delete_execute",
        )

    server.tool(
        name="api_tax_rates_create_preview",
        description="Preview creation of one Billy tax rate without a mutation.",
    )(api_tax_rates_create_preview)
    server.tool(
        name="api_tax_rates_create_execute",
        description="Execute a previewed Billy tax-rate creation with its ticket.",
    )(api_tax_rates_create_execute)
    server.tool(
        name="api_tax_rates_update_preview",
        description="Preview an update to one Billy tax rate without a mutation.",
    )(api_tax_rates_update_preview)
    server.tool(
        name="api_tax_rates_update_execute",
        description="Execute a previewed Billy tax-rate update with its ticket.",
    )(api_tax_rates_update_execute)
    server.tool(
        name="api_tax_rates_delete_preview",
        description="Preview deletion of one Billy tax rate without a mutation.",
    )(api_tax_rates_delete_preview)
    server.tool(
        name="api_tax_rates_delete_execute",
        description="Execute a previewed Billy tax-rate deletion with its ticket.",
    )(api_tax_rates_delete_execute)
    server.tool(
        name="api_tax_rate_deduction_components_create_preview",
        description=(
            "Preview creation of one Billy tax-rate deduction component without a mutation."
        ),
    )(api_tax_rate_deduction_components_create_preview)
    server.tool(
        name="api_tax_rate_deduction_components_create_execute",
        description=(
            "Execute a previewed Billy tax-rate deduction-component creation with its ticket."
        ),
    )(api_tax_rate_deduction_components_create_execute)
    server.tool(
        name="api_tax_rate_deduction_components_update_preview",
        description=(
            "Preview an update to one Billy tax-rate deduction component without a mutation."
        ),
    )(api_tax_rate_deduction_components_update_preview)
    server.tool(
        name="api_tax_rate_deduction_components_update_execute",
        description=(
            "Execute a previewed Billy tax-rate deduction-component update with its ticket."
        ),
    )(api_tax_rate_deduction_components_update_execute)
    server.tool(
        name="api_tax_rate_deduction_components_delete_preview",
        description=(
            "Preview deletion of one Billy tax-rate deduction component without a mutation."
        ),
    )(api_tax_rate_deduction_components_delete_preview)
    server.tool(
        name="api_tax_rate_deduction_components_delete_execute",
        description=(
            "Execute a previewed Billy tax-rate deduction-component deletion with its ticket."
        ),
    )(api_tax_rate_deduction_components_delete_execute)


def _tax_rate_specification(
    *,
    execute_tool_name: str,
    method: WriteMethod,
    payload: dict[str, JsonValue] | None,
    resource_id: str | None,
) -> WriteOperationSpec:
    """Build the server-known singular write shape for one Billy tax rate."""

    return _tax_specification(
        execute_tool_name=execute_tool_name,
        method=method,
        collection_path="/taxRates",
        singular_root="taxRate",
        plural_root="taxRates",
        additional_plural_roots=("taxRateDeductionComponents",),
        payload=payload,
        resource_id=resource_id,
        resource="taxRate",
    )


def _tax_rate_deduction_component_specification(
    *,
    execute_tool_name: str,
    method: WriteMethod,
    payload: dict[str, JsonValue] | None,
    resource_id: str | None,
) -> WriteOperationSpec:
    """Build the server-known singular write shape for one deduction component."""

    return _tax_specification(
        execute_tool_name=execute_tool_name,
        method=method,
        collection_path="/taxRateDeductionComponents",
        singular_root="taxRateDeductionComponent",
        plural_root="taxRateDeductionComponents",
        additional_plural_roots=(),
        payload=payload,
        resource_id=resource_id,
        resource="taxRateDeductionComponent",
    )


def _tax_specification(
    *,
    execute_tool_name: str,
    method: WriteMethod,
    collection_path: str,
    singular_root: str,
    plural_root: str,
    additional_plural_roots: tuple[str, ...],
    payload: dict[str, JsonValue] | None,
    resource_id: str | None,
    resource: str,
) -> WriteOperationSpec:
    """Build one complete server-known tax operation for the shared protocol."""

    action = {
        WriteMethod.POST: "create",
        WriteMethod.PUT: "update",
        WriteMethod.DELETE: "delete",
    }[method]
    display_resource = {
        "taxRate": "tax rate",
        "taxRateDeductionComponent": "tax-rate deduction component",
    }[resource]
    expected_effect_state: dict[str, JsonValue] = {"action": action, "resource": resource}
    if resource_id is not None:
        expected_effect_state["id"] = resource_id
    return WriteOperationSpec(
        execute_tool_name=execute_tool_name,
        method=method,
        collection_path=collection_path,
        singular_root=singular_root,
        plural_root=plural_root,
        additional_plural_roots=additional_plural_roots,
        payload=payload,
        resource_id=resource_id,
        organization_id=None,
        summary=f"{action.capitalize()} one Billy {display_resource}.",
        expected_effect_state=expected_effect_state,
    )
