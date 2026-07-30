---
name: wave_fiver_sales_tax_returns_freeze_ready_research_independent_review
title: Wave-5r salesTaxReturns freeze-ready research independent review
desc: Independent Grok ACCEPT as research for the Wave-5r salesTaxReturns update freeze-ready package; freeze page, product, live, UI, and completeness remain separate.
tags: [billy, api, sales_tax_returns, writes, review, research]
sources:
  - https://www.billy.dk/api/
  - https://api.billysbilling.com/v2
  - wiki/wave_fiver_sales_tax_returns_freeze_ready_research.md
  - wiki/offline_write_probe_rules.md
  - coverage/api_v2_manifest.yaml
  - coverage/status.json
  - docs/superpowers/specs/2026-07-28-billy-mcp-complete-design.md
created: 2026-07-30T14:56:00Z
updated: 2026-07-30T14:56:00Z
---

# Wave-5r salesTaxReturns freeze-ready research independent review

## Verdict

**ACCEPT as research** for the Wave-5r offline freeze-ready package covering singular `salesTaxReturns` update only (exactly two future ticketed tools once a freeze page and product exist).

This is not freeze ACCEPT, product ACCEPT, live ACCEPT, UI ACCEPT, vision ACCEPT, bulk resolution, Wave-5q product independent ACCEPT, or overall completeness. It does not green coverage.

## Scope accepted

- Official API contract for `/v2/salesTaxReturns` Supports get by id, list, **update**, bulk save, bulk delete; omits create and singular delete.
- Independent docs fingerprint: HTTP 200, ETag `"wcw4x9hqvu3603"`, MD5 `8b94b0135c91fd15fe54ea33e088a4be`, body 147934 bytes (byte-identical to the research73 snapshot).
- Unauthenticated probes on locked base `https://api.billysbilling.com/v2` with JSON object body `{}`:
  - `POST /salesTaxReturns` → 405 `METHOD_NOT_ALLOWED`
  - `PUT /salesTaxReturns/:id` → 401 `AUTHENTICATION_REQUIRED`
  - `DELETE /salesTaxReturns/:id` → 405 `METHOD_NOT_ALLOWED`
  - Empty-body PUT → 400 `INVALID_REQUEST_BODY`
- Property boundary matches official table: readonly columns excluded; blank-notes columns `periodText`, `reportDeadline`, `isSettled` stay opaque offline with no live success or reversibility claim.
- Freeze package correctly names only `api_sales_tax_returns_update_preview` and `api_sales_tax_returns_update_execute`; opaque `salesTaxReturn` map; required success root `salesTaxReturns`; shared ticket protocol.
- Inventory `api.salesTaxReturns.update` remains `implemented: false`, `contract_tested: false`, `live_tested: false`; research did not green coverage.
- Root coverage honesty: 178 implemented + contract_tested; live 0; vision 0; `complete: false`; 92 bulk empty-tool red; UI all red.
- No freeze page and no product module on root yet.

## Exact future freeze surface accepted as research package

| Inventory id | Preview | Execute | Method and client path | Request | Required success root |
| --- | --- | --- | --- | --- | --- |
| `api.salesTaxReturns.update` | `api_sales_tax_returns_update_preview` | `api_sales_tax_returns_update_execute` | `PUT /salesTaxReturns/:id` | `id` + `salesTaxReturn` map | `salesTaxReturns` |

## Explicit non-acceptances

- Wave-5r freeze page authoring (not yet on root as product authority)
- Wave-5r freeze independent ACCEPT
- SalesTaxReturns product tools, registration, tests, or coverage greening
- Wave-5q users product independent ACCEPT (separate review of merged `user_writes.py`)
- Live CUD, UI, vision, bulk 92 resolution, association delete offline
- Overall completeness

## Contract discrepancies

None for the freeze-ready research scope.

## Next gate

Codex Power may author wiki-only `wiki/wave_fiver_ticketed_writes_contract.md` from this accepted research package. Independent freeze ACCEPT is required before any salesTaxReturns product module.

Parent scratch detail: `.fractal/main.billy_complete/tmp/grok-review.md` (review73).
