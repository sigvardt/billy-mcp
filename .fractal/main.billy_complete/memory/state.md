---
name: state
desc: Current node state, verified review decisions, and open qualification work.
tags: [billy, coverage, review]
sources:
  - docs/superpowers/specs/2026-07-28-billy-mcp-complete-design.md
  - https://www.billy.dk/api/
created: 2026-07-29T09:56:00Z
updated: 2026-07-31T11:50:00Z
---

# state

## Current state

- RESEARCH102 done: first business UI seed routes. Brief:
  `.fractal/main.billy_complete/tmp/grok-research.md`. Artifacts:
  `tmp/discovery102/summary.json` (scrubbed; frames purged).
- Docs unchanged (ETag `wcw4x9hqvu3603`, MD5 `8b94b0135c91fd15fe54ea33e088a4be`).
- Live headless dual-session: invoices list shell OK (path/h1/CTA match A↔B);
  bank-accounts shell OK (`Bankkonti`; no official `bankAccounts` API resource);
  daybooks **error shell** (`Upsedasse!` / `Log ind igen`) — blocked.
- Tip `dda8ff6` on origin: 186.2 remember + dual READY + vision harness.
- Root offline: 184 implemented+contract_tested. API live 0 (`out_of_scope_by_user`). UI 0/339 live/vision. Residual 29 + bulk 92 red. `complete: false`.
- Operator: grok-only; no live API; interface credentials available.
- Wave-5u residual/bulk real methods remain BLOCK BEFORE NETWORK.
- FIX-VERIFY 186.3: R1 shell-only inventory schema; R2 list-surface vision accept
  + purge; R4 invoices UI_CHANGED message. Offline 1317 pass; live invoices pass.
  vision record accept+purge_verified. complete:false. COMMIT next.

## Verification

- Research99 docs re-fetch: ETag `"wcw4x9hqvu3603"`, 147934 bytes, MD5 `8b94b0135c91fd15fe54ea33e088a4be`, byte-identical to research98.
- Research99 headless login EN/DA reconfirmed; query-locale alone insufficient for Danish; no credential submit; no frames retained.
- Residual 29 unauth matrix: 25 closed_405, transactions POST/PUT open_401, transactions + invoiceReminderAssociations DELETE meta_200.
- Unauth org/residual/bulk samples match prior research classes.
- Coverage honesty: 184/184/0/0, UI 0/339, `complete: false`. No greening.
- No offline FastMCP product slice remains without non-production credentials.
- The credentialed discovery protocol uses fresh second-interface browser
  read-back only; it must not invoke API traffic or require an API token.
- 186.2 IR: ACCEPT product offline+live DOM; vision harness ACCEPT with purge;
  completeness FAIL. Plan: `plans/2026-07-31T09:29:42.163Z-186.2-auth_remember_dual_session_live.md`.

## Review decisions (authoritative)

- Slice 186.2 product (remember + dual live READY DOM): **ACCEPT**; vision
  harness **ACCEPT** with purge; UI inventory still red; completeness **FAIL**.
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

1. Product first read-only invoices UI list from research102 freeze. Auth lane
   ready. Do not invent login-only `ui_*`. Daybooks stays blocked on error
   shell. Bank-accounts is UI shell only (no `api_bank_accounts_*`).
2. Parent 07F2D101: `BILLY_ORGANIZATION_ID` is **not** a user blocker. Derive
   the dedicated test org identity from the authenticated headless UI only.
   Persist only a non-secret identifier **outside git**. No API for org
   discovery. Single-org auto dashboard confirmed again (slug length 21).
3. API live tests and credentialed API calls are prohibited by user scope. Keep
   all API `live_tested` values false with `out_of_scope_by_user`; do not
   resolve `/user/organizations` through a token call.
4. Residual/bulk product remains blocked pending official and defensible offline
   contract evidence; never use live methods to close it.
5. Full UI parity + vision under the dedicated non-production browser org
   (shell href seeds: invoices, daybooks, bank-accounts, uploads, reports-all).
6. `auth_status` remains login-signature-only (`AUTH_REQUIRED`); use
   `auth_login_wait` for READY. Do not treat post-login `auth_status` UI_CHANGED
   as shell failure when wait is READY.

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

- Research101 brief: `.fractal/main.billy_complete/tmp/grok-research.md`
- Discovery101 JSON: `.fractal/main.billy_complete/tmp/discovery101/`
- Review99: `wiki/credentialed_session_discovery_protocol_independent_review.md` (full report `tmp/grok-review.md`)
- Protocol: `wiki/credentialed_session_discovery_protocol.md`
- Review98: `wiki/ui_login_surface_contract_independent_review.md`
- Merged contract: `wiki/ui_login_surface_contract.md`
- Review97: `wiki/wave_fives_research97_independent_review.md`
- Wave-5u contract: `wiki/wave5u_method_probe_contract.md`
- Residual ranking: `wiki/wave_fives_residual_specials_research.md`
- Auth freeze wiki: `wiki/auth_credentials_pre_submit_research.md`
