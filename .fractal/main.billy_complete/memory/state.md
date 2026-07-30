---
name: state
desc: Current node state, verified review decisions, and open qualification work.
tags: [billy, coverage, review]
sources:
  - docs/superpowers/specs/2026-07-28-billy-mcp-complete-design.md
  - https://www.billy.dk/api/
created: 2026-07-30T15:57:03Z
updated: 2026-07-30T21:55:00Z
---

# state

## Current state

- Wave-5c through Wave-5s-C write/special modules merged on root.
- All **6** specials offline producted; live false. Residual clear **29** red. Bulk **92** red. UI **339** red.
- Root offline coverage: **184** implemented + contract_tested. Live/vision **0**. `complete: false`.
- Wave-5t OPTIONS harness: infrastructure only.
- Wave-5u method-probe contract: every residual/bulk real-method candidate **BLOCK BEFORE NETWORK**.
- Typed `auth_status` integrated at tip `cf38b5c` with research91 submit signature (`button[data-cy=login-button]`, labels `Log in`|`Log ind`). Offline ACCEPT under review91. UI coverage stays red.
- Dedicated Grok leaves cannot currently start because the runner lacks authentication. Review91 was delivered separately and accepts the offline slice; a bounded Codex fallback is researching credentials/login/organisation but cannot close a mandatory Grok gate.
- No residual/bulk product without dedicated non-production credentials and non-persistence safety proof.
- `BILLY_API_TOKEN` and UI secrets verified unset.

## Verification

- Review91 docs re-fetch: ETag `"wcw4x9hqvu3603"`, 147934 bytes, MD5 `8b94b0135c91fd15fe54ea33e088a4be` (byte-identical to research91).
- Independent unauth matrix matches research91; empty bulk `ids[]` → **400**; `GET /user/organizations` **404**; `GET /organizations` **401**.
- Independent live headless `auth_status` → `AUTH_REQUIRED` (Danish `Log ind`); `button[type=submit]` count 0.
- Unit: auth model/browser tests **19 passed**; auth server registration tests pass.
- Coverage honesty: 184/184/0/0, `complete: false`. No greening.
- Raw review scratch captures and generated probe scripts were purged; node scratch retains only non-sensitive Markdown briefs.

## Review decisions (authoritative)

- Wave-5m through Wave-5s-C product: **ACCEPT offline only** where previously recorded.
- Research88–90: **ACCEPT as research** (prior reviews).
- Wave-5t harness: **ACCEPT as infrastructure only**.
- Wave-5u plan/contract: **ACCEPT as planning/research only**; mandatory Grok gate remains open for product claims.
- Research91: **ACCEPT as research** (review91).
- Typed `auth_status` offline product: **ACCEPT** credential-absent only (review91); UI rows remain red.
- Overall completeness: **FAIL**.

## Open coverage work

1. Credentialed login / org selection / token bootstrap slices after secure material is available outside git.
2. Dedicated non-production token + org before live residual/bulk or API `live_tested`.
3. Live prove or correct `GET /user/organizations` vs `/organizations`.
4. Optional Wave-5u harness encoding BLOCK-BEFORE-NETWORK (still no product tools).
5. Full UI parity + vision under non-prod org.

## Evidence boundaries

- Do not implement residual or bulk tools from Supports text, unauth 401, meta-200, OPTIONS 204, or empty bulk arrays.
- Do not network residual/bulk real methods without reviewed non-persistence proof.
- Do not green coverage from research, harness scaffolding, or login-only `auth_status`.
- No webhooks (official 0 mentions).
- Codex fallback cannot alone close a mandatory Grok product gate.

## References

- Research91: `.fractal/main.billy_complete/tmp/grok-research.md`
- Review91: `.fractal/main.billy_complete/tmp/grok-review.md`
- Wiki IR: `wiki/wave_fives_research91_independent_review.md`
- Wave-5u contract: `wiki/wave5u_method_probe_contract.md`
- Residual ranking: `wiki/wave_fives_residual_specials_research.md`
