"""Ticketed UI product create preview and execute tools."""

from __future__ import annotations

from pathlib import Path
from typing import Final, Protocol

from fastmcp import FastMCP
from pydantic import BaseModel, ConfigDict, Field, JsonValue

from billy_mcp.browser import BrowserRuntime
from billy_mcp.models import StableErrorCode, ToolError
from billy_mcp.ui_writes.page_flow import FamilyWrite, perform_family_write
from billy_mcp.ui_writes.products_delete_chrome import product_persist_allowed
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
    organization_id: str = Field(min_length=1)
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
    """Bound product-create payload after the browser actor runs."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    canonical_request: dict[str, JsonValue]
    expected_effect_state: dict[str, JsonValue]
    summary: str
    submitted: bool = True


class ProductUiActor(Protocol):
    async def submit_create(
        self, request: dict[str, JsonValue], organization_id: str = ""
    ) -> object: ...


class BrowserProductSubmitter:
    def __init__(
        self,
        runtime: BrowserRuntime,
        readback_runtime: BrowserRuntime | None = None,
        delete_chrome_dump: Path | None = None,
    ) -> None:
        self._runtime = runtime
        self._readback_runtime = readback_runtime or runtime.independent_readback_runtime()
        self._delete_chrome_dump = delete_chrome_dump

    async def submit_create(
        self,
        request: dict[str, JsonValue],
        organization_id: str = "",
    ) -> object:
        if not product_persist_allowed(self._delete_chrome_dump):
            return ToolError(
                code=StableErrorCode.UI_CHANGED,
                message="Product create stays fail-closed until a unique UI delete path is proved.",
            )
        name = str(request.get("name") or "")
        return await perform_family_write(
            self._runtime,
            FamilyWrite(
                write_path="inventory",
                fills=(("name", name),),
                pre_clicks=("Opret produkt",),
                clicks=("Gem",),
                readback_path="inventory",
                readback_text=name,
            ),
            organization_id=organization_id,
            readback_runtime=self._readback_runtime,
        )


def register_ui_product_write_tools(
    server: FastMCP,
    protocol: UiWriteProtocol,
    actor: ProductUiActor | None = None,
    runtime: BrowserRuntime | None = None,
    readback_runtime: BrowserRuntime | None = None,
) -> None:
    """Register UI product create preview and execute tools."""

    if actor is not None:
        bound: ProductUiActor | None = actor
    elif runtime is not None:
        bound = BrowserProductSubmitter(runtime, readback_runtime)
    else:
        bound = None

    def ui_products_create_preview(
        name: str,
        organization_id: str = Field(min_length=1),
        account: str | None = None,
        salesTaxRuleset: str | None = None,
        unitPrice: float | None = None,
    ) -> UiWritePreviewResult | ToolError:
        """Issue a product-create ticket without submitting the Billy form."""

        preview_input = UiProductsCreatePreviewInput(
            name=name,
            organization_id=organization_id,
            account=account,
            salesTaxRuleset=salesTaxRuleset,
            unitPrice=unitPrice,
        )
        return protocol.preview(
            execute_tool_name=_EXECUTE_TOOL_NAME,
            organization_id=preview_input.organization_id,
            target="products",
            canonical_request=preview_input.canonical_request(),
            expected_effect_state={"action": "create", "resource": "product"},
            summary=_PREVIEW_SUMMARY,
        )

    async def ui_products_create_execute(
        confirmation_ticket: str = Field(min_length=1),
    ) -> UiProductsCreateExecuteResult | ToolError:
        """Execute the previewed product create through the browser actor."""

        prepared = protocol.consume(
            UiWriteExecuteInput(confirmation_ticket=confirmation_ticket),
            execute_tool_name=_EXECUTE_TOOL_NAME,
        )
        if isinstance(prepared, ToolError):
            return prepared
        if bound is None:
            return UiProductsCreateExecuteResult(
                canonical_request=prepared.canonical_request,
                expected_effect_state=prepared.expected_effect_state,
                summary=prepared.summary,
                submitted=False,
            )
        submitted = await bound.submit_create(
            prepared.canonical_request,
            organization_id=str(prepared.binding.organization_id or ""),
        )
        if isinstance(submitted, ToolError):
            return submitted
        return UiProductsCreateExecuteResult(
            canonical_request=prepared.canonical_request,
            expected_effect_state=prepared.expected_effect_state,
            summary=prepared.summary,
            submitted=True,
        )

    server.tool(
        name="ui_products_create_preview",
        description=(
            "Preview creation of one Billy product in the Lagermodul form without submitting."
        ),
    )(ui_products_create_preview)
    server.tool(
        name="ui_products_create_execute",
        description="Execute a previewed Billy product creation with its ticket.",
    )(ui_products_create_execute)
