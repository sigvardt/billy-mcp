---
name: state
desc: Current terminal state of the Research96 fail-closed harness fixture slice.
created: 2026-07-30T23:51:09Z
updated: 2026-07-30T23:51:09Z
---

# state

Research96 is represented only by strict frozen, non-network fixtures in
`src/billy_mcp/live_probe.py`. The fixture set covers each frozen residual id
once, the query-only repeated `ids[]` bulk-delete form and rejected JSON/form
body forms, and the organisation-path ambiguity without inferring a replacement
route.

`tests/unit/test_live_probe.py` verifies exact membership and classifications,
adversarial validation failures, body/query rejection, static path ambiguity,
and the existing no-token/missing-gate pre-network denial. The runner remains
OPTIONS-only; no tool, coverage, cleanup, credential, or live-network path was
added.
