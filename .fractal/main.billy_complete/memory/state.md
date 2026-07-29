---
name: state
desc: Current node state, verified review decisions, and open qualification work.
tags: [billy, coverage, review]
sources:
  - docs/superpowers/specs/2026-07-28-billy-mcp-complete-design.md
  - https://www.billy.dk/api/
created: 2026-07-29T12:12:38Z
updated: 2026-07-29T19:20:00Z
---

# state

## Current state

- Wave-5c and Wave-5d parent/line write modules are merged into root; root registration uses the one shared `ConfirmationStore` and `WriteProtocolService`.
- Runtime: **166** `api_*` + 2 coverage; 36 preview + 36 execute ticketed write tools.
- Coverage: implemented 130, contract_tested 130, live 0, vision 0, `complete: false`.
- Official docs fingerprint still etag `hsisik4g9p3603`, MD5 `c2efda0ee4cf9cf200e14910c5fc6996` (body 147934 bytes).
- Wave-5a registration product: **ACCEPT** offline.
- Wave-5b freeze: **ACCEPT**. Wave-5b product at `920ceab`: **REJECTED**. Repair product at `a2a0996`: **ACCEPT**.
- Wave-5c freeze: **ACCEPT**. Wave-5c product at tip `f235ac2`: **ACCEPT** offline by independent Grok.
- Wave-5d freeze at tip `5c376de`: **ACCEPT** offline contract only.
- Wave-5d product at tip **`1108e2f`**: **ACCEPT** offline by independent Grok (`wiki/wave_fived_product_independent_review.md`; full note `tmp/grok-review.md`).
- Reproduced the product review verification locally: focused ticket/registry/coverage suite **110 passed** and the non-live repository suite **753 passed**.
- Wave-5e (bills + billLines) research brief ready at `tmp/grok-research.md`. **Product gate OPEN for freeze promotion** after this product ACCEPT; implement only after Wave-5e freeze ACCEPT.
- UI all red; bulk 92 empty-tool red; four specials red; **79** clear singular writes remain red; no live token in process env.

## Review decisions (authoritative)

- Wave-5a integrated product: **ACCEPT** offline.
- Wave-5b freeze: **ACCEPT**.
- Wave-5b product at `920ceab`: **REJECTED**.
- Wave-5b repair at `a2a0996`: **ACCEPT** offline.
- Wave-5c freeze: **ACCEPT** offline contract only.
- Wave-5c product at tip `f235ac2`: **ACCEPT** offline by independent Grok audit.
- Wave-5d freeze at tip `5c376de`: **ACCEPT** offline contract only.
- Wave-5d product at tip `1108e2f`: **ACCEPT** offline by independent Grok.
- Wave-5e product: **not accepted** until freeze + product review; freeze promotion now authorised.
- Overall completeness: **FAIL** until live, bulk, remaining writes, specials, UI/vision close red rows.

## Open coverage work

1. Promote Wave-5e research brief to `wiki/wave_fivee_ticketed_writes_contract.md`, freeze ACCEPT, implement bills + billLines (target 178 `api_*`, 136 offline rows).
2. Remaining clear writes, specials, bulk (live only), UI/auth/vision, and live qualification.

## Evidence boundaries

- Official API fingerprint: etag `hsisik4g9p3603`, MD5 `c2efda0ee4cf9cf200e14910c5fc6996`.
- Invoice-line writes declare `additional_plural_roots=("invoices",)` and map the parent root only when present.
- Bill line writes must declare `additional_plural_roots=("bills",)` (optional parent root when absent).
- Bill lines fields: account/taxRate/description/amount (not product/unitPrice).
- Unauth DELETE empty 200 is not cleanup proof.
- Product ACCEPT is offline only; no live/UI/bulk/completeness claim.

## References

- Research (scratch): `.fractal/main.billy_complete/tmp/grok-research.md`
- Review (scratch): `.fractal/main.billy_complete/tmp/grok-review.md`
- Wiki freeze 5d: `wiki/wave_fived_ticketed_writes_contract.md`
- Wiki freeze ACCEPT 5d: `wiki/wave_fived_freeze_independent_review.md`
- Wiki product ACCEPT 5d: `wiki/wave_fived_product_independent_review.md`
- Wave-5c Grok product ACCEPT: `wiki/wave_fivec_product_independent_review.md`
