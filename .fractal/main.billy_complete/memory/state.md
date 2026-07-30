---
name: state
desc: Current node state, verified review decisions, and open qualification work.
tags: [billy, coverage, review]
sources:
  - docs/superpowers/specs/2026-07-28-billy-mcp-complete-design.md
  - https://www.billy.dk/api/
created: 2026-07-30T15:57:03Z
updated: 2026-07-30T23:35:00Z
---

# state

## Current state

- Wave-5c through Wave-5s-C write/special modules merged on root.
- All **6** specials offline producted; live false. Residual clear **29** red. Bulk **92** red. UI **339** red.
- Root offline coverage: **184** implemented + contract_tested. Live/vision **0**. `complete: false`.
- Root tip includes offline auth product and Wave-5u form-matrix harness (`2d3b501`).
- Offline auth: `auth_status` / `auth_login_start` / `auth_login_wait` with submit labels **`Log in`** / **`Log ind`** (ACCEPT offline only).
- Research96: docs body still byte-identical (ETag `wcw4x9hqvu3603`, MD5 `8b94b0135c91fd15fe54ea33e088a4be`). New: bulk-delete server form `DELETE /R?ids[]=123&ids[]=456`; no-token `GET /user/organizations` is **404 UNKNOWN_RESOURCE** while `/organizations` is **401**; garbage-token **401** is auth-first and does not prove path existence.
- UI coverage stays red. Completeness **FAIL**.
- Wave-5t OPTIONS harness: infrastructure only.
- Wave-5u: every residual/bulk real-method candidate **BLOCK BEFORE NETWORK**.
- Live password submit, org picker, token bootstrap, residual/bulk networking remain blocked without dedicated non-production secrets and Grok re-review.
- `BILLY_API_TOKEN` and UI secrets verified unset on the research runner.

## Verification

- Research96 docs re-fetch: ETag `"wcw4x9hqvu3603"`, 147934 bytes, MD5 `8b94b0135c91fd15fe54ea33e088a4be`, byte-identical to research92–95.
- Research96 unauth matrix: residual 405/401/meta-200 unchanged; bulk empty `ids[]` → **400** with message stating form `DELETE /contacts?ids[]=123&ids[]=456`; JSON/form body bulk-delete rejected; garbage token → `OAUTH_INVALID_ACCESS_TOKEN` (LOGGER-prefixed JSON; `parse_billy_json` handles).
- Research96 headless login: EN title `Login` / submit **`Log in`**; DA title `Log ind` / submit **`Log ind`**; forms 0; captcha iframe 0; no submit of credentials.
- Coverage honesty: 184/184/0/0, `complete: false`. No greening from research.

## Review decisions (authoritative)

- Wave-5m through Wave-5s-C product: **ACCEPT offline only** where previously recorded.
- Research88–95: **ACCEPT as research** (review95 closed research95 independently).
- Research96: research brief written; awaiting independent review.
- Wave-5t harness: **ACCEPT as infrastructure only**.
- Wave-5u plan/contract and form-matrix harness on tip: **ACCEPT as infrastructure/research encode only** (not residual/bulk product).
- Typed `auth_status` offline product: **ACCEPT** credential-absent only (review91); UI rows remain red.
- Offline auth credential pre-submit product on root: **ACCEPT offline only** (review94; labels reconfirmed research95–96).
- Overall completeness: **FAIL**.

## Open coverage work

1. Dedicated non-production token + org before live residual/bulk or API `live_tested`.
2. Live prove or correct `GET /user/organizations` vs `/organizations` with a **valid** token (do not rewrite from unauth 404 alone).
3. Optional Wave-5u residual unauth gate + bulk-delete canonical-form fixture encode (research96 recommended slice) while every real method stays **BLOCK BEFORE NETWORK** — still no product tools.
4. Full UI parity + vision under non-prod org.
5. Remaining design auth tools (reauth, org list/select, token bootstrap, logout) after post-login discovery.

## Evidence boundaries

- Do not implement residual or bulk tools from Supports text, unauth 401, meta-200, OPTIONS 204, empty bulk arrays, or synthetic-id bulk 200.
- Empty bulk `ids[]` is an error (`INVALID_DELETE_ID_ARRAY`), not a no-op. Server states query form `ids[]` only.
- JSON/body bulk-delete forms are rejected unauth; do not product them.
- Synthetic non-empty bulk-delete meta-200 unauth is not authenticated non-persistence proof.
- Garbage-token 401 is auth-first and path-agnostic; it does not prove `/user/organizations` exists.
- No-token 404 on `/user/organizations` does not alone rewrite the docs path offline.
- Do not network residual/bulk real methods without reviewed non-persistence proof.
- Do not green coverage from research, harness scaffolding, or offline auth tools.
- No webhooks (official 0 mentions).
- Codex fallback cannot alone close a mandatory Grok product gate.
- Do not accept email/password/TOTP/token as MCP tool inputs; references only.
- Do not treat `ZERVANT_GOOGLE_CAPTCHA_*` bootstrap flags as `AUTH_INTERACTION_REQUIRED`.
- `Login` is only a possible page title; exact submit labels remain `Log in` and `Log ind`.
- Offline product ACCEPT does not authorise CI live password submit without non-prod secrets + fresh Grok re-review.

## References

- Research96 brief: `.fractal/main.billy_complete/tmp/grok-research.md`
- Review95: `wiki/wave_fives_research95_independent_review.md`
- Wave-5u contract: `wiki/wave5u_method_probe_contract.md`
- Residual ranking: `wiki/wave_fives_residual_specials_research.md`
- Research freeze wiki: `wiki/auth_credentials_pre_submit_research.md`
