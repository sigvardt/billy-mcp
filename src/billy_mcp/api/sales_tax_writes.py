"""Ticketed FastMCP tools for documented singular Billy sales-tax writes."""

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


class _SalesTaxWritePreviewInput(BaseModel):
    """Base model that forbids undeclared fields around opaque sales-tax payloads."""

    model_config = ConfigDict(extra="forbid", validate_by_alias=True, validate_by_name=True)


class SalesTaxRulesetCreatePreviewInput(_SalesTaxWritePreviewInput):
    """Input for previewing creation of one Billy sales-tax ruleset."""

    sales_tax_ruleset: dict[str, JsonValue] = Field(
        alias="salesTaxRuleset",
        serialization_alias="salesTaxRuleset",
    )


class SalesTaxRulesetUpdatePreviewInput(SalesTaxRulesetCreatePreviewInput):
    """Input for previewing an update to one Billy sales-tax ruleset."""

    id: str = Field(min_length=1)

    @model_validator(mode="after")
    def sales_tax_ruleset_id_matches_route_id(self) -> SalesTaxRulesetUpdatePreviewInput:
        """Keep an optional ruleset body identifier aligned with its route."""

        if "id" in self.sales_tax_ruleset and self.sales_tax_ruleset["id"] != self.id:
            raise ValueError("salesTaxRuleset.id must match id")
        return self


class SalesTaxRulesetDeletePreviewInput(_SalesTaxWritePreviewInput):
    """Input for previewing deletion of one Billy sales-tax ruleset."""

    id: str = Field(min_length=1)


class SalesTaxRuleCreatePreviewInput(_SalesTaxWritePreviewInput):
    """Input for previewing creation of one Billy sales-tax rule."""

    sales_tax_rule: dict[str, JsonValue] = Field(
        alias="salesTaxRule",
        serialization_alias="salesTaxRule",
    )


class SalesTaxRuleUpdatePreviewInput(SalesTaxRuleCreatePreviewInput):
    """Input for previewing an update to one Billy sales-tax rule."""

    id: str = Field(min_length=1)

    @model_validator(mode="after")
    def sales_tax_rule_id_matches_route_id(self) -> SalesTaxRuleUpdatePreviewInput:
        """Keep an optional rule body identifier aligned with its route."""

        if "id" in self.sales_tax_rule and self.sales_tax_rule["id"] != self.id:
            raise ValueError("salesTaxRule.id must match id")
        return self


class SalesTaxRuleDeletePreviewInput(_SalesTaxWritePreviewInput):
    """Input for previewing deletion of one Billy sales-tax rule."""

    id: str = Field(min_length=1)


