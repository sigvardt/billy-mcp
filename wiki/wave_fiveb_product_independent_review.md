---
name: wave_fiveb_product_independent_review
title: Wave-5b product review superseded by P1/P2 findings
desc: Superseded Wave-5b review; P1 executor binding and P2 ticket retention need repair and independent re-review.
tags: [billy, review, writes, coverage]
sources:
  - https://www.billy.dk/api/
  - wiki/wave_fiveb_ticketed_writes_contract.md
  - coverage/status.json
  - docs/superpowers/specs/2026-07-28-billy-mcp-complete-design.md
created: 2026-07-29T16:45:00Z
updated: 2026-07-29T16:45:00Z
---

# Wave-5b product review superseded by P1/P2 findings

## Current verdict

| Claim | Result |
| --- | --- |
| Wave-5b offline product at `920ceab` | **REJECTED / superseded** |
| P1 finding | A ticket could execute through a different `*_execute` tool |
| P2 finding | Expired/consumed ticket state and prepared request bodies grew without pruning |
| Required state | Repair, full offline verification, commit, fresh independent Grok review |
| Wave-5c | **blocked** until the repaired product is independently accepted |

The original ACCEPT below is void. A fallback review reproduced an
`api_accounts_create_preview` ticket passed to
`api_daybook_balance_accounts_delete_execute` performing the stored POST. The
shared protocol did not compare the invoked executor against the ticket-bound
executor. No live, UI, vision, bulk, or completeness claim is valid from that
review. Root HEAD at the original review was `920ceab`. Official docs fingerprint
was unchanged: ETag
`hsisik4g9p3603`, MD5 `c2efda0ee4cf9cf200e14910c5fc6996`.

## Required correction

The shared write protocol must receive a fixed, server-owned execute-tool name
from every execute handler and reject a mismatch before consuming the ticket or
sending HTTP. It must also discard terminal prepared request bodies, while the
confirmation store bounds expired pending bindings and consumed replay markers
by their expiry. Tests must cover direct service rejection, a wrong executor in
the same module, a wrong executor across modules, and clock-driven lifecycle
cleanup while preserving live expiry/replay errors. A fresh Grok review of the
committed repair is mandatory.

## Repair candidate (awaiting independent review)

The root candidate now passes a fixed, server-owned execute-tool name from all
24 registered write executors into `WriteProtocolService.execute`. A mismatch
returns `CONFIRMATION_MISMATCH` before ticket consumption or HTTP. It removes
prepared request bodies after terminal execution, and the confirmation store
prunes expired pending bindings and replay markers on activity without changing
the live expiry/replay errors. Regression tests cover direct service enforcement,
a wrong executor in the same account module, the reproduced
account-to-daybook-balance cross-module path, and clock-driven ticket lifecycle
cleanup; each proves no unexpected request. Lint, Pyright, coverage and
repository-policy checks pass, as does the full non-live suite (**650** tests).
This is a repair candidate only, not a new product acceptance.

## Original review scope (not accepted)

Root registered eighteen ticketed write tools for account groups, accounts, and
daybook balance accounts. The original focused tests omitted executor identity,
so their former product acceptance is not valid.

- preview makes no Billy HTTP call
- execute sends the exact method, path, and singular-root body (or empty DELETE)
- confirmation tickets reject tamper, replay, expiry, and binding mismatches
- outer models forbid extras; execute accepts only `confirmation_ticket`

Runtime is **142** `api_*` tools. Coverage reports implemented/contract_tested
**118**, live **0**, vision **0**, `complete: false`.

The shared `ConfirmationStore` and `WriteProtocolService` remain single
instances. Bulk rows, postings and account-natures writes, specials, UI, and
live greens were not falsely advanced.

## Original root verification

The original root suite passed, but it did not contain the P1 cross-executor
regression. It must be re-run after the repair; no raw browser evidence,
credentials, or live qualification claims are involved.

## What remains red

- Live qualification for the nine Wave-5b rows
- **91** remaining clear singular write rows
- **92** ambiguous bulk rows (empty tools)
- Four specials still red; UI 339 all red; vision 0
- Unauthenticated DELETE empty 200 is not cleanup proof
- Unauthenticated natures/postings CUD still **405** despite some docs Supports flags

## Next product gate

Do not start Wave-5c. First repair and independently re-review the Wave-5b
executor binding, then promote the already-red Wave-5c research to a shared
freeze.

Full scratch report: node `tmp/grok-review.md` (not durable; this wiki page is
the shared summary).
