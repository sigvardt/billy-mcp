"""Ticketed FastMCP tools for documented singular balance-modifier writes."""

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


class _BalanceModifierWritePreviewInput(BaseModel):
    """Forbid undeclared fields around the documented balance-modifier payload."""

    model_config = ConfigDict(extra="forbid", frozen=True)


class BalanceModifierPayload(BaseModel):
    """Writable `#v2balancemodifiers` fields. Amount and dates stay readonly."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    modifier: str = Field(min_length=1)
    subject: str = Field(min_length=1)


class BalanceModifierCreatePreviewInput(_BalanceModifierWritePreviewInput):
    """Input for previewing creation of one Billy balance modifier."""

    balanceModifier: BalanceModifierPayload


class BalanceModifierUpdatePreviewInput(_BalanceModifierWritePreviewInput):
    """Input for previewing an update to one Billy balance modifier."""

    id: str = Field(min_length=1)
    balanceModifier: BalanceModifierPayload


def _balance_modifier_payload(model: BalanceModifierPayload) -> dict[str, JsonValue]:
    """Dump the required documented belongs-to-reference identifiers."""

    dumped = model.model_dump()
    return {str(key): value for key, value in dumped.items()}


def register_balance_modifier_write_tools(
    server: FastMCP,
    client: BillyHttpClient,
    write_protocol: WriteProtocolService,
) -> None:
    """Register exactly the four frozen ticketed balance-modifier write tools."""

    del client

    def api_balance_modifiers_create_preview(
        balanceModifier: BalanceModifierPayload,
    ) -> WritePreviewResult:
        """Preview creation of one balance modifier without sending a mutation."""

        input = BalanceModifierCreatePreviewInput(balanceModifier=balanceModifier)
        return write_protocol.preview(
            _balance_modifier_spec(
                execute_tool_name="api_balance_modifiers_create_execute",
                method=WriteMethod.POST,
                payload=_balance_modifier_payload(input.balanceModifier),
                resource_id=None,
                summary="Create one Billy balance modifier.",
                expected_effect_state={
                    "action": "create",
                    "resource": "balanceModifier",
                },
            )
        )

    def api_balance_modifiers_create_execute(
        confirmation_ticket: str = Field(min_length=1),
    ) -> WriteExecutionResult | ToolError:
        """Execute the exact balance-modifier creation represented by a ticket."""

        return write_protocol.execute(
            WriteExecuteInput(confirmation_ticket=confirmation_ticket),
            execute_tool_name="api_balance_modifiers_create_execute",
        )

    def api_balance_modifiers_update_preview(
        balanceModifier: BalanceModifierPayload,
        id: str = Field(min_length=1),
    ) -> WritePreviewResult:
        """Preview an update to one balance modifier without sending a mutation."""

        input = BalanceModifierUpdatePreviewInput(id=id, balanceModifier=balanceModifier)
        return write_protocol.preview(
            _balance_modifier_spec(
                execute_tool_name="api_balance_modifiers_update_execute",
                method=WriteMethod.PUT,
                payload=_balance_modifier_payload(input.balanceModifier),
                resource_id=input.id,
                summary="Update one Billy balance modifier.",
                expected_effect_state={
                    "action": "update",
                    "resource": "balanceModifier",
                    "id": input.id,
                },
            )
        )

    def api_balance_modifiers_update_execute(
        confirmation_ticket: str = Field(min_length=1),
    ) -> WriteExecutionResult | ToolError:
        """Execute the exact balance-modifier update represented by a ticket."""

        return write_protocol.execute(
            WriteExecuteInput(confirmation_ticket=confirmation_ticket),
            execute_tool_name="api_balance_modifiers_update_execute",
        )

    server.tool(
        name="api_balance_modifiers_create_preview",
        description="Preview creation of one Billy balance modifier without a mutation.",
    )(api_balance_modifiers_create_preview)
    server.tool(
        name="api_balance_modifiers_create_execute",
        description="Execute a previewed Billy balance modifier creation with its ticket.",
    )(api_balance_modifiers_create_execute)
    server.tool(
        name="api_balance_modifiers_update_preview",
        description="Preview an update to one Billy balance modifier without a mutation.",
    )(api_balance_modifiers_update_preview)
    server.tool(
        name="api_balance_modifiers_update_execute",
        description="Execute a previewed Billy balance modifier update with its ticket.",
    )(api_balance_modifiers_update_execute)


def _balance_modifier_spec(
    *,
    execute_tool_name: str,
    method: WriteMethod,
    payload: dict[str, JsonValue] | None,
    resource_id: str | None,
    summary: str,
    expected_effect_state: dict[str, JsonValue],
) -> WriteOperationSpec:
    """Build the server-known operation shape for one balance-modifier write preview."""

    return WriteOperationSpec(
        execute_tool_name=execute_tool_name,
        method=method,
        collection_path="/balanceModifiers",
        singular_root="balanceModifier",
        plural_root="balanceModifiers",
        additional_plural_roots=(),
        payload=payload,
        resource_id=resource_id,
        organization_id=None,
        summary=summary,
        expected_effect_state=expected_effect_state,
    )
