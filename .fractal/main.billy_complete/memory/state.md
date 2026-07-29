---
name: state
desc: Current node state, verified review decisions, and open qualification work.
tags: [billy, coverage, review]
sources:
  - docs/superpowers/specs/2026-07-28-billy-mcp-complete-design.md
  - https://www.billy.dk/api/
created: 2026-07-29T19:15:42Z
updated: 2026-07-29T19:15:42Z
---

# state

## Current state

- Wave-5c and Wave-5d parent/line write modules are merged into root; root registration uses the one shared `ConfirmationStore` and `WriteProtocolService`.
- Runtime: **166** `api_*` + 2 coverage; 36 preview + 36 execute ticketed write tools.
- Coverage: implemented 130, contract_tested 130, live 0, vision 0, `complete: false`.
- Official docs fingerprint still etag `hsisik4g9p3603`, MD5 `c2efda0ee4cf9cf200e14910c5fc6996` (reconfirmed research pass; body 147934 bytes; identical to prior snapshot).
- Wave-5a registration product: **ACCEPT** offline.
- Wave-5b freeze: **ACCEPT**. Wave-5b product at `920ceab`: **REJECTED**. Repair product at `a2a0996`: **ACCEPT**.
- Wave-5c freeze: **ACCEPT**. Wave-5c product at tip `f235ac2`: **ACCEPT** offline by independent Grok.
- Wave-5d freeze at tip `5c376de`: **ACCEPT** offline contract only (`wiki/wave_fived_ticketed_writes_contract.md`; durable review `wiki/wave_fived_freeze_independent_review.md`).
- Wave-5d invoice and invoice-line tools are integrated and tested offline; the required Grok product review is pending.
- Wave-5e (bills + billLines) research brief is ready at scratch `tmp/grok-research.md`. **Product gate CLOSED** until Wave-5d product ACCEPT. Wiki freeze for 5e not created yet.
- UI all red; bulk 92 empty-tool red; four specials red; **79** clear singular writes remain red; no live token in process env.

## Review decisions (authoritative)

- Wave-5a integrated product: **ACCEPT** offline.
- Wave-5b freeze: **ACCEPT**.
- Wave-5b product at `920ceab`: **REJECTED**.
- Wave-5b repair at `a2a0996`: **ACCEPT** offline.
- Wave-5c freeze: **ACCEPT** offline contract only.
- Wave-5c product at tip `f235ac2`: **ACCEPT** offline by independent Grok audit.
- Wave-5d freeze at tip `5c376de`: **ACCEPT** offline contract only.
- Wave-5d product: **integrated, not accepted** until a fresh Grok review accepts it.
- Wave-5e product: **not authorised** until Wave-5d product ACCEPT.
- Overall completeness: **FAIL** until live, bulk, remaining writes, specials, UI/vision close red rows.

## Open coverage work

1. Independent Grok product review of integrated Wave-5d before Wave-5e (bills).
2. On Wave-5d ACCEPT: promote `tmp/grok-research.md` to `wiki/wave_fivee_ticketed_writes_contract.md` and implement bills + billLines (6 clear CUD → 12 tools; target 178 `api_*`, 136 offline rows).
3. Remaining clear writes, specials, bulk (live only), UI/auth/vision, and live qualification.

## Evidence boundaries

- Official API fingerprint: etag `hsisik4g9p3603`, MD5 `c2efda0ee4cf9cf200e14910c5fc6996`.
- Unauth bills / billLines: POST/PUT 401 `AUTHENTICATION_REQUIRED`, DELETE empty 200, GET-id 404 `RECORD_NOT_FOUND` (probe set research24).
- Unauth DELETE empty 200 is not cleanup proof.
- Invoice-line writes declare `additional_plural_roots=("invoices",)` and map the parent root only when present.
- Bill line writes must declare `additional_plural_roots=("bills",)` (optional parent root when absent).
- Bill lines fields: account/taxRate/description/amount (not product/unitPrice).
- Postings Supports lists CUD but unauth HTTP is 405; keep out of Wave-5e.
- Freeze ACCEPT is offline contract only; no product/live/UI/bulk/completeness claim.

## References

- Research (scratch): `.fractal/main.billy_complete/tmp/grok-research.md`
- Review (scratch): `.fractal/main.billy_complete/tmp/grok-review.md`
- Wiki freeze 5d: `wiki/wave_fived_ticketed_writes_contract.md`
- Wiki freeze ACCEPT 5d: `wiki/wave_fived_freeze_independent_review.md`
- Wave-5c Grok product ACCEPT: `wiki/wave_fivec_product_independent_review.md`
- Freeze 5c: `wiki/wave_fivec_ticketed_writes_contract.md`
