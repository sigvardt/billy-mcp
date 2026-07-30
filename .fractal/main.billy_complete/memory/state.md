---
name: state
desc: Current node state, verified review decisions, and open qualification work.
tags: [billy, coverage, review]
sources:
  - docs/superpowers/specs/2026-07-28-billy-mcp-complete-design.md
  - https://www.billy.dk/api/
created: 2026-07-30T15:57:03Z
updated: 2026-07-30T15:57:03Z
---

# state

## Current state

- Wave-5c through Wave-5q write modules merged; shared confirmation store and write protocol.
- Root offline coverage **178** implemented + contract_tested. Live/vision **0**. `complete: false`.
- Wave-5q freeze, freeze IR, product, and product IR are all **ACCEPT offline** on root.
- Wave-5r freeze page on root: `wiki/wave_fiver_ticketed_writes_contract.md` content MD5 **`078aca13828b5e0d71b454c1aa2dc00f`**.
- Wave-5r freeze independent review: **ACCEPT** (`wiki/wave_fiver_freeze_independent_review.md`, reviewed baseline `322f301`).
- Product source remains absent on root; the child leaf `main.billy_complete.wave5r_sales_tax_returns_product` owns the bounded product implementation.
- The current official-document recheck confirms MD5 `8b94b0135c91fd15fe54ea33e088a4be` (ETag `wcw4x9hqvu3603`, 147934 bytes) and unauth salesTaxReturns gates (PUT 401, POST/DELETE 405). The cited product implementation map is accepted as research.
- UI all red (339); bulk 92 empty-tool red; clear not-impl 31; no live token; no UI credentials.

## Verification

- Freeze MD5 `078aca13828b5e0d71b454c1aa2dc00f` verified; freeze IR ACCEPT stands.
- Official docs body is byte-identical to the preceding verified body; no Supports or property drift.
- Coverage honesty: 178/178/0/0; complete false; `api.salesTaxReturns.update` remains red; no false-green rows.
- Freeze ACCEPT authorises product source only; greening requires product + generator + tests.

## Review decisions (authoritative)

- Wave-5m through Wave-5q freeze/product: **ACCEPT** offline.
- Wave-5r research packages: **ACCEPT as research**.
- Wave-5r freeze independent: **ACCEPT**.
- Wave-5r product implementation research: **ACCEPT as research** (`wiki/wave_fiver_product_implementation_research_independent_review.md`).
- Wave-5r product: **not accepted** (not implemented on root).
- Overall completeness: **FAIL**.

## Open coverage work

1. Codex Power: Wave-5r salesTaxReturns update product (178 → 179 offline; 262 → 264 tools) per freeze + `wiki/wave_fiver_product_implementation_research.md` and tmp research76.
2. Grok: product independent review after product lands.
3. Later: remaining clear not-impl, specials, bulk 92, UI/auth/vision, live CUD.

## Evidence boundaries

- Freeze IR ACCEPT is not product ACCEPT, live qualification, or greening.
- Greening requires product module, contract tests, generator offline evidence, and honest status regen.
- salesTaxReturns singular create/delete are 405; restore-via-PUT unproven; settlement may be one-way.
- Do not green coverage from research or freeze alone.

## References

- Freeze IR (authoritative): `wiki/wave_fiver_freeze_independent_review.md`
- Product implementation research: `wiki/wave_fiver_product_implementation_research.md`
- Research scratch: `.fractal/main.billy_complete/tmp/grok-research.md`
- Freeze page: `wiki/wave_fiver_ticketed_writes_contract.md` @ MD5 `078aca13828b5e0d71b454c1aa2dc00f`
- Product-ready map (pre-freeze-IR package): `wiki/wave_fiver_sales_tax_returns_product_ready_research.md`
- Twin template: `src/billy_mcp/api/user_writes.py`
