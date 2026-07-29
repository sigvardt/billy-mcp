---
name: wave_fivec_freeze_independent_review
desc: Independent Grok ACCEPT of the Wave-5c offline ticketed-write contract freeze; product not yet on root.
tags: [billy, review, writes, coverage]
sources:
  - https://www.billy.dk/api/
  - wiki/wave_fivec_ticketed_writes_contract.md
  - coverage/status.json
  - docs/superpowers/specs/2026-07-28-billy-mcp-complete-design.md
created: 2026-07-29T17:45:00Z
updated: 2026-07-29T17:45:00Z
---

# wave_fivec_freeze_independent_review

## Verdict

| Claim | Result |
| --- | --- |
| Wave-5c cited contract freeze | **ACCEPT** |
| Wave-5c product implementation | **not on root** (separate review after merge) |
| Wave-5b offline product (recheck) | **ACCEPT** |
| Overall product completeness | **FAIL** (expected) |
| Coverage honesty / fail-closed bulk-UI-live | **PASS** |

Root HEAD at review: `ab199e2`. Official docs fingerprint unchanged: ETag
`hsisik4g9p3603`, MD5 `c2efda0ee4cf9cf200e14910c5fc6996`, 147934 bytes.

## What was accepted

`wiki/wave_fivec_ticketed_writes_contract.md` freezes exactly six clear singular
CUD inventory rows (`daybookTransactions` and `daybookTransactionLines`
create/update/delete) for offline ticketed preview/execute tools. Paths,
singular roots, inventory preview tool names, shared protocol reuse with
required `execute_tool_name`, P1 mismatch behaviour, opaque singular payloads,
and exclusions (bulk, postings/natures 405, ledger transactions, invoices,
specials, UI, live green) match current official documentation and the
maintained inventory.

## What remains red

- All six Wave-5c rows: discovered only; not implemented or contract-tested.
- Runtime still **142** `api_*` tools (no Wave-5c write tools registered).
- Coverage still implemented/contract_tested **118**, live **0**, vision **0**,
  `complete: false`.
- Bulk 92 empty-tool; four specials red; remaining clear CUD red.
- Unauthenticated DELETE 200 is not cleanup proof. Unauthenticated natures and
  postings CUD return 405 despite some documentation Supports flags.

## Next product gate

After Codex Power leaves land and the root registers the twelve tools and
regenerates coverage to **124** offline rows with **154** `api_*` tools, run a
separate independent product review before expanding scope (Wave-5d invoices
and bills).

Full scratch report: node `tmp/grok-review.md` (not durable; this wiki page is
the shared summary).
