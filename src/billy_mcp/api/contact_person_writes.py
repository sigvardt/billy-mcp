"""Typed ticketed write tools for documented Billy contact-person endpoints."""

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


class _PreviewInput(BaseModel):
    """Base type for the intentionally small contact-person preview surface."""

    model_config = ConfigDict(extra="forbid", validate_by_alias=True, validate_by_name=True)


class ContactPersonCreatePreviewInput(_PreviewInput):
    """Opaque documented contact-person payload for a create preview."""

    contact_person: dict[str, JsonValue] = Field(
        alias="contactPerson", serialization_alias="contactPerson"
    )


class ContactPersonUpdatePreviewInput(ContactPersonCreatePreviewInput):
    """Opaque documented contact-person payload and identifier for an update preview."""

    id: str = Field(min_length=1)


class ContactPersonDeletePreviewInput(_PreviewInput):
    """Identifier for a bodyless documented contact-person delete preview."""

    id: str = Field(min_length=1)


def register_contact_person_write_tools(
    server: FastMCP, client: BillyHttpClient, write_protocol: WriteProtocolService
) -> None:
    """Register exactly the six ticketed contact-person write tools."""

    del client

    def api_contact_persons_create_preview(
        contactPerson: dict[str, JsonValue],
    ) -> WritePreviewResult:
        """Preview a create of one Billy contact person without sending a write."""

        input = ContactPersonCreatePreviewInput(contactPerson=contactPerson)
        return write_protocol.preview(
            _operation_specification(
                input=input,
                method=WriteMethod.POST,
                execute_tool_name="api_contact_persons_create_execute",
            )
        )

    def api_contact_persons_create_execute(
        confirmation_ticket: str = Field(min_length=1),
    ) -> WriteExecutionResult | ToolError:
        """Execute exactly the contact-person create previously bound to a ticket."""

        return write_protocol.execute(WriteExecuteInput(confirmation_ticket=confirmation_ticket))

    def api_contact_persons_update_preview(
        id: str,
        contactPerson: dict[str, JsonValue],
    ) -> WritePreviewResult:
        """Preview an update of one Billy contact person without sending a write."""

        input = ContactPersonUpdatePreviewInput(id=id, contactPerson=contactPerson)
        return write_protocol.preview(
            _operation_specification(
                input=input,
                method=WriteMethod.PUT,
                execute_tool_name="api_contact_persons_update_execute",
            )
        )

    def api_contact_persons_update_execute(
        confirmation_ticket: str = Field(min_length=1),
    ) -> WriteExecutionResult | ToolError:
        """Execute exactly the contact-person update previously bound to a ticket."""

        return write_protocol.execute(WriteExecuteInput(confirmation_ticket=confirmation_ticket))

    def api_contact_persons_delete_preview(id: str = Field(min_length=1)) -> WritePreviewResult:
        """Preview a bodyless deletion of one Billy contact person."""

        input = ContactPersonDeletePreviewInput(id=id)
        return write_protocol.preview(
            _operation_specification(
                input=input,
                method=WriteMethod.DELETE,
                execute_tool_name="api_contact_persons_delete_execute",
            )
        )

    def api_contact_persons_delete_execute(
        confirmation_ticket: str = Field(min_length=1),
    ) -> WriteExecutionResult | ToolError:
        """Execute exactly the contact-person deletion previously bound to a ticket."""

        return write_protocol.execute(WriteExecuteInput(confirmation_ticket=confirmation_ticket))

    server.tool(
        name="api_contact_persons_create_preview",
        description="Preview a ticketed create of one Billy contact person.",
    )(api_contact_persons_create_preview)
    server.tool(
        name="api_contact_persons_create_execute",
        description="Execute a previously previewed Billy contact-person create.",
    )(api_contact_persons_create_execute)
    server.tool(
        name="api_contact_persons_update_preview",
        description="Preview a ticketed update of one Billy contact person.",
    )(api_contact_persons_update_preview)
    server.tool(
        name="api_contact_persons_update_execute",
        description="Execute a previously previewed Billy contact-person update.",
    )(api_contact_persons_update_execute)
    server.tool(
        name="api_contact_persons_delete_preview",
        description="Preview a ticketed bodyless deletion of one Billy contact person.",
    )(api_contact_persons_delete_preview)
    server.tool(
        name="api_contact_persons_delete_execute",
        description="Execute a previously previewed Billy contact-person deletion.",
    )(api_contact_persons_delete_execute)


def _operation_specification(
    *,
    input: ContactPersonCreatePreviewInput | ContactPersonDeletePreviewInput,
    method: WriteMethod,
    execute_tool_name: str,
) -> WriteOperationSpec:
    """Build the complete server-known operation for one documented singular write."""

    resource_id = (
        input.id
        if isinstance(input, (ContactPersonUpdatePreviewInput, ContactPersonDeletePreviewInput))
        else None
    )
    payload = input.contact_person if isinstance(input, ContactPersonCreatePreviewInput) else None
    action = {
        WriteMethod.POST: "create",
        WriteMethod.PUT: "update",
        WriteMethod.DELETE: "delete",
    }[method]
    expected_effect_state: dict[str, JsonValue] = {
        "action": action,
        "resource": "contactPerson",
    }
    if resource_id is not None:
        expected_effect_state["id"] = resource_id
    return WriteOperationSpec(
        execute_tool_name=execute_tool_name,
        method=method,
        collection_path="/contactPersons",
        singular_root="contactPerson",
        plural_root="contactPersons",
        payload=payload,
        resource_id=resource_id,
        organization_id=None,
        summary=f"{action.capitalize()} one Billy contact person.",
        expected_effect_state=expected_effect_state,
    )
