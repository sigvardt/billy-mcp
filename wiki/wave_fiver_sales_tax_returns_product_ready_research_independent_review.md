---
name: wave_fiver_sales_tax_returns_product_ready_research_independent_review
title: Wave-5r salesTaxReturns product-ready research independent review
desc: Independent Grok ACCEPT as research for the Wave-5r freeze verification and product-ready package; freeze IR ACCEPT, product, live, UI, and completeness remain separate.
tags: [billy, api, sales_tax_returns, writes, review, research]
sources:
  - https://www.billy.dk/api/
  - https://api.billysbilling.com/v2
  - wiki/wave_fiver_sales_tax_returns_product_ready_research.md
  - wiki/wave_fiver_sales_tax_returns_freeze_ready_research.md
  - wiki/wave_fiver_sales_tax_returns_freeze_ready_research_independent_review.md
  - wiki/offline_write_probe_rules.md
  - coverage/api_v2_manifest.yaml
  - coverage/status.json
  - docs/superpowers/specs/2026-07-28-billy-mcp-complete-design.md
created: 2026-07-30T15:15:00Z
updated: 2026-07-30T15:15:00Z
---

# Wave-5r salesTaxReturns product-ready research independent review

## Verdict

**ACCEPT as research** for the Wave-5r offline freeze-verification and product-ready package covering singular `salesTaxReturns` update only (exactly two future ticketed tools once freeze IR ACCEPT and product exist).

This is not freeze ACCEPT, product ACCEPT, live ACCEPT, UI ACCEPT, vision ACCEPT, bulk resolution, or overall completeness. It does not green coverage. It does not authorise product source until freeze independent review ACCEPT of freeze content MD5 `078aca13828b5e0d71b454c1aa2dc00f` on root.

## Scope accepted

- Official API contract for `/v2/salesTaxReturns` Supports get by id, list, **update**, bulk save, bulk delete; omits create and singular delete.
- Independent docs fingerprint: HTTP 200, ETag `"wcw4x9hqvu3603"`, MD5 `8b94b0135c91fd15fe54ea33e088a4be`, body 147934 bytes (byte-identical to the research74 snapshot).
- Unauthenticated probes on locked base `https://api.billysbilling.com/v2` with JSON object body `{}`:
  - `POST /salesTaxReturns` → 405 `METHOD_NOT_ALLOWED`
  - `PUT /salesTaxReturns/:id` → 401 `AUTHENTICATION_REQUIRED`
  - `DELETE /salesTaxReturns/:id` → 405 `METHOD_NOT_ALLOWED`
  - Empty-body PUT → 400 `INVALID_REQUEST_BODY`
- Property boundary matches official table: readonly columns excluded; blank-notes columns `periodText`, `reportDeadline`, `isSettled` stay opaque offline with no live success or reversibility claim.
- Freeze page on child tip `a8590b4` content MD5 `078aca13828b5e0d71b454c1aa2dc00f` is consistent with Supports, method gates, ticket protocol, and exclusions; still missing from root.
- Product-ready map correctly names only `api_sales_tax_returns_update_preview` and `api_sales_tax_returns_update_execute`; twin of `user_writes.py`; offline greening path 178→179 and registry 262→264 only after product.
- Inventory `api.salesTaxReturns.update` remains `implemented: false`, `contract_tested: false`, `live_tested: false`; research did not green coverage.
- Root coverage honesty: 178 implemented + contract_tested; live 0; vision 0; `complete: false`; 92 bulk empty-tool red; UI parity salesTaxReturns rows all red.
- No product module on root.

## Exact future product surface accepted as research package

| Inventory id | Preview | Execute | Method and client path | Request | Required success root |
| --- | --- | --- | --- | --- | --- |
| `api.salesTaxReturns.update` | `api_sales_tax_returns_update_preview` | `api_sales_tax_returns_update_execute` | `PUT /salesTaxReturns/:id` | `id` + `salesTaxReturn` map | `salesTaxReturns` |

## Explicit non-acceptances

- Wave-5r freeze independent ACCEPT (freeze page not yet on root as freeze authority)
- Wave-5r product tools, registration, tests, or coverage greening
- Live CUD, UI, vision, bulk 92 resolution, association delete offline
- Overall completeness

## Contract discrepancies

None for the product-ready research scope.

## Next gate

1. Merge freeze page `wiki/wave_fiver_ticketed_writes_contract.md` (MD5 `078aca13828b5e0d71b454c1aa2dc00f`) to root.
2. Independent freeze ACCEPT on that page.
3. Only then Codex Power product leaf per `wiki/wave_fiver_sales_tax_returns_product_ready_research.md`.

Parent scratch detail: `.fractal/main.billy_complete/tmp/grok-review.md` (review74).
