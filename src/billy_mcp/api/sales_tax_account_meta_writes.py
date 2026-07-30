"""Ticketed FastMCP tools for singular Billy sales-tax account and meta-field writes."""

from __future__ import annotations

from collections.abc import Callable

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


class _SalesTaxAccountMetaWritePreviewInput(BaseModel):
    """Forbid undeclared outer fields while keeping documented payloads opaque."""

    model_config = ConfigDict(extra="forbid", validate_by_alias=True, validate_by_name=True)


class SalesTaxAccountCreatePreviewInput(_SalesTaxAccountMetaWritePreviewInput):
    """Input for previewing creation of one Billy sales-tax account."""

    sales_tax_account: dict[str, JsonValue] = Field(
        alias="salesTaxAccount",
        serialization_alias="salesTaxAccount",
    )


class SalesTaxAccountUpdatePreviewInput(SalesTaxAccountCreatePreviewInput):
    """Input for previewing a partial update to one Billy sales-tax account."""

    id: str = Field(min_length=1)

    @model_validator(mode="after")
    def sales_tax_account_id_matches_route_id(self) -> SalesTaxAccountUpdatePreviewInput:
        """Keep an optional account body identifier aligned with the route."""

        if "id" in self.sales_tax_account and self.sales_tax_account["id"] != self.id:
            raise ValueError("salesTaxAccount.id must match id")
        return self


class SalesTaxAccountDeletePreviewInput(_SalesTaxAccountMetaWritePreviewInput):
    """Input for previewing deletion of one Billy sales-tax account."""

    id: str = Field(min_length=1)


class SalesTaxMetaFieldCreatePreviewInput(_SalesTaxAccountMetaWritePreviewInput):
    """Input for previewing creation of one Billy sales-tax meta field."""

    sales_tax_meta_field: dict[str, JsonValue] = Field(
        alias="salesTaxMetaField",
        serialization_alias="salesTaxMetaField",
    )


class SalesTaxMetaFieldUpdatePreviewInput(SalesTaxMetaFieldCreatePreviewInput):
    """Input for previewing a partial update to one Billy sales-tax meta field."""

    id: str = Field(min_length=1)

    @model_validator(mode="after")
    def sales_tax_meta_field_id_matches_route_id(self) -> SalesTaxMetaFieldUpdatePreviewInput:
        """Keep an optional meta-field body identifier aligned with the route."""

        if "id" in self.sales_tax_meta_field and self.sales_tax_meta_field["id"] != self.id:
            raise ValueError("salesTaxMetaField.id must match id")
        return self


class SalesTaxMetaFieldDeletePreviewInput(_SalesTaxAccountMetaWritePreviewInput):
    """Input for previewing deletion of one Billy sales-tax meta field."""

    id: str = Field(min_length=1)


