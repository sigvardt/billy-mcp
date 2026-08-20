"""Ticketed FastMCP tools for documented singular Billy state writes."""

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


class _StateWritePreviewInput(BaseModel):
    """Forbid undeclared fields around the documented state payload."""

    model_config = ConfigDict(extra="forbid", frozen=True)


class StatePayload(BaseModel):
    """Writable `#v2states` fields. Belongs-to values stay opaque strings."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    stateCode: str | None = None
    name: str | None = None
    country: str | None = None


class StateCreatePreviewInput(_StateWritePreviewInput):
    """Input for previewing creation of one Billy state."""

    state: StatePayload


class StateUpdatePreviewInput(_StateWritePreviewInput):
    """Input for previewing an update to one Billy state."""

    id: str = Field(min_length=1)
    state: StatePayload


def _state_payload(model: StatePayload) -> dict[str, JsonValue]:
    """Dump only set documented fields for the ticketed request body."""

    dumped = model.model_dump(exclude_none=True, exclude_unset=True)
    return {str(key): value for key, value in dumped.items()}


def register_state_write_tools(
    server: FastMCP,
    client: BillyHttpClient,
    write_protocol: WriteProtocolService,
) -> None:
    """Register exactly the four frozen ticketed state write tools."""

    del client

    def api_states_create_preview(state: StatePayload) -> WritePreviewResult:
        """Preview creation of one Billy state without sending a mutation."""

        input = StateCreatePreviewInput(state=state)
        return write_protocol.preview(
            _state_spec(
                execute_tool_name="api_states_create_execute",
                method=WriteMethod.POST,
                payload=_state_payload(input.state),
                resource_id=None,
                summary="Create one Billy state.",
                expected_effect_state={"action": "create", "resource": "state"},
            )
        )

    def api_states_create_execute(
        confirmation_ticket: str = Field(min_length=1),
    ) -> WriteExecutionResult | ToolError:
        """Execute the exact state creation represented by a confirmation ticket."""

        return write_protocol.execute(
            WriteExecuteInput(confirmation_ticket=confirmation_ticket),
            execute_tool_name="api_states_create_execute",
        )

    def api_states_update_preview(
        state: StatePayload,
        id: str = Field(min_length=1),
    ) -> WritePreviewResult:
        """Preview an update to one Billy state without sending a mutation."""

        input = StateUpdatePreviewInput(id=id, state=state)
        return write_protocol.preview(
            _state_spec(
                execute_tool_name="api_states_update_execute",
                method=WriteMethod.PUT,
                payload=_state_payload(input.state),
                resource_id=input.id,
                summary="Update one Billy state.",
                expected_effect_state={
                    "action": "update",
                    "resource": "state",
                    "id": input.id,
                },
            )
        )

    def api_states_update_execute(
        confirmation_ticket: str = Field(min_length=1),
    ) -> WriteExecutionResult | ToolError:
        """Execute the exact state update represented by a confirmation ticket."""

        return write_protocol.execute(
            WriteExecuteInput(confirmation_ticket=confirmation_ticket),
            execute_tool_name="api_states_update_execute",
        )

    server.tool(
        name="api_states_create_preview",
        description="Preview creation of one Billy state without making a mutation.",
    )(api_states_create_preview)
    server.tool(
        name="api_states_create_execute",
        description="Execute a previewed Billy state creation with its confirmation ticket.",
    )(api_states_create_execute)
    server.tool(
        name="api_states_update_preview",
        description="Preview an update to one Billy state without making a mutation.",
    )(api_states_update_preview)
    server.tool(
        name="api_states_update_execute",
        description="Execute a previewed Billy state update with its confirmation ticket.",
    )(api_states_update_execute)


def _state_spec(
    *,
    execute_tool_name: str,
    method: WriteMethod,
    payload: dict[str, JsonValue] | None,
    resource_id: str | None,
    summary: str,
    expected_effect_state: dict[str, JsonValue],
) -> WriteOperationSpec:
    """Build the server-known operation shape for one state write preview."""

    return WriteOperationSpec(
        execute_tool_name=execute_tool_name,
        method=method,
        collection_path="/states",
        singular_root="state",
        plural_root="states",
        additional_plural_roots=(),
        payload=payload,
        resource_id=resource_id,
        organization_id=None,
        summary=summary,
        expected_effect_state=expected_effect_state,
    )
