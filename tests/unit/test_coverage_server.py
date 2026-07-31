from __future__ import annotations

import asyncio
import json
from pathlib import Path
from typing import Any, cast

import pytest

from billy_mcp.coverage import CoverageLoadError, load_coverage_report
from billy_mcp.models import (
    AuthLoginStartSuccess,
    AuthLoginWaitSuccess,
    AuthStatusSuccess,
    StableErrorCode,
    UiBankAccountsListSuccess,
    UiBankReconciliationOpenSuccess,
    UiBillsListSuccess,
    UiClientsListSuccess,
    UiCreditorBalancesListSuccess,
    UiDaybooksOpenSuccess,
    UiDebtorBalancesListSuccess,
    UiFinancingOpenSuccess,
    UiInvoicesListSuccess,
    UiProductsImportSuccess,
    UiProductsListSuccess,
    UiQuotesListSuccess,
    UiReceiptInboxListSuccess,
    UiRecurringInvoicesListSuccess,
    UiSuppliersListSuccess,
    UiUploadsListSuccess,
)
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

WAVE_FIVEB_WRITE_API_TOOL_NAMES = frozenset(
    {
        "api_account_groups_create_preview",
        "api_account_groups_create_execute",
        "api_account_groups_update_preview",
        "api_account_groups_update_execute",
        "api_account_groups_delete_preview",
        "api_account_groups_delete_execute",
        "api_accounts_create_preview",
        "api_accounts_create_execute",
        "api_accounts_update_preview",
        "api_accounts_update_execute",
        "api_accounts_delete_preview",
        "api_accounts_delete_execute",
        "api_daybook_balance_accounts_create_preview",
        "api_daybook_balance_accounts_create_execute",
        "api_daybook_balance_accounts_update_preview",
        "api_daybook_balance_accounts_update_execute",
        "api_daybook_balance_accounts_delete_preview",
        "api_daybook_balance_accounts_delete_execute",
    }
)

WAVE_FIVEC_WRITE_API_TOOL_NAMES = frozenset(
    {
        "api_daybook_transactions_create_preview",
        "api_daybook_transactions_create_execute",
        "api_daybook_transactions_update_preview",
        "api_daybook_transactions_update_execute",
        "api_daybook_transactions_delete_preview",
        "api_daybook_transactions_delete_execute",
        "api_daybook_transaction_lines_create_preview",
        "api_daybook_transaction_lines_create_execute",
        "api_daybook_transaction_lines_update_preview",
        "api_daybook_transaction_lines_update_execute",
        "api_daybook_transaction_lines_delete_preview",
        "api_daybook_transaction_lines_delete_execute",
    }
)

WAVE_FIVED_WRITE_API_TOOL_NAMES = frozenset(
    {
        "api_invoices_create_preview",
        "api_invoices_create_execute",
        "api_invoices_update_preview",
        "api_invoices_update_execute",
        "api_invoices_delete_preview",
        "api_invoices_delete_execute",
        "api_invoice_lines_create_preview",
        "api_invoice_lines_create_execute",
        "api_invoice_lines_update_preview",
        "api_invoice_lines_update_execute",
        "api_invoice_lines_delete_preview",
        "api_invoice_lines_delete_execute",
    }
)

WAVE_FIVEE_WRITE_API_TOOL_NAMES = frozenset(
    {
        "api_bills_create_preview",
        "api_bills_create_execute",
        "api_bills_update_preview",
        "api_bills_update_execute",
        "api_bills_delete_preview",
        "api_bills_delete_execute",
        "api_bill_lines_create_preview",
        "api_bill_lines_create_execute",
        "api_bill_lines_update_preview",
        "api_bill_lines_update_execute",
        "api_bill_lines_delete_preview",
        "api_bill_lines_delete_execute",
    }
)

WAVE_FIVEF_WRITE_API_TOOL_NAMES = frozenset(
    {
        "api_tax_rates_create_preview",
        "api_tax_rates_create_execute",
        "api_tax_rates_update_preview",
        "api_tax_rates_update_execute",
        "api_tax_rates_delete_preview",
        "api_tax_rates_delete_execute",
        "api_tax_rate_deduction_components_create_preview",
        "api_tax_rate_deduction_components_create_execute",
        "api_tax_rate_deduction_components_update_preview",
        "api_tax_rate_deduction_components_update_execute",
        "api_tax_rate_deduction_components_delete_preview",
        "api_tax_rate_deduction_components_delete_execute",
    }
)

WAVE_FIVEG_WRITE_API_TOOL_NAMES = frozenset(
    {
        "api_sales_tax_rulesets_create_preview",
        "api_sales_tax_rulesets_create_execute",
        "api_sales_tax_rulesets_update_preview",
        "api_sales_tax_rulesets_update_execute",
        "api_sales_tax_rulesets_delete_preview",
        "api_sales_tax_rulesets_delete_execute",
        "api_sales_tax_rules_create_preview",
        "api_sales_tax_rules_create_execute",
        "api_sales_tax_rules_update_preview",
        "api_sales_tax_rules_update_execute",
        "api_sales_tax_rules_delete_preview",
        "api_sales_tax_rules_delete_execute",
    }
)