def register_sales_tax_write_tools(
    server: FastMCP,
    client: BillyHttpClient,
    write_protocol: WriteProtocolService,
) -> None:
    """Register exactly the twelve frozen ticketed sales-tax write tools."""

    del client

    def api_sales_tax_rulesets_create_preview(
        salesTaxRuleset: dict[str, JsonValue],
    ) -> WritePreviewResult:
        """Preview creation of one Billy sales-tax ruleset without a mutation."""

        input = SalesTaxRulesetCreatePreviewInput(salesTaxRuleset=salesTaxRuleset)
        return write_protocol.preview(
            _sales_tax_ruleset_specification(
                execute_tool_name="api_sales_tax_rulesets_create_execute",
                method=WriteMethod.POST,
                payload=input.sales_tax_ruleset,
                resource_id=None,
            )
        )

    def api_sales_tax_rulesets_create_execute(
        confirmation_ticket: str = Field(min_length=1),
    ) -> WriteExecutionResult | ToolError:
        """Execute the exact sales-tax ruleset creation in a confirmation ticket."""

        return write_protocol.execute(
            WriteExecuteInput(confirmation_ticket=confirmation_ticket),
            execute_tool_name="api_sales_tax_rulesets_create_execute",
        )

    def api_sales_tax_rulesets_update_preview(
        salesTaxRuleset: dict[str, JsonValue],
        id: str = Field(min_length=1),
    ) -> WritePreviewResult:
        """Preview an update to one Billy sales-tax ruleset without a mutation."""

        input = SalesTaxRulesetUpdatePreviewInput(id=id, salesTaxRuleset=salesTaxRuleset)
        return write_protocol.preview(
            _sales_tax_ruleset_specification(
                execute_tool_name="api_sales_tax_rulesets_update_execute",
                method=WriteMethod.PUT,
                payload=input.sales_tax_ruleset,
                resource_id=input.id,
            )
        )

    def api_sales_tax_rulesets_update_execute(
        confirmation_ticket: str = Field(min_length=1),
    ) -> WriteExecutionResult | ToolError:
        """Execute the exact sales-tax ruleset update in a confirmation ticket."""

        return write_protocol.execute(
            WriteExecuteInput(confirmation_ticket=confirmation_ticket),
            execute_tool_name="api_sales_tax_rulesets_update_execute",
        )

    def api_sales_tax_rulesets_delete_preview(id: str = Field(min_length=1)) -> WritePreviewResult:
        """Preview deletion of one Billy sales-tax ruleset without a mutation."""

        input = SalesTaxRulesetDeletePreviewInput(id=id)
        return write_protocol.preview(
            _sales_tax_ruleset_specification(
                execute_tool_name="api_sales_tax_rulesets_delete_execute",
                method=WriteMethod.DELETE,
                payload=None,
                resource_id=input.id,
            )
        )

    def api_sales_tax_rulesets_delete_execute(
        confirmation_ticket: str = Field(min_length=1),
    ) -> WriteExecutionResult | ToolError:
        """Execute the exact sales-tax ruleset deletion in a confirmation ticket."""

        return write_protocol.execute(
            WriteExecuteInput(confirmation_ticket=confirmation_ticket),
            execute_tool_name="api_sales_tax_rulesets_delete_execute",
        )

    def api_sales_tax_rules_create_preview(
        salesTaxRule: dict[str, JsonValue],
    ) -> WritePreviewResult:
        """Preview creation of one Billy sales-tax rule without a mutation."""

        input = SalesTaxRuleCreatePreviewInput(salesTaxRule=salesTaxRule)
        return write_protocol.preview(
            _sales_tax_rule_specification(
                execute_tool_name="api_sales_tax_rules_create_execute",
                method=WriteMethod.POST,
                payload=input.sales_tax_rule,
                resource_id=None,
            )
        )

    def api_sales_tax_rules_create_execute(
        confirmation_ticket: str = Field(min_length=1),
    ) -> WriteExecutionResult | ToolError:
        """Execute the exact sales-tax rule creation in a confirmation ticket."""

        return write_protocol.execute(
            WriteExecuteInput(confirmation_ticket=confirmation_ticket),
            execute_tool_name="api_sales_tax_rules_create_execute",
        )

    def api_sales_tax_rules_update_preview(
        salesTaxRule: dict[str, JsonValue],
        id: str = Field(min_length=1),
    ) -> WritePreviewResult:
        """Preview an update to one Billy sales-tax rule without a mutation."""

        input = SalesTaxRuleUpdatePreviewInput(id=id, salesTaxRule=salesTaxRule)
        return write_protocol.preview(
            _sales_tax_rule_specification(
                execute_tool_name="api_sales_tax_rules_update_execute",
                method=WriteMethod.PUT,
                payload=input.sales_tax_rule,
                resource_id=input.id,
            )
        )

    def api_sales_tax_rules_update_execute(
        confirmation_ticket: str = Field(min_length=1),
    ) -> WriteExecutionResult | ToolError:
        """Execute the exact sales-tax rule update in a confirmation ticket."""

        return write_protocol.execute(
            WriteExecuteInput(confirmation_ticket=confirmation_ticket),
            execute_tool_name="api_sales_tax_rules_update_execute",
        )

    def api_sales_tax_rules_delete_preview(id: str = Field(min_length=1)) -> WritePreviewResult:
        """Preview deletion of one Billy sales-tax rule without a mutation."""

        input = SalesTaxRuleDeletePreviewInput(id=id)
        return write_protocol.preview(
            _sales_tax_rule_specification(
                execute_tool_name="api_sales_tax_rules_delete_execute",
                method=WriteMethod.DELETE,
                payload=None,
                resource_id=input.id,
            )
        )

    def api_sales_tax_rules_delete_execute(
        confirmation_ticket: str = Field(min_length=1),
    ) -> WriteExecutionResult | ToolError:
        """Execute the exact sales-tax rule deletion in a confirmation ticket."""

        return write_protocol.execute(
            WriteExecuteInput(confirmation_ticket=confirmation_ticket),
            execute_tool_name="api_sales_tax_rules_delete_execute",
        )

    _register_tools(
        server,
        (
            (
                "api_sales_tax_rulesets_create_preview",
                api_sales_tax_rulesets_create_preview,
                "Preview creation of one Billy sales-tax ruleset without a mutation.",
            ),
            (
                "api_sales_tax_rulesets_create_execute",
                api_sales_tax_rulesets_create_execute,
                "Execute a previewed Billy sales-tax ruleset creation with its ticket.",
            ),
            (
                "api_sales_tax_rulesets_update_preview",
                api_sales_tax_rulesets_update_preview,
                "Preview an update to one Billy sales-tax ruleset without a mutation.",
            ),
            (
                "api_sales_tax_rulesets_update_execute",
                api_sales_tax_rulesets_update_execute,
                "Execute a previewed Billy sales-tax ruleset update with its ticket.",
            ),
            (
                "api_sales_tax_rulesets_delete_preview",
                api_sales_tax_rulesets_delete_preview,
                "Preview deletion of one Billy sales-tax ruleset without a mutation.",
            ),
            (
                "api_sales_tax_rulesets_delete_execute",
                api_sales_tax_rulesets_delete_execute,
                "Execute a previewed Billy sales-tax ruleset deletion with its ticket.",
            ),
            (
                "api_sales_tax_rules_create_preview",
                api_sales_tax_rules_create_preview,
                "Preview creation of one Billy sales-tax rule without a mutation.",
            ),
            (
                "api_sales_tax_rules_create_execute",
                api_sales_tax_rules_create_execute,
                "Execute a previewed Billy sales-tax rule creation with its ticket.",
            ),
            (
                "api_sales_tax_rules_update_preview",
                api_sales_tax_rules_update_preview,
                "Preview an update to one Billy sales-tax rule without a mutation.",
            ),
            (
                "api_sales_tax_rules_update_execute",
                api_sales_tax_rules_update_execute,
                "Execute a previewed Billy sales-tax rule update with its ticket.",
            ),
            (
                "api_sales_tax_rules_delete_preview",
                api_sales_tax_rules_delete_preview,
                "Preview deletion of one Billy sales-tax rule without a mutation.",
            ),
            (
                "api_sales_tax_rules_delete_execute",
                api_sales_tax_rules_delete_execute,
                "Execute a previewed Billy sales-tax rule deletion with its ticket.",
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


def _sales_tax_ruleset_specification(
    *,
    execute_tool_name: str,
    method: WriteMethod,
    payload: dict[str, JsonValue] | None,
    resource_id: str | None,
) -> WriteOperationSpec:
    """Build the server-known singular write shape for one sales-tax ruleset."""

    return _sales_tax_specification(
        execute_tool_name=execute_tool_name,
        method=method,
        collection_path="/salesTaxRulesets",
        singular_root="salesTaxRuleset",
        plural_root="salesTaxRulesets",
        additional_plural_roots=("salesTaxRules",),
        payload=payload,
        resource_id=resource_id,
        resource="salesTaxRuleset",
    )


def _sales_tax_rule_specification(
    *,
    execute_tool_name: str,
    method: WriteMethod,
    payload: dict[str, JsonValue] | None,
    resource_id: str | None,
) -> WriteOperationSpec:
    """Build the server-known singular write shape for one sales-tax rule."""

    return _sales_tax_specification(
        execute_tool_name=execute_tool_name,
        method=method,
        collection_path="/salesTaxRules",
        singular_root="salesTaxRule",
        plural_root="salesTaxRules",
        additional_plural_roots=(),
        payload=payload,
        resource_id=resource_id,
        resource="salesTaxRule",
    )


def _sales_tax_specification(
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
    """Build one complete server-known sales-tax operation for the shared protocol."""

    action = {
        WriteMethod.POST: "create",
        WriteMethod.PUT: "update",
        WriteMethod.DELETE: "delete",
    }[method]
    display_resource = {
        "salesTaxRuleset": "sales-tax ruleset",
        "salesTaxRule": "sales-tax rule",
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
