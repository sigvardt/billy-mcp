---
name: state
desc: Current Wave-5r salesTaxReturns update delivery state.
tags: [billy, sales_tax_returns, offline, writes]
sources:
  - wiki/wave_fiver_ticketed_writes_contract.md
  - src/billy_mcp/api/sales_tax_return_writes.py
created: 2026-07-30T16:03:49Z
updated: 2026-07-30T16:03:49Z
---

# state

The authorised offline `api.salesTaxReturns.update` product is implemented as
exactly two ticketed tools. Its preview is mutation-free and binds the strict
outer request; execute is ticket-only, performs one escaped PUT, and accepts
only a list-valued `salesTaxReturns` success root. The contract suite covers
schema strictness, opaque payload preservation, ticket failures, typed HTTP
errors, no-network missing-token behavior, and redaction.

The server registry contains 264 API tools. Generator-derived coverage marks
only `api.salesTaxReturns.update` implemented and contract-tested, at 179/179
offline rows with live and vision counts at zero and `complete: false`.
