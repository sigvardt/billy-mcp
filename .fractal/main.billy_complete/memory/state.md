---
name: state
desc: Current node state, verified review decisions, and open qualification work.
tags: [billy, coverage, review]
sources:
  - docs/superpowers/specs/2026-07-28-billy-mcp-complete-design.md
  - https://www.billy.dk/api/
created: 2026-07-29T12:12:38Z
updated: 2026-07-29T20:10:00Z
---

# state

## Current state

- Wave-5c and Wave-5d parent/line write modules are merged into root; root registration uses the one shared `ConfirmationStore` and `WriteProtocolService`.
- Runtime: **166** `api_*` + 2 coverage; 36 preview + 36 execute ticketed write tools. Bill write tools still absent on tip `a3972cd`.
- Coverage: implemented 130, contract_tested 130, live 0, vision 0, `complete: false`. Six Wave-5e CUD rows still red (honest).
- Official docs fingerprint still etag `hsisik4g9p3603`, MD5 `c2efda0ee4cf9cf200e14910c5fc6996` (body 147934 bytes). Independent-review re-fetch matches.
- Wave-5a registration product: **ACCEPT** offline.
- Wave-5b freeze: **ACCEPT**. Wave-5b product at `920ceab`: **REJECTED**. Repair product at `a2a0996`: **ACCEPT**.
- Wave-5c freeze: **ACCEPT**. Wave-5c product at tip `f235ac2`: **ACCEPT** offline by independent Grok.
- Wave-5d freeze at tip `5c376de`: **ACCEPT** offline contract only.
- Wave-5d product at tip **`1108e2f`**: **ACCEPT** offline by independent Grok (`wiki/wave_fived_product_independent_review.md`).
- Wave-5e freeze at `fc8118e`: **ACCEPT** offline (`wiki/wave_fivee_freeze_independent_review.md`). Codex fallback is supplemental only.
- Wave-5e plan at tip **`a3972cd`**: independent Grok review **PASS** on plan fidelity and fail-closed coverage (`tmp/grok-review.md`). Product **not accepted** (modules not on root).
- Wave-5e product leaves (`wave5e_bill_writes`, `wave5e_bill_line_writes`) may be in flight; root must merge owned files only, then request product review.
- Root baseline verification after the plan review: lint (format/Ruff/Pyright,
  coverage inventory, repository policy) passed and non-live suite passed
  **753 tests**. This does not qualify the in-flight product modules.
- Clear red remaining: **77** of 207 clear ops (includes 6 Wave-5e bill/line CUD). After Wave-5e product: target **178** `api_*`, **136** offline rows.
- UI all red; bulk 92 empty-tool red; four specials red; no live token in process env.
- Historical unmerged review branches contain child-seed state and superseded fallback reports only, so they remain intentionally closed rather than merged.

## Review decisions (authoritative)

- Wave-5a integrated product: **ACCEPT** offline.
- Wave-5b freeze: **ACCEPT**.
- Wave-5b product at `920ceab`: **REJECTED**.
- Wave-5b repair at `a2a0996`: **ACCEPT** offline.
- Wave-5c freeze: **ACCEPT** offline contract only.
- Wave-5c product at tip `f235ac2`: **ACCEPT** offline by independent Grok audit.
- Wave-5d freeze at tip `5c376de`: **ACCEPT** offline contract only.
- Wave-5d product at tip `1108e2f`: **ACCEPT** offline by independent Grok.
- Wave-5e freeze at `fc8118e`: **ACCEPT** offline by the authoritative root Grok independent review.
- Wave-5e plan tip `a3972cd`: independent review **PASS** plan/coverage honesty; product **FAIL/not present**.
- Wave-5e product: **not accepted** until product lands on root + independent Grok product review.
- Overall completeness: **FAIL** until live, bulk, remaining writes, specials, UI/vision close red rows.

## Open coverage work

1. Implement bills + billLines under the accepted Wave-5e freeze (target 178 `api_*`, 136 offline rows), then obtain a separate Grok product review.
2. Remaining clear writes (~71 after Wave-5e), specials, bulk (live only), UI/auth/vision, and live qualification.

## Research pass (product handoff)

- Docs re-fetch: ETag `hsisik4g9p3603`, MD5 match, 147934 bytes — no source drift.
- Unauth probes: bills/billLines POST/PUT 401; missing-id DELETE 200 (not cleanup proof); postings CUD still 405.
- Contract unchanged vs freeze: opaque bill payload; bill lines account/taxRate/description/amount; line `additional_plural_roots=("bills",)`; no invoice-style embedded-line rules for bills.
- Clone pattern: `invoice_writes.py` + `invoice_line_writes.py`.
- UI discovery still blocked at login; no UI work in Wave-5e product.

## Evidence boundaries

- Official API fingerprint: etag `hsisik4g9p3603`, MD5 `c2efda0ee4cf9cf200e14910c5fc6996`.
- Invoice-line writes declare `additional_plural_roots=("invoices",)` and map the parent root only when present.
- Bill line writes must declare `additional_plural_roots=("bills",)` (optional parent root when absent).
- Bill lines fields: account/taxRate/description/amount (not product/unitPrice).
- Bill `lines` has-many has no invoice-style required/replace/create-only notes offline.
- Unauth DELETE empty 200 is not cleanup proof.
- Product ACCEPT is offline only; no live/UI/bulk/completeness claim.
- Postings CUD still unauth HTTP 405 despite Supports flags — out of Wave-5e.

## References

- Research (scratch): `.fractal/main.billy_complete/tmp/grok-research.md`
- Review (scratch): `.fractal/main.billy_complete/tmp/grok-review.md`
- Wiki freeze 5d: `wiki/wave_fived_ticketed_writes_contract.md`
- Wiki freeze ACCEPT 5d: `wiki/wave_fived_freeze_independent_review.md`
- Wiki freeze ACCEPT 5e: `wiki/wave_fivee_freeze_independent_review.md`
- Wiki product ACCEPT 5d: `wiki/wave_fived_product_independent_review.md`
- Wave-5c Grok product ACCEPT: `wiki/wave_fivec_product_independent_review.md`
