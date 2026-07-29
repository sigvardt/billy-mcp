"""Ticketed FastMCP tools for documented singular Billy daybook writes."""

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


class _DaybookWritePreviewInput(BaseModel):
    """Base model that forbids undeclared fields around an opaque daybook payload."""

    model_config = ConfigDict(extra="forbid")


class DaybookCreatePreviewInput(_DaybookWritePreviewInput):
    """Input for previewing creation of one Billy daybook."""

    daybook: dict[str, JsonValue]


class DaybookUpdatePreviewInput(_DaybookWritePreviewInput):
    """Input for previewing an update to one Billy daybook."""

    id: str = Field(min_length=1)
    daybook: dict[str, JsonValue]


class DaybookDeletePreviewInput(_DaybookWritePreviewInput):
    """Input for previewing deletion of one Billy daybook."""

    id: str = Field(min_length=1)


def register_daybook_write_tools(
    server: FastMCP,
    client: BillyHttpClient,
    write_protocol: WriteProtocolService,
) -> None:
    """Register exactly the six frozen ticketed daybook write tools."""

    del client

    def api_daybooks_create_preview(daybook: dict[str, JsonValue]) -> WritePreviewResult:
        """Preview creation of one Billy daybook without sending a mutation."""

        input = DaybookCreatePreviewInput(daybook=daybook)
        return write_protocol.preview(
            _daybook_spec(
                execute_tool_name="api_daybooks_create_execute",
                method=WriteMethod.POST,
                payload=input.daybook,
                resource_id=None,
                summary="Create one Billy daybook.",
                expected_effect_state={"action": "create", "resource": "daybook"},
            )
        )

    def api_daybooks_create_execute(
        confirmation_ticket: str = Field(min_length=1),
    ) -> WriteExecutionResult | ToolError:
        """Execute the exact daybook creation represented by a confirmation ticket."""

        return write_protocol.execute(WriteExecuteInput(confirmation_ticket=confirmation_ticket))

    def api_daybooks_update_preview(
        daybook: dict[str, JsonValue],
        id: str = Field(min_length=1),
    ) -> WritePreviewResult:
        """Preview an update to one Billy daybook without sending a mutation."""

        input = DaybookUpdatePreviewInput(id=id, daybook=daybook)
        return write_protocol.preview(
            _daybook_spec(
                execute_tool_name="api_daybooks_update_execute",
                method=WriteMethod.PUT,
                payload=input.daybook,
                resource_id=input.id,
                summary="Update one Billy daybook.",
                expected_effect_state={
                    "action": "update",
                    "resource": "daybook",
                    "id": input.id,
                },
            )
        )

    def api_daybooks_update_execute(
        confirmation_ticket: str = Field(min_length=1),
    ) -> WriteExecutionResult | ToolError:
        """Execute the exact daybook update represented by a confirmation ticket."""

        return write_protocol.execute(WriteExecuteInput(confirmation_ticket=confirmation_ticket))

    def api_daybooks_delete_preview(id: str = Field(min_length=1)) -> WritePreviewResult:
        """Preview deletion of one Billy daybook without sending a mutation."""

        input = DaybookDeletePreviewInput(id=id)
        return write_protocol.preview(
            _daybook_spec(
                execute_tool_name="api_daybooks_delete_execute",
                method=WriteMethod.DELETE,
                payload=None,
                resource_id=input.id,
                summary="Delete one Billy daybook.",
                expected_effect_state={
                    "action": "delete",
                    "resource": "daybook",
                    "id": input.id,
                },
            )
        )

    def api_daybooks_delete_execute(
        confirmation_ticket: str = Field(min_length=1),
    ) -> WriteExecutionResult | ToolError:
        """Execute the exact daybook deletion represented by a confirmation ticket."""

        return write_protocol.execute(WriteExecuteInput(confirmation_ticket=confirmation_ticket))

    server.tool(
        name="api_daybooks_create_preview",
        description="Preview creation of one Billy daybook without making a mutation.",
    )(api_daybooks_create_preview)
    server.tool(
        name="api_daybooks_create_execute",
        description="Execute a previewed Billy daybook creation with its confirmation ticket.",
    )(api_daybooks_create_execute)
    server.tool(
        name="api_daybooks_update_preview",
        description="Preview an update to one Billy daybook without making a mutation.",
    )(api_daybooks_update_preview)
    server.tool(
        name="api_daybooks_update_execute",
        description="Execute a previewed Billy daybook update with its confirmation ticket.",
    )(api_daybooks_update_execute)
    server.tool(
        name="api_daybooks_delete_preview",
        description="Preview deletion of one Billy daybook without making a mutation.",
    )(api_daybooks_delete_preview)
    server.tool(
        name="api_daybooks_delete_execute",
        description="Execute a previewed Billy daybook deletion with its confirmation ticket.",
    )(api_daybooks_delete_execute)


def _daybook_spec(
    *,
    execute_tool_name: str,
    method: WriteMethod,
    payload: dict[str, JsonValue] | None,
    resource_id: str | None,
    summary: str,
    expected_effect_state: dict[str, JsonValue],
) -> WriteOperationSpec:
    """Build the server-known operation shape for one daybook CUD preview."""

    return WriteOperationSpec(
        execute_tool_name=execute_tool_name,
        method=method,
        collection_path="/daybooks",
        singular_root="daybook",
        plural_root="daybooks",
        additional_plural_roots=(),
        payload=payload,
        resource_id=resource_id,
        organization_id=None,
        summary=summary,
        expected_effect_state=expected_effect_state,
    )
