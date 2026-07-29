from __future__ import annotations

import asyncio
from pathlib import Path

import pytest

from billy_mcp.coverage import CoverageLoadError, load_coverage_report
from billy_mcp.models import StableErrorCode
from billy_mcp.server import create_server

WAVE_FOUR_API_TOOL_NAMES = frozenset(
    {
        "api_country_groups_get",
        "api_country_groups_list",
        "api_cities_get",
        "api_cities_list",
        "api_states_get",
        "api_states_list",
        "api_zipcodes_get",
        "api_zipcodes_list",
        "api_tax_rates_get",
        "api_tax_rates_list",
        "api_tax_rate_deduction_components_get",
        "api_tax_rate_deduction_components_list",
        "api_sales_tax_rulesets_get",
        "api_sales_tax_rulesets_list",
        "api_sales_tax_rules_get",
        "api_sales_tax_rules_list",
        "api_sales_tax_accounts_get",
        "api_sales_tax_accounts_list",
        "api_sales_tax_meta_fields_get",
        "api_sales_tax_meta_fields_list",
        "api_sales_tax_returns_get",
        "api_sales_tax_returns_list",
        "api_sales_tax_payments_get",
        "api_sales_tax_payments_list",
        "api_bank_payments_get",
        "api_bank_payments_list",
        "api_bank_line_matches_get",
        "api_bank_line_matches_list",
        "api_bank_lines_get",
        "api_bank_lines_list",
        "api_bank_line_subject_associations_get",
        "api_bank_line_subject_associations_list",
        "api_balance_modifiers_get",
        "api_balance_modifiers_list",
        "api_contact_balance_payments_get",
        "api_contact_balance_payments_list",
        "api_contact_balance_postings_get",
        "api_contact_balance_postings_list",
        "api_invoice_late_fees_get",
        "api_invoice_late_fees_list",
        "api_invoice_reminders_get",
        "api_invoice_reminders_list",
        "api_invoice_reminder_associations_get",
        "api_invoice_reminder_associations_list",
        "api_transactions_get",
        "api_transactions_list",
        "api_postings_get",
        "api_postings_list",
        "api_users_get",
        "api_users_list",
    }
)

WAVE_FIVEA_WRITE_API_TOOL_NAMES = frozenset(
    {
        "api_products_create_preview",
        "api_products_create_execute",
        "api_products_update_preview",
        "api_products_update_execute",
        "api_products_delete_preview",
        "api_products_delete_execute",
        "api_product_prices_create_preview",
        "api_product_prices_create_execute",
        "api_product_prices_update_preview",
        "api_product_prices_update_execute",
        "api_product_prices_delete_preview",
        "api_product_prices_delete_execute",
        "api_contacts_create_preview",
        "api_contacts_create_execute",
        "api_contacts_update_preview",
        "api_contacts_update_execute",
        "api_contacts_delete_preview",
        "api_contacts_delete_execute",
        "api_contact_persons_create_preview",
        "api_contact_persons_create_execute",
        "api_contact_persons_update_preview",
        "api_contact_persons_update_execute",
        "api_contact_persons_delete_preview",
        "api_contact_persons_delete_execute",
        "api_daybooks_create_preview",
        "api_daybooks_create_execute",
        "api_daybooks_update_preview",
        "api_daybooks_update_execute",
        "api_daybooks_delete_preview",
        "api_daybooks_delete_execute",
    }
)


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


def test_server_registers_coverage_reads_and_ticketed_writes(tmp_path: Path) -> None:
    write_coverage_fixture(tmp_path)
    report = load_coverage_report(tmp_path)
    server = create_server(tmp_path)
    tools = asyncio.run(server.list_tools())

    assert report.status.complete is False
    assert report.status.source_counts == {"red": 2}
    assert [row.id for row in report.api_rows] == ["api.products.list"]
    expected_pre_wave_four_tools = {
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
    tool_names = {tool.name for tool in tools}
    api_tool_names = {name for name in tool_names if name.startswith("api_")}
    coverage_tool_names = {name for name in tool_names if name.startswith("coverage_")}

    assert len(WAVE_FOUR_API_TOOL_NAMES) == 50
    assert len(WAVE_FIVEA_WRITE_API_TOOL_NAMES) == 30
    assert len(api_tool_names) == 124
    assert coverage_tool_names == {"coverage_status", "coverage_report"}
    assert tool_names == (
        expected_pre_wave_four_tools | WAVE_FOUR_API_TOOL_NAMES | WAVE_FIVEA_WRITE_API_TOOL_NAMES
    )
