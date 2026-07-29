from __future__ import annotations

import asyncio
from pathlib import Path

import pytest

from billy_mcp.coverage import CoverageLoadError, load_coverage_report
from billy_mcp.models import StableErrorCode
from billy_mcp.server import create_server


def write_coverage_fixture(root: Path) -> None:
    coverage = root / "coverage"
    coverage.mkdir()
    (coverage / "api_v2_manifest.yaml").write_text(
        """operations:
- id: api.products.list
  lane: api
  area: products
  operation: list
  method_or_route: GET /v2/products
  request_fields: [page, pageSize]
  response_fields: [products, meta.paging]
  filters: []
  pagination: {parameters: [page, pageSize]}
  errors: [AUTHENTICATION_REQUIRED]
  side_effects: none
  cleanup: not_applicable
  tool_name: api_products_list
  evidence: frozen fixture
  discovered: true
  implemented: false
  contract_tested: false
  live_tested: false
""",
        encoding="utf-8",
    )
    (coverage / "ui_workflows_manifest.yaml").write_text(
        """workflows:
- id: ui.products.list
  lane: ui
  area: products
  operation: list
  method_or_route: /products
  request_fields: []
  response_fields: []
  filters: []
  pagination: null
  errors: [UI_CHANGED]
  side_effects: none
  cleanup: not_applicable
  tool_name: ''
  evidence: frozen fixture
  discovered: true
  implemented: false
  contract_tested: false
  live_tested: false
  vision_verified: false
""",
        encoding="utf-8",
    )
    (coverage / "browser_egress.yaml").write_text("hosts: []\n", encoding="utf-8")
    (coverage / "status.json").write_text(
        '{"complete": false, "phase": "phase_0_inventory", "source_counts": {"red": 2}}',
        encoding="utf-8",
    )


def test_missing_manifests_return_typed_error(tmp_path: Path) -> None:
    with pytest.raises(CoverageLoadError) as failure:
        load_coverage_report(tmp_path)

    assert failure.value.error.code is StableErrorCode.NOT_FOUND
    assert failure.value.error.details["missing"] == [
        "api_v2_manifest.yaml",
        "ui_workflows_manifest.yaml",
        "browser_egress.yaml",
        "status.json",
    ]


def test_server_registers_only_coverage_and_implemented_read_tools(tmp_path: Path) -> None:
    write_coverage_fixture(tmp_path)
    report = load_coverage_report(tmp_path)
    server = create_server(tmp_path)
    tools = asyncio.run(server.list_tools())

    assert report.status.complete is False
    assert report.status.source_counts == {"red": 2}
    assert [row.id for row in report.api_rows] == ["api.products.list"]
    assert {tool.name for tool in tools} == {
        "coverage_status",
        "coverage_report",
        "api_user_get",
        "api_user_list_organizations",
        "api_organizations_get",
        "api_organizations_list",
        "api_currencies_get",
        "api_currencies_list",
        "api_countries_get",
        "api_countries_list",
        "api_locales_get",
        "api_locales_list",
        "api_products_get",
        "api_products_list",
        "api_product_prices_get",
        "api_product_prices_list",
        "api_contacts_get",
        "api_contacts_list",
        "api_invoices_get",
        "api_invoices_list",
        "api_bills_get",
        "api_bills_list",
        "api_daybook_transactions_get",
        "api_daybook_transactions_list",
        "api_invoice_lines_get",
        "api_invoice_lines_list",
        "api_bill_lines_get",
        "api_bill_lines_list",
        "api_daybook_transaction_lines_get",
        "api_daybook_transaction_lines_list",
        "api_contact_persons_get",
        "api_contact_persons_list",
        "api_daybooks_get",
        "api_daybooks_list",
        "api_daybook_balance_accounts_get",
        "api_daybook_balance_accounts_list",
        "api_accounts_get",
        "api_accounts_list",
        "api_account_groups_get",
        "api_account_groups_list",
        "api_account_natures_get",
        "api_account_natures_list",
        "api_files_get",
        "api_files_list",
        "api_attachments_get",
        "api_attachments_list",
    }
