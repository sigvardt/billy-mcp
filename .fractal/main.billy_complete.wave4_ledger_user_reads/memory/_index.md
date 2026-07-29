---
name: memory
desc: Private working state for the Wave-4 ledger/users leaf.
tags: [billy, wave4, ledger, users]
sources:
  - tmp/grok-research.md
  - tmp/grok-review.md
  - wiki/wave_four_remaining_clear_reads_contract.md
created: 2026-07-29T12:29:18Z
updated: 2026-07-29T12:46:46Z
---

# memory

***

## Product state

- Owned files present (working tree, not yet committed):
  - `src/billy_mcp/api/ledger_user_reads.py`
  - `tests/api/test_ledger_user_reads.py`
- Six tools: transactions/postings/users get+list on `/transactions`,
  `/postings`, `/users` with documented roots and flat forbid inputs.
- Independent review: **PASS** (offline contract). Report: `tmp/grok-review.md`.
- Focused verification: pytest 25 passed; ruff format/check pass; `uv run
  pyright` 0 errors on owned files; node lint passes; non-live node suite 300
  passed. Full mode fails closed only at the global incomplete-coverage gate.

## Coverage / claims

- Inventory six get/list rows still false/false/false.
- `status.complete` false.
- Live, UI, vision red. No greening from this leaf.
- `server.py` does not register the module yet (root integration).

## Contract anchors

- Freeze: `wiki/wave_four_remaining_clear_reads_contract.md` Ledger + users.
- Research: `tmp/grok-research.md`.
- Docs fingerprint: ETag `hsisik4g9p3603`, MD5 `c2efda0ee4cf9cf200e14910c5fc6996`.
- `/users` resource distinct from bootstrap `/user` specials (intact).
