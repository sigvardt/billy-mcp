---
name: state
desc: Current node state, verified review decisions, and open qualification work.
tags: [billy, coverage, review]
sources:
  - docs/superpowers/specs/2026-07-28-billy-mcp-complete-design.md
  - https://www.billy.dk/api/
created: 2026-07-30T15:57:03Z
updated: 2026-07-30T20:45:00Z
---

# state

## Current state

- Wave-5c through Wave-5s-C write/special modules merged on root (email + delivery at `0efceae`).
- All **6** specials offline producted; live false. Residual clear **29** red. Bulk **92** red. UI **339** red.
- Root offline coverage: **184** implemented + contract_tested. Live/vision **0**. `complete: false`.
- Research88 + Wave-5t plan baseline committed at `23dae67`. Review88 **ACCEPT as research** only.
- Research89 reconfirm (docs byte-identical; residual/bulk gates unchanged; login English chrome; unauth `GET /user/organizations` **404** live risk) written to node `tmp/grok-research.md`.
- Wave-5t live-gate harness and Codex UI/auth discovery fallback remain active. No residual/bulk tools on root.
- `BILLY_API_TOKEN` and UI secrets verified unset.

## Verification

- Research89 docs re-fetch: ETag `"wcw4x9hqvu3603"`, 147934 bytes, MD5 `8b94b0135c91fd15fe54ea33e088a4be` (byte-identical to research88).
- Independent unauth residual/bulk probes (119 cases) match research88 gates; PATCH collection meta-200 still not a contract.
- Headless login: `mit.billy.dk/login`, title `Login`, fields `email`/`password`/`remember`, submit text `Log in` (EN).
- Coverage honesty: 184/184/0/0, `complete: false`.

## Review decisions (authoritative)

- Wave-5m through Wave-5s-C product: **ACCEPT offline only** where previously recorded.
- Research88 residual/bulk live-gate ranking: **ACCEPT as research** (review88).
- Research89: research reconfirm only; not product ACCEPT.
- Wave-5t plan baseline: **ACCEPT as planning** only; not product ACCEPT.
- Wave-5t harness/UI product: **not accepted** (not merged).
- Overall completeness: **FAIL**.

## Open coverage work

1. Finish and independently review Wave-5t live-gate harness + UI/auth discovery leaves; merge only after tests + independent review.
2. Residual clear 29 and bulk 92 — live token + non-prod org required; encode matrix in harness first.
3. Live prove or correct `GET /user/organizations` (unauth **404** vs docs + offline tool path).
4. UI/auth/vision qualification — credentials + dedicated org; support EN+DA login labels.
5. Live qualification for high side-effect specials on non-production org only.

## Evidence boundaries

- Do not implement residual or bulk tools from Supports text, unauth 401 alone, or PATCH meta-200.
- Do not green coverage from harness scaffolding or research.
- No webhooks (official 0 mentions; API 404).
- Do not claim vision or UI parity from login-only observation.

## References

- Research89: `.fractal/main.billy_complete/tmp/grok-research.md`
- Review88: `.fractal/main.billy_complete/tmp/grok-review.md`
- Wiki IR: `wiki/wave_fives_research88_independent_review.md`
- Residual ranking: `wiki/wave_fives_residual_specials_research.md`
- Probe rules: `wiki/offline_write_probe_rules.md`
- Plan: `.fractal/main.billy_complete/plans/2026-07-30T20:24:26.315Z-142.19-wave5t_live_gate_harness.md`
