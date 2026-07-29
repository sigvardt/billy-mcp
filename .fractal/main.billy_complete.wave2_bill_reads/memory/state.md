---
name: state
desc: Delivered state of the isolated Bill API read slice.
created: 2026-07-29T10:39:34Z
updated: 2026-07-29T10:39:34Z
---

# state

`src/billy_mcp/api/bill_reads.py` provides only `api_bills_get` and
`api_bills_list` registration against the locked `BillyHttpClient`. The list
request is a strict allowlist for the documented bill filters, sort values, and
page-based query controls; it excludes invoice-only filters and offset paging.

`tests/api/test_bill_reads.py` covers the documented response roots, optional
paging, query construction, local validation, both upstream authentication
envelopes, and tool registration. The delivery is offline-only: it makes no
coverage, live-test, credential, browser, server-wiring, or write claim.

No node work remains open.
