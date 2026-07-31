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
# Official docs fingerprint reconfirmed 2026-07-31 (research100 / independent review).
DOCS_ETAG = "wcw4x9hqvu3603"
DOCS_MD5 = "8b94b0135c91fd15fe54ea33e088a4be"
CURRENT_COVERAGE_PHASE = "phase_1_offline_api_reads_and_writes"
TEST_REFERENCE = "tests/coverage/test_coverage_inventory.py"
SERVER_REGISTRY_TEST_REFERENCE = "tests/unit/test_coverage_server.py"
UI_INVOICES_LIST_UNIT_TEST_REFERENCE = "tests/unit/test_browser.py"
UI_INVOICES_LIST_LIVE_TEST_REFERENCE = "tests/live/test_ui_invoices_list.py"
UI_INVOICES_LIST_MODEL_TEST_REFERENCE = "tests/test_models.py"
UI_INVOICES_LIST_TOOL_NAME = "ui_invoices_list"
UI_PRODUCTS_LIST_UNIT_TEST_REFERENCE = "tests/unit/test_browser.py"
UI_PRODUCTS_LIST_LIVE_TEST_REFERENCE = "tests/live/test_ui_products_list.py"
UI_PRODUCTS_LIST_MODEL_TEST_REFERENCE = "tests/test_models.py"
UI_PRODUCTS_LIST_TOOL_NAME = "ui_products_list"
UI_CLIENTS_LIST_UNIT_TEST_REFERENCE = "tests/unit/test_browser.py"
UI_CLIENTS_LIST_LIVE_TEST_REFERENCE = "tests/live/test_ui_clients_list.py"
UI_CLIENTS_LIST_MODEL_TEST_REFERENCE = "tests/test_models.py"
UI_CLIENTS_LIST_TOOL_NAME = "ui_clients_list"
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
UI_SETTINGS_VAT_OPEN_UNIT_TEST_REFERENCE = "tests/unit/test_browser.py"
UI_SETTINGS_VAT_OPEN_LIVE_TEST_REFERENCE = "tests/live/test_ui_settings_vat_open.py"
UI_SETTINGS_VAT_OPEN_MODEL_TEST_REFERENCE = "tests/test_models.py"
UI_SETTINGS_VAT_OPEN_TOOL_NAME = "ui_settings_vat_open"
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
    "quotes",
    "recurring_invoices",
    "products",
    "product_import",
    "customers",
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
API_QUALIFICATION_FIELDS = ("discovered", "implemented", "contract_tested", "live_tested")
UI_QUALIFICATION_FIELDS = (*API_QUALIFICATION_FIELDS, "vision_verified")

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


def bulk_rows(resource: str) -> list[dict[str, Any]]:
    """Build the two deliberately unimplemented bulk mentions for a resource."""

    area = snake_case(resource)
    route = f"/v2/{resource}"
    return [
        base_api_row(
            row_id=f"api.{resource}.bulk_save",
            area=area,
            operation="bulk_save",
            method_or_route=f"AMBIGUOUS Supports: bulk save {route}",
            request_fields=[],
            response_fields=[],
            filters=[],
            pagination=None,
            side_effects=(
                "unknown until method, body, partial failures, and limits are live-qualified"
            ),
            cleanup="unknown until the bulk contract is qualified on a non-production organisation",
            tool_name="",
            source_kind="ambiguous_bulk",
            contract_status="ambiguous_bulk",
        ),
        base_api_row(
            row_id=f"api.{resource}.bulk_delete",
            area=area,
            operation="bulk_delete",
            method_or_route=f"AMBIGUOUS Supports: bulk delete {route}",
            request_fields=[],
            response_fields=[],
            filters=[],
            pagination=None,
            side_effects=(
                "unknown until method, identifiers, partial failures, and limits are live-qualified"
            ),
            cleanup="unknown until the bulk contract is qualified on a non-production organisation",
            tool_name="",
            source_kind="ambiguous_bulk",
            contract_status="ambiguous_bulk",
        ),
    ]


