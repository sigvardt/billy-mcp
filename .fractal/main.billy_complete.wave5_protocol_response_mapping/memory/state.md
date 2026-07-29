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
---

# state

## Frozen research basis

The cited parent Grok brief, frozen write contract, approved design §§5–6 and
§8, and API inventory agree on the official-documentation fingerprint: ETag
`hsisik4g9p3603`, MD5 `c2efda0ee4cf9cf200e14910c5fc6996`. The cited brief is
read from the parent worktree scratch path
`/Volumes/ssd_1/Repositories/billy-mcp/.worktrees/main.billy_complete/.fractal/main.billy_complete/tmp/grok-research.md`;
the child-facing relative path is intentionally git-ignored. These sources are
authoritative; this leaf performs no further web, interface, or live research.

## Exact response-mapping task

`WriteOperationSpec` declares the primary changed plural root plus every other
documented changed plural root. A mapped success retains each declared root
that is present in `WriteExecutionResult.changed_records`, excludes undeclared
response roots, and does not fabricate an absent declaration. The primary root
remains required for non-delete success; declared additional roots remain
optional. The same declared-root set filters `meta.deletedRecords`: each
present declared root must be a list of strings, while absent and undeclared
metadata roots are omitted. A product response with `products` and
`productPrices` is the focused fixture, with single-root and delete responses
as regression cases.

## Inherited boundaries

Only `src/billy_mcp/api/write_protocol.py` and
`tests/unit/test_write_protocol.py` may receive product changes. Local
MockTransport doubles only: no Billy mutation, registration, coverage/client,
confirmation, auth, UI/browser, inventory, bulk-route, or shared-wiki change.
Ticket single use, canonical request binding, escaped IDs, locked relative
paths, typed invalid-success errors, optional declared-root
`meta.deletedRecords`, and the no-retry policy remain preserved behaviour.
