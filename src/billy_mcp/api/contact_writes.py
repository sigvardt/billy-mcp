"""Ticketed FastMCP tools for documented singular Billy contact writes."""

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

_CREATE_EXECUTE_TOOL = "api_contacts_create_execute"
_UPDATE_EXECUTE_TOOL = "api_contacts_update_execute"
_DELETE_EXECUTE_TOOL = "api_contacts_delete_execute"


class _ContactWritePreviewInput(BaseModel):
    """Base model that rejects undeclared fields around an opaque contact payload."""

    model_config = ConfigDict(extra="forbid")


class ContactCreatePreviewInput(_ContactWritePreviewInput):
    """Input for previewing creation of one Billy contact."""

    contact: dict[str, JsonValue]


class ContactUpdatePreviewInput(_ContactWritePreviewInput):
    """Input for previewing an update to one Billy contact."""

    id: str = Field(min_length=1)
    contact: dict[str, JsonValue]


class ContactDeletePreviewInput(_ContactWritePreviewInput):
    """Input for previewing deletion of one Billy contact."""

    id: str = Field(min_length=1)


def register_contact_write_tools(
    server: FastMCP,
    client: BillyHttpClient,
    write_protocol: WriteProtocolService,
) -> None:
    """Register exactly the six frozen ticketed contact write tools."""

    del client

    def api_contacts_create_preview(input: ContactCreatePreviewInput) -> WritePreviewResult:
        """Preview creation of one Billy contact without sending a mutation."""

        return write_protocol.preview(
            _contact_spec(
                execute_tool_name=_CREATE_EXECUTE_TOOL,
                method=WriteMethod.POST,
                payload=input.contact,
                resource_id=None,
                summary="Create one Billy contact.",
                expected_effect_state={"action": "create", "resource": "contact"},
            )
        )

    def api_contacts_create_execute(
        input: WriteExecuteInput,
    ) -> WriteExecutionResult | ToolError:
        """Execute the exact contact creation represented by a confirmation ticket."""

        return write_protocol.execute(input)

    def api_contacts_update_preview(input: ContactUpdatePreviewInput) -> WritePreviewResult:
        """Preview an update to one Billy contact without sending a mutation."""

        return write_protocol.preview(
            _contact_spec(
                execute_tool_name=_UPDATE_EXECUTE_TOOL,
                method=WriteMethod.PUT,
                payload=input.contact,
                resource_id=input.id,
                summary="Update one Billy contact.",
                expected_effect_state={
                    "action": "update",
                    "resource": "contact",
                    "id": input.id,
                },
            )
        )

    def api_contacts_update_execute(
        input: WriteExecuteInput,
    ) -> WriteExecutionResult | ToolError:
        """Execute the exact contact update represented by a confirmation ticket."""

        return write_protocol.execute(input)

    def api_contacts_delete_preview(input: ContactDeletePreviewInput) -> WritePreviewResult:
        """Preview deletion of one Billy contact without sending a mutation."""

        return write_protocol.preview(
            _contact_spec(
                execute_tool_name=_DELETE_EXECUTE_TOOL,
                method=WriteMethod.DELETE,
                payload=None,
                resource_id=input.id,
                summary="Delete one Billy contact.",
                expected_effect_state={
                    "action": "delete",
                    "resource": "contact",
                    "id": input.id,
                },
            )
        )

    def api_contacts_delete_execute(
        input: WriteExecuteInput,
    ) -> WriteExecutionResult | ToolError:
        """Execute the exact contact deletion represented by a confirmation ticket."""

        return write_protocol.execute(input)

    server.tool(
        name="api_contacts_create_preview",
        description="Preview creation of one Billy contact without making a mutation.",
    )(api_contacts_create_preview)
    server.tool(
        name=_CREATE_EXECUTE_TOOL,
        description="Execute a previewed Billy contact creation with its confirmation ticket.",
    )(api_contacts_create_execute)
    server.tool(
        name="api_contacts_update_preview",
        description="Preview an update to one Billy contact without making a mutation.",
    )(api_contacts_update_preview)
    server.tool(
        name=_UPDATE_EXECUTE_TOOL,
        description="Execute a previewed Billy contact update with its confirmation ticket.",
    )(api_contacts_update_execute)
    server.tool(
        name="api_contacts_delete_preview",
        description="Preview deletion of one Billy contact without making a mutation.",
    )(api_contacts_delete_preview)
    server.tool(
        name=_DELETE_EXECUTE_TOOL,
        description="Execute a previewed Billy contact deletion with its confirmation ticket.",
    )(api_contacts_delete_execute)


def _contact_spec(
    *,
    execute_tool_name: str,
    method: WriteMethod,
    payload: dict[str, JsonValue] | None,
    resource_id: str | None,
    summary: str,
    expected_effect_state: dict[str, JsonValue],
) -> WriteOperationSpec:
    """Build the server-known operation shape for one contact CUD preview."""

    return WriteOperationSpec(
        execute_tool_name=execute_tool_name,
        method=method,
        collection_path="/contacts",
        singular_root="contact",
        plural_root="contacts",
        payload=payload,
        resource_id=resource_id,
        organization_id=None,
        summary=summary,
        expected_effect_state=expected_effect_state,
    )
