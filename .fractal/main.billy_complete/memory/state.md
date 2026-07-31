---
name: state
desc: Current node state, verified review decisions, and open qualification work.
tags: [billy, coverage, review]
sources:
  - docs/superpowers/specs/2026-07-28-billy-mcp-complete-design.md
  - https://www.billy.dk/api/
created: 2026-07-30T15:57:03Z
updated: 2026-07-31T00:00:00Z
---

# state

## Current state

- Wave-5c through Wave-5s-C write/special modules merged on root.
- All **6** specials offline producted; live false. Residual clear **29** red. Bulk **92** red. UI **339** red.
- Root offline coverage: **184** implemented + contract_tested. Live/vision **0**. `complete: false`.
- Offline auth: `auth_status` / `auth_login_start` / `auth_login_wait` with submit labels **`Log in`** / **`Log ind`** (ACCEPT offline only).
- Research96 ACCEPT as research (review96). Research97 reconfirm: docs still byte-identical; full residual-29 unauth matrix (25×405, 2×401 transactions C/U, 2×meta-200 deletes); bulk open/closed classes (save 401 vs 405; delete empty 400 vs 405); DA login needs Playwright locale + Accept-Language (not query alone).
- Research96 residual-gate fixture child **completed** @ `6099f20` on `wave5u_research96_harness`; **not merged** to parent tip. Form-matrix infrastructure ACCEPT only.
- Research97 next slices: (A) merge + IR Research96 harness; (B) encode bulk open/closed class fixtures; still no residual/bulk product tools.
- UI coverage stays red. Completeness **FAIL**.
- Wave-5u: every residual/bulk real-method candidate **BLOCK BEFORE NETWORK**.
- Live residual/bulk/UI remain blocked without dedicated non-production secrets.
- `BILLY_API_TOKEN` and UI secrets verified unset on the research runner.

## Verification

- Research97 docs re-fetch: ETag `"wcw4x9hqvu3603"`, 147934 bytes, MD5 `8b94b0135c91fd15fe54ea33e088a4be`, byte-identical to research96.
- Research97 residual matrix: all **29** inventory ids probed; classifications in `tmp/write-probes-research97.json`.
- Research97 bulk class sample: **30** resources in `tmp/bulk-class-matrix-research97.json`.
- Research97 headless login: EN `Log in` / DA `Log ind` with context locale; forms 0; captcha iframe 0; no credential submit.
- Coverage honesty: 184/184/0/0, `complete: false`. No greening from research or harness.

## Review decisions (authoritative)

- Wave-5m through Wave-5s-C product: **ACCEPT offline only** where previously recorded.
- Research88–96: **ACCEPT as research** (review96 closed research96 independently).
- Research97: research brief only (pending independent review); completeness **FAIL**.
- Wave-5t harness: **ACCEPT as infrastructure only**.
- Wave-5u form-matrix harness: **ACCEPT as infrastructure only** (not residual/bulk product).
- Research96 residual-gate fixture encode: child completed, **not ACCEPT on parent** until merge + IR.
- Typed `auth_status` offline product: **ACCEPT** credential-absent only (review91); UI rows remain red.
- Offline auth credential pre-submit product on root: **ACCEPT offline only** (review94; labels reconfirmed through research97).
- Overall completeness: **FAIL**.

## Open coverage work

1. Dedicated non-production token + org before live residual/bulk or API `live_tested`.
2. Live prove or correct `GET /user/organizations` vs `/organizations` with a **valid** token (do not rewrite from unauth 404 alone).
3. Merge and independently review Research96 residual unauth gate + bulk-delete canonical-form fixtures; then encode research97 bulk open/closed class fixtures. Real methods stay **BLOCK BEFORE NETWORK**. No product tools.
4. Full UI parity + vision under non-prod org.
5. Remaining design auth tools (reauth, org list/select, token bootstrap, logout) after post-login discovery.

## Evidence boundaries

- Do not implement residual or bulk tools from Supports text, unauth 401, meta-200, OPTIONS 204, empty bulk arrays, or synthetic-id bulk 200.
- Empty bulk `ids[]` is an error (`INVALID_DELETE_ID_ARRAY`), not a no-op. Server states query form `ids[]` only.
- JSON/body bulk-delete forms are rejected unauth; do not product them.
- Bulk-save/bulk-delete unauth open/closed classes are research fixtures only, not product authority.
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
- Danish login discovery requires browser context locale + Accept-Language; query `?locale=` alone is insufficient.
- Offline product ACCEPT does not authorise CI live password submit without non-prod secrets + fresh Grok re-review.

## References

- Research97 brief: `.fractal/main.billy_complete/tmp/grok-research.md`
- Review96: `wiki/wave_fives_research96_independent_review.md`
- Review95: `wiki/wave_fives_research95_independent_review.md`
- Wave-5u contract: `wiki/wave5u_method_probe_contract.md`
- Residual ranking: `wiki/wave_fives_residual_specials_research.md`
- Research freeze wiki: `wiki/auth_credentials_pre_submit_research.md`
