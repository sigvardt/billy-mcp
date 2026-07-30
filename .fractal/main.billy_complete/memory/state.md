---
name: state
desc: Current node state, verified review decisions, and open qualification work.
tags: [billy, coverage, review]
sources:
  - docs/superpowers/specs/2026-07-28-billy-mcp-complete-design.md
  - https://www.billy.dk/api/
created: 2026-07-30T15:57:03Z
updated: 2026-07-31T00:36:00Z
---

# state

## Current state

- Wave-5c through Wave-5s-C write/special modules merged on root.
- All **6** specials offline producted; live false. Residual clear **29** red. Bulk **92** red. UI **339** red.
- Root offline coverage: **184** implemented + contract_tested. Live/vision **0**. `complete: false`.
- Wave-5t OPTIONS harness: infrastructure only.
- Wave-5u method-probe contract: every residual/bulk real-method candidate **BLOCK BEFORE NETWORK**.
- Typed `auth_status` at tip lineage with research91/92/93 submit signature (`button[data-cy=login-button]`, labels `Log in`|`Log ind`). Offline ACCEPT under review91. UI coverage stays red.
- Research92 freeze + research93 reconfirm: offline credential-store references + login pre-submit state machine is the product slice.
- Product leaf `auth_credentials_pre_submit_product` tip `b508477` claims ready by radio but review93 **REJECT merge**: `_LOGIN_SUBMIT_LABELS` wrongly allows `Login` instead of frozen `Log in` (tests teach `Login`). Real EN login would always `UI_CHANGED`.
- Repair leaf `auth_credentials_pre_submit_label_repair` is active on the rejected candidate base and owns only the exact-label correction in `browser.py` and its unit tests. No candidate code is merged on root.
- Live password submit, org picker, token bootstrap, residual/bulk networking remain blocked without dedicated non-production secrets and Grok re-review.
- Official docs fingerprint unchanged (ETag `wcw4x9hqvu3603`, MD5 `8b94b0135c91fd15fe54ea33e088a4be`).
- `BILLY_API_TOKEN` and UI secrets verified unset on the review runner.

## Verification

- Review93 docs re-fetch: ETag `"wcw4x9hqvu3603"`, 147934 bytes, MD5 `8b94b0135c91fd15fe54ea33e088a4be` (byte-identical to research93).
- Unauth matrix reconfirm: empty bulk `ids[]` → **400** `INVALID_DELETE_ID_ARRAY`; `GET /user/organizations` **404**; `GET /organizations` **401**; residual closed POST **405**; transactions POST **401**; bulk PUT **401**; bankPayments DELETE **405**.
- Live headless login: `https://mit.billy.dk/login`, title `Login`, button **`Log in`**; forms 0; captcha iframe 0; no submit.
- Coverage honesty: 184/184/0/0, `complete: false`. No greening from research or child product (coverage untouched on child).

## Review decisions (authoritative)

- Wave-5m through Wave-5s-C product: **ACCEPT offline only** where previously recorded.
- Research88–93: **ACCEPT as research** (prior reviews + review93).
- Wave-5t harness: **ACCEPT as infrastructure only**.
- Wave-5u plan/contract: **ACCEPT as planning/research only**; mandatory Grok gate remains open for product claims.
- Typed `auth_status` offline product: **ACCEPT** credential-absent only (review91); UI rows remain red.
- Research92/93 freezes: **ACCEPT as research** (review92/93); pre-submit product not accepted on root.
- Child product `b508477`: **REJECT merge** until submit labels restored to `Log in`|`Log ind` and tests fixed.
- Product repair: pending clean-archive audit, then a fresh Grok product independent review; no earlier research or pre-merge review grants product acceptance.
- Overall completeness: **FAIL**.

## Open coverage work

1. Product label-repair leaf → parent clean-archive review → Grok product IR against research92/93.
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
- Do not treat `ZERVANT_GOOGLE_CAPTCHA_*` bootstrap flags as `AUTH_INTERACTION_REQUIRED`.
- `Login` is only a possible page title; exact submit labels remain `Log in` and `Log ind`.

## References

- Research93: `.fractal/main.billy_complete/tmp/grok-research.md` (current research brief)
- Review93: `.fractal/main.billy_complete/tmp/grok-review.md` (current)
- Wiki IR: `wiki/wave_fives_research93_independent_review.md`
- Research92 freeze wiki: `wiki/auth_credentials_pre_submit_research.md`
- Review92: `wiki/wave_fives_research92_independent_review.md`
- Wave-5u contract: `wiki/wave5u_method_probe_contract.md`
- Residual ranking: `wiki/wave_fives_residual_specials_research.md`
