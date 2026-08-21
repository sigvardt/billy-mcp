---
name: wave_fiveb_product_independent_review
title: Wave-5b product review — original REJECT and repair ACCEPT pointer
desc: Historical REJECT of Wave-5b at 920ceab; repaired product ACCEPT lives on wave_fiveb_repair_independent_review.
tags: [billy, review, writes, coverage]
sources:
  - https://www.billy.dk/api/
  - wiki/wave_fiveb_ticketed_writes_contract.md
  - wiki/wave_fiveb_repair_independent_review.md
  - coverage/status.json
  - docs/superpowers/specs/2026-07-28-billy-mcp-complete-design.md
created: 2026-07-29T16:45:00Z
updated: 2026-07-29T17:20:00Z
---

# Wave-5b product review — original REJECT and repair ACCEPT pointer

## Authoritative current verdict

| Claim | Result |
| --- | --- |
| Wave-5b offline product at `920ceab` | **REJECTED / superseded** |
| Wave-5b offline product with P1/P2 repair at `a2a0996` | **ACCEPT** — see `wiki/wave_fiveb_repair_independent_review.md` |
| Live, UI, vision, bulk, completeness | **not claimed / fail-closed** |

The durable acceptance of the repaired product is recorded on
`wiki/wave_fiveb_repair_independent_review.md`. Do not treat the historical
ACCEPT text below as current product state.

## Historical defect at `920ceab`

A ticket bound for one execute tool could run through a different `*_execute`
tool. Fallback review reproduced an `api_accounts_create_preview` ticket passed
to `api_daybook_balance_accounts_delete_execute` performing the stored POST.
The shared protocol did not compare the invoked executor against the
ticket-bound executor. Expired/consumed ticket state and prepared request bodies
also grew without pruning. Official docs fingerprint at that review was
unchanged: ETag `hsisik4g9p3603`, MD5 `c2efda0ee4cf9cf200e14910c5fc6996`.

## Required correction (now implemented and accepted)

The shared write protocol receives a fixed, server-owned execute-tool name from
every execute handler and rejects a mismatch before consuming the ticket or
sending HTTP. It discards terminal prepared request bodies, and the confirmation
store bounds expired pending bindings and consumed replay markers by their
expiry. Tests cover direct service rejection, a wrong executor in the same
module, a wrong executor across modules, and clock-driven lifecycle cleanup
while preserving live expiry/replay errors.

## Historical product scope (offline only)

Root registered eighteen ticketed write tools for account groups, accounts, and
daybook balance accounts under the Wave-5b freeze. Runtime is **142** `api_*`
tools. Coverage reports implemented/contract_tested **118**, live **0**, vision
**0**, `complete: false`. Bulk rows, postings and account-natures writes,
specials, UI, and live greens were not falsely advanced.

## What remains red

- Live qualification for the nine Wave-5b rows
- Remaining clear singular write rows (including Wave-5c daybook transaction and
  line CUD until implemented)
- **92** ambiguous bulk rows (empty tools)
- Four specials still red; UI 339 all red; vision 0
- Unauthenticated DELETE empty 200 is not cleanup proof
- Unauthenticated natures/postings CUD still **405** despite some docs Supports
  flags

## Next product gate

With the repair ACCEPT recorded, promote the Wave-5c research brief to a shared
wiki freeze, then implement daybook transaction and line ticketed writes under
the same executor-binding protocol. Do not green live/UI/bulk from that work
without their own evidence.
