---
requires_approval: false
agent: codex-power
---

## Research

Reconcile the exact contract questions needed for the next implementation
slice using the already accepted Grok research handoff and independent review.
This leaf owns product implementation, not a fresh external-document or
interface-discovery pass: preserve the cited official evidence exactly and
record any implementation-relevant discrepancy for the parent instead of
making a new unsupported contract claim.

Read the approved design, current inventories, coverage status, memory, recent
plans, the accepted product-ready handoff, and the independent review. Focus
only on the `files.upload` contract and its red coverage rows. Do not contact
external services during this handoff; surface a mismatch for a later Grok
review.

Write a concise implementation brief to `$NODE_DIR/tmp/grok-research.md`,
replacing the prior iteration's file. Include:

1. Exact official source links and access dates from the accepted handoff.
2. Endpoint, method, request, response, filter, pagination, and error evidence.
3. Interface routes, fields, state transitions, plan restrictions, and API
   parity evidence.
4. Ambiguities and what live non-production observation can resolve them.
5. A bounded recommended implementation slice for Codex Power.

Never change coverage to green during research. Never use a headed browser,
touch a desktop window, expose credentials, or create persistent test data.
Clean up any disposable interface records created during discovery.
