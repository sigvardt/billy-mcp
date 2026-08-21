"""Ticketed FastMCP tools for documented singular Billy city writes."""

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


class _CityWritePreviewInput(BaseModel):
    """Forbid undeclared fields around the documented city payload."""

    model_config = ConfigDict(extra="forbid", frozen=True)


class CityPayload(BaseModel):
    """Writable `#v2cities` fields. Belongs-to values stay opaque strings."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    name: str | None = None
    county: str | None = None
    state: str | None = None
    country: str | None = None


class CityCreatePreviewInput(_CityWritePreviewInput):
    """Input for previewing creation of one Billy city."""

    city: CityPayload


class CityUpdatePreviewInput(_CityWritePreviewInput):
    """Input for previewing an update to one Billy city."""

    id: str = Field(min_length=1)
    city: CityPayload


def _city_payload(model: CityPayload) -> dict[str, JsonValue]:
    """Dump only set documented fields for the ticketed request body."""

    dumped = model.model_dump(exclude_none=True, exclude_unset=True)
    return {str(key): value for key, value in dumped.items()}


def register_city_write_tools(
    server: FastMCP,
    client: BillyHttpClient,
    write_protocol: WriteProtocolService,
) -> None:
    """Register exactly the four frozen ticketed city write tools."""

    del client

    def api_cities_create_preview(city: CityPayload) -> WritePreviewResult:
        """Preview creation of one Billy city without sending a mutation."""

        input = CityCreatePreviewInput(city=city)
        return write_protocol.preview(
            _city_spec(
                execute_tool_name="api_cities_create_execute",
                method=WriteMethod.POST,
                payload=_city_payload(input.city),
                resource_id=None,
                summary="Create one Billy city.",
                expected_effect_state={"action": "create", "resource": "city"},
            )
        )

    def api_cities_create_execute(
        confirmation_ticket: str = Field(min_length=1),
    ) -> WriteExecutionResult | ToolError:
        """Execute the exact city creation represented by a confirmation ticket."""

        return write_protocol.execute(
            WriteExecuteInput(confirmation_ticket=confirmation_ticket),
            execute_tool_name="api_cities_create_execute",
        )

    def api_cities_update_preview(
        city: CityPayload,
        id: str = Field(min_length=1),
    ) -> WritePreviewResult:
        """Preview an update to one Billy city without sending a mutation."""

        input = CityUpdatePreviewInput(id=id, city=city)
        return write_protocol.preview(
            _city_spec(
                execute_tool_name="api_cities_update_execute",
                method=WriteMethod.PUT,
                payload=_city_payload(input.city),
                resource_id=input.id,
                summary="Update one Billy city.",
                expected_effect_state={
                    "action": "update",
                    "resource": "city",
                    "id": input.id,
                },
            )
        )

    def api_cities_update_execute(
        confirmation_ticket: str = Field(min_length=1),
    ) -> WriteExecutionResult | ToolError:
        """Execute the exact city update represented by a confirmation ticket."""

        return write_protocol.execute(
            WriteExecuteInput(confirmation_ticket=confirmation_ticket),
            execute_tool_name="api_cities_update_execute",
        )

    server.tool(
        name="api_cities_create_preview",
        description="Preview creation of one Billy city without making a mutation.",
    )(api_cities_create_preview)
    server.tool(
        name="api_cities_create_execute",
        description="Execute a previewed Billy city creation with its confirmation ticket.",
    )(api_cities_create_execute)
    server.tool(
        name="api_cities_update_preview",
        description="Preview an update to one Billy city without making a mutation.",
    )(api_cities_update_preview)
    server.tool(
        name="api_cities_update_execute",
        description="Execute a previewed Billy city update with its confirmation ticket.",
    )(api_cities_update_execute)


def _city_spec(
    *,
    execute_tool_name: str,
    method: WriteMethod,
    payload: dict[str, JsonValue] | None,
    resource_id: str | None,
    summary: str,
    expected_effect_state: dict[str, JsonValue],
) -> WriteOperationSpec:
    """Build the server-known operation shape for one city write preview."""

    return WriteOperationSpec(
        execute_tool_name=execute_tool_name,
        method=method,
        collection_path="/cities",
        singular_root="city",
        plural_root="cities",
        additional_plural_roots=(),
        payload=payload,
        resource_id=resource_id,
        organization_id=None,
        summary=summary,
        expected_effect_state=expected_effect_state,
    )
