"""Ticketed UI product create preview and execute tools."""

from __future__ import annotations

from typing import Final

from fastmcp import FastMCP
from pydantic import BaseModel, ConfigDict, Field, JsonValue

from billy_mcp.models import ToolError
from billy_mcp.ui_writes.protocol import (
    UiWriteExecuteInput,
    UiWritePreviewResult,
    UiWriteProtocol,
)

_EXECUTE_TOOL_NAME: Final = "ui_products_create_execute"
_PREVIEW_SUMMARY: Final = "Preview creation of one Billy product in the interface."


class UiProductsCreatePreviewInput(BaseModel):
    """Strict form fields for a product-create preview. Does not submit."""

    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
        validate_by_alias=True,
        validate_by_name=True,
    )

    name: str = Field(min_length=1)
    account: str | None = None
    sales_tax_ruleset: str | None = Field(default=None, alias="salesTaxRuleset")
    unit_price: float | None = Field(default=None, alias="unitPrice")

    def canonical_request(self) -> dict[str, JsonValue]:
        """Return the bound form fields, omitting unset optionals."""

        payload: dict[str, JsonValue] = {"name": self.name}
        if self.account is not None:
            payload["account"] = self.account
        if self.sales_tax_ruleset is not None:
            payload["salesTaxRuleset"] = self.sales_tax_ruleset
        if self.unit_price is not None:
            payload["unitPrice"] = self.unit_price
        return payload


class UiProductsCreateExecuteResult(BaseModel):
    """Bound product-create payload restored from a consumed ticket."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    canonical_request: dict[str, JsonValue]
    expected_effect_state: dict[str, JsonValue]
    summary: str


def register_ui_product_write_tools(server: FastMCP, protocol: UiWriteProtocol) -> None:
    """Register UI product create preview and execute tools."""

    def ui_products_create_preview(
        name: str,
        account: str | None = None,
        salesTaxRuleset: str | None = None,
        unitPrice: float | None = None,
    ) -> UiWritePreviewResult:
        """Issue a product-create ticket without submitting the Billy form."""

        preview_input = UiProductsCreatePreviewInput(
            name=name,
            account=account,
            salesTaxRuleset=salesTaxRuleset,
            unitPrice=unitPrice,
        )
        return protocol.preview(
            execute_tool_name=_EXECUTE_TOOL_NAME,
            organization_id=None,
            target="products",
            canonical_request=preview_input.canonical_request(),
            expected_effect_state={"action": "create", "resource": "product"},
            summary=_PREVIEW_SUMMARY,
        )

    def ui_products_create_execute(
        confirmation_ticket: str = Field(min_length=1),
    ) -> UiProductsCreateExecuteResult | ToolError:
        """Consume the product-create ticket. Does not call the Billy HTTP API."""

        prepared = protocol.consume(
            UiWriteExecuteInput(confirmation_ticket=confirmation_ticket),
            execute_tool_name=_EXECUTE_TOOL_NAME,
        )
        if isinstance(prepared, ToolError):
            return prepared
        return UiProductsCreateExecuteResult(
            canonical_request=prepared.canonical_request,
            expected_effect_state=prepared.expected_effect_state,
            summary=prepared.summary,
        )

    server.tool(
        name="ui_products_create_preview",
        description=(
            "Preview creation of one Billy product in the Lagermodul form "
            "without submitting."
        ),
    )(ui_products_create_preview)
    server.tool(
        name="ui_products_create_execute",
        description="Execute a previewed Billy product creation with its ticket.",
    )(ui_products_create_execute)
