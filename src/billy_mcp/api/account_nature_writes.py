"""Ticketed FastMCP tools for documented singular Billy account-nature writes."""

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


class _AccountNatureWritePreviewInput(BaseModel):
    """Base model that forbids undeclared fields around the documented nature payload."""

    model_config = ConfigDict(extra="forbid", frozen=True)


class AccountNaturePayload(BaseModel):
    """Writable `#v2accountnatures` fields. Enum members stay opaque strings."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    reportType: str | None = None
    name: str | None = None
    normalBalance: str | None = None


class AccountNatureCreatePreviewInput(_AccountNatureWritePreviewInput):
    """Input for previewing creation of one Billy account nature."""

    accountNature: AccountNaturePayload


class AccountNatureUpdatePreviewInput(_AccountNatureWritePreviewInput):
    """Input for previewing an update to one Billy account nature."""

    id: str = Field(min_length=1)
    accountNature: AccountNaturePayload


def _account_nature_payload(model: AccountNaturePayload) -> dict[str, JsonValue]:
    """Dump only set documented fields for the ticketed request body."""

    dumped = model.model_dump(exclude_none=True, exclude_unset=True)
    return {str(key): value for key, value in dumped.items()}


def register_account_nature_write_tools(
    server: FastMCP,
    client: BillyHttpClient,
    write_protocol: WriteProtocolService,
) -> None:
    """Register exactly the four frozen ticketed account-nature write tools."""

    del client

    def api_account_natures_create_preview(
        accountNature: AccountNaturePayload,
    ) -> WritePreviewResult:
        """Preview creation of one Billy account nature without sending a mutation."""

        input = AccountNatureCreatePreviewInput(accountNature=accountNature)
        return write_protocol.preview(
            _account_nature_spec(
                execute_tool_name="api_account_natures_create_execute",
                method=WriteMethod.POST,
                payload=_account_nature_payload(input.accountNature),
                resource_id=None,
                summary="Create one Billy account nature.",
                expected_effect_state={
                    "action": "create",
                    "resource": "accountNature",
                },
            )
        )

    def api_account_natures_create_execute(
        confirmation_ticket: str = Field(min_length=1),
    ) -> WriteExecutionResult | ToolError:
        """Execute the exact account-nature creation represented by a confirmation ticket."""

        return write_protocol.execute(
            WriteExecuteInput(confirmation_ticket=confirmation_ticket),
            execute_tool_name="api_account_natures_create_execute",
        )

    def api_account_natures_update_preview(
        accountNature: AccountNaturePayload,
        id: str = Field(min_length=1),
    ) -> WritePreviewResult:
        """Preview an update to one Billy account nature without sending a mutation."""

        input = AccountNatureUpdatePreviewInput(id=id, accountNature=accountNature)
        return write_protocol.preview(
            _account_nature_spec(
                execute_tool_name="api_account_natures_update_execute",
                method=WriteMethod.PUT,
                payload=_account_nature_payload(input.accountNature),
                resource_id=input.id,
                summary="Update one Billy account nature.",
                expected_effect_state={
                    "action": "update",
                    "resource": "accountNature",
                    "id": input.id,
                },
            )
        )

    def api_account_natures_update_execute(
        confirmation_ticket: str = Field(min_length=1),
    ) -> WriteExecutionResult | ToolError:
        """Execute the exact account-nature update represented by a confirmation ticket."""

        return write_protocol.execute(
            WriteExecuteInput(confirmation_ticket=confirmation_ticket),
            execute_tool_name="api_account_natures_update_execute",
        )

    server.tool(
        name="api_account_natures_create_preview",
        description="Preview creation of one Billy account nature without making a mutation.",
    )(api_account_natures_create_preview)
    server.tool(
        name="api_account_natures_create_execute",
        description=(
            "Execute a previewed Billy account-nature creation with its confirmation ticket."
        ),
    )(api_account_natures_create_execute)
    server.tool(
        name="api_account_natures_update_preview",
        description="Preview an update to one Billy account nature without making a mutation.",
    )(api_account_natures_update_preview)
    server.tool(
        name="api_account_natures_update_execute",
        description=(
            "Execute a previewed Billy account-nature update with its confirmation ticket."
        ),
    )(api_account_natures_update_execute)


def _account_nature_spec(
    *,
    execute_tool_name: str,
    method: WriteMethod,
    payload: dict[str, JsonValue] | None,
    resource_id: str | None,
    summary: str,
    expected_effect_state: dict[str, JsonValue],
) -> WriteOperationSpec:
    """Build the server-known operation shape for one account-nature write preview."""

    return WriteOperationSpec(
        execute_tool_name=execute_tool_name,
        method=method,
        collection_path="/accountNatures",
        singular_root="accountNature",
        plural_root="accountNatures",
        additional_plural_roots=(),
        payload=payload,
        resource_id=resource_id,
        organization_id=None,
        summary=summary,
        expected_effect_state=expected_effect_state,
    )
