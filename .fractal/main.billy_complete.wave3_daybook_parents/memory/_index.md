---
name: memory
desc: Node-private working state for Wave-3 daybook-parent leaf.
tags: [daybook, research]
sources:
  - https://www.billy.dk/api/
  - wiki/wave_three_unfiltered_reads_contract.md
created: 2026-07-29T11:09:46Z
updated: 2026-07-29T11:27:00Z
---

# memory

***

## Status

The scoped delivery contains `src/billy_mcp/api/daybook_reads.py` and
`tests/api/test_daybook_reads.py`. It provides four typed, read-only tools for
daybooks and daybook balance accounts; it excludes server wiring, coverage,
live calls, UI, writes, and bulk operations. Focused mock-transport tests pass,
as do the node test suite, Ruff, and Pyright.

Full qualification correctly remains unavailable: coverage status is incomplete,
92 bulk contracts are ambiguous, and the wider API/UI rows lack live evidence.
Those root-owned states were not changed by this leaf.

## Implementation pattern

The frozen inputs permit only documented list paging, include, and sorting
controls. Empty include and sort-property strings are rejected. Opaque response
records preserve unmodelled fields, response metadata preserves optional
`meta.paging`, and the shared client retains typed authentication errors.
Module-local `register_daybook_read_tools` exposes exactly four tools. Existing
root server and coverage owners control their later wiring and evidence updates.

## Docs fingerprint

etag `hsisik4g9p3603`, MD5 `c2efda0ee4cf9cf200e14910c5fc6996` (unchanged).
