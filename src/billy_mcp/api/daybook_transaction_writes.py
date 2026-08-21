"""Ticketed FastMCP tools for documented singular Billy daybook-transaction writes."""

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


class _DaybookTransactionWritePreviewInput(BaseModel):
    """Base model that forbids undeclared fields around an opaque transaction payload."""

    model_config = ConfigDict(extra="forbid")


class DaybookTransactionCreatePreviewInput(_DaybookTransactionWritePreviewInput):
    """Input for previewing creation of one Billy daybook transaction."""

    daybookTransaction: dict[str, JsonValue]


class DaybookTransactionUpdatePreviewInput(_DaybookTransactionWritePreviewInput):
    """Input for previewing an update to one Billy daybook transaction."""

    id: str = Field(min_length=1)
    daybookTransaction: dict[str, JsonValue]


class DaybookTransactionDeletePreviewInput(_DaybookTransactionWritePreviewInput):
    """Input for previewing deletion of one Billy daybook transaction."""

    id: str = Field(min_length=1)


def register_daybook_transaction_write_tools(
    server: FastMCP,
    client: BillyHttpClient,
    write_protocol: WriteProtocolService,
) -> None:
    """Register exactly the six frozen ticketed daybook-transaction write tools."""

    del client

    def api_daybook_transactions_create_preview(
        daybookTransaction: dict[str, JsonValue],
    ) -> WritePreviewResult:
        """Preview creation of one Billy daybook transaction without a mutation."""

        input = DaybookTransactionCreatePreviewInput(daybookTransaction=daybookTransaction)
        return write_protocol.preview(
            _daybook_transaction_spec(
                execute_tool_name="api_daybook_transactions_create_execute",
                method=WriteMethod.POST,
                payload=input.daybookTransaction,
                resource_id=None,
                summary="Create one Billy daybook transaction.",
                expected_effect_state={
                    "action": "create",
                    "resource": "daybookTransaction",
                },
            )
        )

    def api_daybook_transactions_create_execute(
        confirmation_ticket: str = Field(min_length=1),
    ) -> WriteExecutionResult | ToolError:
        """Execute the exact daybook-transaction creation in a confirmation ticket."""

        return write_protocol.execute(
            WriteExecuteInput(confirmation_ticket=confirmation_ticket),
            execute_tool_name="api_daybook_transactions_create_execute",
        )

    def api_daybook_transactions_update_preview(
        daybookTransaction: dict[str, JsonValue],
        id: str = Field(min_length=1),
    ) -> WritePreviewResult:
        """Preview an update to one Billy daybook transaction without a mutation."""

        input = DaybookTransactionUpdatePreviewInput(
            id=id,
            daybookTransaction=daybookTransaction,
        )
        return write_protocol.preview(
            _daybook_transaction_spec(
                execute_tool_name="api_daybook_transactions_update_execute",
                method=WriteMethod.PUT,
                payload=input.daybookTransaction,
                resource_id=input.id,
                summary="Update one Billy daybook transaction.",
                expected_effect_state={
                    "action": "update",
                    "resource": "daybookTransaction",
                    "id": input.id,
                },
            )
        )

    def api_daybook_transactions_update_execute(
        confirmation_ticket: str = Field(min_length=1),
    ) -> WriteExecutionResult | ToolError:
        """Execute the exact daybook-transaction update in a confirmation ticket."""

        return write_protocol.execute(
            WriteExecuteInput(confirmation_ticket=confirmation_ticket),
            execute_tool_name="api_daybook_transactions_update_execute",
        )

    def api_daybook_transactions_delete_preview(
        id: str = Field(min_length=1),
    ) -> WritePreviewResult:
        """Preview deletion of one Billy daybook transaction without a mutation."""

        input = DaybookTransactionDeletePreviewInput(id=id)
        return write_protocol.preview(
            _daybook_transaction_spec(
                execute_tool_name="api_daybook_transactions_delete_execute",
                method=WriteMethod.DELETE,
                payload=None,
                resource_id=input.id,
                summary="Delete one Billy daybook transaction.",
                expected_effect_state={
                    "action": "delete",
                    "resource": "daybookTransaction",
                    "id": input.id,
                },
            )
        )

    def api_daybook_transactions_delete_execute(
        confirmation_ticket: str = Field(min_length=1),
    ) -> WriteExecutionResult | ToolError:
        """Execute the exact daybook-transaction deletion in a confirmation ticket."""

        return write_protocol.execute(
            WriteExecuteInput(confirmation_ticket=confirmation_ticket),
            execute_tool_name="api_daybook_transactions_delete_execute",
        )

    server.tool(
        name="api_daybook_transactions_create_preview",
        description="Preview creation of one Billy daybook transaction without a mutation.",
    )(api_daybook_transactions_create_preview)
    server.tool(
        name="api_daybook_transactions_create_execute",
        description="Execute a previewed Billy daybook transaction creation with its ticket.",
    )(api_daybook_transactions_create_execute)
    server.tool(
        name="api_daybook_transactions_update_preview",
        description="Preview an update to one Billy daybook transaction without a mutation.",
    )(api_daybook_transactions_update_preview)
    server.tool(
        name="api_daybook_transactions_update_execute",
        description="Execute a previewed Billy daybook transaction update with its ticket.",
    )(api_daybook_transactions_update_execute)
    server.tool(
        name="api_daybook_transactions_delete_preview",
        description="Preview deletion of one Billy daybook transaction without a mutation.",
    )(api_daybook_transactions_delete_preview)
    server.tool(
        name="api_daybook_transactions_delete_execute",
        description="Execute a previewed Billy daybook transaction deletion with its ticket.",
    )(api_daybook_transactions_delete_execute)


def _daybook_transaction_spec(
    *,
    execute_tool_name: str,
    method: WriteMethod,
    payload: dict[str, JsonValue] | None,
    resource_id: str | None,
    summary: str,
    expected_effect_state: dict[str, JsonValue],
) -> WriteOperationSpec:
    """Build the server-known operation shape for one daybook-transaction CUD preview."""

    return WriteOperationSpec(
        execute_tool_name=execute_tool_name,
        method=method,
        collection_path="/daybookTransactions",
        singular_root="daybookTransaction",
        plural_root="daybookTransactions",
        additional_plural_roots=(),
        payload=payload,
        resource_id=resource_id,
        organization_id=None,
        summary=summary,
        expected_effect_state=expected_effect_state,
    )
