"""Ticketed FastMCP tools for documented singular Billy locale writes."""

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


class _LocaleWritePreviewInput(BaseModel):
    """Forbid undeclared fields around the documented locale payload."""

    model_config = ConfigDict(extra="forbid", frozen=True)


class LocalePayload(BaseModel):
    """Writable `#v2locales` fields."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    name: str | None = None
    icon: str | None = None


class LocaleCreatePreviewInput(_LocaleWritePreviewInput):
    """Input for previewing creation of one Billy locale."""

    locale: LocalePayload


class LocaleUpdatePreviewInput(_LocaleWritePreviewInput):
    """Input for previewing an update to one Billy locale."""

    id: str = Field(min_length=1)
    locale: LocalePayload


def _locale_payload(model: LocalePayload) -> dict[str, JsonValue]:
    """Dump only set documented fields for the ticketed request body."""

    dumped = model.model_dump(exclude_none=True, exclude_unset=True)
    return {str(key): value for key, value in dumped.items()}


def register_locale_write_tools(
    server: FastMCP,
    client: BillyHttpClient,
    write_protocol: WriteProtocolService,
) -> None:
    """Register exactly the four frozen ticketed locale write tools."""

    del client

    def api_locales_create_preview(locale: LocalePayload) -> WritePreviewResult:
        """Preview creation of one Billy locale without sending a mutation."""

        input = LocaleCreatePreviewInput(locale=locale)
        return write_protocol.preview(
            _locale_spec(
                execute_tool_name="api_locales_create_execute",
                method=WriteMethod.POST,
                payload=_locale_payload(input.locale),
                resource_id=None,
                summary="Create one Billy locale.",
                expected_effect_state={"action": "create", "resource": "locale"},
            )
        )

    def api_locales_create_execute(
        confirmation_ticket: str = Field(min_length=1),
    ) -> WriteExecutionResult | ToolError:
        """Execute the exact locale creation represented by a confirmation ticket."""

        return write_protocol.execute(
            WriteExecuteInput(confirmation_ticket=confirmation_ticket),
            execute_tool_name="api_locales_create_execute",
        )

    def api_locales_update_preview(
        locale: LocalePayload,
        id: str = Field(min_length=1),
    ) -> WritePreviewResult:
        """Preview an update to one Billy locale without sending a mutation."""

        input = LocaleUpdatePreviewInput(id=id, locale=locale)
        return write_protocol.preview(
            _locale_spec(
                execute_tool_name="api_locales_update_execute",
                method=WriteMethod.PUT,
                payload=_locale_payload(input.locale),
                resource_id=input.id,
                summary="Update one Billy locale.",
                expected_effect_state={
                    "action": "update",
                    "resource": "locale",
                    "id": input.id,
                },
            )
        )

    def api_locales_update_execute(
        confirmation_ticket: str = Field(min_length=1),
    ) -> WriteExecutionResult | ToolError:
        """Execute the exact locale update represented by a confirmation ticket."""

        return write_protocol.execute(
            WriteExecuteInput(confirmation_ticket=confirmation_ticket),
            execute_tool_name="api_locales_update_execute",
        )

    server.tool(
        name="api_locales_create_preview",
        description="Preview creation of one Billy locale without making a mutation.",
    )(api_locales_create_preview)
    server.tool(
        name="api_locales_create_execute",
        description="Execute a previewed Billy locale creation with its ticket.",
    )(api_locales_create_execute)
    server.tool(
        name="api_locales_update_preview",
        description="Preview an update to one Billy locale without making a mutation.",
    )(api_locales_update_preview)
    server.tool(
        name="api_locales_update_execute",
        description="Execute a previewed Billy locale update with its ticket.",
    )(api_locales_update_execute)


def _locale_spec(
    *,
    execute_tool_name: str,
    method: WriteMethod,
    payload: dict[str, JsonValue] | None,
    resource_id: str | None,
    summary: str,
    expected_effect_state: dict[str, JsonValue],
) -> WriteOperationSpec:
    """Build the server-known operation shape for one locale write preview."""

    return WriteOperationSpec(
        execute_tool_name=execute_tool_name,
        method=method,
        collection_path="/locales",
        singular_root="locale",
        plural_root="locales",
        additional_plural_roots=(),
        payload=payload,
        resource_id=resource_id,
        organization_id=None,
        summary=summary,
        expected_effect_state=expected_effect_state,
    )
