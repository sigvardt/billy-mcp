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
- Wave-5r product leaf `main.billy_complete.wave5r_sales_tax_returns_product` **completed** at `cf33343` (two tools, leaf coverage 179/179, registry 264). Root has **no** product merge yet.
- Research77 residual ranking delivered: official docs MD5 `8b94b0135c91fd15fe54ea33e088a4be` byte-identical; unauth residual matrix reconfirmed; Wave-5s specials map on wiki.
- UI all red (339); bulk 92 empty-tool red; clear not-impl 31 on root; no live token; no UI credentials.

## Verification

- Freeze MD5 `078aca13828b5e0d71b454c1aa2dc00f` verified; freeze IR ACCEPT stands.
- Official docs body is byte-identical to research76; no Supports or property drift.
- Coverage honesty on root: 178/178/0/0; complete false; `api.salesTaxReturns.update` remains red until product merges.
- Research does not green coverage.

## Review decisions (authoritative)

- Wave-5m through Wave-5q freeze/product: **ACCEPT** offline.
- Wave-5r research packages: **ACCEPT as research**.
- Wave-5r freeze independent: **ACCEPT**.
- Wave-5r product implementation research: **ACCEPT as research**.
- Wave-5r product: **not accepted** (not merged on root).
- Wave-5s residual/specials research: **research delivered** (not product).
- Overall completeness: **FAIL**.

## Open coverage work

1. Root: merge Wave-5r product tip `cf33343` to 179 offline / 264 tools.
2. Grok: Wave-5r product independent review after merge.
3. Codex Power Wave-5s-A: `api_invoice_logs_list` (special read).
4. Later: files upload special, invoice email/delivery specials, 405 false friends (live/docs), transactions (live), bulk 92, UI/auth/vision.

## Evidence boundaries

- Leaf product claim is not root product ACCEPT.
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
