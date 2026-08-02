---
name: ui_product_plane_bulk_parity_inventory_honesty
title: UI product-plane bulk parity inventory honesty freeze
desc: Research187 inventory honesty for 58 product-plane UI bulk parity rows — discovery_required qualifications and empty tools; not product ACCEPT, not not_applicable, not greening, not completeness.
tags: [billy, ui, bulk, parity, inventory, honesty, research187]
sources:
  - https://www.billy.dk/api/
  - docs/superpowers/specs/2026-07-28-billy-mcp-complete-design.md
  - wiki/offline_write_probe_rules.md
  - wiki/residual_clear_method_closed_inventory_honesty.md
  - .fractal/main.billy_complete/tmp/grok-research.md
created: 2026-08-02T15:00:00Z
updated: 2026-08-02T15:35:00Z
---

# UI product-plane bulk parity inventory honesty freeze

## Authority and scope

Research187 inventory honesty for the **58 product-plane UI bulk parity** rows that remain red after non-bulk UI residual work. Official docs fingerprint MD5 `8b94b0135c91fd15fe54ea33e088a4be`, ETag `wcw4x9hqvu3603` (unchanged).

This page is **not**:

- product ACCEPT for bulk FastMCP tools
- greening of any UI qualification flag
- UI bulk `not_applicable` (dual bulk-chrome still required per design §10.2)
- API bulk schema resolution
- residual clear resolution
- annual_reports resolution
- a completeness claim (`complete` stays false)

It **is** the durable record that these 58 rows carry a machine-readable discovery-required qualification instead of only a generic design-mapping evidence string.

## Why product-plane bulk stays discovery_required

Design §10.2 allows UI `not_applicable` only when dual-session evidence shows Billy exposes **no** equivalent bulk workflow (no multi-select / bulk-action chrome) on the relevant greened list shell.

Inferring UI bulk NA solely from API `BULK_SCHEMA_UNSPECIFIED_OFFICIAL_DOCS` is **forbidden**. Research187 ran with browser credential refs unset, so dual bulk-chrome was not executed.

## Inventory rules applied

For every id in `UI_PRODUCT_PLANE_BULK_HONESTY_IDS` (29 resources × `bulk_save`/`bulk_delete` = 58):

- `tool_name` is empty
- `discovered`, `implemented`, `contract_tested`, `live_tested`, `vision_verified` stay false
- `parity_status` stays `discovery_required` (never forced to `not_applicable` by this freeze)
- `qualification.kind` is `ui_bulk_parity_discovery_required`
- `qualification.blocker_code` is `UI_BULK_CHROME_DUAL_REQUIRED`
- `qualification.tools_allowed` is false
- `qualification.api_bulk_blocker` is `BULK_SCHEMA_UNSPECIFIED_OFFICIAL_DOCS`
- `qualification.linked_api_row_id` points at the matching `api.<resource>.bulk_*` row
- `qualification.not_applicable_decision` is `deferred`

### Resources (29)

accounts, attachments, bankLineMatches, bankLineSubjectAssociations, bankLines, bankPayments, billLines, bills, contacts, daybookBalanceAccounts, daybookTransactionLines, daybookTransactions, daybooks, files, invoiceLines, invoices, organizations, postings, products, salesTaxAccounts, salesTaxMetaFields, salesTaxPayments, salesTaxReturns, salesTaxRules, salesTaxRulesets, taxRateDeductionComponents, taxRates, transactions, users

## Explicitly excluded

| Family | Treatment |
| --- | --- |
| Geo/reference UI bulk already dual-NA (e.g. accountGroups bulk_*) | Stay `parity_status=not_applicable`; not in this frozenset |
| API bulk ×92 | Stay `external_contract_blocker` ([[offline_write_probe_rules]]) |
| Residual clear ×29 | Stay research186 honesty ([[residual_clear_method_closed_inventory_honesty]]) |
| annual_reports | Stay org_inaccessible; NA rejected |

## Completeness walls still open

| Blocker | Rows |
| --- | ---: |
| Bulk schema unspecified (`external_contract_blocker`) | 92 API |
| Residual clear honesty (still red) | 29 API |
| UI product-plane bulk chrome dual required (remaining honesty) | 28 UI |
| UI product-plane bulk chrome dual NA strong (research188) | 30 UI |
| annual_reports org inaccessible | 1 UI discovery |

After research187 honesty alone: implemented/contract **470**, live/vision **286**. After research188 strong dual-NA: implemented/contract **500**, live/vision **316**, complete **false**.

## Unlock for UI bulk NA (follow-on)

Research188 dual survey landed: **15 resources / 30 rows** promoted to UI `not_applicable` (see [[ui_product_plane_bulk_chrome_dual_na_strong]]). Remaining **28** honesty rows: empty-shell contacts/invoices/bills (+lines) and soft VAT/users seeds. Still does not green API bulk 92.

## Generator and tests

- `scripts/generate_coverage_report.py`: `apply_ui_product_plane_bulk_parity_honesty`, frozensets, qualification builder
- `tests/coverage/test_coverage_inventory.py`: `test_ui_product_plane_bulk_parity_honesty_rows_are_toolless_and_qualified`
