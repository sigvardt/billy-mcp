---
name: state
desc: Current node state, verified review decisions, and open qualification work.
tags: [billy, coverage, review]
sources:
  - docs/superpowers/specs/2026-07-28-billy-mcp-complete-design.md
  - https://www.billy.dk/api/
created: 2026-07-29T22:11:45Z
updated: 2026-07-30T02:40:00Z
---

# state

## Current state

- Wave-5c through Wave-5i write modules are merged into root; root registration uses the one shared `ConfirmationStore` and `WriteProtocolService`.
- Root has Wave-5i product: **220** `api_*` tools; offline coverage **157**. Product review **ACCEPT** at `wiki/wave_fivei_product_independent_review.md`.
- Wave-5j freeze page is merged at root merge **`0db66d0`** (`wiki/wave_fivej_ticketed_writes_contract.md`). Independent freeze review **ACCEPT** at `wiki/wave_fivej_freeze_independent_review.md`.
- Wave-5j product-ready research is independently **ACCEPT**ed at `wiki/wave_fivej_product_ready_research_independent_review.md`.
- Wave-5j product is **not** on root (`bank_line_writes.py` absent). Recovery leaf `wave5j_bank_line_product_recovery` is active and has uncommitted `bank_line_writes.py` plus tests in its worktree.
- Wave-5k freeze-ready research (research44) is independently **ACCEPT**ed at `wiki/wave_fivek_freeze_ready_research_independent_review.md`.
- Wave-5k freeze-implementation research (research45) is recorded at `.fractal/main.billy_complete/tmp/grok-research.md` (full property table, freeze table §5.1, reconfirmed probes). Freeze page not authored.
- Coverage: implemented 157, contract_tested 157, live 0, vision 0, `complete: false`. Clear red CUD: 52.
- UI all red; bulk 92 empty-tool red; no live token; no UI credentials.

## Verification

- Official docs reconfirmed research45: ETag `hsisik4g9p3603`, MD5 `c2efda0ee4cf9cf200e14910c5fc6996`, 147934 bytes (byte-identical to research44).
- Unauth probes reconfirmed: bankPayments POST/PUT **401**; DELETE **405** `METHOD_NOT_ALLOWED` with message “Resource at `bankPayments` does not support deleting a single record.”
- No coverage greens from research. No full-mode claim.

## Review decisions (authoritative)

- Wave-5g product: **ACCEPT** offline.
- Wave-5h freeze / product: **ACCEPT** offline.
- Wave-5i freeze / product: **ACCEPT** offline.
- Wave-5j freeze-ready research: **ACCEPT** offline handoff only.
- Wave-5j freeze-implementation research: **ACCEPT** offline handoff only.
- Wave-5j freeze contract at merge `0db66d0`: **ACCEPT** offline contract.
- Wave-5j product-ready research: **ACCEPT** offline handoff only.
- Wave-5j product: **not present / not accepted**.
- Wave-5k freeze-ready research (research44): **ACCEPT** offline freeze-drafting handoff only (`wiki/wave_fivek_freeze_ready_research_independent_review.md`).
- Wave-5k freeze-implementation research (research45): **cited handoff written**; independent review of this pass not yet recorded.
- Wave-5k freeze / product: **not authored**.
- Overall completeness: **FAIL**.

## Open coverage work

1. Finish/merge Wave-5j bank-line product (nine CUD → 238 tools / 166 offline) and independent Grok product review.
2. After 5j product ACCEPT: author Wave-5k freeze page from research45 §5.1 + research44 ACCEPT, freeze review, then product (create+update only → 242 / 168 offline; delete stays red on 405).
3. Later freezes: salesTaxPayments / contactBalancePayments / invoiceLateFees create+update; invoiceReminders create; salesTaxReturns update; users update; orgs with risk gate; transactions only after readonly resolution.
4. Blocked offline (405 / readonly): accountNatures, postings, balanceModifiers, contactBalancePostings, geo CUD, bankPayments/salesTaxPayments/contactBalancePayments delete, invoiceReminderAssociations create/update, files JSON as binary special.
5. Bulk 92, UI/auth/vision, live CUD still open.

## Evidence boundaries

- Official API fingerprint: etag `hsisik4g9p3603`, MD5 `c2efda0ee4cf9cf200e14910c5fc6996`.
- bankPayments singular DELETE remains **405** and overrides Supports delete for offline tools.
- Inventory still carries `tool_name` for delete; freeze must not register delete tools.
- Inventory create cleanup text still says delete; live path must void via `isVoided` (irreversible).
- No coverage green from research or freeze-ready review.

## References

- Wave-5j freeze ACCEPT: `wiki/wave_fivej_freeze_independent_review.md`
- Wave-5j freeze contract: `wiki/wave_fivej_ticketed_writes_contract.md`
- Wave-5j product-ready research ACCEPT: `wiki/wave_fivej_product_ready_research_independent_review.md`
- Wave-5k freeze-ready research ACCEPT: `wiki/wave_fivek_freeze_ready_research_independent_review.md`
- Research scratch: `.fractal/main.billy_complete/tmp/grok-research.md`
- Offline probe rules: `wiki/offline_write_probe_rules.md`
