---
name: credentialed_session_discovery_protocol
title: Credentialed session discovery protocol
desc: Grok-frozen, headless-only protocol for observing Billy's first non-production post-login state before naming a new auth or UI workflow.
tags: [billy, auth, ui, discovery, headless, non-production, safety]
sources:
  - https://www.billy.dk/api/
  - https://api.billysbilling.com/v2
  - https://mit.billy.dk/
  - docs/superpowers/specs/2026-07-28-billy-mcp-complete-design.md
  - .fractal/main.billy_complete/tmp/grok-research.md
  - wiki/ui_login_surface_contract.md
  - coverage/browser_egress.yaml
created: 2026-07-31T00:48:00Z
updated: 2026-07-31T00:48:00Z
---

# Credentialed session discovery protocol

## Purpose and authority

This is the Grok-frozen protocol from research99 for the first credentialed,
headless observation of a Billy session. It is a discovery runbook, not a new
FastMCP tool, an inventory change, a live qualification, or a vision verdict.
It opens no post-login selector contract by itself.

The existing [[ui_login_surface_contract]] remains authoritative for the only
observed browser state: the queryless unauthenticated login page. The existing
`auth_status`, `auth_login_start`, and `auth_login_wait` tools own that state.
Do not add a duplicate `ui_*` login probe or a generic browser wrapper.

## Preconditions

Stop before launching a browser if any prerequisite is absent, cannot be
resolved, or identifies anything other than the dedicated non-production
organisation. Values remain outside the repository, logs, tool inputs, review
records, and browser evidence.

| Required configuration | Purpose | Retained value |
| --- | --- | --- |
| `BILLY_BROWSER_PRIMARY_REFERENCE` | Opaque keyring reference for the login identity | Opaque reference only |
| `BILLY_BROWSER_SECONDARY_REFERENCE` | Opaque keyring reference for the login secret | Opaque reference only |
| `BILLY_BROWSER_PROFILE` | MCP-owned persistent Chromium profile outside git | Owner-controlled filesystem path only |
| `BILLY_ORGANIZATION_ID` | Expected dedicated non-production organisation | Equality check only; never a default selection command |

The browser may use only `mit.billy.dk` under the reviewed egress policy. The
browser must deny `api.billysbilling.com` and `api.billy.dk`. This protocol
does not invoke the API client or require an API token: the controlling
qualification policy permits only browser-session read-back. Every browser
remains headless and download-disabled.

## Discovery sequence

1. Resolve each required reference without logging its value. Confirm the
   expected organisation and browser credentials refer to the same dedicated
   non-production context.
2. Start the MCP-owned persistent profile under the fixed egress policy. Call
   `auth_status`; on a clean profile, the expected observed result is
   `AUTH_REQUIRED`. A restored session is an observation to record, not an
   inferred `READY` state.
3. Invoke the fixed `auth_login_start` transition. It alone may fill the
   recorded login controls and click the recorded login button. It must not be
   replaced with caller-selected URLs, selectors, typing, clicking, or DOM
   export.
4. Use a discovery-only headless probe, not a public MCP browser tool, to
   record a non-sensitive post-submit summary: final route class, title class,
   control selectors and counts, trimmed labels, and challenge-widget class.
   Do not retain credentials, cookies, storage, raw DOM, request/response
   bodies, customer values, or full URLs containing identifiers.
5. Classify the exact observed state according to the table below. Unknown
   state is a blocker, not a prompt to guess selectors or expand success models.

| Observed post-submit state | Discovery result | Required action |
| --- | --- | --- |
| Login remains visible | Login-failure candidate | Freeze its exact selectors and non-sensitive message class before any later retry contract. |
| Automatable MFA controls | MFA candidate | Freeze the exact controls and separately review whether a configured TOTP reference may be resolved. |
| CAPTCHA, passkey, push approval, or another unautomatable challenge | Interaction-required candidate | Return `AUTH_INTERACTION_REQUIRED` only after this exact challenge is observed; stop automation without opening a visible browser. |
| Organisation picker | `NEEDS_ORGANISATION` candidate | Capture exact picker/submit controls and prove the selected organisation through a fresh independent interface session before naming a selection tool. |
| Authenticated shell without picker | `READY` candidate | Prove the current organisation through a fresh independent interface session before expanding an auth success model. |
| Any other route or control set | `UI_CHANGED` | Stop; record only the non-sensitive drift class and obtain a fresh discovery contract. |

## Organisation, session, and read-back evidence

When an organisation state is actually observed, close the initial page and
launch a fresh headless browser session under the same fixed Billy egress
policy. No page object, DOM locator, browser storage object, or assertion from
the first session may be reused. The second session may use the MCP-owned
persistent profile only to test session restoration; it must independently
reach a bounded Billy interface route and assert the same observed,
non-sensitive organisation or shell state.

Compare the state with the explicitly configured dedicated organisation only
where the interface exposes a stable non-sensitive identifier. If the
interface does not expose enough state to prove that comparison, keep the
workflow blocked rather than substituting an API request, token, or inferred
selector. Do not call `GET /organizations`, `GET /user/organizations`, or any
other API endpoint in this protocol.

Record only whether the fresh session restores the observed shell or returns
to the known login contract. Do not name an `EXPIRED` state,
session-restoration tool, reauthentication tool, or logout workflow until its
exact route and DOM contract have been observed.

## Evidence hygiene and cleanup

The discovery should create no business data. If a disposable record is
unavoidably created, track it, delete it, and independently read back its
absence before the run ends. Keep raw rendered frames, HAR files, traces, and
any temporary captures in owner-only storage outside the repository. A
vision-capable Grok reviewer inspects necessary frames there; purge them after
review.

The retained review record may contain only the coverage/workflow reference,
run reference, non-sensitive DOM assertion and second-interface read-back
references, reviewer verdict, timestamp, and `purge_verified: true`. It must
not contain a frame, trace, HAR, cookie, profile content, credential, token,
organisation name or ID, customer value, or raw DOM capture.

## Product handoff

After a Grok discovery brief records an observed state and is merged, implement
only the smallest matching shared `auth_*` capability. A separate Codex Power
implementation may then add typed models, bounded Playwright logic, offline
tests, and red coverage preservation; it may not claim live or vision success
until the real qualification run and required review are complete. A first
business `ui_*` workflow follows only after the shared authentication state is
proved.

Residual clear 29 and ambiguous bulk 92 are separate work under
[[wave_fives_residual_specials_research]]. This protocol authorises neither
their live methods nor another fixture-only child.

## Explicit prohibitions

- Do not run when any required non-production prerequisite is absent.
- Do not add `ui_*`, `auth_*`, browser, coverage, or webhook code from this
  protocol alone.
- Do not infer selectors, organisation selection, `READY`, session expiry, or
  MFA from configuration, title text, or an unauthenticated response.
- Do not submit production credentials, use a headed browser, or retain
  sensitive browser or customer evidence.
- Do not make a credentialed API request or use an API token for discovery,
  read-back, cleanup, or qualification.
- Do not green API, UI, live, or vision coverage from discovery planning.
