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
DOCS_ETAG = "hsisik4g9p3603"
DOCS_MD5 = "c2efda0ee4cf9cf200e14910c5fc6996"
CURRENT_COVERAGE_PHASE = "phase_1_offline_api_reads_and_writes"
TEST_REFERENCE = "tests/coverage/test_coverage_inventory.py"
SERVER_REGISTRY_TEST_REFERENCE = "tests/unit/test_coverage_server.py"
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
                "test_references": [TEST_REFERENCE],
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
                "browser_action": "deny",
                "api_client_action": "exclusive_allow",
                "owner": "api_client",
                "purpose": "Locked official API client destination",
                "condition": "not available to browser lane",
                "evidence": "Approved design §11.1 and frozen brief §3",
                "test_references": [TEST_REFERENCE],
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
    if any(row.get("live_tested") is not True for row in [*api_rows, *ui_rows]):
        return "BILLY_API_TOKEN is unavailable; no live or UI qualification is claimed"
    if any(row.get("source_kind") == "ambiguous_bulk" for row in api_rows):
        return "Unresolved ambiguous bulk contracts prevent a completeness claim"
    if any(row.get("vision_verified") is not True for row in ui_rows):
        return "UI vision verification is incomplete"
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
    state_summary = (
        "This generated inventory currently satisfies the manifest qualification rules."
        if status["complete"]
        else (
            "This generated inventory is currently incomplete. It freezes the official-doc "
            "snapshot with row-level implementation and contract-test evidence, without asserting "
            "live testing or vision verification."
        )
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
