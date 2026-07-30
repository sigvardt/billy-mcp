---
name: state
desc: Current state of the scoped offline browser-auth implementation.
created: 2026-07-30T22:31:17Z
updated: 2026-07-30T22:31:17Z
---

# state

The offline browser-auth slice has strict opaque reference plumbing, a bounded
keyring resolver seam, and empty-input typed `auth_login_start` and
`auth_login_wait` tools. The browser transition validates the fixed observed
login page before resolution and before each internal action, forces the
existing headless/download-disabled/egress policy, and returns redacted stable
errors on every unqualified path.

Focused fakes cover missing or unresolvable references, signature drift,
ordering, closure, redaction, no challenge lookup, and typed schemas. Ruff,
Pyright, the focused tests, and the node test script pass. No live login,
organisation state, bootstrap, coverage, or independent product review claim
is part of this implementation.
