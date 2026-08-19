---
name: residual_clear_method_closed_inventory_honesty
title: Residual clear method-closed inventory honesty freeze
desc: Residual clear API write honesty. 26 toolless rows remain after ticketed bankPayments.delete. Not completeness.
tags: [billy, api, residual, method-closed, inventory, honesty, research186]
sources:
  - https://www.billy.dk/api/
  - docs/superpowers/specs/2026-07-28-billy-mcp-complete-design.md
  - wiki/offline_write_probe_rules.md
  - .fractal/main.billy_complete/tmp/grok-research.md
  - .fractal/main.billy_complete/tmp/research186_residual_unauth.json
  - src/billy_mcp/live_probe.py
created: 2026-08-02T14:20:00Z
updated: 2026-08-20T00:30:00Z
---

# Residual clear method-closed inventory honesty freeze

## Authority and scope

Research186 inventory honesty for residual clear official write rows that stay red. Current remaining set is **26** (22 method-closed, 2 readonly-map, 2 meta-delete). `api.accountNatures.create` and `api.accountNatures.update` left this freeze: official `#v2accountnatures` still lists create/update with writable `reportType`, `name`, and `normalBalance`. `api.bankPayments.delete` also left this freeze: official `#v2bankpayments` still lists singular delete, so it is a ticketed offline tool (`api_bank_payments_delete_preview`) with no request body. Live API stays `out_of_scope_by_user`. Official docs fingerprint is ETag `tmhc6wpdc835zt`, MD5 `053f755f52e3926b028e29325e3670d4`.

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
| HTTP **405** `METHOD_NOT_ALLOWED` (historical research186 class) | 25 then, **22** remaining | `method_closed_offline` | `METHOD_NOT_ALLOWED_UNAUTH` |
| HTTP **401** `AUTHENTICATION_REQUIRED` on transactions create/update | 2 | `readonly_field_map_insufficient` | `READONLY_PROPERTY_TABLE` |
| HTTP **200** meta-only on two singular deletes | 2 | `meta_delete_unqualified` | `META_DELETE_NOT_CLEANUP_PROOF` |

Parity with `live_probe._RESEARCH96_RESIDUAL_OUTCOMES`. research191 unauth reconfirm (2026-08-02) matched the same 405/401/meta-200 classes (`tmp/research191_unauth_reconfirm.json`). Live API qualification remains `out_of_scope_by_user`.

## Inventory rules applied

For every residual id in `RESIDUAL_CLEAR_HONESTY_IDS`:

- `tool_name` is empty
- `implemented`, `contract_tested`, and `live_tested` stay false
- `source_kind` stays `clear` (not reclassified as `ambiguous_bulk`)
- `qualification.tools_allowed` is false
- `qualification.live_api` is `out_of_scope_by_user`

### Method-closed (22 remaining)

Supports still lists these writes. Unauthenticated 405 is not the contract. Rows stay toolless here only when the official property table has no writable field map, or the slice has not landed yet. `accountNatures` create/update and `bankPayments.delete` are no longer in this set.

### Readonly field map (2)

`api.transactions.create` and `api.transactions.update` open at the unauth auth gate (401) but the official property table is effectively readonly. Do not freeze tools from Supports alone.

### Meta delete unqualified (2)

`api.transactions.delete` and `api.invoiceReminderAssociations.delete` return unauth 200 meta-only for a missing id. That matches the docs' idempotent-delete narrative and is **not** cleanup proof.

API live-test cells stay false with `live_api=out_of_scope_by_user`
([[api_live_qualification_semantics]]). That is not this freeze.

## Completeness walls still open

| Blocker | Rows |
| --- | --- |
| Bulk schema unspecified (`external_contract_blocker`) | 92 API |
| UI product-plane bulk discovery_required ([[ui_product_plane_bulk_parity_inventory_honesty]]) | 58 UI |
| Residual clear honesty (this freeze, still red) | 26 API |
| annual_reports org inaccessible | 1 UI discovery |

Generated snapshot after ticketed `bankPayments.delete`: implemented **526**, contract **531**, live/vision **339**, complete **false**. Historical research186 freeze snapshot was implemented/contract **470**, live/vision **286**.

## Generator and tests

- `scripts/generate_coverage_report.py`: `apply_residual_clear_honesty`, frozensets, qualification builders
- `tests/coverage/test_coverage_inventory.py`: `test_residual_clear_honesty_rows_are_toolless_and_qualified`

## research192 unauth reconfirm (2026-08-02)

Offline docs fingerprint unchanged (MD5 `8b94b0135c91fd15fe54ea33e088a4be`, ETag `wcw4x9hqvu3603`).
Unauth residual matrix reconfirmed on locked base only (no token): method-closed **405**, transactions create/update **401**, meta deletes **200** meta-only.
Inventory `evidence_ref` chain now ends with `research192_unauth_reconfirm`. Still `tools_allowed=false`; not greening; not product ACCEPT; complete stays false.
Scratch: `.fractal/main.billy_complete/tmp/research192_unauth_reconfirm.json` (owner-only).

## research193 stop-churn (2026-08-02)

Official docs fingerprint re-checked only (no residual unauth matrix this pass; parent STEER stops citation-only reconfirm packages after research192):

| Signal | Result |
| --- | --- |
| Docs MD5 / ETag / bytes | `8b94b0135c91fd15fe54ea33e088a4be` / `wcw4x9hqvu3603` / 147934 — **match lock** |
| OpenAPI/Swagger paths on billy.dk | all **404** |
| api-docs page chunk | Supports-line bulk wording only; no bulk body schema |
| Unauth residual re-probe | **not run** (no new contract finding expected; no `evidence_ref` bump) |

Residual **26** stay red and toolless (`tools_allowed=false`). Inventory `evidence_ref` remains ending at `research192_unauth_reconfirm`. Not greening; not product ACCEPT; complete stays false.

### Current external walls (counts after product-plane UI bulk honesty closed)

| Blocker | Rows |
| --- | ---: |
| Bulk schema unspecified | 92 API |
| Residual clear honesty (this freeze) | 26 API |
| annual_reports org inaccessible | 1 UI discovery |
| Product-plane UI bulk parity | **0** open (dual-NA freezes closed) |

Generated coverage snapshot at research193: implemented/contract **528**, live/vision **344**, complete **false**. Current generated snapshot after ticketed `bankPayments.delete`: implemented **526**, contract **531**, live/vision **339**, complete **false**. The live/vision drop versus research193 is later honesty remaps, not this freeze.

Unlock residual tools only when official docs correct the method map or authenticated non-production write proof is in scope (live API remains `out_of_scope_by_user`).
