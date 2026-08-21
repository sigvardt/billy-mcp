"""Offline FastMCP ticket contract for UI product create preview/execute."""

from __future__ import annotations

import asyncio
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import cast

import pytest
from fastmcp import FastMCP
from fastmcp.exceptions import ValidationError as FastMcpValidationError
from pydantic import ValidationError

from billy_mcp.confirmations import MAX_TICKET_TTL, ConfirmationStore
from billy_mcp.models import StableErrorCode
from billy_mcp.server import create_server
from billy_mcp.ui_writes.products import (
    UiProductsCreatePreviewInput,
    register_ui_product_write_tools,
)
from billy_mcp.ui_writes.protocol import UiWritePreviewResult, UiWriteProtocol


class Clock:
    """Mutable UTC clock for deterministic ticket expiry."""

    def __init__(self) -> None:
        self.now = datetime(2026, 8, 16, tzinfo=UTC)

    def __call__(self) -> datetime:
        return self.now


def make_server(protocol: UiWriteProtocol | None = None) -> FastMCP:
    """Register only the product UI write tools on a local FastMCP server."""

    server = FastMCP("ui-products-write-contract-test")
    register_ui_product_write_tools(server, protocol or UiWriteProtocol(ConfirmationStore()))
    return server


def call_tool(server: FastMCP, tool_name: str, arguments: dict[str, object]) -> dict[str, object]:
    """Call one typed tool and return its structured result payload."""

    result = asyncio.run(server.call_tool(tool_name, arguments))
    assert isinstance(result.structured_content, dict)
    structured_content = cast(dict[str, object], result.structured_content)
    payload = structured_content.get("result", structured_content)
    assert isinstance(payload, dict)
    return cast(dict[str, object], payload)


def test_create_server_registers_product_create_preview_and_execute() -> None:
    server = create_server()
    tools = {tool.name: tool for tool in asyncio.run(server.list_tools())}

    assert "ui_products_create_preview" in tools
    assert "ui_products_create_execute" in tools
    assert "ui_products_delete_preview" in tools
    assert "ui_products_delete_execute" in tools
    preview = tools["ui_products_create_preview"].parameters
    execute = tools["ui_products_create_execute"].parameters
    delete_preview = tools["ui_products_delete_preview"].parameters
    delete_execute = tools["ui_products_delete_execute"].parameters
    preview_properties = cast(dict[str, object], preview["properties"])
    execute_properties = cast(dict[str, object], execute["properties"])
    delete_preview_properties = cast(dict[str, object], delete_preview["properties"])
    delete_execute_properties = cast(dict[str, object], delete_execute["properties"])
    assert preview["additionalProperties"] is False
    assert execute["additionalProperties"] is False
    assert set(preview_properties) == {
        "name",
        "organization_id",
        "account",
        "salesTaxRuleset",
        "unitPrice",
    }
    assert set(execute_properties) == {"confirmation_ticket"}
    assert set(delete_preview_properties) == {"unique_tag", "organization_id", "id"}
    assert set(delete_execute_properties) == {"confirmation_ticket"}
    ticket = execute_properties["confirmation_ticket"]
    assert isinstance(ticket, dict)
    assert ticket["minLength"] == 1


def test_create_preview_rejects_unpriced_product() -> None:
    """Owner 56354201: create preview must reject a missing or non-positive unitPrice."""

    server = make_server()
    unpriced: dict[str, object] = {
        "name": "MCP-UI-PRD-UNPRICED",
        "organization_id": "org-test",
    }
    with pytest.raises(ValidationError):
        UiProductsCreatePreviewInput.model_validate(unpriced)
    with pytest.raises(ValidationError):
        UiProductsCreatePreviewInput.model_validate({**unpriced, "unitPrice": 0})
    with pytest.raises(ValidationError):
        UiProductsCreatePreviewInput.model_validate({**unpriced, "unitPrice": -1})

    try:
        missing = call_tool(server, "ui_products_create_preview", unpriced)
    except (ValidationError, FastMcpValidationError, TypeError, ValueError):
        missing = {"code": StableErrorCode.VALIDATION_ERROR}
    assert missing.get("code") == StableErrorCode.VALIDATION_ERROR
    assert not missing.get("confirmation_ticket")


def test_submit_create_does_not_use_delete_chrome_dump_gate() -> None:
    """Owner 56354201: persist is not blocked by proved_delete_path=none."""

    from billy_mcp.ui_writes import products

    body = Path(products.__file__).read_text(encoding="utf-8")
    assert "product_persist_allowed" not in body
    assert "unique UI delete path" not in body


