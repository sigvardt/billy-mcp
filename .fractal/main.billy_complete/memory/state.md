---
name: state
desc: Current node state, verified review decisions, and open qualification work.
tags: [billy, coverage, review]
sources:
  - docs/superpowers/specs/2026-07-28-billy-mcp-complete-design.md
  - https://www.billy.dk/api/
created: 2026-07-29T22:11:45Z
updated: 2026-07-30T00:10:00Z
---

# state

## Current state

- Wave-5c through Wave-5h write modules are merged into root; root registration uses the one shared `ConfirmationStore` and `WriteProtocolService`.
- Root merge **`29cecbe`** integrates Wave-5h attachment product: **208** `api_*` tools; offline product **ACCEPT** at `wiki/wave_fiveh_product_independent_review.md`.
- Wave-5h freeze remains accepted (`wiki/wave_fiveh_ticketed_writes_contract.md`, `wiki/wave_fiveh_freeze_independent_review.md`).
- Wave-5g product remains accepted at **`55faa02`** (`wiki/wave_fiveg_product_independent_review.md`).
- The Wave-5i freeze-ready ACCEPT stands at `wiki/wave_fivei_freeze_ready_research_independent_review.md`.
- Cited freeze-implementation research reconfirms the unchanged docs fingerprint (etag `hsisik4g9p3603`, MD5 `c2efda0ee4cf9cf200e14910c5fc6996`) and the 401 POST/PUT plus DELETE-200 trap on both resources. Full brief: `tmp/grok-research.md`.
- The Wave-5i freeze page is drafted at `wiki/wave_fivei_ticketed_writes_contract.md` and awaits independent Grok review. Product code remains absent and is not authorised.
- Coverage: implemented 151, contract_tested 151, live 0, vision 0, `complete: false`. Clear red CUD: 58.
- UI all red; bulk 92 empty-tool red; specials red; no live token.
- Child product reviews `wave5h_product_review_grok` and `wave5i_freeze_review_grok` exited without durable ACCEPT; root reviews supersede them.
- Their Codex Power fallback review nodes likewise left seed-only branches and no mergeable supplemental review page.
- Child `wave5h_attachment_product` completed and merged.

## Review decisions (authoritative)

- Wave-5g product at root merge `55faa02`: **ACCEPT** offline.
- Wave-5h freeze: **ACCEPT** offline contract.
- Wave-5h product at root merge `29cecbe`: **ACCEPT** offline.
- Wave-5i freeze-ready research: **ACCEPT** offline handoff only; does not green coverage or accept freeze/product.
- Wave-5i freeze-implementation research: primary sources reconfirmed; it authorises the draft but not freeze or product acceptance.
- Wave-5i freeze page: **drafted / pending independent review**.
- Wave-5i product: **not implemented / not accepted**.
- Overall completeness: **FAIL**.

## Open coverage work

1. Independent freeze review for the drafted Wave-5i page; then product-ready research and product (+12 → 220; coverage 157).
2. Later: bank line family CUD (9 clear red), partial CUD cohorts, specials (binary files upload), bulk live, UI/auth/vision, live attachment CUD.
3. Blocked offline (405 / readonly): accountNatures, postings, balanceModifiers, contactBalancePostings, geo CUD, bankPayments/salesTaxPayments delete, transactions CUD, invoiceReminderAssociations create/update.

## Evidence boundaries

- Official API fingerprint: etag `hsisik4g9p3603`, MD5 `c2efda0ee4cf9cf200e14910c5fc6996`; the cited refresh is byte-identical to the existing inventory source.
- Unauth DELETE 200 is not cleanup proof.
- Unauth POST `/files` invalid JSON → 400 `INVALID_REQUEST_BODY`; not a JSON create contract.
- Product ACCEPT requires real offline suites; no green from research/freeze alone.
- salesTaxAccounts: `type` enum values unpublished; `account` not marked immutable.
- salesTaxMetaFields: `isPredefined` not marked readonly (unlike rulesets); keep opaque.

## References

- Freeze-implementation research (scratch): `.fractal/main.billy_complete/tmp/grok-research.md`
- Wiki freeze-ready ACCEPT 5i: `wiki/wave_fivei_freeze_ready_research_independent_review.md`
- Wiki drafted freeze contract 5i: `wiki/wave_fivei_ticketed_writes_contract.md`
- Wiki product ACCEPT 5h: `wiki/wave_fiveh_product_independent_review.md`
- Wiki freeze contract 5h: `wiki/wave_fiveh_ticketed_writes_contract.md`
- Wiki freeze template 5g: `wiki/wave_fiveg_ticketed_writes_contract.md`
- Offline probe rules: `wiki/offline_write_probe_rules.md`