def special_rows() -> list[dict[str, Any]]:
    """Build the six separately documented prose routes without inventing more."""

    return [
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


def build_api_manifest() -> dict[str, Any]:
    """Return the complete 305-operation official snapshot."""

    operations: list[dict[str, Any]] = []
    for resource, create, update, delete in RESOURCE_SUPPORTS:
        operations.extend(standard_rows(resource, create, update, delete))
        operations.extend(bulk_rows(resource))
    operations.extend(special_rows())
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


def apply_ui_uploads_list_shell_evidence(row: dict[str, Any]) -> None:
    """Mark uploads (Bilag) list **shell open** evidence only (research113 / plan 186.14).

    Empty-input tool; path /uploads, h1 Bilag, CTA Upload filer present only (never click;
    never set file inputs). No official /v2/uploads resource — discovery only.
    Does not green receipt_inbox or files/attachments/files_upload parity.
    """

    row["method_or_route"] = "mit.billy.dk /:org_slug/uploads (read-only list shell open)"
    row["tool_name"] = UI_UPLOADS_LIST_TOOL_NAME
    row["request_fields"] = []
    row["response_fields"] = [
        "path_class",
        "heading",
        "upload_action_visible",
        "shell_markers_present",
    ]
    row["filters"] = []
    row["pagination"] = None
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
        "list shell only (path class /:org_slug/uploads, h1 Bilag, CTA Upload filer "
        "present, no file pick); no invent api_uploads_*/api_bilag_*; "
        "aliases upload/bilag/files/inbox/attachments/receipts rejected; "
        "does not green receipt_inbox, files*, attachments*, special.files_upload; "
        "API list filters/sort/pagination UI not producted; "
        "vision record tmp/vision-records/ui_uploads_list.json "
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


def apply_ui_daybooks_open_shell_evidence(row: dict[str, Any]) -> None:
    """Mark daybooks **editor shell open** evidence only (research117).

    Empty-input tool; path /:org_slug/daybooks/new; editor markers (no h1).
    Bare /daybooks is Upsedasse (not success). No invent API tools.
    Never click create/add-line/post. Does not green transactions discovery.
    """

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
        "green ui.discovery.transactions or daybook* parity; vision record "
        "tmp/vision-records/ui_daybooks_open.json (editor frames, accept)"
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


def apply_ui_transactions_list_shell_evidence(row: dict[str, Any]) -> None:
    """Mark transactions (Posteringer) list **shell open** evidence only (research118).

    Empty-input tool; path /:org_slug/transactions (query allowed); h1 Posteringer;
    CTA Ny postering observe-only. Nested /transactions/:segment is create shell
    (not list success). No invent API write tools. Does not green daybooks or
    transactions parity rows.
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
        "green daybooks or ui.parity.transactions.*; vision record "
        "tmp/vision-records/ui_transactions_list.json (list surface frames, accept)"
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


def apply_ui_vat_declarations_list_shell_evidence(row: dict[str, Any]) -> None:
    """Mark VAT declarations (Momsangivelser) list **shell open** evidence only (research120).

    Empty-input tool; path /:org_slug/vat-declarations; h1 Momsangivelser; Periode
    chrome; empty table body valid. Soft aliases rejected. No invent api_vat_*.
    Does not green annual/exports/settings discovery rows or re-scope salesTaxReturns.
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
        "does not green annual_reports/exports/settings or re-scope salesTaxReturns; "
        "vision record tmp/vision-records/ui_vat_declarations_list.json (list frames, accept)"
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


def apply_ui_settings_company_open_shell_evidence(row: dict[str, Any]) -> None:
    """Mark Indstillinger company settings shell open evidence (research126).

    Empty-input tool; path /:org_slug/settings; h1 Indstillinger; company panel
    markers Navn og adresse + Kontaktinformation. Soft nested aliases rejected.
    Never click Gem / Tilføj ejer / upload. No invent api_settings_*. Does not
    green other settings_* or annual_reports.
    """

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
        "settings_* or annual_reports; vision record "
        "tmp/vision-records/ui_settings_company_open.json (Indstillinger company frames, accept)"
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


def apply_ui_settings_accounting_open_shell_evidence(row: dict[str, Any]) -> None:
    """Mark Indstillinger Regnskab (accounting) panel shell open evidence (research127).

    Empty-input tool; request settings/accounting SPA seed; final path
    /:org_slug/settings; h1 Indstillinger; markers Regnskab + Køb + Kontoplan.
    Distinct from company default. Soft aliases rejected. Never click Gem /
    Sæt låsedato. No invent api_settings_*. Does not green other settings_* or
    annual_reports.
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
        "settings_* or annual_reports; vision record "
        "tmp/vision-records/ui_settings_accounting_open.json "
        "(Indstillinger Regnskab frames, accept)"
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


def apply_ui_settings_user_open_shell_evidence(row: dict[str, Any]) -> None:
    """Mark Indstillinger Profil (user) panel shell open evidence (research129).

    Empty-input tool; open hub /:org_slug/settings then observe-only click
    Profil; final path /:org_slug/settings; h1 Indstillinger; markers Profil +
    Billede + Sprog og tema + Skift adgangskode. Soft seeds rejected. Distinct
    from company/accounting/invoicing. Never click Gem / Upload / password
    submit. No invent api_settings_*. Does not green other settings_* or
    annual_reports.
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
        "other settings_* or annual_reports; vision record "
        "tmp/vision-records/ui_settings_user_open.json "
        "(Indstillinger Profil frames, accept)"
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


def apply_ui_settings_vat_open_shell_evidence(row: dict[str, Any]) -> None:
    """Mark Indstillinger Momssatser (VAT) panel shell open evidence (research130).

    Empty-input tool; open hub /:org_slug/settings then observe-only click
    Momssatser; final path /:org_slug/settings; h1 Indstillinger; markers
    Regelsæt + Satser for salg + Satser for køb. Soft seeds rejected. Distinct
    from company/accounting/invoicing/user. Never click Opret / Gem. No invent
    api_settings_*. Does not green other settings_* or annual_reports.
    """

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
        "or annual_reports; vision record "
        "tmp/vision-records/ui_settings_vat_open.json "
        "(Indstillinger Momssatser frames, accept)"
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
        if family == "products":
            apply_ui_products_list_shell_evidence(row, parity_of_api_list=False)
        if family == "customers":
            apply_ui_clients_list_shell_evidence(row, parity_of_api_list=False)
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
            apply_ui_daybooks_open_shell_evidence(row)
        if family == "transactions":
            apply_ui_transactions_list_shell_evidence(row)
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
        if family == "settings_vat":
            apply_ui_settings_vat_open_shell_evidence(row)
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
        if api_row["id"] == "api.products.list":
            apply_ui_products_list_shell_evidence(row, parity_of_api_list=True)
        if api_row["id"] == "api.contacts.list":
            apply_ui_clients_list_shell_evidence(row, parity_of_api_list=True)
        if api_row["id"] == "api.bills.list":
            apply_ui_bills_list_shell_evidence(row, parity_of_api_list=True)
        workflows.append(row)

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
                "purpose": "Path-scoped browser XHR for headless login and shell settle only",
                "condition": "browser auth/bootstrap paths only; never full API browse",
                "evidence": (
                    "research100 headless credentialed discovery: POST /v2/user/login "
                    "then bootstrap GETs reach /:org_slug/dashboard"
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
                    {"match": "prefix", "methods": ["GET"], "path": "/organizations/"},
                    {"match": "prefix", "methods": ["GET"], "path": "/e-invoicing/"},
                ],
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


def row_is_qualified(row: dict[str, Any], fields: tuple[str, ...]) -> bool:
    """Return whether a row satisfies every qualification state for its lane."""

    return all(row.get(field) is True for field in fields)


def coverage_is_complete(api_rows: list[dict[str, Any]], ui_rows: list[dict[str, Any]]) -> bool:
    """Derive a completeness claim from row evidence and unresolved bulk contracts."""

    return (
        bool(api_rows)
        and bool(ui_rows)
        and not any(row.get("source_kind") == "ambiguous_bulk" for row in api_rows)
        and all(row_is_qualified(row, API_QUALIFICATION_FIELDS) for row in api_rows)
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
            "Unresolved ambiguous bulk API contracts remain red; "
            "API live_tested stays false (out_of_scope_by_user); "
            "UI live and vision qualification incomplete"
        )
    if any(
        not row.get("implemented") or not row.get("contract_tested")
        for row in api_rows
        if row.get("source_kind") != "ambiguous_bulk"
    ):
        return "API offline implementation or contract evidence is incomplete"
    if any(not row.get("live_tested") for row in ui_rows) or any(
        row.get("vision_verified") is not True for row in ui_rows
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
