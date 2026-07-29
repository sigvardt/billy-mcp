---
name: state
desc: Current Wave-5a response-mapping delivery state.
tags: [wave-5a, write-protocol, response-mapping]
sources:
  - wiki/wave_five_ticketed_writes_contract.md
  - .fractal/main.billy_complete/tmp/grok-research.md
  - docs/superpowers/specs/2026-07-28-billy-mcp-complete-design.md
  - coverage/api_v2_manifest.yaml
  - src/billy_mcp/api/write_protocol.py
  - tests/unit/test_write_protocol.py
created: 2026-07-29T14:10:20Z
updated: 2026-07-29T14:10:20Z
---

# state

## Frozen basis

The cited official-documentation fingerprint is ETag `hsisik4g9p3603` and MD5
`c2efda0ee4cf9cf200e14910c5fc6996`. The frozen contract and cited parent Grok
brief are authoritative; this leaf performs no further web, interface, or live
research.

## Required hardening

`WriteOperationSpec` must let a resource declare each documented changed plural
root. A successful response must retain every declared root that is present in
`WriteExecutionResult.changed_records`, while preserving the required primary
root rule for non-delete writes and never fabricating an absent declared root.
Undeclared response roots stay excluded. Existing typed invalid-success errors,
delete handling, and primary-root `meta.deletedRecords` behaviour remain
unchanged.

The focused fixture is a product response containing both `products` and
`productPrices`; both must survive mapping. Existing single-root and delete
fixtures remain the regression guard.

## Boundaries

Only `src/billy_mcp/api/write_protocol.py` and
`tests/unit/test_write_protocol.py` may receive product changes. The work uses
local MockTransport doubles only and does not alter registration, coverage,
client, confirmations, authentication, UI/browser, inventory, bulk routes, or
the shared wiki. Tickets, paths, canonical bindings, and the no-retry policy
are out of scope for behavioural change and must remain covered.
