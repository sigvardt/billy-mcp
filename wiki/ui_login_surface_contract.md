---
name: ui_login_surface_contract
title: UI login surface contract
desc: Cited, evidence-bounded boundary for Billy's observed login surface: retain shared auth_status and keep post-login UI/auth work red pending dedicated non-production evidence.
tags: [billy, ui, auth, login, contract, headless]
sources:
  - https://mit.billy.dk/
  - https://www.billy.dk/api/
  - docs/superpowers/specs/2026-07-28-billy-mcp-complete-design.md
  - .fractal/main.billy_complete/tmp/grok-research.md
  - src/billy_mcp/browser.py
  - src/billy_mcp/models.py
  - src/billy_mcp/server.py
  - coverage/browser_egress.yaml
  - coverage/ui_workflows_manifest.yaml
created: 2026-07-31T00:21:07Z
updated: 2026-07-31T00:21:07Z
---

# UI login surface contract

## Decision

**Selected outcome: shared auth/session work, not a new `ui_*` read workflow.**
The only observed interface state is the unauthenticated login page, and the
existing stable `auth_status` tool already reads exactly that state. A proposed
`ui_*` login probe would therefore duplicate `auth_status`; a generic browser
wrapper would contradict the approved design's typed, fixed-workflow boundary.

Organisation selection and session restoration are shared authentication
requirements, but they have no stable new tool name or selector contract yet.
They must not be named, implemented, or represented as a generic UI action
until a dedicated non-production login proves their states. The existing
`auth_login_start` is a separate fixed pre-submit transition and
`auth_login_wait` currently rechecks `auth_status`; neither proves a
post-login page.

## Cited observed-surface evidence

The required evidence authority is the Grok-produced `research97` relay at
`.fractal/main.billy_complete/tmp/grok-research.md`. The retrieval timestamp
available in that relay is day precision; no time-of-day is invented here.

