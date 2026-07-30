"""Ticketed FastMCP tools for singular Billy contact-balance-payment writes."""

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


class _ContactBalancePaymentWritePreviewInput(BaseModel):
    """Forbid undeclared outer fields while preserving opaque payment JSON."""

    model_config = ConfigDict(extra="forbid")


class ContactBalancePaymentCreatePreviewInput(_ContactBalancePaymentWritePreviewInput):
    """Input for previewing creation of one Billy contact balance payment."""

    contactBalancePayment: dict[str, JsonValue]


class ContactBalancePaymentUpdatePreviewInput(_ContactBalancePaymentWritePreviewInput):
    """Input for previewing an update to one Billy contact balance payment."""

    id: str = Field(min_length=1)
    contactBalancePayment: dict[str, JsonValue]

    @model_validator(mode="after")
    def contact_balance_payment_id_matches_route_id(
        self,
    ) -> ContactBalancePaymentUpdatePreviewInput:
        """Keep an optional body identifier aligned with the route."""

        if "id" in self.contactBalancePayment and self.contactBalancePayment["id"] != self.id:
            raise ValueError("contactBalancePayment.id must match id")
        return self


def register_contact_balance_payment_write_tools(
    server: FastMCP,
    client: BillyHttpClient,
    write_protocol: WriteProtocolService,
) -> None:
    """Register exactly the four frozen contact-balance-payment create/update tools."""

    del client

    def api_contact_balance_payments_create_preview(
        contactBalancePayment: dict[str, JsonValue],
    ) -> WritePreviewResult:
        """Preview creation of one Billy contact balance payment without a mutation."""

        input = ContactBalancePaymentCreatePreviewInput(contactBalancePayment=contactBalancePayment)
        return write_protocol.preview(
            _contact_balance_payment_specification(
                execute_tool_name="api_contact_balance_payments_create_execute",
                method=WriteMethod.POST,
                payload=input.contactBalancePayment,
                resource_id=None,
            )
        )

    def api_contact_balance_payments_create_execute(
        confirmation_ticket: str = Field(min_length=1),
    ) -> WriteExecutionResult | ToolError:
        """Execute the exact contact-balance-payment creation in a ticket."""

        return write_protocol.execute(
            WriteExecuteInput(confirmation_ticket=confirmation_ticket),
            execute_tool_name="api_contact_balance_payments_create_execute",
        )

    def api_contact_balance_payments_update_preview(
        contactBalancePayment: dict[str, JsonValue],
        id: str = Field(min_length=1),
    ) -> WritePreviewResult:
        """Preview an update to one Billy contact balance payment without a mutation."""

        input = ContactBalancePaymentUpdatePreviewInput(
            id=id, contactBalancePayment=contactBalancePayment
        )
        return write_protocol.preview(
            _contact_balance_payment_specification(
                execute_tool_name="api_contact_balance_payments_update_execute",
                method=WriteMethod.PUT,
                payload=input.contactBalancePayment,
                resource_id=input.id,
            )
        )

    def api_contact_balance_payments_update_execute(
        confirmation_ticket: str = Field(min_length=1),
    ) -> WriteExecutionResult | ToolError:
        """Execute the exact contact-balance-payment update in a ticket."""

        return write_protocol.execute(
            WriteExecuteInput(confirmation_ticket=confirmation_ticket),
            execute_tool_name="api_contact_balance_payments_update_execute",
        )

    server.tool(
        name="api_contact_balance_payments_create_preview",
        description="Preview creation of one Billy contact balance payment without a mutation.",
    )(api_contact_balance_payments_create_preview)
    server.tool(
        name="api_contact_balance_payments_create_execute",
        description="Execute a previewed Billy contact-balance-payment creation with its ticket.",
    )(api_contact_balance_payments_create_execute)
    server.tool(
        name="api_contact_balance_payments_update_preview",
        description="Preview an update to one Billy contact balance payment without a mutation.",
    )(api_contact_balance_payments_update_preview)
    server.tool(
        name="api_contact_balance_payments_update_execute",
        description="Execute a previewed Billy contact-balance-payment update with its ticket.",
    )(api_contact_balance_payments_update_execute)


def _contact_balance_payment_specification(
    *,
    execute_tool_name: str,
    method: WriteMethod,
    payload: dict[str, JsonValue],
    resource_id: str | None,
) -> WriteOperationSpec:
    """Build the server-known shape for one singular contact-balance-payment write."""

    action = {WriteMethod.POST: "create", WriteMethod.PUT: "update"}[method]
    expected_effect_state: dict[str, JsonValue] = {
        "action": action,
        "resource": "contactBalancePayment",
    }
    if resource_id is not None:
        expected_effect_state["id"] = resource_id
    return WriteOperationSpec(
        execute_tool_name=execute_tool_name,
        method=method,
        collection_path="/contactBalancePayments",
        singular_root="contactBalancePayment",
        plural_root="contactBalancePayments",
        additional_plural_roots=(),
        payload=payload,
        resource_id=resource_id,
        organization_id=None,
        summary=f"{action.capitalize()} one Billy contact balance payment.",
        expected_effect_state=expected_effect_state,
    )