WAVE_FIVEH_WRITE_API_TOOL_NAMES = frozenset(
    {
        "api_attachments_create_preview",
        "api_attachments_create_execute",
        "api_attachments_update_preview",
        "api_attachments_update_execute",
        "api_attachments_delete_preview",
        "api_attachments_delete_execute",
    }
)

WAVE_FIVEI_WRITE_API_TOOL_NAMES = frozenset(
    {
        "api_sales_tax_accounts_create_preview",
        "api_sales_tax_accounts_create_execute",
        "api_sales_tax_accounts_update_preview",
        "api_sales_tax_accounts_update_execute",
        "api_sales_tax_accounts_delete_preview",
        "api_sales_tax_accounts_delete_execute",
        "api_sales_tax_meta_fields_create_preview",
        "api_sales_tax_meta_fields_create_execute",
        "api_sales_tax_meta_fields_update_preview",
        "api_sales_tax_meta_fields_update_execute",
        "api_sales_tax_meta_fields_delete_preview",
        "api_sales_tax_meta_fields_delete_execute",
    }
)

WAVE_FIVEJ_WRITE_API_TOOL_NAMES = frozenset(
    {
        "api_bank_line_matches_create_preview",
        "api_bank_line_matches_create_execute",
        "api_bank_line_matches_update_preview",
        "api_bank_line_matches_update_execute",
        "api_bank_line_matches_delete_preview",
        "api_bank_line_matches_delete_execute",
        "api_bank_lines_create_preview",
        "api_bank_lines_create_execute",
        "api_bank_lines_update_preview",
        "api_bank_lines_update_execute",
        "api_bank_lines_delete_preview",
        "api_bank_lines_delete_execute",
        "api_bank_line_subject_associations_create_preview",
        "api_bank_line_subject_associations_create_execute",
        "api_bank_line_subject_associations_update_preview",
        "api_bank_line_subject_associations_update_execute",
        "api_bank_line_subject_associations_delete_preview",
        "api_bank_line_subject_associations_delete_execute",
    }
)

WAVE_FIVEK_WRITE_API_TOOL_NAMES = frozenset(
    {
        "api_bank_payments_create_preview",
        "api_bank_payments_create_execute",
        "api_bank_payments_update_preview",
        "api_bank_payments_update_execute",
    }
)

WAVE_FIVEL_WRITE_API_TOOL_NAMES = frozenset(
    {
        "api_sales_tax_payments_create_preview",
        "api_sales_tax_payments_create_execute",
        "api_sales_tax_payments_update_preview",
        "api_sales_tax_payments_update_execute",
    }
)

WAVE_FIVEM_WRITE_API_TOOL_NAMES = frozenset(
    {
        "api_contact_balance_payments_create_preview",
        "api_contact_balance_payments_create_execute",
        "api_contact_balance_payments_update_preview",
        "api_contact_balance_payments_update_execute",
    }
)

WAVE_FIVEN_WRITE_API_TOOL_NAMES = frozenset(
    {
        "api_invoice_late_fees_create_preview",
        "api_invoice_late_fees_create_execute",
        "api_invoice_late_fees_update_preview",
        "api_invoice_late_fees_update_execute",
    }
)

WAVE_FIVEO_WRITE_API_TOOL_NAMES = frozenset(
    {
        "api_invoice_reminders_create_preview",
        "api_invoice_reminders_create_execute",
    }
)

WAVE_FIVEP_WRITE_API_TOOL_NAMES = frozenset(
    {
        "api_organizations_create_preview",
        "api_organizations_create_execute",
        "api_organizations_update_preview",
        "api_organizations_update_execute",
    }
)

WAVE_FIVEQ_WRITE_API_TOOL_NAMES = frozenset(
    {
        "api_users_update_preview",
        "api_users_update_execute",
    }
)

WAVE_FIVER_WRITE_API_TOOL_NAMES = frozenset(
    {
        "api_sales_tax_returns_update_preview",
        "api_sales_tax_returns_update_execute",
    }
)

WAVE_FIVESA_API_TOOL_NAMES = frozenset({"api_invoice_logs_list"})

WAVE_FIVESB_API_TOOL_NAMES = frozenset(
    {
        "api_files_upload_preview",
        "api_files_upload_execute",
    }
)

WAVE_FIVESC_API_TOOL_NAMES = frozenset(
    {
        "api_invoices_send_email_preview",
        "api_invoices_send_email_execute",
        "api_invoice_deliveries_create_preview",
        "api_invoice_deliveries_create_execute",
    }
)


class FakeAuthStatusChecker:
    def __init__(self) -> None:
        self.calls = 0

    async def auth_status(self) -> AuthStatusSuccess:
        self.calls += 1
        return AuthStatusSuccess()


