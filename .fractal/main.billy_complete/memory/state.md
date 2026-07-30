---
name: state
desc: Current node state, verified review decisions, and open qualification work.
tags: [billy, coverage, review]
sources:
  - docs/superpowers/specs/2026-07-28-billy-mcp-complete-design.md
  - https://www.billy.dk/api/
created: 2026-07-30T15:57:03Z
updated: 2026-07-30T23:00:23Z
---

# state

## Current state

- Wave-5c through Wave-5s-C write/special modules merged on root.
- All **6** specials offline producted; live false. Residual clear **29** red. Bulk **92** red. UI **339** red.
- Root offline coverage: **184** implemented + contract_tested. Live/vision **0**. `complete: false`.
- Root tip includes offline auth product: opaque browser credential references + `auth_login_start` / `auth_login_wait` with submit labels **`Log in`** / **`Log ind`**.
- Review94: **ACCEPT research94**; **ACCEPT offline product** on tip `a9c7a9b`. Completeness still **FAIL**.
- Typed `auth_status` remains offline ACCEPT (review91). UI coverage stays red.
- Wave-5t OPTIONS harness: infrastructure only.
- Wave-5u method-probe contract: every residual/bulk real-method candidate **BLOCK BEFORE NETWORK**.
- Live password submit, org picker, token bootstrap, residual/bulk networking remain blocked without dedicated non-production secrets and Grok re-review.
- Official docs fingerprint unchanged (ETag `wcw4x9hqvu3603`, MD5 `8b94b0135c91fd15fe54ea33e088a4be`).
- `BILLY_API_TOKEN` and UI secrets verified unset on the review runner.

## Verification

- Review94 docs re-fetch: ETag `"wcw4x9hqvu3603"`, 147934 bytes, MD5 `8b94b0135c91fd15fe54ea33e088a4be`, matching the current recorded contract fingerprint.
- Unauth matrix reconfirm: empty bulk `ids[]` → **400** `INVALID_DELETE_ID_ARRAY`; residual closed POST **405**; transactions POST **401**; bulk PUT **401**; bankPayments DELETE **405**; bankPayments bulk empty **405**; docs org path **404**.
- Live headless login: `https://mit.billy.dk/login`, title `Login`, button **`Log in`**; forms 0; captcha iframe 0; no submit.
- Focused offline auth suite: **39 passed** (`test_browser`, `test_config`, `test_models`).
- Coverage honesty: 184/184/0/0, `complete: false`. No greening from research or product.

## Review decisions (authoritative)

- Wave-5m through Wave-5s-C product: **ACCEPT offline only** where previously recorded.
- Research88–94: **ACCEPT as research**.
- Wave-5t harness: **ACCEPT as infrastructure only**.
- Wave-5u plan/contract: **ACCEPT as planning/research only**.
- Typed `auth_status` offline product: **ACCEPT** credential-absent only (review91); UI rows remain red.
- Research92 freeze wiki: **ACCEPT as research**.
- Offline auth credential pre-submit product on root: **ACCEPT offline only** (review94).
- Overall completeness: **FAIL**.

## Open coverage work

1. Dedicated non-production token + org before live residual/bulk or API `live_tested`.
2. Live prove or correct `GET /user/organizations` vs `/organizations`.
3. Optional Wave-5u harness encoding BLOCK-BEFORE-NETWORK including bulk delete query form candidates (still no product tools).
4. Full UI parity + vision under non-prod org.
5. Close or absorb sibling product-review child if it only duplicates review94.

## Evidence boundaries

- Do not implement residual or bulk tools from Supports text, unauth 401, meta-200, OPTIONS 204, or empty bulk arrays.
- Do not network residual/bulk real methods without reviewed non-persistence proof.
- Do not green coverage from research, harness scaffolding, or offline auth tools.
- No webhooks (official 0 mentions).
- Codex fallback cannot alone close a mandatory Grok product gate.
- Do not accept email/password/TOTP/token as MCP tool inputs; references only.
- Do not treat `ZERVANT_GOOGLE_CAPTCHA_*` bootstrap flags as `AUTH_INTERACTION_REQUIRED`.
- `Login` is only a possible page title; exact submit labels remain `Log in` and `Log ind`.
- Empty bulk `ids[]` is an error (`INVALID_DELETE_ID_ARRAY`), not a no-op.
- Offline product ACCEPT does not authorise CI live password submit without non-prod secrets + fresh Grok re-review.

## References

- Research94: `.fractal/main.billy_complete/tmp/grok-research.md`
- Review94: `.fractal/main.billy_complete/tmp/grok-review.md`
- Wiki IR: `wiki/wave_fives_research94_independent_review.md`
- Research freeze wiki: `wiki/auth_credentials_pre_submit_research.md`
- Wave-5u contract: `wiki/wave5u_method_probe_contract.md`
- Residual ranking: `wiki/wave_fives_residual_specials_research.md`
