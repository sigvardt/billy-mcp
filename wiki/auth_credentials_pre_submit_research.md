---
name: auth_credentials_pre_submit_research
title: Auth credential references and pre-submit login research freeze
desc: Grok research92 contract for the offline credential-reference and fail-closed Billy login slice; it does not qualify live UI or API coverage.
tags: [billy, auth, credentials, login, research, grok, offline]
sources:
  - https://www.billy.dk/api/
  - docs/superpowers/specs/2026-07-28-billy-mcp-complete-design.md
  - .fractal/main.billy_complete/tmp/grok-research.md
  - src/billy_mcp/config.py
  - src/billy_mcp/browser.py
  - coverage/browser_egress.yaml
  - coverage/status.json
created: 2026-07-31T00:15:00Z
updated: 2026-07-31T00:15:00Z
---

# Auth credential references and pre-submit login research freeze

## Authority and scope

This page promotes the non-sensitive implementation boundary in Grok
research92, held in owner-only node scratch as
`.fractal/main.billy_complete/tmp/grok-research.md`. The primary official Billy
API document was re-fetched on 2026-07-31 with ETag `wcw4x9hqvu3603`, body MD5
`8b94b0135c91fd15fe54ea33e088a4be`, and the locked API base
`https://api.billysbilling.com/v2`. The document still has no webhook API and
does not document a bulk wire contract.

The completed Codex Power fallback record was reviewed as supplementary planning
context. Its safe constraints are reconciled here, but it is not an authority
that replaces the Grok brief or supplies an independent product or vision
approval.

The only productable scope is safe credential references plus the typed,
headless, fail-closed login transition through the observed pre-submit state.
This page does not authorise credentialed live testing, post-login inference,
organisation switching, token bootstrap, residual/bulk observation, coverage
changes, or a completeness claim.

## Observed authentication boundary

The MCP-owned, headless browser may open only the reviewed `mit.billy.dk`
route. The fixed root navigation must finish exactly at
`https://mit.billy.dk/login`, with no query, fragment, user info, or nondefault
port. The accepted signature has exactly one visible control each for:

- `input[type=email][name=email]`
- `input[type=password][name=password]`
- `input[type=checkbox][name=remember]`
- `button[data-cy=login-button]`, whose trimmed text is exactly `Log in` or
  `Log ind`

The observed button has no `type` attribute and is outside a form. A selector
such as `button[type=submit]` or `form button` is therefore prohibited. Any
URL, count, visibility, label, or DOM-read drift is `UI_CHANGED`, not a retry
or a generic browser action. No CAPTCHA, passkey, push approval, TOTP screen,
authenticated shell, organisation picker, or session-expiry state has been
observed. `AUTH_INTERACTION_REQUIRED` remains reserved for a future observed,
reviewed unautomatable challenge.

The reviewed egress policy keeps the browser lane on exact Billy interface
hosts and denies `api.billysbilling.com`; API reads continue through the locked
HTTP client rather than Playwright. Chromium stays headless, downloads stay
disabled, and no screenshot, frame, HAR, trace, DOM dump, cookie, or profile
content may be retained in the repository or tool result.

## Credential reference contract

Configuration and typed MCP inputs may retain only opaque credential-store
references or environment-variable names. They must never contain an email,
password, TOTP seed, access token, cookie, selector, URL, click instruction,
or browser/session value. A credential resolver protocol receives a reference
and exposes a secret only as an ephemeral local value inside the bounded login
operation. Tests use a fake resolver.

Resolved values and reference account names are forbidden in models, reprs,
logs, exceptions, ticket state, coverage, evidence, and tool outputs. Missing,
empty, or unresolvable required email/password references return the stable
`AUTH_REQUIRED` result without leaking which reference failed. An optional
TOTP reference must not be resolved or even located until an exact, reviewed
challenge signature proves it is required and automatable.

## Typed pre-submit transition

The implementation may expose only purpose-built `auth_*` operations, such as
the design's `auth_login_start` and `auth_login_wait`; it may not expose
generic navigation, selectors, clicks, typing, page inspection, or arbitrary
credential inputs. The internal operation sequence is fixed:

1. Start the existing persistent context with forced headless mode, disabled
   downloads, and the reviewed egress route handler.
2. Navigate only to the fixed root and validate the exact URL and login
   signature before resolving any credential reference.
3. Resolve email and password only after validation, then immediately repeat
   the same URL and signature validation before a single internal fill/submit
   transition.
4. Keep remember-me unchecked unless a later reviewed policy changes it.
5. Close the page in `finally` on every result. Unknown post-submit state is
   `UI_CHANGED`; no raw response or page content is returned.

The current environment has no Billy credential material, so production code
may be unit-tested with fake resolver/page seams only. A known signature with
missing references must yield `AUTH_REQUIRED` without resolver, fill, or click
calls. A bad route, missing/duplicate/hidden control, or wrong label must yield
`UI_CHANGED` before resolution and with no fill or click call. Egress-policy
failure is `EGRESS_DENIED`; unexpected runtime failure is redacted as
`BILLY_ERROR`.

## Explicitly retained blockers

Billy documents Settings → Access tokens, company-scoped permanent tokens, and
the user/Basic-auth organisation route `GET /v2/user/organizations`. It does
not document the browser organisation picker or Settings DOM. Unauthenticated
research92 sees the docs organisation path return `404` and `/organizations`
return `401`; neither result resolves the live contract. A future organisation
read must use the locked API client and a dedicated non-production credential;
it is not evidence for a browser selector.

The following remain red and blocked pending dedicated non-production material
and fresh Grok review: real password submission, post-login UI discovery,
TOTP, organisation selection, token bootstrap, session expiry and
reauthentication, UI parity/vision evidence, API live rows, all 29 residual
operations, and all 92 ambiguous bulk operations. `coverage/status.json`
therefore remains incomplete: 184 API rows are implemented and contract-tested
offline, with zero live or vision verification; all 339 UI rows remain red.
