"""Ticketed FastMCP tools for documented singular Billy daybook-balance-account writes."""

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


class _DaybookBalanceAccountWritePreviewInput(BaseModel):
    """Base model that forbids undeclared fields around an opaque account payload."""

    model_config = ConfigDict(extra="forbid")


class DaybookBalanceAccountCreatePreviewInput(_DaybookBalanceAccountWritePreviewInput):
    """Input for previewing creation of one Billy daybook balance account."""

    daybookBalanceAccount: dict[str, JsonValue]


class DaybookBalanceAccountUpdatePreviewInput(_DaybookBalanceAccountWritePreviewInput):
    """Input for previewing an update to one Billy daybook balance account."""

    id: str = Field(min_length=1)
    daybookBalanceAccount: dict[str, JsonValue]


class DaybookBalanceAccountDeletePreviewInput(_DaybookBalanceAccountWritePreviewInput):
    """Input for previewing deletion of one Billy daybook balance account."""

    id: str = Field(min_length=1)


def register_daybook_balance_account_write_tools(
    server: FastMCP,
    client: BillyHttpClient,
    write_protocol: WriteProtocolService,
) -> None:
    """Register exactly the six frozen ticketed daybook-balance-account write tools."""

    del client

    def api_daybook_balance_accounts_create_preview(
        daybookBalanceAccount: dict[str, JsonValue],
    ) -> WritePreviewResult:
        """Preview creation of one Billy daybook balance account without a mutation."""

        input = DaybookBalanceAccountCreatePreviewInput(
            daybookBalanceAccount=daybookBalanceAccount,
        )
        return write_protocol.preview(
            _daybook_balance_account_spec(
                execute_tool_name="api_daybook_balance_accounts_create_execute",
                method=WriteMethod.POST,
                payload=input.daybookBalanceAccount,
                resource_id=None,
                summary="Create one Billy daybook balance account.",
                expected_effect_state={
                    "action": "create",
                    "resource": "daybookBalanceAccount",
                },
            )
        )

    def api_daybook_balance_accounts_create_execute(
        confirmation_ticket: str = Field(min_length=1),
    ) -> WriteExecutionResult | ToolError:
        """Execute the exact daybook-balance-account creation in a confirmation ticket."""

        return write_protocol.execute(
            WriteExecuteInput(confirmation_ticket=confirmation_ticket),
            execute_tool_name="api_daybook_balance_accounts_create_execute",
        )

    def api_daybook_balance_accounts_update_preview(
        daybookBalanceAccount: dict[str, JsonValue],
        id: str = Field(min_length=1),
    ) -> WritePreviewResult:
        """Preview an update to one Billy daybook balance account without a mutation."""

        input = DaybookBalanceAccountUpdatePreviewInput(
            id=id,
            daybookBalanceAccount=daybookBalanceAccount,
        )
        return write_protocol.preview(
            _daybook_balance_account_spec(
                execute_tool_name="api_daybook_balance_accounts_update_execute",
                method=WriteMethod.PUT,
                payload=input.daybookBalanceAccount,
                resource_id=input.id,
                summary="Update one Billy daybook balance account.",
                expected_effect_state={
                    "action": "update",
                    "resource": "daybookBalanceAccount",
                    "id": input.id,
                },
            )
        )

    def api_daybook_balance_accounts_update_execute(
        confirmation_ticket: str = Field(min_length=1),
    ) -> WriteExecutionResult | ToolError:
        """Execute the exact daybook-balance-account update in a confirmation ticket."""

        return write_protocol.execute(
            WriteExecuteInput(confirmation_ticket=confirmation_ticket),
            execute_tool_name="api_daybook_balance_accounts_update_execute",
        )

    def api_daybook_balance_accounts_delete_preview(
        id: str = Field(min_length=1),
    ) -> WritePreviewResult:
        """Preview deletion of one Billy daybook balance account without a mutation."""

        input = DaybookBalanceAccountDeletePreviewInput(id=id)
        return write_protocol.preview(
            _daybook_balance_account_spec(
                execute_tool_name="api_daybook_balance_accounts_delete_execute",
                method=WriteMethod.DELETE,
                payload=None,
                resource_id=input.id,
                summary="Delete one Billy daybook balance account.",
                expected_effect_state={
                    "action": "delete",
                    "resource": "daybookBalanceAccount",
                    "id": input.id,
                },
            )
        )

    def api_daybook_balance_accounts_delete_execute(
        confirmation_ticket: str = Field(min_length=1),
    ) -> WriteExecutionResult | ToolError:
        """Execute the exact daybook-balance-account deletion in a confirmation ticket."""

        return write_protocol.execute(
            WriteExecuteInput(confirmation_ticket=confirmation_ticket),
            execute_tool_name="api_daybook_balance_accounts_delete_execute",
        )

    server.tool(
        name="api_daybook_balance_accounts_create_preview",
        description="Preview creation of one Billy daybook balance account without a mutation.",
    )(api_daybook_balance_accounts_create_preview)
    server.tool(
        name="api_daybook_balance_accounts_create_execute",
        description="Execute a previewed Billy daybook balance account creation with its ticket.",
    )(api_daybook_balance_accounts_create_execute)
    server.tool(
        name="api_daybook_balance_accounts_update_preview",
        description="Preview an update to one Billy daybook balance account without a mutation.",
    )(api_daybook_balance_accounts_update_preview)
    server.tool(
        name="api_daybook_balance_accounts_update_execute",
        description="Execute a previewed Billy daybook balance account update with its ticket.",
    )(api_daybook_balance_accounts_update_execute)
    server.tool(
        name="api_daybook_balance_accounts_delete_preview",
        description="Preview deletion of one Billy daybook balance account without a mutation.",
    )(api_daybook_balance_accounts_delete_preview)
    server.tool(
        name="api_daybook_balance_accounts_delete_execute",
        description="Execute a previewed Billy daybook balance account deletion with its ticket.",
    )(api_daybook_balance_accounts_delete_execute)


def _daybook_balance_account_spec(
    *,
    execute_tool_name: str,
    method: WriteMethod,
    payload: dict[str, JsonValue] | None,
    resource_id: str | None,
    summary: str,
    expected_effect_state: dict[str, JsonValue],
) -> WriteOperationSpec:
    """Build the server-known operation shape for one daybook balance account CUD preview."""

    return WriteOperationSpec(
        execute_tool_name=execute_tool_name,
        method=method,
        collection_path="/daybookBalanceAccounts",
        singular_root="daybookBalanceAccount",
        plural_root="daybookBalanceAccounts",
        additional_plural_roots=(),
        payload=payload,
        resource_id=resource_id,
        organization_id=None,
        summary=summary,
        expected_effect_state=expected_effect_state,
    )