class FakeAuthLoginService:
    def __init__(self) -> None:
        self.start_calls = 0
        self.wait_calls = 0

    async def auth_login_start(self) -> AuthLoginStartSuccess:
        self.start_calls += 1
        return AuthLoginStartSuccess()

    async def auth_login_wait(self) -> AuthLoginWaitSuccess:
        self.wait_calls += 1
        return AuthLoginWaitSuccess(status="AUTH_REQUIRED")


class FakeUiProductsListService:
    def __init__(self) -> None:
        self.calls = 0

    async def ui_products_list(self) -> UiProductsListSuccess:
        self.calls += 1
        return UiProductsListSuccess(search_control_visible=True, shell_markers_present=True)


class FakeUiInvoicesListService:
    def __init__(self) -> None:
        self.calls = 0

    async def ui_invoices_list(self) -> UiInvoicesListSuccess:
        self.calls += 1
        return UiInvoicesListSuccess(create_action_visible=True, shell_markers_present=True)


class FakeUiClientsListService:
    def __init__(self) -> None:
        self.calls = 0

    async def ui_clients_list(self) -> UiClientsListSuccess:
        self.calls += 1
        return UiClientsListSuccess(create_action_visible=True, shell_markers_present=True)


class FakeUiBankAccountsListService:
    def __init__(self) -> None:
        self.calls = 0

    async def ui_bank_accounts_list(self) -> UiBankAccountsListSuccess:
        self.calls += 1
        return UiBankAccountsListSuccess(
            connect_bank_action_visible=True,
            shell_markers_present=True,
        )


class FakeUiQuotesListService:
    def __init__(self) -> None:
        self.calls = 0

    async def ui_quotes_list(self) -> UiQuotesListSuccess:
        self.calls += 1
        return UiQuotesListSuccess(create_action_visible=True, shell_markers_present=True)


class FakeUiRecurringInvoicesListService:
    def __init__(self) -> None:
        self.calls = 0

    async def ui_recurring_invoices_list(self) -> UiRecurringInvoicesListSuccess:
        self.calls += 1
        return UiRecurringInvoicesListSuccess(
            create_action_visible=True,
            shell_markers_present=True,
        )


class FakeUiProductsImportService:
    def __init__(self) -> None:
        self.calls = 0

    async def ui_products_import(self) -> UiProductsImportSuccess:
        self.calls += 1
        return UiProductsImportSuccess(
            choose_csv_action_visible=True,
            shell_markers_present=True,
        )


class FakeUiSuppliersListService:
    def __init__(self) -> None:
        self.calls = 0

    async def ui_suppliers_list(self) -> UiSuppliersListSuccess:
        self.calls += 1
        return UiSuppliersListSuccess(create_action_visible=True, shell_markers_present=True)


class FakeUiBillsListService:
    def __init__(self) -> None:
        self.calls = 0

    async def ui_bills_list(self) -> UiBillsListSuccess:
        self.calls += 1
        return UiBillsListSuccess(create_action_visible=True, shell_markers_present=True)


class FakeUiDebtorBalancesListService:
    def __init__(self) -> None:
        self.calls = 0

    async def ui_debtor_balances_list(self) -> UiDebtorBalancesListSuccess:
        self.calls += 1
        return UiDebtorBalancesListSuccess(create_action_visible=True, shell_markers_present=True)


class FakeUiCreditorBalancesListService:
    def __init__(self) -> None:
        self.calls = 0

    async def ui_creditor_balances_list(self) -> UiCreditorBalancesListSuccess:
        self.calls += 1
        return UiCreditorBalancesListSuccess(create_action_visible=True, shell_markers_present=True)


class FakeUiUploadsListService:
    def __init__(self) -> None:
        self.calls = 0

    async def ui_uploads_list(self) -> UiUploadsListSuccess:
        self.calls += 1
        return UiUploadsListSuccess(upload_action_visible=True, shell_markers_present=True)


class FakeUiReceiptInboxListService:
    def __init__(self) -> None:
        self.calls = 0

    async def ui_receipt_inbox_list(self) -> UiReceiptInboxListSuccess:
        self.calls += 1
        return UiReceiptInboxListSuccess(file_control_present=True, shell_markers_present=True)


class FakeUiBankReconciliationOpenService:
    def __init__(self) -> None:
        self.calls = 0

    async def ui_bank_reconciliation_open(self) -> UiBankReconciliationOpenSuccess:
        self.calls += 1
        return UiBankReconciliationOpenSuccess(
            empty_content_shell=True,
            afstemning_nav_visible=True,
            shell_markers_present=True,
        )


class FakeUiDaybooksOpenService:
    def __init__(self) -> None:
        self.calls = 0

    async def ui_daybooks_open(self) -> UiDaybooksOpenSuccess:
        self.calls += 1
        return UiDaybooksOpenSuccess(editor_markers_present=True, shell_markers_present=True)


