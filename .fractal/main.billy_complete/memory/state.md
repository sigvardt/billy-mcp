---
name: state
desc: Current node state, verified review decisions, and open qualification work.
tags: [billy, coverage, review]
sources:
  - docs/superpowers/specs/2026-07-28-billy-mcp-complete-design.md
  - https://www.billy.dk/api/
created: 2026-07-29T12:12:38Z
updated: 2026-07-29T18:52:00Z
---

# state

## Current state

- Wave-5c parent and line write modules are merged into root; root registration uses the one shared `ConfirmationStore` and `WriteProtocolService`.
- Runtime: **154** `api_*` + 2 coverage; 30 preview + 30 execute ticketed write tools.
- Coverage: implemented 124, contract_tested 124, live 0, vision 0, `complete: false`.
- Official docs fingerprint still etag `hsisik4g9p3603`, MD5 `c2efda0ee4cf9cf200e14910c5fc6996`.
- Wave-5a registration product: **ACCEPT** offline.
- Wave-5b freeze: **ACCEPT**. Wave-5b product at `920ceab`: **REJECTED**. Repair product at `a2a0996`: **ACCEPT**.
- Wave-5c freeze: **ACCEPT**. Wave-5c product at tip `f235ac2`: **ACCEPT** offline by independent Grok.
- Wave-5d freeze at tip `5c376de`: **ACCEPT** offline contract only (`wiki/wave_fived_ticketed_writes_contract.md`; durable review `wiki/wave_fived_freeze_independent_review.md`).
- Wave-5d product tools not on root yet. Leaves `wave5d_invoice_writes` and `wave5d_invoice_line_writes` are implementation work; product needs separate Grok review after root integration.
- UI all red; bulk 92 empty-tool red; four specials red; **85** clear singular writes remain red; no live token.

## Review decisions (authoritative)

- Wave-5a integrated product: **ACCEPT** offline.
- Wave-5b freeze: **ACCEPT**.
- Wave-5b product at `920ceab`: **REJECTED**.
- Wave-5b repair at `a2a0996`: **ACCEPT** offline.
- Wave-5c freeze: **ACCEPT** offline contract only.
- Wave-5c product at tip `f235ac2`: **ACCEPT** offline by independent Grok audit.
- Wave-5d freeze at tip `5c376de`: **ACCEPT** offline contract only.
- Wave-5d product: **not accepted** until integrated and re-reviewed.
- Overall completeness: **FAIL** until live, bulk, remaining writes, specials, UI/vision close red rows.

## Open coverage work

1. Merge Wave-5d invoice and invoice-line leaves; root registration to 166 `api_*`; coverage 130 offline.
2. Independent Grok product review of integrated Wave-5d before Wave-5e (bills).
3. Remaining clear writes, specials, bulk (live only), UI/auth/vision, and live qualification.

## Evidence boundaries

- Official API fingerprint: etag `hsisik4g9p3603`, MD5 `c2efda0ee4cf9cf200e14910c5fc6996`.
- Unauth invoices / invoiceLines: POST/PUT 401, DELETE empty 200, GET-id 404.
- Unauth DELETE empty 200 is not cleanup proof.
- Line writes must declare `additional_plural_roots=("invoices",)`.
- Freeze ACCEPT is offline contract only; no product/live/UI/bulk/completeness claim.

## References

- Research (scratch): `.fractal/main.billy_complete/tmp/grok-research.md`
- Review (scratch): `.fractal/main.billy_complete/tmp/grok-review.md`
- Wiki freeze: `wiki/wave_fived_ticketed_writes_contract.md`
- Wiki freeze ACCEPT: `wiki/wave_fived_freeze_independent_review.md`
- Wave-5c Grok product ACCEPT: `wiki/wave_fivec_product_independent_review.md`
- Freeze 5c: `wiki/wave_fivec_ticketed_writes_contract.md`
