---
name: state
desc: Current node state, verified review decisions, and open qualification work.
tags: [billy, coverage, review]
sources:
  - docs/superpowers/specs/2026-07-28-billy-mcp-complete-design.md
  - https://www.billy.dk/api/
created: 2026-07-29T22:11:45Z
updated: 2026-07-29T23:50:00Z
---

# state

## Current state

- Wave-5c through Wave-5g write modules are merged into root; root registration uses the one shared `ConfirmationStore` and `WriteProtocolService`.
- Root merge **`55faa02`** integrates Wave-5g product: **202** `api_*` tools; offline product **ACCEPT** at `wiki/wave_fiveg_product_independent_review.md`.
- Wave-5g freeze remains **`5612aa8`** (`wiki/wave_fiveg_ticketed_writes_contract.md`).
- Wave-5h freeze page merged at **`c14266e`**. Root Grok independent freeze review **ACCEPT** at `wiki/wave_fiveh_freeze_independent_review.md`. Contract at `wiki/wave_fiveh_ticketed_writes_contract.md`.
- Wave-5h product-ready research **ACCEPT** at `wiki/wave_fiveh_product_ready_research_independent_review.md`.
- Wave-5h product-implementation research **ACCEPT** at `wiki/wave_fiveh_product_implementation_research_independent_review.md`.
- Wave-5h product: active Codex child `wave5h_attachment_product` owns offline attachment JSON CUD. Child worktree already has `attachment_writes.py`; root still lacks the module. Registry still **202**. Root integration needs a clean child result, then separate Grok product review.
- Research37: Wave-5i freeze-ready for `salesTaxAccounts` + `salesTaxMetaFields` singular CUD. Docs fingerprint re-verified unchanged (etag `hsisik4g9p3603`, MD5 `c2efda0ee4cf9cf200e14910c5fc6996`). Unauth POST/PUT 401; DELETE missing-id 200 on both resources. Full cited brief: `tmp/grok-research.md`. Freeze page and product still absent.
- Coverage: implemented 148, contract_tested 148, live 0, vision 0, `complete: false`. Clear red CUD: 61.
- UI all red; bulk 92 empty-tool red; specials red; no live token.

## Review decisions (authoritative)

- Wave-5g product at root merge `55faa02`: **ACCEPT** offline.
- Wave-5h freeze-ready research: **ACCEPT** offline handoff only.
- Wave-5h freeze at merge `c14266e`: **ACCEPT** offline contract.
- Wave-5h product-ready research: **ACCEPT** offline handoff only.
- Wave-5h product-implementation research: **ACCEPT** offline handoff only; does not green coverage or accept product.
- Wave-5h product: **not implemented on root / not accepted**.
- Wave-5i freeze-ready research (research37): **drafted; pending independent review**.
- Overall completeness: **FAIL**.

## Open coverage work

1. Codex Power Wave-5h product (child): `attachment_writes` six tools → registry 208, coverage 151 after real suites; independent Grok product review after merge.
2. Independent review of Wave-5i freeze-ready research; then Codex freeze page `wiki/wave_fivei_ticketed_writes_contract.md`.
3. After freeze ACCEPT: product-ready research, then Wave-5i product (+12 → 220; coverage 157).
4. Later: bank line family CUD, partial CUD cohorts, specials (binary files upload), bulk live, UI/auth/vision.
5. Blocked offline (405 / readonly): accountNatures, postings, balanceModifiers, contactBalancePostings, geo CUD, bankPayments/salesTaxPayments delete, transactions CUD, invoiceReminderAssociations create/update.

## Evidence boundaries

- Official API fingerprint: etag `hsisik4g9p3603`, MD5 `c2efda0ee4cf9cf200e14910c5fc6996`.
- Unauth DELETE 200 is not cleanup proof.
- Unauth POST `/files` JSON object may 401; invalid JSON body may 400 `INVALID_REQUEST_BODY`; neither is a JSON create contract.
- Product ACCEPT requires real offline suites; no green from research/freeze alone.
- salesTaxAccounts: `type` enum values unpublished; `account` not marked immutable.
- salesTaxMetaFields: `isPredefined` not marked readonly (unlike rulesets); keep opaque.

## References

- Research freeze-ready 5i (scratch): `.fractal/main.billy_complete/tmp/grok-research.md`
- Wiki freeze ACCEPT 5h: `wiki/wave_fiveh_freeze_independent_review.md`
- Wiki product-ready ACCEPT 5h: `wiki/wave_fiveh_product_ready_research_independent_review.md`
- Wiki freeze contract 5h: `wiki/wave_fiveh_ticketed_writes_contract.md`
- Wiki product ACCEPT 5g: `wiki/wave_fiveg_product_independent_review.md`
- Offline probe rules: `wiki/offline_write_probe_rules.md`
