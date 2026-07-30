"""Ticketed FastMCP tools for singular Billy invoice-reminder creation."""

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


class InvoiceReminderCreatePreviewInput(BaseModel):
    """Forbid undeclared outer fields while preserving opaque reminder JSON."""

    model_config = ConfigDict(extra="forbid")

    invoiceReminder: dict[str, JsonValue]


def register_invoice_reminder_write_tools(
    server: FastMCP,
    client: BillyHttpClient,
    write_protocol: WriteProtocolService,
) -> None:
    """Register exactly the two frozen invoice-reminder create tools."""

    del client

    def api_invoice_reminders_create_preview(
        invoiceReminder: dict[str, JsonValue],
    ) -> WritePreviewResult:
        """Preview creation of one Billy invoice reminder without a mutation."""

        input = InvoiceReminderCreatePreviewInput(invoiceReminder=invoiceReminder)
        return write_protocol.preview(
            _invoice_reminder_create_specification(payload=input.invoiceReminder)
        )

    def api_invoice_reminders_create_execute(
        confirmation_ticket: str = Field(min_length=1),
    ) -> WriteExecutionResult | ToolError:
        """Execute the exact invoice-reminder creation in a ticket."""

        return write_protocol.execute(
            WriteExecuteInput(confirmation_ticket=confirmation_ticket),
            execute_tool_name="api_invoice_reminders_create_execute",
        )

    server.tool(
        name="api_invoice_reminders_create_preview",
        description="Preview creation of one Billy invoice reminder without a mutation.",
    )(api_invoice_reminders_create_preview)
    server.tool(
        name="api_invoice_reminders_create_execute",
        description="Execute a previewed Billy invoice-reminder creation with its ticket.",
    )(api_invoice_reminders_create_execute)


def _invoice_reminder_create_specification(*, payload: dict[str, JsonValue]) -> WriteOperationSpec:
    """Build the server-known shape for one singular invoice-reminder create."""

    return WriteOperationSpec(
        execute_tool_name="api_invoice_reminders_create_execute",
        method=WriteMethod.POST,
        collection_path="/invoiceReminders",
        singular_root="invoiceReminder",
        plural_root="invoiceReminders",
        additional_plural_roots=(),
        payload=payload,
        resource_id=None,
        organization_id=None,
        summary="Create one Billy invoice reminder.",
        expected_effect_state={"action": "create", "resource": "invoiceReminder"},
    )
