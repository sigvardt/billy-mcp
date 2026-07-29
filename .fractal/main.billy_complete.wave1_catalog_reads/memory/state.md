---
name: state
desc: Current delivery state for the catalogue API read slice.
tags: [catalogue, api, reads]
sources: []
created: 2026-07-29T10:09:17Z
updated: 2026-07-29T10:09:17Z
---

# state

The catalogue API read slice is implemented in `src/billy_mcp/api/catalog_reads.py`
with typed FastMCP registration for products and product prices. Its Pydantic
inputs limit list operations to the frozen paging, include, and sort surface;
success models preserve only documented response envelopes and upstream payloads.

`tests/api/test_catalog_reads.py` verifies registration, documented relative
paths, singular and plural roots, optional paging, paging bounds, and typed
authentication errors through mock transport. The focused checks and node
commit-mode suite pass. No live credentials are available, so all four API
coverage rows remain `live_tested: false`; root server wiring and coverage state
remain intentionally outside this slice.
