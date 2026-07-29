---
name: state
desc: Current node state, verified review decisions, and open qualification work.
tags: [billy, coverage, review]
sources:
  - docs/superpowers/specs/2026-07-28-billy-mcp-complete-design.md
  - https://www.billy.dk/api/
created: 2026-07-29T22:11:45Z
updated: 2026-07-29T23:30:00Z
---

# state

## Current state

- Wave-5c through Wave-5g write modules are merged into root; root registration uses the one shared `ConfirmationStore` and `WriteProtocolService`.
- Root merge **`55faa02`** integrates Wave-5g product: **202** `api_*` tools; offline product **ACCEPT** at `wiki/wave_fiveg_product_independent_review.md`.
- Wave-5g freeze remains **`5612aa8`** (`wiki/wave_fiveg_ticketed_writes_contract.md`).
- Wave-5h freeze page merged at **`c14266e`**. Root Grok independent freeze review **ACCEPT** at `wiki/wave_fiveh_freeze_independent_review.md`. Contract at `wiki/wave_fiveh_ticketed_writes_contract.md`.
- Wave-5h product-ready research **ACCEPT** at `wiki/wave_fiveh_product_ready_research_independent_review.md`.
- Research36 (product-implementation handoff) re-fetched official docs: fingerprint **unchanged** (etag `hsisik4g9p3603`, MD5 `c2efda0ee4cf9cf200e14910c5fc6996`, 147934 bytes). Unauth probes reconfirm attachments POST/PUT **401**, DELETE missing-id **200** (not cleanup). Brief: `tmp/grok-research.md`.
- Product gate **open** for six ticketed attachment JSON CUD tools (registry **208**, coverage **151** after suites). **No product module yet** (`attachment_writes.py` absent).
- Current non-live verification passes: formatting, Ruff, Pyright, coverage and repository-policy checks, and **892** non-live tests (last recorded before this research pass).
- Coverage: implemented 148, contract_tested 148, live 0, vision 0, `complete: false`. Clear red CUD: 61.
- UI all red; bulk 92 empty-tool red; specials red; no live token.
- Child `wave5h_freeze_codex_fallback_review` completed a supplemental static
  PASS at `0f3a69a`; it confirms the freeze's internal consistency but is
  non-authoritative and does not open product, live, UI, vision, or coverage
  gates.

## Review decisions (authoritative)

- Wave-5g product at root merge `55faa02`: **ACCEPT** offline.
- Wave-5h freeze-ready research: **ACCEPT** offline handoff only.
- Wave-5h freeze at merge `c14266e`: **ACCEPT** offline contract.
- Wave-5h product-ready research (research35): **ACCEPT** offline handoff only.
- Research36 product-implementation brief: supersedes research35 operator state; **does not** green coverage or accept product.
- Wave-5h product: **not implemented / not accepted**.
- Overall completeness: **FAIL**.

## Open coverage work

1. Codex Power Wave-5h product: `attachment_writes` six tools → registry 208, coverage 151 after real suites; independent Grok product review.
2. Freeze Wave-5i salesTaxAccounts + salesTaxMetaFields CUD; product (+12 → 220; coverage 157).
3. Later: bank line family CUD, partial CUD cohorts, specials (binary files upload), bulk live, UI/auth/vision.
4. Blocked offline (405 / readonly): accountNatures, postings, balanceModifiers, contactBalancePostings, geo CUD, bankPayments/salesTaxPayments delete, transactions CUD, invoiceReminderAssociations create/update.

## Evidence boundaries

- Official API fingerprint: etag `hsisik4g9p3603`, MD5 `c2efda0ee4cf9cf200e14910c5fc6996`.
- Unauth DELETE 200 is not cleanup proof.
- Unauth POST `/files` JSON object may 401; invalid JSON body may 400; neither is a JSON create contract.
- Product ACCEPT requires real offline suites; no green from research/freeze alone.

## References

- Research product-implementation (scratch): `.fractal/main.billy_complete/tmp/grok-research.md`
- Review (scratch): `.fractal/main.billy_complete/tmp/grok-review.md`
- Wiki freeze ACCEPT 5h: `wiki/wave_fiveh_freeze_independent_review.md`
- Wiki product-ready ACCEPT 5h: `wiki/wave_fiveh_product_ready_research_independent_review.md`
- Wiki freeze contract 5h: `wiki/wave_fiveh_ticketed_writes_contract.md`
- Wiki product ACCEPT 5g: `wiki/wave_fiveg_product_independent_review.md`
