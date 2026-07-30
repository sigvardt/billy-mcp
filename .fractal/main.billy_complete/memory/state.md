---
name: state
desc: Current node state, verified review decisions, and open qualification work.
tags: [billy, coverage, review]
sources:
  - docs/superpowers/specs/2026-07-28-billy-mcp-complete-design.md
  - https://www.billy.dk/api/
created: 2026-07-29T22:11:45Z
updated: 2026-07-30T01:20:00Z
---

# state

## Current state

- Wave-5c through Wave-5i write modules are merged into root; root registration uses the one shared `ConfirmationStore` and `WriteProtocolService`.
- Root merge **`084ad77`** integrates Wave-5i product (leaf **`7784901`**): **220** `api_*` tools; offline coverage **157**. Independent product review **ACCEPT** at `wiki/wave_fivei_product_independent_review.md`.
- Wave-5i freeze remains accepted (`wiki/wave_fivei_ticketed_writes_contract.md`, `wiki/wave_fivei_freeze_independent_review.md`).
- Wave-5h product remains accepted at **`29cecbe`** (`wiki/wave_fiveh_product_independent_review.md`).
- Wave-5g product remains accepted at **`55faa02`** (`wiki/wave_fiveg_product_independent_review.md`).
- Wave-5j freeze-ready research (research40) **ACCEPT** as handoff only at `wiki/wave_fivej_freeze_ready_research_independent_review.md`.
- Wave-5j freeze-implementation research (research41) is current at `.fractal/main.billy_complete/tmp/grok-research.md`. Freeze page and product not authored.
- Coverage: implemented 157, contract_tested 157, live 0, vision 0, `complete: false`. Clear red CUD: 52.
- UI all red; bulk 92 empty-tool red; specials mostly red; no live token.
- Child review nodes that exit without durable ACCEPT do not replace root reviews.

## Verification

- Official docs re-fetched research41: ETag `hsisik4g9p3603`, MD5 `c2efda0ee4cf9cf200e14910c5fc6996`, 147934 bytes (unchanged).
- Unauth probes research41: bankLineMatches/bankLines/bankLineSubjectAssociations POST/PUT 401, DELETE missing-id 200; bankPayments DELETE 405; balanceModifiers POST 405.
- No full-mode claim: `coverage/status.json` remains `complete: false` with live and vision counts at zero.

## Review decisions (authoritative)

- Wave-5g product at root merge `55faa02`: **ACCEPT** offline.
- Wave-5h freeze: **ACCEPT** offline contract.
- Wave-5h product at root merge `29cecbe`: **ACCEPT** offline.
- Wave-5i freeze-ready research: **ACCEPT** offline handoff only.
- Wave-5i freeze page at commit `a176887`: **ACCEPT** offline contract.
- Wave-5i product-ready research (research39): **ACCEPT** offline handoff only.
- Wave-5i product at root merge `084ad77`: **ACCEPT** offline (`wiki/wave_fivei_product_independent_review.md`).
- Wave-5j freeze-ready research (research40): **ACCEPT** offline handoff only (`wiki/wave_fivej_freeze_ready_research_independent_review.md`).
- Wave-5j freeze / product: **not present / not accepted**.
- Overall completeness: **FAIL**.

## Open coverage work

1. Author Wave-5j freeze page for bank line family CUD (9 clear ops) from research41, independent freeze review, then product.
2. Later: bankPayments create/update (delete 405 blocked), partial CUD cohorts, specials (binary files upload), bulk live, UI/auth/vision, live CUD.
3. Blocked offline (405 / readonly): accountNatures, postings, balanceModifiers, contactBalancePostings, geo CUD, bankPayments/salesTaxPayments delete, transactions CUD, invoiceReminderAssociations create/update.

## Evidence boundaries

- Official API fingerprint: etag `hsisik4g9p3603`, MD5 `c2efda0ee4cf9cf200e14910c5fc6996` (reconfirmed research41).
- Unauth DELETE 200 is not cleanup proof.
- Product ACCEPT is offline contract suites only; no live_tested greens.
- bankLineMatches embed `lines`/`subjectAssociations`: replace-on-set description vs Notes readonly — live must prove.
- bankPayments singular DELETE remains **405**.

## References

- Review (scratch): `.fractal/main.billy_complete/tmp/grok-review.md`
- Research 5j freeze-impl (scratch): `.fractal/main.billy_complete/tmp/grok-research.md`
- Wiki product ACCEPT 5i: `wiki/wave_fivei_product_independent_review.md`
- Wiki research ACCEPT 5j: `wiki/wave_fivej_freeze_ready_research_independent_review.md`
- Wiki freeze ACCEPT 5i: `wiki/wave_fivei_freeze_independent_review.md`
- Wiki freeze contract 5i: `wiki/wave_fivei_ticketed_writes_contract.md`
- Offline probe rules: `wiki/offline_write_probe_rules.md`
