"""Ticketed FastMCP tools for singular Billy organization writes."""

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


class _OrganizationWritePreviewInput(BaseModel):
    """Forbid undeclared outer fields while preserving opaque organization JSON."""

    model_config = ConfigDict(extra="forbid")


class OrganizationCreatePreviewInput(_OrganizationWritePreviewInput):
    """Input for previewing creation of one Billy organization."""

    organization: dict[str, JsonValue]


class OrganizationUpdatePreviewInput(_OrganizationWritePreviewInput):
    """Input for previewing an update to one Billy organization."""

    id: str = Field(min_length=1)
    organization: dict[str, JsonValue]

    @model_validator(mode="after")
    def organization_id_matches_route_id(self) -> OrganizationUpdatePreviewInput:
        """Keep an optional body identifier aligned with the route."""

        if "id" in self.organization and self.organization["id"] != self.id:
            raise ValueError("organization.id must match id")
        return self


def register_organization_write_tools(
    server: FastMCP,
    client: BillyHttpClient,
    write_protocol: WriteProtocolService,
) -> None:
    """Register exactly the four frozen organization create/update tools."""

    del client

    def api_organizations_create_preview(
        organization: dict[str, JsonValue],
    ) -> WritePreviewResult:
        """Preview creation of one Billy organization without a mutation."""

        input = OrganizationCreatePreviewInput(organization=organization)
        return write_protocol.preview(
            _organization_specification(
                execute_tool_name="api_organizations_create_execute",
                method=WriteMethod.POST,
                payload=input.organization,
                resource_id=None,
            )
        )

    def api_organizations_create_execute(
        confirmation_ticket: str = Field(min_length=1),
    ) -> WriteExecutionResult | ToolError:
        """Execute the exact organization creation in a ticket."""

        return write_protocol.execute(
            WriteExecuteInput(confirmation_ticket=confirmation_ticket),
            execute_tool_name="api_organizations_create_execute",
        )

    def api_organizations_update_preview(
        organization: dict[str, JsonValue],
        id: str = Field(min_length=1),
    ) -> WritePreviewResult:
        """Preview an update to one Billy organization without a mutation."""

        input = OrganizationUpdatePreviewInput(id=id, organization=organization)
        return write_protocol.preview(
            _organization_specification(
                execute_tool_name="api_organizations_update_execute",
                method=WriteMethod.PUT,
                payload=input.organization,
                resource_id=input.id,
            )
        )

    def api_organizations_update_execute(
        confirmation_ticket: str = Field(min_length=1),
    ) -> WriteExecutionResult | ToolError:
        """Execute the exact organization update in a ticket."""

        return write_protocol.execute(
            WriteExecuteInput(confirmation_ticket=confirmation_ticket),
            execute_tool_name="api_organizations_update_execute",
        )

    server.tool(
        name="api_organizations_create_preview",
        description="Preview creation of one Billy organization without a mutation.",
    )(api_organizations_create_preview)
    server.tool(
        name="api_organizations_create_execute",
        description="Execute a previewed Billy organization creation with its ticket.",
    )(api_organizations_create_execute)
    server.tool(
        name="api_organizations_update_preview",
        description="Preview an update to one Billy organization without a mutation.",
    )(api_organizations_update_preview)
    server.tool(
        name="api_organizations_update_execute",
        description="Execute a previewed Billy organization update with its ticket.",
    )(api_organizations_update_execute)


def _organization_specification(
    *,
    execute_tool_name: str,
    method: WriteMethod,
    payload: dict[str, JsonValue],
    resource_id: str | None,
) -> WriteOperationSpec:
    """Build the server-known shape for one singular organization write."""

    action = {WriteMethod.POST: "create", WriteMethod.PUT: "update"}[method]
    expected_effect_state: dict[str, JsonValue] = {
        "action": action,
        "resource": "organization",
    }
    if resource_id is not None:
        expected_effect_state["id"] = resource_id
    return WriteOperationSpec(
        execute_tool_name=execute_tool_name,
        method=method,
        collection_path="/organizations",
        singular_root="organization",
        plural_root="organizations",
        additional_plural_roots=(),
        payload=payload,
        resource_id=resource_id,
        organization_id=None,
        summary=f"{action.capitalize()} one Billy organization.",
        expected_effect_state=expected_effect_state,
    )
