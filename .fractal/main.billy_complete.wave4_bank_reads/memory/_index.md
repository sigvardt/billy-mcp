---
name: memory
desc: Node private state for the scoped Wave-4 bank read leaf.
tags: [bank_reads, review]
sources:
  - https://www.billy.dk/api/
  - wiki/wave_four_remaining_clear_reads_contract.md
  - tmp/grok-research.md
  - tmp/grok-review.md
created: 2026-07-29T12:23:54Z
updated: 2026-07-29T12:23:54Z
---

# memory

***

## Status

The bank read leaf is independently accepted and contains only its two owned
product files. The review report is `tmp/grok-review.md`.

## Implementation stands

- `src/billy_mcp/api/bank_reads.py` and `tests/api/test_bank_reads.py` implement
  and test the frozen read contract.
- Ten tools: bankPayments, bankLineMatches, bankLines, bankLineSubjectAssociations, balanceModifiers get+list.
- Focused gates: 25 pytest pass; ruff format/check; pyright 0 errors.
- Module-local `register_bank_read_tools` only; root `server.py` not wired (parent).
- Inventory ten rows still implemented=false, contract_tested=false, live_tested=false; complete=false.

## Contract facts (durable)

- Docs fingerprint: etag `hsisik4g9p3603`, 147934 bytes, MD5 `c2efda0ee4cf9cf200e14910c5fc6996`.
- Roots/paths match freeze; no list filters; reject offset and parent ids.
- Opaque records; optional meta.paging without fabricated null metadata fields.
- 401 AUTHENTICATION_REQUIRED + OAUTH_INVALID_ACCESS_TOKEN → AUTH_REQUIRED.
- Existing redaction covers bank* keys on log/error path; success stays opaque.
- No writes, bulk, UI, live, or coverage greens in leaf scope.

## Review findings

- Independent review required no code fixes. Its optional BankMeta null-paging
  polish is implemented and regression-tested.
- Inventory sensitivity and root registration are parent-owned boundaries;
  service-level contract tests already cover every get handler.

## Out of scope

Coverage greening, server registration, other Wave-4 clusters, live/UI.
