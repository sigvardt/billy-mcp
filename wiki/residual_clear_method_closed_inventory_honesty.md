---
name: residual_clear_method_closed_inventory_honesty
title: Residual clear method-closed inventory honesty freeze
desc: Residual clear API write honesty. 6 toolless readonly-map rows remain. Not completeness.
tags: [billy, api, residual, method-closed, inventory, honesty, research186]
sources:
  - https://www.billy.dk/api/
  - docs/superpowers/specs/2026-07-28-billy-mcp-complete-design.md
  - wiki/offline_write_probe_rules.md
  - .fractal/main.billy_complete/tmp/grok-research.md
  - .fractal/main.billy_complete/tmp/research186_residual_unauth.json
  - src/billy_mcp/live_probe.py
  - radio:A485F530
created: 2026-08-02T14:20:00Z
updated: 2026-08-20T11:35:00Z
---

# Residual clear method-closed inventory honesty freeze

## Authority and scope

Research186 inventory honesty for residual clear official write rows that stay red. Current remaining set is **6**, all `readonly_field_map_insufficient`. Method-closed remaining is **0**. `api.contactBalancePostings.create` / `.update` and `api.postings.create` / `.update` left the method-closed set: official Supports still lists create/update, but A485F530 found no writable official field map (property tables all readonly or immutable; first-party bundles GET only). Historical unauth 405 is not the contract. `api.accountNatures.create` and `api.accountNatures.update` left this freeze: official `#v2accountnatures` still lists create/update with writable `reportType`, `name`, and `normalBalance`. `api.bankPayments.delete` also left this freeze: official `#v2bankpayments` still lists singular delete, so it is a ticketed offline tool (`api_bank_payments_delete_preview`) with no request body. `api.invoiceReminderAssociations.create` and `api.invoiceReminderAssociations.update` left this freeze: official `#v2invoicereminderassociations` still lists create/update with required `reminder` and `invoice`. `api.invoiceReminderAssociations.delete` left this freeze: official `#v2invoicereminderassociations` still lists singular delete, so it is a ticketed offline tool (`api_invoice_reminder_associations_delete_preview`) with no request body. `api.transactions.delete` left this freeze: official `#v2transactions` still lists singular delete with path `id` and no delete body, so it is a ticketed offline tool (`api_transactions_delete_preview`) with no request body. Historical unauth missing-id DELETE 200 is not cleanup proof and is not the contract. `api.cities.create` and `api.cities.update` left this freeze: official `#v2cities` still lists create/update with optional `name`, `county`, `state`, and `country`. `api.countryGroups.create` and `api.countryGroups.update` left this freeze: official `#v2countrygroups` still lists create/update with optional string `name`, `icon`, and `memberCountryIds`. `api.countries.create` and `api.countries.update` left this freeze: official `#v2countries` still lists create/update with optional string `name`, boolean `hasStates`, `hasFiniteStates`, `hasFiniteZipcodes`, string `icon`, and belongs-to `locale`. `api.currencies.create` and `api.currencies.update` left this freeze: official `#v2currencies` still lists create/update with optional string `name` and float `exchangeRate`. `api.locales.create` and `api.locales.update` left this freeze: official `#v2locales` still lists create/update with optional string `name` and `icon`. `api.states.create` and `api.states.update` left this freeze: official `#v2states` still lists create/update with optional string `stateCode`, `name`, and belongs-to `country`. `api.zipcodes.create` and `api.zipcodes.update` left this freeze: official `#v2zipcodes` still lists create/update with optional string `zipcode`, belongs-to `city`/`state`/`country`, and float `latitude`/`longitude`. `api.balanceModifiers.create` and `api.balanceModifiers.update` left this freeze: official `#v2balancemodifiers` still lists create/update with required belongs-to-reference `modifier` and `subject`. Live API stays `out_of_scope_by_user`. Official docs fingerprint is ETag `tmhc6wpdc835zt`, MD5 `053f755f52e3926b028e29325e3670d4`.

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
| HTTP **405** `METHOD_NOT_ALLOWED` (historical research186 class) | 25 then, **0** remaining as method-closed | `method_closed_offline` | `METHOD_NOT_ALLOWED_UNAUTH` |
| Official property table has no writable create/update field (A485F530) | **6** | `readonly_field_map_insufficient` | `READONLY_PROPERTY_TABLE` |
| HTTP **200** meta-only on two singular deletes | 2 then, **0** remaining | `meta_delete_unqualified` | `META_DELETE_NOT_CLEANUP_PROOF` |

