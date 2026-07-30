---
name: state
desc: Current node state, verified review decisions, and open qualification work.
tags: [billy, coverage, review]
sources:
  - docs/superpowers/specs/2026-07-28-billy-mcp-complete-design.md
  - https://www.billy.dk/api/
created: 2026-07-29T22:11:45Z
updated: 2026-07-30T00:53:00Z
---

# state

## Current state

- Wave-5c through Wave-5h write modules are merged into root; root registration uses the one shared `ConfirmationStore` and `WriteProtocolService`.
- Root merge **`29cecbe`** integrates Wave-5h attachment product: **208** `api_*` tools; offline product **ACCEPT** at `wiki/wave_fiveh_product_independent_review.md`.
- Wave-5h freeze remains accepted (`wiki/wave_fiveh_ticketed_writes_contract.md`, `wiki/wave_fiveh_freeze_independent_review.md`).
- Wave-5g product remains accepted at **`55faa02`** (`wiki/wave_fiveg_product_independent_review.md`).
- Wave-5i freeze-ready ACCEPT stands at `wiki/wave_fivei_freeze_ready_research_independent_review.md`.
- Wave-5i freeze page landed at commit **`a176887`** (`wiki/wave_fivei_ticketed_writes_contract.md`).
- Root independent freeze review **ACCEPT** at `wiki/wave_fivei_freeze_independent_review.md`.
- Wave-5i product-ready research (research39) ACCEPT at `wiki/wave_fivei_product_ready_research_independent_review.md`.
- Root merge **`084ad77`** integrates the Wave-5i product candidate from `7784901`: twelve sales-tax account/meta-field tools, offline coverage **157**, and registry assert **220**. The independent Grok product review remains required before acceptance.
- Wave-5j freeze-ready research (research40) stands at `.fractal/main.billy_complete/tmp/grok-research.md` for nine bank-line singular CUD ops. Not yet independently reviewed; freeze page not authored.
- Coverage: implemented 157, contract_tested 157, live 0, vision 0, `complete: false`. Clear red CUD: 52.
- UI all red; bulk 92 empty-tool red; specials red; no live token.
- Child freeze/product review nodes that exit without durable ACCEPT do not replace root reviews.

## Review decisions (authoritative)

- Wave-5g product at root merge `55faa02`: **ACCEPT** offline.
- Wave-5h freeze: **ACCEPT** offline contract.
- Wave-5h product at root merge `29cecbe`: **ACCEPT** offline.
- Wave-5i freeze-ready research: **ACCEPT** offline handoff only.
- Wave-5i freeze page at commit `a176887`: **ACCEPT** offline contract.
- Wave-5i product-ready research (research39): **ACCEPT** offline handoff only (`wiki/wave_fivei_product_ready_research_independent_review.md`).
- Wave-5i product: **integrated / not independently accepted** on root.
- Wave-5j freeze-ready research (research40): **draft only** — needs independent research review before freeze page.
- Overall completeness: **FAIL**.

## Open coverage work

1. Independent product review of the integrated Wave-5i candidate (220 tools / 157 offline rows).
2. Independent review of Wave-5j freeze-ready research40, then freeze page for bank line family CUD (9 clear ops → later 18 tools / +9 rows).
3. Later: bankPayments create/update (delete 405 blocked), partial CUD cohorts, specials (binary files upload), bulk live, UI/auth/vision, live attachment CUD.
4. Blocked offline (405 / readonly): accountNatures, postings, balanceModifiers, contactBalancePostings, geo CUD, bankPayments/salesTaxPayments delete, transactions CUD, invoiceReminderAssociations create/update.

## Evidence boundaries

- Official API fingerprint: etag `hsisik4g9p3603`, MD5 `c2efda0ee4cf9cf200e14910c5fc6996` (reconfirmed research40).
- Unauth DELETE 200 is not cleanup proof.
- Unauth POST `/files` invalid JSON → 400 `INVALID_REQUEST_BODY`; not a JSON create contract.
- Product ACCEPT requires real offline suites; no green from research/freeze alone.
- salesTaxAccounts: `type` enum values unpublished; `account` not marked immutable.
- salesTaxMetaFields: `isPredefined` not marked readonly (unlike rulesets); keep opaque.
- bankLineMatches: `lines` / `subjectAssociations` have replace-on-set description but Notes `readonly` — live must prove embed; offline keeps arrays opaque inside payload.
- bankLines/bankLineMatches `side` and `differenceType` enums unpublished offline — opaque; do not borrow bankPayments `cashSide` debit/credit as bank-line values.
- bankPayments singular DELETE remains **405** despite Supports listing delete.

## References

- Research freeze-ready 5j (scratch): `.fractal/main.billy_complete/tmp/grok-research.md`
- Probes 5j (scratch): `.fractal/main.billy_complete/tmp/write-probes-research40.json`
- Wiki product-ready ACCEPT 5i: `wiki/wave_fivei_product_ready_research_independent_review.md`
- Wiki freeze ACCEPT 5i: `wiki/wave_fivei_freeze_independent_review.md`
- Wiki freeze contract 5i: `wiki/wave_fivei_ticketed_writes_contract.md`
- Wiki freeze-ready ACCEPT 5i: `wiki/wave_fivei_freeze_ready_research_independent_review.md`
- Wiki product ACCEPT 5h: `wiki/wave_fiveh_product_independent_review.md`
- Offline probe rules: `wiki/offline_write_probe_rules.md`