class FakeUiFinancingOpenService:
    def __init__(self) -> None:
        self.calls = 0

    async def ui_financing_open(self) -> UiFinancingOpenSuccess:
        self.calls += 1
        return UiFinancingOpenSuccess(apply_cta_observed=True, shell_markers_present=True)


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


def test_server_registers_coverage_reads_ticketed_writes_and_auth_status(tmp_path: Path) -> None:
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
    auth_tool_names = {name for name in tool_names if name.startswith("auth_")}
    ui_tool_names = {name for name in tool_names if name.startswith("ui_")}
    coverage_tool_names = {name for name in tool_names if name.startswith("coverage_")}

    assert len(WAVE_FOUR_API_TOOL_NAMES) == 50
    assert len(WAVE_FIVEA_WRITE_API_TOOL_NAMES) == 30
    assert len(WAVE_FIVEB_WRITE_API_TOOL_NAMES) == 18
    assert len(WAVE_FIVEC_WRITE_API_TOOL_NAMES) == 12
    assert len(WAVE_FIVED_WRITE_API_TOOL_NAMES) == 12
    assert len(WAVE_FIVEE_WRITE_API_TOOL_NAMES) == 12
    assert len(WAVE_FIVEF_WRITE_API_TOOL_NAMES) == 12
    assert len(WAVE_FIVEG_WRITE_API_TOOL_NAMES) == 12
    assert len(WAVE_FIVEH_WRITE_API_TOOL_NAMES) == 6
    assert len(WAVE_FIVEI_WRITE_API_TOOL_NAMES) == 12
    assert len(WAVE_FIVEJ_WRITE_API_TOOL_NAMES) == 18
    assert len(WAVE_FIVEK_WRITE_API_TOOL_NAMES) == 4
    assert len(WAVE_FIVEL_WRITE_API_TOOL_NAMES) == 4
    assert len(WAVE_FIVEM_WRITE_API_TOOL_NAMES) == 4
    assert len(WAVE_FIVEN_WRITE_API_TOOL_NAMES) == 4
    assert len(WAVE_FIVEO_WRITE_API_TOOL_NAMES) == 2
    assert len(WAVE_FIVEP_WRITE_API_TOOL_NAMES) == 4
    assert len(WAVE_FIVEQ_WRITE_API_TOOL_NAMES) == 2
    assert len(WAVE_FIVER_WRITE_API_TOOL_NAMES) == 2
    assert len(WAVE_FIVESA_API_TOOL_NAMES) == 1
    assert len(WAVE_FIVESB_API_TOOL_NAMES) == 2
    assert len(WAVE_FIVESC_API_TOOL_NAMES) == 4
    assert len(api_tool_names) == 271
    assert auth_tool_names == {"auth_status", "auth_login_start", "auth_login_wait"}
    assert ui_tool_names == {
        "ui_invoices_list",
        "ui_products_list",
        "ui_clients_list",
        "ui_bank_accounts_list",
        "ui_quotes_list",
        "ui_recurring_invoices_list",
        "ui_products_import",
        "ui_suppliers_list",
        "ui_bills_list",
        "ui_debtor_balances_list",
        "ui_creditor_balances_list",
        "ui_uploads_list",
        "ui_receipt_inbox_list",
        "ui_bank_reconciliation_open",
        "ui_financing_open",
        "ui_daybooks_open",
    }
    assert coverage_tool_names == {"coverage_status", "coverage_report"}
    assert tool_names == (
        expected_pre_wave_four_tools
        | WAVE_FOUR_API_TOOL_NAMES
        | WAVE_FIVEA_WRITE_API_TOOL_NAMES
        | WAVE_FIVEB_WRITE_API_TOOL_NAMES
        | WAVE_FIVEC_WRITE_API_TOOL_NAMES
        | WAVE_FIVED_WRITE_API_TOOL_NAMES
        | WAVE_FIVEE_WRITE_API_TOOL_NAMES
        | WAVE_FIVEF_WRITE_API_TOOL_NAMES
        | WAVE_FIVEG_WRITE_API_TOOL_NAMES
        | WAVE_FIVEH_WRITE_API_TOOL_NAMES
        | WAVE_FIVEI_WRITE_API_TOOL_NAMES
        | WAVE_FIVEJ_WRITE_API_TOOL_NAMES
        | WAVE_FIVEK_WRITE_API_TOOL_NAMES
        | WAVE_FIVEL_WRITE_API_TOOL_NAMES
        | WAVE_FIVEM_WRITE_API_TOOL_NAMES
        | WAVE_FIVEN_WRITE_API_TOOL_NAMES
        | WAVE_FIVEO_WRITE_API_TOOL_NAMES
        | WAVE_FIVEP_WRITE_API_TOOL_NAMES
        | WAVE_FIVEQ_WRITE_API_TOOL_NAMES
        | WAVE_FIVER_WRITE_API_TOOL_NAMES
        | WAVE_FIVESA_API_TOOL_NAMES
        | WAVE_FIVESB_API_TOOL_NAMES
        | WAVE_FIVESC_API_TOOL_NAMES
        | auth_tool_names
        | ui_tool_names
    )


