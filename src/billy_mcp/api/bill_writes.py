"""Ticketed FastMCP tools for documented singular Billy bill writes."""

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


class _BillWritePreviewInput(BaseModel):
    """Base model that forbids undeclared fields around an opaque bill payload."""

    model_config = ConfigDict(extra="forbid")


class BillCreatePreviewInput(_BillWritePreviewInput):
    """Input for previewing creation of one Billy bill."""

    bill: dict[str, JsonValue]


class BillUpdatePreviewInput(_BillWritePreviewInput):
    """Input for previewing an update to one Billy bill."""

    id: str = Field(min_length=1)
    bill: dict[str, JsonValue]

    @model_validator(mode="after")
    def bill_id_matches_route_id(self) -> BillUpdatePreviewInput:
        """Keep an optional bill-body identifier aligned with the target route."""

        if "id" in self.bill and self.bill["id"] != self.id:
            raise ValueError("bill.id must match id")
        return self


class BillDeletePreviewInput(_BillWritePreviewInput):
    """Input for previewing deletion of one Billy bill."""

    id: str = Field(min_length=1)


def register_bill_write_tools(
    server: FastMCP,
    client: BillyHttpClient,
    write_protocol: WriteProtocolService,
) -> None:
    """Register exactly the six frozen ticketed parent-bill write tools."""

    del client

    def api_bills_create_preview(bill: dict[str, JsonValue]) -> WritePreviewResult:
        """Preview creation of one Billy bill without a mutation."""

        input = BillCreatePreviewInput(bill=bill)
        return write_protocol.preview(
            _bill_spec(
                execute_tool_name="api_bills_create_execute",
                method=WriteMethod.POST,
                payload=input.bill,
                resource_id=None,
                summary="Create one Billy bill.",
                expected_effect_state={"action": "create", "resource": "bill"},
            )
        )

    def api_bills_create_execute(
        confirmation_ticket: str = Field(min_length=1),
    ) -> WriteExecutionResult | ToolError:
        """Execute the exact bill creation in a confirmation ticket."""

        return write_protocol.execute(
            WriteExecuteInput(confirmation_ticket=confirmation_ticket),
            execute_tool_name="api_bills_create_execute",
        )

    def api_bills_update_preview(
        bill: dict[str, JsonValue],
        id: str = Field(min_length=1),
    ) -> WritePreviewResult:
        """Preview an update to one Billy bill without a mutation."""

        input = BillUpdatePreviewInput(id=id, bill=bill)
        return write_protocol.preview(
            _bill_spec(
                execute_tool_name="api_bills_update_execute",
                method=WriteMethod.PUT,
                payload=input.bill,
                resource_id=input.id,
                summary="Update one Billy bill.",
                expected_effect_state={
                    "action": "update",
                    "resource": "bill",
                    "id": input.id,
                },
            )
        )

    def api_bills_update_execute(
        confirmation_ticket: str = Field(min_length=1),
    ) -> WriteExecutionResult | ToolError:
        """Execute the exact bill update in a confirmation ticket."""

        return write_protocol.execute(
            WriteExecuteInput(confirmation_ticket=confirmation_ticket),
            execute_tool_name="api_bills_update_execute",
        )

    def api_bills_delete_preview(id: str = Field(min_length=1)) -> WritePreviewResult:
        """Preview deletion of one Billy bill without a mutation."""

        input = BillDeletePreviewInput(id=id)
        return write_protocol.preview(
            _bill_spec(
                execute_tool_name="api_bills_delete_execute",
                method=WriteMethod.DELETE,
                payload=None,
                resource_id=input.id,
                summary="Delete one Billy bill.",
                expected_effect_state={
                    "action": "delete",
                    "resource": "bill",
                    "id": input.id,
                },
            )
        )

    def api_bills_delete_execute(
        confirmation_ticket: str = Field(min_length=1),
    ) -> WriteExecutionResult | ToolError:
        """Execute the exact bill deletion in a confirmation ticket."""

        return write_protocol.execute(
            WriteExecuteInput(confirmation_ticket=confirmation_ticket),
            execute_tool_name="api_bills_delete_execute",
        )

    server.tool(
        name="api_bills_create_preview",
        description="Preview creation of one Billy bill without a mutation.",
    )(api_bills_create_preview)
    server.tool(
        name="api_bills_create_execute",
        description="Execute a previewed Billy bill creation with its ticket.",
    )(api_bills_create_execute)
    server.tool(
        name="api_bills_update_preview",
        description="Preview an update to one Billy bill without a mutation.",
    )(api_bills_update_preview)
    server.tool(
        name="api_bills_update_execute",
        description="Execute a previewed Billy bill update with its ticket.",
    )(api_bills_update_execute)
    server.tool(
        name="api_bills_delete_preview",
        description="Preview deletion of one Billy bill without a mutation.",
    )(api_bills_delete_preview)
    server.tool(
        name="api_bills_delete_execute",
        description="Execute a previewed Billy bill deletion with its ticket.",
    )(api_bills_delete_execute)


def _bill_spec(
    *,
    execute_tool_name: str,
    method: WriteMethod,
    payload: dict[str, JsonValue] | None,
    resource_id: str | None,
    summary: str,
    expected_effect_state: dict[str, JsonValue],
) -> WriteOperationSpec:
    """Build the server-known operation shape for one parent-bill CUD preview."""

    return WriteOperationSpec(
        execute_tool_name=execute_tool_name,
        method=method,
        collection_path="/bills",
        singular_root="bill",
        plural_root="bills",
        additional_plural_roots=(),
        payload=payload,
        resource_id=resource_id,
        organization_id=None,
        summary=summary,
        expected_effect_state=expected_effect_state,
    )
