---
requires_approval: false
agent: codex-power
---

## Research

Research the exact contract questions needed for the next implementation slice.
Use Billy's current official API documentation as the primary source. Use the
dedicated non-production Billy interface for interface discovery. Use other
sources only to locate primary evidence, never as the contract.

Read the approved design, current inventories, coverage status, memory, recent
plans, and unresolved review findings. Focus on red, unknown, ambiguous, or
plan-gated rows. Check whether Billy documentation changed since the last
recorded source review.

Write a concise cited brief to `$NODE_DIR/tmp/codex-power-research.md`,
replacing the prior iteration's file. This is the authorised fallback after
Grok's pre-edit authentication failure; it must identify itself as such and
must not be represented as the required future Grok audit. Include:

1. Exact official source links and access dates.
2. Endpoint, method, request, response, filter, pagination, and error evidence.
3. Interface routes, fields, state transitions, plan restrictions, and API
   parity evidence.
4. Ambiguities and what live non-production observation can resolve them.
5. A bounded recommended implementation slice for Codex Power.

Never change coverage to green during research. Never use a headed browser,
touch a desktop window, expose credentials, or create persistent test data.
Clean up any disposable interface records created during discovery.
