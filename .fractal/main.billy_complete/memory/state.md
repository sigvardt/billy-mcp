---
name: state
desc: Current node state, verified review decisions, and open qualification work.
tags: [billy, coverage, review]
sources:
  - docs/superpowers/specs/2026-07-28-billy-mcp-complete-design.md
  - https://www.billy.dk/api/
created: 2026-07-29T12:12:38Z
updated: 2026-07-29T17:20:00Z
---

# state

## Current state

- Root HEAD `a2a0996`: Wave-5a + Wave-5b writes with P1/P2 repair.
- Runtime: **142** `api_*` + 2 coverage; shared ConfirmationStore + WriteProtocolService; 24 preview + 24 execute writes.
- Coverage: implemented 118, contract_tested 118, live 0, vision 0, `complete: false`.
- Official docs fingerprint still etag `hsisik4g9p3603`, MD5 `c2efda0ee4cf9cf200e14910c5fc6996`.
- Wave-5a registration product: **ACCEPT** offline.
- Wave-5b freeze: **ACCEPT**. Wave-5b product at `920ceab`: **REJECTED**. Repair product at `a2a0996`: **ACCEPT** (independent Grok re-review).
- Wave-5c research brief ready; next is shared wiki freeze, then 12 ticketed tools with P1 binding tests.
- UI all red; bulk 92 empty-tool red; four specials red; **94** clear singular writes still red (including 6 Wave-5c); no live token.

## Review decisions (authoritative)

- Wave-5a integrated product: **ACCEPT** offline.
- Wave-5b freeze: **ACCEPT**.
- Wave-5b product at `920ceab`: **REJECTED** (cross-executor ticket use; unbounded terminal retention).
- Wave-5b repair at `a2a0996`: **ACCEPT** offline. P1/P2 closed with focused **109** passing tests; 24/24 execute handlers bind `execute_tool_name`.
- Durable ACCEPT: `wiki/wave_fiveb_repair_independent_review.md`.
- Wave-5c remains research-only until wiki freeze + implementation; no greening from research.
- Overall completeness: **FAIL** until live, bulk, remaining writes, specials, UI/vision close red rows.

## Next work

1. Promote Wave-5c research to wiki freeze; Codex Power implements 12 daybook-transaction tools with P1 binding tests; independent product review.
2. Remaining clear writes (invoices/bills first), specials, bulk (live only), UI/auth/vision, live qualification.

## Evidence boundaries

- Official API fingerprint: etag `hsisik4g9p3603`, MD5 `c2efda0ee4cf9cf200e14910c5fc6996`.
- Repair review focused suite: **109** passed.
- Unauth DELETE empty 200 is not cleanup proof.
- Unauth natures/postings 405 is not a green reclassification by itself.

## References

- Review (scratch): `.fractal/main.billy_complete/tmp/grok-review.md`
- Wiki repair ACCEPT: `wiki/wave_fiveb_repair_independent_review.md`
- Wiki product history: `wiki/wave_fiveb_product_independent_review.md`
- Freeze 5b: `wiki/wave_fiveb_ticketed_writes_contract.md`
- Research 5c: `.fractal/main.billy_complete/tmp/grok-research.md`