def register_sales_tax_account_meta_write_tools(
    server: FastMCP,
    client: BillyHttpClient,
    write_protocol: WriteProtocolService,
) -> None:
    """Register exactly the twelve frozen sales-tax account and meta-field tools."""

    del client

    def api_sales_tax_accounts_create_preview(
        salesTaxAccount: dict[str, JsonValue],
    ) -> WritePreviewResult:
        """Preview creation of one Billy sales-tax account without a mutation."""

        input = SalesTaxAccountCreatePreviewInput(salesTaxAccount=salesTaxAccount)
        return write_protocol.preview(
            _sales_tax_account_specification(
                execute_tool_name="api_sales_tax_accounts_create_execute",
                method=WriteMethod.POST,
                payload=input.sales_tax_account,
                resource_id=None,
            )
        )

    def api_sales_tax_accounts_create_execute(
        confirmation_ticket: str = Field(min_length=1),
    ) -> WriteExecutionResult | ToolError:
        """Execute the exact sales-tax account creation in a confirmation ticket."""

        return write_protocol.execute(
            WriteExecuteInput(confirmation_ticket=confirmation_ticket),
            execute_tool_name="api_sales_tax_accounts_create_execute",
        )

    def api_sales_tax_accounts_update_preview(
        salesTaxAccount: dict[str, JsonValue],
        id: str = Field(min_length=1),
    ) -> WritePreviewResult:
        """Preview an update to one Billy sales-tax account without a mutation."""

        input = SalesTaxAccountUpdatePreviewInput(id=id, salesTaxAccount=salesTaxAccount)
        return write_protocol.preview(
            _sales_tax_account_specification(
                execute_tool_name="api_sales_tax_accounts_update_execute",
                method=WriteMethod.PUT,
                payload=input.sales_tax_account,
                resource_id=input.id,
            )
        )

    def api_sales_tax_accounts_update_execute(
        confirmation_ticket: str = Field(min_length=1),
    ) -> WriteExecutionResult | ToolError:
        """Execute the exact sales-tax account update in a confirmation ticket."""

        return write_protocol.execute(
            WriteExecuteInput(confirmation_ticket=confirmation_ticket),
            execute_tool_name="api_sales_tax_accounts_update_execute",
        )

    def api_sales_tax_accounts_delete_preview(id: str = Field(min_length=1)) -> WritePreviewResult:
        """Preview deletion of one Billy sales-tax account without a mutation."""

        input = SalesTaxAccountDeletePreviewInput(id=id)
        return write_protocol.preview(
            _sales_tax_account_specification(
                execute_tool_name="api_sales_tax_accounts_delete_execute",
                method=WriteMethod.DELETE,
                payload=None,
                resource_id=input.id,
            )
        )

    def api_sales_tax_accounts_delete_execute(
        confirmation_ticket: str = Field(min_length=1),
    ) -> WriteExecutionResult | ToolError:
        """Execute the exact sales-tax account deletion in a confirmation ticket."""

        return write_protocol.execute(
            WriteExecuteInput(confirmation_ticket=confirmation_ticket),
            execute_tool_name="api_sales_tax_accounts_delete_execute",
        )

    def api_sales_tax_meta_fields_create_preview(
        salesTaxMetaField: dict[str, JsonValue],
    ) -> WritePreviewResult:
        """Preview creation of one Billy sales-tax meta field without a mutation."""

        input = SalesTaxMetaFieldCreatePreviewInput(salesTaxMetaField=salesTaxMetaField)
        return write_protocol.preview(
            _sales_tax_meta_field_specification(
                execute_tool_name="api_sales_tax_meta_fields_create_execute",
                method=WriteMethod.POST,
                payload=input.sales_tax_meta_field,
                resource_id=None,
            )
        )

    def api_sales_tax_meta_fields_create_execute(
        confirmation_ticket: str = Field(min_length=1),
    ) -> WriteExecutionResult | ToolError:
        """Execute the exact sales-tax meta-field creation in a confirmation ticket."""

        return write_protocol.execute(
            WriteExecuteInput(confirmation_ticket=confirmation_ticket),
            execute_tool_name="api_sales_tax_meta_fields_create_execute",
        )

    def api_sales_tax_meta_fields_update_preview(
        salesTaxMetaField: dict[str, JsonValue],
        id: str = Field(min_length=1),
    ) -> WritePreviewResult:
        """Preview an update to one Billy sales-tax meta field without a mutation."""

        input = SalesTaxMetaFieldUpdatePreviewInput(id=id, salesTaxMetaField=salesTaxMetaField)
        return write_protocol.preview(
            _sales_tax_meta_field_specification(
                execute_tool_name="api_sales_tax_meta_fields_update_execute",
                method=WriteMethod.PUT,
                payload=input.sales_tax_meta_field,
                resource_id=input.id,
            )
        )

    def api_sales_tax_meta_fields_update_execute(
        confirmation_ticket: str = Field(min_length=1),
    ) -> WriteExecutionResult | ToolError:
        """Execute the exact sales-tax meta-field update in a confirmation ticket."""

        return write_protocol.execute(
            WriteExecuteInput(confirmation_ticket=confirmation_ticket),
            execute_tool_name="api_sales_tax_meta_fields_update_execute",
        )

    def api_sales_tax_meta_fields_delete_preview(
        id: str = Field(min_length=1),
    ) -> WritePreviewResult:
        """Preview deletion of one Billy sales-tax meta field without a mutation."""

        input = SalesTaxMetaFieldDeletePreviewInput(id=id)
        return write_protocol.preview(
            _sales_tax_meta_field_specification(
                execute_tool_name="api_sales_tax_meta_fields_delete_execute",
                method=WriteMethod.DELETE,
                payload=None,
                resource_id=input.id,
            )
        )

    def api_sales_tax_meta_fields_delete_execute(
        confirmation_ticket: str = Field(min_length=1),
    ) -> WriteExecutionResult | ToolError:
        """Execute the exact sales-tax meta-field deletion in a confirmation ticket."""

        return write_protocol.execute(
            WriteExecuteInput(confirmation_ticket=confirmation_ticket),
            execute_tool_name="api_sales_tax_meta_fields_delete_execute",
        )

    _register_tools(
        server,
        (
            (
                "api_sales_tax_accounts_create_preview",
                api_sales_tax_accounts_create_preview,
                "Preview creation of one Billy sales-tax account without a mutation.",
            ),
            (
                "api_sales_tax_accounts_create_execute",
                api_sales_tax_accounts_create_execute,
                "Execute a previewed Billy sales-tax account creation with its ticket.",
            ),
            (
                "api_sales_tax_accounts_update_preview",
                api_sales_tax_accounts_update_preview,
                "Preview an update to one Billy sales-tax account without a mutation.",
            ),
            (
                "api_sales_tax_accounts_update_execute",
                api_sales_tax_accounts_update_execute,
                "Execute a previewed Billy sales-tax account update with its ticket.",
            ),
            (
                "api_sales_tax_accounts_delete_preview",
                api_sales_tax_accounts_delete_preview,
                "Preview deletion of one Billy sales-tax account without a mutation.",
            ),
            (
                "api_sales_tax_accounts_delete_execute",
                api_sales_tax_accounts_delete_execute,
                "Execute a previewed Billy sales-tax account deletion with its ticket.",
            ),
            (
                "api_sales_tax_meta_fields_create_preview",
                api_sales_tax_meta_fields_create_preview,
                "Preview creation of one Billy sales-tax meta field without a mutation.",
            ),
            (
                "api_sales_tax_meta_fields_create_execute",
                api_sales_tax_meta_fields_create_execute,
                "Execute a previewed Billy sales-tax meta-field creation with its ticket.",
            ),
            (
                "api_sales_tax_meta_fields_update_preview",
                api_sales_tax_meta_fields_update_preview,
                "Preview an update to one Billy sales-tax meta field without a mutation.",
            ),
            (
                "api_sales_tax_meta_fields_update_execute",
                api_sales_tax_meta_fields_update_execute,
                "Execute a previewed Billy sales-tax meta-field update with its ticket.",
            ),
            (
                "api_sales_tax_meta_fields_delete_preview",
                api_sales_tax_meta_fields_delete_preview,
                "Preview deletion of one Billy sales-tax meta field without a mutation.",
            ),
            (
                "api_sales_tax_meta_fields_delete_execute",
                api_sales_tax_meta_fields_delete_execute,
                "Execute a previewed Billy sales-tax meta-field deletion with its ticket.",
            ),
        ),
    )


