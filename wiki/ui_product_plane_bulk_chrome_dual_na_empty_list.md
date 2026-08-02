---
name: ui_product_plane_bulk_chrome_dual_na_empty_list
title: UI product-plane bulk chrome dual not_applicable (empty list shells)
desc: Research190 dual-absent multi-select bulk chrome on real greened empty list shells — 5 resources / 10 UI bulk parity rows not_applicable; empty tool; not product ACCEPT; complete stays false.
tags: [billy, ui, bulk, parity, dual, not_applicable, research190, empty_list]
sources:
  - https://www.billy.dk/api/
  - docs/superpowers/specs/2026-07-28-billy-mcp-complete-design.md
  - wiki/ui_product_plane_bulk_parity_inventory_honesty.md
  - wiki/ui_product_plane_bulk_chrome_dual_na_strong.md
  - wiki/ui_product_plane_bulk_chrome_dual_na_soft_tool.md
  - .fractal/main.billy_complete/tmp/research190_empty_shell_dual.json
created: 2026-08-02T17:10:00Z
updated: 2026-08-02T17:10:00Z
---

# UI product-plane bulk chrome dual not_applicable (empty list shells)

## Authority and scope

Research190 dual-session survey of multi-select / bulk-action chrome on greened Billy empty list shells for the last product-plane API bulk parity honesty rows (contacts / invoices / bills + lines).

Official docs fingerprint MD5 `8b94b0135c91fd15fe54ea33e088a4be`, ETag `wcw4x9hqvu3603` (unchanged). API bulk schema remains unspecified (`BULK_SCHEMA_UNSPECIFIED_OFFICIAL_DOCS`). Live API out of scope.

This page is **not**:

- product ACCEPT for bulk FastMCP tools
- greening of API bulk ×92
- list-tool signature repair for empty org data (`UI_CHANGED` on greened list tools)
- a completeness claim (`complete` stays false)

It **is** design §10.2 UI `not_applicable` for the **empty-list dual-absent** subset only. Completes product-plane UI bulk honesty freezes after [[ui_product_plane_bulk_chrome_dual_na_strong]] and [[ui_product_plane_bulk_chrome_dual_na_soft_tool]].

## Empty-list set (5 resources / 10 UI rows)

For each resource below: `ui.parity.<R>.bulk_save` and `ui.parity.<R>.bulk_delete`.

contacts, invoices, invoiceLines, bills, billLines

### Inventory fields applied

- `tool_name` empty
- `discovered` / `implemented` / `contract_tested` / `live_tested` / `vision_verified` true (NA bookkeeping)
- `parity_status=not_applicable`
- `qualification.kind=ui_not_applicable`
- `qualification.evidence_code=UI_BULK_CHROME_ABSENT_DUAL_EMPTY_LIST`
- `qualification.sessions=dual_independent_ephemeral`
- `qualification.evidence_ref=research190_empty_shell_dual`
- `qualification.empty_list_shell=true`
- `qualification.tool_panel=false`
- linked API bulk rows stay red / toolless / `external_contract_blocker`

### Shell mapping (dual READY/READY, no writes)

| Resources | Shell | Path class | Tool ref (evidence) |
| --- | --- | --- | --- |
| contacts | clients_list | `/clients/empty` | `ui_clients_list` |
| invoices, invoiceLines | invoices_list | `/invoices/empty` | `ui_invoices_list` |
| bills, billLines | bills_list | `/bills/empty` | `ui_bills_list` |

Real empty-state shells (h1 Kontakter/Fakturaer/Køb + “Ingen …” copy) are distinct from nonsense soft-empty control (body_len 127, no h1). Dual metrics: tables 0, rows 0, checkboxes 0, bulk chrome absent.

Greened list tools may return `UI_CHANGED` on empty org data (signature drift). That is a separate product issue and does not invent bulk chrome; dual direct navigation is the primary evidence.

## Completeness walls still open

| Blocker | Rows |
| --- | ---: |
| API bulk schema unspecified | 92 |
| Residual clear honesty | 29 |
| UI product-plane bulk honesty | **0** |
| annual_reports org inaccessible | 1 |

Green counts after this freeze: implemented/contract **528**, live/vision **344**, complete **false**.

## Generator and tests

- `scripts/generate_coverage_report.py`: `apply_ui_product_plane_bulk_chrome_dual_na_empty_list` after soft dual-NA apply
- `tests/coverage/test_coverage_inventory.py`: `test_ui_product_plane_bulk_chrome_dual_na_empty_list_rows`
