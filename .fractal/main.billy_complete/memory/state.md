---
name: state
desc: Current node state, verified review decisions, and open qualification work.
tags: [billy, coverage, review]
sources:
  - docs/superpowers/specs/2026-07-28-billy-mcp-complete-design.md
  - https://www.billy.dk/api/
created: 2026-07-30T15:57:03Z
updated: 2026-07-30T16:08:00Z
---

# state

## Current state

- Wave-5c through Wave-5q write modules merged; shared confirmation store and write protocol.
- Root offline coverage **178** implemented + contract_tested. Live/vision **0**. `complete: false`.
- Wave-5q freeze, freeze IR, product, and product IR are all **ACCEPT offline** on root.
- Wave-5r freeze page on root: `wiki/wave_fiver_ticketed_writes_contract.md` content MD5 **`078aca13828b5e0d71b454c1aa2dc00f`**.
- Wave-5r freeze independent review: **ACCEPT** (`wiki/wave_fiver_freeze_independent_review.md`).
- Wave-5r salesTaxReturns update is root-integrated from leaf `cf33343`: two typed
  tools, 179 implemented + contract-tested rows, and a 264-tool registry.
  Independent Grok product acceptance remains pending.
- Research77 residual ranking delivered: official docs MD5 `8b94b0135c91fd15fe54ea33e088a4be` byte-identical; unauth residual matrix reconfirmed; Wave-5s specials map on wiki.
- UI all red (339); bulk 92 empty-tool red; clear not-impl 31 on root; no live token; no UI credentials.

## Verification

- Freeze MD5 `078aca13828b5e0d71b454c1aa2dc00f` verified; freeze IR ACCEPT stands.
- Official docs body is byte-identical to research76; no Supports or property drift.
- Coverage honesty on root: 179/179/0/0; `complete: false`. The product is
  offline-only and has no live or vision evidence.
- Research does not green coverage.

## Review decisions (authoritative)

- Wave-5m through Wave-5q freeze/product: **ACCEPT** offline.
- Wave-5r research packages: **ACCEPT as research**.
- Wave-5r freeze independent: **ACCEPT**.
- Wave-5r product implementation research: **ACCEPT as research**.
- Wave-5r product: **not accepted** (root-integrated implementation awaits its
  independent Grok review).
- Wave-5s residual/specials research: **research delivered** (not product).
- Overall completeness: **FAIL**.

## Open coverage work

1. Grok: Wave-5r salesTaxReturns update product independent review.
2. Codex Power Wave-5s-A: `api_invoice_logs_list` (special read), only after
   the product review gives an offline ACCEPT.
4. Later: files upload special, invoice email/delivery specials, 405 false friends (live/docs), transactions (live), bulk 92, UI/auth/vision.

## Evidence boundaries

- Root product integration is not product ACCEPT, live qualification, or
  coverage completeness.
- Freeze IR ACCEPT is not product ACCEPT, live qualification, or greening.
- 405 overrides Supports offline; DELETE 200 meta-only is not cleanup proof.
- Do not green coverage from research alone.

## References

- Residual/specials research: `wiki/wave_fives_residual_specials_research.md`
- Research scratch: `.fractal/main.billy_complete/tmp/grok-research.md` (research77)
- Freeze IR: `wiki/wave_fiver_freeze_independent_review.md`
- Product implementation research: `wiki/wave_fiver_product_implementation_research.md`
- Freeze page: `wiki/wave_fiver_ticketed_writes_contract.md` @ MD5 `078aca13828b5e0d71b454c1aa2dc00f`
- Twin special reads: existing `api_user_get` / `api_user_list_organizations`