def _register_tools(
    server: FastMCP,
    tools: tuple[tuple[str, Callable[..., object], str], ...],
) -> None:
    """Register the fixed public names without exposing dynamic request inputs."""

    for name, handler, description in tools:
        server.tool(name=name, description=description)(handler)


def _sales_tax_account_specification(
    *,
    execute_tool_name: str,
    method: WriteMethod,
    payload: dict[str, JsonValue] | None,
    resource_id: str | None,
) -> WriteOperationSpec:
    """Build the complete server-known shape for one sales-tax account CUD operation."""

    return _sales_tax_account_meta_specification(
        execute_tool_name=execute_tool_name,
        method=method,
        collection_path="/salesTaxAccounts",
        singular_root="salesTaxAccount",
        plural_root="salesTaxAccounts",
        payload=payload,
        resource_id=resource_id,
        resource="salesTaxAccount",
        display_resource="sales-tax account",
    )


def _sales_tax_meta_field_specification(
    *,
    execute_tool_name: str,
    method: WriteMethod,
    payload: dict[str, JsonValue] | None,
    resource_id: str | None,
) -> WriteOperationSpec:
    """Build the complete server-known shape for one sales-tax meta-field CUD operation."""

    return _sales_tax_account_meta_specification(
        execute_tool_name=execute_tool_name,
        method=method,
        collection_path="/salesTaxMetaFields",
        singular_root="salesTaxMetaField",
        plural_root="salesTaxMetaFields",
        payload=payload,
        resource_id=resource_id,
        resource="salesTaxMetaField",
        display_resource="sales-tax meta field",
    )


def _sales_tax_account_meta_specification(
    *,
    execute_tool_name: str,
    method: WriteMethod,
    collection_path: str,
    singular_root: str,
    plural_root: str,
    payload: dict[str, JsonValue] | None,
    resource_id: str | None,
    resource: str,
    display_resource: str,
) -> WriteOperationSpec:
    """Build one complete fixed write specification for the shared protocol."""

    action = {
        WriteMethod.POST: "create",
        WriteMethod.PUT: "update",
        WriteMethod.DELETE: "delete",
    }[method]
    expected_effect_state: dict[str, JsonValue] = {"action": action, "resource": resource}
    if resource_id is not None:
        expected_effect_state["id"] = resource_id
    return WriteOperationSpec(
        execute_tool_name=execute_tool_name,
        method=method,
        collection_path=collection_path,
        singular_root=singular_root,
        plural_root=plural_root,
        additional_plural_roots=(),
        payload=payload,
        resource_id=resource_id,
        organization_id=None,
        summary=f"{action.capitalize()} one Billy {display_resource}.",
        expected_effect_state=expected_effect_state,
    )
