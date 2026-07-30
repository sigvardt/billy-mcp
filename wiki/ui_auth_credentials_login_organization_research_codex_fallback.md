---
name: ui_auth_credentials_login_organization_research_codex_fallback
title: UI authentication, credentials, and organisation research — Codex Power fallback
desc: Bounded implementation plan for secure headless Billy login and organisation context; not a Grok finding or UI qualification.
tags: [billy, ui, auth, credentials, organization, research, fallback]
sources:
  - https://www.billy.dk/api/
  - docs/superpowers/specs/2026-07-28-billy-mcp-complete-design.md
  - src/billy_mcp/config.py
  - src/billy_mcp/browser.py
  - coverage/browser_egress.yaml
  - coverage/status.json
  - coverage/ui_workflows_manifest.yaml
  - tests/unit/test_browser.py
  - tests/unit/test_config.py
  - wiki/billy_ui_discovery_brief.md
  - wiki/wave5t_ui_auth_discovery.md
  - wiki/review_provenance_rules.md
created: 2026-07-30T22:05:05Z
updated: 2026-07-30T22:05:05Z
---

# UI authentication, credentials, and organisation research — Codex Power fallback

## Scope and provenance

This is an implementation-ready **research-only** record for the next secure
UI-authentication slice. The designated Grok runner was unavailable because of
runner authentication before it made task edits; this is therefore a **Codex
Power fallback**, not a Grok finding, review, or vision verdict. It does not
satisfy the mandatory later Grok research/review or vision gate described below.

No credential was resolved or used; no form was submitted; no Billy application
browser action or Billy API runtime request was made; no organisation was
selected; no post-login state was reached; and no record was created, changed,
or deleted. This page retains no raw DOM dump, frame, cookie, browser storage,
credential, TOTP value, organisation value, or other sensitive evidence.

The plan intentionally separates direct official documentation, bounded
anonymous observation, and committed-repository observations. Anything not
listed as observed is not a selector, route, capability, or test assertion.

## Direct official Billy documentation

