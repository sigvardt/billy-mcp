---
name: state
desc: Current node state, verified review decisions, and open qualification work.
tags: [billy, coverage, review]
sources:
  - docs/superpowers/specs/2026-07-28-billy-mcp-complete-design.md
  - https://www.billy.dk/api/
created: 2026-07-30T15:57:03Z
updated: 2026-07-30T16:18:00Z
---

# state

## Current state

- Wave-5c through Wave-5r write modules merged on root (including salesTaxReturns update).
- Root offline coverage **179** implemented + contract_tested. Live/vision **0**. `complete: false`. Registry **264** API tools.
- Wave-5q freeze/product IR: **ACCEPT** offline.
- Wave-5r freeze IR: **ACCEPT**. Wave-5r product IR: **ACCEPT** offline (`wiki/wave_fiver_product_independent_review.md`, baseline `5ad69a6`).
- Research77 residual specials ranking: **ACCEPT as research** (`wiki/wave_fives_residual_specials_research.md`).
- UI all red (339); bulk 92 red; clear not-impl 30; specials not-impl 4; no live token; no UI credentials.

## Verification

- Official docs MD5 `8b94b0135c91fd15fe54ea33e088a4be` reconfirmed at product IR.
- Unauth salesTaxReturns gates: PUT 401; POST/DELETE 405.
- Freeze MD5 `078aca13828b5e0d71b454c1aa2dc00f` unchanged.
- Coverage honesty: 179/179/0/0; complete false; bulk/UI red.

## Review decisions (authoritative)

- Wave-5m through Wave-5q freeze/product: **ACCEPT** offline.
- Wave-5r freeze independent: **ACCEPT**.
- Wave-5r product independent: **ACCEPT** offline.
- Wave-5s residual/specials research: **ACCEPT as research**.
- Overall completeness: **FAIL**.

## Open coverage work

1. Codex Power Wave-5s-A: `api_invoice_logs_list` (special read) per Research77.
2. Later: files upload special, invoice email/delivery specials, 405 false friends (live/docs), transactions (live), bulk 92, UI/auth/vision.

## Evidence boundaries

- Product IR ACCEPT is offline only; not live, UI, vision, bulk, or completeness.
- 405 overrides Supports offline; DELETE 200 meta-only is not cleanup proof.
- Do not green coverage from research alone.

## References

- Product IR: `wiki/wave_fiver_product_independent_review.md`
- Review scratch: `.fractal/main.billy_complete/tmp/grok-review.md`
- Residual specials research: `wiki/wave_fives_residual_specials_research.md`
- Freeze IR: `wiki/wave_fiver_freeze_independent_review.md`
- Freeze page: `wiki/wave_fiver_ticketed_writes_contract.md` @ MD5 `078aca13828b5e0d71b454c1aa2dc00f`
