"""Ticketed FastMCP tools for documented singular association writes."""

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


class _InvoiceReminderAssociationWritePreviewInput(BaseModel):
    """Forbid undeclared fields around the documented association payload."""

    model_config = ConfigDict(extra="forbid", frozen=True)


class InvoiceReminderAssociationPayload(BaseModel):
    """Writable `#v2invoicereminderassociations` fields. `lateFee` is readonly."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    reminder: str = Field(min_length=1)
    invoice: str = Field(min_length=1)


class InvoiceReminderAssociationCreatePreviewInput(_InvoiceReminderAssociationWritePreviewInput):
    """Input for previewing creation of one invoice reminder association."""

    invoiceReminderAssociation: InvoiceReminderAssociationPayload


class InvoiceReminderAssociationUpdatePreviewInput(_InvoiceReminderAssociationWritePreviewInput):
    """Input for previewing an update to one invoice reminder association."""

    id: str = Field(min_length=1)
    invoiceReminderAssociation: InvoiceReminderAssociationPayload


class InvoiceReminderAssociationDeletePreviewInput(_InvoiceReminderAssociationWritePreviewInput):
    """Input for previewing deletion of one invoice reminder association."""

    id: str = Field(min_length=1)


def _association_payload(model: InvoiceReminderAssociationPayload) -> dict[str, JsonValue]:
    """Dump the required documented belongs-to identifiers for the ticketed body."""

    dumped = model.model_dump()
    return {str(key): value for key, value in dumped.items()}


def register_invoice_reminder_association_write_tools(
    server: FastMCP,
    client: BillyHttpClient,
    write_protocol: WriteProtocolService,
) -> None:
    """Register the six frozen ticketed association write tools."""

    del client

    def api_invoice_reminder_associations_create_preview(
        invoiceReminderAssociation: InvoiceReminderAssociationPayload,
    ) -> WritePreviewResult:
        """Preview creation of one association without sending a mutation."""

        input = InvoiceReminderAssociationCreatePreviewInput(
            invoiceReminderAssociation=invoiceReminderAssociation
        )
        return write_protocol.preview(
            _association_spec(
                execute_tool_name="api_invoice_reminder_associations_create_execute",
                method=WriteMethod.POST,
                payload=_association_payload(input.invoiceReminderAssociation),
                resource_id=None,
                summary="Create one Billy invoice reminder association.",
                expected_effect_state={
                    "action": "create",
                    "resource": "invoiceReminderAssociation",
                },
            )
        )

    def api_invoice_reminder_associations_create_execute(
        confirmation_ticket: str = Field(min_length=1),
    ) -> WriteExecutionResult | ToolError:
        """Execute the exact association creation represented by a confirmation ticket."""

        return write_protocol.execute(
            WriteExecuteInput(confirmation_ticket=confirmation_ticket),
            execute_tool_name="api_invoice_reminder_associations_create_execute",
        )

    def api_invoice_reminder_associations_update_preview(
        invoiceReminderAssociation: InvoiceReminderAssociationPayload,
        id: str = Field(min_length=1),
    ) -> WritePreviewResult:
        """Preview an update to one association without sending a mutation."""

        input = InvoiceReminderAssociationUpdatePreviewInput(
            id=id, invoiceReminderAssociation=invoiceReminderAssociation
        )
        return write_protocol.preview(
            _association_spec(
                execute_tool_name="api_invoice_reminder_associations_update_execute",
                method=WriteMethod.PUT,
                payload=_association_payload(input.invoiceReminderAssociation),
                resource_id=input.id,
                summary="Update one Billy invoice reminder association.",
                expected_effect_state={
                    "action": "update",
                    "resource": "invoiceReminderAssociation",
                    "id": input.id,
                },
            )
        )

    def api_invoice_reminder_associations_update_execute(
        confirmation_ticket: str = Field(min_length=1),
    ) -> WriteExecutionResult | ToolError:
        """Execute the exact association update represented by a confirmation ticket."""

        return write_protocol.execute(
            WriteExecuteInput(confirmation_ticket=confirmation_ticket),
            execute_tool_name="api_invoice_reminder_associations_update_execute",
        )

    def api_invoice_reminder_associations_delete_preview(
        id: str = Field(min_length=1),
    ) -> WritePreviewResult:
        """Preview deletion of one association without sending a mutation."""

        input = InvoiceReminderAssociationDeletePreviewInput(id=id)
        return write_protocol.preview(
            _association_spec(
                execute_tool_name="api_invoice_reminder_associations_delete_execute",
                method=WriteMethod.DELETE,
                payload=None,
                resource_id=input.id,
                summary="Delete one Billy invoice reminder association.",
                expected_effect_state={
                    "action": "delete",
                    "resource": "invoiceReminderAssociation",
                    "id": input.id,
                },
            )
        )

    def api_invoice_reminder_associations_delete_execute(
        confirmation_ticket: str = Field(min_length=1),
    ) -> WriteExecutionResult | ToolError:
        """Execute the exact association deletion represented by a confirmation ticket."""

        return write_protocol.execute(
            WriteExecuteInput(confirmation_ticket=confirmation_ticket),
            execute_tool_name="api_invoice_reminder_associations_delete_execute",
        )

    server.tool(
        name="api_invoice_reminder_associations_create_preview",
        description=(
            "Preview creation of one Billy invoice reminder association without a mutation."
        ),
    )(api_invoice_reminder_associations_create_preview)
    server.tool(
        name="api_invoice_reminder_associations_create_execute",
        description=(
            "Execute a previewed Billy invoice reminder association creation with its ticket."
        ),
    )(api_invoice_reminder_associations_create_execute)
    server.tool(
        name="api_invoice_reminder_associations_update_preview",
        description=(
            "Preview an update to one Billy invoice reminder association without a mutation."
        ),
    )(api_invoice_reminder_associations_update_preview)
    server.tool(
        name="api_invoice_reminder_associations_update_execute",
        description=(
            "Execute a previewed Billy invoice reminder association update with its ticket."
        ),
    )(api_invoice_reminder_associations_update_execute)
    server.tool(
        name="api_invoice_reminder_associations_delete_preview",
        description=(
            "Preview deletion of one Billy invoice reminder association without a mutation."
        ),
    )(api_invoice_reminder_associations_delete_preview)
    server.tool(
        name="api_invoice_reminder_associations_delete_execute",
        description=(
            "Execute a previewed Billy invoice reminder association deletion with its ticket."
        ),
    )(api_invoice_reminder_associations_delete_execute)


def _association_spec(
    *,
    execute_tool_name: str,
    method: WriteMethod,
    payload: dict[str, JsonValue] | None,
    resource_id: str | None,
    summary: str,
    expected_effect_state: dict[str, JsonValue],
) -> WriteOperationSpec:
    """Build the server-known operation shape for one association write preview."""

    return WriteOperationSpec(
        execute_tool_name=execute_tool_name,
        method=method,
        collection_path="/invoiceReminderAssociations",
        singular_root="invoiceReminderAssociation",
        plural_root="invoiceReminderAssociations",
        additional_plural_roots=(),
        payload=payload,
        resource_id=resource_id,
        organization_id=None,
        summary=summary,
        expected_effect_state=expected_effect_state,
    )
