---
name: residual_clear_method_closed_inventory_honesty
title: Residual clear method-closed inventory honesty freeze
desc: Research186 inventory honesty for 29 residual clear API write rows — empty tool names and method-gate qualifications; not product ACCEPT, not greening, not completeness.
tags: [billy, api, residual, method-closed, inventory, honesty, research186]
sources:
  - https://www.billy.dk/api/
  - docs/superpowers/specs/2026-07-28-billy-mcp-complete-design.md
  - wiki/offline_write_probe_rules.md
  - .fractal/main.billy_complete/tmp/grok-research.md
  - .fractal/main.billy_complete/tmp/research186_residual_unauth.json
  - src/billy_mcp/live_probe.py
created: 2026-08-02T14:20:00Z
updated: 2026-08-02T14:20:00Z
---

# Residual clear method-closed inventory honesty freeze

## Authority and scope

Research186 inventory honesty for the **29 residual clear** official write rows that remain red after offline product waves. Official docs fingerprint MD5 `8b94b0135c91fd15fe54ea33e088a4be`, ETag `wcw4x9hqvu3603` (unchanged).

This page is **not**:

- product ACCEPT for ticketed write tools
- greening of `implemented` / `contract_tested` / `live_tested`
- bulk resolution
- annual_reports resolution
- a completeness claim (`complete` stays false)

It **is** the durable record that inventory no longer advertises non-existent `*_preview` tool names for these rows, and that each row carries a machine-readable qualification aligned with [[offline_write_probe_rules]].

## Unauth residual matrix (research186)

Locked base `https://api.billysbilling.com/v2`, no token:

| Class | Count | Qualification kind | Blocker code |
| --- | ---: | --- | --- |
| HTTP **405** `METHOD_NOT_ALLOWED` | 25 | `method_closed_offline` | `METHOD_NOT_ALLOWED_UNAUTH` |
| HTTP **401** `AUTHENTICATION_REQUIRED` on transactions create/update | 2 | `readonly_field_map_insufficient` | `READONLY_PROPERTY_TABLE` |
| HTTP **200** meta-only on two singular deletes | 2 | `meta_delete_unqualified` | `META_DELETE_NOT_CLEANUP_PROOF` |

Parity with `live_probe._RESEARCH96_RESIDUAL_OUTCOMES`. Live API qualification remains `out_of_scope_by_user`.

## Inventory rules applied

For every residual id in `RESIDUAL_CLEAR_HONESTY_IDS`:

- `tool_name` is empty
- `implemented`, `contract_tested`, and `live_tested` stay false
- `source_kind` stays `clear` (not reclassified as `ambiguous_bulk`)
- `qualification.tools_allowed` is false
- `qualification.live_api` is `out_of_scope_by_user`

### Method-closed (25)

Supports create/update (or bankPayments singular delete) is overridden by unauth 405. No ticketed tools until official docs change or authenticated non-production proof (the latter is out of user-approved live API scope).

### Readonly field map (2)

`api.transactions.create` and `api.transactions.update` open at the unauth auth gate (401) but the official property table is effectively readonly. Do not freeze tools from Supports alone.

### Meta delete unqualified (2)

`api.transactions.delete` and `api.invoiceReminderAssociations.delete` return unauth 200 meta-only for a missing id. That matches the docs' idempotent-delete narrative and is **not** cleanup proof.

## Completeness walls still open

| Blocker | Rows |
| --- | --- |
| Bulk schema unspecified (`external_contract_blocker`) | 92 API |
| UI product-plane bulk discovery_required ([[ui_product_plane_bulk_parity_inventory_honesty]]) | 58 UI |
| Residual clear honesty (this freeze, still red) | 29 API |
| annual_reports org inaccessible | 1 UI discovery |

Green counts after this freeze: implemented/contract **470**, live/vision **286**, complete **false**.

## Generator and tests

- `scripts/generate_coverage_report.py`: `apply_residual_clear_honesty`, frozensets, qualification builders
- `tests/coverage/test_coverage_inventory.py`: `test_residual_clear_honesty_rows_are_toolless_and_qualified`
