---
name: auth_scoped_egress_ready_wait
title: Auth-scoped browser egress and post-login READY wait
desc: Path-scoped browser allow for Billy login/bootstrap API XHR, remember-checked login, dual-session READY wait, and vision purge records.
tags: [billy, auth, browser, egress, login, ready, remember, vision]
sources:
  - coverage/browser_egress.yaml
  - src/billy_mcp/browser.py
  - src/billy_mcp/models.py
  - src/billy_mcp/vision_evidence.py
  - docs/superpowers/specs/2026-07-28-billy-mcp-complete-design.md
  - .fractal/main.billy_complete/tmp/grok-research.md
  - tests/live/test_auth_dual_session.py
created: 2026-07-31T09:20:00Z
updated: 2026-07-31T11:40:00Z
---

# Auth-scoped browser egress and post-login READY wait

## Decision

Browser traffic to `api.billysbilling.com` is no longer a total deny. It is
**path-scoped** (`browser_action: path_allow`) for the auth/bootstrap set
observed in research100. The host is never fully open to the browser lane.
`api.billy.dk` remains denied. `mit.billy.dk` remains fully allowed for the app.

`auth_login_start` always checks Billy's recorded `remember` control when the
login signature is present so the MCP-owned persistent profile can restore after
process close (research101). Remember is never a tool input.

`auth_login_wait` no longer only re-reads the login form. It returns:

| Status | Meaning |
| --- | --- |
| `AUTH_REQUIRED` | Known login signature still present |
| `READY` | Path class `/:org_slug/dashboard` plus a non-PII shell marker |
| `AUTH_INTERACTION_REQUIRED` | Captcha/MFA-style control present |
| `UI_CHANGED` / `BILLY_ERROR` | Fail-closed drift or runtime failure |

`auth_status` remains login-signature-only (`AUTH_REQUIRED` success). When the
session is already READY, `auth_status` may return `UI_CHANGED`. Callers that
need READY must use `auth_login_wait`.

Tool outputs never include org slug, org name, person name, cookies, or tokens.
A UI-derived org slug may be written **outside git** under the MCP data dir for
equality checks (parent directive: discover identity through the interface).

## Dual-session live read-back

Independent second-interface read-back for auth READY is a **second ephemeral
profile** that performs a full `auth_status` → `auth_login_start` →
`auth_login_wait` sequence. It is not a second wait on the same page object and
must not use an API token.

After product remember is checked, the same profile may restore `READY` via
`auth_login_wait` after `BrowserRuntime.close()` without re-submitting
credentials.

Live harness: `tests/live/test_auth_dual_session.py` (marker `live`).

## Vision evidence

Frames for vision review are captured only under owner-only temporary storage
outside the repository (`~/.local/share/billy-mcp/vision-tmp/`). Durable records
use `src/billy_mcp/vision_evidence.py` and may live under the node `tmp/` tree.
Records store workflow ref, run id, assertion refs, second-interface ref,
reviewer verdict, timestamp, and `purge_verified`. Frames are deleted after
capture; production tools never retain screenshots, HAR, or traces.

Shared auth READY vision accept (non-inventory): a durable record under the
node `tmp/vision-records/` may show `reviewer_verdict: accept` after Grok
inspects an owner-only frame of the authenticated dashboard shell (Menu +
Overblik markers, not the login form). That does **not** green UI inventory
rows; business workflows still need their own dual-session and vision evidence.

## Egress rules (summary)

- Exact `POST /v2/user/login`
- Exact/prefix GET bootstrap set: `/v2/auth/`, `/v2/user`, `/v2/user/bootstrap`,
  `/oauth2/tokeninfo`, `/user/organizations`, `/user/umbrellas`,
  `/v2/organizations/`, `/organizations/`, `/e-invoicing/`
- Canary unlisted paths (for example `/v2/invoices`) stay denied for the browser

This is **not** API live qualification. API inventory `live_tested` stays false
with user-scoped out-of-scope policy.

## Coverage honesty

Business UI inventory rows stay red until each has dual-session e2e + vision
accept. Shared auth live harness must not green residual bulk API rows or the
full 339 UI discovery seeds by inference.

API live testing is **out of scope by user policy** (`live_tested` remains false
with that qualification). Status blockers must not claim a missing
`BILLY_API_TOKEN` as the UI gate. Official docs fingerprint for the maintained
status snapshot is ETag `wcw4x9hqvu3603` (MD5 `8b94b0135c91fd15fe54ea33e088a4be`)
as of 2026-07-31.
