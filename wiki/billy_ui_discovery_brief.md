---
name: billy_ui_discovery_brief
desc: First read-only headless Billy UI discovery result for mit.billy.dk (auth blocked).
tags: [billy, ui, discovery, headless]
sources:
  - docs/superpowers/specs/2026-07-28-billy-mcp-complete-design.md
  - /Volumes/ssd_1/Repositories/billy-mcp/.worktrees/main.billy_complete/.fractal/main.billy_complete/tmp/grok-research.md
  - https://www.billy.dk/api/
created: 2026-07-29T09:35:00Z
updated: 2026-07-30T20:45:00Z
---

# billy_ui_discovery_brief

First current, non-sensitive interface-discovery brief for parent integration.
This is **not** a completeness claim and **does not** green any coverage row,
register any UI tool, or assert `not_applicable` for API parity.

## Verdict

**Blocked before authenticated navigation.** Headless Chromium reached the
Billy login screen on host `mit.billy.dk` only. No persisted session restored
to an app shell. UI email/password/TOTP credentials and API token material were
absent from process environment and default keyring account. No login submit
was attempted. No CAPTCHA, passkey, push approval, or MFA challenge was shown
(login form only). No business writes.

Research89 reconfirm (2026-07-30): still login-only without credentials. Chrome
locale observed as **English** (`title=Login`, submit `Log in`, placeholders
`Email`/`Password`, “Keep me logged in”, “Forgot your password?”, “Sign up”,
“Help”). Prior pass saw Danish labels. Prefer `name=` selectors; match both
`Log in` and `Log ind` for submit text.

## Method (observed)

| Control | Setting used |
| --- | --- |
| Runtime | Project `BrowserRuntime` + `BrowserEgressPolicy` (`src/billy_mcp/browser.py`) |
| Browser | Chromium, **headless forced on**, no desktop window controls |
| Profile | MCP default path (`DEFAULT_BROWSER_PROFILE`); directory existed with prior `mit.billy.dk` IndexedDB/Cookies files (session still unauthenticated at load) |
| Allowlist | Exact host `mit.billy.dk` only (HTTPS, default port) |
| Target | `https://mit.billy.dk/` only (redirect handled by app to `/login`) |
| API via browser | Not used |
| Official API docs | Context only via parent research / design; **not** loaded in the browser lane |
| Writes | None (no form submit, no settings change, no record create) |

## Auth surface (pre-browser)

| Signal | Result |
| --- | --- |
| `BILLY_API_TOKEN` env | absent |
| UI email/password/TOTP env names checked | absent |
| Keyring `billy-mcp` / `default` | absent |
| `BILLY_BROWSER_PROFILE` override | absent (default used) |
| Profile directory | present |

## Session state

| Field | Observed |
| --- | --- |
| Final host | `mit.billy.dk` |
| Final path | `/login` |
| Document title | `Log ind` |
| Classification | `unauthenticated_login` |
| Authenticated app chrome | not observed |

## Routes / screens actually reached

Only facts from this headless pass. **No inferred routes.**

| Path | Title | Status |
| --- | --- | --- |
| `/login` (after open of `/`) | Log ind | **observed** |

Blocked / not reached: any post-login route, org picker, settings, invoice or
other product screens. Parent research previously noted SPA shell “Shine” at
HTTP 200 for unauthenticated host checks; this pass specifically landed the
login route under the MCP profile and did not treat marketing or API hosts as
UI routes.

## Safe selectors / DOM assertions (non-sensitive)

Stable **names** and labels observed on `/login` (Ember-generated element `id`
values are session-unstable; prefer `name` / type / visible button text):

| Assertion target | Observed signal |
| --- | --- |
| Email field | `input[type=email][name=email]` placeholder `E-mail` |
| Password field | `input[type=password][name=password]` placeholder `Adgangskode` |
| Remember | `input[type=checkbox][name=remember]` |
| Submit | `button` visible text `Log ind` |
| Forgot password | link text `Har du glemt din adgangskode?` |
| Signup CTA | text `Tilmeld dig gratis` |
| Help link text | `Hjælp` (href points off-host to support; **not navigated**; egress would deny non-allowlisted hosts) |

Body cues (redacted): login framing with “Forbliv logget på” and the login
button; password field present.

## Independent read-back possibility

| Observed UI | Possible later read-back | Status |
| --- | --- | --- |
| Login screen only | None (no business entity rendered) | no business read-back in this pass |
| Post-login app (not reached) | API reads on `https://api.billysbilling.com/v2` after separate token auth | **unverified** |

No API call was made in this discovery pass.

## Plan / MFA / credential blocks

| Blocker | Evidence |
| --- | --- |
| **Credentials absent** | Login form shown; no env UI credentials; no automated submit |
| MFA / CAPTCHA / passkey / push | **Not observed** on the login screen in this pass |
| Plan / paywall gate | **Not observed** (never past login) |
| Session restore | Profile storage present for host, but load still served `/login` |

## No-write confirmation

- No button click on `Log ind`
- No credential typing
- No create/edit/delete of Billy records
- No settings or access-token UI exercised
- `writes_attempted: false` in run metadata

## Evidence purge

| Item | Result |
| --- | --- |
| Headless screenshot for classification | Captured under node scratch only, then deleted |
| Purge result | **purged** (file absent after run; ~25 KiB before delete) |
| Durable brief retention | No frame paths, no cookies, no secrets, no PII |

Scratch JSON under the node `tmp/` directory is git-ignored working metadata
only and is not a coverage artifact.

## Coverage posture

- No `coverage/*` row edited or greened by this node
- No UI tool registered
- No `not_applicable` API parity claim from UI absence
- All authenticated UI families remain **unverified / red** until a future
  non-production-org workflow with credentials, DOM assertions, independent
  read-back, and durable review evidence

## Citations

1. Design: `docs/superpowers/specs/2026-07-28-billy-mcp-complete-design.md`
   (headless policy §4.6 / §10; browser auth §7.2: reuse session, stop on
   unautomatable MFA/CAPTCHA/passkey/push).
2. Parent research brief:
   `/Volumes/ssd_1/Repositories/billy-mcp/.worktrees/main.billy_complete/.fractal/main.billy_complete/tmp/grok-research.md`
   (browser host `mit.billy.dk`; deny API hosts in browser; UI discovery blocked
   without credentials).
3. Official API docs `https://www.billy.dk/api/` for API parity **context only**
   (not fetched in the browser lane during this pass).

## Observed vs blocked vs unverified

| Class | Items |
| --- | --- |
| **Observed** | Headless allowlisted open of `mit.billy.dk`; redirect to `/login`; login form fields/names above; credential/keyring absence; frame purged; no writes |
| **Blocked** | Authenticated navigation and product route inventory (credentials absent) |
| **Unverified** | MFA shape after password, org selection, plan gates, all post-login routes, any API↔UI parity mapping, session longevity |
