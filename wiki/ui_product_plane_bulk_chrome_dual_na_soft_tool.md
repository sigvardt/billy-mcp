---
name: ui_product_plane_bulk_chrome_dual_na_soft_tool
title: UI product-plane bulk chrome dual not_applicable (soft tool panels)
desc: Research189 dual-absent multi-select bulk chrome on real greened tool panels — 9 resources / 18 UI bulk parity rows not_applicable; empty tool; not product ACCEPT; complete stays false.
tags: [billy, ui, bulk, parity, dual, not_applicable, research189]
sources:
  - https://www.billy.dk/api/
  - docs/superpowers/specs/2026-07-28-billy-mcp-complete-design.md
  - wiki/ui_product_plane_bulk_parity_inventory_honesty.md
  - wiki/ui_product_plane_bulk_chrome_dual_na_strong.md
  - .fractal/main.billy_complete/tmp/research189_bulk_followon_dual.json
created: 2026-08-02T16:20:00Z
updated: 2026-08-02T16:20:00Z
---

# UI product-plane bulk chrome dual not_applicable (soft tool panels)

## Authority and scope

Research189 dual-session survey of multi-select / bulk-action chrome on greened Billy tool panels for the soft VAT/users product-plane API bulk parity rows that research188 left honesty-red (soft SPA seeds soft-empty).

Official docs fingerprint MD5 `8b94b0135c91fd15fe54ea33e088a4be`, ETag `wcw4x9hqvu3603` (unchanged). API bulk schema remains unspecified (`BULK_SCHEMA_UNSPECIFIED_OFFICIAL_DOCS`). Live API out of scope.

This page is **not**:

- product ACCEPT for bulk FastMCP tools
- greening of API bulk ×92
- NA of empty-shell contacts/invoices/bills bulk rows
- a completeness claim (`complete` stays false)

It **is** design §10.2 UI `not_applicable` for the **soft tool dual-absent** subset only.

## Soft set (9 resources / 18 UI rows)

For each resource below: `ui.parity.<R>.bulk_save` and `ui.parity.<R>.bulk_delete`.

salesTaxAccounts, salesTaxMetaFields, salesTaxPayments, salesTaxReturns, salesTaxRules, salesTaxRulesets, taxRateDeductionComponents, taxRates, users

### Inventory fields applied

- `tool_name` empty
- `discovered` / `implemented` / `contract_tested` / `live_tested` / `vision_verified` true (NA bookkeeping)
- `parity_status=not_applicable`
- `qualification.kind=ui_not_applicable`
- `qualification.evidence_code=UI_BULK_CHROME_ABSENT_DUAL_TOOL_PANEL`
- `qualification.sessions=dual_independent_ephemeral`
- `qualification.evidence_ref=research189_bulk_followon_dual`
- `qualification.empty_list_shell=false`
- `qualification.tool_panel=true`
- linked API bulk rows stay red / toolless / `external_contract_blocker`

### Panel mapping (dual READY/READY tool success + re-open metrics, no writes)

| Resources | Panel / tool | Path class |
| --- | --- | --- |
| taxRates, taxRateDeductionComponents, salesTaxRules, salesTaxRulesets, salesTaxAccounts, salesTaxMetaFields, salesTaxPayments | `ui_settings_vat_open` (Momssatser) | `/settings` |
| users | `ui_settings_users_open` (Brugere) | `/settings` |
| salesTaxReturns | `ui_vat_declarations_list` (Momsangivelser) | `/vat-declarations` |

Bare SPA seeds `/settings/vat`, `/settings/users`, `/vat-returns` remain soft-empty (research188). Tool open is required. VAT panel preference toggles are not row multi-select bulk chrome.

## Held (still discovery_required honesty)

| Subset | Resources | Why |
| --- | --- | --- |
| Empty-shell dual-absent | contacts, invoices, invoiceLines, bills, billLines | **Promoted by research190** empty-list dual-NA ([[ui_product_plane_bulk_chrome_dual_na_empty_list]]) |

Product-plane UI bulk honesty remaining after empty-list package: **0**. Strong dual-NA ×30 remains separate ([[ui_product_plane_bulk_chrome_dual_na_strong]]).

## Completeness walls still open

| Blocker | Rows |
| --- | ---: |
| API bulk schema unspecified | 92 |
| Residual clear honesty | 29 |
| UI product-plane bulk remaining honesty | 0 |
| annual_reports org inaccessible | 1 |

Green counts after soft freeze alone: implemented/contract **518**, live/vision **334**. After empty-list package: **528** / **344**. complete **false**.

## Generator and tests

- `scripts/generate_coverage_report.py`: `apply_ui_product_plane_bulk_chrome_dual_na_soft_tool` after strong dual-NA apply
- `tests/coverage/test_coverage_inventory.py`: `test_ui_product_plane_bulk_chrome_dual_na_soft_tool_rows`
