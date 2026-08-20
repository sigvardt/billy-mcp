"""Ticketed FastMCP tools for documented singular Billy country writes."""

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


class _CountryWritePreviewInput(BaseModel):
    """Forbid undeclared fields around the documented country payload."""

    model_config = ConfigDict(extra="forbid", frozen=True)


class CountryPayload(BaseModel):
    """Writable `#v2countries` fields. Belongs-to locale stays an opaque string id."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    name: str | None = None
    hasStates: bool | None = None
    hasFiniteStates: bool | None = None
    hasFiniteZipcodes: bool | None = None
    icon: str | None = None
    locale: str | None = None


class CountryCreatePreviewInput(_CountryWritePreviewInput):
    """Input for previewing creation of one Billy country."""

    country: CountryPayload


class CountryUpdatePreviewInput(_CountryWritePreviewInput):
    """Input for previewing an update to one Billy country."""

    id: str = Field(min_length=1)
    country: CountryPayload


def _country_payload(model: CountryPayload) -> dict[str, JsonValue]:
    """Dump only set documented fields for the ticketed request body."""

    dumped = model.model_dump(exclude_none=True, exclude_unset=True)
    return {str(key): value for key, value in dumped.items()}


def register_country_write_tools(
    server: FastMCP,
    client: BillyHttpClient,
    write_protocol: WriteProtocolService,
) -> None:
    """Register exactly the four frozen ticketed country write tools."""

    del client

    def api_countries_create_preview(country: CountryPayload) -> WritePreviewResult:
        """Preview creation of one Billy country without sending a mutation."""

        input = CountryCreatePreviewInput(country=country)
        return write_protocol.preview(
            _country_spec(
                execute_tool_name="api_countries_create_execute",
                method=WriteMethod.POST,
                payload=_country_payload(input.country),
                resource_id=None,
                summary="Create one Billy country.",
                expected_effect_state={"action": "create", "resource": "country"},
            )
        )

    def api_countries_create_execute(
        confirmation_ticket: str = Field(min_length=1),
    ) -> WriteExecutionResult | ToolError:
        """Execute the exact country creation represented by a confirmation ticket."""

        return write_protocol.execute(
            WriteExecuteInput(confirmation_ticket=confirmation_ticket),
            execute_tool_name="api_countries_create_execute",
        )

    def api_countries_update_preview(
        country: CountryPayload,
        id: str = Field(min_length=1),
    ) -> WritePreviewResult:
        """Preview an update to one Billy country without sending a mutation."""

        input = CountryUpdatePreviewInput(id=id, country=country)
        return write_protocol.preview(
            _country_spec(
                execute_tool_name="api_countries_update_execute",
                method=WriteMethod.PUT,
                payload=_country_payload(input.country),
                resource_id=input.id,
                summary="Update one Billy country.",
                expected_effect_state={
                    "action": "update",
                    "resource": "country",
                    "id": input.id,
                },
            )
        )

    def api_countries_update_execute(
        confirmation_ticket: str = Field(min_length=1),
    ) -> WriteExecutionResult | ToolError:
        """Execute the exact country update represented by a confirmation ticket."""

        return write_protocol.execute(
            WriteExecuteInput(confirmation_ticket=confirmation_ticket),
            execute_tool_name="api_countries_update_execute",
        )

    server.tool(
        name="api_countries_create_preview",
        description="Preview creation of one Billy country without making a mutation.",
    )(api_countries_create_preview)
    server.tool(
        name="api_countries_create_execute",
        description="Execute a previewed Billy country creation with its ticket.",
    )(api_countries_create_execute)
    server.tool(
        name="api_countries_update_preview",
        description="Preview an update to one Billy country without making a mutation.",
    )(api_countries_update_preview)
    server.tool(
        name="api_countries_update_execute",
        description="Execute a previewed Billy country update with its ticket.",
    )(api_countries_update_execute)


def _country_spec(
    *,
    execute_tool_name: str,
    method: WriteMethod,
    payload: dict[str, JsonValue] | None,
    resource_id: str | None,
    summary: str,
    expected_effect_state: dict[str, JsonValue],
) -> WriteOperationSpec:
    """Build the server-known operation shape for one country write preview."""

    return WriteOperationSpec(
        execute_tool_name=execute_tool_name,
        method=method,
        collection_path="/countries",
        singular_root="country",
        plural_root="countries",
        additional_plural_roots=(),
        payload=payload,
        resource_id=resource_id,
        organization_id=None,
        summary=summary,
        expected_effect_state=expected_effect_state,
    )