def test_preview_returns_ticket_and_does_not_submit() -> None:
    server = make_server()

    preview = call_tool(
        server,
        "ui_products_create_preview",
        {
            "name": "MCP-TEST-PRODUCT-OFFLINE-1",
            "unitPrice": 1.0,
            "organization_id": "org-test",
        },
    )

    assert preview["confirmation_ticket"]
    assert preview["canonical_request"] == {
        "name": "MCP-TEST-PRODUCT-OFFLINE-1",
        "unitPrice": 1.0,
    }
    assert preview["expected_effect_state"] == {"action": "create", "resource": "product"}
    assert "submit" not in str(preview["summary"]).lower()


def test_preview_binds_optional_form_fields() -> None:
    server = make_server()

    preview = call_tool(
        server,
        "ui_products_create_preview",
        {
            "name": "MCP-TEST-PRODUCT-OFFLINE-FIELDS",
            "account": "1000",
            "salesTaxRuleset": "ruleset-1",
            "unitPrice": 12.5,
            "organization_id": "org-test",
        },
    )

    assert preview["canonical_request"] == {
        "name": "MCP-TEST-PRODUCT-OFFLINE-FIELDS",
        "account": "1000",
        "salesTaxRuleset": "ruleset-1",
        "unitPrice": 12.5,
    }


def test_preview_input_rejects_empty_name_and_unknown_fields() -> None:
    with pytest.raises(ValidationError):
        UiProductsCreatePreviewInput(name="", organization_id="org-test", unitPrice=1.0)
    with pytest.raises(ValidationError):
        UiProductsCreatePreviewInput.model_validate(
            {"name": "MCP-TEST-PRODUCT-OFFLINE-X", "unexpected": True}
        )


def test_execute_consumes_ticket_once_and_echoes_previewed_name() -> None:
    server = make_server()
    preview = call_tool(
        server,
        "ui_products_create_preview",
        {
            "name": "MCP-TEST-PRODUCT-OFFLINE-2",
            "unitPrice": 1.0,
            "organization_id": "org-test",
        },
    )

    first = call_tool(
        server,
        "ui_products_create_execute",
        {"confirmation_ticket": preview["confirmation_ticket"]},
    )
    replay = call_tool(
        server,
        "ui_products_create_execute",
        {"confirmation_ticket": preview["confirmation_ticket"]},
    )

    request = first["canonical_request"]
    assert isinstance(request, dict)
    assert request["name"] == "MCP-TEST-PRODUCT-OFFLINE-2"
    assert replay["code"] == StableErrorCode.CONFIRMATION_CONSUMED


def test_execute_rejects_expired_ticket() -> None:
    clock = Clock()
    server = make_server(UiWriteProtocol(ConfirmationStore(clock=clock)))
    preview = call_tool(
        server,
        "ui_products_create_preview",
        {
            "name": "MCP-TEST-PRODUCT-OFFLINE-3",
            "unitPrice": 1.0,
            "organization_id": "org-test",
        },
    )

    clock.now = clock.now + MAX_TICKET_TTL + timedelta(seconds=1)
    expired = call_tool(
        server,
        "ui_products_create_execute",
        {"confirmation_ticket": preview["confirmation_ticket"]},
    )

    assert expired["code"] == StableErrorCode.CONFIRMATION_EXPIRED


def test_execute_rejects_ticket_bound_to_another_tool() -> None:
    protocol = UiWriteProtocol(ConfirmationStore())
    server = make_server(protocol)
    foreign = protocol.preview(
        execute_tool_name="ui_bills_create_execute",
        organization_id="org-test",
        target="bills",
        canonical_request={"name": "not-a-product"},
        expected_effect_state={"action": "create", "resource": "bill"},
        summary="Create one Billy bill in the interface.",
    )
    assert isinstance(foreign, UiWritePreviewResult)

    mismatch = call_tool(
        server,
        "ui_products_create_execute",
        {"confirmation_ticket": foreign.confirmation_ticket},
    )

    assert mismatch["code"] == StableErrorCode.CONFIRMATION_MISMATCH


def test_delete_preview_returns_ticket_and_execute_consumes_once() -> None:
    server = make_server()
    preview = call_tool(
        server,
        "ui_products_delete_preview",
        {"unique_tag": "MCP-UI-PRD-DEL1", "organization_id": "org-test"},
    )

    assert preview["confirmation_ticket"]
    assert preview["canonical_request"] == {"unique_tag": "MCP-UI-PRD-DEL1"}
    assert preview["expected_effect_state"] == {"action": "delete", "resource": "product"}
    assert "submit" not in str(preview["summary"]).lower()

    first = call_tool(
        server,
        "ui_products_delete_execute",
        {"confirmation_ticket": preview["confirmation_ticket"]},
    )
    replay = call_tool(
        server,
        "ui_products_delete_execute",
        {"confirmation_ticket": preview["confirmation_ticket"]},
    )

    request = first["canonical_request"]
    assert isinstance(request, dict)
    assert request["unique_tag"] == "MCP-UI-PRD-DEL1"
    assert first["submitted"] is False
    assert replay["code"] == StableErrorCode.CONFIRMATION_CONSUMED
