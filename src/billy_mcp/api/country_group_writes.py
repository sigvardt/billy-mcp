"""Ticketed FastMCP tools for documented singular Billy country-group writes."""

from __future__ import annotations

from fastmcp import FastMCP
from pydantic import BaseModel, ConfigDict, Field, JsonValue

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


class _CountryGroupWritePreviewInput(BaseModel):
    """Forbid undeclared fields around the documented country-group payload."""

    model_config = ConfigDict(extra="forbid", frozen=True)


class CountryGroupPayload(BaseModel):
    """Writable `#v2countrygroups` fields. Official member ids stay a string."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    name: str | None = None
    icon: str | None = None
    memberCountryIds: str | None = None


class CountryGroupCreatePreviewInput(_CountryGroupWritePreviewInput):
    """Input for previewing creation of one Billy country group."""

    countryGroup: CountryGroupPayload


class CountryGroupUpdatePreviewInput(_CountryGroupWritePreviewInput):
    """Input for previewing an update to one Billy country group."""

    id: str = Field(min_length=1)
    countryGroup: CountryGroupPayload


def _country_group_payload(model: CountryGroupPayload) -> dict[str, JsonValue]:
    """Dump only set documented fields for the ticketed request body."""

    dumped = model.model_dump(exclude_none=True, exclude_unset=True)
    return {str(key): value for key, value in dumped.items()}


def register_country_group_write_tools(
    server: FastMCP,
    client: BillyHttpClient,
    write_protocol: WriteProtocolService,
) -> None:
    """Register exactly the four frozen ticketed country-group write tools."""

    del client

    def api_country_groups_create_preview(
        countryGroup: CountryGroupPayload,
    ) -> WritePreviewResult:
        """Preview creation of one Billy country group without sending a mutation."""

        input = CountryGroupCreatePreviewInput(countryGroup=countryGroup)
        return write_protocol.preview(
            _country_group_spec(
                execute_tool_name="api_country_groups_create_execute",
                method=WriteMethod.POST,
                payload=_country_group_payload(input.countryGroup),
                resource_id=None,
                summary="Create one Billy country group.",
                expected_effect_state={"action": "create", "resource": "countryGroup"},
            )
        )

    def api_country_groups_create_execute(
        confirmation_ticket: str = Field(min_length=1),
    ) -> WriteExecutionResult | ToolError:
        """Execute the exact country-group creation represented by a confirmation ticket."""

        return write_protocol.execute(
            WriteExecuteInput(confirmation_ticket=confirmation_ticket),
            execute_tool_name="api_country_groups_create_execute",
        )

    def api_country_groups_update_preview(
        countryGroup: CountryGroupPayload,
        id: str = Field(min_length=1),
    ) -> WritePreviewResult:
        """Preview an update to one Billy country group without sending a mutation."""

        input = CountryGroupUpdatePreviewInput(id=id, countryGroup=countryGroup)
        return write_protocol.preview(
            _country_group_spec(
                execute_tool_name="api_country_groups_update_execute",
                method=WriteMethod.PUT,
                payload=_country_group_payload(input.countryGroup),
                resource_id=input.id,
                summary="Update one Billy country group.",
                expected_effect_state={
                    "action": "update",
                    "resource": "countryGroup",
                    "id": input.id,
                },
            )
        )

    def api_country_groups_update_execute(
        confirmation_ticket: str = Field(min_length=1),
    ) -> WriteExecutionResult | ToolError:
        """Execute the exact country-group update represented by a confirmation ticket."""

        return write_protocol.execute(
            WriteExecuteInput(confirmation_ticket=confirmation_ticket),
            execute_tool_name="api_country_groups_update_execute",
        )

    server.tool(
        name="api_country_groups_create_preview",
        description="Preview creation of one Billy country group without making a mutation.",
    )(api_country_groups_create_preview)
    server.tool(
        name="api_country_groups_create_execute",
        description="Execute a previewed Billy country-group creation with its ticket.",
    )(api_country_groups_create_execute)
    server.tool(
        name="api_country_groups_update_preview",
        description="Preview an update to one Billy country group without making a mutation.",
    )(api_country_groups_update_preview)
    server.tool(
        name="api_country_groups_update_execute",
        description="Execute a previewed Billy country-group update with its ticket.",
    )(api_country_groups_update_execute)


def _country_group_spec(
    *,
    execute_tool_name: str,
    method: WriteMethod,
    payload: dict[str, JsonValue] | None,
    resource_id: str | None,
    summary: str,
    expected_effect_state: dict[str, JsonValue],
) -> WriteOperationSpec:
    """Build the server-known operation shape for one country-group write preview."""

    return WriteOperationSpec(
        execute_tool_name=execute_tool_name,
        method=method,
        collection_path="/countryGroups",
        singular_root="countryGroup",
        plural_root="countryGroups",
        additional_plural_roots=(),
        payload=payload,
        resource_id=resource_id,
        organization_id=None,
        summary=summary,
        expected_effect_state=expected_effect_state,
    )
