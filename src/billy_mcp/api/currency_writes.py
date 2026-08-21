"""Ticketed FastMCP tools for documented singular Billy currency writes."""

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


class _CurrencyWritePreviewInput(BaseModel):
    """Forbid undeclared fields around the documented currency payload."""

    model_config = ConfigDict(extra="forbid", frozen=True)


class CurrencyPayload(BaseModel):
    """Writable `#v2currencies` fields."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    name: str | None = None
    exchangeRate: float | None = None


class CurrencyCreatePreviewInput(_CurrencyWritePreviewInput):
    """Input for previewing creation of one Billy currency."""

    currency: CurrencyPayload


class CurrencyUpdatePreviewInput(_CurrencyWritePreviewInput):
    """Input for previewing an update to one Billy currency."""

    id: str = Field(min_length=1)
    currency: CurrencyPayload


def _currency_payload(model: CurrencyPayload) -> dict[str, JsonValue]:
    """Dump only set documented fields for the ticketed request body."""

    dumped = model.model_dump(exclude_none=True, exclude_unset=True)
    return {str(key): value for key, value in dumped.items()}


def register_currency_write_tools(
    server: FastMCP,
    client: BillyHttpClient,
    write_protocol: WriteProtocolService,
) -> None:
    """Register exactly the four frozen ticketed currency write tools."""

    del client

    def api_currencies_create_preview(currency: CurrencyPayload) -> WritePreviewResult:
        """Preview creation of one Billy currency without sending a mutation."""

        input = CurrencyCreatePreviewInput(currency=currency)
        return write_protocol.preview(
            _currency_spec(
                execute_tool_name="api_currencies_create_execute",
                method=WriteMethod.POST,
                payload=_currency_payload(input.currency),
                resource_id=None,
                summary="Create one Billy currency.",
                expected_effect_state={"action": "create", "resource": "currency"},
            )
        )

    def api_currencies_create_execute(
        confirmation_ticket: str = Field(min_length=1),
    ) -> WriteExecutionResult | ToolError:
        """Execute the exact currency creation represented by a confirmation ticket."""

        return write_protocol.execute(
            WriteExecuteInput(confirmation_ticket=confirmation_ticket),
            execute_tool_name="api_currencies_create_execute",
        )

    def api_currencies_update_preview(
        currency: CurrencyPayload,
        id: str = Field(min_length=1),
    ) -> WritePreviewResult:
        """Preview an update to one Billy currency without sending a mutation."""

        input = CurrencyUpdatePreviewInput(id=id, currency=currency)
        return write_protocol.preview(
            _currency_spec(
                execute_tool_name="api_currencies_update_execute",
                method=WriteMethod.PUT,
                payload=_currency_payload(input.currency),
                resource_id=input.id,
                summary="Update one Billy currency.",
                expected_effect_state={
                    "action": "update",
                    "resource": "currency",
                    "id": input.id,
                },
            )
        )

    def api_currencies_update_execute(
        confirmation_ticket: str = Field(min_length=1),
    ) -> WriteExecutionResult | ToolError:
        """Execute the exact currency update represented by a confirmation ticket."""

        return write_protocol.execute(
            WriteExecuteInput(confirmation_ticket=confirmation_ticket),
            execute_tool_name="api_currencies_update_execute",
        )

    server.tool(
        name="api_currencies_create_preview",
        description="Preview creation of one Billy currency without making a mutation.",
    )(api_currencies_create_preview)
    server.tool(
        name="api_currencies_create_execute",
        description="Execute a previewed Billy currency creation with its ticket.",
    )(api_currencies_create_execute)
    server.tool(
        name="api_currencies_update_preview",
        description="Preview an update to one Billy currency without making a mutation.",
    )(api_currencies_update_preview)
    server.tool(
        name="api_currencies_update_execute",
        description="Execute a previewed Billy currency update with its ticket.",
    )(api_currencies_update_execute)


def _currency_spec(
    *,
    execute_tool_name: str,
    method: WriteMethod,
    payload: dict[str, JsonValue] | None,
    resource_id: str | None,
    summary: str,
    expected_effect_state: dict[str, JsonValue],
) -> WriteOperationSpec:
    """Build the server-known operation shape for one currency write preview."""

    return WriteOperationSpec(
        execute_tool_name=execute_tool_name,
        method=method,
        collection_path="/currencies",
        singular_root="currency",
        plural_root="currencies",
        additional_plural_roots=(),
        payload=payload,
        resource_id=resource_id,
        organization_id=None,
        summary=summary,
        expected_effect_state=expected_effect_state,
    )