Parity with `live_probe._RESEARCH96_RESIDUAL_OUTCOMES`. research191 unauth reconfirm (2026-08-02) matched the same 405/401/meta-200 classes (`tmp/research191_unauth_reconfirm.json`). Live API qualification remains `out_of_scope_by_user`.

## Inventory rules applied

For every residual id in `RESIDUAL_CLEAR_HONESTY_IDS`:

- `tool_name` is empty
- `implemented`, `contract_tested`, and `live_tested` stay false
- `source_kind` stays `clear` (not reclassified as `ambiguous_bulk`)
- `qualification.tools_allowed` is false
- `qualification.live_api` is `out_of_scope_by_user`

### Method-closed (0 remaining)

Supports still lists writes that historically returned unauth 405. Unauthenticated 405 is not the contract. Rows stay toolless here only when the official property table has no writable field map, or the slice has not landed yet. `accountNatures` create/update, `bankPayments.delete`, `invoiceReminderAssociations` create/update/delete, `cities` create/update, `countryGroups` create/update, `countries` create/update, `currencies` create/update, `locales` create/update, `states` create/update, `zipcodes` create/update, `balanceModifiers` create/update, `transactions.delete`, `contactBalancePostings` create/update, and `postings` create/update are no longer in this set.

### Readonly field map (6)

`api.contactBalancePostings.create` / `.update`, `api.postings.create` / `.update`, and `api.transactions.create` / `.update`. Official Supports lists create/update. Official property tables have no non-readonly field. First-party bundles expose GET only. Do not freeze tools from Supports alone. Historical unauth 405/401 is not the contract and is not stored as `unauth_status`.

### Meta delete unqualified (0 remaining)

`api.invoiceReminderAssociations.delete` and `api.transactions.delete` left this freeze: official Supports lists singular delete with path `id` and no delete body, so both are ticketed offline tools. The historical unauth missing-id DELETE 200 is not cleanup proof and is not the contract.

API live-test cells stay false with `live_api=out_of_scope_by_user`
([[api_live_qualification_semantics]]). That is not this freeze.

## Completeness walls still open

| Blocker | Rows |
| --- | --- |
| Bulk schema unspecified (`external_contract_blocker`) | 92 API |
| UI product-plane bulk discovery_required ([[ui_product_plane_bulk_parity_inventory_honesty]]) | 58 UI |
| Residual clear honesty (this freeze, still red) | 6 API |
| annual_reports org inaccessible | 1 UI discovery |

Generated snapshot after the A485F530 readonly-map remap: implemented **546**, contract **551**, live/vision **339**, complete **false**. Historical research186 freeze snapshot was implemented/contract **470**, live/vision **286**.

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

Residual **20** stay red and toolless (`tools_allowed=false`). Inventory `evidence_ref` remains ending at `research192_unauth_reconfirm`. Not greening; not product ACCEPT; complete stays false.

### Current external walls (counts after product-plane UI bulk honesty closed)

| Blocker | Rows |
| --- | ---: |
| Bulk schema unspecified | 92 API |
| Residual clear honesty (this freeze) | 20 API |
| annual_reports org inaccessible | 1 UI discovery |
| Product-plane UI bulk parity | **0** open (dual-NA freezes closed) |

Generated coverage snapshot at research193: implemented/contract **528**, live/vision **344**, complete **false**. Current generated snapshot after ticketed `countryGroups` create/update: implemented **532**, contract **537**, live/vision **339**, complete **false**. The live/vision drop versus research193 is later honesty remaps, not this freeze.

Unlock residual tools only when official docs correct the method map or authenticated non-production write proof is in scope (live API remains `out_of_scope_by_user`).
