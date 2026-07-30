---
name: wave_fivei_product_ready_research_independent_review
title: Wave-5i product-ready research independent review ACCEPT
desc: Authoritative root Grok acceptance of the cited offline product-ready handoff for singular sales-tax account and meta-field ticketed writes under the accepted Wave-5i freeze.
tags: [billy, api, sales-tax, writes, review, coverage, research]
sources:
  - https://www.billy.dk/api/
  - wiki/wave_fivei_ticketed_writes_contract.md
  - wiki/wave_fivei_freeze_independent_review.md
  - coverage/api_v2_manifest.yaml
  - coverage/status.json
  - docs/superpowers/specs/2026-07-28-billy-mcp-complete-design.md
created: 2026-07-30T00:42:00Z
updated: 2026-07-30T00:42:00Z
---

# Wave-5i product-ready research independent review ACCEPT

## Verdict

| Claim | Result |
| --- | --- |
| Wave-5i product-ready research handoff | **ACCEPT** offline as implementation handoff only |
| Official documentation versus maintained inventory | **PASS** |
| Research versus accepted freeze tool/path/root map | **PASS** |
| Coverage honesty before product | **PASS** |
| Wave-5i product implementation | **not accepted** — separate Grok review required after root integration |
| Live, UI, vision, bulk, and completeness | **not claimed / fail-closed** |

The authoritative root `INDEPENDENT-REVIEW` Grok step accepted the product-ready
research at scratch `.fractal/main.billy_complete/tmp/grok-research.md`
(research39) against freeze page `wiki/wave_fivei_ticketed_writes_contract.md`,
freeze ACCEPT `wiki/wave_fivei_freeze_independent_review.md`, and root handoff
commit **`d7071df`**. Full cited findings live outside the public repository at
`.fractal/main.billy_complete/tmp/grok-review.md`.

## Exact reviewed scope

This ACCEPT covers only the cited handoff that opens Codex Power product work
for the six singular API v2 CUD operations already frozen:

| Inventory id | Preview tool | Execute tool | HTTP | Request root | Response roots |
| --- | --- | --- | --- | --- | --- |
| `api.salesTaxAccounts.create` | `api_sales_tax_accounts_create_preview` | `api_sales_tax_accounts_create_execute` | `POST /salesTaxAccounts` | `salesTaxAccount` | `salesTaxAccounts` |
| `api.salesTaxAccounts.update` | `api_sales_tax_accounts_update_preview` | `api_sales_tax_accounts_update_execute` | `PUT /salesTaxAccounts/:id` | `salesTaxAccount` | `salesTaxAccounts` |
| `api.salesTaxAccounts.delete` | `api_sales_tax_accounts_delete_preview` | `api_sales_tax_accounts_delete_execute` | `DELETE /salesTaxAccounts/:id` | id binding | `salesTaxAccounts` + optional deleted meta |
| `api.salesTaxMetaFields.create` | `api_sales_tax_meta_fields_create_preview` | `api_sales_tax_meta_fields_create_execute` | `POST /salesTaxMetaFields` | `salesTaxMetaField` | `salesTaxMetaFields` |
| `api.salesTaxMetaFields.update` | `api_sales_tax_meta_fields_update_preview` | `api_sales_tax_meta_fields_update_execute` | `PUT /salesTaxMetaFields/:id` | `salesTaxMetaField` | `salesTaxMetaFields` |
| `api.salesTaxMetaFields.delete` | `api_sales_tax_meta_fields_delete_preview` | `api_sales_tax_meta_fields_delete_execute` | `DELETE /salesTaxMetaFields/:id` | id binding | `salesTaxMetaFields` + optional deleted meta |

Research arithmetic and file ownership match the freeze:

- Registry **208 → 220** `api_*` tools after product.
- Offline coverage **151 → 157** after real suites only.
- Suggested module `src/billy_mcp/api/sales_tax_account_meta_writes.py` and tests
  `tests/api/test_sales_tax_account_meta_writes.py` plus
  `tests/api/test_sales_tax_account_meta_cross_executor.py`.
- Specs: accounts `collection_path="/salesTaxAccounts"`,
  `singular_root="salesTaxAccount"`, `plural_root="salesTaxAccounts"`,
  `additional_plural_roots=()`; meta fields
  `collection_path="/salesTaxMetaFields"`,
  `singular_root="salesTaxMetaField"`, `plural_root="salesTaxMetaFields"`,
  `additional_plural_roots=()`.
- Opaque inner payloads; do not invent account `type` enum values; do not treat
  meta-field `isPredefined` as readonly by borrowing ruleset semantics; do not
  expand Wave-5g `sales_tax_writes.py`; no bulk tools.

A research operator-table HEAD stamp of `301acb9` is superseded by handoff
commit `d7071df`; the tool/path/field surface is unchanged and accepted.

## Product gate

This ACCEPT, together with
`wiki/wave_fivei_freeze_independent_review.md`, opens offline Codex Power
product implementation for the twelve ticketed tools. It is not product ACCEPT,
live qualification, UI/vision acceptance, bulk resolution, or completeness.

After product integrates at root, a separate independent Grok product review
must confirm registry **220**, coverage **157** offline with the six sales-tax
account and meta-field CUD rows greened only by real suites, ticket binding and
replay boundaries, empty multi-roots, and fail-closed live/UI/bulk.

No browser was launched, no credential or customer data was used, and no raw
browser evidence is retained. Coverage remains 151/151/0/0 with
`complete: false` until product and tests land.
