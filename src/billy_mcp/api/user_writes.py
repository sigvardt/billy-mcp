"""Ticketed FastMCP tools for singular Billy user updates."""

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


class _UserWritePreviewInput(BaseModel):
    """Forbid undeclared outer fields while preserving opaque user JSON."""

    model_config = ConfigDict(extra="forbid")


class UserUpdatePreviewInput(_UserWritePreviewInput):
    """Input for previewing an update to one Billy user."""

    id: str = Field(min_length=1)
    user: dict[str, JsonValue]

    @model_validator(mode="after")
    def user_id_matches_route_id(self) -> UserUpdatePreviewInput:
        """Keep an optional body identifier aligned with the route."""

        if "id" in self.user and self.user["id"] != self.id:
            raise ValueError("user.id must match id")
        return self


def register_user_write_tools(
    server: FastMCP,
    client: BillyHttpClient,
    write_protocol: WriteProtocolService,
) -> None:
    """Register exactly the two frozen user update tools."""

    del client

    def api_users_update_preview(
        user: dict[str, JsonValue],
        id: str = Field(min_length=1),
    ) -> WritePreviewResult:
        """Preview an update to one Billy user without a mutation."""

        input = UserUpdatePreviewInput(id=id, user=user)
        return write_protocol.preview(
            _user_update_specification(payload=input.user, resource_id=input.id)
        )

    def api_users_update_execute(
        confirmation_ticket: str = Field(min_length=1),
    ) -> WriteExecutionResult | ToolError:
        """Execute the exact user update in a ticket."""

        return write_protocol.execute(
            WriteExecuteInput(confirmation_ticket=confirmation_ticket),
            execute_tool_name="api_users_update_execute",
        )

    server.tool(
        name="api_users_update_preview",
        description="Preview an update to one Billy user without a mutation.",
    )(api_users_update_preview)
    server.tool(
        name="api_users_update_execute",
        description="Execute a previewed Billy user update with its ticket.",
    )(api_users_update_execute)


def _user_update_specification(
    *, payload: dict[str, JsonValue], resource_id: str
) -> WriteOperationSpec:
    """Build the server-known shape for one singular user update."""

    return WriteOperationSpec(
        execute_tool_name="api_users_update_execute",
        method=WriteMethod.PUT,
        collection_path="/users",
        singular_root="user",
        plural_root="users",
        additional_plural_roots=(),
        payload=payload,
        resource_id=resource_id,
        organization_id=None,
        summary="Update one Billy user.",
        expected_effect_state={"action": "update", "resource": "user", "id": resource_id},
    )