def test_auth_status_registration_has_no_generic_controls_and_uses_typed_output(
    tmp_path: Path,
) -> None:
    write_coverage_fixture(tmp_path)
    checker = FakeAuthStatusChecker()
    server = create_server(tmp_path, auth_status_checker=checker)
    tool = {item.name: item for item in asyncio.run(server.list_tools())}["auth_status"]

    assert tool.parameters["properties"] == {}
    output_schema = tool.output_schema
    assert isinstance(output_schema, dict)
    output_properties = cast(dict[str, Any], output_schema["properties"])
    result_schema = cast(dict[str, Any], output_properties["result"])
    variants = cast(list[dict[str, Any]], result_schema["anyOf"])
    assert any(
        cast(dict[str, Any], variant["properties"]).get("status", {}).get("const")
        == "AUTH_REQUIRED"
        for variant in variants
    )
    assert any(
        {"code", "message"}.issubset(cast(dict[str, Any], variant["properties"]))
        for variant in variants
    )

    result = asyncio.run(server.call_tool("auth_status", {}))

    assert result.structured_content == {"result": {"status": "AUTH_REQUIRED"}}
    assert checker.calls == 1


def test_login_registration_has_empty_inputs_and_typed_stable_outputs(tmp_path: Path) -> None:
    write_coverage_fixture(tmp_path)
    login_service = FakeAuthLoginService()
    server = create_server(tmp_path, auth_login_service=login_service)
    tools = {item.name: item for item in asyncio.run(server.list_tools())}

    start_tool = tools["auth_login_start"]
    wait_tool = tools["auth_login_wait"]
    assert start_tool.parameters["properties"] == {}
    assert wait_tool.parameters["properties"] == {}
    for tool in (start_tool, wait_tool):
        schema = json.dumps(tool.output_schema).lower()
        assert not any(term in schema for term in ("email", "password", "totp", "cookie", "token"))

    start_result = asyncio.run(server.call_tool("auth_login_start", {}))
    wait_result = asyncio.run(server.call_tool("auth_login_wait", {}))

    assert start_result.structured_content == {"result": {"status": "AUTHENTICATING"}}
    assert wait_result.structured_content == {"result": {"status": "AUTH_REQUIRED"}}
    assert login_service.start_calls == 1
    assert login_service.wait_calls == 1


def test_ui_invoices_list_registration_has_empty_input_and_typed_output(tmp_path: Path) -> None:
    write_coverage_fixture(tmp_path)
    invoices = FakeUiInvoicesListService()
    server = create_server(tmp_path, ui_invoices_list_service=invoices)
    tool = {item.name: item for item in asyncio.run(server.list_tools())}["ui_invoices_list"]

    assert tool.parameters["properties"] == {}
    output_schema = tool.output_schema
    assert isinstance(output_schema, dict)
    schema = json.dumps(output_schema).lower()
    assert not any(term in schema for term in ("email", "password", "totp", "cookie", "token"))
    # path_class may mention the redacted segment name; property keys must not.
    properties = cast(dict[str, Any], output_schema.get("properties") or {})
    assert "org_slug" not in properties

    result = asyncio.run(server.call_tool("ui_invoices_list", {}))

    assert result.structured_content == {
        "result": {
            "path_class": "/:org_slug/invoices",
            "heading": "Fakturaer",
            "create_action_visible": True,
            "shell_markers_present": True,
        }
    }
    assert invoices.calls == 1


def test_ui_products_list_registration_has_empty_input_and_typed_output(tmp_path: Path) -> None:
    write_coverage_fixture(tmp_path)
    products = FakeUiProductsListService()
    server = create_server(tmp_path, ui_products_list_service=products)
    tool = {item.name: item for item in asyncio.run(server.list_tools())}["ui_products_list"]

    assert tool.parameters["properties"] == {}
    output_schema = tool.output_schema
    assert isinstance(output_schema, dict)
    schema = json.dumps(output_schema).lower()
    assert not any(term in schema for term in ("email", "password", "totp", "cookie", "token"))
    properties = cast(dict[str, Any], output_schema.get("properties") or {})
    assert "org_slug" not in properties

    result = asyncio.run(server.call_tool("ui_products_list", {}))

    assert result.structured_content == {
        "result": {
            "path_class": "/:org_slug/products",
            "heading": "Produkter",
            "search_control_visible": True,
            "shell_markers_present": True,
        }
    }
    assert products.calls == 1


