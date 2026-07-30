---
name: wave5t_ui_auth_discovery
desc: Cited headless Billy UI/auth discovery fallback: session reuse reaches login only; no UI coverage is qualified.
tags: [billy, ui, auth, discovery, headless, research]
sources:
  - https://www.billy.dk/api/
  - docs/superpowers/specs/2026-07-28-billy-mcp-complete-design.md
  - src/billy_mcp/browser.py
  - src/billy_mcp/server.py
  - coverage/browser_egress.yaml
  - coverage/ui_workflows_manifest.yaml
  - coverage/status.json
  - wiki/billy_ui_discovery_brief.md
  - wiki/wave_fives_residual_specials_research.md
created: 2026-07-30T20:49:03Z
updated: 2026-07-30T20:49:03Z
---

# wave5t_ui_auth_discovery

This Codex Power fallback repeated the bounded interface check after the
designated Grok discovery leaf could not begin. It is a research record only:
no UI workflow was implemented, no coverage row changed, and no live
qualification, read-back, or vision result is claimed.

## Result

**The MCP-owned headless session reached Billy's unauthenticated login route;
it did not restore an authenticated session.** The observed state requires the
future typed result `AUTH_REQUIRED`, not `AUTH_INTERACTION_REQUIRED`: no
unautomatable challenge was observed before credential entry.

| Class | Evidence |
| --- | --- |
| Observed | A headless `BrowserRuntime` open of `https://mit.billy.dk/` returned HTTP 200 and ended at `https://mit.billy.dk/login`. The login signature contained the email, credential, remember-me, and localized login-submit controls. |
| Observed | No authenticated application shell, organisation picker, or business route was reached. No form was submitted and no business action occurred. |
| Existing code | `BrowserRuntime` forces headless persistent Chromium, disables downloads, and applies the reviewed egress policy before navigation. The browser allowlist admits `mit.billy.dk` for typed UI/auth work only. |
| Existing code | The current server registers API and coverage tools, but no `auth_*` or `ui_*` workflow. |
| Inference | The first safe implementation slice is a read-only `auth_status` state machine, not a generic browser-control capability. |

The persistent browser context was opened only to test session reuse. Its
contents were neither inspected nor retained.

## Reachable authentication and navigation state

The table contains only reachable or directly documented entry points; it does
not assert discovery of the interface inventory.

| Entry point or evidence | Future typed workflow | Current state |
| --- | --- | --- |
| Login route and stable control signature | `auth_status` | **Observed.** Report the login state as `AUTH_REQUIRED`; fail closed if the expected route/signature changes. |
| Login transition | `auth_login_start`, then `auth_login_wait` | **Blocked.** No secure browser-login material was available to this run, so no credential entry or submit was attempted. |
| Reauthentication | `auth_reauthenticate` | **Unverified.** A post-login session and expiry transition were not reached. |
| Organisation state | `auth_organizations_list`, `auth_organization_select` | **Unverified.** No organisation selector was reached. The local API manifest's `GET /v2/user/organizations` is only a possible later independent read-back and was not called here. |
| Access-token settings | `auth_api_token_bootstrap_preview`, `auth_api_token_bootstrap_execute` | **Documented only.** Billy's official documentation names Settings → Access tokens; this interface route was not navigated. |
| Product navigation and API-parity families | typed `ui_*` workflows | **Blocked at login.** No post-login entry point was observed, so no parity mapping is claimed. |

`AUTH_INTERACTION_REQUIRED` is deliberately not recommended here. The approved
design reserves it for an observed CAPTCHA, passkey, push approval, or other
unautomatable challenge; none was presented on the observed login state.

## Current coverage and runtime posture

`coverage/status.json` remains incomplete: 184 API rows are implemented and
contract-tested offline, with zero live-tested or vision-verified rows. All 339
UI rows remain red: none is discovered, implemented, contract-tested,
live-tested, or vision-verified. This discovery neither changes that status nor
marks an API-parity row inapplicable.

The approved design requires a dedicated persistent context, headless operation
only, exact reviewed browser egress, typed state machines, and no raw
navigation/click/type/DOM-dump tools. The current implementation supplies the
bounded runtime and policy, but not the future auth registration. Those
existing-code findings are consistent with the earlier
[[billy_ui_discovery_brief]] and the live-gated API posture in
[[wave_fives_residual_specials_research]].

## Next implementation path and prerequisites

Before a UI/auth implementation leaf may proceed, provide all of the following
outside the repository:

1. A dedicated non-production Billy organisation, identified and selected
   explicitly; do not use a production organisation.
2. Either a valid existing MCP-owned browser session or securely provisioned
   Billy browser-login credentials. If the actual post-entry flow shows an
   unautomatable challenge, stop, record only its classification, and return
   `AUTH_INTERACTION_REQUIRED` without opening a visible browser.
3. An organisation-scoped API access credential only when independent API
   read-back is required; it must remain outside source, logs, and evidence.

With those prerequisites, implement one narrow `auth_status` workflow first.
It should launch only the existing `BrowserRuntime`, validate the allowlisted
root/login signature, return `AUTH_REQUIRED` for the observed state, and return
`UI_CHANGED` for an unknown signature. A separate typed login transition and
organisation-selection workflow can follow only after a non-production session
proves its DOM states. Do not add generic browser navigation, selector, click,
type, or DOM-export controls.

## Evidence hygiene

No business record, settings change, email, or invoice action was performed.
No sensitive authentication value, session-store content, downloaded file,
customer value, or raw temporary capture was retained. The bounded check
created no raw evidence requiring repository retention or later cleanup.

## Sources

- [Billy API v2 documentation](https://www.billy.dk/api/) (accessed
  2026-07-30): API base, the web-app/API relationship, company-scoped access
  tokens, and the documented Settings → Access tokens path.
- `docs/superpowers/specs/2026-07-28-billy-mcp-complete-design.md` §§1–2,
  4.6, 7.2–7.3, 10–11, and 13: headless-only policy, auth states, typed-tool
  boundary, egress, and stable errors.
- `src/billy_mcp/browser.py`, `src/billy_mcp/server.py`, and
  `coverage/browser_egress.yaml`: runtime, registration, and exact-host
  findings.
- `coverage/status.json`, `coverage/ui_workflows_manifest.yaml`,
  `coverage/api_v2_manifest.yaml`: current red UI posture and the potential
  organisation read-back endpoint.

