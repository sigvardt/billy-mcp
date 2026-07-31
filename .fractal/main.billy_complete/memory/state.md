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
- Offline auth: `auth_status` / `auth_login_start` / `auth_login_wait` with submit labels **`Log in`** / **`Log ind`** (ACCEPT offline only).
- Research96 harness fixtures **merged** on tip (`1b06773`). Research97 **ACCEPT as research** (review97). Research98 **recorded** (docs unchanged; UI login-surface decision frozen). Review98 **ACCEPT research98 + wiki contract merge as documentation only**; completeness **FAIL**.
- Operator directive: stop residual/bulk fixture loop; UI/auth product lane active. Research98 decision: **no new `ui_*` login probe** (duplicates `auth_status`). Post-login org/session tools blocked without non-prod secrets.
- UI login-surface contract child **completed** and merged at `5e9cb61` (wiki-only). Review98 **ACCEPT as documentation**. No product tool invent from login-only evidence.
- UI coverage stays red. Completeness **FAIL**.
- Wave-5u: every residual/bulk real-method candidate **BLOCK BEFORE NETWORK**.
- Live residual/bulk/UI remain blocked without dedicated non-production secrets.
- `BILLY_API_TOKEN` and UI secrets verified unset on the research runner.

## Verification

- Review98 docs re-fetch: ETag `"wcw4x9hqvu3603"`, 147934 bytes, MD5 `8b94b0135c91fd15fe54ea33e088a4be`, byte-identical to research98.
- Review98 headless login EN/DA reconfirmed; no credential submit; no frames retained.
- Unauth org/residual sample probes match prior research classes (docs org path 404; residual 405/401; empty bulk delete 400).
- Coverage honesty: 184/184/0/0, UI 0/339, `complete: false`. Merge `5e9cb61` wiki-only. No greening.
- `check_coverage.py --reject-false-completeness` passed.

## Review decisions (authoritative)

- Wave-5m through Wave-5s-C product: **ACCEPT offline only** where previously recorded.
- Research88–97: **ACCEPT as research** (review97 closed research97 independently).
- Research98: **research freeze for UI login-surface decision** (no independent product ACCEPT claimed; no coverage green).
- Review98: **ACCEPT research98 + ACCEPT wiki contract merge as documentation only**; completeness **FAIL**.
- Wave-5t harness: **ACCEPT as infrastructure only**.
- Wave-5u form-matrix harness: **ACCEPT as infrastructure only** (not residual/bulk product).
- Research96 residual-gate + bulk canonical-form fixtures on tip: **ACCEPT as infrastructure only** (review97).
- Typed `auth_status` offline product: **ACCEPT** credential-absent only (review91); UI rows remain red.
- Offline auth credential pre-submit product on root: **ACCEPT offline only** (review94; labels reconfirmed through research98/review98).
- Overall completeness: **FAIL**.

## Open coverage work

1. Dedicated non-production token + org before live residual/bulk or API `live_tested`.
2. Live prove or correct `GET /user/organizations` vs `/organizations` with a **valid** token (do not rewrite from unauth 404 alone).
3. Contract citation was retargeted to research98. **No new `ui_*` login tool.** Residual/bulk real methods stay **BLOCK BEFORE NETWORK**.
4. Credentialed headless post-login discovery before any `auth_organizations_*`, reauth, logout UI, token bootstrap UI, or first business `ui_*` workflow.
5. Full UI parity + vision under non-prod org.
6. Residual/bulk product only after non-prod credentials and reviewed non-persistence proofs (separate from UI login lane).

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
- Do not invent a `ui_*` tool that only re-reads the login page already covered by `auth_status`.
- Do not invent post-login selectors, `READY`, or org-picker tools without credentialed non-prod observation.
- No webhooks (official 0 mentions).
- Codex fallback cannot alone close a mandatory Grok product gate.
- Do not accept email/password/TOTP/token as MCP tool inputs; references only.
- Do not treat `ZERVANT_GOOGLE_CAPTCHA_*` bootstrap flags as `AUTH_INTERACTION_REQUIRED`.
- `Login` is only a possible page title; exact submit labels remain `Log in` and `Log ind`.
- Danish login discovery requires browser context locale + Accept-Language; query `?locale=` alone is insufficient.
- Offline product ACCEPT does not authorise CI live password submit without non-prod secrets + fresh Grok re-review.
- Operator interface lane: do not spawn residual/bulk fixture-only children until non-production credentials arrive.

## References

- Research98 brief: `.fractal/main.billy_complete/tmp/grok-research.md`
- Review98: `wiki/ui_login_surface_contract_independent_review.md` (full report `tmp/grok-review.md`)
- Merged contract: `wiki/ui_login_surface_contract.md`
- Review97: `wiki/wave_fives_research97_independent_review.md`
- Wave-5u contract: `wiki/wave5u_method_probe_contract.md`
- Residual ranking: `wiki/wave_fives_residual_specials_research.md`
- Auth freeze wiki: `wiki/auth_credentials_pre_submit_research.md`