def test_ui_clients_list_registration_has_empty_input_and_typed_output(tmp_path: Path) -> None:
    write_coverage_fixture(tmp_path)
    clients = FakeUiClientsListService()
    server = create_server(tmp_path, ui_clients_list_service=clients)
    tool = {item.name: item for item in asyncio.run(server.list_tools())}["ui_clients_list"]

    assert tool.parameters["properties"] == {}
    output_schema = tool.output_schema
    assert isinstance(output_schema, dict)
    schema = json.dumps(output_schema).lower()
    assert not any(term in schema for term in ("email", "password", "totp", "cookie", "token"))
    properties = cast(dict[str, Any], output_schema.get("properties") or {})
    assert "org_slug" not in properties

    result = asyncio.run(server.call_tool("ui_clients_list", {}))

    assert result.structured_content == {
        "result": {
            "path_class": "/:org_slug/clients",
            "heading": "Kunder",
            "create_action_visible": True,
            "shell_markers_present": True,
        }
    }
    assert clients.calls == 1


def test_ui_bank_accounts_list_registration_has_empty_input_and_typed_output(
    tmp_path: Path,
) -> None:
    write_coverage_fixture(tmp_path)
    bank_accounts = FakeUiBankAccountsListService()
    server = create_server(tmp_path, ui_bank_accounts_list_service=bank_accounts)
    tool = {item.name: item for item in asyncio.run(server.list_tools())}["ui_bank_accounts_list"]

    assert tool.parameters["properties"] == {}
    output_schema = tool.output_schema
    assert isinstance(output_schema, dict)
    schema = json.dumps(output_schema).lower()
    assert not any(term in schema for term in ("email", "password", "totp", "cookie", "token"))
    properties = cast(dict[str, Any], output_schema.get("properties") or {})
    assert "org_slug" not in properties

    result = asyncio.run(server.call_tool("ui_bank_accounts_list", {}))

    assert result.structured_content == {
        "result": {
            "path_class": "/:org_slug/bank-accounts",
            "heading": "Bankkonti",
            "connect_bank_action_visible": True,
            "shell_markers_present": True,
        }
    }
    assert bank_accounts.calls == 1


def test_ui_quotes_list_registration_has_empty_input_and_typed_output(tmp_path: Path) -> None:
    write_coverage_fixture(tmp_path)
    quotes = FakeUiQuotesListService()
    server = create_server(tmp_path, ui_quotes_list_service=quotes)
    tool = {item.name: item for item in asyncio.run(server.list_tools())}["ui_quotes_list"]

    assert tool.parameters["properties"] == {}
    output_schema = tool.output_schema
    assert isinstance(output_schema, dict)
    schema = json.dumps(output_schema).lower()
    assert not any(term in schema for term in ("email", "password", "totp", "cookie", "token"))
    properties = cast(dict[str, Any], output_schema.get("properties") or {})
    assert "org_slug" not in properties

    result = asyncio.run(server.call_tool("ui_quotes_list", {}))

    assert result.structured_content == {
        "result": {
            "path_class": "/:org_slug/quotes",
            "heading": "Tilbud",
            "create_action_visible": True,
            "shell_markers_present": True,
        }
    }
    assert quotes.calls == 1


def test_ui_recurring_invoices_list_registration_has_empty_input_and_typed_output(
    tmp_path: Path,
) -> None:
    write_coverage_fixture(tmp_path)
    recurring = FakeUiRecurringInvoicesListService()
    server = create_server(tmp_path, ui_recurring_invoices_list_service=recurring)
    tool = {item.name: item for item in asyncio.run(server.list_tools())}[
        "ui_recurring_invoices_list"
    ]

    assert tool.parameters["properties"] == {}
    output_schema = tool.output_schema
    assert isinstance(output_schema, dict)
    schema = json.dumps(output_schema).lower()
    assert not any(term in schema for term in ("email", "password", "totp", "cookie", "token"))
    properties = cast(dict[str, Any], output_schema.get("properties") or {})
    assert "org_slug" not in properties

    result = asyncio.run(server.call_tool("ui_recurring_invoices_list", {}))

    assert result.structured_content == {
        "result": {
            "path_class": "/:org_slug/recurring_invoices",
            "heading": "Abonnementer",
            "create_action_visible": True,
            "shell_markers_present": True,
        }
    }
    assert recurring.calls == 1


def test_ui_products_import_registration_has_empty_input_and_typed_output(
    tmp_path: Path,
) -> None:
    write_coverage_fixture(tmp_path)
    products_import = FakeUiProductsImportService()
    server = create_server(tmp_path, ui_products_import_service=products_import)
    tool = {item.name: item for item in asyncio.run(server.list_tools())}["ui_products_import"]

    assert tool.parameters["properties"] == {}
    output_schema = tool.output_schema
    assert isinstance(output_schema, dict)
    schema = json.dumps(output_schema).lower()
    assert not any(term in schema for term in ("email", "password", "totp", "cookie", "token"))
    properties = cast(dict[str, Any], output_schema.get("properties") or {})
    assert "org_slug" not in properties
    assert "file_path" not in properties

    result = asyncio.run(server.call_tool("ui_products_import", {}))

    assert result.structured_content == {
        "result": {
            "path_class": "/:org_slug/products/import",
            "heading": "Import af produkter",
            "choose_csv_action_visible": True,
            "shell_markers_present": True,
        }
    }
    assert products_import.calls == 1


