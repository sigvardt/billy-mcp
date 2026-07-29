---
name: state
desc: Current node state, verified review decisions, and open qualification work.
tags: [billy, coverage, review]
sources:
  - docs/superpowers/specs/2026-07-28-billy-mcp-complete-design.md
  - https://www.billy.dk/api/
created: 2026-07-29T12:12:38Z
updated: 2026-07-29T20:40:00Z
---

# state

## Current state

- Wave-5c through Wave-5e parent/line write modules are merged into root; root registration uses the one shared `ConfirmationStore` and `WriteProtocolService`.
- Runtime: **178** `api_*` + 2 coverage; 42 preview + 42 execute ticketed write tools. Bill and bill-line tools are registered through the shared root protocol.
- Coverage: implemented 136, contract_tested 136, live 0, vision 0, `complete: false`. Clear red write-ish ops remain after Wave-5e; Wave-5f targets the six tax CUD rows.
- Official docs fingerprint still etag `hsisik4g9p3603`, MD5 `c2efda0ee4cf9cf200e14910c5fc6996` (body 147934 bytes). Research re-fetch matches research27 (no source drift).
- Wave-5a registration product: **ACCEPT** offline.
- Wave-5b freeze: **ACCEPT**. Wave-5b product at `920ceab`: **REJECTED**. Repair product at `a2a0996`: **ACCEPT**.
- Wave-5c freeze: **ACCEPT**. Wave-5c product at tip `f235ac2`: **ACCEPT** offline by independent Grok.
- Wave-5d freeze at tip `5c376de`: **ACCEPT** offline contract only.
- Wave-5d product at tip **`1108e2f`**: **ACCEPT** offline by independent Grok (`wiki/wave_fived_product_independent_review.md`).
- Wave-5e freeze at `fc8118e`: **ACCEPT** offline (`wiki/wave_fivee_freeze_independent_review.md`). Codex fallback is supplemental only.
- Wave-5e product at tip **`15d0bde`** / root record **`c92ed0e`**: **ACCEPT** offline by independent Grok (`wiki/wave_fivee_product_independent_review.md`).
- Wave-5f freeze: **research complete, freeze not committed**. Brief is freeze-ready.
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
- Wave-5e product at tip `15d0bde`: **ACCEPT** offline by independent Grok.
- Wave-5f freeze: **ready to open** from current research brief; not yet ACCEPTed.
- Overall completeness: **FAIL** until live, bulk, remaining writes, specials, UI/vision close red rows.

## Open coverage work

1. Wave-5f: freeze then implement taxRates + taxRateDeductionComponents (6 clear CUD; target +12 tools / +6 offline rows).
2. Remaining clear writes after 5f, specials, bulk (live only), UI/auth/vision, and live qualification.

## Research pass (Wave-5f freeze-ready handoff)

- Docs re-fetch: ETag `hsisik4g9p3603`, MD5 match, 147934 bytes — no source drift.
- Unauth probes: taxRates and taxRateDeductionComponents POST/PUT **401**, missing-id DELETE **200** (not cleanup proof). OPTIONS Allow includes POST,PUT,DELETE (and PATCH via CORS only).
- Recommended Wave-5f: six singular CUD rows for `taxRates` + `taxRateDeductionComponents`.
- Module: prefer one `tax_writes.py` cloning `catalog_writes.py` (product/price).
- Roots: parent `taxRate` / `taxRates` with `additional_plural_roots=("taxRateDeductionComponents",)`; child `taxRateDeductionComponent` / `taxRateDeductionComponents` with `additional_plural_roots=()`.
- Field notes: most tax-rate fields immutable; `isActive` is the clear mutable update candidate; deduction components nearly all immutable (`priority` candidate); `source` enum values undocumented offline.
- Probe blockers recorded (stay red): postings CUD **405**; bankPayments DELETE **405**; accountNatures/geo create **405**; invoiceReminderAssociations create **405**; salesTaxReturns create **405**.
- Follow-on candidates (401 path): attachments (3), salesTaxRulesets+Rules (6), salesTaxAccounts/MetaFields.
- Transactions: unauth CUD auth-gated but property table all readonly — high live ambiguity; not Wave-5f.
- UI discovery still blocked at login; no UI work in Wave-5f offline product.

## Evidence boundaries

- Official API fingerprint: etag `hsisik4g9p3603`, MD5 `c2efda0ee4cf9cf200e14910c5fc6996`.
- Invoice-line writes declare `additional_plural_roots=("invoices",)` and map the parent root only when present.
- Bill line writes must declare `additional_plural_roots=("bills",)` (optional parent root when absent).
- Bill lines fields: account/taxRate/description/amount (not product/unitPrice).
- Bill `lines` has-many has no invoice-style required/replace/create-only notes offline.
- Tax-rate parent may optionally map `taxRateDeductionComponents` like products→productPrices; child stays without additional roots offline.
- Unauth DELETE empty 200 is not cleanup proof.
- Unauth METHOD_NOT_ALLOWED 405 overrides Supports-flag optimism for offline green paths.
- Product ACCEPT is offline only; no live/UI/bulk/completeness claim.
- Postings CUD still unauth HTTP 405 despite Supports flags — out of Wave-5f.

## References

- Research (scratch): `.fractal/main.billy_complete/tmp/grok-research.md`
- Review (scratch): `.fractal/main.billy_complete/tmp/grok-review.md`
- Wiki freeze 5d: `wiki/wave_fived_ticketed_writes_contract.md`
- Wiki freeze ACCEPT 5d: `wiki/wave_fived_freeze_independent_review.md`
- Wiki freeze ACCEPT 5e: `wiki/wave_fivee_freeze_independent_review.md`
- Wiki product ACCEPT 5d: `wiki/wave_fived_product_independent_review.md`
- Wiki product ACCEPT 5e: `wiki/wave_fivee_product_independent_review.md`
- Wave-5c Grok product ACCEPT: `wiki/wave_fivec_product_independent_review.md`