| Source | Canonical URL | Retrieved | Evidence preserved in this contract |
| --- | --- | --- | --- |
| Billy web application | [https://mit.billy.dk/](https://mit.billy.dk/) | 2026-07-31 | Login-only, credential-absent headless discovery. The reviewed browser host is allowlisted. |
| Billy API documentation | [https://www.billy.dk/api/](https://www.billy.dk/api/) | 2026-07-31 | Primary document was HTTP 200; relay recorded ETag `wcw4x9hqvu3603`, 147934-byte body, and MD5 `8b94b0135c91fd15fe54ea33e088a4be`. It supplies API context only, not browser DOM selectors. |
| Locked API destination | [https://api.billysbilling.com/v2](https://api.billysbilling.com/v2) | 2026-07-31 | API-client-only destination; it is never a browser target. |

The observed final unauthenticated page is exactly
`https://mit.billy.dk/login`. This page is evidence for a login-state check,
not evidence that a session can be restored or an organisation can be chosen.
The relay is also consistent with [[billy_ui_discovery_brief]] and
[[auth_credentials_pre_submit_research]].

## Stable shared interface and bounded workflow

The stable read interface remains **`auth_status`**.

| Part | Typed contract |
| --- | --- |
| Input | `AuthStatusInput`: strict Pydantic model (`extra="forbid"`) with no fields; its only valid caller payload is `{}`. |
| Success | `AuthStatusSuccess(status: Literal[AUTH_REQUIRED])`, serialised as `{"status":"AUTH_REQUIRED"}`. This is the one observed login-only state, not proof of a usable session. |
| Error | `ToolError(code: StableErrorCode, message: str, details: dict[str, Any])`. Relevant fail-closed codes are `UI_CHANGED`, `EGRESS_DENIED`, and `BILLY_ERROR`; `AUTH_REQUIRED` is also the safe error for missing browser-login references in the separate login-start path. |
| Scope | Read only the known unauthenticated state. It accepts no URL, selector, cookie, credential, organisation, session, or browser-control input. |

The workflow is deliberately non-generic:

1. Start the existing persistent Chromium context headlessly with downloads
   disabled and the reviewed browser-egress policy installed.
2. Navigate only to the fixed Billy root. Accept only the final, queryless,
   fragmentless HTTPS login URL above, with no user info and only default HTTPS
   port semantics.
3. Validate the recorded login signature below. On success, return only
   `AUTH_REQUIRED`; close the page. Do not expose the DOM, storage, cookies, or
   browser controls.
4. Any route or signature drift is `UI_CHANGED`; policy-load failure is
   `EGRESS_DENIED`; an unexpected browser failure is a redacted
   `BILLY_ERROR`.

`coverage/browser_egress.yaml` allows `mit.billy.dk` only for typed UI/auth
work and denies it to the API client. It denies `api.billysbilling.com` to the
browser and reserves that host exclusively for the locked API client. This
separation is part of the contract, not a fallback browser-navigation mechanism.

## Exact unauthenticated DOM contract

These are assertions for the observed login page only. Each selector must
resolve to exactly one visible control:

| Purpose | Exact selector | Assertion |
| --- | --- | --- |
| Email | `input[type=email][name=email]` | Count is one and visible. |
| Password | `input[type=password][name=password]` | Count is one and visible. |
| Remember-me | `input[type=checkbox][name=remember]` | Count is one and visible. |
| Login button | `button[data-cy=login-button]` | Count is one and visible; trimmed `inner_text` is exactly `Log in` or `Log ind`. |

The observed page has **no form elements**. The login button is not a
`button[type=submit]` contract: the relay observed a null type attribute and a
button outside a form. Tests and future code must not use `form`, `form button`,
or `button[type=submit]` as substitute selectors. Page title is also not a
submit-label assertion.

For Danish rendering, a Playwright context must set both `locale="da-DK"` and
`Accept-Language: da-DK,da`; a locale query parameter by itself was observed to
leave English browser chrome. The analogous English relay setup used
`locale="en-GB"` and `Accept-Language: en-GB,en`. Locale setup is limited to
checking the observed login signature; it does not establish a post-login
language contract.

## Offline implementation and test boundary

A later Codex Power implementation can test this contract without any Billy
credentials or network access by injecting fake persistent-context, page, and
locator seams. The fixture must contain synthetic controls only and retain no
HTML dump, frame, screenshot, HAR, trace, cookie, token, or customer data.

| Offline scenario | Required result |
| --- | --- |
| Exact login URL and one visible control for every selector; button label `Log in` | `AuthStatusSuccess(status=AUTH_REQUIRED)`. |
| Same fixture with `Log ind` | The same success; no title-language assertion. |
| Missing, duplicate, hidden, or DOM-unreadable control; other button text; final route with a query, fragment, or another path | `ToolError(code=UI_CHANGED)` and no inferred session state. |
| Egress manifest cannot load | `ToolError(code=EGRESS_DENIED)`. A policy-denied request is not a caller-selectable route; it must remain blocked by the route handler and must not create a generic navigation feature. |
| Unexpected browser failure | `ToolError(code=BILLY_ERROR)` with no page, profile, or credential values in details. |
| `auth_login_start` with a known signature but absent opaque references | `ToolError(code=AUTH_REQUIRED)` before resolver, fill, or click calls. This covers the pre-submit guard only, not live authentication. |
| Danish-specific browser setup test | Assert the mocked context receives both `da-DK` locale and `Accept-Language: da-DK,da`; do not model `?locale=da-DK` as sufficient evidence. |

No offline test may assert a successful password submit, MFA, an authenticated
shell, a restored session, an organisation picker, a settings route, a plan
gate, or an API-to-UI parity result. Such an assertion would manufacture an
unobserved authenticated surface.

## Independent read-back

There is **no independent business read-back for `auth_status` today**: the
login page renders no business entity, and no authenticated API call is part of
this workflow. Returning `AUTH_REQUIRED` is the complete read result.

If later credentialed discovery establishes an organisation or restored-session
state, its independent read-back must use the locked API client at
`https://api.billysbilling.com/v2`, never Playwright. It must use a valid,
dedicated non-production company token, compare the browser-selected
organisation with an API organisation read, and preserve only reviewed,
non-sensitive evidence. The unauthenticated `GET /user/organizations` result
does not establish this: the cited relay records no-token `404` and
garbage-token `401`, neither of which proves the browser route or selector.

## Blockers and required live evidence

The following remain unasserted and blocked:

- post-password success and failure pages;
- TOTP, SMS, email, CAPTCHA-after-failure, passkey, or push challenges;
- session restoration, expiry, logout, and reauthentication;
- organisation picker controls and organisation selection;
- Settings → Access tokens DOM and plan-gated screens; and
- all product routes and their API-parity UI workflows.

To open any one of those contracts, a separate approved run needs dedicated
non-production browser credentials or a known MCP-owned non-production session,
an explicitly identified non-production organisation, and a separately held
company API credential when read-back is required. It must remain headless,
stop at an actually observed unautomatable challenge, use exact newly observed
DOM assertions, complete independent API read-back and cleanup where
applicable, receive vision verification, and purge ephemeral visual evidence.
It must not submit production credentials, persist browser artifacts, or infer
the state from configuration flags alone.

## Coverage remains red

This brief changes no coverage artifact. In particular,
`ui.parity.special.user_organizations` remains
`parity_status: discovery_required` with `discovered`, `implemented`,
`contract_tested`, `live_tested`, and `vision_verified` all `false`. The
organisation API-parity family and the rest of the 339 UI manifest rows remain
red. A new UI row must likewise remain red until the dedicated non-production
run supplies observed DOM evidence, its required independent read-back, and
vision evidence.

This login-only evidence must never green a UI row, API live row, or vision
flag; it must not turn inaccessible or plan-gated work into complete coverage.
It also authorises no residual/bulk API research, no FastMCP tool registration,
and no generic navigation, typing, click, selector, or DOM-export tool.

## Non-retention and non-claims

This contract records selectors and typed outcomes only. It does not retain or
request screenshots, rendered frames, HARs, traces, cookies, browser-profile
contents, tokens, credential values, customer data, or raw DOM captures. It
does not claim an authenticated surface, an organisation-selection workflow,
session restoration, a live test, vision verification, or completeness.