def test_ui_suppliers_list_registration_has_empty_input_and_typed_output(tmp_path: Path) -> None:
    write_coverage_fixture(tmp_path)
    suppliers = FakeUiSuppliersListService()
    server = create_server(tmp_path, ui_suppliers_list_service=suppliers)
    tool = {item.name: item for item in asyncio.run(server.list_tools())}["ui_suppliers_list"]

    assert tool.parameters["properties"] == {}
    output_schema = tool.output_schema
    assert isinstance(output_schema, dict)
    schema = json.dumps(output_schema).lower()
    assert not any(term in schema for term in ("email", "password", "totp", "cookie", "token"))
    properties = cast(dict[str, Any], output_schema.get("properties") or {})
    assert "org_slug" not in properties

    result = asyncio.run(server.call_tool("ui_suppliers_list", {}))

    assert result.structured_content == {
        "result": {
            "path_class": "/:org_slug/suppliers",
            "heading": "Leverandører",
            "create_action_visible": True,
            "shell_markers_present": True,
        }
    }
    assert suppliers.calls == 1


def test_ui_bills_list_registration_has_empty_input_and_typed_output(tmp_path: Path) -> None:
    write_coverage_fixture(tmp_path)
    bills = FakeUiBillsListService()
    server = create_server(tmp_path, ui_bills_list_service=bills)
    tool = {item.name: item for item in asyncio.run(server.list_tools())}["ui_bills_list"]

    assert tool.parameters["properties"] == {}
    output_schema = tool.output_schema
    assert isinstance(output_schema, dict)
    schema = json.dumps(output_schema).lower()
    assert not any(term in schema for term in ("email", "password", "totp", "cookie", "token"))
    properties = cast(dict[str, Any], output_schema.get("properties") or {})
    assert "org_slug" not in properties

    result = asyncio.run(server.call_tool("ui_bills_list", {}))

    assert result.structured_content == {
        "result": {
            "path_class": "/:org_slug/bills",
            "heading": "Køb",
            "create_action_visible": True,
            "shell_markers_present": True,
        }
    }
    assert bills.calls == 1


def test_ui_debtor_balances_list_registration_has_empty_input_and_typed_output(
    tmp_path: Path,
) -> None:
    write_coverage_fixture(tmp_path)
    debtor = FakeUiDebtorBalancesListService()
    server = create_server(tmp_path, ui_debtor_balances_list_service=debtor)
    tool = {item.name: item for item in asyncio.run(server.list_tools())}["ui_debtor_balances_list"]

    assert tool.parameters["properties"] == {}
    output_schema = tool.output_schema
    assert isinstance(output_schema, dict)
    schema = json.dumps(output_schema).lower()
    assert not any(term in schema for term in ("email", "password", "totp", "cookie", "token"))
    properties = cast(dict[str, Any], output_schema.get("properties") or {})
    assert "org_slug" not in properties

    result = asyncio.run(server.call_tool("ui_debtor_balances_list", {}))

    assert result.structured_content == {
        "result": {
            "path_class": "/:org_slug/debtorbalance",
            "heading": "Tilgodehavender",
            "create_action_visible": True,
            "shell_markers_present": True,
        }
    }
    assert debtor.calls == 1


def test_ui_creditor_balances_list_registration_has_empty_input_and_typed_output(
    tmp_path: Path,
) -> None:
    write_coverage_fixture(tmp_path)
    creditor = FakeUiCreditorBalancesListService()
    server = create_server(tmp_path, ui_creditor_balances_list_service=creditor)
    tool = {item.name: item for item in asyncio.run(server.list_tools())}[
        "ui_creditor_balances_list"
    ]

    assert tool.parameters["properties"] == {}
    output_schema = tool.output_schema
    assert isinstance(output_schema, dict)
    schema = json.dumps(output_schema).lower()
    assert not any(term in schema for term in ("email", "password", "totp", "cookie", "token"))
    properties = cast(dict[str, Any], output_schema.get("properties") or {})
    assert "org_slug" not in properties

    result = asyncio.run(server.call_tool("ui_creditor_balances_list", {}))

    assert result.structured_content == {
        "result": {
            "path_class": "/:org_slug/creditorbalance",
            "heading": "Skyldige udgifter",
            "create_action_visible": True,
            "shell_markers_present": True,
        }
    }
    assert creditor.calls == 1


