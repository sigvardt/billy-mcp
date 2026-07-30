---
name: state
desc: Current node state, verified review decisions, and open qualification work.
tags: [billy, coverage, review]
sources:
  - docs/superpowers/specs/2026-07-28-billy-mcp-complete-design.md
  - https://www.billy.dk/api/
created: 2026-07-30T15:57:03Z
updated: 2026-07-30T21:03:00Z
---

# state

## Current state

- Wave-5c through Wave-5s-C write/special modules merged on root (email + delivery at `0efceae`).
- All **6** specials offline producted; live false. Residual clear **29** red. Bulk **92** red. UI **339** red.
- Root offline coverage: **184** implemented + contract_tested. Live/vision **0**. `complete: false`.
- Research89 + management plan are on root at `b1a5bdd`. Review89 **ACCEPTS research** and **ACCEPTS harness infrastructure only**.
- Wave-5t live-gate harness was root-integrated at `7571cec` after clean-archive focused tests (**10 passed, 1 opt-in live skip**). It remains an OPTIONS-only matrix with no coverage edits.
- Wave-5t UI/auth discovery fallback remains active without a mergeable product brief vs root.
- `BILLY_API_TOKEN` and UI secrets verified unset.

## Verification

- Review89 docs re-fetch: ETag `"wcw4x9hqvu3603"`, 147934 bytes, MD5 `8b94b0135c91fd15fe54ea33e088a4be` (byte-identical to research89).
- Independent unauth sample probes match research89 residual/bulk/special gates; `GET /user/organizations` unauth **404**.
- Harness child: residual 29 + bulk 92 IDs exact vs inventory; always `contract_qualified: false`.
- Root validation after harness integration: formatter, Ruff, Pyright, inventory,
  and repository-policy checks pass; non-live suite **1265 passed, 1 deselected**.
- Coverage honesty: 184/184/0/0, `complete: false`.

## Review decisions (authoritative)

- Wave-5m through Wave-5s-C product: **ACCEPT offline only** where previously recorded.
- Research88 residual/bulk ranking: **ACCEPT as research** (review88).
- Research89: **ACCEPT as research** (review89).
- Wave-5t plan baseline / 142.20 management plan: **ACCEPT as planning** only.
- Wave-5t live-gate harness: **ACCEPT as infrastructure/research only** (review89); focused archive tests pass; **not** live qualification; keep residual/bulk red.
- Wave-5t UI discovery fallback product: **not accepted** / not ready.
- Overall completeness: **FAIL**.

## Open coverage work

1. Validate the root-integrated Wave-5t harness with root checks; keep coverage flags false.
2. Close or deliver UI discovery fallback with a cited brief (or absorb Research89 login facts only).
3. Residual clear 29 and bulk 92 — live token + non-prod org required for real contracts (OPTIONS harness is not enough).
4. Live prove or correct `GET /user/organizations` (unauth **404** vs docs + offline tool path).
5. UI/auth/vision qualification — credentials + dedicated org; EN+DA login labels.
6. Live qualification for high side-effect specials on non-production org only.

## Evidence boundaries

- Do not implement residual or bulk tools from Supports text, unauth 401 alone, or PATCH meta-200.
- Do not green coverage from harness scaffolding or research.
- No webhooks (official 0 mentions; API 404).
- Do not claim vision or UI parity from login-only observation.

## References

- Research89: `.fractal/main.billy_complete/tmp/grok-research.md`
- Review88: `.fractal/main.billy_complete/tmp/grok-review.md`
- Review89: `wiki/wave_fives_research89_independent_review.md`
- Wiki IR: `wiki/wave_fives_research88_independent_review.md`
- Residual ranking: `wiki/wave_fives_residual_specials_research.md`
- Probe rules: `wiki/offline_write_probe_rules.md`
- Plan: `.fractal/main.billy_complete/plans/2026-07-30T20:49:57.245Z-142.20-wave5t_harness_ui_management.md`
