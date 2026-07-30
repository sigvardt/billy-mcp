---
name: state
desc: Current node state, verified review decisions, and open qualification work.
tags: [billy, coverage, review]
sources:
  - docs/superpowers/specs/2026-07-28-billy-mcp-complete-design.md
  - https://www.billy.dk/api/
created: 2026-07-30T15:57:03Z
updated: 2026-07-30T23:20:00Z
---

# state

## Current state

- Wave-5c through Wave-5s-C write/special modules merged on root.
- All **6** specials offline producted; live false. Residual clear **29** red. Bulk **92** red. UI **339** red.
- Root offline coverage: **184** implemented + contract_tested. Live/vision **0**. `complete: false`.
- Root tip includes offline auth product: opaque browser credential references + `auth_login_start` / `auth_login_wait` with submit labels **`Log in`** / **`Log ind`**.
- Review94: **ACCEPT research94**; **ACCEPT offline product** on tip lineage `a9c7a9b` (current tip includes review acceptance). Completeness still **FAIL**.
- Review95: **ACCEPT research95** as research only; wiki form-matrix promotion ACCEPT as research; harness encode not on root; completeness FAIL.
- Research95: docs body still byte-identical (ETag `wcw4x9hqvu3603`, MD5 `8b94b0135c91fd15fe54ea33e088a4be`). New bulk-delete form matrix: empty `ids[]` → **400** `INVALID_DELETE_ID_ARRAY`; synthetic non-empty id unauth → **200** meta-only (not a live safety proof). EN/DA login labels reconfirmed.
- Typed `auth_status` remains offline ACCEPT (review91). UI coverage stays red.
- Wave-5t OPTIONS harness: infrastructure only.
- Wave-5u method-probe contract: every residual/bulk real-method candidate **BLOCK BEFORE NETWORK**.
- Live password submit, org picker, token bootstrap, residual/bulk networking remain blocked without dedicated non-production secrets and Grok re-review.
- `BILLY_API_TOKEN` and UI secrets verified unset on the research runner.

## Verification

- Review95 docs re-fetch: ETag `"wcw4x9hqvu3603"`, 147934 bytes, MD5 `8b94b0135c91fd15fe54ea33e088a4be`, byte-identical to research95 and research92–94.
- Review95 unauth matrix (31 cases, 0 mismatches): empty bulk `ids[]` → **400** `INVALID_DELETE_ID_ARRAY`; synthetic id → **200** meta; residual closed POST **405**; transactions POST **401**; bankPayments DELETE **405**; docs org path **404**.
- Review95 headless login: EN title `Login` / submit **`Log in`**; DA title `Log ind` / submit **`Log ind`**; forms 0; captcha iframe 0; no submit of credentials.
- Focused offline suite browser+config+live_probe: **45 passed**.
- Coverage honesty: 184/184/0/0, `complete: false`. No greening from research or product.

## Review decisions (authoritative)

- Wave-5m through Wave-5s-C product: **ACCEPT offline only** where previously recorded.
- Research88–95: **ACCEPT as research** (review95 closed research95 independently).
- Wave-5t harness: **ACCEPT as infrastructure only**.
- Wave-5u plan/contract and research95 form-matrix wiki: **ACCEPT as planning/research only**.
- Wave-5u form-matrix harness code on root: **not present** (child in progress; not product ACCEPT).
- Typed `auth_status` offline product: **ACCEPT** credential-absent only (review91); UI rows remain red.
- Research92 freeze wiki: **ACCEPT as research**.
- Offline auth credential pre-submit product on root: **ACCEPT offline only** (review94; reconfirmed labels review95).
- Overall completeness: **FAIL**.

## Open coverage work

1. Dedicated non-production token + org before live residual/bulk or API `live_tested`.
2. Live prove or correct `GET /user/organizations` vs `/organizations`.
3. Optional Wave-5u harness encode of research95 bulk-delete form matrix (empty error vs synthetic meta-200) while every real method stays **BLOCK BEFORE NETWORK** — still no product tools.
4. Full UI parity + vision under non-prod org.

## Evidence boundaries

- Do not implement residual or bulk tools from Supports text, unauth 401, meta-200, OPTIONS 204, empty bulk arrays, or synthetic-id bulk 200.
- Empty bulk `ids[]` is an error (`INVALID_DELETE_ID_ARRAY`), not a no-op.
- Synthetic non-empty bulk-delete meta-200 unauth is not authenticated non-persistence proof.
- Do not network residual/bulk real methods without reviewed non-persistence proof.
- Do not green coverage from research, harness scaffolding, or offline auth tools.
- No webhooks (official 0 mentions).
- Codex fallback cannot alone close a mandatory Grok product gate.
- Do not accept email/password/TOTP/token as MCP tool inputs; references only.
- Do not treat `ZERVANT_GOOGLE_CAPTCHA_*` bootstrap flags as `AUTH_INTERACTION_REQUIRED`.
- `Login` is only a possible page title; exact submit labels remain `Log in` and `Log ind`.
- Offline product ACCEPT does not authorise CI live password submit without non-prod secrets + fresh Grok re-review.

## References

- Review95: `.fractal/main.billy_complete/tmp/grok-review.md`
- Wiki IR research95: `wiki/wave_fives_research95_independent_review.md`
- Research95 brief: `.fractal/main.billy_complete/tmp/grok-research.md`
- Wiki IR research94: `wiki/wave_fives_research94_independent_review.md`
- Research freeze wiki: `wiki/auth_credentials_pre_submit_research.md`
- Wave-5u contract: `wiki/wave5u_method_probe_contract.md`
- Residual ranking: `wiki/wave_fives_residual_specials_research.md`
