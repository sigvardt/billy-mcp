---
name: state
desc: Current node state, verified review decisions, and open qualification work.
tags: [billy, coverage, review]
sources:
  - docs/superpowers/specs/2026-07-28-billy-mcp-complete-design.md
  - https://www.billy.dk/api/
created: 2026-07-29T22:11:45Z
updated: 2026-07-30T03:58:00Z
---

# state

## Current state

- Wave-5c through Wave-5i write modules are merged into root; root registration uses the one shared `ConfirmationStore` and `WriteProtocolService`.
- Wave-5j freeze page is merged (`wiki/wave_fivej_ticketed_writes_contract.md`). Independent freeze review **ACCEPT** at `wiki/wave_fivej_freeze_independent_review.md`.
- Wave-5j product is **merged on root** at **`d86844f`** (`src/billy_mcp/api/bank_line_writes.py`, 18 ticketed tools). Registry **238** `api_*` tools. Offline coverage **166** implemented + contract_tested. Live/vision still 0. `complete: false`.
- Wave-5j product has an **offline-only independent Codex fallback ACCEPT** at
  `wiki/wave_fivej_product_independent_review.md`.
- Wave-5k research chain complete through freeze authoring authority (research44–48).
- Wave-5k freeze authoring authority independent Grok review: **ACCEPT** at
  `wiki/wave_fivek_freeze_authoring_authority_research_independent_review.md`.
- **Wave-5k freeze page is still ABSENT.** Codex Power may author
  `wiki/wave_fivek_ticketed_writes_contract.md` (create+update only; delete
  excluded on 405). Product module still **absent**.
- Research49 product-ready handoff **ACCEPT** offline (root review in
  `.fractal/main.billy_complete/tmp/grok-review.md`). Four-tool recipe validated;
  product still blocked until freeze page + freeze ACCEPT. The original Grok
  wiki-twin child could not authenticate before editing; the policy-required
  Codex fallback review and the Codex freeze-contract child are active.
- Coverage: implemented 166, contract_tested 166, live 0, vision 0, `complete: false`.
  Clear singular CUD rows still red: **43**.
- UI all red; bulk 92 empty-tool red; no live token; no UI credentials.

## Verification

- Official docs reconfirmed for research49 review: ETag `hsisik4g9p3603`, MD5
  `c2efda0ee4cf9cf200e14910c5fc6996`, 147934 bytes (byte-identical to research49 HTML).
- Unauth probes reconfirmed: bankPayments POST/PUT **401**; DELETE **405** with
  message “Resource at `bankPayments` does not support deleting a single record.”
- salesTaxPayments and contactBalancePayments POST/PUT 401, DELETE 405 (Wave-5l seeds).
- No false coverage greens; registry 238; bankPayments write tools absent; freeze page absent.
- Product-ready handoff ACCEPT is not product or freeze ACCEPT. No full-mode claim.

## Review decisions (authoritative)

- Wave-5g product: **ACCEPT** offline.
- Wave-5h freeze / product: **ACCEPT** offline.
- Wave-5i freeze / product: **ACCEPT** offline.
- Wave-5j freeze-ready research: **ACCEPT** offline handoff only.
- Wave-5j freeze-implementation research: **ACCEPT** offline handoff only.
- Wave-5j freeze contract: **ACCEPT** offline contract.
- Wave-5j product-ready research: **ACCEPT** offline handoff only.
- Wave-5j product: **offline-only independent Codex fallback ACCEPT**; product
  non-overclaim does not open Wave-5k product and is not a permanent freeze
  research block. Accepted slice is 18 bank-line tools and 166 offline rows.
- Wave-5k freeze-ready / freeze-implementation / authoring-readiness / package
  research: **ACCEPT** offline handoffs (package content only for package page).
- Wave-5k freeze authoring authority (research48): **ACCEPT** — opens offline
  freeze-page authoring for bankPayments create+update only.
- Wave-5k product-ready research (research49): **ACCEPT offline handoff only** (root independent review; product still blocked on freeze page + freeze ACCEPT).
- Wave-5k freeze page / product: **not authored**.
- Overall completeness: **FAIL**.

## Open coverage work

1. Codex Power authors `wiki/wave_fivek_ticketed_writes_contract.md` (create+update
   only; delete excluded on 405); then independent freeze review ACCEPT.
2. Four-tool product leaf after freeze ACCEPT (research49 product-ready root ACCEPT
   already met) → registry 242 / coverage 168 offline; delete stays red.
3. Later freezes: salesTaxPayments / contactBalancePayments / invoiceLateFees
   create+update; invoiceReminders create; salesTaxReturns update; users update;
   orgs with risk gate; transactions only after readonly resolution.
4. Blocked offline (405 / readonly): accountNatures, postings, balanceModifiers,
   contactBalancePostings, geo CUD, bankPayments/salesTaxPayments/
   contactBalancePayments delete, invoiceReminderAssociations create/update,
   files JSON as binary special.
5. Bulk 92, UI/auth/vision, live CUD still open.

## Evidence boundaries

- Official API fingerprint: etag `hsisik4g9p3603`, MD5 `c2efda0ee4cf9cf200e14910c5fc6996`.
- bankPayments singular DELETE remains **405** and overrides Supports delete for offline tools.
- Inventory still carries `tool_name` for delete; freeze/product must not register delete tools.
- Inventory create cleanup text still says delete; live path must void via `isVoided` (irreversible).
- Clear singular CUD red count observed at research49: **43**.
- No coverage green from research.

## References

- Wave-5j freeze ACCEPT: `wiki/wave_fivej_freeze_independent_review.md`
- Wave-5j freeze contract: `wiki/wave_fivej_ticketed_writes_contract.md`
- Wave-5j product fallback ACCEPT: `wiki/wave_fivej_product_independent_review.md`
- Wave-5k freeze-ready research ACCEPT: `wiki/wave_fivek_freeze_ready_research_independent_review.md`
- Wave-5k freeze-implementation research ACCEPT: `wiki/wave_fivek_freeze_implementation_research_independent_review.md`
- Wave-5k freeze authoring readiness research ACCEPT: `wiki/wave_fivek_freeze_authoring_readiness_research_independent_review.md`
- Wave-5k freeze page package research ACCEPT: `wiki/wave_fivek_freeze_page_authoring_package_research_independent_review.md`
- Wave-5k freeze authoring authority ACCEPT: `wiki/wave_fivek_freeze_authoring_authority_research_independent_review.md`
- Research scratch: `.fractal/main.billy_complete/tmp/grok-research.md` (research49 product-ready)
- Review scratch: `.fractal/main.billy_complete/tmp/grok-review.md` (research49 product-ready ACCEPT)
- Offline probe rules: `wiki/offline_write_probe_rules.md`
