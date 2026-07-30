---
name: wave_fivei_freeze_ready_research_independent_review
title: Wave-5i freeze-ready research independent review ACCEPT
desc: Authoritative root Grok acceptance of the research37 offline freeze-ready handoff for singular salesTaxAccounts and salesTaxMetaFields ticketed writes.
tags: [billy, api, sales-tax, writes, review, coverage, research]
sources:
  - https://www.billy.dk/api/
  - coverage/api_v2_manifest.yaml
  - coverage/status.json
  - wiki/offline_write_probe_rules.md
  - wiki/wave_fiveg_ticketed_writes_contract.md
  - docs/superpowers/specs/2026-07-28-billy-mcp-complete-design.md
created: 2026-07-29T23:58:00Z
updated: 2026-07-29T23:58:00Z
---

# Wave-5i freeze-ready research independent review ACCEPT

## Verdict

| Claim | Result |
| --- | --- |
| Research37 freeze-ready handoff | **ACCEPT** offline as freeze-drafting handoff only |
| Official documentation versus maintained inventory | **PASS** (fingerprint unchanged) |
| Research tool/path/root map versus inventory preview names | **PASS** |
| Unauth method probes versus offline probe rules | **PASS** |
| Coverage honesty (no green from research) | **PASS** |
| Wave-5i freeze page | **not accepted** — page not written yet |
| Wave-5i product | **not accepted** — blocked until freeze ACCEPT |
| Live, UI, vision, bulk, and completeness | **not claimed / fail-closed** |

The authoritative root `INDEPENDENT-REVIEW` Grok step accepted the freeze-ready
research at scratch `.fractal/main.billy_complete/tmp/grok-research.md`
(research37). Child node `wave5i_freeze_review_grok` exited without a durable
ACCEPT and does not replace this page. Full cited findings live outside the
public repository at `.fractal/main.billy_complete/tmp/grok-review.md`.

## Exact reviewed scope

This ACCEPT covers only the cited handoff that freezes drafting authority for
six singular API v2 CUD operations (twelve tools after a later product):

| Inventory id | Preview tool | Execute tool | HTTP | Request root | Response roots |
| --- | --- | --- | --- | --- | --- |
| `api.salesTaxAccounts.create` | `api_sales_tax_accounts_create_preview` | `api_sales_tax_accounts_create_execute` | `POST /salesTaxAccounts` | `salesTaxAccount` | `salesTaxAccounts` |
| `api.salesTaxAccounts.update` | `api_sales_tax_accounts_update_preview` | `api_sales_tax_accounts_update_execute` | `PUT /salesTaxAccounts/:id` | `salesTaxAccount` | `salesTaxAccounts` |
| `api.salesTaxAccounts.delete` | `api_sales_tax_accounts_delete_preview` | `api_sales_tax_accounts_delete_execute` | `DELETE /salesTaxAccounts/:id` | id binding | `salesTaxAccounts` + optional deleted meta |
| `api.salesTaxMetaFields.create` | `api_sales_tax_meta_fields_create_preview` | `api_sales_tax_meta_fields_create_execute` | `POST /salesTaxMetaFields` | `salesTaxMetaField` | `salesTaxMetaFields` |
| `api.salesTaxMetaFields.update` | `api_sales_tax_meta_fields_update_preview` | `api_sales_tax_meta_fields_update_execute` | `PUT /salesTaxMetaFields/:id` | `salesTaxMetaField` | `salesTaxMetaFields` |
| `api.salesTaxMetaFields.delete` | `api_sales_tax_meta_fields_delete_preview` | `api_sales_tax_meta_fields_delete_execute` | `DELETE /salesTaxMetaFields/:id` | id binding | `salesTaxMetaFields` + optional deleted meta |

Independent re-fetch of [official Billy API documentation](https://www.billy.dk/api/)
on 2026-07-29 returned HTTP 200, ETag `"hsisik4g9p3603"`, 147934 bytes, MD5
`c2efda0ee4cf9cf200e14910c5fc6996`. Resource tables for
[`/v2/salesTaxAccounts`](https://www.billy.dk/api/) and
[`/v2/salesTaxMetaFields`](https://www.billy.dk/api/) match the research
property notes, including unpublished `type` enum values, non-immutable
`account`, and `isPredefined` without a readonly marker. Bulk Supports remain
without body contracts and stay empty-tool red in the inventory.

Unauthenticated probes reconfirmed: POST/PUT return **401** on both resources;
missing-id DELETE returns **200** (not cleanup proof). Inventory preview tool
names already reserved; all six clear CUD rows remain `implemented: false` and
`contract_tested: false` at ACCEPT time.

## Operator-state note

Research37's operator banner may still describe pre-merge Wave-5h arithmetic
(coverage 148). Root merge `29cecbe` accepts Wave-5h product offline with
registry **208** and coverage **151**. That staleness does not invalidate the
Wave-5i field or tool map; freeze authors must use current
`coverage/status.json` for global arithmetic and research37 sections 2–4 for
the Wave-5i contract.

## Freeze gate opened

This ACCEPT authorises Codex Power to draft
`wiki/wave_fivei_ticketed_writes_contract.md` from the research brief and this
page. It is not acceptance of the freeze page text, product implementation,
live qualification, browser/UI parity, vision verification, bulk operations,
special routes, or overall completeness.

Suggested later product ownership (not authorised to implement yet): a new
module such as `sales_tax_account_meta_writes.py` with twelve tools, registry
**220** and coverage **157** only after freeze ACCEPT, product-ready research,
real offline suites, and a separate product independent review. Do not expand
Wave-5g `sales_tax_writes.py` for this cohort.

No browser was launched, no credential or customer data was used, and no
coverage row was greened by this research ACCEPT.
