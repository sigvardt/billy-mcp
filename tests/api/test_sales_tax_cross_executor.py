"""Integration tests for shared root-server sales-tax confirmation tickets."""

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
    """Call one typed MCP tool and return its structured payload."""

    result = asyncio.run(server.call_tool(tool_name, arguments))
    structured_content = result.structured_content
    assert isinstance(structured_content, dict)
    payload = structured_content.get("result", structured_content)
    assert isinstance(payload, dict)
    return cast(dict[str, object], payload)


def test_root_shared_service_rejects_cross_resource_executors_without_consuming_tickets(
    monkeypatch: MonkeyPatch,
) -> None:
    """Tickets issued by root's shared store remain bound to their one executor."""

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
        if path == "/salesTaxRulesets":
            return BillyResponse(200, {"salesTaxRulesets": [{"id": "ruleset-1"}]})
        if path == "/salesTaxRules":
            return BillyResponse(200, {"salesTaxRules": [{"id": "rule-1"}]})
        raise AssertionError(f"unexpected request: {method} {path}")

    monkeypatch.setattr(BillyHttpClient, "request", fake_request)
    server = create_server()

    ruleset_preview = call_tool(
        server,
        "api_sales_tax_rulesets_create_preview",
        {"salesTaxRuleset": {"name": "Danish VAT"}},
    )
    rule_mismatch = call_tool(
        server,
        "api_sales_tax_rules_delete_execute",
        {"confirmation_ticket": ruleset_preview["confirmation_ticket"]},
    )
    assert rule_mismatch["code"] == StableErrorCode.CONFIRMATION_MISMATCH
    assert requests == []

    ruleset_execution = call_tool(
        server,
        "api_sales_tax_rulesets_create_execute",
        {"confirmation_ticket": ruleset_preview["confirmation_ticket"]},
    )
    assert ruleset_execution["changed_records"] == {"salesTaxRulesets": [{"id": "ruleset-1"}]}
    assert len(requests) == 1

    rule_preview = call_tool(
        server,
        "api_sales_tax_rules_create_preview",
        {"salesTaxRule": {"rulesetId": "ruleset-1", "countryId": "DK"}},
    )
    ruleset_mismatch = call_tool(
        server,
        "api_sales_tax_rulesets_delete_execute",
        {"confirmation_ticket": rule_preview["confirmation_ticket"]},
    )
    assert ruleset_mismatch["code"] == StableErrorCode.CONFIRMATION_MISMATCH
    assert len(requests) == 1

    rule_execution = call_tool(
        server,
        "api_sales_tax_rules_create_execute",
        {"confirmation_ticket": rule_preview["confirmation_ticket"]},
    )
    assert rule_execution["changed_records"] == {"salesTaxRules": [{"id": "rule-1"}]}
    assert len(requests) == 2
