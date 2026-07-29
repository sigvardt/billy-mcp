---
name: state
desc: Current node state, verified review decisions, and open qualification work.
tags: [billy, coverage, review]
sources:
  - docs/superpowers/specs/2026-07-28-billy-mcp-complete-design.md
  - https://www.billy.dk/api/
created: 2026-07-29T12:12:38Z
updated: 2026-07-29T17:45:00Z
---

# state

## Current state

- Root HEAD under freeze review: `ab199e2` (Wave-5c contract freeze). Wave-5b product code remains `a2a0996`.
- Runtime: **142** `api_*` + 2 coverage; shared ConfirmationStore + WriteProtocolService; 24 preview + 24 execute writes.
- Coverage: implemented 118, contract_tested 118, live 0, vision 0, `complete: false`.
- Official docs fingerprint still etag `hsisik4g9p3603`, MD5 `c2efda0ee4cf9cf200e14910c5fc6996` (re-fetched; unchanged).
- Wave-5a registration product: **ACCEPT** offline.
- Wave-5b freeze: **ACCEPT**. Wave-5b product at `920ceab`: **REJECTED**. Repair product at `a2a0996`: **ACCEPT**.
- Wave-5c freeze: **ACCEPT** (`wiki/wave_fivec_ticketed_writes_contract.md`; durable review `wiki/wave_fivec_freeze_independent_review.md`).
- Wave-5c product: **not on root**. Active leaves: `wave5c_daybook_transaction_writes`, `wave5c_daybook_transaction_line_writes`.
- UI all red; bulk 92 empty-tool red; four specials red; **91** clear singular writes still red (including 6 Wave-5c); no live token.

## Review decisions (authoritative)

- Wave-5a integrated product: **ACCEPT** offline.
- Wave-5b freeze: **ACCEPT**.
- Wave-5b product at `920ceab`: **REJECTED**.
- Wave-5b repair at `a2a0996`: **ACCEPT** offline.
- Wave-5c freeze at `ab199e2`: **ACCEPT** offline contract only.
- Wave-5c product: pending leaf merge + separate independent product review.
- Overall completeness: **FAIL** until live, bulk, remaining writes, specials, UI/vision close red rows.

## Next work

1. Merge Wave-5c leaves when committed and green; root registration to 154 `api_*` and 124 offline rows; independent product review.
2. Remaining clear writes (invoices/bills first), specials, bulk (live only), UI/auth/vision, live qualification.

## Evidence boundaries

- Official API fingerprint: etag `hsisik4g9p3603`, MD5 `c2efda0ee4cf9cf200e14910c5fc6996`.
- Unauth daybookTransactions / daybookTransactionLines: POST/PUT 401, DELETE empty 200, GET-id 404.
- Unauth natures/postings CUD still 405; not a green reclassification by itself.
- Unauth DELETE empty 200 is not cleanup proof.
- Freeze ACCEPT does not green inventory rows.

## References

- Review (scratch): `.fractal/main.billy_complete/tmp/grok-review.md`
- Wiki freeze: `wiki/wave_fivec_ticketed_writes_contract.md`
- Wiki freeze ACCEPT: `wiki/wave_fivec_freeze_independent_review.md`
- Wiki repair ACCEPT: `wiki/wave_fiveb_repair_independent_review.md`
- Freeze 5b: `wiki/wave_fiveb_ticketed_writes_contract.md`
