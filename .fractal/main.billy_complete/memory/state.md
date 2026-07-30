---
name: state
desc: Current node state, verified review decisions, and open qualification work.
tags: [billy, coverage, review]
sources:
  - docs/superpowers/specs/2026-07-28-billy-mcp-complete-design.md
  - https://www.billy.dk/api/
created: 2026-07-30T15:57:03Z
updated: 2026-07-30T21:28:00Z
---

# state

## Current state

- Wave-5c through Wave-5s-C write/special modules merged on root (email + delivery at `0efceae`).
- All **6** specials offline producted; live false. Residual clear **29** red. Bulk **92** red. UI **339** red.
- Root offline coverage: **184** implemented + contract_tested. Live/vision **0**. `complete: false`.
- Wave-5t live-gate harness root-integrated (OPTIONS-only; fail-closed; infrastructure only).
- Research90 + Wave-5u plan on tip `ee46c3f`. Review90 **ACCEPTS research90 and Wave-5u plan as research/planning only**; overall completeness **FAIL**.
- OPTIONS proven non-discriminative (independent review reproduction). Method-level Wave-5u implementation **not** on root yet.
- `BILLY_API_TOKEN` and UI secrets verified unset.

## Verification

- Review90 docs re-fetch: ETag `"wcw4x9hqvu3603"`, 147934 bytes, MD5 `8b94b0135c91fd15fe54ea33e088a4be` (byte-identical to research90).
- Independent unauth: OPTIONS 204 non-discriminative; residual method matrix matches research90; `GET /user/organizations` **404**.
- Residual/bulk candidate matrix exact match to inventory (29+92).
- Coverage honesty: 184/184/0/0, `complete: false`.
- Local verification: wiki lint has no actionable issue; repository lint passes;
  **1,265** tests pass with one live test deselected.  Full live qualification
  remains intentionally unrun because its required credentials and test-org
  guard are absent.

## Review decisions (authoritative)

- Wave-5m through Wave-5s-C product: **ACCEPT offline only** where previously recorded.
- Research88 residual/bulk ranking: **ACCEPT as research** (review88).
- Research89: **ACCEPT as research** (review89).
- Wave-5t plan / harness: **ACCEPT as planning / infrastructure only** (review89).
- Research90: **ACCEPT as research** (review90).
- Wave-5u plan 142.21: **ACCEPT as planning only** (review90).
- Wave-5t UI discovery fallback: **not accepted** / branch held (seed contamination).
- Overall completeness: **FAIL**.

## Open coverage work

1. Wave-5u contract leaf: freeze non-mutating method-observation shapes; reconcile associations delete singular vs `ids[]`.
2. Wave-5u Codex implementation: replace OPTIONS with candidate methods under fail-closed gates; no tools; no coverage green.
3. With dedicated non-production token + org: run method-level matrix; freeze only where methods and writable fields are proven.
4. Live prove or correct `GET /user/organizations` (unauth **404** vs docs + offline tool path).
5. UI/auth/vision qualification — credentials + dedicated org; EN+DA login labels.

## Evidence boundaries

- Do not implement residual or bulk tools from Supports text, unauth 401 alone, PATCH meta-200, or OPTIONS 204.
- Do not green coverage from harness scaffolding or research.
- No webhooks (official 0 mentions; API 404).
- Do not claim vision or UI parity from login-only observation.
- Codex fallback for a Grok-required gate cannot alone close that gate.

## References

- Research90: `.fractal/main.billy_complete/tmp/grok-research.md`
- Review90: `.fractal/main.billy_complete/tmp/grok-review.md`
- Wiki IR: `wiki/wave_fives_research90_independent_review.md`
- Residual ranking: `wiki/wave_fives_residual_specials_research.md`
- Probe rules: `wiki/offline_write_probe_rules.md`
- Plan: `.fractal/main.billy_complete/plans/2026-07-30T21:14:49.522Z-142.21-wave5u_method_level_observation.md`