- Billy documents its v2 API at `https://api.billysbilling.com/v2` and requires
  SSL. [Billy API v2 documentation](https://www.billy.dk/api/)
- The documentation says an access token can be created in **Settings → Access
  tokens**, sent in `X-Access-Token`, is tied to one company, and does not
  expire. A multi-company use case therefore needs a separate company token.
  [Billy API v2 documentation — Authentication](https://www.billy.dk/api/)
- Billy also documents normal email/password HTTP Basic authentication and says
  that, when using a user-tied token or Basic authentication, a user's
  companies can be listed through `GET /v2/user/organizations`.
  [Billy API v2 documentation — Authentication and use cases](https://www.billy.dk/api/)

The public API documentation is an API contract, not evidence of the
post-login web UI. In particular, it supplies no safe basis here for inferring
a browser organisation-picker route, selector, login success signature, TOTP
screen, or post-login recovery sequence.

## Bounded anonymous UI observation

Only the following unauthenticated signature is in bounds:

| Item | Observed value |
| --- | --- |
| Entry | root redirects to `https://mit.billy.dk/login` |
| Visible controls | email, password, and remember controls |
| Submit control | `button[data-cy=login-button]` |
| Localised submit text | `Log in` and `Log ind` |

This observation establishes neither a valid credential nor an authenticated
session. No credential entry, submit, MFA/TOTP/CAPTCHA/passkey/push challenge,
organisation selection, account menu, application route, or post-login page
has been observed. Those unknown post-login behaviours are a **discovery
blocker**, not an invitation to guess selectors or add generic browser tools.

## Committed-repository observations

These are repository facts, not official Billy claims or live qualification:

- `AppConfig` keeps safe settings serialisable, resolves only the current API
  token from the process environment or OS keyring, and already has an optional
  selected-organisation setting. It has no browser-email, password, or TOTP
  resolver.
- `BrowserRuntime` forces a persistent Chromium context to headless mode,
  disables downloads, loads the reviewed egress manifest before launch, and
  allows no generic browser-control tool. The current `auth_status` workflow
  accepts only the bounded login URL and signature above, yielding
  `AUTH_REQUIRED`; deviation fails closed as `UI_CHANGED`.
- The reviewed browser policy permits `mit.billy.dk` for typed UI/auth work and
  denies the API host to the browser lane. Existing browser tests inject a
  launcher, context, page, and controls, which is a useful seam for the next
  slice.
- `coverage/status.json` currently records 339 UI rows and zero
  vision-verified rows. The committed UI manifest has no green UI workflow in
  this scope. **All UI coverage remains red.** This is an inventory observation
  only—not a live, vision, parity, or completeness claim—and this research
  changes no coverage file or generated status.

## Bounded next-slice design

The next implementation must be a narrow typed authentication state machine,
not a caller-directed browser, selector, DOM-export, or credential-entry tool.
Its first deliverable is testable secure plumbing and fail-closed pre-submit
validation; credentialed submission remains gated by the discovery and Grok
requirements in this record.

### 1. Credential-store references and resolution

Add safe, serialisable references to configuration, separate from resolved
values. A proposed shape is:

| Proposed type/field | Stored/serialised content | Prohibited content |
| --- | --- | --- |
| `CredentialReference` | OS-store service and opaque account reference, both non-empty | secret value, email, password, TOTP, token, cookie, or browser-storage value |
| `BrowserLoginReferences.email` | `CredentialReference` | caller-supplied email value |
| `BrowserLoginReferences.password` | `CredentialReference` | caller-supplied password value |
| `BrowserLoginReferences.totp` | optional `CredentialReference` | caller-supplied TOTP value or an assumption that TOTP exists |
| `selected_organization` | existing configured opaque identifier | a production default or implicit organisation switch |

Implement an injected `CredentialResolver` protocol that receives a
`CredentialReference` and returns an ephemeral secret only inside the login
operation. Its OS-keyring implementation may use the existing keyring service;
tests use a fake resolver. Keep resolved values out of Pydantic request/response
models, `repr`, exception text, logs, metrics, tickets, persisted profile data,
snapshots, screenshots, traces, HAR files, and durable evidence. An empty or
unresolvable required reference returns `AUTH_REQUIRED` without identifying the
missing account reference.

The email and password are resolved only after the fixed login page passes the
pre-submit checks. The optional TOTP reference is **not** resolved merely
because it is configured. Resolve it only in a later, separately reviewed
challenge state whose exact DOM signature has been observed; no such state is
known now.

### 2. Typed, headless login pre-submit contract

Propose an empty-input `auth_login` operation rather than any operation that
accepts credentials, URLs, selectors, organisation IDs, or click instructions
from a caller. Before it can type or submit anything, it must:

1. launch only the existing MCP-owned, headless, downloads-disabled runtime and
   reviewed egress policy;
2. open the fixed application root, require the exact final login URL with no
   user-info, query, fragment, or non-default port, and reject every other
   destination as `UI_CHANGED`;
3. require exactly one visible email control, password control, remember
   control, and `button[data-cy=login-button]`; require the submit text to be
   exactly `Log in` or `Log ind`;
4. resolve only the email and password references into ephemeral local values;
5. re-check the same URL/signature immediately before the single typed fill and
   submit transition; and
6. close the page in `finally` and never emit its URL beyond the stable state,
   control contents, resolved values, or browser/session diagnostics.

The future transition must have a narrow page protocol (`fill`, a single submit
action, URL, and only approved locators) so tests can prove the ordering. It
must never expose raw Playwright objects or generic navigation/click/type/DOM
methods through MCP.

### 3. States, failures, expiry, and reauthentication

Use the approved stable errors without manufacturing a `TOTP_REQUIRED` state:

| Condition | Typed result and required behaviour |
| --- | --- |
| The bounded login signature is present before any resolved value is used | `AUTH_REQUIRED` for status; login may proceed only through the gated typed transition above. |
| A required reference is unavailable or empty | `AUTH_REQUIRED`, with no reference name or secret detail. |
| URL, selector count/visibility, submit label, or a post-submit screen not yet discovered differs from its approved signature | `UI_CHANGED`; do not type, click, inspect arbitrary DOM, or retry by guesswork. |
| The reviewed egress policy prevents launch/navigation | `EGRESS_DENIED`. |
| Browser launch/transport failure | `BILLY_ERROR`, redacted and without session or credential material. |
| An explicitly observed and independently reviewed CAPTCHA, passkey, push approval, or other unautomatable challenge is present | `AUTH_INTERACTION_REQUIRED`; stop without a visible browser or automatic retry. |
| A later verified authenticated session returns to an approved login-required signature | `AUTH_EXPIRED`; discard the in-memory authenticated-state marker and restart only the typed pre-submit path. |
| No organisation is explicitly selected after its state is independently discovered | `ORGANIZATION_REQUIRED`. |
| Discovered current organisation conflicts with configured/test-run organisation | `ORGANIZATION_MISMATCH`; do not select, write, or continue. |

No challenge is currently observed. Therefore this slice must not recognise a
TOTP form, CAPTCHA, passkey, push flow, or any other post-submit page from
generic text; an unknown post-submit surface is `UI_CHANGED`. A future
TOTP-specific transition needs a new bounded observation of its exact controls,
a review of whether it is automatable, and its own tests before the optional
reference is resolved.

`AUTH_EXPIRED` is likewise a future transition, not something to infer from
today's login page. Track a verified authenticated state only in memory for the
active runtime; do not persist a boolean, cookie, token, or timestamp as
evidence. A crash, unknown page, or browser restart clears that marker and
fails closed rather than resuming a pending login or write.

### 4. Organisation discovery and explicit selection

Billy's documentation supports an independent API organisation-list read for a
user-tied token or Basic authentication at `GET /v2/user/organizations`; it
also says a Settings-created token is company-scoped. [Billy API v2
documentation](https://www.billy.dk/api/) Treat that API read as a separate,
credential-gated read-back capability—not as evidence of a web selector and
not as a browser-lane request.

After a valid, separately provisioned API credential and dedicated
non-production organisation are available, a future `auth_organizations_list`
may return only typed organisation identifiers and display names needed for an
explicit choice. It must use the locked API client, never the browser lane. A
future `auth_organization_select` may proceed only if all three are true:

1. the configured non-production organisation identifier is explicitly
   supplied outside the repository;
2. the API discovery result confirms it is available to the credential; and
3. an authenticated UI selector and current-organisation read-back have each
   been observed, documented, and independently reviewed.

The organisation-picker route, selector, and resulting UI state are unknown.
Until they are discovered, selection is blocked: do not navigate to a guessed
route, select a default organisation, or use the API list as a proxy for a UI
switch. The existing `selected_organization` setting is a required equality
constraint, never authority to change context.

### 5. Test seams and staged verification

Keep the existing injected browser launcher/context/page seams and add a fake
credential resolver, monotonic clock, and a minimal fill/submit-capable fake
login page. The next source slice needs unit/contract tests for:

- serialised input/output/configuration contains references only, never a
  secret; errors and logs are redacted even when fakes raise with sensitive
  text;
- headless mode, downloads-disabled mode, exact egress host, page closure, and
  the existing exact login URL/signature rules;
- every failing pre-submit check proves that neither resolver nor fill/submit
  is invoked; resolver errors prove that no fill/submit occurs;
- both observed labels pass; duplicate, hidden, missing, or changed controls
  and every other final route fail as `UI_CHANGED`;
- TOTP is not resolved or located before an independently observed challenge
  contract exists; unknown post-submit state does not retry;
- expiry clears only the in-memory verified-state marker; restart/crash clears
  it and does not resume an action; and
- fake API transport proves organisation-list filtering and exact configured
  organisation matching without live network traffic.

Only after those offline tests and the gates below may a dedicated
non-production integration run use real browser/API credentials. It must still
remain headless and typed; it cannot turn into a generic UI test harness.

### 6. Dedicated non-production organisation, read-back, and cleanup

The credentialed run needs a dedicated non-production organisation selected by
an out-of-repository opaque identifier and explicitly allowlisted for the test
runner. The login/organisation-discovery slice must be read-only: its
created-resource ledger is empty, so it may not add a cleanup write merely to
test one.

Before any later UI write test, record a non-sensitive baseline through the
approved independent read-back path, bind the test run to the dedicated
organisation, and reject a mismatch. Track only IDs of resources created by
that run in an ephemeral cleanup ledger; restore or delete them in reverse
dependency order, read back the restored state independently, and perform the
supported final tagged-resource search where available. Fail as
`CLEANUP_FAILED` with non-sensitive leftover identifiers; never suppress an
orphan. No production organisation may be used for qualification or cleanup.

### 7. Evidence handling and required Grok gates

Keep browser profiles, credentials, cookies, and any test-only rendered frames
outside the repository with owner-only permissions. For a later UI run, raw
frames are ephemeral: a vision-capable reviewer may inspect them outside the
repository, after which they are purged. Retain only a non-sensitive evidence
record containing coverage-row identifier, run identifier, assertions,
independent read-back reference, reviewer verdict, and `purge_verified: true`;
never retain a frame, DOM dump, credential, cookie, TOTP, or Billy business
value.

Before any credentialed submission or post-login implementation claim, obtain
a mandatory current Grok research/independent review of this fallback and the
newly observed state contract. Before any UI coverage could become green,
obtain the mandatory Grok vision review of the ephemeral rendered evidence,
DOM assertions, independent read-back, and verified purge. The currently
missing Grok research/review and vision gates remain **outstanding**.

## Delivery boundary

This document recommends secure sequencing; it neither registers a tool nor
changes credentials, coverage, tests, source, status, or generated evidence.
Unknown post-login behaviour remains a discovery blocker, all UI coverage
remains red, and no live, vision, parity, or completeness claim is made.
