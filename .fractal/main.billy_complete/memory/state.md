---
name: state
desc: Current node state, verified review decisions, and open qualification work.
tags: [billy, coverage, review]
sources:
  - docs/superpowers/specs/2026-07-28-billy-mcp-complete-design.md
  - https://www.billy.dk/api/
created: 2026-07-29T22:11:45Z
updated: 2026-07-30T02:07:00Z
---

# state

## Current state

- Wave-5c through Wave-5i write modules are merged into root; root registration uses the one shared `ConfirmationStore` and `WriteProtocolService`.
- Root has Wave-5i product: **220** `api_*` tools; offline coverage **157**. Product review **ACCEPT** at `wiki/wave_fivei_product_independent_review.md`.
- Wave-5j freeze page is merged at root merge **`0db66d0`** (`wiki/wave_fivej_ticketed_writes_contract.md`). Independent freeze review **ACCEPT** at `wiki/wave_fivej_freeze_independent_review.md`.
- The current Wave-5j product-ready research is independently **ACCEPT**ed at `wiki/wave_fivej_product_ready_research_independent_review.md`. Full findings: `.fractal/main.billy_complete/tmp/grok-review.md`.
- Product for Wave-5j is **not** authored (`bank_line_writes.py` absent). Offline product gate is open after freeze ACCEPT + product-ready research ACCEPT.
- Coverage: implemented 157, contract_tested 157, live 0, vision 0, `complete: false`. Clear red CUD: 52 (nine bank-line CUD remain red).
- UI all red; bulk 92 empty-tool red; no live token; no UI credentials.
- Child nodes that exit without durable deliverables do not replace root reviews.

## Verification

- Official docs reconfirmed: ETag `hsisik4g9p3603`, MD5 `c2efda0ee4cf9cf200e14910c5fc6996`, 147934 bytes; byte-identical to the cited product-ready handoff.
- Unauthenticated probes reconfirmed: bank-line POST 401, DELETE missing-id 200; bankPayments DELETE 405.
- Nine inventory CUD rows still `implemented: false` / `contract_tested: false` / `live_tested: false`.
- No full-mode claim.

## Review decisions (authoritative)

- Wave-5g product: **ACCEPT** offline.
- Wave-5h freeze / product: **ACCEPT** offline.
- Wave-5i freeze / product: **ACCEPT** offline.
- Wave-5j freeze-ready research: **ACCEPT** offline handoff only.
- Wave-5j freeze-implementation research: **ACCEPT** offline handoff only.
- Wave-5j freeze contract at merge `0db66d0`: **ACCEPT** offline contract (`wiki/wave_fivej_freeze_independent_review.md`).
- Wave-5j product-ready research: **ACCEPT** offline handoff only (`wiki/wave_fivej_product_ready_research_independent_review.md`).
- Wave-5j product: **not present / not accepted**.
- Overall completeness: **FAIL**.

## Open coverage work

1. Codex Power product leaf for nine bank-line CUD (target 238 tools / 166 offline) from the accepted freeze and product-ready handoff.
2. Independent Grok product review after product merge.
3. Later: bankPayments create/update (delete 405 blocked), other red CUD, bulk live, UI/auth/vision, live CUD.
4. Blocked offline (405 / readonly): accountNatures, postings, balanceModifiers, contactBalancePostings, geo CUD, bankPayments/salesTaxPayments delete, transactions CUD, invoiceReminderAssociations create/update.

## Evidence boundaries

- Official API fingerprint: etag `hsisik4g9p3603`, MD5 `c2efda0ee4cf9cf200e14910c5fc6996`.
- Unauth DELETE 200 is not cleanup proof.
- Freeze and product-ready ACCEPT are offline handoff/contract only; no live_tested greens.
- bankLineMatches embed `lines`/`subjectAssociations`: replace-on-set vs Notes readonly — live must prove.
- bankPayments singular DELETE remains **405**.

## References

- Freeze ACCEPT: `wiki/wave_fivej_freeze_independent_review.md`
- Freeze contract: `wiki/wave_fivej_ticketed_writes_contract.md`
- Product-ready research ACCEPT: `wiki/wave_fivej_product_ready_research_independent_review.md`
- Review scratch: `.fractal/main.billy_complete/tmp/grok-review.md`
- Research scratch: `.fractal/main.billy_complete/tmp/grok-research.md`
- Offline probe rules: `wiki/offline_write_probe_rules.md`
