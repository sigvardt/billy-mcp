---
name: state
desc: Delivered reference-data read module status and verification.
created: 2026-07-29T10:09:39Z
updated: 2026-07-29T10:09:39Z
---

# state

The reference-data delivery consists of `src/billy_mcp/api/reference_reads.py`
and `tests/api/test_reference_reads.py`. It provides typed Pydantic input and
success models plus FastMCP registration for currencies, countries, and locales
get/list tools. Responses preserve opaque record fields and map only documented
singular/plural roots and optional paging.

Focused format, lint, Pyright, and pytest checks pass. The node lint and test
scripts also pass with 48 offline tests. No credentials are available, so all
six coverage rows remain `live_tested: false`; server wiring and coverage
manifest updates remain parent-owned.