def test_ui_uploads_list_registration_has_empty_input_and_typed_output(
    tmp_path: Path,
) -> None:
    write_coverage_fixture(tmp_path)
    uploads = FakeUiUploadsListService()
    server = create_server(tmp_path, ui_uploads_list_service=uploads)
    tool = {item.name: item for item in asyncio.run(server.list_tools())}["ui_uploads_list"]

    assert tool.parameters["properties"] == {}
    output_schema = tool.output_schema
    assert isinstance(output_schema, dict)
    schema = json.dumps(output_schema).lower()
    assert not any(term in schema for term in ("email", "password", "totp", "cookie", "token"))
    properties = cast(dict[str, Any], output_schema.get("properties") or {})
    assert "org_slug" not in properties
    assert "file_path" not in properties
    assert "digest" not in properties

    result = asyncio.run(server.call_tool("ui_uploads_list", {}))

    assert result.structured_content == {
        "result": {
            "path_class": "/:org_slug/uploads",
            "heading": "Bilag",
            "upload_action_visible": True,
            "shell_markers_present": True,
        }
    }
    assert uploads.calls == 1


def test_ui_receipt_inbox_list_registration_has_empty_input_and_typed_output(
    tmp_path: Path,
) -> None:
    write_coverage_fixture(tmp_path)
    receipt_inbox = FakeUiReceiptInboxListService()
    server = create_server(tmp_path, ui_receipt_inbox_list_service=receipt_inbox)
    tool = {item.name: item for item in asyncio.run(server.list_tools())}["ui_receipt_inbox_list"]

    assert tool.parameters["properties"] == {}
    output_schema = tool.output_schema
    assert isinstance(output_schema, dict)
    schema = json.dumps(output_schema).lower()
    assert not any(term in schema for term in ("email", "password", "totp", "cookie", "token"))
    properties = cast(dict[str, Any], output_schema.get("properties") or {})
    assert "org_slug" not in properties
    assert "file_path" not in properties
    assert "digest" not in properties

    result = asyncio.run(server.call_tool("ui_receipt_inbox_list", {}))

    assert result.structured_content == {
        "result": {
            "path_class": "/:org_slug/vouchers",
            "heading": "Bilagsindbakke",
            "file_control_present": True,
            "shell_markers_present": True,
        }
    }
    assert receipt_inbox.calls == 1


def test_ui_bank_reconciliation_open_registration_has_empty_input_and_typed_output(
    tmp_path: Path,
) -> None:
    write_coverage_fixture(tmp_path)
    recon = FakeUiBankReconciliationOpenService()
    server = create_server(tmp_path, ui_bank_reconciliation_open_service=recon)
    tool = {item.name: item for item in asyncio.run(server.list_tools())}[
        "ui_bank_reconciliation_open"
    ]

    assert tool.parameters["properties"] == {}
    output_schema = tool.output_schema
    assert isinstance(output_schema, dict)
    schema = json.dumps(output_schema).lower()
    assert not any(term in schema for term in ("email", "password", "totp", "cookie", "token"))
    properties = cast(dict[str, Any], output_schema.get("properties") or {})
    assert "org_slug" not in properties
    assert "account_id" not in properties
    assert "url" not in properties

    result = asyncio.run(server.call_tool("ui_bank_reconciliation_open", {}))

    assert result.structured_content == {
        "result": {
            "path_class": "/:org_slug/bank_accounts/:id/sync",
            "heading": "",
            "empty_content_shell": True,
            "afstemning_nav_visible": True,
            "shell_markers_present": True,
        }
    }
    assert recon.calls == 1


def test_ui_daybooks_open_registration_has_empty_input_and_typed_output(
    tmp_path: Path,
) -> None:
    write_coverage_fixture(tmp_path)
    daybooks = FakeUiDaybooksOpenService()
    server = create_server(tmp_path, ui_daybooks_open_service=daybooks)
    tool = {item.name: item for item in asyncio.run(server.list_tools())}["ui_daybooks_open"]

    assert tool.parameters["properties"] == {}
    result = asyncio.run(server.call_tool("ui_daybooks_open", {}))

    assert result.structured_content == {
        "result": {
            "path_class": "/:org_slug/daybooks/new",
            "heading": "",
            "editor_markers_present": True,
            "shell_markers_present": True,
        }
    }
    assert daybooks.calls == 1


def test_ui_financing_open_registration_has_empty_input_and_typed_output(
    tmp_path: Path,
) -> None:
    write_coverage_fixture(tmp_path)
    financing = FakeUiFinancingOpenService()
    server = create_server(tmp_path, ui_financing_open_service=financing)
    tool = {item.name: item for item in asyncio.run(server.list_tools())}["ui_financing_open"]

    assert tool.parameters["properties"] == {}
    output_schema = tool.output_schema
    assert isinstance(output_schema, dict)
    schema = json.dumps(output_schema).lower()
    assert not any(term in schema for term in ("email", "password", "totp", "cookie", "token"))
    properties = cast(dict[str, Any], output_schema.get("properties") or {})
    assert "org_slug" not in properties
    assert "url" not in properties
    assert "apply" not in properties

    result = asyncio.run(server.call_tool("ui_financing_open", {}))

    assert result.structured_content == {
        "result": {
            "path_class": "/:org_slug/financing",
            "heading": "Ansøg om erhvervslån",
            "apply_cta_observed": True,
            "shell_markers_present": True,
        }
    }
    assert financing.calls == 1
