"""Ticketed FastMCP tools for documented singular transaction delete."""

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


class TransactionDeletePreviewInput(BaseModel):
    """Input for previewing deletion of one Billy transaction."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    id: str = Field(min_length=1)


def register_transaction_write_tools(
    server: FastMCP,
    client: BillyHttpClient,
    write_protocol: WriteProtocolService,
) -> None:
    """Register the two frozen ticketed transaction delete tools."""

    del client

    def api_transactions_delete_preview(id: str = Field(min_length=1)) -> WritePreviewResult:
        """Preview deletion of one transaction without sending a mutation."""

        input = TransactionDeletePreviewInput(id=id)
        return write_protocol.preview(
            _transaction_spec(
                execute_tool_name="api_transactions_delete_execute",
                resource_id=input.id,
            )
        )

    def api_transactions_delete_execute(
        confirmation_ticket: str = Field(min_length=1),
    ) -> WriteExecutionResult | ToolError:
        """Execute the exact transaction deletion represented by a confirmation ticket."""

        return write_protocol.execute(
            WriteExecuteInput(confirmation_ticket=confirmation_ticket),
            execute_tool_name="api_transactions_delete_execute",
        )

    server.tool(
        name="api_transactions_delete_preview",
        description="Preview deletion of one Billy transaction without a mutation.",
    )(api_transactions_delete_preview)
    server.tool(
        name="api_transactions_delete_execute",
        description="Execute a previewed Billy transaction deletion with its ticket.",
    )(api_transactions_delete_execute)


def _transaction_spec(*, execute_tool_name: str, resource_id: str) -> WriteOperationSpec:
    """Build the server-known operation shape for one transaction delete preview."""

    expected_effect_state: dict[str, JsonValue] = {
        "action": "delete",
        "resource": "transaction",
        "id": resource_id,
    }
    return WriteOperationSpec(
        execute_tool_name=execute_tool_name,
        method=WriteMethod.DELETE,
        collection_path="/transactions",
        singular_root="transaction",
        plural_root="transactions",
        additional_plural_roots=(),
        payload=None,
        resource_id=resource_id,
        organization_id=None,
        summary="Delete one Billy transaction.",
        expected_effect_state=expected_effect_state,
    )
