---
name: auth_scoped_egress_ready_wait
title: Auth-scoped browser egress and post-login READY wait
desc: Path-scoped browser allow for Billy login/bootstrap API XHR and typed auth_login_wait READY vs AUTH_REQUIRED observation.
tags: [billy, auth, browser, egress, login, ready]
sources:
  - coverage/browser_egress.yaml
  - src/billy_mcp/browser.py
  - src/billy_mcp/models.py
  - docs/superpowers/specs/2026-07-28-billy-mcp-complete-design.md
  - .fractal/main.billy_complete/tmp/grok-research.md
created: 2026-07-31T09:20:00Z
updated: 2026-07-31T09:20:00Z
---

# Auth-scoped browser egress and post-login READY wait

## Decision

Browser traffic to `api.billysbilling.com` is no longer a total deny. It is
**path-scoped** (`browser_action: path_allow`) for the auth/bootstrap set
observed in research100. The host is never fully open to the browser lane.
`api.billy.dk` remains denied. `mit.billy.dk` remains fully allowed for the app.

`auth_login_wait` no longer only re-reads the login form. It returns:

| Status | Meaning |
| --- | --- |
| `AUTH_REQUIRED` | Known login signature still present |
| `READY` | Path class `/:org_slug/dashboard` plus a non-PII shell marker |
| `AUTH_INTERACTION_REQUIRED` | Captcha/MFA-style control present |
| `UI_CHANGED` / `BILLY_ERROR` | Fail-closed drift or runtime failure |

Tool outputs never include org slug, org name, person name, cookies, or tokens.
A UI-derived org slug may be written **outside git** under the MCP data dir for
equality checks (parent directive: discover identity through the interface).

## Egress rules (summary)

- Exact `POST /v2/user/login`
- Exact/prefix GET bootstrap set: `/v2/auth/`, `/v2/user`, `/v2/user/bootstrap`,
  `/oauth2/tokeninfo`, `/user/organizations`, `/user/umbrellas`,
  `/v2/organizations/`, `/organizations/`, `/e-invoicing/`
- Canary unlisted paths (for example `/v2/invoices`) stay denied for the browser

This is **not** API live qualification. API inventory `live_tested` stays false
with user-scoped out-of-scope policy.

## Coverage honesty

Live and vision UI flags remain red until dual-session e2e + vision review.
No business `ui_*` tools are introduced by this contract.

API live testing is **out of scope by user policy** (`live_tested` remains false
with that qualification). Status blockers must not claim a missing
`BILLY_API_TOKEN` as the UI gate. Official docs fingerprint for the maintained
status snapshot is ETag `wcw4x9hqvu3603` (MD5 `8b94b0135c91fd15fe54ea33e088a4be`)
as of 2026-07-31.

Independent second-interface read-back for live qualification requires a fresh
browser session or independent path, not only a second wait on the same
persistent profile.
