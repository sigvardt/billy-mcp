---
name: state
desc: Current node state, verified review decisions, and open qualification work.
tags: [billy, coverage, review]
sources:
  - docs/superpowers/specs/2026-07-28-billy-mcp-complete-design.md
  - https://www.billy.dk/api/
created: 2026-07-30T15:57:03Z
updated: 2026-07-30T21:50:00Z
---

# state

## Current state

- Wave-5c through Wave-5s-C write/special modules merged on root (email + delivery at `0efceae`).
- All **6** specials offline producted; live false. Residual clear **29** red. Bulk **92** red. UI **339** red.
- Root offline coverage: **184** implemented + contract_tested. Live/vision **0**. `complete: false`.
- Wave-5t live-gate harness root-integrated (OPTIONS-only; fail-closed; infrastructure only).
- Wave-5u method-probe contract preserved as research-only: every residual/bulk real-method candidate is **BLOCK BEFORE NETWORK**. No tool, live probe product, or coverage change.
- Typed `auth_status` is integrated as a fixed-root, headless, read-only login-signature check. It returns only `AUTH_REQUIRED`, `UI_CHANGED`, `EGRESS_DENIED`, or redacted `BILLY_ERROR`; independent Grok review is still required and UI coverage stays red.
- Research91 freezes the login signature: email/password/remember `name=` controls stay stable; submit is `button[data-cy=login-button]` with exact labels `Log in`|`Log ind`. Live DOM has **no** `type="submit"` attribute and **no** wrapping `<form>`, so `button[type=submit]` is a false `UI_CHANGED` defect if left in the leaf.
- No residual/bulk offline-observation or product wave may begin without dedicated non-production credentials and a later non-persistence safety proof.
- `BILLY_API_TOKEN` and UI secrets verified unset this research pass.

## Verification

- Research91 docs re-fetch: ETag `"wcw4x9hqvu3603"`, 147934 bytes, MD5 `8b94b0135c91fd15fe54ea33e088a4be` (byte-identical to research90).
- Independent unauth: OPTIONS 204 non-discriminative; residual method matrix matches prior; empty bulk `ids[]` → **400** `INVALID_DELETE_ID_ARRAY`; `GET /user/organizations` **404**; `GET /organizations` **401**.
- Headless login: final `https://mit.billy.dk/login`, title `Log ind`, no CAPTCHA; submit `data-cy=login-button` text `Log ind`.
- Coverage honesty: 184/184/0/0, `complete: false`. No greening from research.

## Review decisions (authoritative)

- Wave-5m through Wave-5s-C product: **ACCEPT offline only** where previously recorded.
- Research88 residual/bulk ranking: **ACCEPT as research** (review88).
- Research89: **ACCEPT as research** (review89).
- Wave-5t plan / harness: **ACCEPT as planning / infrastructure only** (review89).
- Research90: **ACCEPT as research** (review90).
- Wave-5u plan: **ACCEPT as planning only** (review90); Codex fallback contract remains research-only and awaits the mandatory Grok gate.
- Wave-5t UI discovery fallback: preserved as bounded login discovery only; qualifies no UI coverage.
- Research91: **research record for next slice** (auth_status signature freeze + live-gate reconfirm); not completeness.
- Overall completeness: **FAIL**.

## Open coverage work

1. Complete the independent Grok review for typed `auth_status`; keep UI coverage red.
2. Plan secure credential resolution, typed login, and organisation-selection slices from observed non-production DOM states.
3. Provision a dedicated non-production token and organisation before any live API/UI qualification; then run safe matrix evidence and cleanup/read-back.
4. Live prove or correct `GET /user/organizations` (unauth **404** vs docs; alternate `GET /organizations` unauth **401**).
5. Optional Wave-5u harness encoding BLOCK-BEFORE-NETWORK for all residual/bulk candidates (still no product tools).
6. UI/auth/vision qualification beyond login — credentials + dedicated org.

## Evidence boundaries

- Do not implement residual or bulk tools from Supports text, unauth 401 alone, PATCH/meta-200, OPTIONS 204, or empty bulk arrays.
- Do not network residual/bulk real methods until a reviewed non-persistence proof exists (Wave-5u contract).
- Do not green coverage from harness scaffolding or research.
- No webhooks (official 0 mentions; API 404).
- Do not claim vision or UI parity from login-only observation.
- Codex fallback for a Grok-required gate cannot alone close that gate.
- `button[type=submit]` is not a valid Billy login submit signature.

## References

- Research91: `.fractal/main.billy_complete/tmp/grok-research.md`
- Review90: `.fractal/main.billy_complete/tmp/grok-review.md`
- Wiki IR: `wiki/wave_fives_research90_independent_review.md`
- Wave-5u contract: `wiki/wave5u_method_probe_contract.md`
- Residual ranking: `wiki/wave_fives_residual_specials_research.md`
- Probe rules: `wiki/offline_write_probe_rules.md`
- Plan: `.fractal/main.billy_complete/plans/2026-07-30T21:14:49.522Z-142.21-wave5u_method_level_observation.md`
