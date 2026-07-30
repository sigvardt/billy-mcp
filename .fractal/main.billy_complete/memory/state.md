---
name: state
desc: Current node state, verified review decisions, and open qualification work.
tags: [billy, coverage, review]
sources:
  - docs/superpowers/specs/2026-07-28-billy-mcp-complete-design.md
  - https://www.billy.dk/api/
created: 2026-07-29T22:11:45Z
updated: 2026-07-30T03:22:00Z
---

# state

## Current state

- Wave-5c through Wave-5i write modules are merged into root; root registration uses the one shared `ConfirmationStore` and `WriteProtocolService`.
- Wave-5j freeze page is merged at root merge **`0db66d0`** (`wiki/wave_fivej_ticketed_writes_contract.md`). Independent freeze review **ACCEPT** at `wiki/wave_fivej_freeze_independent_review.md`.
- Wave-5j product is **merged on root** at **`d86844f`** (`src/billy_mcp/api/bank_line_writes.py`, 18 ticketed tools). Registry **238** `api_*` tools. Offline coverage **166** implemented + contract_tested. Live/vision still 0. `complete: false`.
- Wave-5j product has an **offline-only independent Codex fallback ACCEPT** at
  `wiki/wave_fivej_product_independent_review.md`, merged as `fc3eb29`. The
  page explicitly says the fallback review does **not** authorize Wave-5k work,
  so the Wave-5k freeze-authoring gate remains blocked until an authority that
  can grant it is available. It does not advance live, UI, vision, bulk,
  cleanup, bankPayments, or completeness claims.
- Wave-5k research chain is complete for freeze-package content:
  - freeze-ready ACCEPT (research44)
  - freeze-implementation ACCEPT (research45)
  - freeze authoring readiness ACCEPT (research46)
  - freeze page authoring package research (research47) at `.fractal/main.billy_complete/tmp/grok-research.md` with §5–§6
  - independent Grok ACCEPT of research47 package content: `wiki/wave_fivek_freeze_page_authoring_package_research_independent_review.md`
- Wave-5k freeze page and product are **blocked, not started**. Package content
  is accepted; authoring is not authorized by the Wave-5j product fallback.
- Coverage: implemented 166, contract_tested 166, live 0, vision 0, `complete: false`. Clear non-bulk write rows still red: 46 (includes specials and blocked methods).
- UI all red; bulk 92 empty-tool red; no live token; no UI credentials.

## Verification

- Official docs reconfirmed independently for research47 review: ETag `hsisik4g9p3603`, MD5 `c2efda0ee4cf9cf200e14910c5fc6996`, 147934 bytes (byte-identical to research47).
- Unauth probes reconfirmed independently: bankPayments POST/PUT **401** `AUTHENTICATION_REQUIRED`; DELETE **405** `METHOD_NOT_ALLOWED` with message “Resource at `bankPayments` does not support deleting a single record.”
- salesTaxPayments POST/PUT 401, DELETE 405 (Wave-5l seed consistent).
- No false coverage greens; registry 238; bankPayments write tools absent; freeze page absent.
- No coverage greens from research or this review. No full-mode claim.

## Review decisions (authoritative)

- Wave-5g product: **ACCEPT** offline.
- Wave-5h freeze / product: **ACCEPT** offline.
- Wave-5i freeze / product: **ACCEPT** offline.
- Wave-5j freeze-ready research: **ACCEPT** offline handoff only.
- Wave-5j freeze-implementation research: **ACCEPT** offline handoff only.
- Wave-5j freeze contract at merge `0db66d0`: **ACCEPT** offline contract.
- Wave-5j product-ready research: **ACCEPT** offline handoff only.
- Wave-5j product: **offline-only independent Codex fallback ACCEPT** on the
  merged root bytes; its own explicit non-acceptance keeps Wave-5k blocked. The
  accepted slice is limited to 18 bank-line tools and 166 offline rows.
- Wave-5k freeze-ready research (research44): **ACCEPT** offline freeze-drafting handoff only.
- Wave-5k freeze-implementation research (research45): **ACCEPT** offline freeze-page authoring handoff only.
- Wave-5k freeze authoring readiness (research46): **ACCEPT** offline freeze-page authoring handoff only.
- Wave-5k freeze page authoring package (research47): **ACCEPT** offline package content only; **not** freeze ACCEPT; authoring still blocked by Wave-5j product fallback non-authorization.
- Wave-5k freeze / product: **not authored**.
- Overall completeness: **FAIL**.

## Open coverage work

1. Resolve the authority gap in `wiki/wave_fivej_product_independent_review.md`:
   a review or decision that explicitly opens Wave-5k authoring is required
   before authoring the Wave-5k page from research47 §5–§6, freeze review, or
   product work.
2. Later freezes: salesTaxPayments (research47 §10 seed: amount/side readonly, isVoided update candidate) / contactBalancePayments / invoiceLateFees create+update; invoiceReminders create; salesTaxReturns update; users update; orgs with risk gate; transactions only after readonly resolution.
3. Blocked offline (405 / readonly): accountNatures, postings, balanceModifiers, contactBalancePostings, geo CUD, bankPayments/salesTaxPayments/contactBalancePayments delete, invoiceReminderAssociations create/update, files JSON as binary special.
4. Bulk 92, UI/auth/vision, live CUD still open.

## Evidence boundaries

- Official API fingerprint: etag `hsisik4g9p3603`, MD5 `c2efda0ee4cf9cf200e14910c5fc6996`.
- bankPayments singular DELETE remains **405** and overrides Supports delete for offline tools.
- Inventory still carries `tool_name` for delete; freeze must not register delete tools.
- Inventory create cleanup text still says delete; live path must void via `isVoided` (irreversible).
- No coverage green from research or this review.

## References

- Wave-5j freeze ACCEPT: `wiki/wave_fivej_freeze_independent_review.md`
- Wave-5j freeze contract: `wiki/wave_fivej_ticketed_writes_contract.md`
- Wave-5j product-ready research ACCEPT: `wiki/wave_fivej_product_ready_research_independent_review.md`
- Wave-5j product merge: `d86844f`
- Wave-5j product fallback ACCEPT: `wiki/wave_fivej_product_independent_review.md`
- Wave-5k freeze-ready research ACCEPT: `wiki/wave_fivek_freeze_ready_research_independent_review.md`
- Wave-5k freeze-implementation research ACCEPT: `wiki/wave_fivek_freeze_implementation_research_independent_review.md`
- Wave-5k freeze authoring readiness research ACCEPT: `wiki/wave_fivek_freeze_authoring_readiness_research_independent_review.md`
- Wave-5k freeze page package research ACCEPT: `wiki/wave_fivek_freeze_page_authoring_package_research_independent_review.md`
- Research scratch: `.fractal/main.billy_complete/tmp/grok-research.md` (research47)
- Review scratch: `.fractal/main.billy_complete/tmp/grok-review.md`
- Offline probe rules: `wiki/offline_write_probe_rules.md`
