---
name: state
desc: Current node state, verified review decisions, and open qualification work.
tags: [billy, coverage, review]
sources:
  - docs/superpowers/specs/2026-07-28-billy-mcp-complete-design.md
  - https://www.billy.dk/api/
created: 2026-07-30T15:57:03Z
updated: 2026-07-31T00:22:00Z
---

# state

## Current state

- Wave-5c through Wave-5s-C write/special modules merged on root.
- All **6** specials offline producted; live false. Residual clear **29** red. Bulk **92** red. UI **339** red.
- Root offline coverage: **184** implemented + contract_tested. Live/vision **0**. `complete: false`.
- Wave-5t OPTIONS harness: infrastructure only.
- Wave-5u method-probe contract: every residual/bulk real-method candidate **BLOCK BEFORE NETWORK**.
- Typed `auth_status` at tip `cf38b5c` / IR `853d309` with research91/92 submit signature (`button[data-cy=login-button]`, labels `Log in`|`Log ind`). Offline ACCEPT under review91. UI coverage stays red.
- Research92 freezes next product slice: offline credential-store references + login pre-submit state machine only. Live password submit, org picker, token bootstrap, residual/bulk networking remain blocked without dedicated non-production secrets and Grok re-review.
- Official docs fingerprint unchanged (ETag `wcw4x9hqvu3603`, MD5 `8b94b0135c91fd15fe54ea33e088a4be`).
- `BILLY_API_TOKEN` and UI secrets verified unset on the research runner.
- Codex fallback wiki for credentials/login/org is planning only and does not replace the Grok research92 brief or product gates.

## Verification

- Research92 docs re-fetch: ETag `"wcw4x9hqvu3603"`, 147934 bytes, MD5 `8b94b0135c91fd15fe54ea33e088a4be` (byte-identical to research91/review91).
- Unauth matrix reconfirm: empty bulk `ids[]` → **400** `INVALID_DELETE_ID_ARRAY`; `GET /user/organizations` **404**; `GET /organizations` **401**; residual closed POST **405**; transactions POST **401**.
- Live headless `auth_status` → `AUTH_REQUIRED` (Danish `Log ind`); `button[type=submit]` count 0; no CAPTCHA/passkey.
- Coverage honesty: 184/184/0/0, `complete: false`. No greening from research.
- Review92 independent: docs byte-identical; unauth matrix matches; live auth_status AUTH_REQUIRED; tip freeze has no src/coverage greening.

## Review decisions (authoritative)

- Wave-5m through Wave-5s-C product: **ACCEPT offline only** where previously recorded.
- Research88–90: **ACCEPT as research** (prior reviews).
- Wave-5t harness: **ACCEPT as infrastructure only**.
- Wave-5u plan/contract: **ACCEPT as planning/research only**; mandatory Grok gate remains open for product claims.
- Research91: **ACCEPT as research** (review91).
- Typed `auth_status` offline product: **ACCEPT** credential-absent only (review91); UI rows remain red.
- Research92: **research-only** credential/login/org freeze; not product ACCEPT.
- Review92: **ACCEPT research92 + tip research freeze as research only**; pre-submit product not present; overall FAIL.
- Overall completeness: **FAIL**.

## Open coverage work

1. Offline credential-reference + login pre-submit state machine (research92); live submit/org/bootstrap only after non-prod secrets + Grok re-review.
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
- Do not accept email/password/TOTP/token as MCP tool inputs; references only.

## References

- Research92: `.fractal/main.billy_complete/tmp/grok-research.md` (current research brief)
- Review92: `.fractal/main.billy_complete/tmp/grok-review.md` (current)
- Wiki IR: `wiki/wave_fives_research92_independent_review.md`
- Review91: superseded scratch by review92; offline auth_status ACCEPT still holds
- Wiki IR: `wiki/wave_fives_research91_independent_review.md`
- Codex credentials planning fallback: completed node record reconciled in
  `wiki/auth_credentials_pre_submit_research.md`; it remains non-authoritative
  and is not a Grok gate
- Wave-5u contract: `wiki/wave5u_method_probe_contract.md`
- Residual ranking: `wiki/wave_fives_residual_specials_research.md`
