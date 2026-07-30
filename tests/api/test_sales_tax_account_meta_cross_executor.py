"""Integration tests for root-shared sales-tax account and meta-field tickets."""

from __future__ import annotations

import asyncio
from collections.abc import Mapping
from typing import cast

from fastmcp import FastMCP
from pytest import MonkeyPatch

from billy_mcp.client import BillyHttpClient, BillyResponse
from billy_mcp.models import StableErrorCode
from billy_mcp.server import create_server


def call_tool(server: FastMCP, tool_name: str, arguments: dict[str, object]) -> dict[str, object]:
    """Call one typed root-server MCP tool and return its structured payload."""

    result = asyncio.run(server.call_tool(tool_name, arguments))
    structured_content = result.structured_content
    assert isinstance(structured_content, dict)
    payload = structured_content.get("result", structured_content)
    assert isinstance(payload, dict)
    return cast(dict[str, object], payload)


def test_root_shared_service_rejects_same_and_cross_resource_executors_without_consuming_tickets(
    monkeypatch: MonkeyPatch,
) -> None:
    """Each ticket remains usable only by its exact executor in root's one store."""

    requests: list[tuple[str, str, object | None]] = []

    def fake_request(
        self: BillyHttpClient,
        method: str,
        path: str,
        *,
        params: Mapping[str, str | int | float | bool] | None = None,
        json_body: object | None = None,
    ) -> BillyResponse:
        del self, params
        requests.append((method, path, json_body))
        if path == "/salesTaxAccounts":
            return BillyResponse(200, {"salesTaxAccounts": [{"id": "account-1"}]})
        if path == "/salesTaxMetaFields":
            return BillyResponse(200, {"salesTaxMetaFields": [{"id": "meta-1"}]})
        raise AssertionError(f"unexpected request: {method} {path}")

    monkeypatch.setattr(BillyHttpClient, "request", fake_request)
    server = create_server()

    account_preview = call_tool(
        server,
        "api_sales_tax_accounts_create_preview",
        {"salesTaxAccount": {"type": "opaque"}},
    )
    same_resource_mismatch = call_tool(
        server,
        "api_sales_tax_accounts_delete_execute",
        {"confirmation_ticket": account_preview["confirmation_ticket"]},
    )
    cross_resource_mismatch = call_tool(
        server,
        "api_sales_tax_meta_fields_create_execute",
        {"confirmation_ticket": account_preview["confirmation_ticket"]},
    )
    assert same_resource_mismatch["code"] == StableErrorCode.CONFIRMATION_MISMATCH
    assert cross_resource_mismatch["code"] == StableErrorCode.CONFIRMATION_MISMATCH
    assert requests == []

    account_execution = call_tool(
        server,
        "api_sales_tax_accounts_create_execute",
        {"confirmation_ticket": account_preview["confirmation_ticket"]},
    )
    assert account_execution["changed_records"] == {"salesTaxAccounts": [{"id": "account-1"}]}
    assert requests == [("POST", "/salesTaxAccounts", {"salesTaxAccount": {"type": "opaque"}})]

    meta_preview = call_tool(
        server,
        "api_sales_tax_meta_fields_create_preview",
        {"salesTaxMetaField": {"name": "opaque"}},
    )
    cross_resource_mismatch = call_tool(
        server,
        "api_sales_tax_accounts_create_execute",
        {"confirmation_ticket": meta_preview["confirmation_ticket"]},
    )
    assert cross_resource_mismatch["code"] == StableErrorCode.CONFIRMATION_MISMATCH
    assert len(requests) == 1

    meta_execution = call_tool(
        server,
        "api_sales_tax_meta_fields_create_execute",
        {"confirmation_ticket": meta_preview["confirmation_ticket"]},
    )
    assert meta_execution["changed_records"] == {"salesTaxMetaFields": [{"id": "meta-1"}]}
    assert requests[-1] == (
        "POST",
        "/salesTaxMetaFields",
        {"salesTaxMetaField": {"name": "opaque"}},
    )
