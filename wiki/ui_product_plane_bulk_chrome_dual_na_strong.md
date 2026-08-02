---
name: ui_product_plane_bulk_chrome_dual_na_strong
title: UI product-plane bulk chrome dual not_applicable (strong subset)
desc: Research188 dual-absent multi-select bulk chrome on non-empty greened list shells — 15 resources / 30 UI bulk parity rows not_applicable; empty tool; not product ACCEPT; complete stays false.
tags: [billy, ui, bulk, parity, dual, not_applicable, research188]
sources:
  - https://www.billy.dk/api/
  - docs/superpowers/specs/2026-07-28-billy-mcp-complete-design.md
  - wiki/ui_product_plane_bulk_parity_inventory_honesty.md
  - .fractal/main.billy_complete/tmp/research188_bulk_chrome_dual.json
created: 2026-08-02T15:30:00Z
updated: 2026-08-02T15:30:00Z
---

# UI product-plane bulk chrome dual not_applicable (strong subset)

## Authority and scope

Research188 dual-session survey of multi-select / bulk-action chrome on greened Billy list/open shells for product-plane API bulk parity rows.

Official docs fingerprint MD5 `8b94b0135c91fd15fe54ea33e088a4be`, ETag `wcw4x9hqvu3603` (unchanged). API bulk schema remains unspecified (`BULK_SCHEMA_UNSPECIFIED_OFFICIAL_DOCS`). Live API out of scope.

This page is **not**:

- product ACCEPT for bulk FastMCP tools
- greening of API bulk ×92
- NA of empty-shell or soft VAT/users bulk rows
- a completeness claim (`complete` stays false)

It **is** design §10.2 UI `not_applicable` for the **strong** dual-absent subset only.

## Strong set (15 resources / 30 UI rows)

For each resource below: `ui.parity.<R>.bulk_save` and `ui.parity.<R>.bulk_delete`.

accounts, attachments, bankLineMatches, bankLineSubjectAssociations, bankLines, bankPayments, daybookBalanceAccounts, daybookTransactionLines, daybookTransactions, daybooks, files, organizations, postings, products, transactions

### Inventory fields applied

- `tool_name` empty
- `discovered` / `implemented` / `contract_tested` / `live_tested` / `vision_verified` true (NA bookkeeping)
- `parity_status=not_applicable`
- `qualification.kind=ui_not_applicable`
- `qualification.evidence_code=UI_BULK_CHROME_ABSENT_DUAL`
- `qualification.sessions=dual_independent_ephemeral`
- `qualification.evidence_ref=research188_bulk_chrome_dual`
- `qualification.empty_list_shell=false`
- linked API bulk rows stay red / toolless / `external_contract_blocker`

### Shell mapping (dual READY/READY, no writes)

| Resources | Shell | Path class |
| --- | --- | --- |
| products | products_list | `/products` |
| transactions, postings | transactions_list | `/transactions` |
| attachments, files | uploads_list | `/uploads` |
| bankLines, bankLineMatches, bankLineSubjectAssociations, bankPayments | bank_accounts_list | `/bank-accounts` |
| daybooks family | daybooks_open | `/daybooks/<id>` |
| accounts | settings_accounting | `/settings` |
| organizations | settings_company | `/settings` |

## Held after research188 (before research189 soft package)

| Subset | Resources | Why |
| --- | --- | --- |
| Empty-shell dual-absent | contacts, invoices, invoiceLines, bills, billLines | Dual landed on `/…/empty`; bulk chrome may appear when rows exist |
| Soft path seeds | salesTax*, taxRates*, taxRateDeductionComponents, users | Soft SPA seeds soft-empty; need tool-based dual |

Research189 promoted soft tool dual-absent ×18 to NA ([[ui_product_plane_bulk_chrome_dual_na_soft_tool]]). Empty-shell ×10 remain `UI_BULK_CHROME_DUAL_REQUIRED` (see [[ui_product_plane_bulk_parity_inventory_honesty]]).

## Completeness walls still open (after research189 soft package)

| Blocker | Rows |
| --- | ---: |
| API bulk schema unspecified | 92 |
| Residual clear honesty | 29 |
| UI product-plane bulk remaining honesty | 10 |
| annual_reports org inaccessible | 1 |

Green counts after strong freeze alone: implemented/contract **500**, live/vision **316**. After soft package: **518** / **334**. `complete` stays **false**.

## Generator and tests

- `scripts/generate_coverage_report.py`: `apply_ui_product_plane_bulk_chrome_dual_na_strong` after honesty apply
- `tests/coverage/test_coverage_inventory.py`: `test_ui_product_plane_bulk_chrome_dual_na_strong_rows`
