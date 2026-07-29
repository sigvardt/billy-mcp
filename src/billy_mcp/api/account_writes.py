"""Ticketed FastMCP tools for documented singular Billy account writes."""

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


class _AccountWritePreviewInput(BaseModel):
    """Base model that forbids undeclared fields around opaque account payloads."""

    model_config = ConfigDict(extra="forbid")


class AccountGroupCreatePreviewInput(_AccountWritePreviewInput):
    """Input for previewing creation of one Billy account group."""

    accountGroup: dict[str, JsonValue]


class AccountGroupUpdatePreviewInput(_AccountWritePreviewInput):
    """Input for previewing an update to one Billy account group."""

    id: str = Field(min_length=1)
    accountGroup: dict[str, JsonValue]


class AccountGroupDeletePreviewInput(_AccountWritePreviewInput):
    """Input for previewing deletion of one Billy account group."""

    id: str = Field(min_length=1)


class AccountCreatePreviewInput(_AccountWritePreviewInput):
    """Input for previewing creation of one Billy account."""

    account: dict[str, JsonValue]


class AccountUpdatePreviewInput(_AccountWritePreviewInput):
    """Input for previewing an update to one Billy account."""

    id: str = Field(min_length=1)
    account: dict[str, JsonValue]


class AccountDeletePreviewInput(_AccountWritePreviewInput):
    """Input for previewing deletion of one Billy account."""

    id: str = Field(min_length=1)


