---
name: state
desc: Current node state, verified review decisions, and open qualification work.
tags: [billy, coverage, review]
sources:
  - docs/superpowers/specs/2026-07-28-billy-mcp-complete-design.md
  - https://www.billy.dk/api/
created: 2026-07-30T05:20:45Z
updated: 2026-07-30T05:20:45Z
---

# state

## Current state

- Wave-5c through Wave-5j write modules are merged into root; root registration uses the one shared `ConfirmationStore` and `WriteProtocolService`.
- Wave-5j and Wave-5k products are on root (`src/billy_mcp/api/bank_line_writes.py` and `src/billy_mcp/api/bank_payment_writes.py`). Registry **242** `api_*` tools. Offline coverage **168** implemented + contract_tested. Live/vision still 0. `complete: false`.
- Wave-5k freeze page is on root at `wiki/wave_fivek_ticketed_writes_contract.md`.
- **Wave-5k freeze independent Grok review: ACCEPT** at
  `wiki/wave_fivek_freeze_independent_review.md`. Opens offline four-tool product leaf only.
- Wave-5k product is merged with four ticketed bank-payment create/update tools,
  tests, server registration, and generated coverage evidence. `api.bankPayments.create`
  and `.update` are offline-qualified only; delete stays red (405).
- Wave-5k product still requires an independent Grok product review. Its merge does
  not green live, UI, vision, bulk, or `complete`.
- Next freeze after product ACCEPT: **Wave-5l salesTaxPayments** create+update
  (seeded in research53). Then contactBalancePayments, invoiceLateFees,
  invoiceReminders create-only.
- UI all red; bulk 92 empty-tool red; no live token; no UI credentials.

## Verification

- Official docs retain ETag `hsisik4g9p3603`, MD5
  `c2efda0ee4cf9cf200e14910c5fc6996`, and a 147934-byte body (research53 reconfirm).
- Unauth probes research53: bankPayments and salesTaxPayments POST/PUT **401**;
  singular DELETE **405**. invoiceReminders PUT **405**.
- Clean-archive root integration validation passed Ruff, Pyright, 1,038 non-live
  tests, coverage validation, and repository policy checks.
- No false coverage greens: registry 242; only bankPayments create/update became
  implemented and contract-tested; live/vision remain zero.
- Freeze ACCEPT does not green coverage and is not product ACCEPT.

## Review decisions (authoritative)

- Wave-5g through Wave-5i freeze/product: **ACCEPT** offline where recorded.
- Wave-5j freeze and product: **ACCEPT** offline (product via Codex fallback ACCEPT page).
- Wave-5k freeze-ready / implementation / authoring-readiness / package / authority research: **ACCEPT** offline handoffs as recorded.
- Wave-5k product-ready research: **ACCEPT offline handoff only**.
- Wave-5k freeze page: **ACCEPT** at `wiki/wave_fivek_freeze_independent_review.md`.
- Wave-5k product: **merged and offline-verified; independent product acceptance pending**.
- Overall completeness: **FAIL**.

## Open coverage work

1. Independent Wave-5k product review ACCEPT after the merged offline verification.
2. Wave-5l freeze + product: salesTaxPayments create+update (**+2 → 170**, tools **246**).
3. Later freezes: contactBalancePayments / invoiceLateFees create+update;
   invoiceReminders create only (PUT 405); remaining blocked CUD.
4. Bulk 92, UI/auth/vision, live CUD still open.
5. Inventory cleanup text debt: several create rows still say “delete dedicated
   test resource” where singular DELETE is 405; freezes must use void/`isVoided`
   where documented (research does not green coverage to fix text).

## Evidence boundaries

- Official API fingerprint: etag `hsisik4g9p3603`, MD5 `c2efda0ee4cf9cf200e14910c5fc6996`.
- bankPayments singular DELETE remains **405**; no delete tools.
- salesTaxPayments Supports omits singular delete; DELETE still 405; `isVoided` present.
- Inventory create cleanup for bankPayments: void via irreversible `isVoided` (live verify later).
- No coverage green from review alone.

## References

- Freeze ACCEPT: `wiki/wave_fivek_freeze_independent_review.md`
- Freeze contract: `wiki/wave_fivek_ticketed_writes_contract.md`
- Fallback freeze record: `wiki/wave_fivek_freeze_codex_fallback_review.md`
- Current research scratch: `.fractal/main.billy_complete/tmp/grok-research.md` (research53)
- Current review scratch: `.fractal/main.billy_complete/tmp/grok-review.md`
