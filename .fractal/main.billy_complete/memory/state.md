---
name: state
desc: Current node state, verified review decisions, and open qualification work.
tags: [billy, coverage, review]
sources:
  - docs/superpowers/specs/2026-07-28-billy-mcp-complete-design.md
  - https://www.billy.dk/api/
created: 2026-07-29T09:56:00Z
updated: 2026-07-31T09:45:00Z
---

# state

## Current state

- FIX-VERIFY 186.1: IR non-blocking residuals applied — docs fingerprint
  `wcw4x9hqvu3603` / `8b94b013…` on status+api official_docs; blocker text no
  longer cites missing `BILLY_API_TOKEN`. `complete: false` unchanged.
  lint + commit-mode tests **1307 passed**. Slice offline ACCEPT; completeness FAIL.
- EXECUTE 186.1 **delivered offline + live smoke READY** (not coverage green):
  path-scoped `browser_action: path_allow` on `api.billysbilling.com`;
  `AuthLoginWaitSuccess` AUTH_REQUIRED|READY; dual live wait READY; org slug
  persisted outside git (`~/.local/share/billy-mcp/ui-org-identity.json`).
  Wiki: `wiki/auth_scoped_egress_ready_wait.md`. Live/vision coverage still red.
- PLAN 186.1:
  `plans/2026-07-31T09:05:11.028Z-186.1-auth_scoped_egress_ready_wait.md`.
- RESEARCH100 written: `.fractal/main.billy_complete/tmp/grok-research.md`.
  Docs ETag `wcw4x9hqvu3603` / MD5 `8b94b013…` match research99. Credentialed
  headless discovery: under current browser egress (deny API host) login stays
  on `/login` with send-failure error because `POST /v2/user/login` is blocked.
  Research-only allow of `api.billysbilling.com` yields dual-session
  `ready_shell_candidate` at path class `/:org_slug/dashboard` (no picker/MFA).
  Frames purged; JSON scrubbed. Next product slice: path-scoped auth egress +
  post-login `auth_login_wait` observation; live/vision stay red.
- PREPARE iter1: parent `main` already up to date. No child merges.
  Product candidate `ui_auth_status` already on root via later integrate +
  login product commits (child tip is stale relative to label repair and
  login tools). Wiki-only children: credentials Codex fallback superseded by
  Grok auth freeze; wave5t trailing-newline only; wave5u tip regresses
  research95 bulk-delete table — keep root. All other tips are init/fail/
  kill scaffolding. No running children.
- Wave-5c through Wave-5s-C write/special modules merged on root.
- All **6** specials offline producted; live false. Residual clear **29** red. Bulk **92** red. UI **339** red.
- Root offline coverage: **184** implemented + contract_tested. API live/vision **0**. `complete: false`.
- Offline auth: `auth_status` / `auth_login_start` / `auth_login_wait` with submit labels **`Log in`** / **`Log ind`** (ACCEPT offline only).
- Research96 harness fixtures **merged**. Research97–98 **ACCEPT as research**. Review98 **ACCEPT** login-surface wiki as documentation only.
- Research99 **recorded**: docs byte-identical to research98; residual full matrix **25×405 / 2×401 / 2×meta-200**; login EN/DA reconfirmed; **credentialed session discovery protocol frozen** in research brief.
- Operator directive: stop residual/bulk fixture loop; UI/auth product lane active. **No new `ui_*` login tool.**
- UI login-surface contract **merged** (`5e9cb61`). No product tool invent from login-only evidence.
- UI coverage stays red. Completeness **FAIL**.
- Wave-5u: every residual/bulk real-method candidate **BLOCK BEFORE NETWORK**.
- API live qualification is outside user-approved scope: API `live_tested` must
  stay false with `out_of_scope_by_user`. Never live-verify the API lane.
- **2026-07-31 continue:** parent scope override + grok-only + interface
  credentials available. Keyring service `billy-mcp` accounts
  `browser-primary` / `browser-secondary` resolve. Env refs
  `BILLY_BROWSER_PRIMARY_REFERENCE` and `BILLY_BROWSER_SECONDARY_REFERENCE` set.
  `BILLY_API_TOKEN` not required and not set. `BILLY_ORGANIZATION_ID` still
  unset. Next work is headless credentialed session discovery per
  `wiki/credentialed_session_discovery_protocol.md`, then product only the
  observed post-login auth/ui capability.

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

1. PLAN/EXECUTE research100 slice: path-scoped browser allow for auth/bootstrap
   API paths; extend `auth_login_wait` for READY vs login-failure vs interaction;
   offline tests; no live/vision green.
2. Parent 07F2D101: `BILLY_ORGANIZATION_ID` is **not** a user blocker. Derive
   the dedicated test org identity from the authenticated headless UI only.
   Persist only a non-secret identifier **outside git**. No API for org
   discovery. Ask Joakim only if multiple orgs appear and the correct one is
   ambiguous. Research100 saw single-org auto dashboard (path class
   `/:org_slug/dashboard`).
3. After independent review of research100, implement only the observed shared
   `auth_*` capability. Keep live/vision red until real e2e + vision record.
3. API live tests and credentialed API calls are prohibited by user scope. Keep
   all API `live_tested` values false with `out_of_scope_by_user`; do not
   resolve `/user/organizations` through a token call.
4. Residual/bulk product remains blocked pending official and defensible offline
   contract evidence; never use live methods to close it.
5. Full UI parity + vision under the dedicated non-production browser org.
6. Align `coverage/status.json` blocker text with scoped policy (drop false
   BILLY_API_TOKEN requirement for completeness once UI path qualifies).

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
- Operator interface lane: do not spawn residual/bulk fixture-only children.
- Interface live read-back must use a second interface path or a fresh browser
  session; it must not use an API token or live API call.
- Grok-only execution: every child spawn must pass `--agent=grok`. No
  `codex-power`, bare `codex`, `claude`, `opencode`, or `omp`.
- Browser keyring credentials are available; do not claim they are absent.

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
