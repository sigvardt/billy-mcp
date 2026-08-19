"""Ticketed UI product delete preview and execute tools."""

from __future__ import annotations

from typing import Final, Protocol

from fastmcp import FastMCP
from pydantic import BaseModel, ConfigDict, Field, JsonValue

from billy_mcp.browser import BrowserRuntime
from billy_mcp.models import StableErrorCode, ToolError
from billy_mcp.ui_writes.page_flow import require_matching_org_slug
from billy_mcp.ui_writes.products_delete_row import (
    LIST_PATHS,
    delete_tagged_row,
    prove_unfiltered_row_absent,
)
from billy_mcp.ui_writes.protocol import (
    UiWriteExecuteInput,
    UiWritePreviewResult,
    UiWriteProtocol,
)

_EXECUTE_TOOL_NAME: Final = "ui_products_delete_execute"
_PREVIEW_SUMMARY: Final = "Preview deletion of one Billy product in the interface."


class UiProductsDeletePreviewInput(BaseModel):
    """Strict fields for a product-delete preview. Does not submit."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    unique_tag: str = Field(min_length=1)
    organization_id: str = Field(min_length=1)
    id: str | None = None

    def canonical_request(self) -> dict[str, JsonValue]:
        """Return the bound delete identity."""

        payload: dict[str, JsonValue] = {"unique_tag": self.unique_tag}
        if self.id is not None:
            payload["id"] = self.id
        return payload


class UiProductsDeleteExecuteResult(BaseModel):
    """Bound product-delete payload after the browser actor runs."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    canonical_request: dict[str, JsonValue]
    expected_effect_state: dict[str, JsonValue]
    summary: str
    submitted: bool = True


class ProductDeleteActor(Protocol):
    async def submit_delete(
        self, request: dict[str, JsonValue], organization_id: str = ""
    ) -> object: ...


class BrowserProductDeleter:
    def __init__(
        self,
        runtime: BrowserRuntime,
        readback_runtime: BrowserRuntime | None = None,
    ) -> None:
        self._runtime = runtime
        self._readback_runtime = readback_runtime or runtime.independent_readback_runtime()

    async def submit_delete(
        self,
        request: dict[str, JsonValue],
        organization_id: str = "",
    ) -> object:
        tag = str(request.get("unique_tag") or "")
        bound = organization_id.strip()
        if not tag or not bound:
            return ToolError(
                code=StableErrorCode.VALIDATION_ERROR,
                message="Product delete requires a unique tag and organisation.",
            )
        try:
            context = await self._runtime.start()
            page = await context.new_page()
        except (OSError, RuntimeError, AssertionError):
            return ToolError(
                code=StableErrorCode.BILLY_ERROR,
                message="Billy interface write could not start the browser.",
            )
        try:
            slug = await require_matching_org_slug(page, bound, "products")
            if isinstance(slug, ToolError):
                return slug
            clicked = False
            for path in LIST_PATHS:
                if await delete_tagged_row(page, organization_id=slug, path=path, tag=tag):
                    clicked = True
                    break
            if not clicked:
                already_gone = await prove_unfiltered_row_absent(
                    self._readback_runtime,
                    organization_id=bound,
                    tag=tag,
                )
                if already_gone is None:
                    return None
                return ToolError(
                    code=StableErrorCode.UI_CHANGED,
                    message="Billy product row delete-icon is not visible.",
                )
        finally:
            await page.close()
        return await prove_unfiltered_row_absent(
            self._readback_runtime,
            organization_id=bound,
            tag=tag,
        )


def register_ui_product_delete_tools(
    server: FastMCP,
    protocol: UiWriteProtocol,
    runtime: BrowserRuntime | None = None,
    readback_runtime: BrowserRuntime | None = None,
) -> None:
    """Register UI product delete preview and execute tools."""

    bound: ProductDeleteActor | None = None
    if runtime is not None:
        bound = BrowserProductDeleter(runtime, readback_runtime)

    def ui_products_delete_preview(
        unique_tag: str = Field(min_length=1),
        organization_id: str = Field(min_length=1),
        id: str | None = None,
    ) -> UiWritePreviewResult | ToolError:
        """Issue a product-delete ticket without submitting the Billy form."""

        preview_input = UiProductsDeletePreviewInput(
            unique_tag=unique_tag,
            organization_id=organization_id,
            id=id,
        )
        return protocol.preview(
            execute_tool_name=_EXECUTE_TOOL_NAME,
            organization_id=preview_input.organization_id,
            target="products",
            canonical_request=preview_input.canonical_request(),
            expected_effect_state={"action": "delete", "resource": "product"},
            summary=_PREVIEW_SUMMARY,
        )

    async def ui_products_delete_execute(
        confirmation_ticket: str = Field(min_length=1),
    ) -> UiProductsDeleteExecuteResult | ToolError:
        """Execute the previewed product delete through the browser actor."""

        prepared = protocol.consume(
            UiWriteExecuteInput(confirmation_ticket=confirmation_ticket),
            execute_tool_name=_EXECUTE_TOOL_NAME,
        )
        if isinstance(prepared, ToolError):
            return prepared
        if bound is None:
            return UiProductsDeleteExecuteResult(
                canonical_request=prepared.canonical_request,
                expected_effect_state=prepared.expected_effect_state,
                summary=prepared.summary,
                submitted=False,
            )
        submitted = await bound.submit_delete(
            prepared.canonical_request,
            organization_id=str(prepared.binding.organization_id or ""),
        )
        if isinstance(submitted, ToolError):
            return submitted
        return UiProductsDeleteExecuteResult(
            canonical_request=prepared.canonical_request,
            expected_effect_state=prepared.expected_effect_state,
            summary=prepared.summary,
            submitted=True,
        )

    server.tool(
        name="ui_products_delete_preview",
        description="Preview deletion of one Billy product without submitting.",
    )(ui_products_delete_preview)
    server.tool(
        name="ui_products_delete_execute",
        description="Execute a previewed Billy product deletion with its ticket.",
    )(ui_products_delete_execute)
