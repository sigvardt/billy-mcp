#!/usr/bin/env python3
"""Generate the maintained coverage inventories and their derived report.

The ``.yaml`` artifacts are JSON documents, which is a valid YAML subset. This
keeps the inventory dependency-free while preserving a machine-readable YAML
contract for later tooling.
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DOCS_URL = "https://www.billy.dk/api/"
# Official docs fingerprint promoted 2026-08-19 (89DEED22). Live intro cites
# GET /v2/organizations for the existing list row. Special /user/organizations
# is kept though absent from the current page.
DOCS_ETAG = "tmhc6wpdc835zt"
DOCS_MD5 = "053f755f52e3926b028e29325e3670d4"

# Dual-proved geo/reference UI families (research138 + research139 + research142
# + research143 + research144 + research147 + research148 + research149 +
# research150 specials delivery/logs + research162 productPrices): no
# equivalent mit.billy.dk workflow (nav absence + soft-empty path class ==
# nonsense). research139 adds currencies/locales after dual path contrast.
# research142 adds accountNatures/balanceModifiers after residual dual soft-empty.
# research143 adds accountGroups (7 ops including singular delete). research144
# adds contactBalancePostings (6) + invoiceReminderAssociations (7) +
# invoiceLateFees (6) = 19 join/meta ops. research147 adds contactBalancePayments
# (6 ops). research148 adds contactPersons (7 ops including singular delete).
# research149 adds invoiceReminders (5 ops; no singular update/delete in docs).
# research150 adds specials invoice_delivery + invoice_logs only (exact ids; never
# bare api.special. which would green invoice_email/files_upload/user_*).
# research162 adds productPrices (7 ops including singular delete; products list
# shell is products only — not a productPrices workflow).
GEO_UI_NOT_APPLICABLE_API_PREFIXES: tuple[str, ...] = (
    "api.accountGroups.",
    "api.accountNatures.",
    "api.balanceModifiers.",
    "api.cities.",
    "api.contactBalancePayments.",
    "api.contactBalancePostings.",
    "api.contactPersons.",
    "api.countries.",
    "api.countryGroups.",
    "api.currencies.",
    "api.invoiceLateFees.",
    "api.invoiceReminderAssociations.",
    "api.invoiceReminders.",
    "api.locales.",
    "api.productPrices.",
    "api.products.get",
    "api.products.update",
    "api.products.delete",
    "api.organizations.create",
    "api.accounts.get",
    "api.accounts.create",
    "api.accounts.update",
    "api.accounts.delete",
    "api.special.invoice_delivery",
    "api.special.invoice_logs",
    "api.special.invoice_email",
    "api.invoiceLines.get",
    "api.invoiceLines.list",
    "api.invoiceLines.create",
    "api.invoiceLines.update",
    "api.invoiceLines.delete",
    "api.daybooks.update",
    "api.billLines.get",
    "api.billLines.list",
    "api.billLines.create",
    "api.billLines.update",
    "api.billLines.delete",
    "api.users.get",
    "api.users.update",
    "api.daybookTransactions.get",
    "api.daybookTransactions.list",
    "api.daybookTransactions.update",
    "api.daybookTransactions.delete",
    "api.taxRates.get",
    "api.taxRates.create",
    "api.taxRates.update",
    "api.taxRates.delete",
    "api.salesTaxRulesets.get",
    "api.salesTaxRulesets.create",
    "api.salesTaxRulesets.update",
    "api.salesTaxRulesets.delete",
    "api.taxRateDeductionComponents.get",
    "api.taxRateDeductionComponents.list",
    "api.taxRateDeductionComponents.create",
    "api.taxRateDeductionComponents.update",
    "api.taxRateDeductionComponents.delete",
    "api.transactions.get",
    "api.transactions.update",
    "api.transactions.delete",
    "api.daybookTransactionLines.get",
    "api.daybookTransactionLines.list",
    "api.daybookTransactionLines.create",
    "api.daybookTransactionLines.update",
    "api.daybookTransactionLines.delete",
    "api.daybookBalanceAccounts.get",
    "api.daybookBalanceAccounts.list",
    "api.daybookBalanceAccounts.create",
    "api.daybookBalanceAccounts.update",
    "api.daybookBalanceAccounts.delete",
    "api.bankLines.get",
    "api.bankLines.list",
    "api.bankLines.create",
    "api.bankLines.update",
    "api.bankLines.delete",
    "api.bankPayments.get",
    "api.bankPayments.list",
    "api.bankPayments.create",
    "api.bankPayments.update",
    "api.bankPayments.delete",
    "api.bankLineMatches.get",
    "api.bankLineMatches.list",
    "api.bankLineMatches.create",
    "api.bankLineMatches.update",
    "api.bankLineMatches.delete",
    "api.bankLineSubjectAssociations.get",
    "api.bankLineSubjectAssociations.list",
    "api.bankLineSubjectAssociations.create",
    "api.bankLineSubjectAssociations.update",
    "api.bankLineSubjectAssociations.delete",
    "api.postings.get",
    "api.postings.list",
    "api.postings.create",
    "api.postings.update",
    "api.salesTaxAccounts.get",
    "api.salesTaxAccounts.list",
    "api.salesTaxAccounts.create",
    "api.salesTaxAccounts.update",
    "api.salesTaxAccounts.delete",
    "api.salesTaxRules.get",
    "api.salesTaxRules.list",
    "api.salesTaxRules.create",
    "api.salesTaxRules.update",
    "api.salesTaxRules.delete",
    "api.salesTaxMetaFields.get",
    "api.salesTaxMetaFields.list",
    "api.salesTaxMetaFields.create",
    "api.salesTaxMetaFields.update",
    "api.salesTaxMetaFields.delete",
    "api.salesTaxPayments.get",
    "api.salesTaxPayments.list",
    "api.salesTaxPayments.create",
    "api.salesTaxPayments.update",
    "api.salesTaxReturns.get",
    "api.salesTaxReturns.update",
    "api.files.list",
    "api.files.get",
    "api.attachments.get",
    "api.attachments.create",
    "api.attachments.update",
    "api.attachments.delete",
    "api.states.",
    "api.zipcodes.",
)
GEO_UI_NOT_APPLICABLE_EVIDENCE_CODE = "GEO_UI_NO_EQUIVALENT_WORKFLOW"
GEO_UI_NOT_APPLICABLE_ROW_COUNT = (
    268  # prior 258 + research190 product-plane bulk chrome dual NA empty list (10)
)
GEO_UI_NOT_APPLICABLE_RESEARCH139_RESOURCES: frozenset[str] = frozenset({"currencies", "locales"})
GEO_UI_NOT_APPLICABLE_RESEARCH142_RESOURCES: frozenset[str] = frozenset(
    {"accountNatures", "balanceModifiers"}
)
GEO_UI_NOT_APPLICABLE_RESEARCH143_RESOURCES: frozenset[str] = frozenset({"accountGroups"})
GEO_UI_NOT_APPLICABLE_RESEARCH144_RESOURCES: frozenset[str] = frozenset(
    {"contactBalancePostings", "invoiceLateFees", "invoiceReminderAssociations"}
)
GEO_UI_NOT_APPLICABLE_RESEARCH147_RESOURCES: frozenset[str] = frozenset({"contactBalancePayments"})
GEO_UI_NOT_APPLICABLE_RESEARCH148_RESOURCES: frozenset[str] = frozenset({"contactPersons"})
GEO_UI_NOT_APPLICABLE_RESEARCH149_RESOURCES: frozenset[str] = frozenset({"invoiceReminders"})
GEO_UI_NOT_APPLICABLE_RESEARCH162_RESOURCES: frozenset[str] = frozenset({"productPrices"})
# Exact full API special row ids (resource segment is "special" for all specials).
GEO_UI_NOT_APPLICABLE_RESEARCH150_SPECIAL_IDS: frozenset[str] = frozenset(
    {"api.special.invoice_delivery", "api.special.invoice_logs"}
)
# research176: products get/update/delete only
# (list/create stay tool-green; bulk external-contract red).
GEO_UI_NOT_APPLICABLE_RESEARCH176_PRODUCT_IDS: frozenset[str] = frozenset(
    {
        "api.products.get",
        "api.products.update",
        "api.products.delete",
    }
)
# research177: organizations.create only
# (list/get/update dual-count on ui_settings_company_open; bulk external-contract red).
GEO_UI_NOT_APPLICABLE_RESEARCH177_ORG_CREATE_IDS: frozenset[str] = frozenset(
    {"api.organizations.create"}
)
# research178: accounts get/create/update/delete only
# (list stays tool-green on ui_settings_accounting_open; bulk external-contract red).
GEO_UI_NOT_APPLICABLE_RESEARCH178_ACCOUNT_IDS: frozenset[str] = frozenset(
    {
        "api.accounts.get",
        "api.accounts.create",
        "api.accounts.update",
        "api.accounts.delete",
    }
)
# research178: special.invoice_email compose absence (exact special id).
GEO_UI_NOT_APPLICABLE_RESEARCH178_SPECIAL_IDS: frozenset[str] = frozenset(
    {"api.special.invoice_email"}
)
# research179: invoiceLines get/list/create/update/delete only
# (dedicated UI absent dual; embedded on invoices.update only; bulk external-contract red).
GEO_UI_NOT_APPLICABLE_RESEARCH179_INVOICE_LINE_IDS: frozenset[str] = frozenset(
    {
        "api.invoiceLines.get",
        "api.invoiceLines.list",
        "api.invoiceLines.create",
        "api.invoiceLines.update",
        "api.invoiceLines.delete",
    }
)
# research180: daybooks.update + billLines non-bulk + users.get/update
# (daybooks.delete producted; bulk external-contract red; users.list stays tool-green).
GEO_UI_NOT_APPLICABLE_RESEARCH180_DAYBOOKS_UPDATE_IDS: frozenset[str] = frozenset(
    {"api.daybooks.update"}
)
GEO_UI_NOT_APPLICABLE_RESEARCH180_BILL_LINE_IDS: frozenset[str] = frozenset(
    {
        "api.billLines.get",
        "api.billLines.list",
        "api.billLines.create",
        "api.billLines.update",
        "api.billLines.delete",
    }
)
GEO_UI_NOT_APPLICABLE_RESEARCH180_USERS_IDS: frozenset[str] = frozenset(
    {"api.users.get", "api.users.update"}
)
# research181: daybookTransactions get/list/update/delete dedicated absent dual
# (create producted as ui_daybook_transactions_create_open; bulk external-contract red)
# + taxRates get/create/update/delete (list stays tool-green on ui_settings_vat_open)
# + salesTaxRulesets get/create/update/delete (list stays tool-green on same VAT shell)
# + taxRateDeductionComponents get/list/create/update/delete (no dedicated surface)
# + transactions get/update/delete (list stays tool-green; create producted research182).
# research182: daybookTransactionLines get/list/create/update/delete (embedded-only).
GEO_UI_NOT_APPLICABLE_RESEARCH181_DAYBOOK_TX_IDS: frozenset[str] = frozenset(
    {
        "api.daybookTransactions.get",
        "api.daybookTransactions.list",
        "api.daybookTransactions.update",
        "api.daybookTransactions.delete",
    }
)
GEO_UI_NOT_APPLICABLE_RESEARCH181_TAX_RATE_IDS: frozenset[str] = frozenset(
    {
        "api.taxRates.get",
        "api.taxRates.create",
        "api.taxRates.update",
        "api.taxRates.delete",
    }
)
GEO_UI_NOT_APPLICABLE_RESEARCH181_SALES_TAX_RULESET_IDS: frozenset[str] = frozenset(
    {
        "api.salesTaxRulesets.get",
        "api.salesTaxRulesets.create",
        "api.salesTaxRulesets.update",
        "api.salesTaxRulesets.delete",
    }
)
GEO_UI_NOT_APPLICABLE_RESEARCH181_TAX_RATE_DEDUCTION_IDS: frozenset[str] = frozenset(
    {
        "api.taxRateDeductionComponents.get",
        "api.taxRateDeductionComponents.list",
        "api.taxRateDeductionComponents.create",
        "api.taxRateDeductionComponents.update",
        "api.taxRateDeductionComponents.delete",
    }
)
GEO_UI_NOT_APPLICABLE_RESEARCH181_TRANSACTIONS_IDS: frozenset[str] = frozenset(
    {
        "api.transactions.get",
        "api.transactions.update",
        "api.transactions.delete",
    }
)

GEO_UI_NOT_APPLICABLE_RESEARCH182_DAYBOOK_TRANSACTION_LINE_IDS: frozenset[str] = frozenset(
    {
        "api.daybookTransactionLines.get",
        "api.daybookTransactionLines.list",
        "api.daybookTransactionLines.create",
        "api.daybookTransactionLines.update",
        "api.daybookTransactionLines.delete",
    }
)

# research183: residual soft-empty dual NA freeze (exact non-bulk ids only).
# Keep greened parents exclusive: daybooks/daybookTransactions create, bank
# accounts/recon, transactions list/create, settings VAT, vat-declarations list.
# research184 dual-counts attachments.list + files.create on Bilag; NA files
# list/get; research185 NA attachments get/create/update/delete. Bulk/annual stay red.
GEO_UI_NOT_APPLICABLE_RESEARCH183_IDS: frozenset[str] = frozenset(
    {
        "api.daybookBalanceAccounts.get",
        "api.daybookBalanceAccounts.list",
        "api.daybookBalanceAccounts.create",
        "api.daybookBalanceAccounts.update",
        "api.daybookBalanceAccounts.delete",
        "api.bankLines.get",
        "api.bankLines.list",
        "api.bankLines.create",
        "api.bankLines.update",
        "api.bankLines.delete",
        "api.bankPayments.get",
        "api.bankPayments.list",
        "api.bankPayments.create",
        "api.bankPayments.update",
        "api.bankPayments.delete",
        "api.bankLineMatches.get",
        "api.bankLineMatches.list",
        "api.bankLineMatches.create",
        "api.bankLineMatches.update",
        "api.bankLineMatches.delete",
        "api.bankLineSubjectAssociations.get",
        "api.bankLineSubjectAssociations.list",
        "api.bankLineSubjectAssociations.create",
        "api.bankLineSubjectAssociations.update",
        "api.bankLineSubjectAssociations.delete",
        "api.postings.get",
        "api.postings.list",
        "api.postings.create",
        "api.postings.update",
        "api.salesTaxAccounts.get",
        "api.salesTaxAccounts.list",
        "api.salesTaxAccounts.create",
        "api.salesTaxAccounts.update",
        "api.salesTaxAccounts.delete",
        "api.salesTaxRules.get",
        "api.salesTaxRules.list",
        "api.salesTaxRules.create",
        "api.salesTaxRules.update",
        "api.salesTaxRules.delete",
        "api.salesTaxMetaFields.get",
        "api.salesTaxMetaFields.list",
        "api.salesTaxMetaFields.create",
        "api.salesTaxMetaFields.update",
        "api.salesTaxMetaFields.delete",
        "api.salesTaxPayments.get",
        "api.salesTaxPayments.list",
        "api.salesTaxPayments.create",
        "api.salesTaxPayments.update",
        "api.salesTaxReturns.get",
        "api.salesTaxReturns.update",
    }
)

# research184: files.list + files.get only — soft /files empty dual; Bilag SPA
# hits /v2/attachments not /v2/files (research184 dual). attachments.list dual-
# counted; residual attachments NA closed by research185. Bulk stays red.
GEO_UI_NOT_APPLICABLE_RESEARCH184_IDS: frozenset[str] = frozenset(
    {
        "api.files.list",
        "api.files.get",
    }
)

# research185: attachments get/create/update/delete only
# (list dual-counted on Bilag research184; upload create is files.create dual-
# count; bulk external-contract red; soft /attachments empty dual; Bilag no
# Slet/Gem/tbody dual).
GEO_UI_NOT_APPLICABLE_RESEARCH185_IDS: frozenset[str] = frozenset(
    {
        "api.attachments.get",
        "api.attachments.create",
        "api.attachments.update",
        "api.attachments.delete",
    }
)
GEO_UI_NOT_APPLICABLE_RESEARCH183_FAMILY: dict[str, dict[str, str]] = {
    "daybookBalanceAccounts": {
        "evidence_ref": "research183_daybook_balance_accounts_soft_empty_dual",
        "dual_agree_flag": "dual_agree_no_dedicated_daybookBalanceAccounts_surface",
        "family_label": "daybookBalanceAccounts.get+list+create+update+delete",
    },
    "bankLines": {
        "evidence_ref": "research183_bank_lines_soft_empty_dual",
        "dual_agree_flag": "dual_agree_no_dedicated_bankLines_surface",
        "family_label": "bankLines.get+list+create+update+delete",
    },
    "bankPayments": {
        "evidence_ref": "research183_bank_payments_soft_empty_dual",
        "dual_agree_flag": "dual_agree_no_dedicated_bankPayments_surface",
        "family_label": "bankPayments.get+list+create+update+delete",
    },
    "bankLineMatches": {
        "evidence_ref": "research183_bank_line_matches_soft_empty_dual",
        "dual_agree_flag": "dual_agree_no_dedicated_bankLineMatches_surface",
        "family_label": "bankLineMatches.get+list+create+update+delete",
    },
    "bankLineSubjectAssociations": {
        "evidence_ref": "research183_bank_line_subject_associations_soft_empty_dual",
        "dual_agree_flag": "dual_agree_no_dedicated_bankLineSubjectAssociations_surface",
        "family_label": "bankLineSubjectAssociations.get+list+create+update+delete",
    },
    "postings": {
        "evidence_ref": "research183_postings_soft_empty_dual",
        "dual_agree_flag": "dual_agree_no_dedicated_postings_surface",
        "family_label": "postings.get+list+create+update",
    },
    "salesTaxAccounts": {
        "evidence_ref": "research183_sales_tax_accounts_soft_empty_dual",
        "dual_agree_flag": "dual_agree_no_dedicated_salesTaxAccounts_surface",
        "family_label": "salesTaxAccounts.get+list+create+update+delete",
    },
    "salesTaxRules": {
        "evidence_ref": "research183_sales_tax_rules_soft_empty_dual",
        "dual_agree_flag": "dual_agree_no_dedicated_salesTaxRules_surface",
        "family_label": "salesTaxRules.get+list+create+update+delete",
    },
    "salesTaxMetaFields": {
        "evidence_ref": "research183_sales_tax_meta_fields_soft_empty_dual",
        "dual_agree_flag": "dual_agree_no_dedicated_salesTaxMetaFields_surface",
        "family_label": "salesTaxMetaFields.get+list+create+update+delete",
    },
    "salesTaxPayments": {
        "evidence_ref": "research183_sales_tax_payments_soft_empty_dual",
        "dual_agree_flag": "dual_agree_no_dedicated_salesTaxPayments_surface",
        "family_label": "salesTaxPayments.get+list+create+update",
    },
    "salesTaxReturns": {
        "evidence_ref": "research183_sales_tax_returns_get_update_soft_empty_dual",
        "dual_agree_flag": "dual_agree_no_salesTaxReturns_get_update_form_surface",
        "family_label": "salesTaxReturns.get+update",
    },
}
CURRENT_COVERAGE_PHASE = "phase_1_offline_api_reads_and_writes"
TEST_REFERENCE = "tests/coverage/test_coverage_inventory.py"
SERVER_REGISTRY_TEST_REFERENCE = "tests/unit/test_coverage_server.py"
UI_INVOICES_LIST_UNIT_TEST_REFERENCE = "tests/unit/test_browser.py"
UI_INVOICES_LIST_LIVE_TEST_REFERENCE = "tests/live/test_ui_invoices_list.py"
UI_INVOICES_LIST_MODEL_TEST_REFERENCE = "tests/test_models.py"
UI_INVOICES_LIST_TOOL_NAME = "ui_invoices_list"
UI_INVOICES_CREATE_OPEN_UNIT_TEST_REFERENCE = "tests/unit/test_browser.py"
UI_INVOICES_CREATE_OPEN_LIVE_TEST_REFERENCE = "tests/live/test_ui_invoices_create_open.py"
UI_INVOICES_CREATE_OPEN_MODEL_TEST_REFERENCE = "tests/test_models.py"
UI_INVOICES_CREATE_OPEN_TOOL_NAME = "ui_invoices_create_open"
UI_INVOICES_GET_OPEN_UNIT_TEST_REFERENCE = "tests/unit/test_browser.py"
UI_INVOICES_GET_OPEN_LIVE_TEST_REFERENCE = "tests/live/test_ui_invoices_get_open.py"
UI_INVOICES_GET_OPEN_MODEL_TEST_REFERENCE = "tests/test_models.py"
UI_INVOICES_GET_OPEN_TOOL_NAME = "ui_invoices_get_open"
UI_INVOICES_UPDATE_OPEN_UNIT_TEST_REFERENCE = "tests/unit/test_browser.py"
UI_INVOICES_UPDATE_OPEN_LIVE_TEST_REFERENCE = "tests/live/test_ui_invoices_update_open.py"
UI_INVOICES_UPDATE_OPEN_MODEL_TEST_REFERENCE = "tests/test_models.py"
UI_INVOICES_UPDATE_OPEN_TOOL_NAME = "ui_invoices_update_open"
UI_INVOICES_DELETE_OPEN_UNIT_TEST_REFERENCE = "tests/unit/test_browser.py"
UI_INVOICES_DELETE_OPEN_LIVE_TEST_REFERENCE = "tests/live/test_ui_invoices_delete_open.py"
UI_INVOICES_DELETE_OPEN_MODEL_TEST_REFERENCE = "tests/test_models.py"
UI_INVOICES_DELETE_OPEN_TOOL_NAME = "ui_invoices_delete_open"
UI_BILLS_CREATE_OPEN_UNIT_TEST_REFERENCE = "tests/unit/test_browser.py"
UI_BILLS_CREATE_OPEN_LIVE_TEST_REFERENCE = "tests/live/test_ui_bills_create_open.py"
UI_BILLS_CREATE_OPEN_MODEL_TEST_REFERENCE = "tests/test_models.py"
UI_BILLS_CREATE_OPEN_TOOL_NAME = "ui_bills_create_open"
UI_BILLS_GET_OPEN_UNIT_TEST_REFERENCE = "tests/unit/test_browser.py"
UI_BILLS_GET_OPEN_LIVE_TEST_REFERENCE = "tests/live/test_ui_bills_get_open.py"
UI_BILLS_GET_OPEN_MODEL_TEST_REFERENCE = "tests/test_models.py"
UI_BILLS_GET_OPEN_TOOL_NAME = "ui_bills_get_open"
UI_BILLS_UPDATE_OPEN_UNIT_TEST_REFERENCE = "tests/unit/test_browser.py"
UI_BILLS_UPDATE_OPEN_LIVE_TEST_REFERENCE = "tests/live/test_ui_bills_update_open.py"
UI_BILLS_UPDATE_OPEN_MODEL_TEST_REFERENCE = "tests/test_models.py"
UI_BILLS_UPDATE_OPEN_TOOL_NAME = "ui_bills_update_open"
UI_BILLS_DELETE_OPEN_UNIT_TEST_REFERENCE = "tests/unit/test_browser.py"
UI_BILLS_DELETE_OPEN_LIVE_TEST_REFERENCE = "tests/live/test_ui_bills_delete_open.py"
UI_BILLS_DELETE_OPEN_MODEL_TEST_REFERENCE = "tests/test_models.py"
UI_BILLS_DELETE_OPEN_TOOL_NAME = "ui_bills_delete_open"
UI_PRODUCTS_LIST_UNIT_TEST_REFERENCE = "tests/unit/test_browser.py"
UI_PRODUCTS_LIST_LIVE_TEST_REFERENCE = "tests/live/test_ui_products_list.py"
UI_PRODUCTS_LIST_MODEL_TEST_REFERENCE = "tests/test_models.py"
UI_PRODUCTS_LIST_TOOL_NAME = "ui_products_list"
UI_CLIENTS_LIST_UNIT_TEST_REFERENCE = "tests/unit/test_browser.py"
UI_CLIENTS_LIST_LIVE_TEST_REFERENCE = "tests/live/test_ui_clients_list.py"
UI_CLIENTS_LIST_MODEL_TEST_REFERENCE = "tests/test_models.py"
UI_CLIENTS_LIST_TOOL_NAME = "ui_clients_list"
UI_CLIENTS_CREATE_OPEN_UNIT_TEST_REFERENCE = "tests/unit/test_browser.py"
UI_CLIENTS_CREATE_OPEN_LIVE_TEST_REFERENCE = "tests/live/test_ui_clients_create_open.py"
UI_CLIENTS_CREATE_OPEN_MODEL_TEST_REFERENCE = "tests/test_models.py"
UI_CLIENTS_CREATE_OPEN_TOOL_NAME = "ui_clients_create_open"
UI_CLIENTS_GET_OPEN_UNIT_TEST_REFERENCE = "tests/unit/test_browser.py"
UI_CLIENTS_GET_OPEN_LIVE_TEST_REFERENCE = "tests/live/test_ui_clients_get_open.py"
UI_CLIENTS_GET_OPEN_MODEL_TEST_REFERENCE = "tests/test_models.py"
UI_CLIENTS_GET_OPEN_TOOL_NAME = "ui_clients_get_open"
UI_CLIENTS_UPDATE_OPEN_UNIT_TEST_REFERENCE = "tests/unit/test_browser.py"
UI_CLIENTS_UPDATE_OPEN_LIVE_TEST_REFERENCE = "tests/live/test_ui_clients_update_open.py"
UI_CLIENTS_UPDATE_OPEN_MODEL_TEST_REFERENCE = "tests/test_models.py"
UI_CLIENTS_UPDATE_OPEN_TOOL_NAME = "ui_clients_update_open"
UI_CLIENTS_DELETE_OPEN_UNIT_TEST_REFERENCE = "tests/unit/test_browser.py"
UI_CLIENTS_DELETE_OPEN_LIVE_TEST_REFERENCE = "tests/live/test_ui_clients_delete_open.py"
UI_CLIENTS_DELETE_OPEN_MODEL_TEST_REFERENCE = "tests/test_models.py"
UI_CLIENTS_DELETE_OPEN_TOOL_NAME = "ui_clients_delete_open"
UI_SUPPLIERS_CREATE_OPEN_UNIT_TEST_REFERENCE = "tests/unit/test_browser.py"
UI_SUPPLIERS_CREATE_OPEN_LIVE_TEST_REFERENCE = "tests/live/test_ui_suppliers_create_open.py"
UI_SUPPLIERS_CREATE_OPEN_MODEL_TEST_REFERENCE = "tests/test_models.py"
UI_SUPPLIERS_CREATE_OPEN_TOOL_NAME = "ui_suppliers_create_open"
UI_PRODUCTS_CREATE_OPEN_UNIT_TEST_REFERENCE = "tests/unit/test_browser.py"
UI_PRODUCTS_CREATE_OPEN_LIVE_TEST_REFERENCE = "tests/live/test_ui_products_create_open.py"
UI_PRODUCTS_CREATE_OPEN_MODEL_TEST_REFERENCE = "tests/test_models.py"
UI_PRODUCTS_CREATE_OPEN_TOOL_NAME = "ui_products_create_open"
UI_BANK_ACCOUNTS_LIST_UNIT_TEST_REFERENCE = "tests/unit/test_browser.py"
UI_BANK_ACCOUNTS_LIST_LIVE_TEST_REFERENCE = "tests/live/test_ui_bank_accounts_list.py"
UI_BANK_ACCOUNTS_LIST_MODEL_TEST_REFERENCE = "tests/test_models.py"
UI_BANK_ACCOUNTS_LIST_TOOL_NAME = "ui_bank_accounts_list"
UI_QUOTES_LIST_UNIT_TEST_REFERENCE = "tests/unit/test_browser.py"
UI_QUOTES_LIST_LIVE_TEST_REFERENCE = "tests/live/test_ui_quotes_list.py"
UI_QUOTES_LIST_MODEL_TEST_REFERENCE = "tests/test_models.py"
UI_QUOTES_LIST_TOOL_NAME = "ui_quotes_list"
UI_RECURRING_INVOICES_LIST_UNIT_TEST_REFERENCE = "tests/unit/test_browser.py"
UI_RECURRING_INVOICES_LIST_LIVE_TEST_REFERENCE = "tests/live/test_ui_recurring_invoices_list.py"
UI_RECURRING_INVOICES_LIST_MODEL_TEST_REFERENCE = "tests/test_models.py"
UI_RECURRING_INVOICES_LIST_TOOL_NAME = "ui_recurring_invoices_list"
UI_PRODUCTS_IMPORT_UNIT_TEST_REFERENCE = "tests/unit/test_browser.py"
UI_PRODUCTS_IMPORT_LIVE_TEST_REFERENCE = "tests/live/test_ui_products_import.py"
UI_PRODUCTS_IMPORT_MODEL_TEST_REFERENCE = "tests/test_models.py"
UI_PRODUCTS_IMPORT_TOOL_NAME = "ui_products_import"
UI_SUPPLIERS_LIST_UNIT_TEST_REFERENCE = "tests/unit/test_browser.py"
UI_SUPPLIERS_LIST_LIVE_TEST_REFERENCE = "tests/live/test_ui_suppliers_list.py"
UI_SUPPLIERS_LIST_MODEL_TEST_REFERENCE = "tests/test_models.py"
UI_SUPPLIERS_LIST_TOOL_NAME = "ui_suppliers_list"
UI_BILLS_LIST_UNIT_TEST_REFERENCE = "tests/unit/test_browser.py"
UI_BILLS_LIST_LIVE_TEST_REFERENCE = "tests/live/test_ui_bills_list.py"
UI_BILLS_LIST_MODEL_TEST_REFERENCE = "tests/test_models.py"
UI_BILLS_LIST_TOOL_NAME = "ui_bills_list"
UI_DEBTOR_BALANCES_LIST_UNIT_TEST_REFERENCE = "tests/unit/test_browser.py"
UI_DEBTOR_BALANCES_LIST_LIVE_TEST_REFERENCE = "tests/live/test_ui_debtor_balances_list.py"
UI_DEBTOR_BALANCES_LIST_MODEL_TEST_REFERENCE = "tests/test_models.py"
UI_DEBTOR_BALANCES_LIST_TOOL_NAME = "ui_debtor_balances_list"
UI_CREDITOR_BALANCES_LIST_UNIT_TEST_REFERENCE = "tests/unit/test_browser.py"
UI_CREDITOR_BALANCES_LIST_LIVE_TEST_REFERENCE = "tests/live/test_ui_creditor_balances_list.py"
UI_CREDITOR_BALANCES_LIST_MODEL_TEST_REFERENCE = "tests/test_models.py"
UI_CREDITOR_BALANCES_LIST_TOOL_NAME = "ui_creditor_balances_list"
UI_UPLOADS_LIST_UNIT_TEST_REFERENCE = "tests/unit/test_browser.py"
UI_UPLOADS_LIST_LIVE_TEST_REFERENCE = "tests/live/test_ui_uploads_list.py"
UI_UPLOADS_LIST_MODEL_TEST_REFERENCE = "tests/test_models.py"
UI_UPLOADS_LIST_TOOL_NAME = "ui_uploads_list"
UI_RECEIPT_INBOX_LIST_UNIT_TEST_REFERENCE = "tests/unit/test_browser.py"
UI_RECEIPT_INBOX_LIST_LIVE_TEST_REFERENCE = "tests/live/test_ui_receipt_inbox_list.py"
UI_RECEIPT_INBOX_LIST_MODEL_TEST_REFERENCE = "tests/test_models.py"
UI_RECEIPT_INBOX_LIST_TOOL_NAME = "ui_receipt_inbox_list"
UI_BANK_RECONCILIATION_OPEN_UNIT_TEST_REFERENCE = "tests/unit/test_browser.py"
UI_BANK_RECONCILIATION_OPEN_LIVE_TEST_REFERENCE = "tests/live/test_ui_bank_reconciliation_open.py"
UI_BANK_RECONCILIATION_OPEN_MODEL_TEST_REFERENCE = "tests/test_models.py"
UI_BANK_RECONCILIATION_OPEN_TOOL_NAME = "ui_bank_reconciliation_open"
UI_FINANCING_OPEN_UNIT_TEST_REFERENCE = "tests/unit/test_browser.py"
UI_FINANCING_OPEN_LIVE_TEST_REFERENCE = "tests/live/test_ui_financing_open.py"
UI_FINANCING_OPEN_MODEL_TEST_REFERENCE = "tests/test_models.py"
UI_FINANCING_OPEN_TOOL_NAME = "ui_financing_open"
UI_DAYBOOKS_OPEN_UNIT_TEST_REFERENCE = "tests/unit/test_browser.py"
UI_DAYBOOKS_OPEN_LIVE_TEST_REFERENCE = "tests/live/test_ui_daybooks_open.py"
UI_DAYBOOKS_OPEN_MODEL_TEST_REFERENCE = "tests/test_models.py"
UI_DAYBOOKS_OPEN_TOOL_NAME = "ui_daybooks_open"
UI_DAYBOOKS_GET_OPEN_UNIT_TEST_REFERENCE = "tests/unit/test_browser.py"
UI_DAYBOOKS_GET_OPEN_LIVE_TEST_REFERENCE = "tests/live/test_ui_daybooks_get_open.py"
UI_DAYBOOKS_GET_OPEN_MODEL_TEST_REFERENCE = "tests/test_models.py"
UI_DAYBOOKS_GET_OPEN_TOOL_NAME = "ui_daybooks_get_open"
UI_DAYBOOKS_DELETE_OPEN_UNIT_TEST_REFERENCE = "tests/unit/test_browser.py"
UI_DAYBOOKS_DELETE_OPEN_LIVE_TEST_REFERENCE = "tests/live/test_ui_daybooks_delete_open.py"
UI_DAYBOOKS_DELETE_OPEN_MODEL_TEST_REFERENCE = "tests/test_models.py"
UI_DAYBOOKS_DELETE_OPEN_TOOL_NAME = "ui_daybooks_delete_open"
UI_DAYBOOK_TRANSACTIONS_CREATE_OPEN_UNIT_TEST_REFERENCE = "tests/unit/test_browser.py"
UI_DAYBOOK_TRANSACTIONS_CREATE_OPEN_LIVE_TEST_REFERENCE = (
    "tests/live/test_ui_daybook_transactions_create_open.py"
)
UI_DAYBOOK_TRANSACTIONS_CREATE_OPEN_MODEL_TEST_REFERENCE = "tests/test_models.py"
UI_DAYBOOK_TRANSACTIONS_CREATE_OPEN_TOOL_NAME = "ui_daybook_transactions_create_open"

UI_TRANSACTIONS_CREATE_OPEN_UNIT_TEST_REFERENCE = "tests/unit/test_browser.py"
UI_TRANSACTIONS_CREATE_OPEN_LIVE_TEST_REFERENCE = "tests/live/test_ui_transactions_create_open.py"
UI_TRANSACTIONS_CREATE_OPEN_MODEL_TEST_REFERENCE = "tests/test_models.py"
UI_TRANSACTIONS_CREATE_OPEN_TOOL_NAME = "ui_transactions_create_open"
UI_TRANSACTIONS_LIST_UNIT_TEST_REFERENCE = "tests/unit/test_browser.py"
UI_TRANSACTIONS_LIST_LIVE_TEST_REFERENCE = "tests/live/test_ui_transactions_list.py"
UI_TRANSACTIONS_LIST_MODEL_TEST_REFERENCE = "tests/test_models.py"
UI_TRANSACTIONS_LIST_TOOL_NAME = "ui_transactions_list"
UI_REPORTS_OPEN_UNIT_TEST_REFERENCE = "tests/unit/test_browser.py"
UI_REPORTS_OPEN_LIVE_TEST_REFERENCE = "tests/live/test_ui_reports_open.py"
UI_REPORTS_OPEN_MODEL_TEST_REFERENCE = "tests/test_models.py"
UI_REPORTS_OPEN_TOOL_NAME = "ui_reports_open"
UI_VAT_DECLARATIONS_LIST_UNIT_TEST_REFERENCE = "tests/unit/test_browser.py"
UI_VAT_DECLARATIONS_LIST_LIVE_TEST_REFERENCE = "tests/live/test_ui_vat_declarations_list.py"
UI_VAT_DECLARATIONS_LIST_MODEL_TEST_REFERENCE = "tests/test_models.py"
UI_VAT_DECLARATIONS_LIST_TOOL_NAME = "ui_vat_declarations_list"
UI_EXPORTS_OPEN_UNIT_TEST_REFERENCE = "tests/unit/test_browser.py"
UI_EXPORTS_OPEN_LIVE_TEST_REFERENCE = "tests/live/test_ui_exports_open.py"
UI_EXPORTS_OPEN_MODEL_TEST_REFERENCE = "tests/test_models.py"
UI_EXPORTS_OPEN_TOOL_NAME = "ui_exports_open"
UI_SAFT_EXPORTS_OPEN_UNIT_TEST_REFERENCE = "tests/unit/test_browser.py"
UI_SAFT_EXPORTS_OPEN_LIVE_TEST_REFERENCE = "tests/live/test_ui_saft_exports_open.py"
UI_SAFT_EXPORTS_OPEN_MODEL_TEST_REFERENCE = "tests/test_models.py"
UI_SAFT_EXPORTS_OPEN_TOOL_NAME = "ui_saft_exports_open"
UI_ADDONS_OPEN_UNIT_TEST_REFERENCE = "tests/unit/test_browser.py"
UI_ADDONS_OPEN_LIVE_TEST_REFERENCE = "tests/live/test_ui_addons_open.py"
UI_ADDONS_OPEN_MODEL_TEST_REFERENCE = "tests/test_models.py"
UI_ADDONS_OPEN_TOOL_NAME = "ui_addons_open"
UI_INTEGRATIONS_OPEN_UNIT_TEST_REFERENCE = "tests/unit/test_browser.py"
UI_INTEGRATIONS_OPEN_LIVE_TEST_REFERENCE = "tests/live/test_ui_integrations_open.py"
UI_INTEGRATIONS_OPEN_MODEL_TEST_REFERENCE = "tests/test_models.py"
UI_INTEGRATIONS_OPEN_TOOL_NAME = "ui_integrations_open"
UI_INVENTORY_OPEN_UNIT_TEST_REFERENCE = "tests/unit/test_browser.py"
UI_INVENTORY_OPEN_LIVE_TEST_REFERENCE = "tests/live/test_ui_inventory_open.py"
UI_INVENTORY_OPEN_MODEL_TEST_REFERENCE = "tests/test_models.py"
UI_INVENTORY_OPEN_TOOL_NAME = "ui_inventory_open"
UI_SETTINGS_COMPANY_OPEN_UNIT_TEST_REFERENCE = "tests/unit/test_browser.py"
UI_SETTINGS_COMPANY_OPEN_LIVE_TEST_REFERENCE = "tests/live/test_ui_settings_company_open.py"
UI_SETTINGS_COMPANY_OPEN_MODEL_TEST_REFERENCE = "tests/test_models.py"
UI_SETTINGS_COMPANY_OPEN_TOOL_NAME = "ui_settings_company_open"
UI_SETTINGS_ACCOUNTING_OPEN_UNIT_TEST_REFERENCE = "tests/unit/test_browser.py"
UI_SETTINGS_ACCOUNTING_OPEN_LIVE_TEST_REFERENCE = "tests/live/test_ui_settings_accounting_open.py"
UI_SETTINGS_ACCOUNTING_OPEN_MODEL_TEST_REFERENCE = "tests/test_models.py"
UI_SETTINGS_ACCOUNTING_OPEN_TOOL_NAME = "ui_settings_accounting_open"
UI_SETTINGS_INVOICING_OPEN_UNIT_TEST_REFERENCE = "tests/unit/test_browser.py"
UI_SETTINGS_INVOICING_OPEN_LIVE_TEST_REFERENCE = "tests/live/test_ui_settings_invoicing_open.py"
UI_SETTINGS_INVOICING_OPEN_MODEL_TEST_REFERENCE = "tests/test_models.py"
UI_SETTINGS_INVOICING_OPEN_TOOL_NAME = "ui_settings_invoicing_open"
UI_SETTINGS_USER_OPEN_UNIT_TEST_REFERENCE = "tests/unit/test_browser.py"
UI_SETTINGS_USER_OPEN_LIVE_TEST_REFERENCE = "tests/live/test_ui_settings_user_open.py"
UI_SETTINGS_USER_OPEN_MODEL_TEST_REFERENCE = "tests/test_models.py"
UI_SETTINGS_USER_OPEN_TOOL_NAME = "ui_settings_user_open"
UI_SETTINGS_USER_ORGANIZATIONS_OPEN_UNIT_TEST_REFERENCE = "tests/unit/test_browser.py"
UI_SETTINGS_USER_ORGANIZATIONS_OPEN_LIVE_TEST_REFERENCE = (
    "tests/live/test_ui_settings_user_organizations_open.py"
)
UI_SETTINGS_USER_ORGANIZATIONS_OPEN_MODEL_TEST_REFERENCE = "tests/test_models.py"
UI_SETTINGS_USER_ORGANIZATIONS_OPEN_TOOL_NAME = "ui_settings_user_organizations_open"
UI_SETTINGS_VAT_OPEN_UNIT_TEST_REFERENCE = "tests/unit/test_browser.py"
UI_SETTINGS_VAT_OPEN_LIVE_TEST_REFERENCE = "tests/live/test_ui_settings_vat_open.py"
UI_SETTINGS_VAT_OPEN_MODEL_TEST_REFERENCE = "tests/test_models.py"
UI_SETTINGS_VAT_OPEN_TOOL_NAME = "ui_settings_vat_open"
UI_SETTINGS_USERS_OPEN_UNIT_TEST_REFERENCE = "tests/unit/test_browser.py"
UI_SETTINGS_USERS_OPEN_LIVE_TEST_REFERENCE = "tests/live/test_ui_settings_users_open.py"
UI_SETTINGS_USERS_OPEN_MODEL_TEST_REFERENCE = "tests/test_models.py"
UI_SETTINGS_USERS_OPEN_TOOL_NAME = "ui_settings_users_open"
UI_SETTINGS_ACCESS_TOKEN_OPEN_UNIT_TEST_REFERENCE = "tests/unit/test_browser.py"
UI_SETTINGS_ACCESS_TOKEN_OPEN_LIVE_TEST_REFERENCE = (
    "tests/live/test_ui_settings_access_token_open.py"
)
UI_SETTINGS_ACCESS_TOKEN_OPEN_MODEL_TEST_REFERENCE = "tests/test_models.py"
UI_SETTINGS_ACCESS_TOKEN_OPEN_TOOL_NAME = "ui_settings_access_token_open"
UI_SETTINGS_BETA_OPEN_UNIT_TEST_REFERENCE = "tests/unit/test_browser.py"
UI_SETTINGS_BETA_OPEN_LIVE_TEST_REFERENCE = "tests/live/test_ui_settings_beta_open.py"
UI_SETTINGS_BETA_OPEN_MODEL_TEST_REFERENCE = "tests/test_models.py"
UI_SETTINGS_BETA_OPEN_TOOL_NAME = "ui_settings_beta_open"
UI_SETTINGS_SUBSCRIPTION_OPEN_UNIT_TEST_REFERENCE = "tests/unit/test_browser.py"
UI_SETTINGS_SUBSCRIPTION_OPEN_LIVE_TEST_REFERENCE = (
    "tests/live/test_ui_settings_subscription_open.py"
)
UI_SETTINGS_SUBSCRIPTION_OPEN_MODEL_TEST_REFERENCE = "tests/test_models.py"
UI_SETTINGS_SUBSCRIPTION_OPEN_TOOL_NAME = "ui_settings_subscription_open"
COMMON_ERRORS = ["AUTHENTICATION_REQUIRED", "OAUTH_INVALID_ACCESS_TOKEN"]
FILES_UPLOAD_ALIAS = "api.special.files_upload"
FILES_UPLOAD_TOOL_NAME = "api_files_upload_preview"
FILES_UPLOAD_REQUEST_FIELDS = [
    "file_bytes",
    "X-Access-Token",
    "X-Filename",
    "Content-Type",
    "x-create-attachment?",
    "x-create-variants?",
    "x-organizationid?",
    "x-should-scan?",
]
PAGING = {
    "parameters": ["page", "pageSize"],
    "page_size_default": 1000,
    "page_size_maximum": 1000,
    "response_fields": [
        "meta.paging.page",
        "meta.paging.pageCount",
        "meta.paging.pageSize",
        "meta.paging.total",
        "meta.paging.firstUrl",
        "meta.paging.previousUrl",
        "meta.paging.nextUrl",
        "meta.paging.lastUrl",
    ],
}

# The official Supports matrix frozen in the cited parent research brief. Every
# listed resource has get, list, bulk save, and bulk delete; the booleans are
# the only clear create/update/delete flags.
RESOURCE_SUPPORTS: tuple[tuple[str, bool, bool, bool], ...] = (
    ("accountGroups", True, True, True),
    ("accountNatures", True, True, False),
    ("accounts", True, True, True),
    ("attachments", True, True, True),
    ("balanceModifiers", True, True, False),
    ("bankLineMatches", True, True, True),
    ("bankLines", True, True, True),
    ("bankLineSubjectAssociations", True, True, True),
    ("bankPayments", True, True, True),
    ("billLines", True, True, True),
    ("bills", True, True, True),
    ("cities", True, True, False),
    ("contactBalancePayments", True, True, False),
    ("contactBalancePostings", True, True, False),
    ("contactPersons", True, True, True),
    ("contacts", True, True, True),
    ("countryGroups", True, True, False),
    ("countries", True, True, False),
    ("currencies", True, True, False),
    ("daybookBalanceAccounts", True, True, True),
    ("daybooks", True, True, True),
    ("daybookTransactionLines", True, True, True),
    ("daybookTransactions", True, True, True),
    ("files", True, False, False),
    ("invoiceLateFees", True, True, False),
    ("invoiceLines", True, True, True),
    ("invoiceReminderAssociations", True, True, True),
    ("invoiceReminders", True, False, False),
    ("invoices", True, True, True),
    ("locales", True, True, False),
    ("organizations", True, True, False),
    ("postings", True, True, False),
    ("productPrices", True, True, True),
    ("products", True, True, True),
    ("salesTaxAccounts", True, True, True),
    ("salesTaxMetaFields", True, True, True),
    ("salesTaxPayments", True, True, False),
    ("salesTaxReturns", False, True, False),
    ("salesTaxRules", True, True, True),
    ("salesTaxRulesets", True, True, True),
    ("states", True, True, False),
    ("taxRateDeductionComponents", True, True, True),
    ("taxRates", True, True, True),
    ("transactions", True, True, True),
    ("users", False, True, False),
    ("zipcodes", True, True, False),
)

INVOICE_FILTERS: dict[str, Any] = {
    "sortProperty": [
        "entryDate",
        "dueDate",
        "createdTime",
        "invoiceNo",
        "lineDescription",
        "amount",
        "grossAmount",
        "balance",
        "contact.name",
        "approvedTime",
        "orderNo",
    ],
    "sortDirection": ["ASC", "DESC"],
    "organizationId": "string",
    "contactId": "string",
    "creditedInvoiceId": "string",
    "state": ["draft", "approved", "voided"],
    "invoiceNo": "string",
    "externalId": "string",
    "minEntryDate": "date",
    "maxEntryDate": "date",
    "entryDatePeriod": [
        "all",
        "dates:A...B",
        "day:",
        "halfYear:",
        "month:",
        "quarter:",
        "year:",
        "fiscalYear:",
    ],
    "minApprovedTime": "date-time",
    "maxApprovedTime": "date-time",
    "approvedTimePeriod": [
        "all",
        "dates:…",
        "from:",
        "half:",
        "month:",
        "quarter:",
        "through:",
        "year:",
        "fiscalYear:",
    ],
    "minDueDate": "date",
    "maxDueDate": "date",
    "isPaid": "boolean",
    "currencyId": "string",
    "recurringInvoiceId": "string",
    "amount": "float",
    "quoteId": "string",
    "q": [
        "invoiceNo",
        "orderNo",
        "contact.name",
        "lineDescription",
        "amount",
        "amount+tax",
        "balance",
    ],
}

BILL_FILTERS: dict[str, Any] = {
    "sortProperty": [
        "entryDate",
        "dueDate",
        "createdTime",
        "lineDescription",
        "amount",
        "grossAmount",
        "balance",
        "contact.name",
        "voucherNo",
        "suppliersInvoiceNo",
        "attachments",
    ],
    "sortDirection": ["ASC", "DESC"],
    "organizationId": "string",
    "contactId": "string",
    "creditedBillId": "string",
    "minEntryDate": "date",
    "maxEntryDate": "date",
    "minDueDate": "date",
    "maxDueDate": "date",
    "isPaid": "boolean",
    "hasAttachments": "boolean",
    "state": ["draft", "approved", "voided"],
    "currencyId": "string",
    "suppliersInvoiceNo": "string",
    "isBare": "boolean",
    "amount": "float",
    "q": [
        "contact.name",
        "lineDescription",
        "voucherNo",
        "amount",
        "suppliersInvoiceNo",
        "balance",
    ],
}

DAYBOOK_TRANSACTION_FILTERS: dict[str, Any] = {
    "sortProperty": ["priority", "entryDate", "createdTime"],
    "sortDirection": ["ASC", "DESC"],
    "organizationId": "string",
    "daybookId": "string",
    "apiType": "string",
    "state": ["draft", "approved", "voided"],
    "minEntryDate": "date",
    "maxEntryDate": "date",
    "q": ["description", "extendedDescription", "voucherNo"],
}

GEO_COUNTRY_ID_FILTER: dict[str, Any] = {
    "countryId": {"type": "string", "required": True},
}
LIVE_GEO_COUNTRY_ID_EVIDENCE = (
    "Cited Wave-4 Grok brief: unauthenticated list requests without a non-empty "
    "countryId return Billy 400 OTHER before authentication."
)

LIST_FILTERS: dict[str, dict[str, Any]] = {
    "invoices": INVOICE_FILTERS,
    "bills": BILL_FILTERS,
    "daybookTransactions": DAYBOOK_TRANSACTION_FILTERS,
    "cities": GEO_COUNTRY_ID_FILTER,
    "states": GEO_COUNTRY_ID_FILTER,
    "zipcodes": GEO_COUNTRY_ID_FILTER,
}

UI_DISCOVERY_FAMILIES: tuple[str, ...] = (
    "invoices",
    "invoices_create",
    "bills_create",
    "quotes",
    "recurring_invoices",
    "products",
    "products_create",
    "product_import",
    "customers",
    "clients_create",
    "suppliers_create",
    "debtor_balances",
    "creditor_balances",
    "uploads",
    "receipt_inbox",
    "purchases",
    "suppliers",
    "bank_accounts",
    "bank_reconciliation",
    "financing",
    "daybooks",
    "transactions",
    "reports",
    "vat_declarations",
    "annual_reports",
    "exports",
    "saft_exports",
    "addons",
    "integrations",
    "inventory",
    "settings_company",
    "settings_user",
    "settings_user_organizations",
    "settings_accounting",
    "settings_vat",
    "settings_invoicing",
    "settings_users",
    "settings_subscription",
    "settings_access_token",
    "settings_beta",
)

SINGULAR_ROOT_KEY_OVERRIDES = {
    "bankLineMatches": "bankLineMatch",
}
API_QUALIFICATION_FIELDS = ("discovered", "implemented", "contract_tested")
UI_QUALIFICATION_FIELDS = (
    "discovered",
    "implemented",
    "contract_tested",
    "live_tested",
    "vision_verified",
)
LIVE_API_OUT_OF_SCOPE = "out_of_scope_by_user"
LIVE_API_DEFERRED_KIND = "live_api_deferred"
LIVE_API_OWNER_SKIP = "LIVE_API_OWNER_SKIP"
# Lock promoted to the captured 2026-08-19 page; no remaining drift pair.
DOCS_ETAG_OBSERVED = DOCS_ETAG
DOCS_MD5_OBSERVED = DOCS_MD5

# Owner 96908DC6 / E004E7D5: open-only chrome is not a finished CUD write.
# Empty after FE6FA4B1 moved the last five residual writes to owner scope.
UI_CUD_PARITY_OPEN_ONLY_HONESTY_IDS: frozenset[str] = frozenset()
# Owner FE6FA4B1: residual writes with no unique safe CUD cycle, or Godkend persist.
UI_RESIDUAL_WRITE_OWNER_SCOPE: dict[str, str] = {
    "ui.parity.daybookTransactions.create": "GODKEND_HIGH_IMPACT_PROHIBITED",
    "ui.parity.transactions.create": "GODKEND_HIGH_IMPACT_PROHIBITED",
    "ui.parity.files.create": "FILES_NO_UI_DELETE",
    "ui.parity.daybooks.create": "DAYBOOKS_UNIQUE_PERSIST_ABSENT",
    "ui.parity.daybooks.delete": "DAYBOOKS_UNIQUE_PERSIST_ABSENT",
}
UI_RESIDUAL_WRITE_OWNER_SCOPE_REASON: dict[str, str] = {
    "GODKEND_HIGH_IMPACT_PROHIBITED": (
        "Godkend / Bogfoer / posting is prohibited (radio:96908DC6); posting is irreversible"
    ),
    "FILES_NO_UI_DELETE": ("Bilag Slet count 0 dual; no uniquely verifiable file delete cycle"),
    "DAYBOOKS_UNIQUE_PERSIST_ABSENT": (
        "unique_persist_token=none; no tagged create so no tagged delete cycle"
    ),
}
# Owner 58D7D0E1: accepted independent vision plus live FastMCP preview/execute.
# Family records cover sibling CUD rows. Do not green files or ledger.
UI_CUD_PARITY_PROVED_WRITE: dict[str, tuple[str, str]] = {
    "ui.parity.contacts.create": (
        "ui_clients_create_preview",
        "tmp/vision-records/ui_contacts_writes.json",
    ),
    "ui.parity.contacts.update": (
        "ui_clients_update_preview",
        "tmp/vision-records/ui_contacts_writes.json",
    ),
    "ui.parity.contacts.delete": (
        "ui_clients_delete_preview",
        "tmp/vision-records/ui_contacts_writes.json",
    ),
    "ui.parity.bills.create": (
        "ui_bills_create_preview",
        "tmp/vision-records/ui_bills_writes.json",
    ),
    "ui.parity.bills.update": (
        "ui_bills_update_preview",
        "tmp/vision-records/ui_bills_writes.json",
    ),
    "ui.parity.bills.delete": (
        "ui_bills_delete_preview",
        "tmp/vision-records/ui_bills_writes.json",
    ),
    "ui.parity.organizations.update": (
        "ui_organizations_update_preview",
        "tmp/vision-records/ui_organizations_writes.json",
    ),
    "ui.parity.invoices.create": (
        "ui_invoices_create_preview",
        "tmp/vision-records/ui_invoices_writes.json",
    ),
    "ui.parity.invoices.update": (
        "ui_invoices_update_preview",
        "tmp/vision-records/ui_invoices_writes.json",
    ),
    "ui.parity.invoices.delete": (
        "ui_invoices_delete_preview",
        "tmp/vision-records/ui_invoices_writes.json",
    ),
    "ui.parity.products.create": (
        "ui_products_create_preview",
        "tmp/vision-records/ui_products_writes.json",
    ),
}
UI_CUD_PROVED_PARITY_STATUS = "preview_execute"
OPEN_ONLY_PARITY_STATUSES: frozenset[str] = frozenset(
    {
        "form_open_only",
        "create_chrome_open_only",
        "delete_chrome_open_only",
    }
)
# After 93D7A063 accept+purge: CUD parity names preview tools.
# 58D7D0E1 proved apply greens these rows. Discovery/get-open stay *_open.
UI_CONTACTS_CUD_PREVIEW_TOOL_NAMES: dict[str, str] = {
    "ui.parity.contacts.create": "ui_clients_create_preview",
    "ui.parity.contacts.update": "ui_clients_update_preview",
    "ui.parity.contacts.delete": "ui_clients_delete_preview",
}
# After bills CUD accept+purge: CUD parity names preview tools.
# 58D7D0E1 proved apply greens these rows. Discovery/get-open stay *_open.
UI_BILLS_CUD_PREVIEW_TOOL_NAMES: dict[str, str] = {
    "ui.parity.bills.create": "ui_bills_create_preview",
    "ui.parity.bills.update": "ui_bills_update_preview",
    "ui.parity.bills.delete": "ui_bills_delete_preview",
}
# After 23709235 accept+purge: update CUD names the preview tool.
# 58D7D0E1 proved apply greens this row. Discovery/list/get stay *_open.
UI_ORGANIZATIONS_UPDATE_PREVIEW_TOOL_NAMES: dict[str, str] = {
    "ui.parity.organizations.update": "ui_organizations_update_preview",
}
# After 60b6d620 accept+purge: invoice CUD names preview tools.
# 58D7D0E1 proved apply greens these rows. Discovery/list/get stay *_open.
UI_INVOICES_CUD_PREVIEW_TOOL_NAMES: dict[str, str] = {
    "ui.parity.invoices.create": "ui_invoices_create_preview",
    "ui.parity.invoices.update": "ui_invoices_update_preview",
    "ui.parity.invoices.delete": "ui_invoices_delete_preview",
}
# After 29c1b1de accept+purge: product create names the preview tool.
# 58D7D0E1 proved apply greens this row. Discovery stays *_open.
UI_PRODUCTS_CREATE_PREVIEW_TOOL_NAMES: dict[str, str] = {
    "ui.parity.products.create": "ui_products_create_preview",
}


# The inventory is generated from this narrow, source-controlled map rather
# than hand-editing checked-in generated artifacts. Each entry is a real module
# contract suite plus the root registry assertion that exposes the tool.
OFFLINE_API_IMPLEMENTATION_EVIDENCE: dict[str, tuple[str, ...]] = {
    "api.special.user_get": ("tests/api/test_bootstrap_reads.py", SERVER_REGISTRY_TEST_REFERENCE),
    "api.special.user_organizations": (
        "tests/api/test_bootstrap_reads.py",
        SERVER_REGISTRY_TEST_REFERENCE,
    ),
    "api.special.invoice_logs": (
        "tests/api/test_invoice_log_reads.py",
        SERVER_REGISTRY_TEST_REFERENCE,
    ),
    "api.special.invoice_email": (
        "tests/api/test_invoice_email_delivery_writes.py",
        SERVER_REGISTRY_TEST_REFERENCE,
    ),
    "api.special.invoice_delivery": (
        "tests/api/test_invoice_email_delivery_writes.py",
        SERVER_REGISTRY_TEST_REFERENCE,
    ),
    "api.organizations.get": ("tests/api/test_bootstrap_reads.py", SERVER_REGISTRY_TEST_REFERENCE),
    "api.organizations.list": ("tests/api/test_bootstrap_reads.py", SERVER_REGISTRY_TEST_REFERENCE),
    "api.organizations.create": (
        "tests/api/test_organization_writes.py",
        SERVER_REGISTRY_TEST_REFERENCE,
    ),
    "api.organizations.update": (
        "tests/api/test_organization_writes.py",
        SERVER_REGISTRY_TEST_REFERENCE,
    ),
    "api.currencies.get": ("tests/api/test_reference_reads.py", SERVER_REGISTRY_TEST_REFERENCE),
    "api.currencies.list": ("tests/api/test_reference_reads.py", SERVER_REGISTRY_TEST_REFERENCE),
    "api.countries.get": ("tests/api/test_reference_reads.py", SERVER_REGISTRY_TEST_REFERENCE),
    "api.countries.list": ("tests/api/test_reference_reads.py", SERVER_REGISTRY_TEST_REFERENCE),
    "api.locales.get": ("tests/api/test_reference_reads.py", SERVER_REGISTRY_TEST_REFERENCE),
    "api.locales.list": ("tests/api/test_reference_reads.py", SERVER_REGISTRY_TEST_REFERENCE),
    "api.products.get": ("tests/api/test_catalog_reads.py", SERVER_REGISTRY_TEST_REFERENCE),
    "api.products.list": ("tests/api/test_catalog_reads.py", SERVER_REGISTRY_TEST_REFERENCE),
    "api.products.create": ("tests/api/test_catalog_writes.py", SERVER_REGISTRY_TEST_REFERENCE),
    "api.products.update": ("tests/api/test_catalog_writes.py", SERVER_REGISTRY_TEST_REFERENCE),
    "api.products.delete": ("tests/api/test_catalog_writes.py", SERVER_REGISTRY_TEST_REFERENCE),
    "api.productPrices.get": ("tests/api/test_catalog_reads.py", SERVER_REGISTRY_TEST_REFERENCE),
    "api.productPrices.list": ("tests/api/test_catalog_reads.py", SERVER_REGISTRY_TEST_REFERENCE),
    "api.productPrices.create": (
        "tests/api/test_catalog_writes.py",
        SERVER_REGISTRY_TEST_REFERENCE,
    ),
    "api.productPrices.update": (
        "tests/api/test_catalog_writes.py",
        SERVER_REGISTRY_TEST_REFERENCE,
    ),
    "api.productPrices.delete": (
        "tests/api/test_catalog_writes.py",
        SERVER_REGISTRY_TEST_REFERENCE,
    ),
    "api.contacts.get": ("tests/api/test_contact_reads.py", SERVER_REGISTRY_TEST_REFERENCE),
    "api.contacts.list": ("tests/api/test_contact_reads.py", SERVER_REGISTRY_TEST_REFERENCE),
    "api.contacts.create": ("tests/api/test_contact_writes.py", SERVER_REGISTRY_TEST_REFERENCE),
    "api.contacts.update": ("tests/api/test_contact_writes.py", SERVER_REGISTRY_TEST_REFERENCE),
    "api.contacts.delete": ("tests/api/test_contact_writes.py", SERVER_REGISTRY_TEST_REFERENCE),
    "api.invoices.get": ("tests/api/test_invoice_reads.py", SERVER_REGISTRY_TEST_REFERENCE),
    "api.invoices.list": ("tests/api/test_invoice_reads.py", SERVER_REGISTRY_TEST_REFERENCE),
    "api.invoices.create": ("tests/api/test_invoice_writes.py", SERVER_REGISTRY_TEST_REFERENCE),
    "api.invoices.update": ("tests/api/test_invoice_writes.py", SERVER_REGISTRY_TEST_REFERENCE),
    "api.invoices.delete": ("tests/api/test_invoice_writes.py", SERVER_REGISTRY_TEST_REFERENCE),
    "api.bills.get": ("tests/api/test_bill_reads.py", SERVER_REGISTRY_TEST_REFERENCE),
    "api.bills.list": ("tests/api/test_bill_reads.py", SERVER_REGISTRY_TEST_REFERENCE),
    "api.bills.create": ("tests/api/test_bill_writes.py", SERVER_REGISTRY_TEST_REFERENCE),
    "api.bills.update": ("tests/api/test_bill_writes.py", SERVER_REGISTRY_TEST_REFERENCE),
    "api.bills.delete": ("tests/api/test_bill_writes.py", SERVER_REGISTRY_TEST_REFERENCE),
    "api.daybookTransactions.get": (
        "tests/api/test_daybook_transaction_reads.py",
        SERVER_REGISTRY_TEST_REFERENCE,
    ),
    "api.daybookTransactions.list": (
        "tests/api/test_daybook_transaction_reads.py",
        SERVER_REGISTRY_TEST_REFERENCE,
    ),
    "api.daybookTransactions.create": (
        "tests/api/test_daybook_transaction_writes.py",
        SERVER_REGISTRY_TEST_REFERENCE,
    ),
    "api.daybookTransactions.update": (
        "tests/api/test_daybook_transaction_writes.py",
        SERVER_REGISTRY_TEST_REFERENCE,
    ),
    "api.daybookTransactions.delete": (
        "tests/api/test_daybook_transaction_writes.py",
        SERVER_REGISTRY_TEST_REFERENCE,
    ),
    "api.invoiceLines.get": ("tests/api/test_line_reads.py", SERVER_REGISTRY_TEST_REFERENCE),
    "api.invoiceLines.list": ("tests/api/test_line_reads.py", SERVER_REGISTRY_TEST_REFERENCE),
    "api.invoiceLines.create": (
        "tests/api/test_invoice_line_writes.py",
        SERVER_REGISTRY_TEST_REFERENCE,
    ),
    "api.invoiceLines.update": (
        "tests/api/test_invoice_line_writes.py",
        SERVER_REGISTRY_TEST_REFERENCE,
    ),
    "api.invoiceLines.delete": (
        "tests/api/test_invoice_line_writes.py",
        SERVER_REGISTRY_TEST_REFERENCE,
    ),
    "api.billLines.get": ("tests/api/test_line_reads.py", SERVER_REGISTRY_TEST_REFERENCE),
    "api.billLines.list": ("tests/api/test_line_reads.py", SERVER_REGISTRY_TEST_REFERENCE),
    "api.billLines.create": (
        "tests/api/test_bill_line_writes.py",
        SERVER_REGISTRY_TEST_REFERENCE,
    ),
    "api.billLines.update": (
        "tests/api/test_bill_line_writes.py",
        SERVER_REGISTRY_TEST_REFERENCE,
    ),
    "api.billLines.delete": (
        "tests/api/test_bill_line_writes.py",
        SERVER_REGISTRY_TEST_REFERENCE,
    ),
    "api.daybookTransactionLines.get": (
        "tests/api/test_line_reads.py",
        SERVER_REGISTRY_TEST_REFERENCE,
    ),
    "api.daybookTransactionLines.list": (
        "tests/api/test_line_reads.py",
        SERVER_REGISTRY_TEST_REFERENCE,
    ),
    "api.daybookTransactionLines.create": (
        "tests/api/test_daybook_transaction_line_writes.py",
        SERVER_REGISTRY_TEST_REFERENCE,
    ),
    "api.daybookTransactionLines.update": (
        "tests/api/test_daybook_transaction_line_writes.py",
        SERVER_REGISTRY_TEST_REFERENCE,
    ),
    "api.daybookTransactionLines.delete": (
        "tests/api/test_daybook_transaction_line_writes.py",
        SERVER_REGISTRY_TEST_REFERENCE,
    ),
    "api.contactPersons.get": (
        "tests/api/test_contact_person_reads.py",
        SERVER_REGISTRY_TEST_REFERENCE,
    ),
    "api.contactPersons.list": (
        "tests/api/test_contact_person_reads.py",
        SERVER_REGISTRY_TEST_REFERENCE,
    ),
    "api.contactPersons.create": (
        "tests/api/test_contact_person_writes.py",
        SERVER_REGISTRY_TEST_REFERENCE,
    ),
    "api.contactPersons.update": (
        "tests/api/test_contact_person_writes.py",
        SERVER_REGISTRY_TEST_REFERENCE,
    ),
    "api.contactPersons.delete": (
        "tests/api/test_contact_person_writes.py",
        SERVER_REGISTRY_TEST_REFERENCE,
    ),
    "api.daybooks.get": ("tests/api/test_daybook_reads.py", SERVER_REGISTRY_TEST_REFERENCE),
    "api.daybooks.list": ("tests/api/test_daybook_reads.py", SERVER_REGISTRY_TEST_REFERENCE),
    "api.daybooks.create": ("tests/api/test_daybook_writes.py", SERVER_REGISTRY_TEST_REFERENCE),
    "api.daybooks.update": ("tests/api/test_daybook_writes.py", SERVER_REGISTRY_TEST_REFERENCE),
    "api.daybooks.delete": ("tests/api/test_daybook_writes.py", SERVER_REGISTRY_TEST_REFERENCE),
    "api.daybookBalanceAccounts.get": (
        "tests/api/test_daybook_reads.py",
        SERVER_REGISTRY_TEST_REFERENCE,
    ),
    "api.daybookBalanceAccounts.list": (
        "tests/api/test_daybook_reads.py",
        SERVER_REGISTRY_TEST_REFERENCE,
    ),
    "api.daybookBalanceAccounts.create": (
        "tests/api/test_daybook_balance_account_writes.py",
        SERVER_REGISTRY_TEST_REFERENCE,
    ),
    "api.daybookBalanceAccounts.update": (
        "tests/api/test_daybook_balance_account_writes.py",
        SERVER_REGISTRY_TEST_REFERENCE,
    ),
    "api.daybookBalanceAccounts.delete": (
        "tests/api/test_daybook_balance_account_writes.py",
        SERVER_REGISTRY_TEST_REFERENCE,
    ),
    "api.accounts.get": ("tests/api/test_account_reads.py", SERVER_REGISTRY_TEST_REFERENCE),
    "api.accounts.list": ("tests/api/test_account_reads.py", SERVER_REGISTRY_TEST_REFERENCE),
    "api.accounts.create": ("tests/api/test_account_writes.py", SERVER_REGISTRY_TEST_REFERENCE),
    "api.accounts.update": ("tests/api/test_account_writes.py", SERVER_REGISTRY_TEST_REFERENCE),
    "api.accounts.delete": ("tests/api/test_account_writes.py", SERVER_REGISTRY_TEST_REFERENCE),
    "api.accountGroups.get": (
        "tests/api/test_account_reads.py",
        SERVER_REGISTRY_TEST_REFERENCE,
    ),
    "api.accountGroups.list": (
        "tests/api/test_account_reads.py",
        SERVER_REGISTRY_TEST_REFERENCE,
    ),
    "api.accountGroups.create": (
        "tests/api/test_account_writes.py",
        SERVER_REGISTRY_TEST_REFERENCE,
    ),
    "api.accountGroups.update": (
        "tests/api/test_account_writes.py",
        SERVER_REGISTRY_TEST_REFERENCE,
    ),
    "api.accountGroups.delete": (
        "tests/api/test_account_writes.py",
        SERVER_REGISTRY_TEST_REFERENCE,
    ),
    "api.accountNatures.get": (
        "tests/api/test_account_reads.py",
        SERVER_REGISTRY_TEST_REFERENCE,
    ),
    "api.accountNatures.list": (
        "tests/api/test_account_reads.py",
        SERVER_REGISTRY_TEST_REFERENCE,
    ),
    "api.files.get": (
        "tests/api/test_file_attachment_reads.py",
        SERVER_REGISTRY_TEST_REFERENCE,
    ),
    "api.files.list": (
        "tests/api/test_file_attachment_reads.py",
        SERVER_REGISTRY_TEST_REFERENCE,
    ),
    "api.files.create": ("tests/api/test_file_upload_writes.py", SERVER_REGISTRY_TEST_REFERENCE),
    "api.special.files_upload": (
        "tests/api/test_file_upload_writes.py",
        SERVER_REGISTRY_TEST_REFERENCE,
    ),
    "api.attachments.get": (
        "tests/api/test_file_attachment_reads.py",
        SERVER_REGISTRY_TEST_REFERENCE,
    ),
    "api.attachments.list": (
        "tests/api/test_file_attachment_reads.py",
        SERVER_REGISTRY_TEST_REFERENCE,
    ),
    "api.attachments.create": (
        "tests/api/test_attachment_writes.py",
        "tests/api/test_attachment_cross_executor.py",
        SERVER_REGISTRY_TEST_REFERENCE,
    ),
    "api.attachments.update": (
        "tests/api/test_attachment_writes.py",
        "tests/api/test_attachment_cross_executor.py",
        SERVER_REGISTRY_TEST_REFERENCE,
    ),
    "api.attachments.delete": (
        "tests/api/test_attachment_writes.py",
        "tests/api/test_attachment_cross_executor.py",
        SERVER_REGISTRY_TEST_REFERENCE,
    ),
    "api.countryGroups.get": ("tests/api/test_geo_reads.py", SERVER_REGISTRY_TEST_REFERENCE),
    "api.countryGroups.list": ("tests/api/test_geo_reads.py", SERVER_REGISTRY_TEST_REFERENCE),
    "api.cities.get": ("tests/api/test_geo_reads.py", SERVER_REGISTRY_TEST_REFERENCE),
    "api.cities.list": ("tests/api/test_geo_reads.py", SERVER_REGISTRY_TEST_REFERENCE),
    "api.states.get": ("tests/api/test_geo_reads.py", SERVER_REGISTRY_TEST_REFERENCE),
    "api.states.list": ("tests/api/test_geo_reads.py", SERVER_REGISTRY_TEST_REFERENCE),
    "api.zipcodes.get": ("tests/api/test_geo_reads.py", SERVER_REGISTRY_TEST_REFERENCE),
    "api.zipcodes.list": ("tests/api/test_geo_reads.py", SERVER_REGISTRY_TEST_REFERENCE),
    "api.taxRates.get": ("tests/api/test_tax_reads.py", SERVER_REGISTRY_TEST_REFERENCE),
    "api.taxRates.list": ("tests/api/test_tax_reads.py", SERVER_REGISTRY_TEST_REFERENCE),
    "api.taxRateDeductionComponents.get": (
        "tests/api/test_tax_reads.py",
        SERVER_REGISTRY_TEST_REFERENCE,
    ),
    "api.taxRateDeductionComponents.list": (
        "tests/api/test_tax_reads.py",
        SERVER_REGISTRY_TEST_REFERENCE,
    ),
    "api.taxRates.create": ("tests/api/test_tax_writes.py", SERVER_REGISTRY_TEST_REFERENCE),
    "api.taxRates.update": ("tests/api/test_tax_writes.py", SERVER_REGISTRY_TEST_REFERENCE),
    "api.taxRates.delete": ("tests/api/test_tax_writes.py", SERVER_REGISTRY_TEST_REFERENCE),
    "api.taxRateDeductionComponents.create": (
        "tests/api/test_tax_writes.py",
        SERVER_REGISTRY_TEST_REFERENCE,
    ),
    "api.taxRateDeductionComponents.update": (
        "tests/api/test_tax_writes.py",
        SERVER_REGISTRY_TEST_REFERENCE,
    ),
    "api.taxRateDeductionComponents.delete": (
        "tests/api/test_tax_writes.py",
        SERVER_REGISTRY_TEST_REFERENCE,
    ),
    "api.salesTaxRulesets.get": ("tests/api/test_tax_reads.py", SERVER_REGISTRY_TEST_REFERENCE),
    "api.salesTaxRulesets.list": ("tests/api/test_tax_reads.py", SERVER_REGISTRY_TEST_REFERENCE),
    "api.salesTaxRulesets.create": (
        "tests/api/test_sales_tax_writes.py",
        "tests/api/test_sales_tax_cross_executor.py",
        SERVER_REGISTRY_TEST_REFERENCE,
    ),
    "api.salesTaxRulesets.update": (
        "tests/api/test_sales_tax_writes.py",
        "tests/api/test_sales_tax_cross_executor.py",
        SERVER_REGISTRY_TEST_REFERENCE,
    ),
    "api.salesTaxRulesets.delete": (
        "tests/api/test_sales_tax_writes.py",
        "tests/api/test_sales_tax_cross_executor.py",
        SERVER_REGISTRY_TEST_REFERENCE,
    ),
    "api.salesTaxRules.get": ("tests/api/test_tax_reads.py", SERVER_REGISTRY_TEST_REFERENCE),
    "api.salesTaxRules.list": ("tests/api/test_tax_reads.py", SERVER_REGISTRY_TEST_REFERENCE),
    "api.salesTaxRules.create": (
        "tests/api/test_sales_tax_writes.py",
        "tests/api/test_sales_tax_cross_executor.py",
        SERVER_REGISTRY_TEST_REFERENCE,
    ),
    "api.salesTaxRules.update": (
        "tests/api/test_sales_tax_writes.py",
        "tests/api/test_sales_tax_cross_executor.py",
        SERVER_REGISTRY_TEST_REFERENCE,
    ),
    "api.salesTaxRules.delete": (
        "tests/api/test_sales_tax_writes.py",
        "tests/api/test_sales_tax_cross_executor.py",
        SERVER_REGISTRY_TEST_REFERENCE,
    ),
    "api.salesTaxAccounts.get": ("tests/api/test_tax_reads.py", SERVER_REGISTRY_TEST_REFERENCE),
    "api.salesTaxAccounts.list": ("tests/api/test_tax_reads.py", SERVER_REGISTRY_TEST_REFERENCE),
    "api.salesTaxAccounts.create": (
        "tests/api/test_sales_tax_account_meta_writes.py",
        "tests/api/test_sales_tax_account_meta_cross_executor.py",
        SERVER_REGISTRY_TEST_REFERENCE,
    ),
    "api.salesTaxAccounts.update": (
        "tests/api/test_sales_tax_account_meta_writes.py",
        "tests/api/test_sales_tax_account_meta_cross_executor.py",
        SERVER_REGISTRY_TEST_REFERENCE,
    ),
    "api.salesTaxAccounts.delete": (
        "tests/api/test_sales_tax_account_meta_writes.py",
        "tests/api/test_sales_tax_account_meta_cross_executor.py",
        SERVER_REGISTRY_TEST_REFERENCE,
    ),
    "api.salesTaxMetaFields.get": ("tests/api/test_tax_reads.py", SERVER_REGISTRY_TEST_REFERENCE),
    "api.salesTaxMetaFields.list": ("tests/api/test_tax_reads.py", SERVER_REGISTRY_TEST_REFERENCE),
    "api.salesTaxMetaFields.create": (
        "tests/api/test_sales_tax_account_meta_writes.py",
        "tests/api/test_sales_tax_account_meta_cross_executor.py",
        SERVER_REGISTRY_TEST_REFERENCE,
    ),
    "api.salesTaxMetaFields.update": (
        "tests/api/test_sales_tax_account_meta_writes.py",
        "tests/api/test_sales_tax_account_meta_cross_executor.py",
        SERVER_REGISTRY_TEST_REFERENCE,
    ),
    "api.salesTaxMetaFields.delete": (
        "tests/api/test_sales_tax_account_meta_writes.py",
        "tests/api/test_sales_tax_account_meta_cross_executor.py",
        SERVER_REGISTRY_TEST_REFERENCE,
    ),
    "api.salesTaxReturns.get": ("tests/api/test_tax_reads.py", SERVER_REGISTRY_TEST_REFERENCE),
    "api.salesTaxReturns.list": ("tests/api/test_tax_reads.py", SERVER_REGISTRY_TEST_REFERENCE),
    "api.salesTaxReturns.update": (
        "tests/api/test_sales_tax_return_writes.py",
        SERVER_REGISTRY_TEST_REFERENCE,
    ),
    "api.salesTaxPayments.get": ("tests/api/test_tax_reads.py", SERVER_REGISTRY_TEST_REFERENCE),
    "api.salesTaxPayments.list": ("tests/api/test_tax_reads.py", SERVER_REGISTRY_TEST_REFERENCE),
    "api.salesTaxPayments.create": (
        "tests/api/test_sales_tax_payment_writes.py",
        SERVER_REGISTRY_TEST_REFERENCE,
    ),
    "api.salesTaxPayments.update": (
        "tests/api/test_sales_tax_payment_writes.py",
        SERVER_REGISTRY_TEST_REFERENCE,
    ),
    "api.bankPayments.get": ("tests/api/test_bank_reads.py", SERVER_REGISTRY_TEST_REFERENCE),
    "api.bankPayments.list": ("tests/api/test_bank_reads.py", SERVER_REGISTRY_TEST_REFERENCE),
    "api.bankPayments.create": (
        "tests/api/test_bank_payment_writes.py",
        SERVER_REGISTRY_TEST_REFERENCE,
    ),
    "api.bankPayments.update": (
        "tests/api/test_bank_payment_writes.py",
        SERVER_REGISTRY_TEST_REFERENCE,
    ),
    "api.bankLineMatches.get": ("tests/api/test_bank_reads.py", SERVER_REGISTRY_TEST_REFERENCE),
    "api.bankLineMatches.list": ("tests/api/test_bank_reads.py", SERVER_REGISTRY_TEST_REFERENCE),
    "api.bankLineMatches.create": (
        "tests/api/test_bank_line_writes.py",
        "tests/api/test_bank_line_cross_executor.py",
        SERVER_REGISTRY_TEST_REFERENCE,
    ),
    "api.bankLineMatches.update": (
        "tests/api/test_bank_line_writes.py",
        "tests/api/test_bank_line_cross_executor.py",
        SERVER_REGISTRY_TEST_REFERENCE,
    ),
    "api.bankLineMatches.delete": (
        "tests/api/test_bank_line_writes.py",
        "tests/api/test_bank_line_cross_executor.py",
        SERVER_REGISTRY_TEST_REFERENCE,
    ),
    "api.bankLines.get": ("tests/api/test_bank_reads.py", SERVER_REGISTRY_TEST_REFERENCE),
    "api.bankLines.list": ("tests/api/test_bank_reads.py", SERVER_REGISTRY_TEST_REFERENCE),
    "api.bankLines.create": (
        "tests/api/test_bank_line_writes.py",
        "tests/api/test_bank_line_cross_executor.py",
        SERVER_REGISTRY_TEST_REFERENCE,
    ),
    "api.bankLines.update": (
        "tests/api/test_bank_line_writes.py",
        "tests/api/test_bank_line_cross_executor.py",
        SERVER_REGISTRY_TEST_REFERENCE,
    ),
    "api.bankLines.delete": (
        "tests/api/test_bank_line_writes.py",
        "tests/api/test_bank_line_cross_executor.py",
        SERVER_REGISTRY_TEST_REFERENCE,
    ),
    "api.bankLineSubjectAssociations.get": (
        "tests/api/test_bank_reads.py",
        SERVER_REGISTRY_TEST_REFERENCE,
    ),
    "api.bankLineSubjectAssociations.list": (
        "tests/api/test_bank_reads.py",
        SERVER_REGISTRY_TEST_REFERENCE,
    ),
    "api.bankLineSubjectAssociations.create": (
        "tests/api/test_bank_line_writes.py",
        "tests/api/test_bank_line_cross_executor.py",
        SERVER_REGISTRY_TEST_REFERENCE,
    ),
    "api.bankLineSubjectAssociations.update": (
        "tests/api/test_bank_line_writes.py",
        "tests/api/test_bank_line_cross_executor.py",
        SERVER_REGISTRY_TEST_REFERENCE,
    ),
    "api.bankLineSubjectAssociations.delete": (
        "tests/api/test_bank_line_writes.py",
        "tests/api/test_bank_line_cross_executor.py",
        SERVER_REGISTRY_TEST_REFERENCE,
    ),
    "api.balanceModifiers.get": ("tests/api/test_bank_reads.py", SERVER_REGISTRY_TEST_REFERENCE),
    "api.balanceModifiers.list": ("tests/api/test_bank_reads.py", SERVER_REGISTRY_TEST_REFERENCE),
    "api.contactBalancePayments.get": (
        "tests/api/test_balance_invoice_ext_reads.py",
        SERVER_REGISTRY_TEST_REFERENCE,
    ),
    "api.contactBalancePayments.list": (
        "tests/api/test_balance_invoice_ext_reads.py",
        SERVER_REGISTRY_TEST_REFERENCE,
    ),
    "api.contactBalancePayments.create": (
        "tests/api/test_contact_balance_payment_writes.py",
        SERVER_REGISTRY_TEST_REFERENCE,
    ),
    "api.contactBalancePayments.update": (
        "tests/api/test_contact_balance_payment_writes.py",
        SERVER_REGISTRY_TEST_REFERENCE,
    ),
    "api.contactBalancePostings.get": (
        "tests/api/test_balance_invoice_ext_reads.py",
        SERVER_REGISTRY_TEST_REFERENCE,
    ),
    "api.contactBalancePostings.list": (
        "tests/api/test_balance_invoice_ext_reads.py",
        SERVER_REGISTRY_TEST_REFERENCE,
    ),
    "api.invoiceLateFees.get": (
        "tests/api/test_balance_invoice_ext_reads.py",
        SERVER_REGISTRY_TEST_REFERENCE,
    ),
    "api.invoiceLateFees.list": (
        "tests/api/test_balance_invoice_ext_reads.py",
        SERVER_REGISTRY_TEST_REFERENCE,
    ),
    "api.invoiceLateFees.create": (
        "tests/api/test_invoice_late_fee_writes.py",
        SERVER_REGISTRY_TEST_REFERENCE,
    ),
    "api.invoiceLateFees.update": (
        "tests/api/test_invoice_late_fee_writes.py",
        SERVER_REGISTRY_TEST_REFERENCE,
    ),
    "api.invoiceReminders.get": (
        "tests/api/test_balance_invoice_ext_reads.py",
        SERVER_REGISTRY_TEST_REFERENCE,
    ),
    "api.invoiceReminders.list": (
        "tests/api/test_balance_invoice_ext_reads.py",
        SERVER_REGISTRY_TEST_REFERENCE,
    ),
    "api.invoiceReminders.create": (
        "tests/api/test_invoice_reminder_writes.py",
        SERVER_REGISTRY_TEST_REFERENCE,
    ),
    "api.invoiceReminderAssociations.get": (
        "tests/api/test_balance_invoice_ext_reads.py",
        SERVER_REGISTRY_TEST_REFERENCE,
    ),
    "api.invoiceReminderAssociations.list": (
        "tests/api/test_balance_invoice_ext_reads.py",
        SERVER_REGISTRY_TEST_REFERENCE,
    ),
    "api.transactions.get": ("tests/api/test_ledger_user_reads.py", SERVER_REGISTRY_TEST_REFERENCE),
    "api.transactions.list": (
        "tests/api/test_ledger_user_reads.py",
        SERVER_REGISTRY_TEST_REFERENCE,
    ),
    "api.postings.get": ("tests/api/test_ledger_user_reads.py", SERVER_REGISTRY_TEST_REFERENCE),
    "api.postings.list": ("tests/api/test_ledger_user_reads.py", SERVER_REGISTRY_TEST_REFERENCE),
    "api.users.get": ("tests/api/test_ledger_user_reads.py", SERVER_REGISTRY_TEST_REFERENCE),
    "api.users.list": ("tests/api/test_ledger_user_reads.py", SERVER_REGISTRY_TEST_REFERENCE),
    "api.users.update": ("tests/api/test_user_writes.py", SERVER_REGISTRY_TEST_REFERENCE),
}

WRITE_RESPONSE_FIELD_OVERRIDES: dict[tuple[str, str], list[str]] = {
    ("invoiceReminders", "create"): ["invoiceReminders[]"],
    ("organizations", "create"): ["organizations[]"],
}


def snake_case(value: str) -> str:
    """Return a stable planned-tool segment from an official resource name."""

    return re.sub(r"(?<!^)([A-Z])", r"_\1", value).lower()


def singular(value: str) -> str:
    """Return the documented JSON root-key shape without claiming field schemas."""

    if value in SINGULAR_ROOT_KEY_OVERRIDES:
        return SINGULAR_ROOT_KEY_OVERRIDES[value]
    if value.endswith("ies"):
        return f"{value[:-3]}y"
    return value[:-1] if value.endswith("s") else value


def red_status(*, discovered: bool) -> dict[str, Any]:
    """Return the Phase 0 status fields shared by all inventory rows."""

    return {
        "discovered": discovered,
        "implemented": False,
        "contract_tested": False,
        "live_tested": False,
        "vision_verified": None,
        "vision_evidence": None,
    }


def sensitivity_for(side_effects: str) -> str:
    """Classify frozen risk without turning a red row into a live qualification."""

    if side_effects == "none":
        return "low"
    if side_effects.startswith("high:") or "not_recoverable" in side_effects:
        return "high"
    if side_effects.startswith("unknown"):
        return "unknown"
    return "medium"


def base_api_row(
    *,
    row_id: str,
    area: str,
    operation: str,
    method_or_route: str,
    request_fields: list[str],
    response_fields: list[str],
    filters: dict[str, Any] | list[Any],
    pagination: dict[str, Any] | None,
    side_effects: str,
    cleanup: str,
    tool_name: str,
    source_kind: str,
    contract_status: str = "documented",
) -> dict[str, Any]:
    """Build one documented API row with all §12.1 and freeze fields."""

    offline_test_references = OFFLINE_API_IMPLEMENTATION_EVIDENCE.get(row_id, ())
    row: dict[str, Any] = {
        "id": row_id,
        "lane": "api",
        "area": area,
        "operation": operation,
        "method_or_route": method_or_route,
        "request_fields": request_fields,
        "response_fields": response_fields,
        "filters": filters,
        "pagination": pagination,
        "errors": COMMON_ERRORS,
        "sensitivity": sensitivity_for(side_effects),
        "side_effects": side_effects,
        "cleanup": cleanup,
        "tool_name": tool_name,
        "test_references": [TEST_REFERENCE, *offline_test_references],
        "evidence": f"{DOCS_URL} official API v2; docs etag {DOCS_ETAG}; MD5 {DOCS_MD5}",
        "source_kind": source_kind,
        "contract_status": contract_status,
    }
    row.update(red_status(discovered=True))
    if offline_test_references:
        row["implemented"] = True
        row["contract_tested"] = True
    return row


def standard_rows(resource: str, create: bool, update: bool, delete: bool) -> list[dict[str, Any]]:
    """Build clear conventional rows for one Supports resource."""

    area = snake_case(resource)
    singular_name = singular(resource)
    route = f"/v2/{resource}"
    list_filters = LIST_FILTERS.get(resource, {})
    list_request_fields = list(
        dict.fromkeys(
            ["page", "pageSize", "include", "sortProperty", "sortDirection", *list(list_filters)]
        )
    )
    rows = [
        base_api_row(
            row_id=f"api.{resource}.get",
            area=area,
            operation="get",
            method_or_route=f"GET {route}/:id",
            request_fields=["id", "include"],
            response_fields=[singular_name],
            filters=[],
            pagination=None,
            side_effects="none",
            cleanup="not_applicable",
            tool_name=f"api_{area}_get",
            source_kind="clear",
        ),
        base_api_row(
            row_id=f"api.{resource}.list",
            area=area,
            operation="list",
            method_or_route=f"GET {route}",
            request_fields=list_request_fields,
            response_fields=[f"{resource}[]", "meta.paging"],
            filters=list_filters,
            pagination=PAGING,
            side_effects="none",
            cleanup="not_applicable",
            tool_name=f"api_{area}_list",
            source_kind="clear",
        ),
    ]
    if resource in {"cities", "states", "zipcodes"}:
        rows[1]["contract_status"] = "documented_plus_live_observation"
        rows[1]["evidence"] = f"{rows[1]['evidence']}; {LIVE_GEO_COUNTRY_ID_EVIDENCE}"
    for operation, supported, method, side_effects, cleanup in (
        ("create", create, "POST", f"creates {singular_name}", "delete dedicated test resource"),
        ("update", update, "PUT", f"updates {singular_name}", "restore prior test state"),
        (
            "delete",
            delete,
            "DELETE",
            f"deletes {singular_name}",
            "not_recoverable; use disposable test data",
        ),
    ):
        if not supported:
            continue
        if resource == "bankPayments" and operation == "create":
            cleanup = (
                "void dedicated test resource via documented irreversible "
                "isVoided; independently verify"
            )
        if resource == "salesTaxPayments" and operation == "create":
            cleanup = (
                "live non-production cleanup strategy unqualified; singular DELETE is unsupported"
            )
        if (
            resource
            in {
                "contactBalancePayments",
                "invoiceLateFees",
                "invoiceReminders",
                "organizations",
            }
            and operation == "create"
        ):
            cleanup = (
                "live non-production cleanup strategy unqualified; singular DELETE is unsupported"
            )
        if resource == "users" and operation == "update":
            side_effects = "high: updates user PII and privilege flags"
            cleanup = (
                "must read and restore prior non-production user state via PUT before "
                "greening; singular DELETE is method-closed (405)"
            )
        if resource == "files" and operation == "create":
            row = base_api_row(
                row_id="api.files.create",
                area="files",
                operation="create",
                method_or_route="POST /v2/files",
                request_fields=FILES_UPLOAD_REQUEST_FIELDS,
                response_fields=["files[]", "attachments?"],
                filters=[],
                pagination=None,
                side_effects="high: uploads file content and may create attachment variants",
                cleanup=(
                    "delete only dedicated test attachments after live upload "
                    "contract qualification"
                ),
                tool_name="",
                source_kind="clear",
            )
            row["alias_of"] = FILES_UPLOAD_ALIAS
            rows.append(row)
            continue
        request_fields = [singular_name] if operation == "create" else ["id", singular_name]
        if operation == "delete":
            request_fields = ["id"]
        response_fields = WRITE_RESPONSE_FIELD_OVERRIDES.get(
            (resource, operation), ["changed_records[]", "meta.deletedRecords"]
        )
        rows.append(
            base_api_row(
                row_id=f"api.{resource}.{operation}",
                area=area,
                operation=operation,
                method_or_route=f"{method} {route}" + ("/:id" if operation != "create" else ""),
                request_fields=request_fields,
                response_fields=response_fields,
                filters=[],
                pagination=None,
                side_effects=side_effects,
                cleanup=cleanup,
                tool_name=f"api_{area}_{operation}_preview",
                source_kind="clear",
            )
        )
    return rows


RESIDUAL_EVIDENCE_REF_CHAIN = (
    "research186_residual_unauth+research191_unauth_reconfirm+research192_unauth_reconfirm"
)


def bulk_external_contract_qualification() -> dict[str, Any]:
    """Machine-readable external-contract freeze for ambiguous bulk rows.

    Research137 exhausted official docs and versioned assets: no exact bulk
    request/response schema. Live API qualification is out of user scope.
    Rows stay red (ambiguous_bulk); this is not greening and not a tool plan.
    """

    return {
        "kind": "external_contract_blocker",
        "blocker_code": "BULK_SCHEMA_UNSPECIFIED_OFFICIAL_DOCS",
        "docs_etag": DOCS_ETAG,
        "docs_md5": DOCS_MD5,
        "asset_sweep": "research137",
        "offline_shape": "research136",
        "reconfirm_ref": "research192_unauth_reconfirm",
        "live_api": "out_of_scope_by_user",
        "tools_allowed": False,
    }


# Research186 residual clear honesty: Supports write rows that must not plan tools.
# Unauth matrix matches live_probe._RESEARCH96_RESIDUAL_OUTCOMES (reconfirmed 2026-08-02).
RESIDUAL_METHOD_CLOSED_IDS: frozenset[str] = frozenset(
    {
        "api.accountNatures.create",
        "api.accountNatures.update",
        "api.balanceModifiers.create",
        "api.balanceModifiers.update",
        "api.bankPayments.delete",
        "api.cities.create",
        "api.cities.update",
        "api.contactBalancePostings.create",
        "api.contactBalancePostings.update",
        "api.countryGroups.create",
        "api.countryGroups.update",
        "api.countries.create",
        "api.countries.update",
        "api.currencies.create",
        "api.currencies.update",
        "api.invoiceReminderAssociations.create",
        "api.invoiceReminderAssociations.update",
        "api.locales.create",
        "api.locales.update",
        "api.postings.create",
        "api.postings.update",
        "api.states.create",
        "api.states.update",
        "api.zipcodes.create",
        "api.zipcodes.update",
    }
)
RESIDUAL_READONLY_MAP_IDS: frozenset[str] = frozenset(
    {
        "api.transactions.create",
        "api.transactions.update",
    }
)
RESIDUAL_META_DELETE_IDS: frozenset[str] = frozenset(
    {
        "api.transactions.delete",
        "api.invoiceReminderAssociations.delete",
    }
)
RESIDUAL_CLEAR_HONESTY_IDS: frozenset[str] = (
    RESIDUAL_METHOD_CLOSED_IDS | RESIDUAL_READONLY_MAP_IDS | RESIDUAL_META_DELETE_IDS
)


def method_closed_offline_qualification() -> dict[str, Any]:
    """Machine-readable freeze for unauth METHOD_NOT_ALLOWED residual clear writes.

    Research186 / research96: Supports optimism is overridden by unauth 405.
    Not greening and not a tool plan (offline_write_probe_rules rule 3).
    """

    return {
        "kind": "method_closed_offline",
        "blocker_code": "METHOD_NOT_ALLOWED_UNAUTH",
        "docs_etag": DOCS_ETAG,
        "docs_md5": DOCS_MD5,
        "evidence_ref": RESIDUAL_EVIDENCE_REF_CHAIN,
        "fixture_ref": "research96_residual_unauth",
        "live_api": "out_of_scope_by_user",
        "tools_allowed": False,
    }


def readonly_field_map_qualification() -> dict[str, Any]:
    """Freeze for auth-gated writes whose docs property table lacks writable fields."""

    return {
        "kind": "readonly_field_map_insufficient",
        "blocker_code": "READONLY_PROPERTY_TABLE",
        "docs_etag": DOCS_ETAG,
        "docs_md5": DOCS_MD5,
        "evidence_ref": RESIDUAL_EVIDENCE_REF_CHAIN,
        "unauth_status": 401,
        "live_api": "out_of_scope_by_user",
        "tools_allowed": False,
    }


def meta_delete_unqualified_qualification() -> dict[str, Any]:
    """Freeze for unauth 200 meta-only deletes without cleanup proof."""

    return {
        "kind": "meta_delete_unqualified",
        "blocker_code": "META_DELETE_NOT_CLEANUP_PROOF",
        "docs_etag": DOCS_ETAG,
        "docs_md5": DOCS_MD5,
        "evidence_ref": RESIDUAL_EVIDENCE_REF_CHAIN,
        "unauth_status": 200,
        "live_api": "out_of_scope_by_user",
        "tools_allowed": False,
    }


def apply_residual_clear_honesty(operations: list[dict[str, Any]]) -> None:
    """Clear false planned tool names and attach residual honesty qualifications.

    Inventory honesty only (research186). Keeps residual clear rows red and
    source_kind=clear. Never marks implemented/contract_tested.
    """

    method_closed_q = method_closed_offline_qualification()
    readonly_q = readonly_field_map_qualification()
    meta_delete_q = meta_delete_unqualified_qualification()
    for row in operations:
        row_id = str(row.get("id", ""))
        if row_id not in RESIDUAL_CLEAR_HONESTY_IDS:
            continue
        if row.get("source_kind") != "clear":
            continue
        row["tool_name"] = ""
        if row_id in RESIDUAL_METHOD_CLOSED_IDS:
            row["qualification"] = dict(method_closed_q)
            row["evidence"] = (
                f"{row.get('evidence', '')}; research186 unauth METHOD_NOT_ALLOWED "
                f"(405) overrides Supports for offline tools; "
                f"blocker_code={method_closed_q['blocker_code']}; "
                f"tools_allowed=false; live_api=out_of_scope_by_user; "
                "research96 residual fixture parity; research191/research192 unauth reconfirm"
            ).lstrip("; ")
        elif row_id in RESIDUAL_READONLY_MAP_IDS:
            row["qualification"] = dict(readonly_q)
            row["evidence"] = (
                f"{row.get('evidence', '')}; research186 unauth AUTHENTICATION_REQUIRED "
                "(401) opens method at auth gate but official property table is "
                "effectively readonly (no non-readonly create/update field map); "
                f"blocker_code={readonly_q['blocker_code']}; tools_allowed=false; "
                "do not freeze ticketed tools from Supports alone; "
                "research191/research192 unauth reconfirm"
            ).lstrip("; ")
        elif row_id in RESIDUAL_META_DELETE_IDS:
            row["qualification"] = dict(meta_delete_q)
            row["evidence"] = (
                f"{row.get('evidence', '')}; research186 unauth DELETE missing-id "
                "returns 200 meta-only (not cleanup proof, not live qualification); "
                f"blocker_code={meta_delete_q['blocker_code']}; tools_allowed=false; "
                "research191/research192 unauth reconfirm"
            ).lstrip("; ")
        # Hard honesty: residual must stay red and toolless.
        row["implemented"] = False
        row["contract_tested"] = False
        row["live_tested"] = False


def live_api_deferred_qualification() -> dict[str, Any]:
    """Live-API-only skip for implemented offline API rows (NODE.md requirement 2).

    Does not classify the operation itself out of scope. Does not green
    live_tested. tools_allowed is omitted so existing tools stay.
    """

    return {
        "kind": LIVE_API_DEFERRED_KIND,
        "scope_code": LIVE_API_OWNER_SKIP,
        "live_api": LIVE_API_OUT_OF_SCOPE,
        "docs_etag": DOCS_ETAG,
        "docs_md5": DOCS_MD5,
        "docs_etag_observed": DOCS_ETAG_OBSERVED,
        "docs_md5_observed": DOCS_MD5_OBSERVED,
    }


def apply_api_live_api_deferred(operations: list[dict[str, Any]]) -> None:
    """Attach live_api_deferred only where no qualification exists yet."""

    qualification = live_api_deferred_qualification()
    for row in operations:
        if row.get("qualification"):
            continue
        row["qualification"] = dict(qualification)
        row["live_tested"] = False


# Research187 UI product-plane bulk parity honesty: incomplete bulk UI rows that
# still need dual bulk-chrome evidence (design §10.2). Not NA, not greening.
UI_PRODUCT_PLANE_BULK_RESOURCES: frozenset[str] = frozenset(
    {
        "accounts",
        "attachments",
        "bankLineMatches",
        "bankLineSubjectAssociations",
        "bankLines",
        "bankPayments",
        "billLines",
        "bills",
        "contacts",
        "daybookBalanceAccounts",
        "daybookTransactionLines",
        "daybookTransactions",
        "daybooks",
        "files",
        "invoiceLines",
        "invoices",
        "organizations",
        "postings",
        "products",
        "salesTaxAccounts",
        "salesTaxMetaFields",
        "salesTaxPayments",
        "salesTaxReturns",
        "salesTaxRules",
        "salesTaxRulesets",
        "taxRateDeductionComponents",
        "taxRates",
        "transactions",
        "users",
    }
)
UI_PRODUCT_PLANE_BULK_HONESTY_IDS: frozenset[str] = frozenset(
    {
        f"ui.parity.{resource}.{op}"
        for resource in UI_PRODUCT_PLANE_BULK_RESOURCES
        for op in ("bulk_save", "bulk_delete")
    }
)


def ui_bulk_parity_discovery_required_qualification(
    resource: str, operation: str
) -> dict[str, Any]:
    """Machine-readable freeze for product-plane UI bulk parity discovery_required rows.

    Research187: dual bulk-chrome survey required before UI bulk NA or product.
    Linked to API bulk external-contract blocker. Not greening and not NA.
    """

    linked_api = f"api.{resource}.{operation}"
    return {
        "kind": "ui_bulk_parity_discovery_required",
        "blocker_code": "UI_BULK_CHROME_DUAL_REQUIRED",
        "tools_allowed": False,
        "docs_md5": DOCS_MD5,
        "docs_etag": DOCS_ETAG,
        "api_bulk_blocker": "BULK_SCHEMA_UNSPECIFIED_OFFICIAL_DOCS",
        "linked_api_row_id": linked_api,
        "evidence_ref": "research187",
        "not_applicable_decision": "deferred",
        "not_applicable_reason": (
            "Design §10.2 requires dual-session evidence that Billy exposes no "
            "equivalent bulk workflow (multi-select / bulk-action chrome) before "
            "UI bulk not_applicable. Inferring NA from API external_contract_blocker "
            "alone is forbidden. Browser credential refs were unset in research187; "
            "dual bulk-chrome not run."
        ),
    }


def apply_ui_cud_parity_open_only_honesty(workflows: list[dict[str, Any]]) -> None:
    """Stop treating open-only CUD parity chrome as implemented live writes.

    Keeps discovered and open-form contract_tested. Leaves tool_name on the
    existing *_open / list / shell tool until a preview tool exists.
    """

    if not UI_CUD_PARITY_OPEN_ONLY_HONESTY_IDS:
        return
    seen: set[str] = set()
    for row in workflows:
        row_id = str(row.get("id", ""))
        if row_id not in UI_CUD_PARITY_OPEN_ONLY_HONESTY_IDS:
            continue
        seen.add(row_id)
        if row.get("parity_status") not in OPEN_ONLY_PARITY_STATUSES:
            raise RuntimeError(
                f"{row_id} honesty requires an open-only parity_status, "
                f"got {row.get('parity_status')!r}"
            )
        row["implemented"] = False
        row["live_tested"] = False
        row["vision_verified"] = False
        prior = str(row.get("evidence") or "").strip()
        honesty = (
            "owner 96908DC6 / E004E7D5 CUD parity honesty: open-only chrome "
            "is not a finished create/update/delete write; implemented and "
            "live_tested stay false until ui_*_preview + ui_*_execute exist"
        )
        if honesty not in prior:
            row["evidence"] = f"{prior}; {honesty}" if prior else honesty
    missing = UI_CUD_PARITY_OPEN_ONLY_HONESTY_IDS - seen
    if missing:
        raise RuntimeError(f"CUD parity honesty missing rows: {sorted(missing)}")


def apply_ui_contacts_cud_preview_tool_names(workflows: list[dict[str, Any]]) -> None:
    """Point contacts CUD parity rows at preview tools after honesty.

    Leaves ``parity_status`` open-only. Proved apply later sets
    ``preview_execute``. Discovery and get-open stay on
    ``ui_clients_*_open``.
    """

    seen: set[str] = set()
    for row in workflows:
        row_id = str(row.get("id", ""))
        preview = UI_CONTACTS_CUD_PREVIEW_TOOL_NAMES.get(row_id)
        if preview is None:
            continue
        seen.add(row_id)
        row["tool_name"] = preview
    missing = set(UI_CONTACTS_CUD_PREVIEW_TOOL_NAMES) - seen
    if missing:
        raise RuntimeError(f"contacts CUD preview mapping missing rows: {sorted(missing)}")


def apply_ui_bills_cud_preview_tool_names(workflows: list[dict[str, Any]]) -> None:
    """Point bills CUD parity rows at preview tools after honesty.

    Leaves ``parity_status`` open-only. Proved apply later sets
    ``preview_execute``. Discovery and get-open stay on
    ``ui_bills_*_open``.
    """

    seen: set[str] = set()
    for row in workflows:
        row_id = str(row.get("id", ""))
        preview = UI_BILLS_CUD_PREVIEW_TOOL_NAMES.get(row_id)
        if preview is None:
            continue
        seen.add(row_id)
        row["tool_name"] = preview
    missing = set(UI_BILLS_CUD_PREVIEW_TOOL_NAMES) - seen
    if missing:
        raise RuntimeError(f"bills CUD preview mapping missing rows: {sorted(missing)}")


def apply_ui_organizations_update_preview_tool_name(workflows: list[dict[str, Any]]) -> None:
    """Point organizations update CUD at the preview tool after honesty.

    Leaves ``parity_status`` open-only. Proved apply later sets
    ``preview_execute``. Discovery, list, and get stay on
    ``ui_settings_company_open``.
    """

    seen: set[str] = set()
    for row in workflows:
        row_id = str(row.get("id", ""))
        preview = UI_ORGANIZATIONS_UPDATE_PREVIEW_TOOL_NAMES.get(row_id)
        if preview is None:
            continue
        seen.add(row_id)
        row["tool_name"] = preview
    missing = set(UI_ORGANIZATIONS_UPDATE_PREVIEW_TOOL_NAMES) - seen
    if missing:
        raise RuntimeError(f"organizations update preview mapping missing rows: {sorted(missing)}")


def apply_ui_invoices_cud_preview_tool_names(workflows: list[dict[str, Any]]) -> None:
    """Point invoices CUD parity rows at preview tools after honesty.

    Leaves ``parity_status`` open-only. Proved apply later sets
    ``preview_execute``. Discovery, list, and get stay on
    ``ui_invoices_*_open`` / ``ui_invoices_list``.
    """

    seen: set[str] = set()
    for row in workflows:
        row_id = str(row.get("id", ""))
        preview = UI_INVOICES_CUD_PREVIEW_TOOL_NAMES.get(row_id)
        if preview is None:
            continue
        seen.add(row_id)
        row["tool_name"] = preview
    missing = set(UI_INVOICES_CUD_PREVIEW_TOOL_NAMES) - seen
    if missing:
        raise RuntimeError(f"invoices CUD preview mapping missing rows: {sorted(missing)}")


def apply_ui_products_create_preview_tool_name(workflows: list[dict[str, Any]]) -> None:
    """Point products.create parity at the preview tool after honesty.

    Leaves ``parity_status`` open-only. Proved apply later sets
    ``preview_execute``. Discovery stays ``ui_products_create_open``.
    research176 get/update/delete stay toolless ``not_applicable``.
    """

    seen: set[str] = set()
    for row in workflows:
        row_id = str(row.get("id", ""))
        preview = UI_PRODUCTS_CREATE_PREVIEW_TOOL_NAMES.get(row_id)
        if preview is None:
            continue
        seen.add(row_id)
        row["tool_name"] = preview
    missing = set(UI_PRODUCTS_CREATE_PREVIEW_TOOL_NAMES) - seen
    if missing:
        raise RuntimeError(f"products create preview mapping missing rows: {sorted(missing)}")


def _vision_record_qualifies(root: Path, relative: str) -> bool:
    """True when the durable record is an independent accept with purge verified."""

    payload = json.loads((root / relative).read_text(encoding="utf-8"))
    return (
        payload.get("author") == "independent_review"
        and payload.get("reviewer_verdict") == "accept"
        and payload.get("purge_verified") is True
    )


def apply_ui_cud_proved_preview_execute(
    workflows: list[dict[str, Any]], *, root: Path = ROOT
) -> None:
    """Green the 11 accepted CUD rows after honesty and preview remaps.

    Requires a qualifying vision record and a preview tool name. Leaves
    ``vision_evidence`` null. Residual files and ledger writes are owner-scoped
    after this apply.
    """

    overlap = set(UI_CUD_PARITY_PROVED_WRITE) & UI_CUD_PARITY_OPEN_ONLY_HONESTY_IDS
    if overlap:
        raise RuntimeError(f"proved CUD ids still on honesty: {sorted(overlap)}")
    if len(UI_CUD_PARITY_PROVED_WRITE) != 11:
        raise RuntimeError(
            f"UI_CUD_PARITY_PROVED_WRITE must be exactly 11 (got {len(UI_CUD_PARITY_PROVED_WRITE)})"
        )
    seen: set[str] = set()
    for row in workflows:
        row_id = str(row.get("id", ""))
        mapping = UI_CUD_PARITY_PROVED_WRITE.get(row_id)
        if mapping is None:
            continue
        preview, record_rel = mapping
        seen.add(row_id)
        if not _vision_record_qualifies(root, record_rel):
            raise RuntimeError(
                f"{row_id} proved write missing qualifying vision record {record_rel}"
            )
        if row.get("tool_name") != preview:
            raise RuntimeError(
                f"{row_id} proved write requires tool_name {preview!r}, "
                f"got {row.get('tool_name')!r}"
            )
        row["parity_status"] = UI_CUD_PROVED_PARITY_STATUS
        row["implemented"] = True
        row["live_tested"] = True
        row["vision_verified"] = True
        cite = f"58D7D0E1 proved preview_execute; vision {record_rel}"
        prior = str(row.get("evidence") or "").strip()
        if cite not in prior:
            row["evidence"] = f"{prior}; {cite}" if prior else cite
    missing = set(UI_CUD_PARITY_PROVED_WRITE) - seen
    if missing:
        raise RuntimeError(f"proved CUD mapping missing rows: {sorted(missing)}")


def apply_ui_residual_write_out_of_scope_by_user(workflows: list[dict[str, Any]]) -> None:
    """Record FE6FA4B1 owner scope on residual files and ledger CUD rows.

    Keeps discovered and open-form contract_tested. Forces implemented, live,
    and vision false. Rejects not_applicable because nav and routes exist.
    Does not green. Does not invent ui_annual_* tools.
    """

    if len(UI_RESIDUAL_WRITE_OWNER_SCOPE) != 5:
        raise RuntimeError(
            "UI_RESIDUAL_WRITE_OWNER_SCOPE must be exactly 5 "
            f"(got {len(UI_RESIDUAL_WRITE_OWNER_SCOPE)})"
        )
    overlap_proved = set(UI_RESIDUAL_WRITE_OWNER_SCOPE) & set(UI_CUD_PARITY_PROVED_WRITE)
    if overlap_proved:
        raise RuntimeError(f"residual owner-scope ids still proved: {sorted(overlap_proved)}")
    overlap_honesty = set(UI_RESIDUAL_WRITE_OWNER_SCOPE) & UI_CUD_PARITY_OPEN_ONLY_HONESTY_IDS
    if overlap_honesty:
        raise RuntimeError(f"residual owner-scope ids still on honesty: {sorted(overlap_honesty)}")
    seen: set[str] = set()
    for row in workflows:
        row_id = str(row.get("id", ""))
        scope_code = UI_RESIDUAL_WRITE_OWNER_SCOPE.get(row_id)
        if scope_code is None:
            continue
        seen.add(row_id)
        reason = UI_RESIDUAL_WRITE_OWNER_SCOPE_REASON[scope_code]
        row["discovered"] = True
        row["contract_tested"] = True
        row["implemented"] = False
        row["live_tested"] = False
        row["vision_verified"] = False
        row["vision_evidence"] = None
        row["parity_status"] = "out_of_scope_by_user"
        row["qualification"] = {
            "kind": "out_of_scope_by_user",
            "scope_code": scope_code,
            "owner_decision_ref": "radio:FE6FA4B1",
            "owner_decision_date": "2026-08-19",
            "tools_allowed": False,
            "reason": reason,
            "not_applicable_decision": "rejected",
            "not_applicable_reason": (
                "nav and route exist; owner skip is safety or cleanup scope, "
                "not absence of a Billy UI workflow"
            ),
        }
        godkend = ""
        if scope_code == "GODKEND_HIGH_IMPACT_PROHIBITED":
            godkend = " radio:96908DC6 high-impact Godkend/Bogfoer prohibition;"
        cite = (
            "owner decision radio:FE6FA4B1 (2026-08-19): qualification.kind="
            f"out_of_scope_by_user scope_code={scope_code} tools_allowed=false; "
            f"not_applicable rejected;{godkend} {reason}; "
            "implemented/live/vision stay false"
        )
        prior = str(row.get("evidence") or "").strip()
        if "radio:FE6FA4B1" not in prior:
            row["evidence"] = f"{prior}; {cite}" if prior else cite
        route = str(row.get("method_or_route") or "")
        marker = "owner out_of_scope_by_user"
        if marker not in route:
            row["method_or_route"] = (
                f"{route} ({marker} scope_code={scope_code} radio:FE6FA4B1; "
                "not_applicable rejected)"
            )
    missing = set(UI_RESIDUAL_WRITE_OWNER_SCOPE) - seen
    if missing:
        raise RuntimeError(f"residual owner-scope missing rows: {sorted(missing)}")


def apply_ui_product_plane_bulk_parity_honesty(workflows: list[dict[str, Any]]) -> None:
    """Attach discovery_required qualifications to product-plane UI bulk parity rows.

    Inventory honesty only (research187). Keeps the 58 rows red and
    parity_status=discovery_required. Never marks implemented/live/vision.
    Skips rows already not_applicable (geo/reference dual freezes).
    """

    if len(UI_PRODUCT_PLANE_BULK_HONESTY_IDS) != 58:
        raise RuntimeError(
            "UI_PRODUCT_PLANE_BULK_HONESTY_IDS must be exactly 58 "
            f"(got {len(UI_PRODUCT_PLANE_BULK_HONESTY_IDS)})"
        )
    if len(UI_PRODUCT_PLANE_BULK_RESOURCES) != 29:
        raise RuntimeError(
            "UI_PRODUCT_PLANE_BULK_RESOURCES must be exactly 29 "
            f"(got {len(UI_PRODUCT_PLANE_BULK_RESOURCES)})"
        )

    for row in workflows:
        row_id = str(row.get("id", ""))
        if row_id not in UI_PRODUCT_PLANE_BULK_HONESTY_IDS:
            continue
        if row.get("parity_status") == "not_applicable":
            # Geo/reference dual freezes win; product-plane set should not overlap.
            continue
        # ui.parity.<resource>.bulk_save|bulk_delete
        parts = row_id.split(".")
        if len(parts) < 4:
            continue
        resource = parts[2]
        operation = parts[3]
        if resource not in UI_PRODUCT_PLANE_BULK_RESOURCES:
            continue
        if operation not in ("bulk_save", "bulk_delete"):
            continue

        qual = ui_bulk_parity_discovery_required_qualification(resource, operation)
        row["tool_name"] = ""
        row["parity_status"] = "discovery_required"
        row["qualification"] = dict(qual)
        prior = str(row.get("evidence") or "").strip()
        honesty = (
            "research187 UI product-plane bulk parity inventory honesty: "
            f"blocker_code={qual['blocker_code']}; tools_allowed=false; "
            f"api_bulk_blocker={qual['api_bulk_blocker']}; "
            f"linked_api_row_id={qual['linked_api_row_id']}; "
            "dual bulk-chrome required before not_applicable or product; "
            "not greening"
        )
        row["evidence"] = f"{prior}; {honesty}" if prior else honesty
        row["discovered"] = False
        row["implemented"] = False
        row["contract_tested"] = False
        row["live_tested"] = False
        row["vision_verified"] = False


# Research188 UI product-plane bulk chrome dual NA (strong subset only).
# Dual-absent multi-select/bulk-action chrome on non-empty greened list shells.
# Empty-shell family stays research187 honesty; soft VAT/users handled by
# research189 soft tool package.
UI_BULK_CHROME_ABSENT_DUAL_EVIDENCE_CODE = "UI_BULK_CHROME_ABSENT_DUAL"
UI_BULK_CHROME_DUAL_NA_STRONG_RESOURCES: frozenset[str] = frozenset(
    {
        "accounts",
        "attachments",
        "bankLineMatches",
        "bankLineSubjectAssociations",
        "bankLines",
        "bankPayments",
        "daybookBalanceAccounts",
        "daybookTransactionLines",
        "daybookTransactions",
        "daybooks",
        "files",
        "organizations",
        "postings",
        "products",
        "transactions",
    }
)
UI_BULK_CHROME_DUAL_NA_STRONG_IDS: frozenset[str] = frozenset(
    {
        f"ui.parity.{resource}.{op}"
        for resource in UI_BULK_CHROME_DUAL_NA_STRONG_RESOURCES
        for op in ("bulk_save", "bulk_delete")
    }
)
# resource -> greened list/open shell observed dual (research188)
UI_BULK_CHROME_DUAL_NA_STRONG_SHELLS: dict[str, dict[str, str]] = {
    "accounts": {
        "shell_id": "settings_accounting",
        "path_class": "/settings",
        "tool_ref": "ui_settings_accounting_open",
    },
    "attachments": {
        "shell_id": "uploads_list",
        "path_class": "/uploads",
        "tool_ref": "ui_uploads_list",
    },
    "files": {
        "shell_id": "uploads_list",
        "path_class": "/uploads",
        "tool_ref": "ui_uploads_list",
    },
    "bankLineMatches": {
        "shell_id": "bank_accounts_list",
        "path_class": "/bank-accounts",
        "tool_ref": "ui_bank_accounts_list",
    },
    "bankLineSubjectAssociations": {
        "shell_id": "bank_accounts_list",
        "path_class": "/bank-accounts",
        "tool_ref": "ui_bank_accounts_list",
    },
    "bankLines": {
        "shell_id": "bank_accounts_list",
        "path_class": "/bank-accounts",
        "tool_ref": "ui_bank_accounts_list",
    },
    "bankPayments": {
        "shell_id": "bank_accounts_list",
        "path_class": "/bank-accounts",
        "tool_ref": "ui_bank_accounts_list",
    },
    "daybookBalanceAccounts": {
        "shell_id": "daybooks_open",
        "path_class": "/daybooks/<id>",
        "tool_ref": "ui_daybooks_open",
    },
    "daybookTransactionLines": {
        "shell_id": "daybooks_open",
        "path_class": "/daybooks/<id>",
        "tool_ref": "ui_daybooks_open",
    },
    "daybookTransactions": {
        "shell_id": "daybooks_open",
        "path_class": "/daybooks/<id>",
        "tool_ref": "ui_daybooks_open",
    },
    "daybooks": {
        "shell_id": "daybooks_open",
        "path_class": "/daybooks/<id>",
        "tool_ref": "ui_daybooks_open",
    },
    "organizations": {
        "shell_id": "settings_company",
        "path_class": "/settings",
        "tool_ref": "ui_settings_company_open",
    },
    "postings": {
        "shell_id": "transactions_list",
        "path_class": "/transactions",
        "tool_ref": "ui_transactions_list",
    },
    "products": {
        "shell_id": "products_list",
        "path_class": "/products",
        "tool_ref": "ui_products_list",
    },
    "transactions": {
        "shell_id": "transactions_list",
        "path_class": "/transactions",
        "tool_ref": "ui_transactions_list",
    },
}


def ui_bulk_chrome_absent_dual_qualification(resource: str, operation: str) -> dict[str, Any]:
    """Machine-readable UI not_applicable for strong dual-absent bulk chrome rows."""

    shell = UI_BULK_CHROME_DUAL_NA_STRONG_SHELLS[resource]
    linked_api = f"api.{resource}.{operation}"
    return {
        "kind": "ui_not_applicable",
        "evidence_code": UI_BULK_CHROME_ABSENT_DUAL_EVIDENCE_CODE,
        "not_applicable_decision": "accepted",
        "not_applicable_reason": (
            "research188 dual independent ephemeral sessions: non-empty greened "
            "list/open shell exposes no multi-select / bulk-action chrome for this "
            "API bulk parity row; design §10.2 UI not_applicable accepted; no bulk "
            "FastMCP tool; empty-list shells and soft VAT/users seeds excluded"
        ),
        "sessions": "dual_independent_ephemeral",
        "docs_etag": DOCS_ETAG,
        "docs_md5": DOCS_MD5,
        "evidence_ref": "research188_bulk_chrome_dual",
        "tools_allowed": False,
        "empty_list_shell": False,
        "linked_api_row_id": linked_api,
        "shell_id": shell["shell_id"],
        "path_class": shell["path_class"],
        "tool_ref": shell["tool_ref"],
        "api_bulk_blocker": "BULK_SCHEMA_UNSPECIFIED_OFFICIAL_DOCS",
    }


def apply_ui_product_plane_bulk_chrome_dual_na_strong(
    workflows: list[dict[str, Any]],
) -> None:
    """Promote research188 strong dual-absent product-plane bulk rows to UI NA.

    Exact 15 resources / 30 bulk_save+bulk_delete UI parity ids only. Runs after
    research187 honesty so NA wins over discovery_required for this subset.
    Held empty-shell honesty rows are not touched (soft VAT/users handled by soft-tool package).
    """

    if len(UI_BULK_CHROME_DUAL_NA_STRONG_RESOURCES) != 15:
        raise RuntimeError(
            "UI_BULK_CHROME_DUAL_NA_STRONG_RESOURCES must be exactly 15 "
            f"(got {len(UI_BULK_CHROME_DUAL_NA_STRONG_RESOURCES)})"
        )
    if len(UI_BULK_CHROME_DUAL_NA_STRONG_IDS) != 30:
        raise RuntimeError(
            "UI_BULK_CHROME_DUAL_NA_STRONG_IDS must be exactly 30 "
            f"(got {len(UI_BULK_CHROME_DUAL_NA_STRONG_IDS)})"
        )
    if set(UI_BULK_CHROME_DUAL_NA_STRONG_SHELLS) != UI_BULK_CHROME_DUAL_NA_STRONG_RESOURCES:
        raise RuntimeError("shell map must cover exactly strong dual-NA resources")
    if not UI_BULK_CHROME_DUAL_NA_STRONG_IDS.issubset(UI_PRODUCT_PLANE_BULK_HONESTY_IDS):
        raise RuntimeError("strong dual-NA ids must be a subset of product-plane honesty ids")

    for row in workflows:
        row_id = str(row.get("id", ""))
        if row_id not in UI_BULK_CHROME_DUAL_NA_STRONG_IDS:
            continue
        parts = row_id.split(".")
        if len(parts) < 4:
            continue
        resource = parts[2]
        operation = parts[3]
        if resource not in UI_BULK_CHROME_DUAL_NA_STRONG_RESOURCES:
            continue
        if operation not in ("bulk_save", "bulk_delete"):
            continue

        shell = UI_BULK_CHROME_DUAL_NA_STRONG_SHELLS[resource]
        qual = ui_bulk_chrome_absent_dual_qualification(resource, operation)
        linked_api = qual["linked_api_row_id"]
        row["tool_name"] = ""
        row["parity_status"] = "not_applicable"
        row["discovered"] = True
        row["implemented"] = True
        row["contract_tested"] = True
        row["live_tested"] = True
        row["vision_verified"] = True
        row["vision_evidence"] = None
        row["sensitivity"] = "low"
        row["side_effects"] = (
            "none; UI bulk parity classified not_applicable — no bulk browser "
            "workflow tool and no records may be created through a bulk UI tool"
        )
        row["cleanup"] = (
            "not_applicable; no UI bulk tool and no disposable records for this parity row"
        )
        row["errors"] = [
            "AUTH_INTERACTION_REQUIRED",
            "UI_CHANGED",
            UI_BULK_CHROME_ABSENT_DUAL_EVIDENCE_CODE,
        ]
        row["method_or_route"] = (
            f"no equivalent mit.billy.dk bulk workflow for {linked_api} "
            f"(research188 dual-session: shell {shell['shell_id']} path_class "
            f"{shell['path_class']} non-empty greened list/open; dual_agree "
            "multi-select/bulk-action chrome absent; empty_list_shell=false; "
            f"evidence_code={UI_BULK_CHROME_ABSENT_DUAL_EVIDENCE_CODE}; "
            "not_applicable accepted)"
        )
        row["qualification"] = dict(qual)
        prior = str(row.get("evidence") or "").strip()
        na_evidence = (
            "research188 dual independent ephemeral browser sessions (no "
            f"BILLY_API_TOKEN): dual_agree_bulk_chrome_absent true on "
            f"{shell['shell_id']} ({shell['path_class']}; tool_ref="
            f"{shell['tool_ref']}); no multi-select row chrome / bulk-action "
            f"toolbar for {linked_api}; design §10.2 UI parity not_applicable "
            f"accepted; evidence_code={UI_BULK_CHROME_ABSENT_DUAL_EVIDENCE_CODE}; "
            "no ui_* bulk tool; API bulk lane unchanged "
            "(external_contract_blocker BULK_SCHEMA_UNSPECIFIED_OFFICIAL_DOCS; "
            "live_tested false out_of_scope_by_user); "
            "evidence_ref=research188_bulk_chrome_dual; "
            f"docs etag {DOCS_ETAG}; MD5 {DOCS_MD5}; empty_list_shell=false; "
            "held empty-shell contacts/invoices/bills not in this freeze; soft "
            "VAT/users promoted separately by research189 soft tool package"
        )
        row["evidence"] = f"{prior}; {na_evidence}" if prior else na_evidence


# Research189 UI product-plane bulk chrome dual NA (soft tool-panel subset).
# Dual-absent multi-select/bulk-action chrome on real greened tool panels
# (ui_settings_vat_open / ui_settings_users_open / ui_vat_declarations_list).
# Empty-shell contacts/invoices/bills(+lines) stay research187 honesty.
UI_BULK_CHROME_ABSENT_DUAL_TOOL_PANEL_EVIDENCE_CODE = "UI_BULK_CHROME_ABSENT_DUAL_TOOL_PANEL"
UI_BULK_CHROME_DUAL_NA_SOFT_TOOL_RESOURCES: frozenset[str] = frozenset(
    {
        "salesTaxAccounts",
        "salesTaxMetaFields",
        "salesTaxPayments",
        "salesTaxReturns",
        "salesTaxRules",
        "salesTaxRulesets",
        "taxRateDeductionComponents",
        "taxRates",
        "users",
    }
)
UI_BULK_CHROME_DUAL_NA_SOFT_TOOL_IDS: frozenset[str] = frozenset(
    {
        f"ui.parity.{resource}.{op}"
        for resource in UI_BULK_CHROME_DUAL_NA_SOFT_TOOL_RESOURCES
        for op in ("bulk_save", "bulk_delete")
    }
)
# resource -> greened tool panel observed dual (research189)
UI_BULK_CHROME_DUAL_NA_SOFT_TOOL_PANELS: dict[str, dict[str, str]] = {
    "salesTaxAccounts": {
        "shell_id": "settings_vat_tool",
        "path_class": "/settings",
        "tool_ref": "ui_settings_vat_open",
    },
    "salesTaxMetaFields": {
        "shell_id": "settings_vat_tool",
        "path_class": "/settings",
        "tool_ref": "ui_settings_vat_open",
    },
    "salesTaxPayments": {
        "shell_id": "settings_vat_tool",
        "path_class": "/settings",
        "tool_ref": "ui_settings_vat_open",
    },
    "salesTaxRules": {
        "shell_id": "settings_vat_tool",
        "path_class": "/settings",
        "tool_ref": "ui_settings_vat_open",
    },
    "salesTaxRulesets": {
        "shell_id": "settings_vat_tool",
        "path_class": "/settings",
        "tool_ref": "ui_settings_vat_open",
    },
    "taxRateDeductionComponents": {
        "shell_id": "settings_vat_tool",
        "path_class": "/settings",
        "tool_ref": "ui_settings_vat_open",
    },
    "taxRates": {
        "shell_id": "settings_vat_tool",
        "path_class": "/settings",
        "tool_ref": "ui_settings_vat_open",
    },
    "salesTaxReturns": {
        "shell_id": "vat_declarations_tool",
        "path_class": "/vat-declarations",
        "tool_ref": "ui_vat_declarations_list",
    },
    "users": {
        "shell_id": "settings_users_tool",
        "path_class": "/settings",
        "tool_ref": "ui_settings_users_open",
    },
}


def ui_bulk_chrome_absent_dual_tool_panel_qualification(
    resource: str, operation: str
) -> dict[str, Any]:
    """Machine-readable UI not_applicable for soft dual-absent tool-panel bulk rows."""

    panel = UI_BULK_CHROME_DUAL_NA_SOFT_TOOL_PANELS[resource]
    linked_api = f"api.{resource}.{operation}"
    return {
        "kind": "ui_not_applicable",
        "evidence_code": UI_BULK_CHROME_ABSENT_DUAL_TOOL_PANEL_EVIDENCE_CODE,
        "not_applicable_decision": "accepted",
        "not_applicable_reason": (
            "research189 dual independent ephemeral sessions: greened tool panel "
            "open succeeds and re-open bulk metrics show no multi-select / "
            "bulk-action chrome for this API bulk parity row; design §10.2 UI "
            "not_applicable accepted; no bulk FastMCP tool; empty-list shells "
            "excluded"
        ),
        "sessions": "dual_independent_ephemeral",
        "docs_etag": DOCS_ETAG,
        "docs_md5": DOCS_MD5,
        "evidence_ref": "research189_bulk_followon_dual",
        "tools_allowed": False,
        "empty_list_shell": False,
        "tool_panel": True,
        "linked_api_row_id": linked_api,
        "shell_id": panel["shell_id"],
        "path_class": panel["path_class"],
        "tool_ref": panel["tool_ref"],
        "api_bulk_blocker": "BULK_SCHEMA_UNSPECIFIED_OFFICIAL_DOCS",
    }


def apply_ui_product_plane_bulk_chrome_dual_na_soft_tool(
    workflows: list[dict[str, Any]],
) -> None:
    """Promote research189 soft tool dual-absent product-plane bulk rows to UI NA.

    Exact 9 resources / 18 bulk_save+bulk_delete UI parity ids only. Runs after
    research187 honesty and research188 strong dual-NA so NA wins over
    discovery_required for this subset. Empty-shell honesty rows are not touched.
    """

    if len(UI_BULK_CHROME_DUAL_NA_SOFT_TOOL_RESOURCES) != 9:
        raise RuntimeError(
            "UI_BULK_CHROME_DUAL_NA_SOFT_TOOL_RESOURCES must be exactly 9 "
            f"(got {len(UI_BULK_CHROME_DUAL_NA_SOFT_TOOL_RESOURCES)})"
        )
    if len(UI_BULK_CHROME_DUAL_NA_SOFT_TOOL_IDS) != 18:
        raise RuntimeError(
            "UI_BULK_CHROME_DUAL_NA_SOFT_TOOL_IDS must be exactly 18 "
            f"(got {len(UI_BULK_CHROME_DUAL_NA_SOFT_TOOL_IDS)})"
        )
    if set(UI_BULK_CHROME_DUAL_NA_SOFT_TOOL_PANELS) != UI_BULK_CHROME_DUAL_NA_SOFT_TOOL_RESOURCES:
        raise RuntimeError("panel map must cover exactly soft dual-NA resources")
    if not UI_BULK_CHROME_DUAL_NA_SOFT_TOOL_IDS.issubset(UI_PRODUCT_PLANE_BULK_HONESTY_IDS):
        raise RuntimeError("soft dual-NA ids must be a subset of product-plane honesty ids")
    if UI_BULK_CHROME_DUAL_NA_SOFT_TOOL_RESOURCES & UI_BULK_CHROME_DUAL_NA_STRONG_RESOURCES:
        raise RuntimeError("soft dual-NA resources must not overlap strong dual-NA resources")
    empty_held = {
        "contacts",
        "invoices",
        "invoiceLines",
        "bills",
        "billLines",
    }
    if UI_BULK_CHROME_DUAL_NA_SOFT_TOOL_RESOURCES & empty_held:
        raise RuntimeError("soft dual-NA resources must not include empty-shell held set")

    for row in workflows:
        row_id = str(row.get("id", ""))
        if row_id not in UI_BULK_CHROME_DUAL_NA_SOFT_TOOL_IDS:
            continue
        parts = row_id.split(".")
        if len(parts) < 4:
            continue
        resource = parts[2]
        operation = parts[3]
        if resource not in UI_BULK_CHROME_DUAL_NA_SOFT_TOOL_RESOURCES:
            continue
        if operation not in ("bulk_save", "bulk_delete"):
            continue

        panel = UI_BULK_CHROME_DUAL_NA_SOFT_TOOL_PANELS[resource]
        qual = ui_bulk_chrome_absent_dual_tool_panel_qualification(resource, operation)
        linked_api = qual["linked_api_row_id"]
        row["tool_name"] = ""
        row["parity_status"] = "not_applicable"
        row["discovered"] = True
        row["implemented"] = True
        row["contract_tested"] = True
        row["live_tested"] = True
        row["vision_verified"] = True
        row["vision_evidence"] = None
        row["sensitivity"] = "low"
        row["side_effects"] = (
            "none; UI bulk parity classified not_applicable — no bulk browser "
            "workflow tool and no records may be created through a bulk UI tool"
        )
        row["cleanup"] = (
            "not_applicable; no UI bulk tool and no disposable records for this parity row"
        )
        row["errors"] = [
            "AUTH_INTERACTION_REQUIRED",
            "UI_CHANGED",
            UI_BULK_CHROME_ABSENT_DUAL_TOOL_PANEL_EVIDENCE_CODE,
        ]
        row["method_or_route"] = (
            f"no equivalent mit.billy.dk bulk workflow for {linked_api} "
            f"(research189 dual-session: tool panel {panel['shell_id']} "
            f"tool_ref={panel['tool_ref']} path_class {panel['path_class']}; "
            "dual tool success + re-open dual_agree multi-select/bulk-action "
            "chrome absent; empty_list_shell=false; tool_panel=true; "
            f"evidence_code={UI_BULK_CHROME_ABSENT_DUAL_TOOL_PANEL_EVIDENCE_CODE}; "
            "not_applicable accepted)"
        )
        row["qualification"] = dict(qual)
        prior = str(row.get("evidence") or "").strip()
        na_evidence = (
            "research189 dual independent ephemeral browser sessions (no "
            f"BILLY_API_TOKEN): dual tool READY sessions; tool_ref="
            f"{panel['tool_ref']} success then re-open panel "
            f"{panel['shell_id']} ({panel['path_class']}); "
            "dual_agree_bulk_chrome_absent true (preference toggles on VAT "
            f"panel are non-row multi-select); no bulk-action chrome for "
            f"{linked_api}; design §10.2 UI parity not_applicable accepted; "
            f"evidence_code={UI_BULK_CHROME_ABSENT_DUAL_TOOL_PANEL_EVIDENCE_CODE}; "
            "no ui_* bulk tool; API bulk lane unchanged "
            "(external_contract_blocker BULK_SCHEMA_UNSPECIFIED_OFFICIAL_DOCS; "
            "live_tested false out_of_scope_by_user); "
            "evidence_ref=research189_bulk_followon_dual; "
            f"docs etag {DOCS_ETAG}; MD5 {DOCS_MD5}; empty_list_shell=false; "
            "tool_panel=true; held empty-shell contacts/invoices/bills not in "
            "this freeze"
        )
        row["evidence"] = f"{prior}; {na_evidence}" if prior else na_evidence


# Research190 UI product-plane bulk chrome dual NA (empty-list shell subset).
# Dual-absent multi-select/bulk-action chrome on real greened empty list shells
# (/clients/empty, /invoices/empty, /bills/empty). Completes product-plane bulk
# honesty freezes after research188 strong + research189 soft tool packages.
UI_BULK_CHROME_ABSENT_DUAL_EMPTY_LIST_EVIDENCE_CODE = "UI_BULK_CHROME_ABSENT_DUAL_EMPTY_LIST"
UI_BULK_CHROME_DUAL_NA_EMPTY_LIST_RESOURCES: frozenset[str] = frozenset(
    {
        "contacts",
        "invoices",
        "invoiceLines",
        "bills",
        "billLines",
    }
)
UI_BULK_CHROME_DUAL_NA_EMPTY_LIST_IDS: frozenset[str] = frozenset(
    {
        f"ui.parity.{resource}.{op}"
        for resource in UI_BULK_CHROME_DUAL_NA_EMPTY_LIST_RESOURCES
        for op in ("bulk_save", "bulk_delete")
    }
)
# resource -> greened empty list shell observed dual (research190)
UI_BULK_CHROME_DUAL_NA_EMPTY_LIST_SHELLS: dict[str, dict[str, str]] = {
    "contacts": {
        "shell_id": "clients_list",
        "path_class": "/clients/empty",
        "tool_ref": "ui_clients_list",
    },
    "invoices": {
        "shell_id": "invoices_list",
        "path_class": "/invoices/empty",
        "tool_ref": "ui_invoices_list",
    },
    "invoiceLines": {
        "shell_id": "invoices_list",
        "path_class": "/invoices/empty",
        "tool_ref": "ui_invoices_list",
    },
    "bills": {
        "shell_id": "bills_list",
        "path_class": "/bills/empty",
        "tool_ref": "ui_bills_list",
    },
    "billLines": {
        "shell_id": "bills_list",
        "path_class": "/bills/empty",
        "tool_ref": "ui_bills_list",
    },
}


def ui_bulk_chrome_absent_dual_empty_list_qualification(
    resource: str, operation: str
) -> dict[str, Any]:
    """Machine-readable UI not_applicable for empty-list dual-absent bulk rows."""

    shell = UI_BULK_CHROME_DUAL_NA_EMPTY_LIST_SHELLS[resource]
    linked_api = f"api.{resource}.{operation}"
    return {
        "kind": "ui_not_applicable",
        "evidence_code": UI_BULK_CHROME_ABSENT_DUAL_EMPTY_LIST_EVIDENCE_CODE,
        "not_applicable_decision": "accepted",
        "not_applicable_reason": (
            "research190 dual independent ephemeral sessions: greened empty "
            "list shells land on /…/empty with real h1 empty-state copy and no "
            "multi-select / bulk-action chrome for this API bulk parity row; "
            "design §10.2 UI not_applicable accepted; no bulk FastMCP tool; "
            "distinct from soft-empty nonsense control"
        ),
        "sessions": "dual_independent_ephemeral",
        "docs_etag": DOCS_ETAG,
        "docs_md5": DOCS_MD5,
        "evidence_ref": "research190_empty_shell_dual",
        "tools_allowed": False,
        "empty_list_shell": True,
        "tool_panel": False,
        "linked_api_row_id": linked_api,
        "shell_id": shell["shell_id"],
        "path_class": shell["path_class"],
        "tool_ref": shell["tool_ref"],
        "api_bulk_blocker": "BULK_SCHEMA_UNSPECIFIED_OFFICIAL_DOCS",
    }


def apply_ui_product_plane_bulk_chrome_dual_na_empty_list(
    workflows: list[dict[str, Any]],
) -> None:
    """Promote research190 empty-list dual-absent product-plane bulk rows to UI NA.

    Exact 5 resources / 10 bulk_save+bulk_delete UI parity ids only. Runs after
    research187 honesty, research188 strong, and research189 soft dual-NA so NA
    wins over discovery_required for this subset.
    """

    if len(UI_BULK_CHROME_DUAL_NA_EMPTY_LIST_RESOURCES) != 5:
        raise RuntimeError(
            "UI_BULK_CHROME_DUAL_NA_EMPTY_LIST_RESOURCES must be exactly 5 "
            f"(got {len(UI_BULK_CHROME_DUAL_NA_EMPTY_LIST_RESOURCES)})"
        )
    if len(UI_BULK_CHROME_DUAL_NA_EMPTY_LIST_IDS) != 10:
        raise RuntimeError(
            "UI_BULK_CHROME_DUAL_NA_EMPTY_LIST_IDS must be exactly 10 "
            f"(got {len(UI_BULK_CHROME_DUAL_NA_EMPTY_LIST_IDS)})"
        )
    if set(UI_BULK_CHROME_DUAL_NA_EMPTY_LIST_SHELLS) != UI_BULK_CHROME_DUAL_NA_EMPTY_LIST_RESOURCES:
        raise RuntimeError("shell map must cover exactly empty-list dual-NA resources")
    if not UI_BULK_CHROME_DUAL_NA_EMPTY_LIST_IDS.issubset(UI_PRODUCT_PLANE_BULK_HONESTY_IDS):
        raise RuntimeError("empty-list dual-NA ids must be a subset of product-plane honesty ids")
    if UI_BULK_CHROME_DUAL_NA_EMPTY_LIST_RESOURCES & UI_BULK_CHROME_DUAL_NA_STRONG_RESOURCES:
        raise RuntimeError("empty-list dual-NA resources must not overlap strong dual-NA resources")
    if UI_BULK_CHROME_DUAL_NA_EMPTY_LIST_RESOURCES & UI_BULK_CHROME_DUAL_NA_SOFT_TOOL_RESOURCES:
        raise RuntimeError("empty-list dual-NA resources must not overlap soft dual-NA resources")
    if UI_BULK_CHROME_DUAL_NA_EMPTY_LIST_IDS & UI_BULK_CHROME_DUAL_NA_STRONG_IDS:
        raise RuntimeError("empty-list dual-NA ids must not overlap strong dual-NA ids")
    if UI_BULK_CHROME_DUAL_NA_EMPTY_LIST_IDS & UI_BULK_CHROME_DUAL_NA_SOFT_TOOL_IDS:
        raise RuntimeError("empty-list dual-NA ids must not overlap soft dual-NA ids")

    for row in workflows:
        row_id = str(row.get("id", ""))
        if row_id not in UI_BULK_CHROME_DUAL_NA_EMPTY_LIST_IDS:
            continue
        parts = row_id.split(".")
        if len(parts) < 4:
            continue
        resource = parts[2]
        operation = parts[3]
        if resource not in UI_BULK_CHROME_DUAL_NA_EMPTY_LIST_RESOURCES:
            continue
        if operation not in ("bulk_save", "bulk_delete"):
            continue

        shell = UI_BULK_CHROME_DUAL_NA_EMPTY_LIST_SHELLS[resource]
        qual = ui_bulk_chrome_absent_dual_empty_list_qualification(resource, operation)
        linked_api = qual["linked_api_row_id"]
        row["tool_name"] = ""
        row["parity_status"] = "not_applicable"
        row["discovered"] = True
        row["implemented"] = True
        row["contract_tested"] = True
        row["live_tested"] = True
        row["vision_verified"] = True
        row["vision_evidence"] = None
        row["sensitivity"] = "low"
        row["side_effects"] = (
            "none; UI bulk parity classified not_applicable — no bulk browser "
            "workflow tool and no records may be created through a bulk UI tool"
        )
        row["cleanup"] = (
            "not_applicable; no UI bulk tool and no disposable records for this parity row"
        )
        row["errors"] = [
            "AUTH_INTERACTION_REQUIRED",
            "UI_CHANGED",
            UI_BULK_CHROME_ABSENT_DUAL_EMPTY_LIST_EVIDENCE_CODE,
        ]
        row["method_or_route"] = (
            f"no equivalent mit.billy.dk bulk workflow for {linked_api} "
            f"(research190 dual-session: empty list shell {shell['shell_id']} "
            f"tool_ref={shell['tool_ref']} path_class {shell['path_class']}; "
            "dual_agree multi-select/bulk-action chrome absent; "
            "empty_list_shell=true; tool_panel=false; "
            f"evidence_code={UI_BULK_CHROME_ABSENT_DUAL_EMPTY_LIST_EVIDENCE_CODE}; "
            "not_applicable accepted)"
        )
        row["qualification"] = dict(qual)
        prior = str(row.get("evidence") or "").strip()
        na_evidence = (
            "research190 dual independent ephemeral browser sessions (no "
            f"BILLY_API_TOKEN): dual READY/READY; empty list shell "
            f"{shell['shell_id']} path_class {shell['path_class']} "
            f"(tool_ref={shell['tool_ref']}); real h1 empty-state copy distinct "
            "from nonsense soft-empty control; dual_agree_bulk_chrome_absent "
            f"true (tables/rows/checkboxes 0); no bulk-action chrome for "
            f"{linked_api}; design §10.2 UI parity not_applicable accepted; "
            f"evidence_code={UI_BULK_CHROME_ABSENT_DUAL_EMPTY_LIST_EVIDENCE_CODE}; "
            "no ui_* bulk tool; API bulk lane unchanged "
            "(external_contract_blocker BULK_SCHEMA_UNSPECIFIED_OFFICIAL_DOCS; "
            "live_tested false out_of_scope_by_user); "
            "evidence_ref=research190_empty_shell_dual; "
            f"docs etag {DOCS_ETAG}; MD5 {DOCS_MD5}; empty_list_shell=true; "
            "tool_panel=false; completes product-plane bulk honesty freezes "
            "(strong+soft+empty-list)"
        )
        row["evidence"] = f"{prior}; {na_evidence}" if prior else na_evidence


def bulk_rows(resource: str) -> list[dict[str, Any]]:
    """Build the two deliberately unimplemented bulk mentions for a resource.

    Research136 freezes offline path/method *shape hints* only. Research137
    records an external-contract blocker after official docs/asset exhaust.
    Full request/response contracts remain unresolved, so rows stay
    ``ambiguous_bulk`` with empty tool names and no implemented/contract_tested
    green.
    """

    area = snake_case(resource)
    route = f"/v2/{resource}"
    qualification = bulk_external_contract_qualification()
    shape_evidence = (
        f"{DOCS_URL} official API v2; docs etag {DOCS_ETAG}; MD5 {DOCS_MD5}; "
        "research136 offline unauth shape freeze only (not a full bulk body/"
        "response contract; not live-qualified); research137 official docs "
        "and research191/research192 reconfirm; versioned-asset exhaust (OpenAPI/swagger "
        "probes 404; page chunk "
        "Supports-only; no bulk body/response schema) → external_contract_blocker "
        f"{qualification['blocker_code']}; live_api=out_of_scope_by_user; no bulk tools"
    )
    bulk_save = base_api_row(
        row_id=f"api.{resource}.bulk_save",
        area=area,
        operation="bulk_save",
        method_or_route=(
            f"AMBIGUOUS Supports: bulk save {route}; offline shape PUT {route}/bulk "
            "(research136 object-root only; not full body/response contract)"
        ),
        request_fields=["json_object_root"],
        response_fields=[],
        filters=[],
        pagination=None,
        side_effects=(
            "unknown until field schema, partial failures, empty-array semantics, "
            "and limits are contracted; offline unauth only proves object-root body "
            "parse then AUTHENTICATION_REQUIRED; blocked by external_contract_blocker "
            f"{qualification['blocker_code']}"
        ),
        cleanup=(
            "unknown until the bulk contract is published by Billy official docs "
            "or live API scope is re-opened; external_contract_blocker active"
        ),
        tool_name="",
        source_kind="ambiguous_bulk",
        contract_status="ambiguous_bulk",
    )
    bulk_save["errors"] = [
        *COMMON_ERRORS,
        "INVALID_REQUEST_BODY",
    ]
    bulk_save["evidence"] = shape_evidence
    bulk_save["qualification"] = qualification
    bulk_delete = base_api_row(
        row_id=f"api.{resource}.bulk_delete",
        area=area,
        operation="bulk_delete",
        method_or_route=(
            f"AMBIGUOUS Supports: bulk delete {route}; offline shape DELETE "
            f"{route}?ids[]= (research136 empty-ids fail-closed; not effect contract)"
        ),
        request_fields=["ids[]"],
        response_fields=[],
        filters=[],
        pagination=None,
        side_effects=(
            "unknown until identifiers, partial failures, and limits are contracted; "
            "empty ids are INVALID_DELETE_ID_ARRAY offline; unauth non-empty id "
            "200 meta-only is not effect proof; blocked by external_contract_blocker "
            f"{qualification['blocker_code']}"
        ),
        cleanup=(
            "unknown until the bulk contract is published by Billy official docs "
            "or live API scope is re-opened; external_contract_blocker active"
        ),
        tool_name="",
        source_kind="ambiguous_bulk",
        contract_status="ambiguous_bulk",
    )
    bulk_delete["errors"] = [
        *COMMON_ERRORS,
        "INVALID_DELETE_ID_ARRAY",
    ]
    bulk_delete["evidence"] = shape_evidence
    bulk_delete["qualification"] = qualification
    return [bulk_save, bulk_delete]


def special_rows() -> list[dict[str, Any]]:
    """Build the six separately documented prose routes without inventing more."""

    rows = [
        base_api_row(
            row_id="api.special.files_upload",
            area="files",
            operation="upload",
            method_or_route="POST /v2/files",
            request_fields=FILES_UPLOAD_REQUEST_FIELDS,
            response_fields=["files[]", "attachments?"],
            filters=[],
            pagination=None,
            side_effects="high: uploads file content and may create attachment variants",
            cleanup=(
                "delete only dedicated test attachments after live upload contract qualification"
            ),
            tool_name=FILES_UPLOAD_TOOL_NAME,
            source_kind="special",
        ),
        base_api_row(
            row_id="api.special.invoice_email",
            area="invoices",
            operation="send_email",
            method_or_route="POST /v2/invoices/:invoiceId/emails",
            request_fields=[
                "invoiceId",
                "email.contactPersonId",
                "email.emailBody",
                "email.emailSubject",
                "email.copyToUserId?",
            ],
            response_fields=["changed_records[]"],
            filters=[],
            pagination=None,
            side_effects="high: sends external email",
            cleanup="not_reversible; use a dedicated non-production destination",
            tool_name="api_invoices_send_email_preview",
            source_kind="special",
        ),
        base_api_row(
            row_id="api.special.invoice_delivery",
            area="invoice_deliveries",
            operation="create",
            method_or_route="POST /v2/invoiceDeliveries",
            request_fields=[
                "invoiceDelivery.invoiceId",
                "invoiceDelivery.organizationId",
                "invoiceDelivery.receiverIdType (gln|cvr)",
                "invoiceDelivery.receiverGln?",
                "invoiceDelivery.orderReference?",
                "invoiceDelivery.senderUserId",
            ],
            response_fields=["invoiceDelivery"],
            filters=[],
            pagination=None,
            side_effects="high: asynchronous external e-invoice delivery",
            cleanup=(
                "not_reversible; requires a supported sandbox or resettable dedicated organisation"
            ),
            tool_name="api_invoice_deliveries_create_preview",
            source_kind="special",
        ),
        base_api_row(
            row_id="api.special.invoice_logs",
            area="invoice_logs",
            operation="list",
            method_or_route="GET /v2/invoiceLogs",
            request_fields=["invoiceId", "organizationId", "sortProperty", "sortDirection"],
            response_fields=["invoiceLogs[]"],
            filters={"sortProperty": ["eventTime"], "sortDirection": ["DESC"]},
            pagination=None,
            side_effects="none",
            cleanup="not_applicable",
            tool_name="api_invoice_logs_list",
            source_kind="special",
        ),
        base_api_row(
            row_id="api.special.user_get",
            area="user",
            operation="get",
            method_or_route="GET /v2/user",
            request_fields=[],
            response_fields=["user"],
            filters=[],
            pagination=None,
            side_effects="none",
            cleanup="not_applicable",
            tool_name="api_user_get",
            source_kind="special",
        ),
        base_api_row(
            row_id="api.special.user_organizations",
            area="user_organizations",
            operation="list",
            method_or_route="GET /v2/user/organizations",
            request_fields=[],
            response_fields=["organizations[]"],
            filters=[],
            pagination=None,
            side_effects="none",
            cleanup="not_applicable",
            tool_name="api_user_list_organizations",
            source_kind="special",
        ),
    ]
    user_organizations = next(row for row in rows if row["id"] == "api.special.user_organizations")
    user_organizations["evidence"] = (
        f"{user_organizations['evidence']}; live intro lists user companies "
        "via GET /v2/organizations (api.organizations.list); "
        "GET /v2/user/organizations is absent from the current official page; "
        "tool path kept"
    )
    return rows


def build_api_manifest() -> dict[str, Any]:
    """Return the complete 305-operation official snapshot."""

    operations: list[dict[str, Any]] = []
    for resource, create, update, delete in RESOURCE_SUPPORTS:
        operations.extend(standard_rows(resource, create, update, delete))
        operations.extend(bulk_rows(resource))
    operations.extend(special_rows())
    apply_residual_clear_honesty(operations)
    apply_api_live_api_deferred(operations)
    return {
        "manifest": "billy_api_v2_phase_0",
        "schema_version": 1,
        "official_docs": {"url": DOCS_URL, "etag": DOCS_ETAG, "md5": DOCS_MD5},
        "operations": operations,
    }


def apply_ui_invoices_list_shell_evidence(
    row: dict[str, Any],
    *,
    parity_of_api_list: bool = False,
) -> None:
    """Mark invoices list **shell open** evidence only (IR 186.3 R1/R2).

    The tool has empty input and does not implement API list filters or
    pagination UI. Parity rows must not keep the full API request schema while
    claiming contract/live green. vision_evidence stays null in the inventory;
    the durable review record lives outside git under node tmp.
    """

    row["method_or_route"] = "mit.billy.dk /:org_slug/invoices (read-only list shell open)"
    row["tool_name"] = UI_INVOICES_LIST_TOOL_NAME
    # Shell-only contract actually tested by ui_invoices_list (empty tool input).
    row["request_fields"] = []
    row["response_fields"] = [
        "path_class",
        "heading",
        "create_action_visible",
        "shell_markers_present",
    ]
    row["filters"] = []
    row["pagination"] = None
    row["test_references"] = [
        TEST_REFERENCE,
        UI_INVOICES_LIST_MODEL_TEST_REFERENCE,
        UI_INVOICES_LIST_UNIT_TEST_REFERENCE,
        UI_INVOICES_LIST_LIVE_TEST_REFERENCE,
        UI_INVOICES_GET_OPEN_LIVE_TEST_REFERENCE,
        SERVER_REGISTRY_TEST_REFERENCE,
    ]
    row["evidence"] = (
        "research102 dual-session headless observation + ui_invoices_list product; "
        "list shell only (path class, h1 Fakturaer, CTA Opret faktura present, no create); "
        "API list filters/sort/pagination UI not producted; "
        "vision record tmp/vision-records/ui_invoices_list.json (list surface frames, accept)"
    )
    if parity_of_api_list:
        row["evidence"] = f"{row['evidence']}; maps api.invoices.list to UI list-shell open only"
    row["discovered"] = True
    row["implemented"] = True
    row["contract_tested"] = True
    row["live_tested"] = True
    row["vision_verified"] = True
    row["vision_evidence"] = None
    row["parity_status"] = "list_shell_open_only"
    row["sensitivity"] = "low"
    row["side_effects"] = "none"
    row["cleanup"] = "not_applicable; read-only observation creates no records"
    row["errors"] = [
        "AUTH_REQUIRED",
        "AUTH_INTERACTION_REQUIRED",
        "UI_CHANGED",
        "EGRESS_DENIED",
        "BILLY_ERROR",
    ]


def apply_ui_invoices_create_open_shell_evidence(
    row: dict[str, Any],
    *,
    parity_of_api_create: bool = False,
) -> None:
    """Mark invoices create form **open only** evidence (research153).

    Empty-input tool; open /:org_slug/invoices/new; h1 Opret faktura; markers
    Gem som kladde + line chrome (Tilføj linje/Beskrivelse). Never submit
    Godkend/Send/Gem/Tilføj/Vedhæft. Distinct from list shell and special
    invoice_email. When ``parity_of_api_create`` is true, dual-counts exact
    ``ui.parity.invoices.create`` for ``api.invoices.create``.
    """

    row["method_or_route"] = (
        "mit.billy.dk /:org_slug/invoices/new (read-only invoice create form open; "
        "never Godkend/Send/Gem som kladde/Vis preview/Tilføj linje/Vedhæft/Slet)"
    )
    row["tool_name"] = UI_INVOICES_CREATE_OPEN_TOOL_NAME
    row["request_fields"] = []
    row["response_fields"] = [
        "path_class",
        "heading",
        "shell_kind",
        "draft_save_chrome_visible",
        "line_chrome_visible",
        "shell_markers_present",
    ]
    row["filters"] = []
    row["pagination"] = None
    if not parity_of_api_create:
        row["api_row_id"] = None
    row["test_references"] = [
        TEST_REFERENCE,
        UI_INVOICES_CREATE_OPEN_MODEL_TEST_REFERENCE,
        UI_INVOICES_CREATE_OPEN_UNIT_TEST_REFERENCE,
        UI_INVOICES_CREATE_OPEN_LIVE_TEST_REFERENCE,
        SERVER_REGISTRY_TEST_REFERENCE,
    ]
    row["evidence"] = (
        "research153 dual-session headless observation + ui_invoices_create_open product; "
        "form open only (path class /:org_slug/invoices/new, h1 Opret faktura, "
        "shell_kind=invoices_create, Gem som kladde + line chrome; never submit; "
        "distinct from list shell and special POST /invoices/:id/emails; "
        "Levering settings not this form); soft /emails empty dual; "
        "vision record tmp/vision-records/ui_invoices_create_open.json "
        "(Opret faktura form frames, accept)"
    )
    if parity_of_api_create:
        row["evidence"] = f"{row['evidence']}; maps api.invoices.create to UI create-form open only"
    row["discovered"] = True
    row["implemented"] = True
    row["contract_tested"] = True
    row["live_tested"] = True
    row["vision_verified"] = True
    row["vision_evidence"] = None
    row["parity_status"] = "form_open_only"
    row["sensitivity"] = "medium"
    row["side_effects"] = "none when open-only; product path never submits"
    row["cleanup"] = "not_applicable; read-only observation creates no records"
    row["errors"] = [
        "AUTH_REQUIRED",
        "AUTH_INTERACTION_REQUIRED",
        "UI_CHANGED",
        "EGRESS_DENIED",
        "BILLY_ERROR",
    ]


def apply_ui_invoices_get_open_shell_evidence(
    row: dict[str, Any],
    *,
    parity_of_api_get: bool = False,
) -> None:
    """Mark invoices detail **get/open only** evidence (research169).

    Empty-input tool; open /:org_slug/invoices, open first non-header invoice
    detail at path class /:org_slug/invoices/:id/edit. Never Gem/Send/Slet.
    Requires scoped browser path_allow for GET/POST/DELETE /v2/invoices (GET
    list/data plane; POST/DELETE for disposable seed/cleanup). When
    ``parity_of_api_get`` is true, dual-counts exact ``ui.parity.invoices.get``.
    """

    row["method_or_route"] = (
        "mit.billy.dk /:org_slug/invoices + first non-header invoice detail "
        "(read-only invoices get/open; never Gem/Send/Slet/Godkend submit; "
        "/invoices/new not success)"
    )
    row["tool_name"] = UI_INVOICES_GET_OPEN_TOOL_NAME
    row["request_fields"] = []
    row["response_fields"] = [
        "path_class",
        "shell_kind",
        "detail_open",
        "entry_date_control_present",
        "contact_control_present",
        "line_chrome_present",
        "shell_markers_present",
    ]
    row["filters"] = []
    row["pagination"] = None
    if not parity_of_api_get:
        row["api_row_id"] = None
    row["test_references"] = [
        TEST_REFERENCE,
        UI_INVOICES_GET_OPEN_MODEL_TEST_REFERENCE,
        UI_INVOICES_GET_OPEN_UNIT_TEST_REFERENCE,
        UI_INVOICES_GET_OPEN_LIVE_TEST_REFERENCE,
        SERVER_REGISTRY_TEST_REFERENCE,
    ]
    row["evidence"] = (
        "research169 dual-session headless observation + ui_invoices_get_open product; "
        "scoped api.billysbilling.com path_allow for GET/POST/DELETE /v2/invoices "
        "(GET list settle from research168; POST/DELETE disposable draft seed/cleanup; "
        "emails still denied); detail open only (path class /:org_slug/invoices/:id/edit, "
        "shell_kind=invoices_get, entryDate/contact/line chrome; never Gem/Send/Slet; "
        "distinct from list shell ui_invoices_list and create form_open "
        "ui_invoices_create_open); vision record tmp/vision-records/ui_invoices_get_open.json "
        "(invoice detail frames, accept)"
    )
    if parity_of_api_get:
        row["evidence"] = f"{row['evidence']}; maps api.invoices.get to UI detail get/open only"
    row["discovered"] = True
    row["implemented"] = True
    row["contract_tested"] = True
    row["live_tested"] = True
    row["vision_verified"] = True
    row["vision_evidence"] = None
    row["parity_status"] = "detail_open_only"
    row["sensitivity"] = "medium"
    row["side_effects"] = "none when open-only; product path never submits"
    row["cleanup"] = (
        "not_applicable for product path; live harness creates disposable contact+"
        "product+invoice then deletes in reverse with fresh list read-back"
    )
    row["errors"] = [
        "AUTH_REQUIRED",
        "AUTH_INTERACTION_REQUIRED",
        "UI_CHANGED",
        "EGRESS_DENIED",
        "BILLY_ERROR",
    ]


def apply_ui_bills_get_open_shell_evidence(
    row: dict[str, Any],
    *,
    parity_of_api_get: bool = False,
) -> None:
    """Mark bills detail **get/open only** evidence (research170).

    Empty-input tool; open /:org_slug/bills, open first non-header bill detail
    at path class /:org_slug/bills/:id. Never Gem/Godkend/Opdater/Slet/Træk.
    Requires scoped browser path_allow for GET/POST/DELETE /v2/bills and GET
    /v2/taxRates (seed). When ``parity_of_api_get`` is true, dual-counts exact
    ``ui.parity.bills.get``.
    """

    row["method_or_route"] = (
        "mit.billy.dk /:org_slug/bills + first non-header bill detail "
        "(read-only bills get/open; never Gem/Godkend/Opdater/Slet/Træk submit; "
        "/bills/new not success)"
    )
    row["tool_name"] = UI_BILLS_GET_OPEN_TOOL_NAME
    row["request_fields"] = []
    row["response_fields"] = [
        "path_class",
        "shell_kind",
        "detail_open",
        "kladde_or_state_chrome_present",
        "supplier_chrome_present",
        "amount_or_line_chrome_present",
        "shell_markers_present",
    ]
    row["filters"] = []
    row["pagination"] = None
    if not parity_of_api_get:
        row["api_row_id"] = None
    row["test_references"] = [
        TEST_REFERENCE,
        UI_BILLS_GET_OPEN_MODEL_TEST_REFERENCE,
        UI_BILLS_GET_OPEN_UNIT_TEST_REFERENCE,
        UI_BILLS_GET_OPEN_LIVE_TEST_REFERENCE,
        SERVER_REGISTRY_TEST_REFERENCE,
    ]
    row["evidence"] = (
        "research170 dual-session headless observation + ui_bills_get_open product; "
        "scoped api.billysbilling.com path_allow for GET/POST/DELETE /v2/bills and "
        "GET /v2/taxRates (GET list settle from research168; POST/DELETE disposable "
        "draft seed with nested accountId+taxRateId+description+amount, no paymentDate; "
        "emails still denied); detail open only (path class /:org_slug/bills/:id, "
        "shell_kind=bills_get, kladde/supplier/amount chrome; never write submit; "
        "distinct from list shell ui_bills_list and create form_open "
        "ui_bills_create_open); vision record tmp/vision-records/ui_bills_get_open.json "
        "(bill detail frames, accept)"
    )
    if parity_of_api_get:
        row["evidence"] = f"{row['evidence']}; maps api.bills.get to UI detail get/open only"
    row["discovered"] = True
    row["implemented"] = True
    row["contract_tested"] = True
    row["live_tested"] = True
    row["vision_verified"] = True
    row["vision_evidence"] = None
    row["parity_status"] = "detail_open_only"
    row["sensitivity"] = "medium"
    row["side_effects"] = "none when open-only; product path never submits"
    row["cleanup"] = (
        "not_applicable for product path; live harness creates disposable contact+"
        "bill then deletes in reverse with fresh list read-back"
    )
    row["errors"] = [
        "AUTH_REQUIRED",
        "AUTH_INTERACTION_REQUIRED",
        "UI_CHANGED",
        "EGRESS_DENIED",
        "BILLY_ERROR",
    ]


def apply_ui_invoices_update_open_shell_evidence(
    row: dict[str, Any],
    *,
    parity_of_api_update: bool = False,
) -> None:
    """Mark invoices edit form **open only** evidence (research174).

    Empty-input tool; open /:org_slug/invoices, open first non-header invoice
    edit form at path class /:org_slug/invoices/:id/edit. Never Gem/Gem som
    kladde/Godkend og send/Send/Slet submit. Distinct from get detail_open_only
    on the same path (update requires Gem som kladde + multi-label form freeze).
    When ``parity_of_api_update`` is true, dual-counts exact
    ``ui.parity.invoices.update``.
    """

    row["method_or_route"] = (
        "mit.billy.dk /:org_slug/invoices + first non-header invoice edit form "
        "(read-only invoices update form open; never Gem/Gem som kladde/Godkend/"
        "Send/Slet submit; /invoices/new not success)"
    )
    row["tool_name"] = UI_INVOICES_UPDATE_OPEN_TOOL_NAME
    row["request_fields"] = []
    row["response_fields"] = [
        "path_class",
        "shell_kind",
        "form_open",
        "gem_kladde_or_save_chrome_present",
        "date_or_payment_terms_chrome_present",
        "contact_or_customer_chrome_present",
        "inputs_present",
        "shell_markers_present",
    ]
    row["filters"] = []
    row["pagination"] = None
    if not parity_of_api_update:
        row["api_row_id"] = None
    row["test_references"] = [
        TEST_REFERENCE,
        UI_INVOICES_UPDATE_OPEN_MODEL_TEST_REFERENCE,
        UI_INVOICES_UPDATE_OPEN_UNIT_TEST_REFERENCE,
        UI_INVOICES_UPDATE_OPEN_LIVE_TEST_REFERENCE,
        SERVER_REGISTRY_TEST_REFERENCE,
    ]
    row["evidence"] = (
        "research174 dual-session headless observation + ui_invoices_update_open product; "
        "committed api.billysbilling.com path_allow for GET/POST/DELETE /v2/invoices and "
        "products/contacts seed (disposable draft invoice; emails still denied); form open "
        "only (path class /:org_slug/invoices/:id/edit, shell_kind=invoices_update, Gem som "
        "kladde + Fakturanr/Dato/Betalingsfrist chrome + inputs≥3; never write submit; "
        "distinct from list shell ui_invoices_list, create form_open ui_invoices_create_open, "
        "and get detail_open ui_invoices_get_open); vision record "
        "tmp/vision-records/ui_invoices_update_open.json (invoice edit form frames, accept)"
    )
    if parity_of_api_update:
        row["evidence"] = f"{row['evidence']}; maps api.invoices.update to UI edit form open only"
    row["discovered"] = True
    row["implemented"] = True
    row["contract_tested"] = True
    row["live_tested"] = True
    row["vision_verified"] = True
    row["vision_evidence"] = None
    row["parity_status"] = "form_open_only"
    row["sensitivity"] = "medium"
    row["side_effects"] = "none when open-only; product path never submits"
    row["cleanup"] = (
        "not_applicable for product path; live harness creates disposable contact+"
        "product+invoice then deletes in reverse with fresh list read-back"
    )
    row["errors"] = [
        "AUTH_REQUIRED",
        "AUTH_INTERACTION_REQUIRED",
        "UI_CHANGED",
        "EGRESS_DENIED",
        "BILLY_ERROR",
    ]


def apply_ui_bills_update_open_shell_evidence(
    row: dict[str, Any],
    *,
    parity_of_api_update: bool = False,
) -> None:
    """Mark bills edit form **open only** evidence (research172).

    Empty-input tool; open /:org_slug/bills, open first non-header bill edit
    form at path class /:org_slug/bills/:id/edit. Never Opdater/Godkend/Slet/
    Træk/Upload/Registrer betaling submit. Distinct from get detail_open_only
    on /:org_slug/bills/:id. When ``parity_of_api_update`` is true, dual-counts
    exact ``ui.parity.bills.update``.
    """

    row["method_or_route"] = (
        "mit.billy.dk /:org_slug/bills + first non-header bill edit form "
        "(read-only bills update form open; never Opdater/Godkend/Slet/Træk submit; "
        "/bills/new and read /bills/:id not success)"
    )
    row["tool_name"] = UI_BILLS_UPDATE_OPEN_TOOL_NAME
    row["request_fields"] = []
    row["response_fields"] = [
        "path_class",
        "shell_kind",
        "form_open",
        "ret_regning_chrome_present",
        "opdater_present",
        "leverandor_or_dates_chrome_present",
        "inputs_present",
        "shell_markers_present",
    ]
    row["filters"] = []
    row["pagination"] = None
    if not parity_of_api_update:
        row["api_row_id"] = None
    row["test_references"] = [
        TEST_REFERENCE,
        UI_BILLS_UPDATE_OPEN_MODEL_TEST_REFERENCE,
        UI_BILLS_UPDATE_OPEN_UNIT_TEST_REFERENCE,
        UI_BILLS_UPDATE_OPEN_LIVE_TEST_REFERENCE,
        SERVER_REGISTRY_TEST_REFERENCE,
    ]
    row["evidence"] = (
        "research172 dual-session headless observation + ui_bills_update_open product; "
        "committed api.billysbilling.com path_allow for GET/POST/DELETE /v2/bills and "
        "GET /v2/taxRates (disposable draft seed with nested accountId+taxRateId+"
        "description+amount, no paymentDate; emails still denied); form open only "
        "(path class /:org_slug/bills/:id/edit, shell_kind=bills_update, Ret regning/"
        "Opdater/Leverandør/Bilagsdato chrome; never write submit; distinct from list "
        "shell ui_bills_list, create form_open ui_bills_create_open, and get detail "
        "ui_bills_get_open); vision record tmp/vision-records/ui_bills_update_open.json "
        "(bill edit form frames, accept)"
    )
    if parity_of_api_update:
        row["evidence"] = f"{row['evidence']}; maps api.bills.update to UI edit form open only"
    row["discovered"] = True
    row["implemented"] = True
    row["contract_tested"] = True
    row["live_tested"] = True
    row["vision_verified"] = True
    row["vision_evidence"] = None
    row["parity_status"] = "form_open_only"
    row["sensitivity"] = "medium"
    row["side_effects"] = "none when open-only; product path never submits"
    row["cleanup"] = (
        "not_applicable for product path; live harness creates disposable contact+"
        "bill then deletes in reverse with fresh list read-back"
    )
    row["errors"] = [
        "AUTH_REQUIRED",
        "AUTH_INTERACTION_REQUIRED",
        "UI_CHANGED",
        "EGRESS_DENIED",
        "BILLY_ERROR",
    ]


def apply_ui_bills_delete_open_shell_evidence(
    row: dict[str, Any],
    *,
    parity_of_api_delete: bool = False,
) -> None:
    """Mark bills delete chrome **open only** evidence (research173).

    Empty-input tool; open /:org_slug/bills, open first non-header bill edit at
    path class /:org_slug/bills/:id/edit; primary Slet present; click Slet once
    for confirm (Slet≥2 + Annuller); dismiss Annuller only. Never permanent
    delete / second Slet / Opdater / Godkend. Distinct from update form_open and
    get detail_open. When ``parity_of_api_delete`` is true, dual-counts exact
    ``ui.parity.bills.delete``.
    """

    row["method_or_route"] = (
        "mit.billy.dk /:org_slug/bills + first non-header bill edit delete chrome "
        "(read-only: Slet confirm open + Annuller dismiss; never permanent delete; "
        "/bills/new and read /bills/:id without Slet not success)"
    )
    row["tool_name"] = UI_BILLS_DELETE_OPEN_TOOL_NAME
    row["request_fields"] = []
    row["response_fields"] = [
        "path_class",
        "shell_kind",
        "edit_open",
        "slet_present",
        "confirm_open",
        "annuller_present",
        "confirm_dismissed",
        "shell_markers_present",
    ]
    row["filters"] = []
    row["pagination"] = None
    if not parity_of_api_delete:
        row["api_row_id"] = None
    row["test_references"] = [
        TEST_REFERENCE,
        UI_BILLS_DELETE_OPEN_MODEL_TEST_REFERENCE,
        UI_BILLS_DELETE_OPEN_UNIT_TEST_REFERENCE,
        UI_BILLS_DELETE_OPEN_LIVE_TEST_REFERENCE,
        SERVER_REGISTRY_TEST_REFERENCE,
    ]
    row["evidence"] = (
        "research173 dual-session headless observation + ui_bills_delete_open product; "
        "committed api.billysbilling.com path_allow for GET/POST/DELETE /v2/bills and "
        "GET /v2/taxRates (disposable draft seed with nested accountId+taxRateId+"
        "description+amount, no paymentDate; emails still denied); delete chrome only "
        "(path class /:org_slug/bills/:id/edit, shell_kind=bills_delete, primary Slet, "
        "confirm Slet≥2+Annuller, Annuller dismiss; never permanent delete; distinct "
        "from list shell ui_bills_list, create form_open ui_bills_create_open, get "
        "detail ui_bills_get_open, and update form_open ui_bills_update_open); vision "
        "record tmp/vision-records/ui_bills_delete_open.json (bill delete chrome "
        "frames, accept)"
    )
    if parity_of_api_delete:
        row["evidence"] = f"{row['evidence']}; maps api.bills.delete to UI delete chrome open only"
    row["discovered"] = True
    row["implemented"] = True
    row["contract_tested"] = True
    row["live_tested"] = True
    row["vision_verified"] = True
    row["vision_evidence"] = None
    row["parity_status"] = "delete_chrome_open_only"
    row["sensitivity"] = "medium"
    row["side_effects"] = "none when open-only; product path never confirms delete"
    row["cleanup"] = (
        "not_applicable for product path; live harness creates disposable contact+"
        "bill then deletes in reverse with fresh list read-back"
    )
    row["errors"] = [
        "AUTH_REQUIRED",
        "AUTH_INTERACTION_REQUIRED",
        "UI_CHANGED",
        "EGRESS_DENIED",
        "BILLY_ERROR",
    ]


def apply_ui_bills_create_open_shell_evidence(
    row: dict[str, Any],
    *,
    parity_of_api_create: bool = False,
) -> None:
    """Mark bills create form **open only** evidence (research154).

    Empty-input tool; open /:org_slug/bills/new; h1 Opret køb; markers
    Gem som kladde + line chrome (Tilføj linje/Beskrivelse/Linje). Never submit
    Godkend/Gem/Upload/Tilføj. Distinct from list shell. When
    ``parity_of_api_create`` is true, dual-counts exact
    ``ui.parity.bills.create`` for ``api.bills.create``.
    """

    row["method_or_route"] = (
        "mit.billy.dk /:org_slug/bills/new (read-only bill create form open; "
        "never Godkend/Gem som kladde/Upload fil/Træk/Tilføj linje/Slet)"
    )
    row["tool_name"] = UI_BILLS_CREATE_OPEN_TOOL_NAME
    row["request_fields"] = []
    row["response_fields"] = [
        "path_class",
        "heading",
        "shell_kind",
        "draft_save_chrome_visible",
        "line_chrome_visible",
        "shell_markers_present",
    ]
    row["filters"] = []
    row["pagination"] = None
    if not parity_of_api_create:
        row["api_row_id"] = None
    row["test_references"] = [
        TEST_REFERENCE,
        UI_BILLS_CREATE_OPEN_MODEL_TEST_REFERENCE,
        UI_BILLS_CREATE_OPEN_UNIT_TEST_REFERENCE,
        UI_BILLS_CREATE_OPEN_LIVE_TEST_REFERENCE,
        SERVER_REGISTRY_TEST_REFERENCE,
    ]
    row["evidence"] = (
        "research154 dual-session headless observation + ui_bills_create_open product; "
        "form open only (path class /:org_slug/bills/new, h1 Opret køb, "
        "shell_kind=bills_create, Gem som kladde + line chrome; never submit; "
        "distinct from list shell ui_bills_list and special invoice_email); "
        "soft /emails empty dual; "
        "vision record tmp/vision-records/ui_bills_create_open.json "
        "(Opret køb form frames, accept)"
    )
    if parity_of_api_create:
        row["evidence"] = f"{row['evidence']}; maps api.bills.create to UI create-form open only"
    row["discovered"] = True
    row["implemented"] = True
    row["contract_tested"] = True
    row["live_tested"] = True
    row["vision_verified"] = True
    row["vision_evidence"] = None
    row["parity_status"] = "form_open_only"
    row["sensitivity"] = "medium"
    row["side_effects"] = "none when open-only; product path never submits"
    row["cleanup"] = "not_applicable; read-only observation creates no records"
    row["errors"] = [
        "AUTH_REQUIRED",
        "AUTH_INTERACTION_REQUIRED",
        "UI_CHANGED",
        "EGRESS_DENIED",
        "BILLY_ERROR",
    ]


def apply_ui_products_list_shell_evidence(
    row: dict[str, Any],
    *,
    parity_of_api_list: bool = False,
) -> None:
    """Mark products list **shell open** evidence only (research103 / plan 186.4).

    Empty-input tool; no API list filters or pagination UI. vision_evidence stays
    null in the inventory; durable review record lives under node tmp.
    """

    row["method_or_route"] = "mit.billy.dk /:org_slug/products (read-only list shell open)"
    row["tool_name"] = UI_PRODUCTS_LIST_TOOL_NAME
    row["request_fields"] = []
    row["response_fields"] = [
        "path_class",
        "heading",
        "search_control_visible",
        "shell_markers_present",
    ]
    row["filters"] = []
    row["pagination"] = None
    row["test_references"] = [
        TEST_REFERENCE,
        UI_PRODUCTS_LIST_MODEL_TEST_REFERENCE,
        UI_PRODUCTS_LIST_UNIT_TEST_REFERENCE,
        UI_PRODUCTS_LIST_LIVE_TEST_REFERENCE,
        SERVER_REGISTRY_TEST_REFERENCE,
    ]
    row["evidence"] = (
        "research103 dual-session headless observation + ui_products_list product; "
        "list shell only (path class, h1 Produkter, data-cy search-button present, no create); "
        "API list filters/sort/pagination UI not producted; "
        "vision record tmp/vision-records/ui_products_list.json (list surface frames, accept)"
    )
    if parity_of_api_list:
        row["evidence"] = f"{row['evidence']}; maps api.products.list to UI list-shell open only"
    row["discovered"] = True
    row["implemented"] = True
    row["contract_tested"] = True
    row["live_tested"] = True
    row["vision_verified"] = True
    row["vision_evidence"] = None
    row["parity_status"] = "list_shell_open_only"
    row["sensitivity"] = "low"
    row["side_effects"] = "none"
    row["cleanup"] = "not_applicable; read-only observation creates no records"
    row["errors"] = [
        "AUTH_REQUIRED",
        "AUTH_INTERACTION_REQUIRED",
        "UI_CHANGED",
        "EGRESS_DENIED",
        "BILLY_ERROR",
    ]


def apply_ui_clients_list_shell_evidence(
    row: dict[str, Any],
    *,
    parity_of_api_list: bool = False,
) -> None:
    """Mark clients list **shell open** evidence only (research104 / plan 186.5).

    Empty-input tool; UI path /clients, h1 Kunder, CTA Opret kontakt. Maps
    offline api.contacts.list for list-open only. vision_evidence stays null.
    """

    row["method_or_route"] = "mit.billy.dk /:org_slug/clients (read-only list shell open)"
    row["tool_name"] = UI_CLIENTS_LIST_TOOL_NAME
    row["request_fields"] = []
    row["response_fields"] = [
        "path_class",
        "heading",
        "create_action_visible",
        "shell_markers_present",
    ]
    row["filters"] = []
    row["pagination"] = None
    row["test_references"] = [
        TEST_REFERENCE,
        UI_CLIENTS_LIST_MODEL_TEST_REFERENCE,
        UI_CLIENTS_LIST_UNIT_TEST_REFERENCE,
        UI_CLIENTS_LIST_LIVE_TEST_REFERENCE,
        SERVER_REGISTRY_TEST_REFERENCE,
    ]
    row["evidence"] = (
        "research104 dual-session headless observation + ui_clients_list product; "
        "list shell only (path class, h1 Kunder, CTA Opret kontakt present, no create); "
        "API list filters/sort/pagination UI not producted; "
        "vision record tmp/vision-records/ui_clients_list.json (list surface frames, accept)"
    )
    if parity_of_api_list:
        row["evidence"] = f"{row['evidence']}; maps api.contacts.list to UI list-shell open only"
    row["discovered"] = True
    row["implemented"] = True
    row["contract_tested"] = True
    row["live_tested"] = True
    row["vision_verified"] = True
    row["vision_evidence"] = None
    row["parity_status"] = "list_shell_open_only"
    row["sensitivity"] = "low"
    row["side_effects"] = "none"
    row["cleanup"] = "not_applicable; read-only observation creates no records"
    row["errors"] = [
        "AUTH_REQUIRED",
        "AUTH_INTERACTION_REQUIRED",
        "UI_CHANGED",
        "EGRESS_DENIED",
        "BILLY_ERROR",
    ]


def apply_ui_clients_create_open_shell_evidence(
    row: dict[str, Any],
    *,
    parity_of_api_create: bool = False,
) -> None:
    """Mark clients create form **open only** evidence (research160).

    Empty-input tool; open /:org_slug/clients then click Opret kontakt dialog.
    Form open only — never Gem/Opret submit. Soft /clients/new rejected.
    Distinct from list shell and special invoice_email. When
    ``parity_of_api_create`` is true, dual-counts exact
    ``ui.parity.contacts.create`` for ``api.contacts.create``.
    """

    row["method_or_route"] = (
        "mit.billy.dk /:org_slug/clients + Opret kontakt dialog "
        "(read-only clients create form open; never Gem/Opret/Save submit; "
        "soft /clients/new not success)"
    )
    row["tool_name"] = UI_CLIENTS_CREATE_OPEN_TOOL_NAME
    row["request_fields"] = []
    row["response_fields"] = [
        "path_class",
        "heading",
        "shell_kind",
        "create_dialog_open",
        "name_field_visible",
        "registration_no_field_present",
        "address_or_person_fields_present",
        "shell_markers_present",
    ]
    row["filters"] = []
    row["pagination"] = None
    if not parity_of_api_create:
        row["api_row_id"] = None
    row["test_references"] = [
        TEST_REFERENCE,
        UI_CLIENTS_CREATE_OPEN_MODEL_TEST_REFERENCE,
        UI_CLIENTS_CREATE_OPEN_UNIT_TEST_REFERENCE,
        UI_CLIENTS_CREATE_OPEN_LIVE_TEST_REFERENCE,
        SERVER_REGISTRY_TEST_REFERENCE,
    ]
    row["evidence"] = (
        "research160 dual-session headless observation + ui_clients_create_open product; "
        "form open only (path class /:org_slug/clients, h1 Kunder, shell_kind=clients_create, "
        "CTA Opret kontakt dialog with name+registrationNo+street/person fields; never submit; "
        "soft /clients/new chrome-only rejected; distinct from list shell ui_clients_list "
        "and special POST /invoices/:id/emails); "
        "vision record tmp/vision-records/ui_clients_create_open.json "
        "(Opret kontakt create dialog frames, accept)"
    )
    if parity_of_api_create:
        row["evidence"] = f"{row['evidence']}; maps api.contacts.create to UI create-form open only"
    row["discovered"] = True
    row["implemented"] = True
    row["contract_tested"] = True
    row["live_tested"] = True
    row["vision_verified"] = True
    row["vision_evidence"] = None
    row["parity_status"] = "form_open_only"
    row["sensitivity"] = "medium"
    row["side_effects"] = "none when open-only; product path never submits"
    row["cleanup"] = "not_applicable; read-only observation creates no records"
    row["errors"] = [
        "AUTH_REQUIRED",
        "AUTH_INTERACTION_REQUIRED",
        "UI_CHANGED",
        "EGRESS_DENIED",
        "BILLY_ERROR",
    ]


def apply_ui_clients_get_open_shell_evidence(
    row: dict[str, Any],
    *,
    parity_of_api_get: bool = False,
) -> None:
    """Mark clients detail **get/open only** evidence (research164).

    Empty-input tool; open /:org_slug/clients, open first non-header contact detail
    (path class /:org_slug/clients/:id or valued name drawer). Never Gem/Slet.
    Header-row false positives rejected. Requires scoped browser path_allow for
    GET /v2/contacts (and seed POST/DELETE when live harness creates disposables).
    When ``parity_of_api_get`` is true, dual-counts exact ``ui.parity.contacts.get``.
    """

    row["method_or_route"] = (
        "mit.billy.dk /:org_slug/clients + first non-header contact detail "
        "(read-only clients get/open; never Gem/Slet/Save submit; "
        "header-only dialog not success; soft /clients/new not success)"
    )
    row["tool_name"] = UI_CLIENTS_GET_OPEN_TOOL_NAME
    row["request_fields"] = []
    row["response_fields"] = [
        "path_class",
        "shell_kind",
        "detail_open",
        "contact_name_visible",
        "edit_action_visible",
        "detail_markers_present",
        "shell_markers_present",
    ]
    row["filters"] = []
    row["pagination"] = None
    if not parity_of_api_get:
        row["api_row_id"] = None
    row["test_references"] = [
        TEST_REFERENCE,
        UI_CLIENTS_GET_OPEN_MODEL_TEST_REFERENCE,
        UI_CLIENTS_GET_OPEN_UNIT_TEST_REFERENCE,
        UI_CLIENTS_GET_OPEN_LIVE_TEST_REFERENCE,
        SERVER_REGISTRY_TEST_REFERENCE,
    ]
    row["evidence"] = (
        "research164 dual-session headless observation + ui_clients_get_open product; "
        "scoped api.billysbilling.com path_allow for GET/POST/DELETE /v2/contacts and "
        "GET /v2/countries (data-plane was ERR_BLOCKED_BY_CLIENT under auth-only path_allow); "
        "detail open only (path class /:org_slug/contacts/:id/customer customer profile "
        "overview, shell_kind=clients_get, non-header row open with Name (Kunde) + Ret chrome; "
        "never Gem/Slet/Ret submit; header-only dialog rejected; distinct from list shell "
        "ui_clients_list and create form_open ui_clients_create_open); "
        "vision record tmp/vision-records/ui_clients_get_open.json "
        "(client detail frames, accept)"
    )
    if parity_of_api_get:
        row["evidence"] = f"{row['evidence']}; maps api.contacts.get to UI detail get/open only"
    row["discovered"] = True
    row["implemented"] = True
    row["contract_tested"] = True
    row["live_tested"] = True
    row["vision_verified"] = True
    row["vision_evidence"] = None
    row["parity_status"] = "detail_open_only"
    row["sensitivity"] = "medium"
    row["side_effects"] = "none when open-only; product path never submits"
    row["cleanup"] = (
        "not_applicable for product path; live harness may create disposable contact "
        "then delete in reverse with fresh list read-back"
    )
    row["errors"] = [
        "AUTH_REQUIRED",
        "AUTH_INTERACTION_REQUIRED",
        "UI_CHANGED",
        "EGRESS_DENIED",
        "BILLY_ERROR",
    ]


def apply_ui_clients_update_open_shell_evidence(
    row: dict[str, Any],
    *,
    parity_of_api_update: bool = False,
) -> None:
    """Mark clients update form **open only** evidence (research166).

    Empty-input tool; open /:org_slug/clients, open contact detail, click Ret,
    classify name-valued edit fields. Never Gem/Slet/Save. Distinct from get
    overview and create form. When ``parity_of_api_update`` is true, dual-counts
    exact ``ui.parity.contacts.update``.
    """

    row["method_or_route"] = (
        "mit.billy.dk /:org_slug/clients + contacts/:id/customer + Ret edit form "
        "(read-only clients update open; never Gem/Slet/Save submit; "
        "get overview without Ret not success; soft /clients/new not success)"
    )
    row["tool_name"] = UI_CLIENTS_UPDATE_OPEN_TOOL_NAME
    row["request_fields"] = []
    row["response_fields"] = [
        "path_class",
        "shell_kind",
        "edit_form_open",
        "name_field_visible",
        "name_field_has_value",
        "address_or_person_fields_present",
        "country_field_present",
        "shell_markers_present",
    ]
    row["filters"] = []
    row["pagination"] = None
    if not parity_of_api_update:
        row["api_row_id"] = None
    row["test_references"] = [
        TEST_REFERENCE,
        UI_CLIENTS_UPDATE_OPEN_MODEL_TEST_REFERENCE,
        UI_CLIENTS_UPDATE_OPEN_UNIT_TEST_REFERENCE,
        UI_CLIENTS_UPDATE_OPEN_LIVE_TEST_REFERENCE,
        SERVER_REGISTRY_TEST_REFERENCE,
    ]
    row["evidence"] = (
        "research166 dual-session headless observation + ui_clients_update_open product; "
        "scoped api.billysbilling.com path_allow for contacts data-plane (from research164); "
        "Ret edit form open only (path class /:org_slug/contacts/:id/customer, "
        "shell_kind=clients_update, name input valued + address/country content fields; "
        "never Gem/Slet submit; distinct from list shell ui_clients_list, create form_open "
        "ui_clients_create_open, and get overview ui_clients_get_open); "
        "vision record tmp/vision-records/ui_clients_update_open.json "
        "(client edit form frames, accept)"
    )
    if parity_of_api_update:
        row["evidence"] = (
            f"{row['evidence']}; maps api.contacts.update to UI Ret edit form open only"
        )
    row["discovered"] = True
    row["implemented"] = True
    row["contract_tested"] = True
    row["live_tested"] = True
    row["vision_verified"] = True
    row["vision_evidence"] = None
    row["parity_status"] = "form_open_only"
    row["sensitivity"] = "medium"
    row["side_effects"] = "none when open-only; product path never submits"
    row["cleanup"] = (
        "not_applicable for product path; live harness may create disposable contact "
        "then delete in reverse with fresh list read-back"
    )
    row["errors"] = [
        "AUTH_REQUIRED",
        "AUTH_INTERACTION_REQUIRED",
        "UI_CHANGED",
        "EGRESS_DENIED",
        "BILLY_ERROR",
    ]


def apply_ui_invoices_delete_open_shell_evidence(
    row: dict[str, Any],
    *,
    parity_of_api_delete: bool = False,
) -> None:
    """Mark invoices delete chrome **open only** evidence (research175).

    Empty-input tool; open /:org_slug/invoices/:id/edit, open Mere, classify
    exact Slet text (primary Slet button absent). Never confirm Slet/Send/Gem.
    Distinct from get/update freezes on the same path. When
    ``parity_of_api_delete`` is true, dual-counts exact ``ui.parity.invoices.delete``.
    """

    row["method_or_route"] = (
        "mit.billy.dk /:org_slug/invoices/:id/edit + Mere menu "
        "(read-only invoices delete chrome open; never confirm Slet; "
        "primary Slet button absent; soft /invoices/new not success)"
    )
    row["tool_name"] = UI_INVOICES_DELETE_OPEN_TOOL_NAME
    row["request_fields"] = []
    row["response_fields"] = [
        "path_class",
        "shell_kind",
        "edit_open",
        "mere_open",
        "slet_text_visible",
        "dupliker_visible",
        "primary_slet_absent",
        "shell_markers_present",
    ]
    row["filters"] = []
    row["pagination"] = None
    if not parity_of_api_delete:
        row["api_row_id"] = None
    row["test_references"] = [
        TEST_REFERENCE,
        UI_INVOICES_DELETE_OPEN_MODEL_TEST_REFERENCE,
        UI_INVOICES_DELETE_OPEN_UNIT_TEST_REFERENCE,
        UI_INVOICES_DELETE_OPEN_LIVE_TEST_REFERENCE,
        SERVER_REGISTRY_TEST_REFERENCE,
    ]
    row["evidence"] = (
        "research175 dual-session headless observation + ui_invoices_delete_open product; "
        "scoped api.billysbilling.com path_allow for invoices data-plane; "
        "Mere delete chrome open only (path class /:org_slug/invoices/:id/edit, "
        "shell_kind=invoices_delete, Slet text visible after Mere; never confirm delete; "
        "distinct from list shell ui_invoices_list, create form_open ui_invoices_create_open, "
        "get ui_invoices_get_open, and form_open ui_invoices_update_open); "
        "vision record tmp/vision-records/ui_invoices_delete_open.json "
        "(invoice delete chrome frames, accept)"
    )
    if parity_of_api_delete:
        row["evidence"] = (
            f"{row['evidence']}; maps api.invoices.delete to UI Mere delete chrome open only"
        )
    row["discovered"] = True
    row["implemented"] = True
    row["contract_tested"] = True
    row["live_tested"] = True
    row["vision_verified"] = True
    row["vision_evidence"] = None
    row["parity_status"] = "delete_chrome_open_only"
    row["sensitivity"] = "medium"
    row["side_effects"] = "none when open-only; product path never confirms delete"
    row["cleanup"] = (
        "not_applicable for product path; live harness may create disposable invoice "
        "then delete in reverse with fresh list read-back"
    )
    row["errors"] = [
        "AUTH_REQUIRED",
        "AUTH_INTERACTION_REQUIRED",
        "UI_CHANGED",
        "EGRESS_DENIED",
        "BILLY_ERROR",
    ]


def apply_ui_clients_delete_open_shell_evidence(
    row: dict[str, Any],
    *,
    parity_of_api_delete: bool = False,
) -> None:
    """Mark clients delete chrome **open only** evidence (research167).

    Empty-input tool; open /:org_slug/clients, open contact detail, open Mere,
    classify Slet kontakt visibility. Never confirm Slet/Arkivér. Distinct from
    get overview, Ret update form, and create dialog. When
    ``parity_of_api_delete`` is true, dual-counts exact ``ui.parity.contacts.delete``.
    """

    row["method_or_route"] = (
        "mit.billy.dk /:org_slug/clients + contacts/:id/customer + Mere menu "
        "(read-only clients delete chrome open; never confirm Slet/Arkivér; "
        "primary Slet absent; soft /clients/new not success)"
    )
    row["tool_name"] = UI_CLIENTS_DELETE_OPEN_TOOL_NAME
    row["request_fields"] = []
    row["response_fields"] = [
        "path_class",
        "shell_kind",
        "detail_open",
        "mere_open",
        "slet_kontakt_visible",
        "arkiver_kontakt_visible",
        "primary_slet_absent",
        "shell_markers_present",
    ]
    row["filters"] = []
    row["pagination"] = None
    if not parity_of_api_delete:
        row["api_row_id"] = None
    row["test_references"] = [
        TEST_REFERENCE,
        UI_CLIENTS_DELETE_OPEN_MODEL_TEST_REFERENCE,
        UI_CLIENTS_DELETE_OPEN_UNIT_TEST_REFERENCE,
        UI_CLIENTS_DELETE_OPEN_LIVE_TEST_REFERENCE,
        SERVER_REGISTRY_TEST_REFERENCE,
    ]
    row["evidence"] = (
        "research167 dual-session headless observation + ui_clients_delete_open product; "
        "scoped api.billysbilling.com path_allow for contacts data-plane (from research164); "
        "Mere delete chrome open only (path class /:org_slug/contacts/:id/customer, "
        "shell_kind=clients_delete, Slet kontakt visible after Mere; never confirm delete; "
        "distinct from list shell ui_clients_list, create form_open ui_clients_create_open, "
        "get overview ui_clients_get_open, and Ret form ui_clients_update_open); "
        "vision record tmp/vision-records/ui_clients_delete_open.json "
        "(client delete chrome frames, accept)"
    )
    if parity_of_api_delete:
        row["evidence"] = (
            f"{row['evidence']}; maps api.contacts.delete to UI Mere delete chrome open only"
        )
    row["discovered"] = True
    row["implemented"] = True
    row["contract_tested"] = True
    row["live_tested"] = True
    row["vision_verified"] = True
    row["vision_evidence"] = None
    row["parity_status"] = "delete_chrome_open_only"
    row["sensitivity"] = "medium"
    row["side_effects"] = "none when open-only; product path never confirms delete"
    row["cleanup"] = (
        "not_applicable for product path; live harness may create disposable contact "
        "then delete in reverse with fresh list read-back"
    )
    row["errors"] = [
        "AUTH_REQUIRED",
        "AUTH_INTERACTION_REQUIRED",
        "UI_CHANGED",
        "EGRESS_DENIED",
        "BILLY_ERROR",
    ]


def apply_ui_suppliers_create_open_shell_evidence(row: dict[str, Any]) -> None:
    """Mark suppliers create form **open only** evidence (research161).

    Empty-input tool; open /:org_slug/suppliers then click Opret kontakt dialog.
    Form open only — never Gem/Opret submit. Soft /suppliers/new rejected.
    Distinct from list shell ui_suppliers_list and clients create. Does **not**
    dual-count api.contacts.create (already mapped via ui_clients_create_open).
    """

    row["method_or_route"] = (
        "mit.billy.dk /:org_slug/suppliers + Opret kontakt dialog "
        "(read-only suppliers create form open; never Gem/Opret/Save submit; "
        "soft /suppliers/new not success)"
    )
    row["tool_name"] = UI_SUPPLIERS_CREATE_OPEN_TOOL_NAME
    row["request_fields"] = []
    row["response_fields"] = [
        "path_class",
        "heading",
        "shell_kind",
        "create_dialog_open",
        "name_field_visible",
        "registration_no_field_present",
        "address_or_person_fields_present",
        "shell_markers_present",
    ]
    row["filters"] = []
    row["pagination"] = None
    row["api_row_id"] = None
    row["test_references"] = [
        TEST_REFERENCE,
        UI_SUPPLIERS_CREATE_OPEN_MODEL_TEST_REFERENCE,
        UI_SUPPLIERS_CREATE_OPEN_UNIT_TEST_REFERENCE,
        UI_SUPPLIERS_CREATE_OPEN_LIVE_TEST_REFERENCE,
        SERVER_REGISTRY_TEST_REFERENCE,
    ]
    row["evidence"] = (
        "research161 dual-session headless observation + ui_suppliers_create_open product; "
        "form open only (path class /:org_slug/suppliers, h1 Leverandører, "
        "shell_kind=suppliers_create, CTA Opret kontakt dialog with "
        "name+registrationNo+person/street fields; never submit; soft /suppliers/new "
        "not success path; distinct from list shell ui_suppliers_list and clients create; "
        "does not re-count api.contacts.create); "
        "vision record tmp/vision-records/ui_suppliers_create_open.json "
        "(Opret kontakt create dialog frames, accept)"
    )
    row["discovered"] = True
    row["implemented"] = True
    row["contract_tested"] = True
    row["live_tested"] = True
    row["vision_verified"] = True
    row["vision_evidence"] = None
    row["parity_status"] = "form_open_only"
    row["sensitivity"] = "medium"
    row["side_effects"] = "none when open-only; product path never submits"
    row["cleanup"] = "not_applicable; read-only observation creates no records"
    row["errors"] = [
        "AUTH_REQUIRED",
        "AUTH_INTERACTION_REQUIRED",
        "UI_CHANGED",
        "EGRESS_DENIED",
        "BILLY_ERROR",
    ]


def apply_ui_products_create_open_shell_evidence(
    row: dict[str, Any],
    *,
    parity_of_api_create: bool = False,
) -> None:
    """Mark products create form **open only** evidence (research163).

    Empty-input tool; open /:org_slug/inventory then click Opret produkt.
    Form open only — never Gem/Opret submit. Soft /products/new rejected.
    Catalog /products has no create CTA. Distinct from list shell and
    shell-only inventory open. When ``parity_of_api_create`` is true, dual-counts
    exact ``ui.parity.products.create`` for ``api.products.create``.
    """

    row["method_or_route"] = (
        "mit.billy.dk /:org_slug/inventory + Opret produkt form "
        "(read-only products create form open; never Gem/Opret/Save submit; "
        "soft /products/new not success; catalog /products list has no create CTA)"
    )
    row["tool_name"] = UI_PRODUCTS_CREATE_OPEN_TOOL_NAME
    row["request_fields"] = []
    row["response_fields"] = [
        "path_class",
        "heading",
        "shell_kind",
        "create_form_open",
        "name_field_visible",
        "account_field_present",
        "sales_tax_ruleset_field_present",
        "unit_price_field_present",
        "shell_markers_present",
    ]
    row["filters"] = []
    row["pagination"] = None
    if not parity_of_api_create:
        row["api_row_id"] = None
    row["test_references"] = [
        TEST_REFERENCE,
        UI_PRODUCTS_CREATE_OPEN_MODEL_TEST_REFERENCE,
        UI_PRODUCTS_CREATE_OPEN_UNIT_TEST_REFERENCE,
        UI_PRODUCTS_CREATE_OPEN_LIVE_TEST_REFERENCE,
        SERVER_REGISTRY_TEST_REFERENCE,
    ]
    row["evidence"] = (
        "research163 dual-session headless observation + ui_products_create_open product; "
        "form open only (path class /:org_slug/inventory, h1 Lagermodul, "
        "shell_kind=products_create, CTA Opret produkt form with "
        "name+account+salesTaxRuleset+unitPrice fields; never submit; soft /products/new "
        "chrome-only rejected; catalog /products Mere export/import only; distinct from "
        "list shell ui_products_list and shell-only ui_inventory_open; unitPrice is create "
        "embed chrome not productPrices resource — productPrices dual-NA research162); "
        "vision record tmp/vision-records/ui_products_create_open.json "
        "(Opret produkt create form frames, accept)"
    )
    if parity_of_api_create:
        row["evidence"] = f"{row['evidence']}; maps api.products.create to UI create-form open only"
    row["discovered"] = True
    row["implemented"] = True
    row["contract_tested"] = True
    row["live_tested"] = True
    row["vision_verified"] = True
    row["vision_evidence"] = None
    row["parity_status"] = "form_open_only"
    row["sensitivity"] = "medium"
    row["side_effects"] = "none when open-only; product path never submits"
    row["cleanup"] = "not_applicable; read-only observation creates no records"
    row["errors"] = [
        "AUTH_REQUIRED",
        "AUTH_INTERACTION_REQUIRED",
        "UI_CHANGED",
        "EGRESS_DENIED",
        "BILLY_ERROR",
    ]


def apply_ui_bank_accounts_list_shell_evidence(row: dict[str, Any]) -> None:
    """Mark bank accounts list **shell open** evidence only (research105 / plan 186.6).

    UI-only: no bankAccounts API resource. Empty-input tool; path /bank-accounts,
    h1 Bankkonti, CTA Forbind til bank. vision_evidence stays null.
    """

    row["method_or_route"] = "mit.billy.dk /:org_slug/bank-accounts (read-only list shell open)"
    row["tool_name"] = UI_BANK_ACCOUNTS_LIST_TOOL_NAME
    row["request_fields"] = []
    row["response_fields"] = [
        "path_class",
        "heading",
        "connect_bank_action_visible",
        "shell_markers_present",
    ]
    row["filters"] = []
    row["pagination"] = None
    row["api_row_id"] = None
    row["test_references"] = [
        TEST_REFERENCE,
        UI_BANK_ACCOUNTS_LIST_MODEL_TEST_REFERENCE,
        UI_BANK_ACCOUNTS_LIST_UNIT_TEST_REFERENCE,
        UI_BANK_ACCOUNTS_LIST_LIVE_TEST_REFERENCE,
        SERVER_REGISTRY_TEST_REFERENCE,
    ]
    row["evidence"] = (
        "research105 dual-session headless observation + ui_bank_accounts_list product; "
        "UI-only list shell (path class, h1 Bankkonti, CTA Forbind til bank present, no connect); "
        "no bankAccounts API resource; do not invent api_bank_accounts_*; "
        "does not green bankLines/bankPayments parity; "
        "vision record tmp/vision-records/ui_bank_accounts_list.json (list surface frames, accept)"
    )
    row["discovered"] = True
    row["implemented"] = True
    row["contract_tested"] = True
    row["live_tested"] = True
    row["vision_verified"] = True
    row["vision_evidence"] = None
    row["parity_status"] = "list_shell_open_only"
    row["sensitivity"] = "low"
    row["side_effects"] = "none"
    row["cleanup"] = "not_applicable; read-only observation creates no records"
    row["errors"] = [
        "AUTH_REQUIRED",
        "AUTH_INTERACTION_REQUIRED",
        "UI_CHANGED",
        "EGRESS_DENIED",
        "BILLY_ERROR",
    ]


def apply_ui_quotes_list_shell_evidence(row: dict[str, Any]) -> None:
    """Mark quotes list **shell open** evidence only (research106 / plan 186.7).

    UI-only: no quotes API resource. Empty-input tool; path /quotes (optional /empty),
    h1 Tilbud, CTA Opret tilbud. vision_evidence stays null.
    """

    row["method_or_route"] = (
        "mit.billy.dk /:org_slug/quotes (read-only list shell open; empty suffix allowed)"
    )
    row["tool_name"] = UI_QUOTES_LIST_TOOL_NAME
    row["request_fields"] = []
    row["response_fields"] = [
        "path_class",
        "heading",
        "create_action_visible",
        "shell_markers_present",
    ]
    row["filters"] = []
    row["pagination"] = None
    row["api_row_id"] = None
    row["test_references"] = [
        TEST_REFERENCE,
        UI_QUOTES_LIST_MODEL_TEST_REFERENCE,
        UI_QUOTES_LIST_UNIT_TEST_REFERENCE,
        UI_QUOTES_LIST_LIVE_TEST_REFERENCE,
        SERVER_REGISTRY_TEST_REFERENCE,
    ]
    row["evidence"] = (
        "research106 dual-session headless observation + ui_quotes_list product; "
        "UI-only list shell (path class /:org_slug/quotes, empty /quotes/empty accepted, "
        "h1 Tilbud, CTA Opret tilbud present, no create); "
        "no quotes API resource; do not invent api_quotes_*; "
        "does not green invoices quoteId UI parity or recurring_invoices; "
        "vision record tmp/vision-records/ui_quotes_list.json (list surface frames, accept)"
    )
    row["discovered"] = True
    row["implemented"] = True
    row["contract_tested"] = True
    row["live_tested"] = True
    row["vision_verified"] = True
    row["vision_evidence"] = None
    row["parity_status"] = "list_shell_open_only"
    row["sensitivity"] = "low"
    row["side_effects"] = "none"
    row["cleanup"] = "not_applicable; read-only observation creates no records"
    row["errors"] = [
        "AUTH_REQUIRED",
        "AUTH_INTERACTION_REQUIRED",
        "UI_CHANGED",
        "EGRESS_DENIED",
        "BILLY_ERROR",
    ]


def apply_ui_recurring_invoices_list_shell_evidence(row: dict[str, Any]) -> None:
    """Mark recurring invoices list **shell open** evidence only (research107 / plan 186.8).

    UI-only: no recurring invoices API resource. Empty-input tool; path
    /recurring_invoices (optional /empty), h1 Abonnementer, CTA Opret abonnement.
    vision_evidence stays null.
    """

    row["method_or_route"] = (
        "mit.billy.dk /:org_slug/recurring_invoices "
        "(read-only list shell open; empty suffix allowed)"
    )
    row["tool_name"] = UI_RECURRING_INVOICES_LIST_TOOL_NAME
    row["request_fields"] = []
    row["response_fields"] = [
        "path_class",
        "heading",
        "create_action_visible",
        "shell_markers_present",
    ]
    row["filters"] = []
    row["pagination"] = None
    row["api_row_id"] = None
    row["test_references"] = [
        TEST_REFERENCE,
        UI_RECURRING_INVOICES_LIST_MODEL_TEST_REFERENCE,
        UI_RECURRING_INVOICES_LIST_UNIT_TEST_REFERENCE,
        UI_RECURRING_INVOICES_LIST_LIVE_TEST_REFERENCE,
        SERVER_REGISTRY_TEST_REFERENCE,
    ]
    row["evidence"] = (
        "research107 dual-session headless observation + ui_recurring_invoices_list product; "
        "UI-only list shell (path class /:org_slug/recurring_invoices, optional /empty, "
        "h1 Abonnementer, CTA Opret abonnement present, no create); "
        "no recurring invoices API resource; do not invent api_recurring_*; "
        "does not green invoices recurringInvoiceId UI parity; "
        "vision record tmp/vision-records/ui_recurring_invoices_list.json "
        "(list surface frames, accept)"
    )
    row["discovered"] = True
    row["implemented"] = True
    row["contract_tested"] = True
    row["live_tested"] = True
    row["vision_verified"] = True
    row["vision_evidence"] = None
    row["parity_status"] = "list_shell_open_only"
    row["sensitivity"] = "low"
    row["side_effects"] = "none"
    row["cleanup"] = "not_applicable; read-only observation creates no records"
    row["errors"] = [
        "AUTH_REQUIRED",
        "AUTH_INTERACTION_REQUIRED",
        "UI_CHANGED",
        "EGRESS_DENIED",
        "BILLY_ERROR",
    ]


def apply_ui_products_import_shell_evidence(row: dict[str, Any]) -> None:
    """Mark products import **shell open** evidence only (research108 / plan 186.9).

    UI-only: no product CSV import API. Empty-input tool; path /products/import,
    h1 Import af produkter, control Vælg CSV-fil present only (never choose/upload).
    vision_evidence stays null.
    """

    row["method_or_route"] = (
        "mit.billy.dk /:org_slug/products/import (read-only import shell open; no file upload)"
    )
    row["tool_name"] = UI_PRODUCTS_IMPORT_TOOL_NAME
    row["request_fields"] = []
    row["response_fields"] = [
        "path_class",
        "heading",
        "choose_csv_action_visible",
        "shell_markers_present",
    ]
    row["filters"] = []
    row["pagination"] = None
    row["api_row_id"] = None
    row["test_references"] = [
        TEST_REFERENCE,
        UI_PRODUCTS_IMPORT_MODEL_TEST_REFERENCE,
        UI_PRODUCTS_IMPORT_UNIT_TEST_REFERENCE,
        UI_PRODUCTS_IMPORT_LIVE_TEST_REFERENCE,
        SERVER_REGISTRY_TEST_REFERENCE,
    ]
    row["evidence"] = (
        "research108 dual-session headless observation + ui_products_import product; "
        "UI-only import shell (path class /:org_slug/products/import, "
        "h1 Import af produkter, CTA Vælg CSV-fil present, no file choose/upload); "
        "no product import API resource; do not invent api_products_import_*; "
        "does not green suppliers/bills/balances/uploads discovery; "
        "vision record tmp/vision-records/ui_products_import.json "
        "(import surface frames, accept)"
    )
    row["discovered"] = True
    row["implemented"] = True
    row["contract_tested"] = True
    row["live_tested"] = True
    row["vision_verified"] = True
    row["vision_evidence"] = None
    row["parity_status"] = "list_shell_open_only"
    row["sensitivity"] = "low"
    row["side_effects"] = "none"
    row["cleanup"] = "not_applicable; read-only observation creates no records"
    row["errors"] = [
        "AUTH_REQUIRED",
        "AUTH_INTERACTION_REQUIRED",
        "UI_CHANGED",
        "EGRESS_DENIED",
        "BILLY_ERROR",
    ]


def apply_ui_suppliers_list_shell_evidence(row: dict[str, Any]) -> None:
    """Mark suppliers list **shell open** evidence only (research109 / plan 186.10).

    Empty-input tool; path /suppliers, h1 Leverandører, CTA Opret kontakt present only
    (never create). No separate suppliers API resource (contacts isSupplier).
    vision_evidence stays null. Does not re-green api.contacts.list live cells.
    """

    row["method_or_route"] = "mit.billy.dk /:org_slug/suppliers (read-only list shell open)"
    row["tool_name"] = UI_SUPPLIERS_LIST_TOOL_NAME
    row["request_fields"] = []
    row["response_fields"] = [
        "path_class",
        "heading",
        "create_action_visible",
        "shell_markers_present",
    ]
    row["filters"] = []
    row["pagination"] = None
    row["api_row_id"] = None
    row["test_references"] = [
        TEST_REFERENCE,
        UI_SUPPLIERS_LIST_MODEL_TEST_REFERENCE,
        UI_SUPPLIERS_LIST_UNIT_TEST_REFERENCE,
        UI_SUPPLIERS_LIST_LIVE_TEST_REFERENCE,
        SERVER_REGISTRY_TEST_REFERENCE,
    ]
    row["evidence"] = (
        "research109 dual-session headless observation + ui_suppliers_list product; "
        "list shell only (path class /:org_slug/suppliers, h1 Leverandører, "
        "CTA Opret kontakt present, no create); no suppliers API resource "
        "(vendors are contacts with isSupplier); do not invent api_suppliers_*; "
        "does not green purchases/bills/balances/uploads discovery; "
        "vision record tmp/vision-records/ui_suppliers_list.json "
        "(list surface frames, accept)"
    )
    row["discovered"] = True
    row["implemented"] = True
    row["contract_tested"] = True
    row["live_tested"] = True
    row["vision_verified"] = True
    row["vision_evidence"] = None
    row["parity_status"] = "list_shell_open_only"
    row["sensitivity"] = "low"
    row["side_effects"] = "none"
    row["cleanup"] = "not_applicable; read-only observation creates no records"
    row["errors"] = [
        "AUTH_REQUIRED",
        "AUTH_INTERACTION_REQUIRED",
        "UI_CHANGED",
        "EGRESS_DENIED",
        "BILLY_ERROR",
    ]


def apply_ui_bills_list_shell_evidence(
    row: dict[str, Any],
    *,
    parity_of_api_list: bool = False,
) -> None:
    """Mark bills/purchases list **shell open** evidence only (research110 / plan 186.11).

    Empty-input tool; path /bills, h1 Køb, CTA Opret køb present only (never create).
    Discovery family is purchases; real route is bills. vision_evidence stays null.
    Does not green bill create/update/delete/bulk or billLines parity rows.
    """

    row["method_or_route"] = "mit.billy.dk /:org_slug/bills (read-only list shell open)"
    row["tool_name"] = UI_BILLS_LIST_TOOL_NAME
    row["request_fields"] = []
    row["response_fields"] = [
        "path_class",
        "heading",
        "create_action_visible",
        "shell_markers_present",
    ]
    row["filters"] = []
    row["pagination"] = None
    if not parity_of_api_list:
        row["api_row_id"] = None
    row["test_references"] = [
        TEST_REFERENCE,
        UI_BILLS_LIST_MODEL_TEST_REFERENCE,
        UI_BILLS_LIST_UNIT_TEST_REFERENCE,
        UI_BILLS_LIST_LIVE_TEST_REFERENCE,
        SERVER_REGISTRY_TEST_REFERENCE,
    ]
    row["evidence"] = (
        "research110 dual-session headless observation + ui_bills_list product; "
        "list shell only (path class /:org_slug/bills, h1 Køb, CTA Opret køb present, "
        "no create); inventory discovery family purchases maps to bills route; "
        "do not invent api_purchases_*; aliases purchases/purchase/bill/regninger/kob "
        "rejected; does not green bill create/bulk, billLines, balances, or uploads; "
        "API list filters/sort/pagination UI not producted; "
        "vision record tmp/vision-records/ui_bills_list.json (list surface frames, accept)"
    )
    if parity_of_api_list:
        row["evidence"] = f"{row['evidence']}; maps api.bills.list to UI list-shell open only"
    row["discovered"] = True
    row["implemented"] = True
    row["contract_tested"] = True
    row["live_tested"] = True
    row["vision_verified"] = True
    row["vision_evidence"] = None
    row["parity_status"] = "list_shell_open_only"
    row["sensitivity"] = "low"
    row["side_effects"] = "none"
    row["cleanup"] = "not_applicable; read-only observation creates no records"
    row["errors"] = [
        "AUTH_REQUIRED",
        "AUTH_INTERACTION_REQUIRED",
        "UI_CHANGED",
        "EGRESS_DENIED",
        "BILLY_ERROR",
    ]


def apply_ui_debtor_balances_list_shell_evidence(row: dict[str, Any]) -> None:
    """Mark debtor balances list **shell open** evidence only (research111 / plan 186.12).

    Empty-input tool; path /debtorbalance, h1 Tilgodehavender, CTA Opret faktura present
    only (never create). No official /v2/debtorbalance resource — discovery only.
    Does not green creditor_balances or contactBalance*/balanceModifiers parity.
    """

    row["method_or_route"] = "mit.billy.dk /:org_slug/debtorbalance (read-only list shell open)"
    row["tool_name"] = UI_DEBTOR_BALANCES_LIST_TOOL_NAME
    row["request_fields"] = []
    row["response_fields"] = [
        "path_class",
        "heading",
        "create_action_visible",
        "shell_markers_present",
    ]
    row["filters"] = []
    row["pagination"] = None
    row["api_row_id"] = None
    row["test_references"] = [
        TEST_REFERENCE,
        UI_DEBTOR_BALANCES_LIST_MODEL_TEST_REFERENCE,
        UI_DEBTOR_BALANCES_LIST_UNIT_TEST_REFERENCE,
        UI_DEBTOR_BALANCES_LIST_LIVE_TEST_REFERENCE,
        SERVER_REGISTRY_TEST_REFERENCE,
    ]
    row["evidence"] = (
        "research111 dual-session headless observation + ui_debtor_balances_list product; "
        "list shell only (path class /:org_slug/debtorbalance, h1 Tilgodehavender, "
        "CTA Opret faktura present, no create); no invent api_debtor_balances_*; "
        "aliases debtor-balances/debtor_balances/tilgodehavender/receivables rejected; "
        "does not green creditor_balances, contactBalance*, balanceModifiers, or uploads; "
        "API list filters/sort/pagination UI not producted; "
        "vision record tmp/vision-records/ui_debtor_balances_list.json "
        "(list surface frames, accept)"
    )
    row["discovered"] = True
    row["implemented"] = True
    row["contract_tested"] = True
    row["live_tested"] = True
    row["vision_verified"] = True
    row["vision_evidence"] = None
    row["parity_status"] = "list_shell_open_only"
    row["sensitivity"] = "low"
    row["side_effects"] = "none"
    row["cleanup"] = "not_applicable; read-only observation creates no records"
    row["errors"] = [
        "AUTH_REQUIRED",
        "AUTH_INTERACTION_REQUIRED",
        "UI_CHANGED",
        "EGRESS_DENIED",
        "BILLY_ERROR",
    ]


def apply_ui_creditor_balances_list_shell_evidence(row: dict[str, Any]) -> None:
    """Mark creditor balances list **shell open** evidence only (research112 / plan 186.13).

    Empty-input tool; path /creditorbalance, h1 Skyldige udgifter, CTA Opret køb present
    only (never create). No official /v2/creditorbalance resource — discovery only.
    Does not green uploads or contactBalance*/balanceModifiers parity.
    """

    row["method_or_route"] = "mit.billy.dk /:org_slug/creditorbalance (read-only list shell open)"
    row["tool_name"] = UI_CREDITOR_BALANCES_LIST_TOOL_NAME
    row["request_fields"] = []
    row["response_fields"] = [
        "path_class",
        "heading",
        "create_action_visible",
        "shell_markers_present",
    ]
    row["filters"] = []
    row["pagination"] = None
    row["api_row_id"] = None
    row["test_references"] = [
        TEST_REFERENCE,
        UI_CREDITOR_BALANCES_LIST_MODEL_TEST_REFERENCE,
        UI_CREDITOR_BALANCES_LIST_UNIT_TEST_REFERENCE,
        UI_CREDITOR_BALANCES_LIST_LIVE_TEST_REFERENCE,
        SERVER_REGISTRY_TEST_REFERENCE,
    ]
    row["evidence"] = (
        "research112 dual-session headless observation + ui_creditor_balances_list product; "
        "list shell only (path class /:org_slug/creditorbalance, h1 Skyldige udgifter, "
        "CTA Opret køb present, no create); no invent api_creditor_balances_*; "
        "aliases creditor-balances/creditor_balances/payables/skyldige-udgifter rejected; "
        "does not green uploads, contactBalance*, balanceModifiers, or debtor re-scope; "
        "API list filters/sort/pagination UI not producted; "
        "vision record tmp/vision-records/ui_creditor_balances_list.json "
        "(list surface frames, accept)"
    )
    row["discovered"] = True
    row["implemented"] = True
    row["contract_tested"] = True
    row["live_tested"] = True
    row["vision_verified"] = True
    row["vision_evidence"] = None
    row["parity_status"] = "list_shell_open_only"
    row["sensitivity"] = "low"
    row["side_effects"] = "none"
    row["cleanup"] = "not_applicable; read-only observation creates no records"
    row["errors"] = [
        "AUTH_REQUIRED",
        "AUTH_INTERACTION_REQUIRED",
        "UI_CHANGED",
        "EGRESS_DENIED",
        "BILLY_ERROR",
    ]


def apply_ui_uploads_list_shell_evidence(
    row: dict[str, Any],
    *,
    parity_of_special_files_upload: bool = False,
    parity_of_api_attachments_list: bool = False,
    parity_of_api_files_create: bool = False,
) -> None:
    """Mark uploads (Bilag) list shell + upload-surface open evidence.

    research113 / plan 186.14 list shell; research155 strengthens file-input
    binding chrome (input[type=file] present; never set). Empty-input tool;
    path /uploads, h1 Bilag, CTA Upload filer, file_input_present. No official
    /v2/uploads resource. Does not green receipt_inbox. Dual-count flags are
    mutually exclusive per call:

    - ``parity_of_special_files_upload`` → ``api.special.files_upload``
    - ``parity_of_api_attachments_list`` → ``api.attachments.list`` (research184;
      Bilag SPA hits /v2/attachments dual)
    - ``parity_of_api_files_create`` → ``api.files.create`` (research184;
      upload-surface open only; peer special.files_upload)

    Does not dual-count attachments.get/create/update/delete onto Bilag (those
    are research185 NA) or files.list/get (research184 NA).
    """

    parity_flags = (
        parity_of_special_files_upload,
        parity_of_api_attachments_list,
        parity_of_api_files_create,
    )
    if sum(1 for flag in parity_flags if flag) > 1:
        raise ValueError("uploads dual-count flags are mutually exclusive")

    row["method_or_route"] = (
        "mit.billy.dk /:org_slug/uploads (read-only Bilag list + upload-surface "
        "open; never set input[type=file] / never submit upload)"
    )
    row["tool_name"] = UI_UPLOADS_LIST_TOOL_NAME
    row["request_fields"] = []
    row["response_fields"] = [
        "path_class",
        "heading",
        "upload_action_visible",
        "file_input_present",
        "shell_markers_present",
    ]
    row["filters"] = []
    row["pagination"] = None
    if not any(parity_flags):
        row["api_row_id"] = None
    row["test_references"] = [
        TEST_REFERENCE,
        UI_UPLOADS_LIST_MODEL_TEST_REFERENCE,
        UI_UPLOADS_LIST_UNIT_TEST_REFERENCE,
        UI_UPLOADS_LIST_LIVE_TEST_REFERENCE,
        SERVER_REGISTRY_TEST_REFERENCE,
    ]
    row["evidence"] = (
        "research113 dual-session headless observation + ui_uploads_list product; "
        "research155 dual reconfirm file_input_present (input[type=file] count "
        "class ≥1 both sessions; never set files); list shell only (path class "
        "/:org_slug/uploads, h1 Bilag, CTA Upload filer present, no file pick); "
        "no invent api_uploads_*/api_bilag_*; does not green receipt_inbox, "
        "attachments residual closed by research185 NA, files.list/get research184 NA, "
        "invoice_email; "
        "API list filters/sort/pagination UI not producted; vision record "
        "tmp/vision-records/ui_uploads_list.json (list surface frames, accept)"
    )
    if parity_of_special_files_upload:
        row["evidence"] = (
            f"{row['evidence']}; research155 dual-session reconfirm; maps "
            "api.special.files_upload (POST /v2/files binary upload surface) to "
            "UI Bilag upload-surface open only"
        )
    if parity_of_api_attachments_list:
        row["evidence"] = (
            f"{row['evidence']}; research184 dual-session: Bilag SPA resource hits "
            "/v2/attachments dual (files hits 0); soft /attachments empty dual; maps "
            "api.attachments.list to UI Bilag list shell open only; residual "
            "get/create/update/delete are research185 NA (not dual-count)"
        )
    if parity_of_api_files_create:
        row["evidence"] = (
            f"{row['evidence']}; research184 dual-session: maps api.files.create to "
            "UI Bilag upload-surface open only (peer special.files_upload; never set "
            "input[type=file] / never submit); soft /files empty dual is not list/get"
        )
    row["discovered"] = True
    row["implemented"] = True
    row["contract_tested"] = True
    row["live_tested"] = True
    row["vision_verified"] = True
    row["vision_evidence"] = None
    if parity_of_api_files_create:
        row["parity_status"] = "create_chrome_open_only"
        row["sensitivity"] = "medium"
        row["side_effects"] = "none when open-only; product path never submits upload"
    else:
        row["parity_status"] = "list_shell_open_only"
        row["sensitivity"] = "low"
        row["side_effects"] = "none"
    row["cleanup"] = "not_applicable; read-only observation creates no records"
    row["errors"] = [
        "AUTH_REQUIRED",
        "AUTH_INTERACTION_REQUIRED",
        "UI_CHANGED",
        "EGRESS_DENIED",
        "BILLY_ERROR",
    ]


def apply_ui_receipt_inbox_list_shell_evidence(row: dict[str, Any]) -> None:
    """Mark receipt inbox (Bilagsindbakke) list **shell open** evidence only (research114).

    Empty-input tool; path /vouchers, h1 Bilagsindbakke; file input presence only
    (never set). Distinct from uploads/Bilag. No official /v2/vouchers resource.
    Does not green uploads, files/attachments/files_upload parity.
    """

    row["method_or_route"] = "mit.billy.dk /:org_slug/vouchers (read-only list shell open)"
    row["tool_name"] = UI_RECEIPT_INBOX_LIST_TOOL_NAME
    row["request_fields"] = []
    row["response_fields"] = [
        "path_class",
        "heading",
        "file_control_present",
        "shell_markers_present",
    ]
    row["filters"] = []
    row["pagination"] = None
    row["api_row_id"] = None
    row["test_references"] = [
        TEST_REFERENCE,
        UI_RECEIPT_INBOX_LIST_MODEL_TEST_REFERENCE,
        UI_RECEIPT_INBOX_LIST_UNIT_TEST_REFERENCE,
        UI_RECEIPT_INBOX_LIST_LIVE_TEST_REFERENCE,
        SERVER_REGISTRY_TEST_REFERENCE,
    ]
    row["evidence"] = (
        "research114 dual-session headless observation + ui_receipt_inbox_list product; "
        "list shell only (path class /:org_slug/vouchers, h1 Bilagsindbakke, "
        "file input present observe-only, never set, never click Ret); "
        "no invent api_vouchers_*/api_receipt_inbox_*/api_bilagsindbakke_*; "
        "aliases inbox/receipts/kvittering/indbakke/voucher rejected; "
        "distinct from uploads Bilag; does not green uploads, files*, attachments*, "
        "special.files_upload; API list filters/sort/pagination UI not producted; "
        "vision record tmp/vision-records/ui_receipt_inbox_list.json "
        "(list surface frames, accept)"
    )
    row["discovered"] = True
    row["implemented"] = True
    row["contract_tested"] = True
    row["live_tested"] = True
    row["vision_verified"] = True
    row["vision_evidence"] = None
    row["parity_status"] = "list_shell_open_only"
    row["sensitivity"] = "low"
    row["side_effects"] = "none"
    row["cleanup"] = "not_applicable; read-only observation creates no records"
    row["errors"] = [
        "AUTH_REQUIRED",
        "AUTH_INTERACTION_REQUIRED",
        "UI_CHANGED",
        "EGRESS_DENIED",
        "BILLY_ERROR",
    ]


def apply_ui_bank_reconciliation_open_shell_evidence(row: dict[str, Any]) -> None:
    """Mark bank reconciliation (Afstemning) **shell open** evidence only (research115).

    Empty-input tool; path /:org_slug/bank_accounts/:id/sync (underscore); harvest
    Afstemning nav href; empty content shell valid in test org. Distinct from
    bank-accounts list / Bankkonti. No invent api_bank_accounts_*/reconciliation.
    Does not green bank_accounts discovery or bankLines/bankLineMatches/bankPayments
    UI parity. Never connect/import/match.
    """

    row["method_or_route"] = (
        "mit.billy.dk /:org_slug/bank_accounts/:id/sync (Afstemning shell open only)"
    )
    row["tool_name"] = UI_BANK_RECONCILIATION_OPEN_TOOL_NAME
    row["request_fields"] = []
    row["response_fields"] = [
        "path_class",
        "heading",
        "empty_content_shell",
        "afstemning_nav_visible",
        "shell_markers_present",
    ]
    row["filters"] = []
    row["pagination"] = None
    row["api_row_id"] = None
    row["test_references"] = [
        TEST_REFERENCE,
        UI_BANK_RECONCILIATION_OPEN_MODEL_TEST_REFERENCE,
        UI_BANK_RECONCILIATION_OPEN_UNIT_TEST_REFERENCE,
        UI_BANK_RECONCILIATION_OPEN_LIVE_TEST_REFERENCE,
        SERVER_REGISTRY_TEST_REFERENCE,
    ]
    row["evidence"] = (
        "research115 dual-session headless observation + ui_bank_reconciliation_open product; "
        "shell open only (path class /:org_slug/bank_accounts/:id/sync via Afstemning href "
        "harvest; empty content shell valid; never invent account id; never click Forbind/"
        "Importer/Match); no invent api_bank_accounts_*/api_reconciliation_*/api_afstemning_*; "
        "aliases bank-reconciliation/afstemning/query variants rejected; distinct from "
        "bank-accounts Bankkonti; does not green bank_accounts, bankLines*, bankLineMatches*, "
        "bankPayments* parity; vision record tmp/vision-records/ui_bank_reconciliation_open.json "
        "(recon surface frames, accept)"
    )
    row["discovered"] = True
    row["implemented"] = True
    row["contract_tested"] = True
    row["live_tested"] = True
    row["vision_verified"] = True
    row["vision_evidence"] = None
    row["parity_status"] = "shell_open_only"
    row["sensitivity"] = "low"
    row["side_effects"] = "none"
    row["cleanup"] = "not_applicable; read-only observation creates no records"
    row["errors"] = [
        "AUTH_REQUIRED",
        "AUTH_INTERACTION_REQUIRED",
        "UI_CHANGED",
        "EGRESS_DENIED",
        "BILLY_ERROR",
    ]


def apply_ui_financing_open_shell_evidence(row: dict[str, Any]) -> None:
    """Mark financing **shell open** evidence only (research116).

    Empty-input tool; path /:org_slug/financing; h1 Ansøg om erhvervslån.
    No invent api_financing_*/loans. Never click apply/offer/submit (design §14.4).
    Does not green bank_accounts or bank_reconciliation discovery.
    """

    row["method_or_route"] = (
        "mit.billy.dk /:org_slug/financing (read-only financing shell open only)"
    )
    row["tool_name"] = UI_FINANCING_OPEN_TOOL_NAME
    row["request_fields"] = []
    row["response_fields"] = [
        "path_class",
        "heading",
        "apply_cta_observed",
        "shell_markers_present",
    ]
    row["filters"] = []
    row["pagination"] = None
    row["api_row_id"] = None
    row["test_references"] = [
        TEST_REFERENCE,
        UI_FINANCING_OPEN_MODEL_TEST_REFERENCE,
        UI_FINANCING_OPEN_UNIT_TEST_REFERENCE,
        UI_FINANCING_OPEN_LIVE_TEST_REFERENCE,
        SERVER_REGISTRY_TEST_REFERENCE,
    ]
    row["evidence"] = (
        "research116 dual-session headless observation + ui_financing_open product; "
        "shell open only (path class /:org_slug/financing; h1 Ansøg om erhvervslån; "
        "Bank nav Ansøg om lån; apply CTA observe-only Få et uforpligtende tilbud; "
        "never click apply/offer/consent/submit per design §14.4); no invent "
        "api_financing_*/api_loans_*/api_froda_*; soft subpaths and aliases rejected; "
        "distinct from bank-accounts Bankkonti and bank recon Afstemning; does not "
        "green bank_accounts or bank_reconciliation; vision record "
        "tmp/vision-records/ui_financing_open.json (landing frames, accept)"
    )
    row["discovered"] = True
    row["implemented"] = True
    row["contract_tested"] = True
    row["live_tested"] = True
    row["vision_verified"] = True
    row["vision_evidence"] = None
    row["parity_status"] = "shell_open_only"
    row["sensitivity"] = "low"
    row["side_effects"] = "none"
    row["cleanup"] = "not_applicable; read-only observation creates no records"
    row["errors"] = [
        "AUTH_REQUIRED",
        "AUTH_INTERACTION_REQUIRED",
        "UI_CHANGED",
        "EGRESS_DENIED",
        "BILLY_ERROR",
    ]


def apply_ui_daybooks_open_shell_evidence(
    row: dict[str, Any],
    *,
    parity_of_api_list: bool = False,
    parity_of_api_create: bool = False,
) -> None:
    """Mark daybooks **editor shell / create-form open** evidence (research117).

    Empty-input tool; path /:org_slug/daybooks/new; editor markers (no h1).
    Bare /daybooks is Upsedasse (not success). No invent API tools.
    Never click create/add-line/post. Does not green transactions discovery.
    When ``parity_of_api_list`` is true, dual-counts ``ui.parity.daybooks.list``
    for ``api.daybooks.list`` (research156). When ``parity_of_api_create`` is
    true, dual-counts ``ui.parity.daybooks.create`` for ``api.daybooks.create``
    (research157, form_open_only). Flags are mutually exclusive per call.
    """

    if parity_of_api_list and parity_of_api_create:
        raise ValueError("daybooks dual-count flags are mutually exclusive")

    if parity_of_api_create:
        row["method_or_route"] = (
            "mit.billy.dk /:org_slug/daybooks/new (read-only daybook create form open only; "
            "bare /daybooks is error shell; never Opret/Tilføj/Bogfør)"
        )
    else:
        row["method_or_route"] = (
            "mit.billy.dk /:org_slug/daybooks/new (read-only daybook editor shell open only; "
            "bare /daybooks is error shell)"
        )
    row["tool_name"] = UI_DAYBOOKS_OPEN_TOOL_NAME
    row["request_fields"] = []
    row["response_fields"] = [
        "path_class",
        "heading",
        "editor_markers_present",
        "shell_markers_present",
    ]
    row["filters"] = []
    row["pagination"] = None
    if not parity_of_api_list and not parity_of_api_create:
        row["api_row_id"] = None
    row["test_references"] = [
        TEST_REFERENCE,
        UI_DAYBOOKS_OPEN_MODEL_TEST_REFERENCE,
        UI_DAYBOOKS_OPEN_UNIT_TEST_REFERENCE,
        UI_DAYBOOKS_OPEN_LIVE_TEST_REFERENCE,
        SERVER_REGISTRY_TEST_REFERENCE,
    ]
    row["evidence"] = (
        "research117 dual-session headless observation + ui_daybooks_open product; "
        "shell open only (path class /:org_slug/daybooks/new; markers Opret ny "
        "kassekladde / Tilføj kassekladdelinje / Ingen postering valgt; empty h1 "
        "allowed; bare /daybooks dual Upsedasse rejected); never click create/"
        "add-line/post; no invent api_daybooks_* beyond offline product; does not "
        "green ui.discovery.transactions or daybooks get/update/delete/bulk "
        "UI parity or nested daybookTransactions*/lines/balanceAccounts; "
        "API list filters/sort/pagination UI not producted; vision record "
        "tmp/vision-records/ui_daybooks_open.json (editor frames, accept)"
    )
    if parity_of_api_list:
        row["evidence"] = (
            f"{row['evidence']}; research156 dual-session reconfirm; "
            "maps api.daybooks.list to UI daybook editor shell open only"
        )
    if parity_of_api_create:
        row["evidence"] = (
            f"{row['evidence']}; research157 dual-session reconfirm; "
            "maps api.daybooks.create to UI daybook create-form open only "
            "(form_open_only; never submits)"
        )
    row["discovered"] = True
    row["implemented"] = True
    row["contract_tested"] = True
    row["live_tested"] = True
    row["vision_verified"] = True
    row["vision_evidence"] = None
    if parity_of_api_create:
        row["parity_status"] = "form_open_only"
        row["sensitivity"] = "medium"
        row["side_effects"] = "none when open-only; product path never submits"
    else:
        row["parity_status"] = "shell_open_only"
        row["sensitivity"] = "low"
        row["side_effects"] = "none"
    row["cleanup"] = "not_applicable; read-only observation creates no records"
    row["errors"] = [
        "AUTH_REQUIRED",
        "AUTH_INTERACTION_REQUIRED",
        "UI_CHANGED",
        "EGRESS_DENIED",
        "BILLY_ERROR",
    ]


def apply_ui_daybooks_get_open_shell_evidence(
    row: dict[str, Any],
    *,
    parity_of_api_get: bool = False,
) -> None:
    """Mark daybooks **detail get open** evidence (research179).

    Empty-input tool; path /:org_slug/daybooks/:id; editor markers dual.
    Never create/add-line/post/delete. Distinct from list+create on /daybooks/new.
    When ``parity_of_api_get`` is true, dual-counts exact ``ui.parity.daybooks.get``.
    """

    row["method_or_route"] = (
        "mit.billy.dk /:org_slug/daybooks/:id (read-only daybook get/open; "
        "SPA list under committed egress; never Opret/Tilføj/Bogfør/Slet; "
        "bare /daybooks and /daybooks/new not success)"
    )
    row["tool_name"] = UI_DAYBOOKS_GET_OPEN_TOOL_NAME
    row["request_fields"] = []
    row["response_fields"] = [
        "path_class",
        "shell_kind",
        "detail_open",
        "editor_markers_present",
        "shell_markers_present",
    ]
    row["filters"] = []
    row["pagination"] = None
    if not parity_of_api_get:
        row["api_row_id"] = None
    row["test_references"] = [
        TEST_REFERENCE,
        UI_DAYBOOKS_GET_OPEN_MODEL_TEST_REFERENCE,
        UI_DAYBOOKS_GET_OPEN_UNIT_TEST_REFERENCE,
        UI_DAYBOOKS_GET_OPEN_LIVE_TEST_REFERENCE,
        SERVER_REGISTRY_TEST_REFERENCE,
    ]
    row["evidence"] = (
        "research179 dual-session headless observation + ui_daybooks_get_open product; "
        "scoped api.billysbilling.com path_allow for GET/POST/DELETE /v2/daybooks "
        "(GET list; POST/DELETE disposable seed/cleanup in live harness); "
        "detail open only (path class /:org_slug/daybooks/:id, shell_kind=daybooks_get, "
        "editor markers Opret ny kassekladde / Tilføj kassekladdelinje / Ingen postering valgt; "
        "never Opret/Tilføj/Bogfør/Slet; distinct from list+create ui_daybooks_open on "
        "/daybooks/new); vision record tmp/vision-records/ui_daybooks_get_open.json "
        "(daybook get frames, accept)"
    )
    if parity_of_api_get:
        row["evidence"] = f"{row['evidence']}; maps api.daybooks.get to UI detail get/open only"
    row["discovered"] = True
    row["implemented"] = True
    row["contract_tested"] = True
    row["live_tested"] = True
    row["vision_verified"] = True
    row["vision_evidence"] = None
    row["parity_status"] = "detail_open_only"
    row["sensitivity"] = "medium"
    row["side_effects"] = "none when open-only; product path never submits"
    row["cleanup"] = (
        "not_applicable for product path; live harness creates disposable daybook "
        "then deletes with fresh read-back"
    )
    row["errors"] = [
        "AUTH_REQUIRED",
        "AUTH_INTERACTION_REQUIRED",
        "UI_CHANGED",
        "EGRESS_DENIED",
        "BILLY_ERROR",
    ]


def apply_ui_daybooks_delete_open_shell_evidence(
    row: dict[str, Any],
    *,
    parity_of_api_delete: bool = False,
) -> None:
    """Mark daybooks **Mere delete chrome open only** evidence (research180).

    Empty-input tool; open /:org_slug/daybooks/:id, open Mere, classify Slet text
    in menu (export CSV/XLS/Importér + Slet). Never confirm Slet. Distinct from
    get open and list+create on /daybooks/new. When ``parity_of_api_delete`` is
    true, dual-counts exact ``ui.parity.daybooks.delete``.
    """

    row["method_or_route"] = (
        "mit.billy.dk /:org_slug/daybooks/:id + Mere menu "
        "(read-only daybooks delete chrome open; never confirm Slet; "
        "primary Slet button absent; /daybooks/new and bare /daybooks not success)"
    )
    row["tool_name"] = UI_DAYBOOKS_DELETE_OPEN_TOOL_NAME
    row["request_fields"] = []
    row["response_fields"] = [
        "path_class",
        "shell_kind",
        "detail_open",
        "mere_open",
        "slet_text_visible",
        "export_menu_visible",
        "primary_slet_absent",
        "shell_markers_present",
    ]
    row["filters"] = []
    row["pagination"] = None
    if not parity_of_api_delete:
        row["api_row_id"] = None
    row["test_references"] = [
        TEST_REFERENCE,
        UI_DAYBOOKS_DELETE_OPEN_MODEL_TEST_REFERENCE,
        UI_DAYBOOKS_DELETE_OPEN_UNIT_TEST_REFERENCE,
        UI_DAYBOOKS_DELETE_OPEN_LIVE_TEST_REFERENCE,
        SERVER_REGISTRY_TEST_REFERENCE,
    ]
    row["evidence"] = (
        "research180 dual-session headless observation + ui_daybooks_delete_open product; "
        "scoped api.billysbilling.com path_allow for GET/POST/DELETE /v2/daybooks "
        "(GET list; POST/DELETE disposable seed/cleanup in live harness); "
        "Mere delete chrome open only (path class /:org_slug/daybooks/:id, "
        "shell_kind=daybooks_delete, menu body Eksportér CSV/XLS/Importér/Slet dual; "
        "never confirm Slet; distinct from list+create ui_daybooks_open on /daybooks/new "
        "and get ui_daybooks_get_open); vision record "
        "tmp/vision-records/ui_daybooks_delete_open.json (daybook delete chrome frames, accept)"
    )
    if parity_of_api_delete:
        row["evidence"] = (
            f"{row['evidence']}; maps api.daybooks.delete to UI Mere delete chrome open only"
        )
    row["discovered"] = True
    row["implemented"] = True
    row["contract_tested"] = True
    row["live_tested"] = True
    row["vision_verified"] = True
    row["vision_evidence"] = None
    row["parity_status"] = "delete_chrome_open_only"
    row["sensitivity"] = "medium"
    row["side_effects"] = "none when open-only; product path never confirms delete"
    row["cleanup"] = (
        "not_applicable for product path; live harness creates disposable daybook "
        "then deletes with fresh read-back"
    )
    row["errors"] = [
        "AUTH_REQUIRED",
        "AUTH_INTERACTION_REQUIRED",
        "UI_CHANGED",
        "EGRESS_DENIED",
        "BILLY_ERROR",
    ]


def apply_ui_daybook_transactions_create_open_shell_evidence(
    row: dict[str, Any],
    *,
    parity_of_api_create: bool = False,
) -> None:
    """Mark daybookTransactions **create chrome open only** evidence (research181).

    Empty-input tool; open /:org_slug/daybooks/:id; classify Tilføj kassekladdelinje
    + Ingen postering valgt. Never click Tilføj/Bogfør/Slet confirm. Distinct from
    get open and Mere delete chrome. When ``parity_of_api_create`` is true, dual-counts
    exact ``ui.parity.daybookTransactions.create``.
    """

    row["method_or_route"] = (
        "mit.billy.dk /:org_slug/daybooks/:id "
        "(read-only daybookTransactions create chrome open; "
        "Tilføj kassekladdelinje + Ingen postering valgt; never add line/post/delete; "
        "/daybooks/new and bare /daybooks not success)"
    )
    row["tool_name"] = UI_DAYBOOK_TRANSACTIONS_CREATE_OPEN_TOOL_NAME
    row["request_fields"] = []
    row["response_fields"] = [
        "path_class",
        "shell_kind",
        "detail_open",
        "line_add_chrome_visible",
        "empty_postering_state",
        "shell_markers_present",
    ]
    row["filters"] = []
    row["pagination"] = None
    if not parity_of_api_create:
        row["api_row_id"] = None
    row["test_references"] = [
        TEST_REFERENCE,
        UI_DAYBOOK_TRANSACTIONS_CREATE_OPEN_MODEL_TEST_REFERENCE,
        UI_DAYBOOK_TRANSACTIONS_CREATE_OPEN_UNIT_TEST_REFERENCE,
        UI_DAYBOOK_TRANSACTIONS_CREATE_OPEN_LIVE_TEST_REFERENCE,
        SERVER_REGISTRY_TEST_REFERENCE,
    ]
    row["evidence"] = (
        "research181 dual-session headless observation + ui_daybook_transactions_create_open "
        "product; scoped api.billysbilling.com path_allow for GET/POST/DELETE /v2/daybooks "
        "(GET list; POST/DELETE disposable seed/cleanup in live harness); "
        "create chrome open only (path class /:org_slug/daybooks/:id, "
        "shell_kind=daybook_transactions_create, Tilføj kassekladdelinje + "
        "Ingen postering valgt dual; never click Tilføj/Bogfør; distinct from "
        "list+create ui_daybooks_open on /daybooks/new, get ui_daybooks_get_open, "
        "and delete ui_daybooks_delete_open Mere chrome); vision record "
        "tmp/vision-records/ui_daybook_transactions_create_open.json "
        "(daybook create chrome frames, accept)"
    )
    if parity_of_api_create:
        row["evidence"] = (
            f"{row['evidence']}; maps api.daybookTransactions.create to UI create chrome open only"
        )
    row["discovered"] = True
    row["implemented"] = True
    row["contract_tested"] = True
    row["live_tested"] = True
    row["vision_verified"] = True
    row["vision_evidence"] = None
    row["parity_status"] = "create_chrome_open_only"
    row["sensitivity"] = "medium"
    row["side_effects"] = "none when open-only; product path never adds lines or posts"
    row["cleanup"] = (
        "not_applicable for product path; live harness creates disposable daybook "
        "then deletes with fresh read-back"
    )
    row["errors"] = [
        "AUTH_REQUIRED",
        "AUTH_INTERACTION_REQUIRED",
        "UI_CHANGED",
        "EGRESS_DENIED",
        "BILLY_ERROR",
    ]


def apply_ui_transactions_create_open_shell_evidence(
    row: dict[str, Any],
    *,
    parity_of_api_create: bool = False,
) -> None:
    """Mark transactions **create chrome open only** evidence (research182).

    Empty-input tool; open /:org_slug/transactions; classify Posteringer + Ny postering.
    Never click Gem/Bogfør/Opret submit/void/Slet. Soft /transactions/new title shell
    is not success alone. When ``parity_of_api_create`` is true, dual-counts exact
    ``ui.parity.transactions.create``.
    """

    row["method_or_route"] = (
        "mit.billy.dk /:org_slug/transactions "
        "(read-only transactions create chrome open; "
        "Posteringer + Ny postering; never submit/post/void/delete; "
        "soft /transactions/new title shell not success alone)"
    )
    row["tool_name"] = UI_TRANSACTIONS_CREATE_OPEN_TOOL_NAME
    row["request_fields"] = []
    row["response_fields"] = [
        "path_class",
        "shell_kind",
        "list_open",
        "create_cta_visible",
        "shell_markers_present",
    ]
    row["filters"] = []
    row["pagination"] = None
    if not parity_of_api_create:
        row["api_row_id"] = None
    row["test_references"] = [
        TEST_REFERENCE,
        UI_TRANSACTIONS_CREATE_OPEN_MODEL_TEST_REFERENCE,
        UI_TRANSACTIONS_CREATE_OPEN_UNIT_TEST_REFERENCE,
        UI_TRANSACTIONS_CREATE_OPEN_LIVE_TEST_REFERENCE,
        SERVER_REGISTRY_TEST_REFERENCE,
    ]
    row["evidence"] = (
        "research182 dual-session headless observation + ui_transactions_create_open "
        "product; open /:org_slug/transactions create chrome open only "
        "(shell_kind=transactions_create, Posteringer + Ny postering dual; never "
        "Gem/Bogfør/Opret submit; soft /transactions/new title shell inputs_n 0 dual "
        "not form_open_only; distinct from ui_transactions_list list mapping and "
        "already-NA get/update/delete; no dual-count onto postings.*); vision record "
        "tmp/vision-records/ui_transactions_create_open.json "
        "(transactions create chrome frames, accept)"
    )
    if parity_of_api_create:
        row["evidence"] = (
            f"{row['evidence']}; maps api.transactions.create to UI create chrome open only"
        )
    row["discovered"] = True
    row["implemented"] = True
    row["contract_tested"] = True
    row["live_tested"] = True
    row["vision_verified"] = True
    row["vision_evidence"] = None
    row["parity_status"] = "create_chrome_open_only"
    row["sensitivity"] = "medium"
    row["side_effects"] = "none when open-only; product path never posts or voids transactions"
    row["cleanup"] = "not_applicable for product path; no disposable transaction seed required"
    row["errors"] = [
        "AUTH_REQUIRED",
        "AUTH_INTERACTION_REQUIRED",
        "UI_CHANGED",
        "EGRESS_DENIED",
        "BILLY_ERROR",
    ]


def apply_ui_transactions_list_shell_evidence(
    row: dict[str, Any],
    *,
    parity_of_api_list: bool = False,
) -> None:
    """Mark transactions (Posteringer) list **shell open** evidence only (research118).

    Empty-input tool; path /:org_slug/transactions (query allowed); h1 Posteringer;
    CTA Ny postering observe-only. Nested /transactions/:segment is create shell
    (not list success). No invent API write tools. Does not green daybooks or
    transaction create/update/delete/bulk. When ``parity_of_api_list`` is true,
    dual-counts ``ui.parity.transactions.list`` for ``api.transactions.list``.
    """

    row["method_or_route"] = (
        "mit.billy.dk /:org_slug/transactions (read-only Posteringer list shell open only; "
        "nested /transactions/:segment is create shell)"
    )
    row["tool_name"] = UI_TRANSACTIONS_LIST_TOOL_NAME
    row["request_fields"] = []
    row["response_fields"] = [
        "path_class",
        "heading",
        "create_action_visible",
        "shell_markers_present",
    ]
    row["filters"] = []
    row["pagination"] = None
    if not parity_of_api_list:
        row["api_row_id"] = None
    row["test_references"] = [
        TEST_REFERENCE,
        UI_TRANSACTIONS_LIST_MODEL_TEST_REFERENCE,
        UI_TRANSACTIONS_LIST_UNIT_TEST_REFERENCE,
        UI_TRANSACTIONS_LIST_LIVE_TEST_REFERENCE,
        SERVER_REGISTRY_TEST_REFERENCE,
    ]
    row["evidence"] = (
        "research118 dual-session headless observation + ui_transactions_list product; "
        "list shell only (path class /:org_slug/transactions, h1 Posteringer, CTA "
        "Ny postering present, no create); nested /transactions/:segment create shell "
        "rejected; soft aliases empty; no invent api_transactions write tools; does not "
        "green daybooks or transaction create/update/delete/bulk; "
        "API list filters/sort/pagination UI not producted; "
        "vision record tmp/vision-records/ui_transactions_list.json (list surface frames, accept)"
    )
    if parity_of_api_list:
        row["evidence"] = (
            f"{row['evidence']}; maps api.transactions.list to UI list-shell open only"
        )
    row["discovered"] = True
    row["implemented"] = True
    row["contract_tested"] = True
    row["live_tested"] = True
    row["vision_verified"] = True
    row["vision_evidence"] = None
    row["parity_status"] = "list_shell_open_only"
    row["sensitivity"] = "low"
    row["side_effects"] = "none"
    row["cleanup"] = "not_applicable; read-only observation creates no records"
    row["errors"] = [
        "AUTH_REQUIRED",
        "AUTH_INTERACTION_REQUIRED",
        "UI_CHANGED",
        "EGRESS_DENIED",
        "BILLY_ERROR",
    ]


def apply_ui_reports_open_shell_evidence(row: dict[str, Any]) -> None:
    """Mark reports (Rapporter) hub **shell open** evidence only (research119).

    Empty-input tool; path /:org_slug/reports-all (+ optional tab
    profit-and-loss|balance|trial-balance); h1 Rapporter; Eksport observe-only.
    Bare /reports is soft empty chrome (not success). No invent api_reports_*.
    Does not green vat/annual/exports discovery rows.
    """

    row["method_or_route"] = (
        "mit.billy.dk /:org_slug/reports-all (read-only Rapporter hub shell open only; "
        "optional tab profit-and-loss|balance|trial-balance; bare /reports rejected)"
    )
    row["tool_name"] = UI_REPORTS_OPEN_TOOL_NAME
    row["request_fields"] = []
    row["response_fields"] = [
        "path_class",
        "heading",
        "export_action_visible",
        "shell_markers_present",
    ]
    row["filters"] = []
    row["pagination"] = None
    row["api_row_id"] = None
    row["test_references"] = [
        TEST_REFERENCE,
        UI_REPORTS_OPEN_MODEL_TEST_REFERENCE,
        UI_REPORTS_OPEN_UNIT_TEST_REFERENCE,
        UI_REPORTS_OPEN_LIVE_TEST_REFERENCE,
        SERVER_REGISTRY_TEST_REFERENCE,
    ]
    row["evidence"] = (
        "research119 dual-session headless observation + ui_reports_open product; "
        "shell open only (path class /:org_slug/reports-all with optional tab, h1 "
        "Rapporter, tabs Resultatopgørelse/Balance/Saldobalance, Eksport observe-only); "
        "bare /reports soft empty rejected; no invent api_reports_*; does not green "
        "vat_declarations/annual_reports/exports; vision record "
        "tmp/vision-records/ui_reports_open.json (hub frames, accept)"
    )
    row["discovered"] = True
    row["implemented"] = True
    row["contract_tested"] = True
    row["live_tested"] = True
    row["vision_verified"] = True
    row["vision_evidence"] = None
    row["parity_status"] = "shell_open_only"
    row["sensitivity"] = "low"
    row["side_effects"] = "none"
    row["cleanup"] = "not_applicable; read-only observation creates no records"
    row["errors"] = [
        "AUTH_REQUIRED",
        "AUTH_INTERACTION_REQUIRED",
        "UI_CHANGED",
        "EGRESS_DENIED",
        "BILLY_ERROR",
    ]


def apply_ui_vat_declarations_list_shell_evidence(
    row: dict[str, Any],
    *,
    parity_of_api_list: bool = False,
) -> None:
    """Mark VAT declarations (Momsangivelser) list **shell open** evidence only (research120).

    Empty-input tool; path /:org_slug/vat-declarations; h1 Momsangivelser; Periode
    chrome; empty table body valid. Soft aliases rejected. No invent api_vat_*.
    Does not green annual/exports/settings discovery rows or salesTaxReturns
    get/update/bulk UI parity. When ``parity_of_api_list`` is true, dual-counts
    ``ui.parity.salesTaxReturns.list`` for ``api.salesTaxReturns.list`` (research140).
    """

    row["method_or_route"] = (
        "mit.billy.dk /:org_slug/vat-declarations (read-only Momsangivelser list shell "
        "open only; soft aliases rejected; empty list valid)"
    )
    row["tool_name"] = UI_VAT_DECLARATIONS_LIST_TOOL_NAME
    row["request_fields"] = []
    row["response_fields"] = [
        "path_class",
        "heading",
        "period_column_visible",
        "shell_markers_present",
    ]
    row["filters"] = []
    row["pagination"] = None
    if not parity_of_api_list:
        row["api_row_id"] = None
    row["test_references"] = [
        TEST_REFERENCE,
        UI_VAT_DECLARATIONS_LIST_MODEL_TEST_REFERENCE,
        UI_VAT_DECLARATIONS_LIST_UNIT_TEST_REFERENCE,
        UI_VAT_DECLARATIONS_LIST_LIVE_TEST_REFERENCE,
        SERVER_REGISTRY_TEST_REFERENCE,
    ]
    row["evidence"] = (
        "research120 dual-session headless observation + ui_vat_declarations_list product; "
        "list shell only (path class /:org_slug/vat-declarations, h1 Momsangivelser, "
        "Periode chrome, empty list valid); soft aliases rejected; no invent api_vat_*; "
        "does not green annual_reports/exports/settings or salesTaxReturns "
        "get/update/bulk UI parity; "
        "API list filters/sort/pagination UI not producted; "
        "vision record tmp/vision-records/ui_vat_declarations_list.json (list frames, accept)"
    )
    if parity_of_api_list:
        row["evidence"] = (
            f"{row['evidence']}; research140 dual-session reconfirm; "
            "maps api.salesTaxReturns.list to UI list-shell open only"
        )
    row["discovered"] = True
    row["implemented"] = True
    row["contract_tested"] = True
    row["live_tested"] = True
    row["vision_verified"] = True
    row["vision_evidence"] = None
    row["parity_status"] = "list_shell_open_only"
    row["sensitivity"] = "low"
    row["side_effects"] = "none"
    row["cleanup"] = "not_applicable; read-only observation creates no records"
    row["errors"] = [
        "AUTH_REQUIRED",
        "AUTH_INTERACTION_REQUIRED",
        "UI_CHANGED",
        "EGRESS_DENIED",
        "BILLY_ERROR",
    ]


def apply_ui_exports_open_shell_evidence(row: dict[str, Any]) -> None:
    """Mark exports (Eksportér data) hub **shell open** evidence only (research121).

    Empty-input tool; path /:org_slug/exports; h1 Eksportér data; export/SAF-T
    CTAs observe-only (never click). Soft aliases rejected. No invent api_exports_*.
    Does not green annual_reports/saft_exports/settings discovery rows.
    """

    row["method_or_route"] = (
        "mit.billy.dk /:org_slug/exports (read-only Eksportér data hub shell open only; "
        "export/SAF-T CTAs observe-only)"
    )
    row["tool_name"] = UI_EXPORTS_OPEN_TOOL_NAME
    row["request_fields"] = []
    row["response_fields"] = [
        "path_class",
        "heading",
        "saft_export_cta_observed",
        "shell_markers_present",
    ]
    row["filters"] = []
    row["pagination"] = None
    row["api_row_id"] = None
    row["test_references"] = [
        TEST_REFERENCE,
        UI_EXPORTS_OPEN_MODEL_TEST_REFERENCE,
        UI_EXPORTS_OPEN_UNIT_TEST_REFERENCE,
        UI_EXPORTS_OPEN_LIVE_TEST_REFERENCE,
        SERVER_REGISTRY_TEST_REFERENCE,
    ]
    row["evidence"] = (
        "research121 dual-session headless observation + ui_exports_open product; "
        "shell open only (path class /:org_slug/exports, h1 Eksportér data, export "
        "chrome, SAF-T CTA observe-only); soft aliases rejected; no invent api_exports_*; "
        "does not green annual_reports/saft_exports/settings; vision record "
        "tmp/vision-records/ui_exports_open.json (hub frames, accept)"
    )
    row["discovered"] = True
    row["implemented"] = True
    row["contract_tested"] = True
    row["live_tested"] = True
    row["vision_verified"] = True
    row["vision_evidence"] = None
    row["parity_status"] = "shell_open_only"
    row["sensitivity"] = "low"
    row["side_effects"] = "none"
    row["cleanup"] = "not_applicable; read-only observation creates no records"
    row["errors"] = [
        "AUTH_REQUIRED",
        "AUTH_INTERACTION_REQUIRED",
        "UI_CHANGED",
        "EGRESS_DENIED",
        "BILLY_ERROR",
    ]


def apply_ui_saft_exports_open_shell_evidence(row: dict[str, Any]) -> None:
    """Mark SAF-T observe-only shell evidence on exports hub (research122).

    Empty-input tool; path /:org_slug/exports; h1 Eksportér data; requires
    Eksportér som SAF-T CTA present (never click). Soft saft* aliases rejected.
    No invent api_saft_*/api_exports_*. Does not re-green exports or annual_reports.
    """

    row["method_or_route"] = (
        "mit.billy.dk /:org_slug/exports (read-only SAF-T CTA observe on Eksportér "
        "data hub; never click Eksportér som SAF-T / Eksport / Download)"
    )
    row["tool_name"] = UI_SAFT_EXPORTS_OPEN_TOOL_NAME
    row["request_fields"] = []
    row["response_fields"] = [
        "path_class",
        "heading",
        "saft_export_cta_observed",
        "shell_markers_present",
    ]
    row["filters"] = []
    row["pagination"] = None
    row["api_row_id"] = None
    row["test_references"] = [
        TEST_REFERENCE,
        UI_SAFT_EXPORTS_OPEN_MODEL_TEST_REFERENCE,
        UI_SAFT_EXPORTS_OPEN_UNIT_TEST_REFERENCE,
        UI_SAFT_EXPORTS_OPEN_LIVE_TEST_REFERENCE,
        SERVER_REGISTRY_TEST_REFERENCE,
    ]
    row["evidence"] = (
        "research122 dual-session headless observation + ui_saft_exports_open product; "
        "shell open only (path class /:org_slug/exports, h1 Eksportér data, required "
        "SAF-T CTA Eksportér som SAF-T observe-only); soft saft* rejected; no invent "
        "api_saft_*/api_exports_*; does not re-green exports/annual_reports/settings; "
        "vision record tmp/vision-records/ui_saft_exports_open.json (hub frames, accept)"
    )
    row["discovered"] = True
    row["implemented"] = True
    row["contract_tested"] = True
    row["live_tested"] = True
    row["vision_verified"] = True
    row["vision_evidence"] = None
    row["parity_status"] = "shell_open_only"
    row["sensitivity"] = "low"
    row["side_effects"] = "none"
    row["cleanup"] = "not_applicable; read-only observation creates no records"
    row["errors"] = [
        "AUTH_REQUIRED",
        "AUTH_INTERACTION_REQUIRED",
        "UI_CHANGED",
        "EGRESS_DENIED",
        "BILLY_ERROR",
    ]


def apply_ui_addons_open_shell_evidence(row: dict[str, Any]) -> None:
    """Mark Fordele (add-ons) shell open evidence (research123).

    Empty-input tool; path /:org_slug/add-ons; h1 Fordele. Soft aliases
    (addons, integrations, nested, settings/*) rejected. Never partner CTAs.
    No invent api_addons_*/api_integrations_*. Does not green integrations,
    inventory, settings_*, or annual_reports.
    """

    row["method_or_route"] = (
        "mit.billy.dk /:org_slug/add-ons (read-only Fordele hub shell open only; "
        "never click partner install/connect/access-token/loan CTAs)"
    )
    row["tool_name"] = UI_ADDONS_OPEN_TOOL_NAME
    row["request_fields"] = []
    row["response_fields"] = [
        "path_class",
        "heading",
        "shell_markers_present",
    ]
    row["filters"] = []
    row["pagination"] = None
    row["api_row_id"] = None
    row["test_references"] = [
        TEST_REFERENCE,
        UI_ADDONS_OPEN_MODEL_TEST_REFERENCE,
        UI_ADDONS_OPEN_UNIT_TEST_REFERENCE,
        UI_ADDONS_OPEN_LIVE_TEST_REFERENCE,
        SERVER_REGISTRY_TEST_REFERENCE,
    ]
    row["evidence"] = (
        "research123 dual-session headless observation + ui_addons_open product; "
        "shell open only (path class /:org_slug/add-ons, h1 Fordele); soft aliases "
        "rejected; no invent api_addons_*/api_integrations_*; does not green "
        "integrations/inventory/settings/annual_reports; vision record "
        "tmp/vision-records/ui_addons_open.json (hub frames, accept)"
    )
    row["discovered"] = True
    row["implemented"] = True
    row["contract_tested"] = True
    row["live_tested"] = True
    row["vision_verified"] = True
    row["vision_evidence"] = None
    row["parity_status"] = "shell_open_only"
    row["sensitivity"] = "low"
    row["side_effects"] = "none"
    row["cleanup"] = "not_applicable; read-only observation creates no records"
    row["errors"] = [
        "AUTH_REQUIRED",
        "AUTH_INTERACTION_REQUIRED",
        "UI_CHANGED",
        "EGRESS_DENIED",
        "BILLY_ERROR",
    ]


def apply_ui_integrations_open_shell_evidence(row: dict[str, Any]) -> None:
    """Mark integrations soft-empty classification evidence (research124).

    Empty-input tool; path /:org_slug/integrations; empty h1 soft-empty chrome.
    Not Fordele/add-ons. Soft aliases rejected. Never navigate www.billy.dk or
    partner CTAs. No invent api_integrations_*. Does not green addons,
    inventory, settings_*, or annual_reports.
    """

    row["method_or_route"] = (
        "mit.billy.dk /:org_slug/integrations (read-only soft-empty shell "
        "classification only; never navigate www.billy.dk; never partner CTAs)"
    )
    row["tool_name"] = UI_INTEGRATIONS_OPEN_TOOL_NAME
    row["request_fields"] = []
    row["response_fields"] = [
        "path_class",
        "shell_kind",
        "dedicated_shell",
        "same_shell_as_addons",
        "heading",
        "shell_markers_present",
    ]
    row["filters"] = []
    row["pagination"] = None
    row["api_row_id"] = None
    row["test_references"] = [
        TEST_REFERENCE,
        UI_INTEGRATIONS_OPEN_MODEL_TEST_REFERENCE,
        UI_INTEGRATIONS_OPEN_UNIT_TEST_REFERENCE,
        UI_INTEGRATIONS_OPEN_LIVE_TEST_REFERENCE,
        SERVER_REGISTRY_TEST_REFERENCE,
    ]
    row["evidence"] = (
        "research124 dual-session headless observation + ui_integrations_open product; "
        "soft_empty_shell_observed (path class /:org_slug/integrations, empty h1, "
        "dedicated_shell=false, same_shell_as_addons=false); soft aliases rejected; "
        "Fordele not success; no invent api_integrations_*; does not green "
        "addons/inventory/settings/annual_reports; vision record "
        "tmp/vision-records/ui_integrations_open.json (soft-empty chrome, accept)"
    )
    row["discovered"] = True
    row["implemented"] = True
    row["contract_tested"] = True
    row["live_tested"] = True
    row["vision_verified"] = True
    row["vision_evidence"] = None
    row["parity_status"] = "soft_empty_shell_observed"
    row["sensitivity"] = "low"
    row["side_effects"] = "none"
    row["cleanup"] = "not_applicable; read-only observation creates no records"
    row["errors"] = [
        "AUTH_REQUIRED",
        "AUTH_INTERACTION_REQUIRED",
        "UI_CHANGED",
        "EGRESS_DENIED",
        "BILLY_ERROR",
    ]


def apply_ui_inventory_open_shell_evidence(row: dict[str, Any]) -> None:
    """Mark Lagermodul inventory shell open evidence (research125).

    Empty-input tool; path /:org_slug/inventory; h1 Lagermodul. Soft aliases
    (lager, stock, warehouse, nested inventory/*, settings/inventory) rejected.
    Never click Opret primo / Opret produkt / Opret status. No invent
    api_inventory_*. Distinct from products list. Does not green settings_*,
    annual_reports, products, addons, or integrations.
    """

    row["method_or_route"] = (
        "mit.billy.dk /:org_slug/inventory (read-only Lagermodul shell open only; "
        "never click Opret primo/produkt/status create CTAs)"
    )
    row["tool_name"] = UI_INVENTORY_OPEN_TOOL_NAME
    row["request_fields"] = []
    row["response_fields"] = [
        "path_class",
        "heading",
        "shell_kind",
        "create_cta_markers_present",
    ]
    row["filters"] = []
    row["pagination"] = None
    row["api_row_id"] = None
    row["test_references"] = [
        TEST_REFERENCE,
        UI_INVENTORY_OPEN_MODEL_TEST_REFERENCE,
        UI_INVENTORY_OPEN_UNIT_TEST_REFERENCE,
        UI_INVENTORY_OPEN_LIVE_TEST_REFERENCE,
        SERVER_REGISTRY_TEST_REFERENCE,
    ]
    row["evidence"] = (
        "research125 dual-session headless observation + ui_inventory_open product; "
        "shell open only (path class /:org_slug/inventory, h1 Lagermodul, "
        "shell_kind=lagermodul); soft aliases rejected; products list not success; "
        "no invent api_inventory_*; never click Opret CTAs; does not green "
        "settings/annual/products re-green; vision record "
        "tmp/vision-records/ui_inventory_open.json (Lagermodul frames, accept)"
    )
    row["discovered"] = True
    row["implemented"] = True
    row["contract_tested"] = True
    row["live_tested"] = True
    row["vision_verified"] = True
    row["vision_evidence"] = None
    row["parity_status"] = "shell_open_only"
    row["sensitivity"] = "low"
    row["side_effects"] = "none"
    row["cleanup"] = "not_applicable; read-only observation creates no records"
    row["errors"] = [
        "AUTH_REQUIRED",
        "AUTH_INTERACTION_REQUIRED",
        "UI_CHANGED",
        "EGRESS_DENIED",
        "BILLY_ERROR",
    ]


def apply_ui_settings_company_open_shell_evidence(
    row: dict[str, Any],
    *,
    parity_of_api_list: bool = False,
    parity_of_api_get: bool = False,
    parity_of_api_update: bool = False,
) -> None:
    """Mark Indstillinger company settings shell open evidence (research126).

    Empty-input tool; path /:org_slug/settings; h1 Indstillinger; company panel
    markers Navn og adresse + Kontaktinformation. Soft nested aliases rejected.
    Never click Gem / Tilføj ejer / upload. No invent api_settings_*. Does not
    green other settings_* or annual_reports or organizations create/bulk UI
    parity. When ``parity_of_api_list`` is true, dual-counts
    ``ui.parity.organizations.list`` for ``api.organizations.list`` (research146).
    When ``parity_of_api_get`` is true, dual-counts ``ui.parity.organizations.get``
    (research177, detail_open_only). When ``parity_of_api_update`` is true,
    dual-counts ``ui.parity.organizations.update`` (research177, form_open_only).
    Flags are mutually exclusive per call.
    """

    flag_count = sum(
        1 for flag in (parity_of_api_list, parity_of_api_get, parity_of_api_update) if flag
    )
    if flag_count > 1:
        raise ValueError("organizations dual-count flags are mutually exclusive")

    if parity_of_api_get:
        row["method_or_route"] = (
            "mit.billy.dk /:org_slug/settings (read-only Indstillinger company/"
            "Virksomhed identity form open only; Navn/CVR/Adresse family; never "
            "click Gem/Tilføj ejer/upload)"
        )
    elif parity_of_api_update:
        row["method_or_route"] = (
            "mit.billy.dk /:org_slug/settings (read-only Indstillinger company/"
            "Virksomhed update form open only; Gem ændringer present; never click "
            "Gem/Tilføj ejer/upload)"
        )
    else:
        row["method_or_route"] = (
            "mit.billy.dk /:org_slug/settings (read-only Indstillinger company/"
            "Virksomhed panel open only; never click Gem/Tilføj ejer/upload)"
        )
    row["tool_name"] = UI_SETTINGS_COMPANY_OPEN_TOOL_NAME
    row["request_fields"] = []
    row["response_fields"] = [
        "path_class",
        "heading",
        "shell_kind",
        "company_panel_markers_present",
    ]
    row["filters"] = []
    row["pagination"] = None
    if not parity_of_api_list and not parity_of_api_get and not parity_of_api_update:
        row["api_row_id"] = None
    row["test_references"] = [
        TEST_REFERENCE,
        UI_SETTINGS_COMPANY_OPEN_MODEL_TEST_REFERENCE,
        UI_SETTINGS_COMPANY_OPEN_UNIT_TEST_REFERENCE,
        UI_SETTINGS_COMPANY_OPEN_LIVE_TEST_REFERENCE,
        SERVER_REGISTRY_TEST_REFERENCE,
    ]
    row["evidence"] = (
        "research126 dual-session headless observation + ui_settings_company_open "
        "product; shell open only (path class /:org_slug/settings, h1 Indstillinger, "
        "shell_kind=settings_company, company panel markers); soft aliases rejected; "
        "no invent api_settings_*; never click Gem/Tilføj ejer; does not green other "
        "settings_* or annual_reports or organizations create/bulk UI parity; "
        "API list filters/sort/pagination UI not producted; "
        "vision record tmp/vision-records/ui_settings_company_open.json "
        "(Indstillinger company frames, accept)"
    )
    if parity_of_api_list:
        row["evidence"] = (
            f"{row['evidence']}; research146 dual-session reconfirm; "
            "maps api.organizations.list to UI settings company/Virksomhed shell open only"
        )
    if parity_of_api_get:
        row["evidence"] = (
            f"{row['evidence']}; research177 dual-session reconfirm; "
            "maps api.organizations.get to UI settings company identity form open only "
            "(detail_open_only; Navn/CVR/Adresse family dual; never Gem)"
        )
    if parity_of_api_update:
        row["evidence"] = (
            f"{row['evidence']}; research177 dual-session reconfirm; "
            "maps api.organizations.update to UI settings company update form open only "
            "(form_open_only; Gem ændringer dual present; never submits)"
        )
    row["discovered"] = True
    row["implemented"] = True
    row["contract_tested"] = True
    row["live_tested"] = True
    row["vision_verified"] = True
    row["vision_evidence"] = None
    if parity_of_api_get:
        row["parity_status"] = "detail_open_only"
        row["sensitivity"] = "low"
        row["side_effects"] = "none"
    elif parity_of_api_update:
        row["parity_status"] = "form_open_only"
        row["sensitivity"] = "medium"
        row["side_effects"] = "none when open-only; product path never submits"
    else:
        row["parity_status"] = "shell_open_only"
        row["sensitivity"] = "low"
        row["side_effects"] = "none"
    row["cleanup"] = "not_applicable; read-only observation creates no records"
    row["errors"] = [
        "AUTH_REQUIRED",
        "AUTH_INTERACTION_REQUIRED",
        "UI_CHANGED",
        "EGRESS_DENIED",
        "BILLY_ERROR",
    ]


def apply_ui_settings_accounting_open_shell_evidence(
    row: dict[str, Any],
    *,
    parity_of_api_list: bool = False,
) -> None:
    """Mark Indstillinger Regnskab (accounting) panel shell open evidence (research127).

    Empty-input tool; request settings/accounting SPA seed; final path
    /:org_slug/settings; h1 Indstillinger; markers Regnskab + Køb + Kontoplan.
    Distinct from company default. Soft aliases rejected. Never click Gem /
    Sæt låsedato. No invent api_settings_*. Does not green other settings_* or
    annual_reports or accounts get/create/update/delete/bulk UI parity. When
    ``parity_of_api_list`` is true, dual-counts ``ui.parity.accounts.list`` for
    ``api.accounts.list`` (research145).
    """

    row["method_or_route"] = (
        "mit.billy.dk /:org_slug/settings (read-only Indstillinger Regnskab/"
        "accounting panel open via settings/accounting SPA seed; never click "
        "Gem/Sæt låsedato/Opret*)"
    )
    row["tool_name"] = UI_SETTINGS_ACCOUNTING_OPEN_TOOL_NAME
    row["request_fields"] = []
    row["response_fields"] = [
        "path_class",
        "heading",
        "shell_kind",
        "accounting_panel_markers_present",
    ]
    row["filters"] = []
    row["pagination"] = None
    if not parity_of_api_list:
        row["api_row_id"] = None
    row["test_references"] = [
        TEST_REFERENCE,
        UI_SETTINGS_ACCOUNTING_OPEN_MODEL_TEST_REFERENCE,
        UI_SETTINGS_ACCOUNTING_OPEN_UNIT_TEST_REFERENCE,
        UI_SETTINGS_ACCOUNTING_OPEN_LIVE_TEST_REFERENCE,
        SERVER_REGISTRY_TEST_REFERENCE,
    ]
    row["evidence"] = (
        "research127 dual-session headless observation + ui_settings_accounting_open "
        "product; shell open only (seed settings/accounting → path class "
        "/:org_slug/settings, h1 Indstillinger, shell_kind=settings_accounting, "
        "Regnskab/Køb/Kontoplan markers; distinct from company); soft aliases rejected; "
        "no invent api_settings_*; never click Gem/Sæt låsedato; does not green other "
        "settings_* or annual_reports or accounts get/create/update/delete/bulk UI "
        "parity; API list filters/sort/pagination UI not producted; "
        "vision record tmp/vision-records/ui_settings_accounting_open.json "
        "(Indstillinger Regnskab frames, accept)"
    )
    if parity_of_api_list:
        row["evidence"] = (
            f"{row['evidence']}; research145 dual-session reconfirm; "
            "maps api.accounts.list to UI settings Regnskab/Kontoplan shell open only"
        )
    row["discovered"] = True
    row["implemented"] = True
    row["contract_tested"] = True
    row["live_tested"] = True
    row["vision_verified"] = True
    row["vision_evidence"] = None
    row["parity_status"] = "shell_open_only"
    row["sensitivity"] = "low"
    row["side_effects"] = "none"
    row["cleanup"] = "not_applicable; read-only observation creates no records"
    row["errors"] = [
        "AUTH_REQUIRED",
        "AUTH_INTERACTION_REQUIRED",
        "UI_CHANGED",
        "EGRESS_DENIED",
        "BILLY_ERROR",
    ]


def apply_ui_settings_invoicing_open_shell_evidence(row: dict[str, Any]) -> None:
    """Mark Indstillinger Faktura (invoicing) panel shell open evidence (research128).

    Empty-input tool; request settings/invoicing SPA seed; final path
    /:org_slug/settings; h1 Indstillinger; markers Faktura + Produkter +
    (Betalingsmetoder or Standard fakturalogo). Distinct from company default
    and accounting Regnskab. Soft aliases rejected. Never click Gem / Opret
    betalingsmetode / Upload. No invent api_settings_*. Does not green other
    settings_* or annual_reports.
    """

    row["method_or_route"] = (
        "mit.billy.dk /:org_slug/settings (read-only Indstillinger Faktura/"
        "invoicing panel open via settings/invoicing SPA seed; never click "
        "Gem/Opret betalingsmetode/Upload/Opret*)"
    )
    row["tool_name"] = UI_SETTINGS_INVOICING_OPEN_TOOL_NAME
    row["request_fields"] = []
    row["response_fields"] = [
        "path_class",
        "heading",
        "shell_kind",
        "invoicing_panel_markers_present",
    ]
    row["filters"] = []
    row["pagination"] = None
    row["api_row_id"] = None
    row["test_references"] = [
        TEST_REFERENCE,
        UI_SETTINGS_INVOICING_OPEN_MODEL_TEST_REFERENCE,
        UI_SETTINGS_INVOICING_OPEN_UNIT_TEST_REFERENCE,
        UI_SETTINGS_INVOICING_OPEN_LIVE_TEST_REFERENCE,
        SERVER_REGISTRY_TEST_REFERENCE,
    ]
    row["evidence"] = (
        "research128 dual-session headless observation + ui_settings_invoicing_open "
        "product; shell open only (seed settings/invoicing → path class "
        "/:org_slug/settings, h1 Indstillinger, shell_kind=settings_invoicing, "
        "Faktura/Produkter/Betalingsmetoder markers; distinct from company and "
        "accounting); soft aliases rejected; no invent api_settings_*; never click "
        "Gem/Opret betalingsmetode/Upload; does not green other settings_* or "
        "annual_reports; vision record "
        "tmp/vision-records/ui_settings_invoicing_open.json "
        "(Indstillinger Faktura frames, accept)"
    )
    row["discovered"] = True
    row["implemented"] = True
    row["contract_tested"] = True
    row["live_tested"] = True
    row["vision_verified"] = True
    row["vision_evidence"] = None
    row["parity_status"] = "shell_open_only"
    row["sensitivity"] = "low"
    row["side_effects"] = "none"
    row["cleanup"] = "not_applicable; read-only observation creates no records"
    row["errors"] = [
        "AUTH_REQUIRED",
        "AUTH_INTERACTION_REQUIRED",
        "UI_CHANGED",
        "EGRESS_DENIED",
        "BILLY_ERROR",
    ]


def apply_ui_settings_user_open_shell_evidence(
    row: dict[str, Any],
    *,
    parity_of_special_user_get: bool = False,
) -> None:
    """Mark Indstillinger Profil (user) panel shell open evidence (research129).

    Empty-input tool; open hub /:org_slug/settings then observe-only click
    Profil; final path /:org_slug/settings; h1 Indstillinger; markers Profil +
    Billede + Sprog og tema + Skift adgangskode. Soft seeds rejected. Distinct
    from company/accounting/invoicing. Never click Gem / Upload / password
    submit. No invent api_settings_*. Does not green other settings_* or
    annual_reports or special.user_organizations / users get/update/bulk UI
    parity. When ``parity_of_special_user_get`` is true, dual-counts
    ``ui.parity.special.user_get`` for ``api.special.user_get`` (research151).
    """

    row["method_or_route"] = (
        "mit.billy.dk /:org_slug/settings (read-only Indstillinger Profil/user "
        "panel open via hub + side-nav click Profil; never click "
        "Gem/Upload/password submit/Opret*)"
    )
    row["tool_name"] = UI_SETTINGS_USER_OPEN_TOOL_NAME
    row["request_fields"] = []
    row["response_fields"] = [
        "path_class",
        "heading",
        "shell_kind",
        "user_panel_markers_present",
    ]
    row["filters"] = []
    row["pagination"] = None
    if not parity_of_special_user_get:
        row["api_row_id"] = None
    row["test_references"] = [
        TEST_REFERENCE,
        UI_SETTINGS_USER_OPEN_MODEL_TEST_REFERENCE,
        UI_SETTINGS_USER_OPEN_UNIT_TEST_REFERENCE,
        UI_SETTINGS_USER_OPEN_LIVE_TEST_REFERENCE,
        SERVER_REGISTRY_TEST_REFERENCE,
    ]
    row["evidence"] = (
        "research129 dual-session headless observation + ui_settings_user_open "
        "product; shell open only (hub /:org_slug/settings + click Profil → path "
        "class /:org_slug/settings, h1 Indstillinger, shell_kind=settings_user, "
        "Profil/Billede/Sprog og tema/Skift adgangskode markers; distinct from "
        "company/accounting/invoicing); soft seeds rejected; no invent "
        "api_settings_*; never click Gem/Upload/password submit; does not green "
        "other settings_* or annual_reports or special.user_organizations or "
        "users get/update/bulk UI parity; vision record "
        "tmp/vision-records/ui_settings_user_open.json "
        "(Indstillinger Profil frames, accept)"
    )
    if parity_of_special_user_get:
        row["evidence"] = (
            f"{row['evidence']}; research151 dual-session reconfirm; "
            "maps api.special.user_get to UI settings Profil shell open only"
        )
    row["discovered"] = True
    row["implemented"] = True
    row["contract_tested"] = True
    row["live_tested"] = True
    row["vision_verified"] = True
    row["vision_evidence"] = None
    row["parity_status"] = "shell_open_only"
    row["sensitivity"] = "low"
    row["side_effects"] = "none"
    row["cleanup"] = "not_applicable; read-only observation creates no records"
    row["errors"] = [
        "AUTH_REQUIRED",
        "AUTH_INTERACTION_REQUIRED",
        "UI_CHANGED",
        "EGRESS_DENIED",
        "BILLY_ERROR",
    ]


def apply_ui_settings_user_organizations_open_shell_evidence(
    row: dict[str, Any],
    *,
    parity_of_special_user_organizations: bool = False,
) -> None:
    """Mark Indstillinger Virksomheder (user organizations) panel evidence (research152).

    Empty-input tool; open hub /:org_slug/settings then observe-only click Profil
    then Virksomheder; final path /:org_slug/settings; h1 Indstillinger; markers
    Virksomheder + Alle organisationer + Opret organisation (chrome only). Soft
    seeds rejected. Distinct from Profil user fields, company form, Brugere.
    Never click Opret organisation / Gem. No invent api_settings_*. When
    ``parity_of_special_user_organizations`` is true, dual-counts exact
    ``ui.parity.special.user_organizations`` for ``api.special.user_organizations``.
    Does not green invoice_email, files_upload, user_get, users.*, organizations.*.
    """

    row["method_or_route"] = (
        "mit.billy.dk /:org_slug/settings (read-only Indstillinger Virksomheder/"
        "user-organizations panel open via hub + side-nav click Profil then "
        "Virksomheder; never click Opret organisation/Gem/Upload/Slet)"
    )
    row["tool_name"] = UI_SETTINGS_USER_ORGANIZATIONS_OPEN_TOOL_NAME
    row["request_fields"] = []
    row["response_fields"] = [
        "path_class",
        "heading",
        "shell_kind",
        "user_organizations_panel_markers_present",
    ]
    row["filters"] = []
    row["pagination"] = None
    if not parity_of_special_user_organizations:
        row["api_row_id"] = None
    row["test_references"] = [
        TEST_REFERENCE,
        UI_SETTINGS_USER_ORGANIZATIONS_OPEN_MODEL_TEST_REFERENCE,
        UI_SETTINGS_USER_ORGANIZATIONS_OPEN_UNIT_TEST_REFERENCE,
        UI_SETTINGS_USER_ORGANIZATIONS_OPEN_LIVE_TEST_REFERENCE,
        SERVER_REGISTRY_TEST_REFERENCE,
    ]
    row["evidence"] = (
        "research152 dual-session headless observation + "
        "ui_settings_user_organizations_open product; shell open only (hub "
        "/:org_slug/settings + click Profil then Virksomheder → path class "
        "/:org_slug/settings, h1 Indstillinger, shell_kind=settings_user_organizations, "
        "Virksomheder/Alle organisationer/Opret organisation markers; distinct from "
        "Profil user fields/company/Brugere); soft seeds rejected; no invent "
        "api_settings_*; never click Opret organisation/Gem; does not green "
        "invoice_email/files_upload/user_get/users.* /organizations.* or annual_reports; "
        "vision record tmp/vision-records/ui_settings_user_organizations_open.json "
        "(Indstillinger Virksomheder frames, accept)"
    )
    if parity_of_special_user_organizations:
        row["evidence"] = (
            f"{row['evidence']}; maps api.special.user_organizations to UI "
            "settings Virksomheder multi-org shell open only"
        )
    row["discovered"] = True
    row["implemented"] = True
    row["contract_tested"] = True
    row["live_tested"] = True
    row["vision_verified"] = True
    row["vision_evidence"] = None
    row["parity_status"] = "shell_open_only"
    row["sensitivity"] = "low"
    row["side_effects"] = "none"
    row["cleanup"] = "not_applicable; read-only observation creates no records"
    row["errors"] = [
        "AUTH_REQUIRED",
        "AUTH_INTERACTION_REQUIRED",
        "UI_CHANGED",
        "EGRESS_DENIED",
        "BILLY_ERROR",
    ]


def apply_ui_settings_vat_open_shell_evidence(
    row: dict[str, Any],
    *,
    parity_of_api_list: bool = False,
    parity_of_api_sales_tax_rulesets_list: bool = False,
) -> None:
    """Mark Indstillinger Momssatser (VAT) panel shell open evidence (research130).

    Empty-input tool; open hub /:org_slug/settings then observe-only click
    Momssatser; final path /:org_slug/settings; h1 Indstillinger; markers
    Regelsæt + Satser for salg + Satser for køb. Soft seeds rejected. Distinct
    from company/accounting/invoicing/user. Never click Opret / Gem. No invent
    api_settings_*. Does not green other settings_* or annual_reports or
    taxRates get/create/update/delete/bulk UI parity or nested salesTaxRules /
    taxRateDeductionComponents / residual salesTaxRulesets ops. When
    ``parity_of_api_list`` is true, dual-counts ``ui.parity.taxRates.list`` for
    ``api.taxRates.list`` (research158). When
    ``parity_of_api_sales_tax_rulesets_list`` is true, dual-counts
    ``ui.parity.salesTaxRulesets.list`` for ``api.salesTaxRulesets.list``
    (research159; Regelsæt section). Flags are mutually exclusive.
    """

    if parity_of_api_list and parity_of_api_sales_tax_rulesets_list:
        raise ValueError(
            "apply_ui_settings_vat_open_shell_evidence: "
            "parity_of_api_list and parity_of_api_sales_tax_rulesets_list "
            "are mutually exclusive"
        )

    row["method_or_route"] = (
        "mit.billy.dk /:org_slug/settings (read-only Indstillinger Momssatser/VAT "
        "panel open via hub + side-nav click Momssatser; never click "
        "Opret/Gem/Tilføj/Upload)"
    )
    row["tool_name"] = UI_SETTINGS_VAT_OPEN_TOOL_NAME
    row["request_fields"] = []
    row["response_fields"] = [
        "path_class",
        "heading",
        "shell_kind",
        "vat_panel_markers_present",
    ]
    row["filters"] = []
    row["pagination"] = None
    if not parity_of_api_list and not parity_of_api_sales_tax_rulesets_list:
        row["api_row_id"] = None
    row["test_references"] = [
        TEST_REFERENCE,
        UI_SETTINGS_VAT_OPEN_MODEL_TEST_REFERENCE,
        UI_SETTINGS_VAT_OPEN_UNIT_TEST_REFERENCE,
        UI_SETTINGS_VAT_OPEN_LIVE_TEST_REFERENCE,
        SERVER_REGISTRY_TEST_REFERENCE,
    ]
    row["evidence"] = (
        "research130 dual-session headless observation + ui_settings_vat_open "
        "product; shell open only (hub /:org_slug/settings + click Momssatser → "
        "path class /:org_slug/settings, h1 Indstillinger, shell_kind=settings_vat, "
        "Regelsæt/Satser for salg/Satser for køb markers; distinct from "
        "company/accounting/invoicing/user); soft seeds rejected; no invent "
        "api_settings_*; never click Opret/Gem; does not green other settings_* "
        "or annual_reports or taxRates get/create/update/delete/bulk UI parity "
        "or salesTaxRules/taxRateDeductionComponents/residual salesTaxRulesets "
        "ops UI parity; "
        "API list filters/sort/pagination UI not producted; vision record "
        "tmp/vision-records/ui_settings_vat_open.json "
        "(Indstillinger Momssatser frames, accept)"
    )
    if parity_of_api_list:
        row["evidence"] = (
            f"{row['evidence']}; research158 dual-session reconfirm; "
            "maps api.taxRates.list to UI settings Momssatser shell open only"
        )
    if parity_of_api_sales_tax_rulesets_list:
        row["evidence"] = (
            f"{row['evidence']}; research159 dual-session reconfirm; "
            "maps api.salesTaxRulesets.list to UI settings Momssatser Regelsæt "
            "shell open only"
        )
    row["discovered"] = True
    row["implemented"] = True
    row["contract_tested"] = True
    row["live_tested"] = True
    row["vision_verified"] = True
    row["vision_evidence"] = None
    row["parity_status"] = "shell_open_only"
    row["sensitivity"] = "low"
    row["side_effects"] = "none"
    row["cleanup"] = "not_applicable; read-only observation creates no records"
    row["errors"] = [
        "AUTH_REQUIRED",
        "AUTH_INTERACTION_REQUIRED",
        "UI_CHANGED",
        "EGRESS_DENIED",
        "BILLY_ERROR",
    ]


def apply_ui_settings_users_open_shell_evidence(
    row: dict[str, Any],
    *,
    parity_of_api_list: bool = False,
) -> None:
    """Mark Indstillinger Brugere (org users) panel shell open evidence (research131).

    Empty-input tool; open hub /:org_slug/settings then observe-only click
    Brugere; final path /:org_slug/settings; h1 Indstillinger; markers
    Brugere + Revisorer og bogholdere. Soft seeds rejected. Distinct from
    company/accounting/invoicing/user/vat. Never click Invitér / Overdrag /
    Gem. No invent api_settings_*. Does not green other settings_* or
    annual_reports or users get/update/bulk UI parity. When
    ``parity_of_api_list`` is true, dual-counts ``ui.parity.users.list`` for
    ``api.users.list`` (research141).
    """

    row["method_or_route"] = (
        "mit.billy.dk /:org_slug/settings (read-only Indstillinger Brugere/org users "
        "panel open via hub + side-nav click Brugere; never click "
        "Invitér/Overdrag/Gem/Opret/Tilføj/Upload)"
    )
    row["tool_name"] = UI_SETTINGS_USERS_OPEN_TOOL_NAME
    row["request_fields"] = []
    row["response_fields"] = [
        "path_class",
        "heading",
        "shell_kind",
        "users_panel_markers_present",
    ]
    row["filters"] = []
    row["pagination"] = None
    if not parity_of_api_list:
        row["api_row_id"] = None
    row["test_references"] = [
        TEST_REFERENCE,
        UI_SETTINGS_USERS_OPEN_MODEL_TEST_REFERENCE,
        UI_SETTINGS_USERS_OPEN_UNIT_TEST_REFERENCE,
        UI_SETTINGS_USERS_OPEN_LIVE_TEST_REFERENCE,
        UI_SETTINGS_ACCESS_TOKEN_OPEN_LIVE_TEST_REFERENCE,
        SERVER_REGISTRY_TEST_REFERENCE,
    ]
    row["evidence"] = (
        "research131 dual-session headless observation + ui_settings_users_open "
        "product; shell open only (hub /:org_slug/settings + click Brugere → "
        "path class /:org_slug/settings, h1 Indstillinger, shell_kind=settings_users, "
        "Brugere/Revisorer og bogholdere markers; distinct from "
        "company/accounting/invoicing/user/vat); soft seeds rejected; no invent "
        "api_settings_*; never click Invitér/Overdrag/Gem; does not green other "
        "settings_* or annual_reports or users get/update/bulk UI parity; "
        "API list filters/sort/pagination UI not producted; "
        "vision record tmp/vision-records/ui_settings_users_open.json "
        "(Indstillinger Brugere frames, accept)"
    )
    if parity_of_api_list:
        row["evidence"] = (
            f"{row['evidence']}; research141 dual-session reconfirm; "
            "maps api.users.list to UI settings Brugere shell open only"
        )
    row["discovered"] = True
    row["implemented"] = True
    row["contract_tested"] = True
    row["live_tested"] = True
    row["vision_verified"] = True
    row["vision_evidence"] = None
    row["parity_status"] = "shell_open_only"
    row["sensitivity"] = "low"
    row["side_effects"] = "none"
    row["cleanup"] = "not_applicable; read-only observation creates no records"
    row["errors"] = [
        "AUTH_REQUIRED",
        "AUTH_INTERACTION_REQUIRED",
        "UI_CHANGED",
        "EGRESS_DENIED",
        "BILLY_ERROR",
    ]


def apply_ui_settings_access_token_open_shell_evidence(row: dict[str, Any]) -> None:
    """Mark Indstillinger Adgangsnøgler (access keys) panel shell open (research132).

    Empty-input tool; open hub /:org_slug/settings then observe-only click
    Adgangsnøgler; final path /:org_slug/settings; h1 Indstillinger; marker
    Adgangsnøgler. Soft seeds rejected. Distinct from
    company/accounting/invoicing/user/vat/users/beta. Never click Opret
    adgangsnøgle. No invent api_settings_*. Does not green other settings_*
    or annual_reports.
    """

    row["method_or_route"] = (
        "mit.billy.dk /:org_slug/settings (read-only Indstillinger Adgangsnøgler/"
        "access keys panel open via hub + side-nav click Adgangsnøgler; never "
        "click Opret adgangsnøgle/Gem/Opret/Tilføj/Upload)"
    )
    row["tool_name"] = UI_SETTINGS_ACCESS_TOKEN_OPEN_TOOL_NAME
    row["request_fields"] = []
    row["response_fields"] = [
        "path_class",
        "heading",
        "shell_kind",
        "access_token_panel_markers_present",
    ]
    row["filters"] = []
    row["pagination"] = None
    row["api_row_id"] = None
    row["test_references"] = [
        TEST_REFERENCE,
        UI_SETTINGS_ACCESS_TOKEN_OPEN_MODEL_TEST_REFERENCE,
        UI_SETTINGS_ACCESS_TOKEN_OPEN_UNIT_TEST_REFERENCE,
        UI_SETTINGS_ACCESS_TOKEN_OPEN_LIVE_TEST_REFERENCE,
        SERVER_REGISTRY_TEST_REFERENCE,
    ]
    row["evidence"] = (
        "research132 dual-session headless observation + "
        "ui_settings_access_token_open product; shell open only (hub "
        "/:org_slug/settings + click Adgangsnøgler → path class "
        "/:org_slug/settings, h1 Indstillinger, shell_kind=settings_access_token, "
        "Adgangsnøgler marker; distinct from company/accounting/invoicing/"
        "user/vat/users/beta); soft seeds rejected; no invent api_settings_*; "
        "never click Opret adgangsnøgle; does not green other settings_* or "
        "annual_reports; vision record "
        "tmp/vision-records/ui_settings_access_token_open.json "
        "(Indstillinger Adgangsnøgler frames, accept)"
    )
    row["discovered"] = True
    row["implemented"] = True
    row["contract_tested"] = True
    row["live_tested"] = True
    row["vision_verified"] = True
    row["vision_evidence"] = None
    row["parity_status"] = "shell_open_only"
    row["sensitivity"] = "low"
    row["side_effects"] = "none"
    row["cleanup"] = "not_applicable; read-only observation creates no records"
    row["errors"] = [
        "AUTH_REQUIRED",
        "AUTH_INTERACTION_REQUIRED",
        "UI_CHANGED",
        "EGRESS_DENIED",
        "BILLY_ERROR",
    ]


def apply_ui_settings_beta_open_shell_evidence(row: dict[str, Any]) -> None:
    """Mark Indstillinger Betas panel shell open (research133).

    Empty-input tool; open hub /:org_slug/settings then observe-only click
    Betas; final path /:org_slug/settings; h1 Indstillinger; markers Betas +
    Tidlig adgang. Soft empty seeds rejected. Distinct from
    company/accounting/invoicing/user/vat/users/access_token. Never click
    Opret/Gem. No invent api_settings_*/api_beta_*. Does not green other
    settings_* or annual_reports.
    """

    row["method_or_route"] = (
        "mit.billy.dk /:org_slug/settings (read-only Indstillinger Betas/"
        "early-access panel open via hub + side-nav click Betas; never "
        "click Opret/Gem/Tilføj/Upload/Opgrader)"
    )
    row["tool_name"] = UI_SETTINGS_BETA_OPEN_TOOL_NAME
    row["request_fields"] = []
    row["response_fields"] = [
        "path_class",
        "heading",
        "shell_kind",
        "beta_panel_markers_present",
    ]
    row["filters"] = []
    row["pagination"] = None
    row["api_row_id"] = None
    row["test_references"] = [
        TEST_REFERENCE,
        UI_SETTINGS_BETA_OPEN_MODEL_TEST_REFERENCE,
        UI_SETTINGS_BETA_OPEN_UNIT_TEST_REFERENCE,
        UI_SETTINGS_BETA_OPEN_LIVE_TEST_REFERENCE,
        SERVER_REGISTRY_TEST_REFERENCE,
    ]
    row["evidence"] = (
        "research133 dual-session headless observation + "
        "ui_settings_beta_open product; shell open only (hub "
        "/:org_slug/settings + click Betas → path class "
        "/:org_slug/settings, h1 Indstillinger, shell_kind=settings_beta, "
        "Betas + Tidlig adgang markers; distinct from company/accounting/"
        "invoicing/user/vat/users/access_token); soft empty seeds rejected; "
        "no invent api_settings_*/api_beta_*; never click Opret; does not "
        "green other settings_* or annual_reports; vision record "
        "tmp/vision-records/ui_settings_beta_open.json "
        "(Indstillinger Betas frames, accept)"
    )
    row["discovered"] = True
    row["implemented"] = True
    row["contract_tested"] = True
    row["live_tested"] = True
    row["vision_verified"] = True
    row["vision_evidence"] = None
    row["parity_status"] = "shell_open_only"
    row["sensitivity"] = "low"
    row["side_effects"] = "none"
    row["cleanup"] = "not_applicable; read-only observation creates no records"
    row["errors"] = [
        "AUTH_REQUIRED",
        "AUTH_INTERACTION_REQUIRED",
        "UI_CHANGED",
        "EGRESS_DENIED",
        "BILLY_ERROR",
    ]


def apply_ui_settings_subscription_open_shell_evidence(row: dict[str, Any]) -> None:
    """Mark Indstillinger Abonnement empty panel shell open (research134).

    Empty-input tool; open hub /:org_slug/settings then observe-only click
    Abonnement; final path /:org_slug/settings; h1 Indstillinger; empty panel
    (no h2 / no panel-only content markers). Soft empty seeds rejected.
    Distinct from company/accounting/invoicing/user/vat/users/access_token/beta.
    Never click Opgrader/Skift/Betal/Køb/Gem. No invent api_settings_*/
    api_subscription_*. Does not green annual_reports.
    """

    row["method_or_route"] = (
        "mit.billy.dk /:org_slug/settings (read-only Indstillinger Abonnement "
        "empty panel open via hub + side-nav click Abonnement; never click "
        "Opgrader/Skift abonnement/Betal/Køb/Gem/Opret)"
    )
    row["tool_name"] = UI_SETTINGS_SUBSCRIPTION_OPEN_TOOL_NAME
    row["request_fields"] = []
    row["response_fields"] = [
        "path_class",
        "heading",
        "shell_kind",
        "empty_panel",
    ]
    row["filters"] = []
    row["pagination"] = None
    row["api_row_id"] = None
    row["test_references"] = [
        TEST_REFERENCE,
        UI_SETTINGS_SUBSCRIPTION_OPEN_MODEL_TEST_REFERENCE,
        UI_SETTINGS_SUBSCRIPTION_OPEN_UNIT_TEST_REFERENCE,
        UI_SETTINGS_SUBSCRIPTION_OPEN_LIVE_TEST_REFERENCE,
        SERVER_REGISTRY_TEST_REFERENCE,
    ]
    row["evidence"] = (
        "research134 dual-session headless observation + "
        "ui_settings_subscription_open product; shell open only (hub "
        "/:org_slug/settings + click Abonnement → path class "
        "/:org_slug/settings, h1 Indstillinger, shell_kind=settings_subscription, "
        "empty panel; distinct from company/accounting/invoicing/user/vat/users/"
        "access_token/beta); soft empty seeds rejected; no invent "
        "api_settings_*/api_subscription_*; never click Opgrader/Betal; does not "
        "green annual_reports or other settings_*; vision record "
        "tmp/vision-records/ui_settings_subscription_open.json "
        "(Indstillinger Abonnement empty frames, accept)"
    )
    row["discovered"] = True
    row["implemented"] = True
    row["contract_tested"] = True
    row["live_tested"] = True
    row["vision_verified"] = True
    row["vision_evidence"] = None
    row["parity_status"] = "shell_open_only"
    row["sensitivity"] = "low"
    row["side_effects"] = "none"
    row["cleanup"] = "not_applicable; read-only observation creates no records"
    row["errors"] = [
        "AUTH_REQUIRED",
        "AUTH_INTERACTION_REQUIRED",
        "UI_CHANGED",
        "EGRESS_DENIED",
        "BILLY_ERROR",
    ]


def apply_ui_annual_reports_out_of_scope_by_user(row: dict[str, Any]) -> None:
    """Record owner plan skip for annual_reports (radio DC3B8E96, 2026-08-04).

    Owner decision: Årsrapporter is not in Joakim's Billy plan for this
    deployment. Treat ui.discovery.annual_reports as out_of_scope_by_user — not
    a completion blocker, not not_applicable (nav/route still exist), and not a
    live dual unlock wait. Do not invent ui_annual_* or api_annual_* tools.

    Historical dual Upsedasse evidence (research122/191/192) is retained under
    prior_evidence_ref for inventory honesty. Qualification flags stay false so
    the row is never claimed live- or vision-verified; completeness excludes
    owner-scoped rows instead of greening live cells.
    """

    row["method_or_route"] = (
        "mit.billy.dk /:org_slug/annual_reports (nav Årsrapporter present; "
        "owner out_of_scope_by_user scope_code=ANNUAL_REPORTS_OWNER_SKIP "
        "radio:DC3B8E96; not_applicable rejected; no tool)"
    )
    row["tool_name"] = ""
    row["request_fields"] = []
    row["response_fields"] = []
    row["filters"] = []
    row["pagination"] = None
    row["api_row_id"] = None
    row["test_references"] = [TEST_REFERENCE]
    row["evidence"] = (
        "owner decision radio:DC3B8E96 (2026-08-04): Årsrapporter not included "
        "in Billy plan for this deployment → qualification.kind="
        "out_of_scope_by_user scope_code=ANNUAL_REPORTS_OWNER_SKIP "
        "tools_allowed=false; not a completion blocker; do not invent "
        "ui_annual_* or api_annual_*; not_applicable rejected (nav Årsrapporter "
        "and route family exist; owner skip is plan scope, not absence of UI). "
        "Prior dual evidence retained: research121/122/135 + research191 dual "
        "reconfirm (READY/READY; path /:org_slug/annual_reports; h1 Upsedasse! "
        "both; productable_shell false; tmp/research191_annual_dual.json) + "
        "research192 walls reconfirm; no live dual re-probe for owner skip; "
        "live_tested and vision_verified remain false (not dual-qualified)"
    )
    row["discovered"] = False
    row["implemented"] = False
    row["contract_tested"] = False
    row["live_tested"] = False
    row["vision_verified"] = False
    row["vision_evidence"] = None
    row["parity_status"] = "out_of_scope_by_user"
    row["sensitivity"] = "unknown"
    row["side_effects"] = (
        "none; owner out of scope — no annual-reports FastMCP tool and no "
        "disposable annual-report records for this deployment"
    )
    row["cleanup"] = (
        "not_applicable for owner out-of-scope discovery; no records may be "
        "created; not_applicable parity classification rejected while nav "
        "route exists"
    )
    row["errors"] = [
        "AUTH_INTERACTION_REQUIRED",
        "UI_CHANGED",
    ]
    row["qualification"] = {
        "kind": "out_of_scope_by_user",
        "scope_code": "ANNUAL_REPORTS_OWNER_SKIP",
        "owner_decision_ref": "radio:DC3B8E96",
        "owner_decision_date": "2026-08-04",
        "tools_allowed": False,
        "reason": ("Årsrapporter is not included in the owner Billy plan for this MCP deployment"),
        "not_applicable_decision": "rejected",
        "not_applicable_reason": (
            "nav Årsrapporter and route family exist; owner skip is plan "
            "scope, not absence of a Billy UI workflow"
        ),
        "prior_evidence_ref": "research191_annual_dual",
        "historical_dual_ref": "discovery122_summary_dual_saft.annual_reports",
        "historical_dual_judgment": "A1_UPSEDASSE_STAY_RED",
        "supersedes_blocker_code": "ANNUAL_REPORTS_ORG_INACCESSIBLE",
    }


def geo_ui_not_applicable_api_row(api_row_id: str) -> bool:
    """Return whether dual-session research freezes this API row as UI NA."""

    if api_row_id in GEO_UI_NOT_APPLICABLE_RESEARCH183_IDS:
        return True
    if api_row_id in GEO_UI_NOT_APPLICABLE_RESEARCH184_IDS:
        return True
    if api_row_id in GEO_UI_NOT_APPLICABLE_RESEARCH185_IDS:
        return True
    return any(api_row_id.startswith(prefix) for prefix in GEO_UI_NOT_APPLICABLE_API_PREFIXES)


def apply_ui_geo_reference_not_applicable_evidence(row: dict[str, Any]) -> None:
    """Record dual-session absence of a Billy UI workflow for geo/reference API ops.

    research138: geo families (cities/countries/countryGroups/states/zipcodes).
    research139: currencies + locales after dual path contrast closed the
    research138 deferral.
    research142: accountNatures + balanceModifiers residual soft-empty dual.
    research143: accountGroups residual soft-empty dual (dedicated freeze).
    research144: contactBalancePostings + invoiceReminderAssociations +
    invoiceLateFees residual soft-empty dual (dedicated freeze).
    research147: contactBalancePayments residual soft-empty dual (dedicated
    freeze; balance shells are contrast only — not a payment workflow).
    research148: contactPersons residual soft-empty dual (dedicated freeze;
    clients/Kunder shell is contacts only — not a contactPersons workflow).
    research149: invoiceReminders residual soft-empty dual (dedicated freeze;
    invoices/Fakturaer shell is invoices only — not an invoiceReminders workflow).
    research150: specials invoice_delivery + invoice_logs residual soft-empty dual
    (dedicated freeze; settings Levering is email-only string, not e-invoice/logs
    workflow; invoices shell lacks e-invoice/log markers).
    research162: productPrices residual soft-empty dual (dedicated freeze;
    products/Produkter shell is products only — not a productPrices workflow).
    research176: products.get/update/delete dual absence (dedicated freeze; exact
    ids only — list/create stay tool-green; soft detail chrome-only; list Mere is
    Export/Import only; inventory create is create-only; no dual-count steal).
    research177: organizations.create dual absence (dedicated freeze; exact id
    only — list/get/update dual-count on ui_settings_company_open; create CTA 0 dual).
    research178: accounts.get/create/update/delete dual absence (dedicated freeze;
    exact ids only — list stays tool-green on settings accounting; no create CTA /
    Ret / Mere→Slet dual) + special.invoice_email dual absence (soft email/send/
    delivery empty; Godkend og send on edit rejected as non-compose).
    research179: invoiceLines get/list/create/update/delete dual absence of dedicated
    UI (exact ids only — lines embedded on invoice edit dual; soft /invoiceLines paths
    not a line inventory; no dual-count onto invoices.update; bulk external-contract).
    research180: daybooks.update form absent dual (Mere-only id chrome; soft edit/update
    empty) + billLines get/list/create/update/delete dedicated absent dual (embedded on
    bill edit) + users.get/update dual absence (Brugere list panel only; no detail form).
    research181: daybookTransactions get/list/update/delete dedicated absent dual
    (create producted separately) + taxRates get/create/update/delete (list shell only)
    + salesTaxRulesets get/create/update/delete (list shell only) +
    taxRateDeductionComponents non-bulk absent dual + transactions get/update/delete
    (list shell only; create deferred).
    research184: files.list + files.get only (soft /files empty dual; Bilag SPA hits
    /v2/attachments not /v2/files; attachments.list dual-counted separately).
    research185: attachments.get/create/update/delete dual absence (exact ids only —
    list dual-counted on Bilag; upload surface already greened as files.create +
    special.files_upload; soft /attachments empty; Bilag Slet/Gem/tbody/click 0 dual;
    ban dual-count create onto Bilag upload).
    All: two independent ephemeral READY sessions found no matching UI workflow;
    candidate path classes render soft-empty SPA chrome only (body_len 127,
    h1_count 0) identical to nonsense paths, while known shells expose real
    headings. Design §10.2 allows UI parity not_applicable only when no
    equivalent UI workflow exists — accepted here. Contrast annual_reports
    where nav exists → NA rejected.
    """

    api_row_id = str(row.get("api_row_id") or "")
    resource = api_row_id.split(".", 2)[1] if api_row_id.startswith("api.") else "geo"
    is_research178_accounts = api_row_id in GEO_UI_NOT_APPLICABLE_RESEARCH178_ACCOUNT_IDS
    is_research178_email = api_row_id in GEO_UI_NOT_APPLICABLE_RESEARCH178_SPECIAL_IDS
    is_research179_invoice_lines = api_row_id in GEO_UI_NOT_APPLICABLE_RESEARCH179_INVOICE_LINE_IDS
    is_research180_daybooks_update = (
        api_row_id in GEO_UI_NOT_APPLICABLE_RESEARCH180_DAYBOOKS_UPDATE_IDS
    )
    is_research180_bill_lines = api_row_id in GEO_UI_NOT_APPLICABLE_RESEARCH180_BILL_LINE_IDS
    is_research180_users = api_row_id in GEO_UI_NOT_APPLICABLE_RESEARCH180_USERS_IDS
    is_research181_daybook_tx = api_row_id in GEO_UI_NOT_APPLICABLE_RESEARCH181_DAYBOOK_TX_IDS
    is_research181_tax_rates = api_row_id in GEO_UI_NOT_APPLICABLE_RESEARCH181_TAX_RATE_IDS
    is_research181_rulesets = api_row_id in GEO_UI_NOT_APPLICABLE_RESEARCH181_SALES_TAX_RULESET_IDS
    is_research181_deduction = (
        api_row_id in GEO_UI_NOT_APPLICABLE_RESEARCH181_TAX_RATE_DEDUCTION_IDS
    )
    is_research181_transactions = api_row_id in GEO_UI_NOT_APPLICABLE_RESEARCH181_TRANSACTIONS_IDS
    is_research182_dtl = (
        api_row_id in GEO_UI_NOT_APPLICABLE_RESEARCH182_DAYBOOK_TRANSACTION_LINE_IDS
    )
    is_research183 = api_row_id in GEO_UI_NOT_APPLICABLE_RESEARCH183_IDS
    is_research184 = api_row_id in GEO_UI_NOT_APPLICABLE_RESEARCH184_IDS
    is_research185 = api_row_id in GEO_UI_NOT_APPLICABLE_RESEARCH185_IDS
    is_research177 = api_row_id in GEO_UI_NOT_APPLICABLE_RESEARCH177_ORG_CREATE_IDS
    is_research176 = api_row_id in GEO_UI_NOT_APPLICABLE_RESEARCH176_PRODUCT_IDS
    is_research162 = resource in GEO_UI_NOT_APPLICABLE_RESEARCH162_RESOURCES
    is_research150 = api_row_id in GEO_UI_NOT_APPLICABLE_RESEARCH150_SPECIAL_IDS
    is_research149 = resource in GEO_UI_NOT_APPLICABLE_RESEARCH149_RESOURCES
    is_research148 = resource in GEO_UI_NOT_APPLICABLE_RESEARCH148_RESOURCES
    is_research147 = resource in GEO_UI_NOT_APPLICABLE_RESEARCH147_RESOURCES
    is_research144 = resource in GEO_UI_NOT_APPLICABLE_RESEARCH144_RESOURCES
    is_research143 = resource in GEO_UI_NOT_APPLICABLE_RESEARCH143_RESOURCES
    is_research142 = resource in GEO_UI_NOT_APPLICABLE_RESEARCH142_RESOURCES
    is_research139 = resource in GEO_UI_NOT_APPLICABLE_RESEARCH139_RESOURCES
    if is_research180_daybooks_update:
        research_id = "research180"
        evidence_ref = "research180_daybooks_update_form_absent_dual"
        nonsense_path = "zz-r180-daybooks-update-none"
        dual_agree_flag = "dual_agree_no_daybooks_update_form"
        family_label = "daybooks.update"
        contrast_shells = (
            "daybooks_get(id Mere-only)/daybooks_new(list+create)/invoices/bills/clients"
        )
        list_heading_suffix = (
            "/daybooks id editor(get only Mere dual)/daybooks/new/Fakturaer/Køb/Kunder"
        )
        contrast_controls = [
            "daybooks/id",
            "daybooks/new",
            "invoices",
            "bills",
            "clients",
            nonsense_path,
        ]
    elif is_research180_bill_lines:
        research_id = "research180"
        evidence_ref = "research180_bill_lines_dedicated_absent_dual"
        nonsense_path = "zz-r180-bill-lines-none"
        dual_agree_flag = "dual_agree_no_dedicated_billLines_surface"
        family_label = "billLines.get+list+create+update+delete"
        contrast_shells = (
            "bills_edit(embedded lines only)/bills_list/bills_create/invoices/clients/daybooks"
        )
        list_heading_suffix = (
            "/Køb edit(line fields dual embedded)/Køb/Fakturaer/Kunder/daybooks editor"
        )
        contrast_controls = [
            "bills",
            "bills_edit",
            "invoices",
            "clients",
            "daybooks/new",
            nonsense_path,
        ]
    elif is_research180_users:
        research_id = "research180"
        evidence_ref = "research180_users_get_update_absent_dual"
        nonsense_path = "zz-r180-users-detail-none"
        dual_agree_flag = "dual_agree_no_users_get_update_surface"
        family_label = "users.get+update"
        contrast_shells = (
            "settings_users(list shell only)/settings_company/settings_accounting/invoices/clients"
        )
        list_heading_suffix = (
            "/Indstillinger Brugere(list only)/Virksomhed/Regnskab/Fakturaer/Kunder"
        )
        contrast_controls = [
            "settings_users",
            "settings_company",
            "settings_accounting",
            "invoices",
            "clients",
            nonsense_path,
        ]
    elif is_research181_daybook_tx:
        research_id = "research181"
        evidence_ref = "research181_daybook_transactions_dedicated_absent_dual"
        nonsense_path = "zz-r181-daybook-tx-none"
        dual_agree_flag = "dual_agree_no_dedicated_daybookTransactions_surface"
        family_label = "daybookTransactions.get+list+update+delete"
        contrast_shells = (
            "daybooks_id(create chrome only for create product)/daybooks_new/"
            "transactions_list/invoices/clients"
        )
        list_heading_suffix = (
            "/daybooks/:id(create chrome product only)/daybooks/new/Posteringer/Fakturaer/Kunder"
        )
        contrast_controls = [
            "daybooks/id",
            "daybooks/new",
            "transactions",
            "invoices",
            "clients",
            nonsense_path,
        ]
    elif is_research181_tax_rates:
        research_id = "research181"
        evidence_ref = "research181_tax_rates_get_create_update_delete_absent_dual"
        nonsense_path = "zz-r181-tax-rates-none"
        dual_agree_flag = "dual_agree_no_taxRates_get_create_update_delete_surface"
        family_label = "taxRates.get+create+update+delete"
        contrast_shells = (
            "settings_vat(list shell only)/settings_company/settings_accounting/invoices/clients"
        )
        list_heading_suffix = (
            "/Indstillinger Momssatser(list only)/Virksomhed/Regnskab/Fakturaer/Kunder"
        )
        contrast_controls = [
            "settings_vat",
            "settings_company",
            "settings_accounting",
            "invoices",
            "clients",
            nonsense_path,
        ]
    elif is_research181_rulesets:
        research_id = "research181"
        evidence_ref = "research181_sales_tax_rulesets_non_list_absent_dual"
        nonsense_path = "zz-r181-rulesets-none"
        dual_agree_flag = "dual_agree_no_salesTaxRulesets_get_create_update_delete_surface"
        family_label = "salesTaxRulesets.get+create+update+delete"
        contrast_shells = (
            "settings_vat(list shell Regelsæt text only)/settings_company/invoices/clients/daybooks"
        )
        list_heading_suffix = (
            "/Indstillinger Momssatser Regelsæt(list only)/Virksomhed/Fakturaer/Kunder"
        )
        contrast_controls = [
            "settings_vat",
            "settings_company",
            "invoices",
            "clients",
            "daybooks/new",
            nonsense_path,
        ]
    elif is_research181_deduction:
        research_id = "research181"
        evidence_ref = "research181_tax_rate_deduction_components_absent_dual"
        nonsense_path = "zz-r181-deduction-none"
        dual_agree_flag = "dual_agree_no_taxRateDeductionComponents_surface"
        family_label = "taxRateDeductionComponents.get+list+create+update+delete"
        contrast_shells = "settings_vat(list only)/settings_accounting/invoices/clients/daybooks"
        list_heading_suffix = (
            "/Indstillinger Momssatser(list only)/Regnskab/Fakturaer/Kunder/daybooks"
        )
        contrast_controls = [
            "settings_vat",
            "settings_accounting",
            "invoices",
            "clients",
            "daybooks/new",
            nonsense_path,
        ]
    elif is_research182_dtl:
        research_id = "research182"
        evidence_ref = "research182_daybook_transaction_lines_embedded_only_dual"
        nonsense_path = "zz-r182-dtl-none"
        dual_agree_flag = "dual_agree_no_dedicated_daybookTransactionLines_surface"
        family_label = "daybookTransactionLines.get+list+create+update+delete"
        contrast_shells = (
            "daybooks_id(embedded Tilføj only; create greened as "
            "ui_daybook_transactions_create_open)/daybooks/new/transactions/invoices"
        )
        list_heading_suffix = (
            "/daybooks id(embedded line chrome dual)/daybooks/new/Posteringer/Fakturaer"
        )
        contrast_controls = [
            "daybooks/id",
            "daybooks/new",
            "transactions",
            "invoices",
            nonsense_path,
        ]
    elif is_research183:
        research_id = "research183"
        fam = GEO_UI_NOT_APPLICABLE_RESEARCH183_FAMILY.get(resource, {})
        evidence_ref = fam.get("evidence_ref", "research183_residual_soft_empty_dual")
        dual_agree_flag = fam.get("dual_agree_flag", "dual_agree_soft_empty_residual_family")
        family_label = fam.get("family_label", resource)
        nonsense_path = "zz-r183-none"
        contrast_shells = (
            "daybooks_id/transactions_list_create/bank_accounts/bank_recon/"
            "settings_vat/vat_declarations/uploads(Bilag dual-count deferred)"
        )
        list_heading_suffix = (
            "/daybooks editor/Posteringer/Bankkonti/Afstemning/Momssatser/Momsangivelser/Bilag"
        )
        contrast_controls = [
            "daybooks/id",
            "transactions",
            "bank_accounts",
            "bank_reconciliation",
            "settings_vat",
            "vat-declarations",
            "uploads",
            nonsense_path,
        ]
    elif is_research184:
        research_id = "research184"
        evidence_ref = "research184_files_list_get_soft_empty_dual"
        dual_agree_flag = "dual_agree_no_files_list_get_surface"
        family_label = "files.list+get"
        nonsense_path = "zz-r184-files-none"
        contrast_shells = (
            "uploads_Bilag(attachments inventory SPA dual; files hits 0)/"
            "receipt_inbox_vouchers/soft_files_empty"
        )
        list_heading_suffix = (
            "/Bilag(attachments SPA dual; not files.list)/Bilagsindbakke/soft /files empty"
        )
        contrast_controls = [
            "uploads",
            "vouchers",
            "files",
            nonsense_path,
        ]
    elif is_research185:
        research_id = "research185"
        evidence_ref = "research185_attachments_get_create_update_delete_dual"
        dual_agree_flag = "dual_agree_no_attachments_get_create_update_delete_surface"
        family_label = "attachments.get+create+update+delete"
        nonsense_path = "zz-r185-attachments-residual-none"
        contrast_shells = (
            "uploads_Bilag(list shell dual-count attachments.list; SPA attachments hits dual; "
            "Slet/Gem/tbody/click 0 dual)/soft_attachments_empty/receipt_inbox_vouchers/"
            "files_create_upload_surface"
        )
        list_heading_suffix = (
            "/Bilag(list only; no get/update/delete chrome dual)/soft /attachments empty/"
            "Bilagsindbakke/files.create upload open only"
        )
        contrast_controls = [
            "uploads",
            "attachments",
            "vouchers",
            "files",
            nonsense_path,
        ]
    elif is_research181_transactions:
        research_id = "research181"
        evidence_ref = "research181_transactions_get_update_delete_absent_dual"
        nonsense_path = "zz-r181-tx-detail-none"
        dual_agree_flag = "dual_agree_no_transactions_get_update_delete_surface"
        family_label = "transactions.get+update+delete"
        contrast_shells = (
            "transactions_list(list shell; create producted ui_transactions_create_open)/"
            "daybooks/invoices/clients"
        )
        list_heading_suffix = "/Posteringer(list only)/daybooks editor/Fakturaer/Kunder"
        contrast_controls = [
            "transactions",
            "daybooks/new",
            "invoices",
            "clients",
            nonsense_path,
        ]
    elif is_research179_invoice_lines:
        research_id = "research179"
        evidence_ref = "research179_invoice_lines_dedicated_absent_dual"
        nonsense_path = "zz-r179-invoice-lines-none"
        dual_agree_flag = "dual_agree_no_dedicated_invoiceLines_surface"
        family_label = "invoiceLines.get+list+create+update+delete"
        contrast_shells = (
            "invoices_edit(embedded lines only)/invoices_list/invoices_create/"
            "clients/products/uploads/daybooks"
        )
        list_heading_suffix = (
            "/Faktura edit(line fields dual embedded)/Fakturaer/"
            "Kunder/Produkter/Bilag/daybooks editor"
        )
        contrast_controls = [
            "invoices",
            "invoices_edit",
            "clients",
            "products",
            "uploads",
            "daybooks/new",
            nonsense_path,
        ]
    elif is_research178_accounts:
        research_id = "research178"
        evidence_ref = "research178_accounts_get_create_update_delete_dual"
        nonsense_path = "zz-r178-none"
        dual_agree_flag = "dual_agree_no_accounts_get_create_update_delete_surface"
        family_label = "accounts.get+create+update+delete"
        contrast_shells = (
            "settings_accounting(list shell only)/invoices/clients/suppliers/"
            "uploads/daybooks/products"
        )
        list_heading_suffix = (
            "/Indstillinger Regnskab Kontoplan(list only)/Fakturaer/Kunder/"
            "Leverandører/Bilag/daybooks editor/Produkter"
        )
        contrast_controls = [
            "settings_accounting",
            "invoices",
            "clients",
            "suppliers",
            "uploads",
            "daybooks/new",
            "products",
            nonsense_path,
        ]
    elif is_research178_email:
        research_id = "research178"
        evidence_ref = "research178_special_invoice_email_dual"
        nonsense_path = "zz-r178-email-none"
        dual_agree_flag = "dual_agree_no_invoice_email_compose_surface"
        family_label = "special.invoice_email"
        contrast_shells = (
            "invoices_edit(Godkend og send contrast only)/invoices_list/"
            "settings_invoicing/uploads/clients/products"
        )
        list_heading_suffix = (
            "/Faktura edit(Godkend og send not compose)/Fakturaer/"
            "Indstillinger Levering email string/Bilag/Kunder/Produkter"
        )
        contrast_controls = [
            "invoices",
            "invoices_edit",
            "settings_invoicing",
            "uploads",
            "clients",
            "products",
            nonsense_path,
        ]
    elif is_research177:
        research_id = "research177"
        evidence_ref = "research177_organizations_create_dual"
        nonsense_path = "zz-r177-none"
        dual_agree_flag = "dual_agree_no_organizations_create_surface"
        family_label = "organizations.create"
        contrast_shells = (
            "settings_company(list/get/update dual-count)/invoices/clients/"
            "suppliers/uploads/daybooks/products"
        )
        list_heading_suffix = (
            "/Indstillinger Virksomhed (list+get+update dual-count)/Fakturaer/"
            "Kunder/Leverandører/Bilag/daybooks editor/Produkter"
        )
        contrast_controls = [
            "settings_company",
            "invoices",
            "clients",
            "suppliers",
            "uploads",
            "daybooks/new",
            "products",
            nonsense_path,
        ]
    elif is_research176:
        research_id = "research176"
        evidence_ref = "research176_products_get_update_delete_dual"
        nonsense_path = "zz-r176-none"
        dual_agree_flag = "dual_agree_no_products_get_update_delete_surface"
        family_label = "products.get+update+delete"
        contrast_shells = (
            "products_list/products_create(inventory Opret produkt)/invoices/"
            "clients/suppliers/uploads/daybooks/bank_recon"
        )
        list_heading_suffix = (
            "/Produkter(list only)/Lagermodul create form/Fakturaer/Kunder/"
            "Leverandører/Bilag/daybooks editor/Bankkonti"
        )
        contrast_controls = [
            "products",
            "products_create",
            "invoices",
            "clients",
            "suppliers",
            "uploads",
            "daybooks/new",
            "bank_reconciliation",
            nonsense_path,
        ]
    elif is_research162:
        research_id = "research162"
        evidence_ref = "research162_product_prices_dual"
        nonsense_path = "zz-r162-none"
        dual_agree_flag = "dual_agree_soft_empty_productPrices"
        family_label = "productPrices"
        contrast_shells = (
            "products/products_import/invoices/clients/suppliers/uploads/"
            "daybooks/bank_recon/settings_vat"
        )
        list_heading_suffix = (
            "/Produkter/import shell/Fakturaer/Kunder/Leverandører/Bilag/"
            "daybooks editor/Bankkonti/Afstemning/Momssatser"
        )
        contrast_controls = [
            "products",
            "products_import",
            "invoices",
            "clients",
            "suppliers",
            "uploads",
            "daybooks/new",
            "bank_reconciliation",
            "settings_vat",
            nonsense_path,
        ]
    elif is_research150:
        research_id = "research150"
        evidence_ref = "research150_specials_invoice_delivery_logs_dual"
        nonsense_path = "zz-research150-no-such-route"
        dual_agree_flag = "dual_agree_soft_empty_specials_delivery_logs"
        family_label = "special.invoice_delivery+invoice_logs"
        contrast_shells = (
            "invoices/settings_invoicing(email Levering contrast)/uploads/"
            "transactions/clients/suppliers/daybooks/bank_recon/products"
        )
        list_heading_suffix = (
            "/Fakturaer/Indstillinger(Levering af faktura pr. e-mail)/Bilag/"
            "Posteringer/Kunder/Leverandører/daybooks editor/Bankkonti/Produkter"
        )
        contrast_controls = [
            "invoices",
            "settings_invoicing",
            "uploads",
            "transactions",
            "clients",
            "suppliers",
            "daybooks/new",
            "bank_reconciliation",
            "products",
            nonsense_path,
        ]
    elif is_research149:
        research_id = "research149"
        evidence_ref = "research149_invoice_reminders_dual"
        nonsense_path = "zz-research149-no-such-route"
        dual_agree_flag = "dual_agree_soft_empty_invoiceReminders"
        family_label = "invoiceReminders"
        contrast_shells = (
            "invoices/clients/suppliers/uploads/settings_company/"
            "settings_users/settings_invoicing/daybooks/bank_recon/products"
        )
        list_heading_suffix = (
            "/Fakturaer/Kunder/Leverandører/Bilag/Indstillinger/"
            "daybooks editor/Bankkonti/Afstemning/Produkter"
        )
        contrast_controls = [
            "invoices",
            "clients",
            "suppliers",
            "uploads",
            "settings_company",
            "settings_users",
            "settings_invoicing",
            "daybooks/new",
            "bank_reconciliation",
            "products",
            nonsense_path,
        ]
    elif is_research148:
        research_id = "research148"
        evidence_ref = "research148_contact_persons_dual"
        nonsense_path = "zz-research148-no-such-route"
        dual_agree_flag = "dual_agree_soft_empty_contactPersons"
        family_label = "contactPersons"
        contrast_shells = (
            "clients/invoices/suppliers/uploads/settings_company/"
            "settings_users/daybooks/bank_recon/products"
        )
        list_heading_suffix = (
            "/Kunder/Fakturaer/Leverandører/Bilag/Indstillinger/"
            "daybooks editor/Bankkonti/Afstemning/Produkter"
        )
        contrast_controls = [
            "clients",
            "invoices",
            "suppliers",
            "uploads",
            "settings_company",
            "settings_users",
            "daybooks/new",
            "bank_reconciliation",
            "products",
            nonsense_path,
        ]
    elif is_research147:
        research_id = "research147"
        evidence_ref = "research147_contact_balance_payments_dual"
        nonsense_path = "zz-research147-no-such-route"
        dual_agree_flag = "dual_agree_soft_empty_contactBalancePayments"
        family_label = "contactBalancePayments"
        contrast_shells = (
            "debtor_balances/creditor_balances/invoices/settings_accounting/"
            "settings_vat/daybooks/bank_recon/products/uploads"
        )
        list_heading_suffix = (
            "/Tilgodehavender/Skyldige udgifter/Fakturaer/Indstillinger/"
            "daybooks editor/Bankkonti/Afstemning/Produkter/Bilag"
        )
        contrast_controls = [
            "debtor_balances",
            "creditor_balances",
            "invoices",
            "settings_accounting",
            "settings_vat",
            "daybooks/new",
            "bank_reconciliation",
            "products",
            "uploads",
            nonsense_path,
        ]
    elif is_research144:
        research_id = "research144"
        evidence_ref = "research144_contact_invoice_join_dual"
        nonsense_path = "zz-research144-no-such-route"
        dual_agree_flag = "dual_agree_soft_empty_contact_invoice_join"
        family_label = "contactBalancePostings/invoiceReminderAssociations/invoiceLateFees"
        contrast_shells = (
            "invoices/debtor_balances/creditor_balances/settings_invoicing/"
            "settings_accounting/settings_vat/daybooks/bank_recon/products/uploads"
        )
        list_heading_suffix = (
            "/Fakturaer/balances/Indstillinger/daybooks editor/Bankkonti/Afstemning/Produkter"
        )
        contrast_controls = [
            "invoices",
            "debtor_balances",
            "creditor_balances",
            "settings_invoicing",
            "settings_accounting",
            "settings_vat",
            "daybooks/new",
            "bank_reconciliation",
            "products",
            "uploads",
            nonsense_path,
        ]
    elif is_research143:
        research_id = "research143"
        evidence_ref = "research143_account_groups_dual"
        nonsense_path = "zz-research143-no-such-route"
        dual_agree_flag = "dual_agree_soft_empty_accountGroups"
        family_label = "accountGroups"
        contrast_shells = (
            "settings_accounting/settings_vat/settings_company/daybooks_new/bank-accounts/products"
        )
        list_heading_suffix = (
            "/Indstillinger(Kontoplan|Momssatser|company)/daybooks editor/Bankkonti/Produkter"
        )
        contrast_controls = [
            "settings_accounting",
            "settings_vat",
            "settings_company",
            "daybooks/new",
            "bank-accounts",
            "products",
            nonsense_path,
        ]
    elif is_research142:
        research_id = "research142"
        evidence_ref = "research142_account_natures_balance_modifiers_dual"
        nonsense_path = "zz-research142-no-such-route"
        dual_agree_flag = "dual_agree_soft_empty_accountNatures_balanceModifiers"
        family_label = "accountNatures/balanceModifiers"
        contrast_shells = "settings_accounting/settings_vat/daybooks_new/bank-accounts"
        list_heading_suffix = "/Indstillinger(Kontoplan|Momssatser)/daybooks editor/Bankkonti"
        contrast_controls = [
            "settings_accounting",
            "settings_vat",
            "daybooks/new",
            "bank-accounts",
            nonsense_path,
        ]
    elif is_research139:
        research_id = "research139"
        evidence_ref = "research139_currencies_locales_dual+contrast"
        nonsense_path = "zzzz-research139-nonexistent"
        dual_agree_flag = "dual_agree_no_currency_locale_nav"
        family_label = "currency/locale"
        contrast_shells = "invoices/products/transactions/vat-declarations/settings"
        list_heading_suffix = "/Momsangivelser/Indstillinger"
        contrast_controls = [
            "invoices",
            "products",
            "transactions",
            "vat-declarations",
            "settings",
            nonsense_path,
        ]
    else:
        research_id = "research138"
        evidence_ref = "research138_geo_ui_dual+contrast"
        nonsense_path = "zzzz-research138-nonexistent"
        dual_agree_flag = "dual_agree_no_geo_nav"
        family_label = "geo"
        contrast_shells = "invoices/products/transactions"
        list_heading_suffix = ""
        contrast_controls = [
            "invoices",
            "products",
            "transactions",
            nonsense_path,
        ]
    row["method_or_route"] = (
        f"no equivalent mit.billy.dk UI workflow for {api_row_id} "
        f"({research_id} dual-session: no nav label/href for {resource}; "
        "candidate path classes soft-empty SPA chrome-only body_len 127 "
        "h1_count 0 identical to nonsense paths; known list shells contrast "
        "with h1 Fakturaer/Produkter/Posteringer"
        f"{list_heading_suffix}; "
        f"evidence_code={GEO_UI_NOT_APPLICABLE_EVIDENCE_CODE}; "
        "not_applicable accepted)"
    )

    if is_research177:
        row["method_or_route"] = (
            f"no equivalent mit.billy.dk UI workflow for {api_row_id} "
            f"({research_id} dual-session: company/Virksomhed panel dual present "
            "for list/get/update dual-count; Opret/Ny/Tilføj virksomhed create "
            "CTAs 0 dual; multi-org create workflow absent; "
            f"contrast shells{list_heading_suffix}; "
            f"evidence_code={GEO_UI_NOT_APPLICABLE_EVIDENCE_CODE}; "
            "not_applicable accepted)"
        )
    if is_research176:
        row["method_or_route"] = (
            f"no equivalent mit.billy.dk UI workflow for {api_row_id} "
            f"({research_id} dual-session: soft /products/:id|/edit|/overview "
            "chrome-only marker false inputs_n 0; list click stays list "
            "(false-green risk); list Mere Eksportér/Importér only Slet 0 dual; "
            "inventory Opret produkt is create-only already greened; "
            f"contrast shells{list_heading_suffix}; "
            f"evidence_code={GEO_UI_NOT_APPLICABLE_EVIDENCE_CODE}; "
            "not_applicable accepted)"
        )
    if is_research178_accounts:
        row["method_or_route"] = (
            f"no equivalent mit.billy.dk UI workflow for {api_row_id} "
            f"({research_id} dual-session: settings accounting Regnskab/Kontoplan "
            "panel dual is list shell only; Tilføj/Opret/Ny konto create CTAs 0 dual; "
            "Ret/row get-update absent dual; Mere→Slet konto absent dual; "
            "soft /accounts routes rewrite only; "
            f"contrast shells{list_heading_suffix}; "
            f"evidence_code={GEO_UI_NOT_APPLICABLE_EVIDENCE_CODE}; "
            "not_applicable accepted)"
        )
    if is_research179_invoice_lines:
        row["method_or_route"] = (
            f"no equivalent mit.billy.dk UI dedicated workflow for {api_row_id} "
            f"({research_id} dual-session: soft /invoiceLines|/invoice-lines|"
            "/invoices/:id/lines not a line inventory dual; invoice edit path dual "
            "embeds line fields (inputs_n 9) already mapped to invoices.update; "
            "no dual-count steal of line ops onto parent update tool; "
            f"contrast shells{list_heading_suffix}; "
            f"evidence_code={GEO_UI_NOT_APPLICABLE_EVIDENCE_CODE}; "
            "not_applicable accepted)"
        )
    if is_research180_daybooks_update:
        row["method_or_route"] = (
            f"no equivalent mit.billy.dk UI workflow for {api_row_id} "
            f"({research_id} dual-session: daybook id path dual is get/editor chrome "
            "with Mere only; Gem/Opdater/Ret/name form 0 dual; soft /edit|/update "
            "empty inputs 0 dual; no dual-count steal onto daybooks.get tool; "
            f"contrast shells{list_heading_suffix}; "
            f"evidence_code={GEO_UI_NOT_APPLICABLE_EVIDENCE_CODE}; "
            "not_applicable accepted)"
        )
    if is_research180_bill_lines:
        row["method_or_route"] = (
            f"no equivalent mit.billy.dk UI dedicated workflow for {api_row_id} "
            f"({research_id} dual-session: soft /billLines|/bill-lines|"
            "/bills/:id/lines not a line inventory dual; bill edit path dual "
            "embeds line fields (inputs_n 11) already mapped to bills.update; "
            "no dual-count steal of line ops onto parent bill tools; "
            f"contrast shells{list_heading_suffix}; "
            f"evidence_code={GEO_UI_NOT_APPLICABLE_EVIDENCE_CODE}; "
            "not_applicable accepted)"
        )
    if is_research180_users:
        row["method_or_route"] = (
            f"no equivalent mit.billy.dk UI workflow for {api_row_id} "
            f"({research_id} dual-session: settings Brugere panel dual is list shell "
            "only (Brugere + Revisorer og bogholdere markers); Ret/detail form 0 dual; "
            "users.list stays tool-green on ui_settings_users_open; no dual-count steal; "
            f"contrast shells{list_heading_suffix}; "
            f"evidence_code={GEO_UI_NOT_APPLICABLE_EVIDENCE_CODE}; "
            "not_applicable accepted)"
        )
    if is_research181_daybook_tx:
        row["method_or_route"] = (
            f"no equivalent mit.billy.dk UI dedicated workflow for {api_row_id} "
            f"({research_id} dual-session: dedicated /daybook-transactions paths "
            "soft-empty body_len 138 dual; seeded dtx id routes not detail forms dual; "
            "create chrome lives on daybooks/:id producted separately as "
            "ui_daybook_transactions_create_open; no dual-count steal onto daybooks.* "
            "or create product; "
            f"contrast shells{list_heading_suffix}; "
            f"evidence_code={GEO_UI_NOT_APPLICABLE_EVIDENCE_CODE}; "
            "not_applicable accepted)"
        )
    if is_research181_tax_rates:
        row["method_or_route"] = (
            f"no equivalent mit.billy.dk UI workflow for {api_row_id} "
            f"({research_id} dual-session: settings Momssatser panel dual is list shell "
            "only; Opret/Ret/Gem/Slet chrome 0 dual; soft /tax-rates/:id inputs 0 dual; "
            "taxRates.list stays tool-green on ui_settings_vat_open; no dual-count steal; "
            f"contrast shells{list_heading_suffix}; "
            f"evidence_code={GEO_UI_NOT_APPLICABLE_EVIDENCE_CODE}; "
            "not_applicable accepted)"
        )
    if is_research181_rulesets:
        row["method_or_route"] = (
            f"no equivalent mit.billy.dk UI workflow for {api_row_id} "
            f"({research_id} dual-session: settings Momssatser Regelsæt list shell dual; "
            "dedicated soft ruleset routes body_len 138 dual; get/create/update/delete "
            "chrome 0 dual; salesTaxRulesets.list stays tool-green on "
            "ui_settings_vat_open; no dual-count steal; "
            f"contrast shells{list_heading_suffix}; "
            f"evidence_code={GEO_UI_NOT_APPLICABLE_EVIDENCE_CODE}; "
            "not_applicable accepted)"
        )
    if is_research181_deduction:
        row["method_or_route"] = (
            f"no equivalent mit.billy.dk UI workflow for {api_row_id} "
            f"({research_id} dual-session: no nav/dedicated path dual; soft-empty SPA "
            "chrome class dual; no form chrome dual; "
            f"contrast shells{list_heading_suffix}; "
            f"evidence_code={GEO_UI_NOT_APPLICABLE_EVIDENCE_CODE}; "
            "not_applicable accepted)"
        )
    if is_research182_dtl:
        row["method_or_route"] = (
            f"no equivalent mit.billy.dk UI dedicated workflow for {api_row_id} "
            f"({research_id} dual-session: dedicated /daybook-transaction-lines paths "
            "soft-empty body_len 138 dual; line chrome lives embedded on daybooks/:id "
            "already greened as ui_daybook_transactions_create_open for "
            "daybookTransactions.create only; no dual-count steal onto lines.* or "
            "daybooks.*; "
            f"contrast shells{list_heading_suffix}; "
            f"evidence_code={GEO_UI_NOT_APPLICABLE_EVIDENCE_CODE}; "
            "not_applicable accepted)"
        )
    if is_research184:
        row["method_or_route"] = (
            f"no equivalent mit.billy.dk UI dedicated workflow for {api_row_id} "
            f"({research_id} dual-session: soft /files|/filer soft-empty body_len 138 dual; "
            "Bilag /:org_slug/uploads is attachments inventory (SPA hits /v2/attachments "
            "dual, files hits 0 dual); attachments.list dual-counted on ui_uploads_list "
            "separately; do not dual-count files.list/get onto Bilag; "
            f"contrast shells{list_heading_suffix}; "
            f"evidence_code={GEO_UI_NOT_APPLICABLE_EVIDENCE_CODE}; "
            "not_applicable accepted)"
        )
    if is_research185:
        row["method_or_route"] = (
            f"no equivalent mit.billy.dk UI dedicated workflow for {api_row_id} "
            f"({research_id} dual-session: soft /attachments soft-empty dual; Bilag list "
            "shell dual has SPA /v2/attachments hits but Slet/Gem/tbody/click candidates "
            "0 dual (no get/update/delete chrome); Vedhæft join-form 0 dual; upload "
            "surface already greened as files.create + special.files_upload — ban "
            "dual-count as attachments.create; attachments.list stays dual-count on "
            "ui_uploads_list; "
            f"contrast shells{list_heading_suffix}; "
            f"evidence_code={GEO_UI_NOT_APPLICABLE_EVIDENCE_CODE}; "
            "not_applicable accepted)"
        )
    if is_research183:
        ban = {
            "daybookBalanceAccounts": (
                "no dual-count onto ui_daybooks_* or ui_daybook_transactions_create_open"
            ),
            "bankLines": (
                "no dual-count onto ui_bank_accounts_list or ui_bank_reconciliation_open"
            ),
            "bankPayments": (
                "no dual-count onto ui_bank_accounts_list or ui_bank_reconciliation_open"
            ),
            "bankLineMatches": (
                "no dual-count onto ui_bank_accounts_list or ui_bank_reconciliation_open"
            ),
            "bankLineSubjectAssociations": (
                "no dual-count onto ui_bank_accounts_list or ui_bank_reconciliation_open"
            ),
            "postings": (
                "no dual-count onto ui_transactions_list or "
                "ui_transactions_create_open (Posteringer is transactions)"
            ),
            "salesTaxAccounts": "no dual-count onto ui_settings_vat_open",
            "salesTaxRules": "no dual-count onto ui_settings_vat_open",
            "salesTaxMetaFields": "no dual-count onto ui_settings_vat_open",
            "salesTaxPayments": "no dual-count onto ui_vat_declarations_list",
            "salesTaxReturns": (
                "list stays tool-green on ui_vat_declarations_list; detail soft "
                "inputs_n 0 dual — no get/update product"
            ),
        }.get(resource, "no dual-count steal onto greened parent shells")
        row["method_or_route"] = (
            f"no equivalent mit.billy.dk UI dedicated workflow for {api_row_id} "
            f"({research_id} dual-session: dedicated soft routes soft-empty body_len "
            f"138 dual; {ban}; "
            f"contrast shells{list_heading_suffix}; "
            f"evidence_code={GEO_UI_NOT_APPLICABLE_EVIDENCE_CODE}; "
            "not_applicable accepted)"
        )
    if is_research181_transactions:
        row["method_or_route"] = (
            f"no equivalent mit.billy.dk UI workflow for {api_row_id} "
            f"({research_id} dual-session: Posteringer list shell dual ready; "
            "id/detail Ret/Gem/Slet form 0 dual; transactions.list stays tool-green on "
            "ui_transactions_list; transactions.create deferred (Ny postering); "
            "no dual-count steal; "
            f"contrast shells{list_heading_suffix}; "
            f"evidence_code={GEO_UI_NOT_APPLICABLE_EVIDENCE_CODE}; "
            "not_applicable accepted)"
        )
    if is_research178_email:
        row["method_or_route"] = (
            f"no equivalent mit.billy.dk UI workflow for {api_row_id} "
            f"({research_id} dual-session: soft /invoices/:id/email|/send|/delivery "
            "inputs_n 0 Send 0 dual; invoice edit Godkend og send present dual but "
            "rejected as irreversible approve-send not email compose; "
            f"contrast shells{list_heading_suffix}; "
            f"evidence_code={GEO_UI_NOT_APPLICABLE_EVIDENCE_CODE}; "
            "not_applicable accepted)"
        )
    row["tool_name"] = ""
    row["request_fields"] = []
    row["response_fields"] = []
    row["filters"] = []
    row["pagination"] = None
    row["test_references"] = [TEST_REFERENCE]
    levering_note = ""
    if is_research150:
        levering_note = (
            "settings/invoicing dual body_len 1494 shows Levering af faktura pr. "
            "e-mail (email settings only; e_invoice/GLN markers dual false) — "
            "blocks special.invoice_email pure NA only, not delivery/logs; "
        )
    if is_research177:
        levering_note = (
            "research177 dual: company panel dual present (list/get/update "
            "dual-count on ui_settings_company_open); create CTAs "
            "Opret/Ny/Tilføj virksomhed 0 dual; exact organizations.create id "
            "only — not list/get/update/bulk; "
        )
    if is_research179_invoice_lines:
        levering_note = (
            "research179 dual: dedicated invoiceLines routes absent; lines only "
            "embedded on invoice edit (already invoices.update); exact five ops; "
            "not bulk_*; "
        )
    if is_research176:
        levering_note = (
            "research176 dual: soft /products/:id|/edit|/overview chrome-only "
            "(marker false, inputs_n 0); list marker true but click stays list "
            "(false-green risk); list Mere Eksportér/Importér only (Slet 0 dual); "
            "inventory Opret produkt is create-only (already greened); "
            "exact get/update/delete ids only — not list/create/bulk; "
        )
    if is_research178_accounts:
        levering_note = (
            "research178 dual: settings accounting Regnskab/Kontoplan panel dual "
            "(accounts.list shell only on ui_settings_accounting_open); "
            "create CTAs Tilføj/Opret/Ny konto 0 dual; Ret/row get-update absent; "
            "Mere→Slet konto absent; exact get/create/update/delete ids only — "
            "not list/bulk; "
        )
    if is_research178_email:
        levering_note = (
            "research178 dual: soft /invoices/:id/email|/send|/delivery empty "
            "(inputs_n 0, Send 0); edit surface Godkend og send 1 dual rejected as "
            "non-compose irreversible approve-send; exact special.invoice_email id "
            "only — not invoice CRUD tools; "
        )
    if is_research183:
        levering_note = (
            "research183 dual: soft-empty SPA chrome body_len 138 dual for exact "
            "non-bulk residual ids; greened parents stay exclusive (daybooks/"
            "transactions/bank accounts+recon/settings VAT/vat list); attachments/"
            "files Bilag dual-count deferred; annual Upsedasse red; bulk external-"
            "contract red; "
        )
    if is_research184:
        levering_note = (
            "research184 dual: soft /files empty dual; Bilag SPA resource hits "
            "attachments dual and files 0 dual; attachments.list dual-counted on "
            "ui_uploads_list; files.create dual-counted as upload-surface open only; "
            "files.list/get NA only; residual attachments closed by research185; bulk "
            "external-contract red; annual Upsedasse red; "
        )
    if is_research185:
        levering_note = (
            "research185 dual: soft /attachments empty dual; Bilag SPA attachments "
            "hits dual files 0; Slet/Gem/tbody/click candidates 0 dual; no Vedhæft "
            "join-form dual; upload already greened as files.create/"
            "special.files_upload — ban dual-count attachments.create onto Bilag; "
            "attachments.list stays tool-green dual-count; exact get/create/update/"
            "delete ids only — not list/bulk; bulk external-contract red; annual "
            "Upsedasse red; "
        )
    row["evidence"] = (
        f"{research_id} dual independent ephemeral browser sessions (no "
        f"BILLY_API_TOKEN): {dual_agree_flag} true; candidate {family_label} path "
        f"classes soft-empty identical to nonsense "
        f"({nonsense_path}); contrast {contrast_shells} real shells with h1; "
        f"{levering_note}"
        "design §10.2 UI parity "
        f"not_applicable accepted for {api_row_id}; "
        f"evidence_code={GEO_UI_NOT_APPLICABLE_EVIDENCE_CODE}; "
        f"no ui_* {family_label} tool; API lane unchanged (reads offline-green, "
        "live_tested false out_of_scope_by_user; bulk external-contract red); "
        f"evidence_ref={evidence_ref}; "
        f"docs etag {DOCS_ETAG}; MD5 {DOCS_MD5}"
    )
    row["discovered"] = True
    row["implemented"] = True
    row["contract_tested"] = True
    row["live_tested"] = True
    row["vision_verified"] = True
    row["vision_evidence"] = None
    row["parity_status"] = "not_applicable"
    row["sensitivity"] = "low"
    row["side_effects"] = (
        "none; UI parity classified not_applicable — no browser workflow tool "
        "and no records may be created through a geo/reference UI tool"
    )
    row["cleanup"] = "not_applicable; no UI tool and no disposable records for this parity row"
    row["errors"] = [
        "AUTH_INTERACTION_REQUIRED",
        "UI_CHANGED",
        GEO_UI_NOT_APPLICABLE_EVIDENCE_CODE,
    ]
    row["qualification"] = {
        "kind": "ui_not_applicable",
        "evidence_code": GEO_UI_NOT_APPLICABLE_EVIDENCE_CODE,
        "not_applicable_decision": "accepted",
        "not_applicable_reason": (
            "dual-session evidence shows Billy exposes no equivalent UI "
            "workflow for this geo/reference API capability on the dedicated "
            "non-production organisation (nav absence + soft-empty == nonsense)"
        ),
        "sessions": "dual_independent_ephemeral",
        "docs_etag": DOCS_ETAG,
        "docs_md5": DOCS_MD5,
        "evidence_ref": evidence_ref,
        "contrast_controls": contrast_controls,
        "deferred_families": [],
    }


def build_ui_manifest(api_manifest: dict[str, Any]) -> dict[str, Any]:
    """Return red UI route seeds and an explicit parity map for every API row."""

    workflows: list[dict[str, Any]] = []
    for family in UI_DISCOVERY_FAMILIES:
        row: dict[str, Any] = {
            "id": f"ui.discovery.{family}",
            "lane": "ui",
            "area": family,
            "operation": "discovery",
            "method_or_route": f"DISCOVERY REQUIRED: mit.billy.dk route family {family}",
            "request_fields": [],
            "response_fields": [],
            "filters": [],
            "pagination": None,
            "errors": ["AUTH_INTERACTION_REQUIRED", "UI_CHANGED"],
            "sensitivity": "unknown",
            "side_effects": "unknown until a headless typed workflow is verified",
            "cleanup": "not_applicable for route discovery; no records may be created",
            "tool_name": "",
            "test_references": [TEST_REFERENCE],
            "evidence": (
                "Approved design §10.3 route-family discovery seed; no headless qualification yet"
            ),
            "workflow_kind": "discovery",
            "parity_status": "discovery_required",
            "api_row_id": None,
        }
        row.update(red_status(discovered=False))
        row["vision_verified"] = False
        if family == "invoices":
            apply_ui_invoices_list_shell_evidence(row, parity_of_api_list=False)
        if family == "invoices_create":
            apply_ui_invoices_create_open_shell_evidence(row, parity_of_api_create=False)
        if family == "bills_create":
            apply_ui_bills_create_open_shell_evidence(row, parity_of_api_create=False)
        if family == "products":
            apply_ui_products_list_shell_evidence(row, parity_of_api_list=False)
        if family == "customers":
            apply_ui_clients_list_shell_evidence(row, parity_of_api_list=False)
        if family == "clients_create":
            apply_ui_clients_create_open_shell_evidence(row, parity_of_api_create=False)
        if family == "suppliers_create":
            apply_ui_suppliers_create_open_shell_evidence(row)
        if family == "products_create":
            apply_ui_products_create_open_shell_evidence(row, parity_of_api_create=False)
        if family == "bank_accounts":
            apply_ui_bank_accounts_list_shell_evidence(row)
        if family == "quotes":
            apply_ui_quotes_list_shell_evidence(row)
        if family == "recurring_invoices":
            apply_ui_recurring_invoices_list_shell_evidence(row)
        if family == "product_import":
            apply_ui_products_import_shell_evidence(row)
        if family == "suppliers":
            apply_ui_suppliers_list_shell_evidence(row)
        if family == "purchases":
            apply_ui_bills_list_shell_evidence(row, parity_of_api_list=False)
        if family == "debtor_balances":
            apply_ui_debtor_balances_list_shell_evidence(row)
        if family == "creditor_balances":
            apply_ui_creditor_balances_list_shell_evidence(row)
        if family == "uploads":
            apply_ui_uploads_list_shell_evidence(row)
        if family == "receipt_inbox":
            apply_ui_receipt_inbox_list_shell_evidence(row)
        if family == "bank_reconciliation":
            apply_ui_bank_reconciliation_open_shell_evidence(row)
        if family == "financing":
            apply_ui_financing_open_shell_evidence(row)
        if family == "daybooks":
            apply_ui_daybooks_open_shell_evidence(row, parity_of_api_list=False)
        if family == "transactions":
            apply_ui_transactions_list_shell_evidence(row, parity_of_api_list=False)
        if family == "reports":
            apply_ui_reports_open_shell_evidence(row)
        if family == "vat_declarations":
            apply_ui_vat_declarations_list_shell_evidence(row)
        if family == "exports":
            apply_ui_exports_open_shell_evidence(row)
        if family == "saft_exports":
            apply_ui_saft_exports_open_shell_evidence(row)
        if family == "addons":
            apply_ui_addons_open_shell_evidence(row)
        if family == "integrations":
            apply_ui_integrations_open_shell_evidence(row)
        if family == "inventory":
            apply_ui_inventory_open_shell_evidence(row)
        if family == "settings_company":
            apply_ui_settings_company_open_shell_evidence(row)
        if family == "settings_accounting":
            apply_ui_settings_accounting_open_shell_evidence(row)
        if family == "settings_invoicing":
            apply_ui_settings_invoicing_open_shell_evidence(row)
        if family == "settings_user":
            apply_ui_settings_user_open_shell_evidence(row)
        if family == "settings_user_organizations":
            apply_ui_settings_user_organizations_open_shell_evidence(row)
        if family == "settings_vat":
            apply_ui_settings_vat_open_shell_evidence(row)
        if family == "settings_users":
            apply_ui_settings_users_open_shell_evidence(row)
        if family == "settings_access_token":
            apply_ui_settings_access_token_open_shell_evidence(row)
        if family == "settings_beta":
            apply_ui_settings_beta_open_shell_evidence(row)
        if family == "settings_subscription":
            apply_ui_settings_subscription_open_shell_evidence(row)
        if family == "annual_reports":
            apply_ui_annual_reports_out_of_scope_by_user(row)
        workflows.append(row)

    for api_row in api_manifest["operations"]:
        row = {
            "id": f"ui.parity.{api_row['id'][4:]}",
            "lane": "ui",
            "area": api_row["area"],
            "operation": "api_parity",
            "method_or_route": f"PARITY DISCOVERY REQUIRED for {api_row['id']}",
            "request_fields": api_row["request_fields"],
            "response_fields": api_row["response_fields"],
            "filters": api_row["filters"],
            "pagination": api_row["pagination"],
            "errors": ["AUTH_INTERACTION_REQUIRED", "UI_CHANGED"],
            "sensitivity": api_row["sensitivity"],
            "side_effects": api_row["side_effects"],
            "cleanup": api_row["cleanup"],
            "tool_name": "",
            "test_references": [TEST_REFERENCE],
            "evidence": (
                f"API parity required by approved design §10.2; mapped from {api_row['id']}"
            ),
            "workflow_kind": "api_parity",
            "parity_status": "discovery_required",
            "api_row_id": api_row["id"],
        }
        row.update(red_status(discovered=False))
        row["vision_verified"] = False
        # Shell-open only: rewrite schema to the empty-input tool contract (R1).
        if api_row["id"] == "api.invoices.list":
            apply_ui_invoices_list_shell_evidence(row, parity_of_api_list=True)
        if api_row["id"] == "api.invoices.create":
            apply_ui_invoices_create_open_shell_evidence(row, parity_of_api_create=True)
        if api_row["id"] == "api.invoices.get":
            apply_ui_invoices_get_open_shell_evidence(row, parity_of_api_get=True)
        if api_row["id"] == "api.invoices.update":
            apply_ui_invoices_update_open_shell_evidence(row, parity_of_api_update=True)
        if api_row["id"] == "api.invoices.delete":
            apply_ui_invoices_delete_open_shell_evidence(row, parity_of_api_delete=True)
        if api_row["id"] == "api.bills.get":
            apply_ui_bills_get_open_shell_evidence(row, parity_of_api_get=True)
        if api_row["id"] == "api.bills.update":
            apply_ui_bills_update_open_shell_evidence(row, parity_of_api_update=True)
        if api_row["id"] == "api.bills.delete":
            apply_ui_bills_delete_open_shell_evidence(row, parity_of_api_delete=True)
        if api_row["id"] == "api.bills.create":
            apply_ui_bills_create_open_shell_evidence(row, parity_of_api_create=True)
        if api_row["id"] == "api.products.list":
            apply_ui_products_list_shell_evidence(row, parity_of_api_list=True)
        if api_row["id"] == "api.products.create":
            apply_ui_products_create_open_shell_evidence(row, parity_of_api_create=True)
        if api_row["id"] == "api.contacts.list":
            apply_ui_clients_list_shell_evidence(row, parity_of_api_list=True)
        if api_row["id"] == "api.contacts.create":
            apply_ui_clients_create_open_shell_evidence(row, parity_of_api_create=True)
        if api_row["id"] == "api.contacts.get":
            apply_ui_clients_get_open_shell_evidence(row, parity_of_api_get=True)
        if api_row["id"] == "api.contacts.update":
            apply_ui_clients_update_open_shell_evidence(row, parity_of_api_update=True)
        if api_row["id"] == "api.contacts.delete":
            apply_ui_clients_delete_open_shell_evidence(row, parity_of_api_delete=True)
        if api_row["id"] == "api.bills.list":
            apply_ui_bills_list_shell_evidence(row, parity_of_api_list=True)
        if api_row["id"] == "api.transactions.list":
            apply_ui_transactions_list_shell_evidence(row, parity_of_api_list=True)
        if api_row["id"] == "api.salesTaxReturns.list":
            apply_ui_vat_declarations_list_shell_evidence(row, parity_of_api_list=True)
        if api_row["id"] == "api.users.list":
            apply_ui_settings_users_open_shell_evidence(row, parity_of_api_list=True)
        if api_row["id"] == "api.accounts.list":
            apply_ui_settings_accounting_open_shell_evidence(row, parity_of_api_list=True)
        if api_row["id"] == "api.taxRates.list":
            apply_ui_settings_vat_open_shell_evidence(row, parity_of_api_list=True)
        if api_row["id"] == "api.salesTaxRulesets.list":
            apply_ui_settings_vat_open_shell_evidence(
                row, parity_of_api_sales_tax_rulesets_list=True
            )
        if api_row["id"] == "api.organizations.list":
            apply_ui_settings_company_open_shell_evidence(row, parity_of_api_list=True)
        if api_row["id"] == "api.organizations.get":
            apply_ui_settings_company_open_shell_evidence(row, parity_of_api_get=True)
        if api_row["id"] == "api.organizations.update":
            apply_ui_settings_company_open_shell_evidence(row, parity_of_api_update=True)
        if api_row["id"] == "api.daybooks.get":
            apply_ui_daybooks_get_open_shell_evidence(row, parity_of_api_get=True)
        if api_row["id"] == "api.daybooks.delete":
            apply_ui_daybooks_delete_open_shell_evidence(row, parity_of_api_delete=True)
        if api_row["id"] == "api.daybookTransactions.create":
            apply_ui_daybook_transactions_create_open_shell_evidence(row, parity_of_api_create=True)
        if api_row["id"] == "api.transactions.create":
            apply_ui_transactions_create_open_shell_evidence(row, parity_of_api_create=True)
        if api_row["id"] == "api.daybooks.list":
            apply_ui_daybooks_open_shell_evidence(row, parity_of_api_list=True)
        if api_row["id"] == "api.daybooks.create":
            apply_ui_daybooks_open_shell_evidence(row, parity_of_api_create=True)
        if api_row["id"] == "api.special.user_get":
            apply_ui_settings_user_open_shell_evidence(row, parity_of_special_user_get=True)
        if api_row["id"] == "api.special.user_organizations":
            apply_ui_settings_user_organizations_open_shell_evidence(
                row, parity_of_special_user_organizations=True
            )
        if api_row["id"] == "api.special.files_upload":
            apply_ui_uploads_list_shell_evidence(row, parity_of_special_files_upload=True)
        if api_row["id"] == "api.attachments.list":
            apply_ui_uploads_list_shell_evidence(row, parity_of_api_attachments_list=True)
        if api_row["id"] == "api.files.create":
            apply_ui_uploads_list_shell_evidence(row, parity_of_api_files_create=True)
        if geo_ui_not_applicable_api_row(api_row["id"]):
            apply_ui_geo_reference_not_applicable_evidence(row)
        workflows.append(row)

    apply_ui_product_plane_bulk_parity_honesty(workflows)
    apply_ui_product_plane_bulk_chrome_dual_na_strong(workflows)
    apply_ui_product_plane_bulk_chrome_dual_na_soft_tool(workflows)
    apply_ui_product_plane_bulk_chrome_dual_na_empty_list(workflows)
    apply_ui_cud_parity_open_only_honesty(workflows)
    apply_ui_contacts_cud_preview_tool_names(workflows)
    apply_ui_bills_cud_preview_tool_names(workflows)
    apply_ui_organizations_update_preview_tool_name(workflows)
    apply_ui_invoices_cud_preview_tool_names(workflows)
    apply_ui_products_create_preview_tool_name(workflows)
    apply_ui_cud_proved_preview_execute(workflows)
    apply_ui_residual_write_out_of_scope_by_user(workflows)

    return {
        "manifest": "billy_ui_workflows_phase_0",
        "schema_version": 1,
        "workflows": workflows,
    }


def build_browser_egress() -> dict[str, Any]:
    """Return the deliberately minimal browser policy from the frozen brief."""

    return {
        "manifest": "billy_browser_egress_phase_0",
        "schema_version": 1,
        "default_action": "deny",
        "hosts": [
            {
                "host": "mit.billy.dk",
                "browser_action": "allow",
                "api_client_action": "deny",
                "owner": "ui_auth",
                "purpose": "Billy web interface and headless authentication only",
                "condition": "typed UI/auth workflow",
                "evidence": "Frozen brief §10.3: official app host",
                "test_references": [
                    TEST_REFERENCE,
                    "tests/unit/test_browser.py",
                    UI_INVOICES_LIST_LIVE_TEST_REFERENCE,
                    UI_PRODUCTS_LIST_LIVE_TEST_REFERENCE,
                    UI_CLIENTS_LIST_LIVE_TEST_REFERENCE,
                    UI_BANK_ACCOUNTS_LIST_LIVE_TEST_REFERENCE,
                    UI_QUOTES_LIST_LIVE_TEST_REFERENCE,
                    UI_RECURRING_INVOICES_LIST_LIVE_TEST_REFERENCE,
                    UI_PRODUCTS_IMPORT_LIVE_TEST_REFERENCE,
                    UI_SUPPLIERS_LIST_LIVE_TEST_REFERENCE,
                    UI_BILLS_LIST_LIVE_TEST_REFERENCE,
                    UI_DEBTOR_BALANCES_LIST_LIVE_TEST_REFERENCE,
                    UI_CREDITOR_BALANCES_LIST_LIVE_TEST_REFERENCE,
                    UI_UPLOADS_LIST_LIVE_TEST_REFERENCE,
                    UI_RECEIPT_INBOX_LIST_LIVE_TEST_REFERENCE,
                    UI_BANK_RECONCILIATION_OPEN_LIVE_TEST_REFERENCE,
                    UI_FINANCING_OPEN_LIVE_TEST_REFERENCE,
                    UI_DAYBOOKS_OPEN_LIVE_TEST_REFERENCE,
                    UI_DAYBOOKS_GET_OPEN_LIVE_TEST_REFERENCE,
                    UI_DAYBOOKS_DELETE_OPEN_LIVE_TEST_REFERENCE,
                    UI_DAYBOOK_TRANSACTIONS_CREATE_OPEN_LIVE_TEST_REFERENCE,
                    UI_TRANSACTIONS_CREATE_OPEN_LIVE_TEST_REFERENCE,
                    UI_TRANSACTIONS_LIST_LIVE_TEST_REFERENCE,
                    UI_REPORTS_OPEN_LIVE_TEST_REFERENCE,
                    UI_VAT_DECLARATIONS_LIST_LIVE_TEST_REFERENCE,
                    UI_EXPORTS_OPEN_LIVE_TEST_REFERENCE,
                    UI_SAFT_EXPORTS_OPEN_LIVE_TEST_REFERENCE,
                    UI_ADDONS_OPEN_LIVE_TEST_REFERENCE,
                    UI_INTEGRATIONS_OPEN_LIVE_TEST_REFERENCE,
                    UI_INVENTORY_OPEN_LIVE_TEST_REFERENCE,
                    UI_SETTINGS_COMPANY_OPEN_LIVE_TEST_REFERENCE,
                    UI_SETTINGS_ACCOUNTING_OPEN_LIVE_TEST_REFERENCE,
                    UI_SETTINGS_INVOICING_OPEN_LIVE_TEST_REFERENCE,
                    UI_SETTINGS_USER_OPEN_LIVE_TEST_REFERENCE,
                    UI_SETTINGS_VAT_OPEN_LIVE_TEST_REFERENCE,
                    UI_SETTINGS_USERS_OPEN_LIVE_TEST_REFERENCE,
                    UI_SETTINGS_ACCESS_TOKEN_OPEN_LIVE_TEST_REFERENCE,
                    UI_SETTINGS_BETA_OPEN_LIVE_TEST_REFERENCE,
                    UI_SETTINGS_SUBSCRIPTION_OPEN_LIVE_TEST_REFERENCE,
                ],
            },
            {
                "host": "download.billy.dk",
                "browser_action": "allow",
                "api_client_action": "deny",
                "owner": "future_typed_download",
                "purpose": "Typed Billy file download handling only",
                "condition": "future verified typed download workflow; not general navigation",
                "evidence": "Frozen brief §10.3: files downloadUrl host",
                "test_references": [TEST_REFERENCE],
            },
            {
                "host": "api.billysbilling.com",
                "browser_action": "path_allow",
                "api_client_action": "exclusive_allow",
                "owner": "ui_auth",
                "purpose": (
                    "Path-scoped browser XHR for headless login, shell settle, contacts UI, "
                    "products UI, invoices list/get seed+cleanup, and bills list/get "
                    "seed+cleanup data-plane"
                ),
                "condition": (
                    "browser auth/bootstrap paths plus scoped UI contacts, products, invoices, "
                    "and bills data-planes (research164/165/168/169/170); never full API browse"
                ),
                "evidence": (
                    "research100 headless credentialed discovery: POST /v2/user/login "
                    "then bootstrap GETs reach /:org_slug/dashboard; research164 dual XHR: "
                    "GET/POST/DELETE /v2/contacts and GET /v2/countries for clients; "
                    "F3F318A2 PUT prefix /v2/contacts/ for SPA contact update only "
                    "(no collection PUT, no PATCH); "
                    "research165 dual XHR: GET/POST/DELETE /v2/products plus GET /v2/accounts "
                    "and GET /v2/salesTaxRulesets for products list/detail and disposable seed "
                    "(was ERR_BLOCKED_BY_CLIENT under contacts-only path_allow); "
                    "research168 dual XHR: GET /v2/invoices and GET /v2/bills (prefix covers "
                    "/summary); research169 dual: exact POST /v2/invoices and prefix DELETE "
                    "/v2/invoices for disposable draft seed/cleanup and invoice detail get-open "
                    "at /:org_slug/invoices/:id/edit; research170 dual: exact POST /v2/bills, "
                    "prefix DELETE /v2/bills, and GET /v2/taxRates for disposable draft bill "
                    "seed and bill detail get-open at /:org_slug/bills/:id (emails still denied); "
                    "31F6E753 PUT prefix /v2/bills/ for SPA draft bill update only "
                    "(no collection PUT, no PATCH); "
                    "32662804 PUT prefix /v2/invoices/ for SPA draft invoice update only "
                    "(no collection PUT, no PATCH, no emails); leftover edit after fresh "
                    "page still exact_count=0 input_count=8 product_text_count=0 while "
                    "GET /v2/invoiceLines was denied, so GET prefix /v2/invoiceLines is "
                    "allowed for line-editor render only (no POST/PUT/PATCH/DELETE); "
                    "D859572B forbids PUT /v2/invoiceLines/ unless a captured blocked XHR "
                    "names that path; "
                    "research179 dual: GET/POST/DELETE /v2/daybooks for daybook "
                    "get-open SPA list and disposable seed/cleanup"
                ),
                "browser_path_allows": [
                    {"match": "exact", "methods": ["POST"], "path": "/v2/user/login"},
                    {"match": "prefix", "methods": ["GET"], "path": "/v2/auth/"},
                    {"match": "exact", "methods": ["GET"], "path": "/v2/user"},
                    {"match": "exact", "methods": ["GET"], "path": "/v2/user/bootstrap"},
                    {"match": "exact", "methods": ["GET"], "path": "/oauth2/tokeninfo"},
                    {"match": "exact", "methods": ["GET"], "path": "/user/organizations"},
                    {"match": "exact", "methods": ["GET"], "path": "/user/umbrellas"},
                    {"match": "prefix", "methods": ["GET"], "path": "/v2/organizations/"},
                    {"match": "prefix", "methods": ["PUT"], "path": "/v2/organizations/"},
                    {"match": "prefix", "methods": ["GET"], "path": "/organizations/"},
                    {"match": "prefix", "methods": ["GET"], "path": "/e-invoicing/"},
                    {"match": "prefix", "methods": ["GET"], "path": "/v2/contacts"},
                    {"match": "prefix", "methods": ["POST"], "path": "/v2/contacts"},
                    {"match": "prefix", "methods": ["DELETE"], "path": "/v2/contacts"},
                    {"match": "prefix", "methods": ["PUT"], "path": "/v2/contacts/"},
                    {"match": "prefix", "methods": ["GET"], "path": "/v2/countries"},
                    {"match": "prefix", "methods": ["GET"], "path": "/v2/products"},
                    {"match": "prefix", "methods": ["POST"], "path": "/v2/products"},
                    {"match": "prefix", "methods": ["DELETE"], "path": "/v2/products"},
                    {"match": "prefix", "methods": ["GET"], "path": "/v2/accounts"},
                    {"match": "prefix", "methods": ["GET"], "path": "/v2/salesTaxRulesets"},
                    {"match": "prefix", "methods": ["GET"], "path": "/v2/invoices"},
                    {"match": "exact", "methods": ["POST"], "path": "/v2/invoices"},
                    {"match": "prefix", "methods": ["DELETE"], "path": "/v2/invoices"},
                    {"match": "prefix", "methods": ["PUT"], "path": "/v2/invoices/"},
                    {"match": "prefix", "methods": ["GET"], "path": "/v2/invoiceLines"},
                    {"match": "prefix", "methods": ["GET"], "path": "/v2/bills"},
                    {"match": "exact", "methods": ["POST"], "path": "/v2/bills"},
                    {"match": "prefix", "methods": ["DELETE"], "path": "/v2/bills"},
                    {"match": "prefix", "methods": ["PUT"], "path": "/v2/bills/"},
                    {"match": "prefix", "methods": ["GET"], "path": "/v2/taxRates"},
                    {"match": "prefix", "methods": ["GET"], "path": "/v2/daybooks"},
                    {"match": "exact", "methods": ["POST"], "path": "/v2/daybooks"},
                    {"match": "prefix", "methods": ["DELETE"], "path": "/v2/daybooks"},
                ],
                "test_references": [
                    TEST_REFERENCE,
                    "tests/unit/test_browser.py",
                    UI_INVOICES_LIST_LIVE_TEST_REFERENCE,
                    UI_PRODUCTS_LIST_LIVE_TEST_REFERENCE,
                    UI_CLIENTS_LIST_LIVE_TEST_REFERENCE,
                    UI_CLIENTS_GET_OPEN_LIVE_TEST_REFERENCE,
                    UI_CLIENTS_CREATE_OPEN_LIVE_TEST_REFERENCE,
                    UI_BANK_ACCOUNTS_LIST_LIVE_TEST_REFERENCE,
                    UI_QUOTES_LIST_LIVE_TEST_REFERENCE,
                    UI_RECURRING_INVOICES_LIST_LIVE_TEST_REFERENCE,
                    UI_PRODUCTS_IMPORT_LIVE_TEST_REFERENCE,
                    UI_SUPPLIERS_LIST_LIVE_TEST_REFERENCE,
                    UI_BILLS_LIST_LIVE_TEST_REFERENCE,
                    UI_BILLS_GET_OPEN_LIVE_TEST_REFERENCE,
                    UI_BILLS_UPDATE_OPEN_LIVE_TEST_REFERENCE,
                    UI_DEBTOR_BALANCES_LIST_LIVE_TEST_REFERENCE,
                    UI_CREDITOR_BALANCES_LIST_LIVE_TEST_REFERENCE,
                    UI_UPLOADS_LIST_LIVE_TEST_REFERENCE,
                    UI_RECEIPT_INBOX_LIST_LIVE_TEST_REFERENCE,
                    UI_BANK_RECONCILIATION_OPEN_LIVE_TEST_REFERENCE,
                    UI_FINANCING_OPEN_LIVE_TEST_REFERENCE,
                    UI_DAYBOOKS_OPEN_LIVE_TEST_REFERENCE,
                    UI_DAYBOOKS_GET_OPEN_LIVE_TEST_REFERENCE,
                    UI_DAYBOOKS_DELETE_OPEN_LIVE_TEST_REFERENCE,
                    UI_DAYBOOK_TRANSACTIONS_CREATE_OPEN_LIVE_TEST_REFERENCE,
                    UI_TRANSACTIONS_CREATE_OPEN_LIVE_TEST_REFERENCE,
                    UI_TRANSACTIONS_LIST_LIVE_TEST_REFERENCE,
                    UI_REPORTS_OPEN_LIVE_TEST_REFERENCE,
                    UI_VAT_DECLARATIONS_LIST_LIVE_TEST_REFERENCE,
                    UI_EXPORTS_OPEN_LIVE_TEST_REFERENCE,
                    UI_SAFT_EXPORTS_OPEN_LIVE_TEST_REFERENCE,
                    UI_ADDONS_OPEN_LIVE_TEST_REFERENCE,
                    UI_INTEGRATIONS_OPEN_LIVE_TEST_REFERENCE,
                    UI_INVENTORY_OPEN_LIVE_TEST_REFERENCE,
                    UI_SETTINGS_COMPANY_OPEN_LIVE_TEST_REFERENCE,
                    UI_SETTINGS_ACCOUNTING_OPEN_LIVE_TEST_REFERENCE,
                    UI_SETTINGS_INVOICING_OPEN_LIVE_TEST_REFERENCE,
                    UI_SETTINGS_USER_OPEN_LIVE_TEST_REFERENCE,
                    UI_SETTINGS_VAT_OPEN_LIVE_TEST_REFERENCE,
                    UI_SETTINGS_USERS_OPEN_LIVE_TEST_REFERENCE,
                    UI_SETTINGS_ACCESS_TOKEN_OPEN_LIVE_TEST_REFERENCE,
                    UI_SETTINGS_BETA_OPEN_LIVE_TEST_REFERENCE,
                    UI_SETTINGS_SUBSCRIPTION_OPEN_LIVE_TEST_REFERENCE,
                ],
            },
            {
                "host": "api.billy.dk",
                "browser_action": "deny",
                "api_client_action": "deny",
                "owner": "none",
                "purpose": "Denied API alias",
                "condition": "never permitted",
                "evidence": "Frozen brief §2.3 and §10.3 alias-host denial",
                "test_references": [TEST_REFERENCE],
            },
        ],
    }


def count_by(items: list[dict[str, Any]], key: str) -> dict[str, int]:
    """Count non-empty string values in a list of manifest records."""

    counts: dict[str, int] = {}
    for item in items:
        value = item.get(key)
        if isinstance(value, str):
            counts[value] = counts.get(value, 0) + 1
    return dict(sorted(counts.items()))


def is_owner_out_of_scope(row: dict[str, Any]) -> bool:
    """Return whether a row is excluded from qualification completeness by owner scope."""

    qualification = row.get("qualification")
    return isinstance(qualification, dict) and qualification.get("kind") == "out_of_scope_by_user"


def row_is_qualified(row: dict[str, Any], fields: tuple[str, ...]) -> bool:
    """Return whether a row satisfies every qualification state for its lane."""

    if is_owner_out_of_scope(row):
        # Owner-scoped rows are non-blocking; do not require live/vision green cells.
        return True
    return all(row.get(field) is True for field in fields)


def api_qualification_live_api(row: dict[str, Any]) -> str | None:
    """Return the machine-readable live-API scope marker, if present."""

    qualification = row.get("qualification")
    if not isinstance(qualification, dict):
        return None
    live_api = qualification.get("live_api")
    return live_api if isinstance(live_api, str) else None


def api_row_is_qualified(row: dict[str, Any]) -> bool:
    """API completeness: offline flags true, live_tested false, live_api set."""

    return (
        all(row.get(field) is True for field in API_QUALIFICATION_FIELDS)
        and row.get("live_tested") is False
        and api_qualification_live_api(row) == LIVE_API_OUT_OF_SCOPE
    )


def coverage_is_complete(api_rows: list[dict[str, Any]], ui_rows: list[dict[str, Any]]) -> bool:
    """Derive a completeness claim from row evidence and unresolved bulk contracts."""

    return (
        bool(api_rows)
        and bool(ui_rows)
        and not any(row.get("source_kind") == "ambiguous_bulk" for row in api_rows)
        and all(api_row_is_qualified(row) for row in api_rows)
        and all(row_is_qualified(row, UI_QUALIFICATION_FIELDS) for row in ui_rows)
    )


def qualification_blocker(api_rows: list[dict[str, Any]], ui_rows: list[dict[str, Any]]) -> str:
    """Describe the first current evidence gap without changing qualification state."""

    if coverage_is_complete(api_rows, ui_rows):
        return "No manifest qualification blockers remain."
    # User scope (2026-07-31): API live testing is out of scope. Do not blame a
    # missing BILLY_API_TOKEN for incomplete UI qualification.
    if any(row.get("source_kind") == "ambiguous_bulk" for row in api_rows):
        return (
            "External-contract bulk freeze BULK_SCHEMA_UNSPECIFIED_OFFICIAL_DOCS: "
            "92 ambiguous_bulk rows stay red after official docs/asset exhaust "
            "(research137); no bulk tools; "
            "API live_tested stays false (out_of_scope_by_user); "
            "UI annual_reports out_of_scope_by_user (owner radio:DC3B8E96); "
            "product-plane UI bulk honesty closed via dual-NA strong+soft+"
            "empty-list freezes"
        )
    if any(
        not row.get("implemented") or not row.get("contract_tested")
        for row in api_rows
        if row.get("source_kind") != "ambiguous_bulk"
    ):
        return "API offline implementation or contract evidence is incomplete"
    if any(not row.get("live_tested") for row in ui_rows if not is_owner_out_of_scope(row)) or any(
        row.get("vision_verified") is not True for row in ui_rows if not is_owner_out_of_scope(row)
    ):
        return (
            "UI interface live qualification and vision verification incomplete; "
            "API live testing is out of scope by user policy"
        )
    return "Manifest qualification evidence is incomplete"


def build_status(api_manifest: dict[str, Any], ui_manifest: dict[str, Any]) -> dict[str, Any]:
    """Return the generated completeness source derived from manifest row evidence."""

    api_rows = api_manifest["operations"]
    ui_rows = ui_manifest["workflows"]
    rows = api_rows + ui_rows
    return {
        "schema_version": 1,
        "complete": coverage_is_complete(api_rows, ui_rows),
        "phase": CURRENT_COVERAGE_PHASE,
        "official_docs": {"etag": DOCS_ETAG, "md5": DOCS_MD5},
        "source_counts": {
            "api_clear": count_by(api_rows, "source_kind").get("clear", 0),
            "api_ambiguous_bulk": count_by(api_rows, "source_kind").get("ambiguous_bulk", 0),
            "api_special": count_by(api_rows, "source_kind").get("special", 0),
            "api_total": len(api_rows),
            "ui_discovery": count_by(ui_rows, "workflow_kind").get("discovery", 0),
            "ui_api_parity": count_by(ui_rows, "workflow_kind").get("api_parity", 0),
            "ui_total": len(ui_rows),
            "all_rows": len(rows),
        },
        "qualification": {
            "implemented_rows": sum(bool(row["implemented"]) for row in rows),
            "contract_tested_rows": sum(bool(row["contract_tested"]) for row in rows),
            "live_tested_rows": sum(bool(row["live_tested"]) for row in rows),
            "vision_verified_rows": sum(bool(row["vision_verified"]) for row in ui_rows),
            "blocker": qualification_blocker(api_rows, ui_rows),
        },
    }


def render_report(status: dict[str, Any]) -> str:
    """Render a deterministic human-readable companion to status.json."""

    counts = status["source_counts"]
    qualification = status["qualification"]
    if status["complete"]:
        state_summary = (
            "This generated inventory currently satisfies the manifest qualification rules."
        )
    else:
        state_summary = (
            "This generated inventory is currently incomplete. It freezes the official-doc "
            "snapshot with row-level implementation and contract-test evidence. "
            f"Implemented/contract rows: {qualification['implemented_rows']}/"
            f"{qualification['contract_tested_rows']}; UI live/vision rows: "
            f"{qualification['live_tested_rows']}/{qualification['vision_verified_rows']}. "
            "API live_tested remains false under out_of_scope_by_user (not live-verified)."
        )
    return "\n".join(
        [
            "# Phase 1 offline API read-and-write coverage status",
            "",
            state_summary,
            "",
            "| Source | Count |",
            "| --- | ---: |",
            f"| Clear API operations | {counts['api_clear']} |",
            f"| Ambiguous bulk mentions | {counts['api_ambiguous_bulk']} |",
            f"| Documented special routes | {counts['api_special']} |",
            f"| API snapshot total | {counts['api_total']} |",
            f"| UI discovery seeds | {counts['ui_discovery']} |",
            f"| UI API-parity mappings | {counts['ui_api_parity']} |",
            "",
            f"Complete: `{str(status['complete']).lower()}`",
            "",
            f"Blocker: {qualification['blocker']}",
            "",
        ]
    )


def write_json(path: Path, payload: dict[str, Any]) -> None:
    """Write stable JSON text, valid YAML, with a final newline."""

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def generate(root: Path) -> dict[str, Any]:
    """Write every generated coverage artifact below ``root``."""

    api_manifest = build_api_manifest()
    ui_manifest = build_ui_manifest(api_manifest)
    status = build_status(api_manifest, ui_manifest)
    coverage = root / "coverage"
    write_json(coverage / "api_v2_manifest.yaml", api_manifest)
    write_json(coverage / "ui_workflows_manifest.yaml", ui_manifest)
    write_json(coverage / "browser_egress.yaml", build_browser_egress())
    write_json(coverage / "status.json", status)
    (coverage / "report.md").write_text(render_report(status), encoding="utf-8")
    return status


def main() -> int:
    """Generate the checked-in artifacts."""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true", help="deprecated compatibility flag")
    parser.parse_args()
    status = generate(ROOT)
    print(
        "Generated coverage: "
        f"{status['source_counts']['api_total']} API rows, "
        f"{status['source_counts']['ui_total']} UI rows, complete={status['complete']}."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
