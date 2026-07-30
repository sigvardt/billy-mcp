---
name: state
desc: Current fail-closed boundary for the Wave-5u bulk-delete form-matrix harness.
created: 2026-07-30T23:25:05Z
updated: 2026-07-30T23:25:05Z
---

# state

`src/billy_mcp/live_probe.py` fixes bulk-delete candidate query construction to
`ids[]` and keeps research95 form observations immutable: empty forms are
`INVALID_DELETE_ID_ARRAY` validation errors, while a synthetic-id metadata-only
success remains unqualified.

Every frozen residual and bulk candidate has a default-deny real-method gate
whose required non-persistence, dual-organisation, owner-only evidence,
cleanup, and independent-read-back fields are all false. The only runner path
remains the existing OPTIONS observation loop, which is unqualified and
redacted.

Focused unit tests, Ruff, Pyright, and the node lint/test scripts pass. No
coverage, status, tool, credential, browser, or live-request surface changed.
