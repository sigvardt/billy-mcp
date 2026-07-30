---
name: state
desc: Current node state, verified review decisions, and open qualification work.
tags: [billy, coverage, review]
sources:
  - docs/superpowers/specs/2026-07-28-billy-mcp-complete-design.md
  - https://www.billy.dk/api/
created: 2026-07-30T15:57:03Z
updated: 2026-07-30T21:12:00Z
---

# state

## Current state

- Wave-5c through Wave-5s-C write/special modules merged on root (email + delivery at `0efceae`).
- All **6** specials offline producted; live false. Residual clear **29** red. Bulk **92** red. UI **339** red.
- Root offline coverage: **184** implemented + contract_tested. Live/vision **0**. `complete: false`.
- Research89 + Wave-5t plan accepted as research/planning. Review89 ACCEPTS research and harness infrastructure only.
- Wave-5t live-gate harness root-integrated at `7571cec` (OPTIONS-only; fail-closed; no coverage edits).
- Research90 reconfirms docs fingerprint and proves **OPTIONS cannot discriminate method support** (204 + full CORS Allow list on both closed and open routes). Next product slice is **Wave-5u method-level live observation**, not residual/bulk tools.
- Wave-5t UI/auth discovery fallback completed a login-only record at `871e6c6` but branch is seed-contaminated; login facts reconfirmed in research90 (English chrome, stable `name=` selectors). Do not merge the contaminated branch as-is.
- `BILLY_API_TOKEN` and UI secrets verified unset.

## Verification

- Research90 docs re-fetch: ETag `"wcw4x9hqvu3603"`, 147934 bytes, MD5 `8b94b0135c91fd15fe54ea33e088a4be` (byte-identical to research88/89).
- Method-level unauth residual/bulk/special matrix matches research89; OPTIONS **204** non-discriminative (new).
- `GET /user/organizations` unauth **404** `UNKNOWN_RESOURCE` (`Unknown resource \`v2/user/organizations\``).
- Coverage honesty: 184/184/0/0, `complete: false`.

## Review decisions (authoritative)

- Wave-5m through Wave-5s-C product: **ACCEPT offline only** where previously recorded.
- Research88 residual/bulk ranking: **ACCEPT as research** (review88).
- Research89: **ACCEPT as research** (review89).
- Wave-5t plan baseline / 142.20 management plan: **ACCEPT as planning** only.
- Wave-5t live-gate harness: **ACCEPT as infrastructure/research only** (review89); OPTIONS-only is explicitly non-qualifying; research90 strengthens that claim.
- Wave-5t UI discovery fallback research record: **not accepted** / branch intentionally held (seed contamination).
- Overall completeness: **FAIL**.

## Open coverage work

1. Implement Wave-5u method-level live residual/bulk observation upgrade (still fail-closed; still unqualified; no coverage green).
2. With dedicated non-production token + org: run method-level matrix; freeze only where methods and writable fields are proven.
3. Live prove or correct `GET /user/organizations` (unauth **404** vs docs + offline tool path).
4. UI/auth/vision qualification — credentials + dedicated org; EN+DA login labels.
5. Extract/review clean UI discovery brief without child-seed artifacts only if it adds beyond research90 login facts.

## Evidence boundaries

- Do not implement residual or bulk tools from Supports text, unauth 401 alone, PATCH meta-200, or OPTIONS 204.
- Do not green coverage from harness scaffolding or research.
- No webhooks (official 0 mentions; API 404).
- Do not claim vision or UI parity from login-only observation.

## References

- Research90: `.fractal/main.billy_complete/tmp/grok-research.md`
- Review89: `wiki/wave_fives_research89_independent_review.md`
- Residual ranking: `wiki/wave_fives_residual_specials_research.md`
- Probe rules: `wiki/offline_write_probe_rules.md`
- Plan: `.fractal/main.billy_complete/plans/2026-07-30T20:49:57.245Z-142.20-wave5t_harness_ui_management.md`
