"""Ticketed FastMCP tools for documented singular Billy attachment JSON writes."""

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


class _AttachmentWritePreviewInput(BaseModel):
    """Base model that forbids undeclared fields around opaque attachment JSON."""

    model_config = ConfigDict(extra="forbid")


class AttachmentCreatePreviewInput(_AttachmentWritePreviewInput):
    """Input for previewing creation of one Billy attachment."""

    attachment: dict[str, JsonValue]


class AttachmentUpdatePreviewInput(_AttachmentWritePreviewInput):
    """Input for previewing a partial update to one Billy attachment."""

    id: str = Field(min_length=1)
    attachment: dict[str, JsonValue]

    @model_validator(mode="after")
    def attachment_id_matches_route_id(self) -> AttachmentUpdatePreviewInput:
        """Keep an optional attachment-body identifier aligned with the route."""

        if "id" in self.attachment and self.attachment["id"] != self.id:
            raise ValueError("attachment.id must match id")
        return self


class AttachmentDeletePreviewInput(_AttachmentWritePreviewInput):
    """Input for previewing deletion of one Billy attachment."""

    id: str = Field(min_length=1)


def register_attachment_write_tools(
    server: FastMCP,
    client: BillyHttpClient,
    write_protocol: WriteProtocolService,
) -> None:
    """Register exactly the six frozen ticketed attachment JSON write tools."""

    del client

    def api_attachments_create_preview(
        attachment: dict[str, JsonValue],
    ) -> WritePreviewResult:
        """Preview creation of one Billy attachment without a mutation."""

        input = AttachmentCreatePreviewInput(attachment=attachment)
        return write_protocol.preview(
            _attachment_specification(
                execute_tool_name="api_attachments_create_execute",
                method=WriteMethod.POST,
                payload=input.attachment,
                resource_id=None,
            )
        )

    def api_attachments_create_execute(
        confirmation_ticket: str = Field(min_length=1),
    ) -> WriteExecutionResult | ToolError:
        """Execute the exact attachment creation in a confirmation ticket."""

        return write_protocol.execute(
            WriteExecuteInput(confirmation_ticket=confirmation_ticket),
            execute_tool_name="api_attachments_create_execute",
        )

    def api_attachments_update_preview(
        attachment: dict[str, JsonValue],
        id: str = Field(min_length=1),
    ) -> WritePreviewResult:
        """Preview a partial update to one Billy attachment without a mutation."""

        input = AttachmentUpdatePreviewInput(id=id, attachment=attachment)
        return write_protocol.preview(
            _attachment_specification(
                execute_tool_name="api_attachments_update_execute",
                method=WriteMethod.PUT,
                payload=input.attachment,
                resource_id=input.id,
            )
        )

    def api_attachments_update_execute(
        confirmation_ticket: str = Field(min_length=1),
    ) -> WriteExecutionResult | ToolError:
        """Execute the exact attachment update in a confirmation ticket."""

        return write_protocol.execute(
            WriteExecuteInput(confirmation_ticket=confirmation_ticket),
            execute_tool_name="api_attachments_update_execute",
        )

    def api_attachments_delete_preview(id: str = Field(min_length=1)) -> WritePreviewResult:
        """Preview deletion of one Billy attachment without a mutation."""

        input = AttachmentDeletePreviewInput(id=id)
        return write_protocol.preview(
            _attachment_specification(
                execute_tool_name="api_attachments_delete_execute",
                method=WriteMethod.DELETE,
                payload=None,
                resource_id=input.id,
            )
        )

    def api_attachments_delete_execute(
        confirmation_ticket: str = Field(min_length=1),
    ) -> WriteExecutionResult | ToolError:
        """Execute the exact attachment deletion in a confirmation ticket."""

        return write_protocol.execute(
            WriteExecuteInput(confirmation_ticket=confirmation_ticket),
            execute_tool_name="api_attachments_delete_execute",
        )

    server.tool(
        name="api_attachments_create_preview",
        description="Preview creation of one Billy attachment without a mutation.",
    )(api_attachments_create_preview)
    server.tool(
        name="api_attachments_create_execute",
        description="Execute a previewed Billy attachment creation with its ticket.",
    )(api_attachments_create_execute)
    server.tool(
        name="api_attachments_update_preview",
        description="Preview a partial update to one Billy attachment without a mutation.",
    )(api_attachments_update_preview)
    server.tool(
        name="api_attachments_update_execute",
        description="Execute a previewed Billy attachment update with its ticket.",
    )(api_attachments_update_execute)
    server.tool(
        name="api_attachments_delete_preview",
        description="Preview deletion of one Billy attachment without a mutation.",
    )(api_attachments_delete_preview)
    server.tool(
        name="api_attachments_delete_execute",
        description="Execute a previewed Billy attachment deletion with its ticket.",
    )(api_attachments_delete_execute)


def _attachment_specification(
    *,
    execute_tool_name: str,
    method: WriteMethod,
    payload: dict[str, JsonValue] | None,
    resource_id: str | None,
) -> WriteOperationSpec:
    """Build the server-known operation shape for one singular attachment CUD preview."""

    action = {
        WriteMethod.POST: "create",
        WriteMethod.PUT: "update",
        WriteMethod.DELETE: "delete",
    }[method]
    expected_effect_state: dict[str, JsonValue] = {"action": action, "resource": "attachment"}
    if resource_id is not None:
        expected_effect_state["id"] = resource_id
    return WriteOperationSpec(
        execute_tool_name=execute_tool_name,
        method=method,
        collection_path="/attachments",
        singular_root="attachment",
        plural_root="attachments",
        additional_plural_roots=(),
        payload=payload,
        resource_id=resource_id,
        organization_id=None,
        summary=f"{action.capitalize()} one Billy attachment.",
        expected_effect_state=expected_effect_state,
    )
