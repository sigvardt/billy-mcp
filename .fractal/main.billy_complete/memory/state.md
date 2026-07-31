---
name: state
desc: Current node state, verified review decisions, and open qualification work.
tags: [billy, coverage, review]
sources:
  - docs/superpowers/specs/2026-07-28-billy-mcp-complete-design.md
  - https://www.billy.dk/api/
created: 2026-07-29T09:56:00Z
updated: 2026-07-31T08:48:28Z
---

# state

## Current state

- Wave-5c through Wave-5s-C write/special modules merged on root.
- All **6** specials offline producted; live false. Residual clear **29** red. Bulk **92** red. UI **339** red.
- Root offline coverage: **184** implemented + contract_tested. API live/vision **0**. `complete: false`.
- Offline auth: `auth_status` / `auth_login_start` / `auth_login_wait` with submit labels **`Log in`** / **`Log ind`** (ACCEPT offline only).
- Research96 harness fixtures **merged**. Research97–98 **ACCEPT as research**. Review98 **ACCEPT** login-surface wiki as documentation only.
- Research99 **recorded**: docs byte-identical to research98; residual full matrix **25×405 / 2×401 / 2×meta-200**; login EN/DA reconfirmed; **credentialed session discovery protocol frozen** in research brief.
- Operator directive: stop residual/bulk fixture loop; UI/auth product lane active. **No new `ui_*` login tool.** Post-login org/session tools blocked without non-prod secrets.
- UI login-surface contract **merged** (`5e9cb61`). No product tool invent from login-only evidence.
- UI coverage stays red. Completeness **FAIL**.
- Wave-5u: every residual/bulk real-method candidate **BLOCK BEFORE NETWORK**.
- API live qualification is outside user-approved scope: API `live_tested` must
  stay false with `out_of_scope_by_user`; UI live qualification remains blocked
  without dedicated non-production browser credentials.
- `BILLY_*` env keys verified **absent** on the research runner (no token, no browser refs).

## Verification

- Research99 docs re-fetch: ETag `"wcw4x9hqvu3603"`, 147934 bytes, MD5 `8b94b0135c91fd15fe54ea33e088a4be`, byte-identical to research98.
- Research99 headless login EN/DA reconfirmed; query-locale alone insufficient for Danish; no credential submit; no frames retained.
- Residual 29 unauth matrix: 25 closed_405, transactions POST/PUT open_401, transactions + invoiceReminderAssociations DELETE meta_200.
- Unauth org/residual/bulk samples match prior research classes.
- Coverage honesty: 184/184/0/0, UI 0/339, `complete: false`. No greening.
- No offline FastMCP product slice remains without non-production credentials.
- The credentialed discovery protocol uses fresh second-interface browser
  read-back only; it must not invoke API traffic or require an API token.

## Review decisions (authoritative)

- Wave-5m through Wave-5s-C product: **ACCEPT offline only** where previously recorded.
- Research88–98: **ACCEPT as research** (where independently reviewed).
- Research99: **research freeze for credentialed discovery protocol** (no product ACCEPT; no coverage green).
- Review99: **ACCEPT research99 + ACCEPT protocol wiki as documentation only**; completeness **FAIL**.
- Review98: **ACCEPT research98 + ACCEPT wiki contract merge as documentation only**; completeness **FAIL**.
- Wave-5t harness / Wave-5u form-matrix / Research96 residual-gate fixtures: **ACCEPT as infrastructure only**.
- Typed `auth_status` offline product: **ACCEPT** credential-absent only.
- Offline auth credential pre-submit product on root: **ACCEPT offline only**.
- Overall completeness: **FAIL**.

## Open coverage work

1. Dedicated non-production browser credential references and organisation
   identity before post-login UI discovery.
2. Execute the research99 credentialed discovery protocol headlessly; obtain a
   cited Grok brief with a fresh second-interface read-back; then implement only
   the observed next `auth_*` capability.
3. API live tests and credentialed API calls are prohibited by user scope. Keep
   all API `live_tested` values false with `out_of_scope_by_user`; do not
   resolve `/user/organizations` through a token call.
4. Residual/bulk product remains blocked pending official and defensible offline
   contract evidence; never use live methods to close it.
5. Full UI parity + vision under the dedicated non-production browser org.

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
- There is no remaining offline FastMCP product slice without non-production credentials.
- Interface live read-back must use a second interface path or a fresh browser
  session; it must not use an API token or live API call.

## References

- Research99 brief: `.fractal/main.billy_complete/tmp/grok-research.md`
- Review99: `wiki/credentialed_session_discovery_protocol_independent_review.md` (full report `tmp/grok-review.md`)
- Protocol: `wiki/credentialed_session_discovery_protocol.md`
- Review98: `wiki/ui_login_surface_contract_independent_review.md`
- Merged contract: `wiki/ui_login_surface_contract.md`
- Review97: `wiki/wave_fives_research97_independent_review.md`
- Wave-5u contract: `wiki/wave5u_method_probe_contract.md`
- Residual ranking: `wiki/wave_fives_residual_specials_research.md`
- Auth freeze wiki: `wiki/auth_credentials_pre_submit_research.md`
