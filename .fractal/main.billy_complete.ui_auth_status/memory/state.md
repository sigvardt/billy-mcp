---
name: state
desc: Completed auth-status implementation facts and verification posture.
created: 2026-07-30T21:44:11Z
updated: 2026-07-30T21:44:11Z
---

# state

`auth_status` is a registered, read-only FastMCP tool backed by the existing
headless `BrowserRuntime`. It opens only `https://mit.billy.dk/`, recognises
only the exact HTTPS `/login` route with visible email, password, remember-me,
and `button[data-cy="login-button"]` submit control whose exact trimmed label
is `Log in` or `Log ind`, and otherwise returns structured `UI_CHANGED`.
Browser runtime failures are structured and do not include session or credential
values.

The implementation changes only the permitted browser, models, server, and
focused test files. UI coverage artifacts and their red status are unchanged;
this offline check does not qualify any UI workflow. Full formatting, Ruff,
Pyright, the focused test suite, and the node non-live test command passed.

Independent Grok review after parent merge remains outside this node's completed
implementation scope.
