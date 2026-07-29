---
name: state
desc: Current delivery state for the Wave-4 tax read slice.
tags: [tax, wave4, read_only]
sources: []
created: 2026-07-29T12:25:11Z
updated: 2026-07-29T12:25:11Z
---

# state

## Current

- `src/billy_mcp/api/tax_reads.py` contains all 16 frozen tax get/list tools.
- `tests/api/test_tax_reads.py` covers every path/root, encoded ID, query
  surface, optional metadata envelope, strict input rejection, typed 401, and
  flat registry schema.
- The independent offline review passed. Its optional list-root error coverage
  recommendation is incorporated.

## Verified

- Focused tax suite passes with 163 tests.
- The non-live project suite passes with 387 tests.
- Ruff format/check and Pyright pass.
- Full qualification deliberately fails only at the fail-closed coverage gate:
  coverage is incomplete, 92 bulk rows remain ambiguous, and all live/UI
  qualification states remain red.

## Boundaries

- The frozen Wave-4 contract and Grok brief remain the sole tax evidence.
- Coverage, root server registration, redaction, writes, bulk, live testing,
  UI, and completeness claims are owned outside this leaf.
