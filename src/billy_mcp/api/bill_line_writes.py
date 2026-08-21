"""Ticketed FastMCP tools for documented singular Billy bill-line writes."""

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


class _BillLineWritePreviewInput(BaseModel):
    """Base model that forbids undeclared fields around an opaque line payload."""

    model_config = ConfigDict(extra="forbid")


class BillLineCreatePreviewInput(_BillLineWritePreviewInput):
    """Input for previewing creation of one Billy bill line."""

    billLine: dict[str, JsonValue]


class BillLineUpdatePreviewInput(_BillLineWritePreviewInput):
    """Input for previewing an update to one Billy bill line."""

    id: str = Field(min_length=1)
    billLine: dict[str, JsonValue]

    @model_validator(mode="after")
    def payload_id_matches_route_id(self) -> BillLineUpdatePreviewInput:
        """Reject a payload identity that disagrees with the route identity."""

        if "id" in self.billLine and self.billLine["id"] != self.id:
            raise ValueError("billLine.id must match the update id")
        return self


class BillLineDeletePreviewInput(_BillLineWritePreviewInput):
    """Input for previewing deletion of one Billy bill line."""

    id: str = Field(min_length=1)


def register_bill_line_write_tools(
    server: FastMCP,
    client: BillyHttpClient,
    write_protocol: WriteProtocolService,
) -> None:
    """Register exactly the six frozen ticketed bill-line write tools."""

    del client

    def api_bill_lines_create_preview(
        billLine: dict[str, JsonValue],
    ) -> WritePreviewResult:
        """Preview creation of one Billy bill line without a mutation."""

        input = BillLineCreatePreviewInput(billLine=billLine)
        return write_protocol.preview(
            _bill_line_spec(
                execute_tool_name="api_bill_lines_create_execute",
                method=WriteMethod.POST,
                payload=input.billLine,
                resource_id=None,
                summary="Create one Billy bill line.",
                expected_effect_state={"action": "create", "resource": "billLine"},
            )
        )

    def api_bill_lines_create_execute(
        confirmation_ticket: str = Field(min_length=1),
    ) -> WriteExecutionResult | ToolError:
        """Execute the exact bill-line creation in a confirmation ticket."""

        return write_protocol.execute(
            WriteExecuteInput(confirmation_ticket=confirmation_ticket),
            execute_tool_name="api_bill_lines_create_execute",
        )

    def api_bill_lines_update_preview(
        billLine: dict[str, JsonValue],
        id: str = Field(min_length=1),
    ) -> WritePreviewResult:
        """Preview an update to one Billy bill line without a mutation."""

        input = BillLineUpdatePreviewInput(id=id, billLine=billLine)
        return write_protocol.preview(
            _bill_line_spec(
                execute_tool_name="api_bill_lines_update_execute",
                method=WriteMethod.PUT,
                payload=input.billLine,
                resource_id=input.id,
                summary="Update one Billy bill line.",
                expected_effect_state={
                    "action": "update",
                    "resource": "billLine",
                    "id": input.id,
                },
            )
        )

    def api_bill_lines_update_execute(
        confirmation_ticket: str = Field(min_length=1),
    ) -> WriteExecutionResult | ToolError:
        """Execute the exact bill-line update in a confirmation ticket."""

        return write_protocol.execute(
            WriteExecuteInput(confirmation_ticket=confirmation_ticket),
            execute_tool_name="api_bill_lines_update_execute",
        )

    def api_bill_lines_delete_preview(
        id: str = Field(min_length=1),
    ) -> WritePreviewResult:
        """Preview deletion of one Billy bill line without a mutation."""

        input = BillLineDeletePreviewInput(id=id)
        return write_protocol.preview(
            _bill_line_spec(
                execute_tool_name="api_bill_lines_delete_execute",
                method=WriteMethod.DELETE,
                payload=None,
                resource_id=input.id,
                summary="Delete one Billy bill line.",
                expected_effect_state={
                    "action": "delete",
                    "resource": "billLine",
                    "id": input.id,
                },
            )
        )

    def api_bill_lines_delete_execute(
        confirmation_ticket: str = Field(min_length=1),
    ) -> WriteExecutionResult | ToolError:
        """Execute the exact bill-line deletion in a confirmation ticket."""

        return write_protocol.execute(
            WriteExecuteInput(confirmation_ticket=confirmation_ticket),
            execute_tool_name="api_bill_lines_delete_execute",
        )

    server.tool(
        name="api_bill_lines_create_preview",
        description="Preview creation of one Billy bill line without a mutation.",
    )(api_bill_lines_create_preview)
    server.tool(
        name="api_bill_lines_create_execute",
        description="Execute a previewed Billy bill-line creation with its ticket.",
    )(api_bill_lines_create_execute)
    server.tool(
        name="api_bill_lines_update_preview",
        description="Preview an update to one Billy bill line without a mutation.",
    )(api_bill_lines_update_preview)
    server.tool(
        name="api_bill_lines_update_execute",
        description="Execute a previewed Billy bill-line update with its ticket.",
    )(api_bill_lines_update_execute)
    server.tool(
        name="api_bill_lines_delete_preview",
        description="Preview deletion of one Billy bill line without a mutation.",
    )(api_bill_lines_delete_preview)
    server.tool(
        name="api_bill_lines_delete_execute",
        description="Execute a previewed Billy bill-line deletion with its ticket.",
    )(api_bill_lines_delete_execute)


def _bill_line_spec(
    *,
    execute_tool_name: str,
    method: WriteMethod,
    payload: dict[str, JsonValue] | None,
    resource_id: str | None,
    summary: str,
    expected_effect_state: dict[str, JsonValue],
) -> WriteOperationSpec:
    """Build the server-known operation shape for one bill-line CUD preview."""

    return WriteOperationSpec(
        execute_tool_name=execute_tool_name,
        method=method,
        collection_path="/billLines",
        singular_root="billLine",
        plural_root="billLines",
        additional_plural_roots=("bills",),
        payload=payload,
        resource_id=resource_id,
        organization_id=None,
        summary=summary,
        expected_effect_state=expected_effect_state,
    )