def register_account_write_tools(
    server: FastMCP,
    client: BillyHttpClient,
    write_protocol: WriteProtocolService,
) -> None:
    """Register exactly the twelve frozen ticketed account write tools."""

    del client

    def api_account_groups_create_preview(
        accountGroup: dict[str, JsonValue],
    ) -> WritePreviewResult:
        """Preview creation of one Billy account group without sending a mutation."""

        input = AccountGroupCreatePreviewInput(accountGroup=accountGroup)
        return write_protocol.preview(
            _account_specification(
                execute_tool_name="api_account_groups_create_execute",
                method=WriteMethod.POST,
                collection_path="/accountGroups",
                singular_root="accountGroup",
                plural_root="accountGroups",
                resource="accountGroup",
                payload=input.accountGroup,
                resource_id=None,
            )
        )

    def api_account_groups_create_execute(
        confirmation_ticket: str = Field(min_length=1),
    ) -> WriteExecutionResult | ToolError:
        """Execute the exact account-group creation represented by a confirmation ticket."""

        return write_protocol.execute(
            WriteExecuteInput(confirmation_ticket=confirmation_ticket),
            execute_tool_name="api_account_groups_create_execute",
        )

    def api_account_groups_update_preview(
        accountGroup: dict[str, JsonValue],
        id: str = Field(min_length=1),
    ) -> WritePreviewResult:
        """Preview an update to one Billy account group without sending a mutation."""

        input = AccountGroupUpdatePreviewInput(id=id, accountGroup=accountGroup)
        return write_protocol.preview(
            _account_specification(
                execute_tool_name="api_account_groups_update_execute",
                method=WriteMethod.PUT,
                collection_path="/accountGroups",
                singular_root="accountGroup",
                plural_root="accountGroups",
                resource="accountGroup",
                payload=input.accountGroup,
                resource_id=input.id,
            )
        )

    def api_account_groups_update_execute(
        confirmation_ticket: str = Field(min_length=1),
    ) -> WriteExecutionResult | ToolError:
        """Execute the exact account-group update represented by a confirmation ticket."""

        return write_protocol.execute(
            WriteExecuteInput(confirmation_ticket=confirmation_ticket),
            execute_tool_name="api_account_groups_update_execute",
        )

    def api_account_groups_delete_preview(id: str = Field(min_length=1)) -> WritePreviewResult:
        """Preview deletion of one Billy account group without sending a mutation."""

        input = AccountGroupDeletePreviewInput(id=id)
        return write_protocol.preview(
            _account_specification(
                execute_tool_name="api_account_groups_delete_execute",
                method=WriteMethod.DELETE,
                collection_path="/accountGroups",
                singular_root="accountGroup",
                plural_root="accountGroups",
                resource="accountGroup",
                payload=None,
                resource_id=input.id,
            )
        )

    def api_account_groups_delete_execute(
        confirmation_ticket: str = Field(min_length=1),
    ) -> WriteExecutionResult | ToolError:
        """Execute the exact account-group deletion represented by a confirmation ticket."""

        return write_protocol.execute(
            WriteExecuteInput(confirmation_ticket=confirmation_ticket),
            execute_tool_name="api_account_groups_delete_execute",
        )

    def api_accounts_create_preview(account: dict[str, JsonValue]) -> WritePreviewResult:
        """Preview creation of one Billy account without sending a mutation."""

        input = AccountCreatePreviewInput(account=account)
        return write_protocol.preview(
            _account_specification(
                execute_tool_name="api_accounts_create_execute",
                method=WriteMethod.POST,
                collection_path="/accounts",
                singular_root="account",
                plural_root="accounts",
                resource="account",
                payload=input.account,
                resource_id=None,
            )
        )

    def api_accounts_create_execute(
        confirmation_ticket: str = Field(min_length=1),
    ) -> WriteExecutionResult | ToolError:
        """Execute the exact account creation represented by a confirmation ticket."""

        return write_protocol.execute(
            WriteExecuteInput(confirmation_ticket=confirmation_ticket),
            execute_tool_name="api_accounts_create_execute",
        )

    def api_accounts_update_preview(
        account: dict[str, JsonValue],
        id: str = Field(min_length=1),
    ) -> WritePreviewResult:
        """Preview an update to one Billy account without sending a mutation."""

        input = AccountUpdatePreviewInput(id=id, account=account)
        return write_protocol.preview(
            _account_specification(
                execute_tool_name="api_accounts_update_execute",
                method=WriteMethod.PUT,
                collection_path="/accounts",
                singular_root="account",
                plural_root="accounts",
                resource="account",
                payload=input.account,
                resource_id=input.id,
            )
        )

    def api_accounts_update_execute(
        confirmation_ticket: str = Field(min_length=1),
    ) -> WriteExecutionResult | ToolError:
        """Execute the exact account update represented by a confirmation ticket."""

        return write_protocol.execute(
            WriteExecuteInput(confirmation_ticket=confirmation_ticket),
            execute_tool_name="api_accounts_update_execute",
        )

    def api_accounts_delete_preview(id: str = Field(min_length=1)) -> WritePreviewResult:
        """Preview deletion of one Billy account without sending a mutation."""

        input = AccountDeletePreviewInput(id=id)
        return write_protocol.preview(
            _account_specification(
                execute_tool_name="api_accounts_delete_execute",
                method=WriteMethod.DELETE,
                collection_path="/accounts",
                singular_root="account",
                plural_root="accounts",
                resource="account",
                payload=None,
                resource_id=input.id,
            )
        )

    def api_accounts_delete_execute(
        confirmation_ticket: str = Field(min_length=1),
    ) -> WriteExecutionResult | ToolError:
        """Execute the exact account deletion represented by a confirmation ticket."""

        return write_protocol.execute(
            WriteExecuteInput(confirmation_ticket=confirmation_ticket),
            execute_tool_name="api_accounts_delete_execute",
        )

    server.tool(
        name="api_account_groups_create_preview",
        description="Preview creation of one Billy account group without making a mutation.",
    )(api_account_groups_create_preview)
    server.tool(
        name="api_account_groups_create_execute",
        description=(
            "Execute a previewed Billy account-group creation with its confirmation ticket."
        ),
    )(api_account_groups_create_execute)
    server.tool(
        name="api_account_groups_update_preview",
        description="Preview an update to one Billy account group without making a mutation.",
    )(api_account_groups_update_preview)
    server.tool(
        name="api_account_groups_update_execute",
        description="Execute a previewed Billy account-group update with its confirmation ticket.",
    )(api_account_groups_update_execute)
    server.tool(
        name="api_account_groups_delete_preview",
        description="Preview deletion of one Billy account group without making a mutation.",
    )(api_account_groups_delete_preview)
    server.tool(
        name="api_account_groups_delete_execute",
        description=(
            "Execute a previewed Billy account-group deletion with its confirmation ticket."
        ),
    )(api_account_groups_delete_execute)
    server.tool(
        name="api_accounts_create_preview",
        description="Preview creation of one Billy account without making a mutation.",
    )(api_accounts_create_preview)
    server.tool(
        name="api_accounts_create_execute",
        description="Execute a previewed Billy account creation with its confirmation ticket.",
    )(api_accounts_create_execute)
    server.tool(
        name="api_accounts_update_preview",
        description="Preview an update to one Billy account without making a mutation.",
    )(api_accounts_update_preview)
    server.tool(
        name="api_accounts_update_execute",
        description="Execute a previewed Billy account update with its confirmation ticket.",
    )(api_accounts_update_execute)
    server.tool(
        name="api_accounts_delete_preview",
        description="Preview deletion of one Billy account without making a mutation.",
    )(api_accounts_delete_preview)
    server.tool(
        name="api_accounts_delete_execute",
        description="Execute a previewed Billy account deletion with its confirmation ticket.",
    )(api_accounts_delete_execute)


def _account_specification(
    *,
    execute_tool_name: str,
    method: WriteMethod,
    collection_path: str,
    singular_root: str,
    plural_root: str,
    resource: str,
    payload: dict[str, JsonValue] | None,
    resource_id: str | None,
) -> WriteOperationSpec:
    """Build one complete server-known account write for the shared protocol."""

    action = {
        WriteMethod.POST: "create",
        WriteMethod.PUT: "update",
        WriteMethod.DELETE: "delete",
    }[method]
    expected_effect_state: dict[str, JsonValue] = {"action": action, "resource": resource}
    if resource_id is not None:
        expected_effect_state["id"] = resource_id
    return WriteOperationSpec(
        execute_tool_name=execute_tool_name,
        method=method,
        collection_path=collection_path,
        singular_root=singular_root,
        plural_root=plural_root,
        additional_plural_roots=(),
        payload=payload,
        resource_id=resource_id,
        organization_id=None,
        summary=f"{action.capitalize()} one Billy {resource.replace('Group', ' group')}.",
        expected_effect_state=expected_effect_state,
    )
