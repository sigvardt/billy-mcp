---
name: state
desc: Delivered daybook-transaction read slice state.
created: 2026-07-29T10:37:08Z
updated: 2026-07-29T10:37:08Z
---

# state

The daybook-transaction slice is implemented in
`src/billy_mcp/api/daybook_transaction_reads.py` with only two typed FastMCP
registrations: `api_daybook_transactions_get` and
`api_daybook_transactions_list`. It uses the locked client, relative paths,
strict request models, typed success responses, and typed client failures.

`tests/api/test_daybook_transaction_reads.py` verifies the frozen query
allowlist, local validation, response roots, optional paging, both documented
authentication envelopes, and registration. Server wiring and coverage state
remain intentionally owned by the parent node.
