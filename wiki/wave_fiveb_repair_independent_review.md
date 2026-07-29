---
name: wave_fiveb_repair_independent_review
title: Wave-5b P1/P2 repair independent review ACCEPT
desc: Independent Grok acceptance of the ticketed-write executor-binding and ticket-prune repair on root a2a0996.
tags: [billy, review, writes, coverage]
sources:
  - https://www.billy.dk/api/
  - wiki/wave_fiveb_ticketed_writes_contract.md
  - wiki/wave_fiveb_product_independent_review.md
  - coverage/status.json
  - docs/superpowers/specs/2026-07-28-billy-mcp-complete-design.md
created: 2026-07-29T17:20:00Z
updated: 2026-07-29T17:20:00Z
---

# Wave-5b P1/P2 repair independent review ACCEPT

## Verdict

| Claim | Result |
| --- | --- |
| Wave-5b offline product at `920ceab` (pre-repair) | **REJECTED / superseded** |
| Wave-5b offline product with P1/P2 repair at `a2a0996` | **ACCEPT** |
| Live, UI, vision, bulk, completeness | **not claimed / fail-closed** |
| Wave-5c product work | **allowed only after** the Wave-5c research brief is promoted to a shared wiki freeze |

Reviewed commit: `a2a0996`. Official docs fingerprint unchanged: ETag
`hsisik4g9p3603`, MD5 `c2efda0ee4cf9cf200e14910c5fc6996`, 147934 bytes.

## What was wrong

At `920ceab`, a confirmation ticket bound for one execute tool could run through
a different `*_execute` tool because `WriteProtocolService.execute` did not
receive the invoked executor name. Fallback review reproduced an
`api_accounts_create_preview` ticket driving HTTP through
`api_daybook_balance_accounts_delete_execute`. Expired and consumed ticket
state plus prepared request bodies also grew without pruning.

## What the repair proves

- Every preview binds `WriteOperationSpec.execute_tool_name` into the ticket.
- Every one of the 24 execute handlers passes that exact server-owned name into
  `WriteProtocolService.execute`.
- A mismatch returns `CONFIRMATION_MISMATCH` before ticket consumption and
  before HTTP. The original ticket remains usable only by its bound executor.
- Successful execution discards the prepared request body while preserving
  replay markers. Expired prepared bodies and expired confirmation records are
  pruned on activity without hiding live expiry or replay errors.

Focused offline evidence this review:

```text
uv run pytest -q \
  tests/unit/test_write_protocol.py \
  tests/unit/test_confirmations.py \
  tests/api/test_account_writes.py \
  tests/api/test_daybook_balance_account_writes.py \
  tests/unit/test_coverage_server.py \
  tests/coverage/test_coverage_inventory.py
```

**109 passed.** Runtime remains **142** `api_*` tools plus two coverage tools.
Coverage remains implemented/contract_tested **118**, live **0**, vision **0**,
`complete: false`. No Wave-5b row was greened for live use. No bulk, special,
or UI row was greened. No credentials or browser evidence entered the tree.

## Cross-module regression retained

`tests/api/test_account_writes.py` keeps:

- same-module wrong executor (account create ticket on account-group delete)
- cross-module wrong executor (account create ticket on daybook-balance delete)

Both assert `CONFIRMATION_MISMATCH` and zero HTTP, then prove the correct
executor still runs once.

## Qualification boundaries

- The nine Wave-5b CUD inventory rows remain offline-only until live
  non-production tests exist.
- Unauthenticated DELETE empty 200 is not cleanup proof.
- Unauthenticated postings and accountNatures CUD still return 405 despite some
  docs Supports flags; they stay red without tools.
- The 92 ambiguous bulk rows stay red with empty tools.
- Wave-5c daybook transaction and line CUD remain red until implemented under
  the same executor-binding protocol after a shared freeze of the research
  brief.

## Supersedes

This ACCEPT supersedes the repair-candidate language on
`wiki/wave_fiveb_product_independent_review.md` for product state. That page
remains the historical record of the original defect and the void ACCEPT at
`920ceab`.

Full scratch report: node `tmp/grok-review.md` (not durable; this wiki page is
the shared summary).
