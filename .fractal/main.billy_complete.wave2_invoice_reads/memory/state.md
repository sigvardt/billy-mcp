---
name: state
desc: Current state of the invoice read-only API slice.
created: 2026-07-29T10:39:02Z
updated: 2026-07-29T10:39:02Z
---

# state

The invoice slice is implemented in `src/billy_mcp/api/invoice_reads.py` with
strict Pydantic request models, the frozen allowlisted GET query surface, typed
FastMCP registration, opaque invoice payloads, optional paging, and propagated
typed client failures. `tests/api/test_invoice_reads.py` covers the contract
with mock transport only; focused and non-live node verification pass.
