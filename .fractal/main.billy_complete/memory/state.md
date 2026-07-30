---
name: state
desc: Current node state, verified review decisions, and open qualification work.
tags: [billy, coverage, review]
sources:
  - docs/superpowers/specs/2026-07-28-billy-mcp-complete-design.md
  - https://www.billy.dk/api/
created: 2026-07-30T11:33:24Z
updated: 2026-07-30T15:25:00Z
---

# state

## Current state

- Wave-5c through Wave-5q write modules merged; shared confirmation store and write protocol.
- Root offline coverage **178** implemented + contract_tested. Live/vision **0**. `complete: false`.
- Wave-5q freeze, freeze IR, product, and product IR are all **ACCEPT offline** on root.
- Wave-5r freeze page **on root**: `wiki/wave_fiver_ticketed_writes_contract.md` content MD5 **`078aca13828b5e0d71b454c1aa2dc00f`**.
- Wave-5r freeze IR page **missing**. Primary next gate is freeze independent review.
- Research75: freeze IR readiness re-verification against official docs (MD5 `8b94b0135c91fd15fe54ea33e088a4be`) and unauth probes; product-ready map still valid after freeze IR ACCEPT.
- No `sales_tax_return_writes.py` and no greening of `api.salesTaxReturns.update`.
- UI all red (339); bulk 92 empty-tool red; clear not-impl 31; no live token; no UI credentials.
- Docs body still MD5 `8b94b0135c91fd15fe54ea33e088a4be` (ETag `wcw4x9hqvu3603`, 147934 bytes).

## Verification

- Research75 independently re-fetched docs and unauthenticated salesTaxReturns gates; results match Research74/Review74 and Research73/Review73.
- Freeze page MD5 `078aca13828b5e0d71b454c1aa2dc00f` present on root HEAD `a418165`; consistent with Supports, property boundary, method gates, and ticketed-write design.
- Coverage honesty: 178/178/0/0; complete false; `api.salesTaxReturns.update` remains red; zero false-green rows from research.
- Product-ready research does not authorise product source before freeze IR ACCEPT.

## Review decisions (authoritative)

- Wave-5m through Wave-5p freeze/product: **ACCEPT** offline.
- Wave-5q freeze independent: **ACCEPT**.
- Wave-5q product: **ACCEPT offline** on root.
- Research73 Wave-5r freeze-ready: **ACCEPT as research** (review73).
- Research74 Wave-5r product-ready package: **ACCEPT as research** (review74). Not freeze IR.
- Research75 Wave-5r freeze IR readiness: research only; freeze IR still open.
- Overall completeness: **FAIL**.

## Open coverage work

1. Grok: Wave-5r freeze independent review of freeze MD5 `078aca13828b5e0d71b454c1aa2dc00f` on root.
2. After Wave-5r freeze IR ACCEPT: salesTaxReturns update product (178 → 179 offline; 262 → 264 tools) per `wiki/wave_fiver_sales_tax_returns_product_ready_research.md`.
3. Later: transactions (method-open needs writable-column evidence), specials, method-closed Supports honesty; associations delete needs live cleanup proof.
4. Bulk 92, UI/auth/vision, live CUD still open.

## Evidence boundaries

- Research ACCEPT is not freeze ACCEPT, product ACCEPT, or live qualification.
- Freeze page on root is not freeze IR ACCEPT.
- Freeze IR ACCEPT authorises product source; greening requires product + generator + tests.
- salesTaxReturns singular create/delete are 405: freeze is update-only; restore-via-PUT unproven; settlement may be one-way.
- Do not green coverage from research or freeze alone.

## References

- Research75 brief: `.fractal/main.billy_complete/tmp/grok-research.md`
- Freeze IR readiness wiki: `wiki/wave_fiver_freeze_ir_ready_research.md`
- Freeze page (root): `wiki/wave_fiver_ticketed_writes_contract.md` @ MD5 `078aca13828b5e0d71b454c1aa2dc00f`
- Product-ready wiki: `wiki/wave_fiver_sales_tax_returns_product_ready_research.md`
- Product-ready IR wiki: `wiki/wave_fiver_sales_tax_returns_product_ready_research_independent_review.md`
- Freeze-ready wiki: `wiki/wave_fiver_sales_tax_returns_freeze_ready_research.md`
- Freeze-ready IR wiki: `wiki/wave_fiver_sales_tax_returns_freeze_ready_research_independent_review.md`
- Wave-5q product: `src/billy_mcp/api/user_writes.py`
- Wave-5q product IR: `wiki/wave_fiveq_users_product_independent_review.md`
