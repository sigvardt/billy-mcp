---
name: state
desc: Current node state, verified review decisions, and open qualification work.
tags: [billy, coverage, review]
sources:
  - docs/superpowers/specs/2026-07-28-billy-mcp-complete-design.md
  - https://www.billy.dk/api/
created: 2026-07-30T11:33:24Z
updated: 2026-07-30T15:15:00Z
---

# state

## Current state

- Wave-5c through Wave-5q write modules merged; shared confirmation store and write protocol.
- Root offline coverage **178** implemented + contract_tested. Live/vision **0**. `complete: false`.
- Wave-5q freeze page + freeze IR **ACCEPT** on root (freeze MD5 `c53717468aff0406799feca225a00728`).
- Wave-5q users product merged (`user_writes.py`); registry 262; `api.users.update` offline-green only; live still red.
- Wave-5q product independent review: **ACCEPT offline** on child tip `4b1cffb` (`wiki/wave_fiveq_users_product_independent_review.md`); root merge of that review page still open.
- Wave-5r freeze-ready research + research IR **ACCEPT as research** on root.
- Wave-5r freeze page authored on child tip `a8590b4` with content MD5 **`078aca13828b5e0d71b454c1aa2dc00f`**; **not on root yet**.
- Research74: freeze page re-verified against official docs (MD5 `8b94b0135c91fd15fe54ea33e088a4be`) and unauth probes; product-ready package published for post-freeze-IR work.
- No `sales_tax_return_writes.py` and no greening of `api.salesTaxReturns.update`.
- UI all red (339); bulk 92 empty-tool red; no live token; no UI credentials.
- Docs body still MD5 `8b94b0135c91fd15fe54ea33e088a4be` (ETag `wcw4x9hqvu3603`, 147934 bytes).

## Verification

- Review74 independently re-fetched the docs and unauthenticated salesTaxReturns gates; its results match Research74 and the prior Research73/Review73 evidence.
- Research74 **ACCEPT as research**; freeze page still child-only; no product greening.
- Freeze child page MD5 `078aca13828b5e0d71b454c1aa2dc00f` consistent with Supports, property boundary, method gates, and ticketed-write design.
- Coverage honesty: 178/178/0/0; complete false; `api.salesTaxReturns.update` remains red; zero false-green rows from research.
- Product-ready research does not authorise product source before freeze IR ACCEPT.

## Review decisions (authoritative)

- Wave-5m through Wave-5p freeze/product: **ACCEPT** offline.
- Wave-5q freeze independent: **ACCEPT**.
- Wave-5q product-ready research: **ACCEPT as research**.
- Wave-5q product on root: **merged**.
- Wave-5q product independent: **ACCEPT offline** on child `4b1cffb` (root merge pending).
- Research73 Wave-5r freeze-ready: **ACCEPT as research** (review73).
- Research74 Wave-5r freeze verification + product-ready package: **ACCEPT as research** (review74). Not freeze IR.
- Overall completeness: **FAIL**.

## Open coverage work

1. Merge Wave-5r freeze page to root (MD5 `078aca13828b5e0d71b454c1aa2dc00f`).
2. Grok: Wave-5r freeze independent review after freeze on root.
3. Optionally merge Wave-5q product IR wiki from child `4b1cffb`.
4. After Wave-5r freeze IR ACCEPT: salesTaxReturns update product (178 → 179 offline; 262 → 264 tools) per `wiki/wave_fiver_sales_tax_returns_product_ready_research.md`.
5. Later: transactions (method-open but all columns readonly offline), specials, method-closed Supports honesty; associations delete needs live cleanup proof.
6. Bulk 92, UI/auth/vision, live CUD still open.

## Evidence boundaries

- Research ACCEPT is not freeze ACCEPT, product ACCEPT, or live qualification.
- Freeze page authoring is not freeze IR ACCEPT.
- Freeze IR ACCEPT authorises product source; greening requires product + generator + tests.
- salesTaxReturns singular create/delete are 405: freeze is update-only; cleanup restore-via-PUT unproven; settlement may be one-way.
- Do not green coverage from research or freeze alone.

## References

- Research74 brief: `.fractal/main.billy_complete/tmp/grok-research.md`
- Product-ready wiki: `wiki/wave_fiver_sales_tax_returns_product_ready_research.md`
- Product-ready IR wiki: `wiki/wave_fiver_sales_tax_returns_product_ready_research_independent_review.md`
- Review74: `.fractal/main.billy_complete/tmp/grok-review.md`
- Freeze-ready wiki: `wiki/wave_fiver_sales_tax_returns_freeze_ready_research.md`
- Freeze-ready IR wiki: `wiki/wave_fiver_sales_tax_returns_freeze_ready_research_independent_review.md`
- Freeze page (child only): `wiki/wave_fiver_ticketed_writes_contract.md` @ MD5 `078aca13828b5e0d71b454c1aa2dc00f`
- Wave-5q freeze page: `wiki/wave_fiveq_ticketed_writes_contract.md`
- Wave-5q product: `src/billy_mcp/api/user_writes.py`
- Wave-5q product IR (child): `wiki/wave_fiveq_users_product_independent_review.md`
