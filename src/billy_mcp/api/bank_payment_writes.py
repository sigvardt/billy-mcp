"""Ticketed FastMCP tools for singular Billy bank-payment writes."""

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


class _BankPaymentWritePreviewInput(BaseModel):
    """Forbid undeclared outer fields while preserving opaque bank-payment JSON."""

    model_config = ConfigDict(extra="forbid")


class BankPaymentCreatePreviewInput(_BankPaymentWritePreviewInput):
    """Input for previewing creation of one Billy bank payment."""

    bankPayment: dict[str, JsonValue]


class BankPaymentUpdatePreviewInput(_BankPaymentWritePreviewInput):
    """Input for previewing a partial update to one Billy bank payment."""

    id: str = Field(min_length=1)
    bankPayment: dict[str, JsonValue]

    @model_validator(mode="after")
    def bank_payment_id_matches_route_id(self) -> BankPaymentUpdatePreviewInput:
        """Keep an optional bank-payment body identifier aligned with the route."""

        if "id" in self.bankPayment and self.bankPayment["id"] != self.id:
            raise ValueError("bankPayment.id must match id")
        return self


class BankPaymentDeletePreviewInput(_BankPaymentWritePreviewInput):
    """Input for previewing deletion of one Billy bank payment."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    id: str = Field(min_length=1)


def register_bank_payment_write_tools(
    server: FastMCP,
    client: BillyHttpClient,
    write_protocol: WriteProtocolService,
) -> None:
    """Register ticketed create, update, and delete tools for bank payments."""

    del client

    def api_bank_payments_create_preview(
        bankPayment: dict[str, JsonValue],
    ) -> WritePreviewResult:
        """Preview creation of one Billy bank payment without a mutation."""

        input = BankPaymentCreatePreviewInput(bankPayment=bankPayment)
        return write_protocol.preview(
            _bank_payment_specification(
                execute_tool_name="api_bank_payments_create_execute",
                method=WriteMethod.POST,
                payload=input.bankPayment,
                resource_id=None,
            )
        )

    def api_bank_payments_create_execute(
        confirmation_ticket: str = Field(min_length=1),
    ) -> WriteExecutionResult | ToolError:
        """Execute the exact bank-payment creation in a confirmation ticket."""

        return write_protocol.execute(
            WriteExecuteInput(confirmation_ticket=confirmation_ticket),
            execute_tool_name="api_bank_payments_create_execute",
        )

    def api_bank_payments_update_preview(
        bankPayment: dict[str, JsonValue],
        id: str = Field(min_length=1),
    ) -> WritePreviewResult:
        """Preview a partial update to one Billy bank payment without a mutation."""

        input = BankPaymentUpdatePreviewInput(id=id, bankPayment=bankPayment)
        return write_protocol.preview(
            _bank_payment_specification(
                execute_tool_name="api_bank_payments_update_execute",
                method=WriteMethod.PUT,
                payload=input.bankPayment,
                resource_id=input.id,
            )
        )

    def api_bank_payments_update_execute(
        confirmation_ticket: str = Field(min_length=1),
    ) -> WriteExecutionResult | ToolError:
        """Execute the exact bank-payment update in a confirmation ticket."""

        return write_protocol.execute(
            WriteExecuteInput(confirmation_ticket=confirmation_ticket),
            execute_tool_name="api_bank_payments_update_execute",
        )

    def api_bank_payments_delete_preview(id: str = Field(min_length=1)) -> WritePreviewResult:
        """Preview deletion of one Billy bank payment without a mutation."""

        input = BankPaymentDeletePreviewInput(id=id)
        return write_protocol.preview(
            _bank_payment_specification(
                execute_tool_name="api_bank_payments_delete_execute",
                method=WriteMethod.DELETE,
                payload=None,
                resource_id=input.id,
            )
        )

    def api_bank_payments_delete_execute(
        confirmation_ticket: str = Field(min_length=1),
    ) -> WriteExecutionResult | ToolError:
        """Execute the exact bank-payment deletion in a confirmation ticket."""

        return write_protocol.execute(
            WriteExecuteInput(confirmation_ticket=confirmation_ticket),
            execute_tool_name="api_bank_payments_delete_execute",
        )

    server.tool(
        name="api_bank_payments_create_preview",
        description="Preview creation of one Billy bank payment without a mutation.",
    )(api_bank_payments_create_preview)
    server.tool(
        name="api_bank_payments_create_execute",
        description="Execute a previewed Billy bank-payment creation with its ticket.",
    )(api_bank_payments_create_execute)
    server.tool(
        name="api_bank_payments_update_preview",
        description="Preview a partial update to one Billy bank payment without a mutation.",
    )(api_bank_payments_update_preview)
    server.tool(
        name="api_bank_payments_update_execute",
        description="Execute a previewed Billy bank-payment update with its ticket.",
    )(api_bank_payments_update_execute)
    server.tool(
        name="api_bank_payments_delete_preview",
        description="Preview deletion of one Billy bank payment without a mutation.",
    )(api_bank_payments_delete_preview)
    server.tool(
        name="api_bank_payments_delete_execute",
        description="Execute a previewed Billy bank-payment deletion with its ticket.",
    )(api_bank_payments_delete_execute)


def _bank_payment_specification(
    *,
    execute_tool_name: str,
    method: WriteMethod,
    payload: dict[str, JsonValue] | None,
    resource_id: str | None,
) -> WriteOperationSpec:
    """Build the server-known operation shape for one singular bank-payment write."""

    action = {
        WriteMethod.POST: "create",
        WriteMethod.PUT: "update",
        WriteMethod.DELETE: "delete",
    }[method]
    expected_effect_state: dict[str, JsonValue] = {
        "action": action,
        "resource": "bankPayment",
    }
    if resource_id is not None:
        expected_effect_state["id"] = resource_id
    return WriteOperationSpec(
        execute_tool_name=execute_tool_name,
        method=method,
        collection_path="/bankPayments",
        singular_root="bankPayment",
        plural_root="bankPayments",
        additional_plural_roots=(),
        payload=payload,
        resource_id=resource_id,
        organization_id=None,
        summary=f"{action.capitalize()} one Billy bank payment.",
        expected_effect_state=expected_effect_state,
    )
