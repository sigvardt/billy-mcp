"""Ticketed FastMCP tools for documented singular Billy zipcode writes."""

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


class _ZipcodeWritePreviewInput(BaseModel):
    """Forbid undeclared fields around the documented zipcode payload."""

    model_config = ConfigDict(extra="forbid", frozen=True)


class ZipcodePayload(BaseModel):
    """Writable `#v2zipcodes` fields. Belongs-to values stay opaque strings."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    zipcode: str | None = None
    city: str | None = None
    state: str | None = None
    country: str | None = None
    latitude: float | None = None
    longitude: float | None = None


class ZipcodeCreatePreviewInput(_ZipcodeWritePreviewInput):
    """Input for previewing creation of one Billy zipcode."""

    zipcode: ZipcodePayload


class ZipcodeUpdatePreviewInput(_ZipcodeWritePreviewInput):
    """Input for previewing an update to one Billy zipcode."""

    id: str = Field(min_length=1)
    zipcode: ZipcodePayload


def _zipcode_payload(model: ZipcodePayload) -> dict[str, JsonValue]:
    """Dump only set documented fields for the ticketed request body."""

    dumped = model.model_dump(exclude_none=True, exclude_unset=True)
    return {str(key): value for key, value in dumped.items()}


def register_zipcode_write_tools(
    server: FastMCP,
    client: BillyHttpClient,
    write_protocol: WriteProtocolService,
) -> None:
    """Register exactly the four frozen ticketed zipcode write tools."""

    del client

    def api_zipcodes_create_preview(zipcode: ZipcodePayload) -> WritePreviewResult:
        """Preview creation of one Billy zipcode without sending a mutation."""

        input = ZipcodeCreatePreviewInput(zipcode=zipcode)
        return write_protocol.preview(
            _zipcode_spec(
                execute_tool_name="api_zipcodes_create_execute",
                method=WriteMethod.POST,
                payload=_zipcode_payload(input.zipcode),
                resource_id=None,
                summary="Create one Billy zipcode.",
                expected_effect_state={"action": "create", "resource": "zipcode"},
            )
        )

    def api_zipcodes_create_execute(
        confirmation_ticket: str = Field(min_length=1),
    ) -> WriteExecutionResult | ToolError:
        """Execute the exact zipcode creation represented by a confirmation ticket."""

        return write_protocol.execute(
            WriteExecuteInput(confirmation_ticket=confirmation_ticket),
            execute_tool_name="api_zipcodes_create_execute",
        )

    def api_zipcodes_update_preview(
        zipcode: ZipcodePayload,
        id: str = Field(min_length=1),
    ) -> WritePreviewResult:
        """Preview an update to one Billy zipcode without sending a mutation."""

        input = ZipcodeUpdatePreviewInput(id=id, zipcode=zipcode)
        return write_protocol.preview(
            _zipcode_spec(
                execute_tool_name="api_zipcodes_update_execute",
                method=WriteMethod.PUT,
                payload=_zipcode_payload(input.zipcode),
                resource_id=input.id,
                summary="Update one Billy zipcode.",
                expected_effect_state={
                    "action": "update",
                    "resource": "zipcode",
                    "id": input.id,
                },
            )
        )

    def api_zipcodes_update_execute(
        confirmation_ticket: str = Field(min_length=1),
    ) -> WriteExecutionResult | ToolError:
        """Execute the exact zipcode update represented by a confirmation ticket."""

        return write_protocol.execute(
            WriteExecuteInput(confirmation_ticket=confirmation_ticket),
            execute_tool_name="api_zipcodes_update_execute",
        )

    server.tool(
        name="api_zipcodes_create_preview",
        description="Preview creation of one Billy zipcode without making a mutation.",
    )(api_zipcodes_create_preview)
    server.tool(
        name="api_zipcodes_create_execute",
        description="Execute a previewed Billy zipcode creation with its confirmation ticket.",
    )(api_zipcodes_create_execute)
    server.tool(
        name="api_zipcodes_update_preview",
        description="Preview an update to one Billy zipcode without making a mutation.",
    )(api_zipcodes_update_preview)
    server.tool(
        name="api_zipcodes_update_execute",
        description="Execute a previewed Billy zipcode update with its confirmation ticket.",
    )(api_zipcodes_update_execute)


def _zipcode_spec(
    *,
    execute_tool_name: str,
    method: WriteMethod,
    payload: dict[str, JsonValue] | None,
    resource_id: str | None,
    summary: str,
    expected_effect_state: dict[str, JsonValue],
) -> WriteOperationSpec:
    """Build the server-known operation shape for one zipcode write preview."""

    return WriteOperationSpec(
        execute_tool_name=execute_tool_name,
        method=method,
        collection_path="/zipcodes",
        singular_root="zipcode",
        plural_root="zipcodes",
        additional_plural_roots=(),
        payload=payload,
        resource_id=resource_id,
        organization_id=None,
        summary=summary,
        expected_effect_state=expected_effect_state,
    )
