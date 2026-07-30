---
name: state
desc: Current node state, verified review decisions, and open qualification work.
tags: [billy, coverage, review]
sources:
  - docs/superpowers/specs/2026-07-28-billy-mcp-complete-design.md
  - https://www.billy.dk/api/
created: 2026-07-30T15:57:03Z
updated: 2026-07-30T16:38:00Z
---

# state

## Current state

- Wave-5c through Wave-5r write modules merged on root (including salesTaxReturns update).
- Root offline coverage **179** implemented + contract_tested. Live/vision **0**. `complete: false`. Registry **264** API tools.
- Wave-5q freeze/product IR: **ACCEPT** offline.
- Wave-5r freeze IR: **ACCEPT**. Wave-5r product IR: **ACCEPT** offline (`wiki/wave_fiver_product_independent_review.md`, baseline `5ad69a6`).
- Research77 residual specials ranking: **ACCEPT as research** (`wiki/wave_fives_residual_specials_research.md`).
- Research78 Wave-5s-A invoiceLogs list contract: **ACCEPT as research** (`wiki/wave_fivesa_invoice_logs_research_independent_review.md` @ `97f7e12`).
- Product child `wave5sa_invoice_logs_product` active for Codex Power implementation; no product tip on root yet.
- UI all red (339); bulk 92 red; clear not-impl 30; specials not-impl 4; no live token; no UI credentials.

## Verification

- Official docs MD5 `8b94b0135c91fd15fe54ea33e088a4be` reconfirmed at research IR.
- Unauth invoiceLogs: collection GET 401; id GET 404; POST/PUT/DELETE 405.
- Inventory `api.special.invoice_logs` still red; not in offline evidence map.
- Coverage honesty: 179/179/0/0; complete false; bulk/UI red; registry 264; tool absent.

## Review decisions (authoritative)

- Wave-5m through Wave-5q freeze/product: **ACCEPT** offline.
- Wave-5r freeze independent: **ACCEPT**.
- Wave-5r product independent: **ACCEPT** offline.
- Wave-5s residual/specials research: **ACCEPT as research**.
- Wave-5s-A invoiceLogs research IR: **ACCEPT as research** (not product ACCEPT).
- Overall completeness: **FAIL**.

## Open coverage work

1. Codex Power Wave-5s-A product leaf: `api_invoice_logs_list` per accepted research; then Grok product IR.
2. Later: files upload special, invoice email/delivery specials, 405 false friends (live/docs), transactions (live), bulk 92, UI/auth/vision.

## Evidence boundaries

- Research IR ACCEPT is not product, live, UI, vision, bulk, or completeness.
- 405 overrides Supports offline; DELETE 200 meta-only is not cleanup proof.
- invoiceLogs singular GET 404 is not product authorisation for a get tool.
- Do not green coverage from research alone.

## References

- Research IR: `wiki/wave_fivesa_invoice_logs_research_independent_review.md`
- Wave-5s-A research: `wiki/wave_fivesa_invoice_logs_list_research.md`
- Review scratch: `.fractal/main.billy_complete/tmp/grok-review.md`
- Product IR (Wave-5r): `wiki/wave_fiver_product_independent_review.md`
- Residual specials research: `wiki/wave_fives_residual_specials_research.md`
