---
name: state
desc: Durable delivery state for the bootstrap API read module.
created: 2026-07-29T10:10:53Z
updated: 2026-07-29T10:10:53Z
---

# state

The bootstrap read delivery is complete in
`src/billy_mcp/api/bootstrap_reads.py` with focused coverage in
`tests/api/test_bootstrap_reads.py`. It registers `api_user_get`,
`api_user_list_organizations`, `api_organizations_get`, and
`api_organizations_list` against an injected `BillyHttpClient` only.

The module preserves only documented envelope roots and opaque record/paging
objects, accepts no inferred filters or generic HTTP controls, and uses shared
redaction for sensitive organisation fields. FastMCP wraps each declared
success-or-`ToolError` union in a typed `result` output field; the contract test
asserts that both schema variants are present.

Mock transport verification covers paths, query parameters, root mapping,
optional paging, paging limits, and both documented 401 error envelopes. No
credential was available or used, so live verification remains false. Server
wiring and coverage-manifest files are not part of the delivered commit.
