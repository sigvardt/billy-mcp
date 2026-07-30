---
name: state
desc: Current node state, verified review decisions, and open qualification work.
tags: [billy, coverage, review]
sources:
  - docs/superpowers/specs/2026-07-28-billy-mcp-complete-design.md
  - https://www.billy.dk/api/
created: 2026-07-30T05:20:45Z
updated: 2026-07-30T05:29:28Z
---

# state

## Current state

- Wave-5c through Wave-5k write modules are merged into root; root registration uses the one shared `ConfirmationStore` and `WriteProtocolService`.
- Wave-5k product is on root (`src/billy_mcp/api/bank_payment_writes.py`). Registry **242** `api_*` tools. Offline coverage **168** implemented + contract_tested. Live/vision still 0. `complete: false`.
- Wave-5k freeze page: `wiki/wave_fivek_ticketed_writes_contract.md` with freeze **ACCEPT** at `wiki/wave_fivek_freeze_independent_review.md`.
- **Wave-5k product independent Grok review: ACCEPT** at
  `wiki/wave_fivek_product_independent_review.md` (root HEAD `ee40a40`).
  Full findings: `.fractal/main.billy_complete/tmp/grok-review.md`.
- The reviewer node reached its iteration cap after writing the root-owned
  evidence handoff; manager validation reproduced the focused suite and keeps
  the cited Grok verdict as the independent product decision.
- bankPayments create+update offline-qualified only; delete stays red (405); bulk stays ambiguous.
- Next freeze after product ACCEPT: **Wave-5l salesTaxPayments** create+update
  (seeded in research53). Then contactBalancePayments, invoiceLateFees,
  invoiceReminders create-only.
- UI all red; bulk 92 empty-tool red; no live token; no UI credentials.

## Verification

- Official docs retain ETag `hsisik4g9p3603`, MD5
  `c2efda0ee4cf9cf200e14910c5fc6996`, and a 147934-byte body.
- Unauth probes: bankPayments POST/PUT **401**; DELETE **405**.
- Product tests at review: 20 passed (`test_bank_payment_writes` + coverage server suite portion).
- Clean-root non-live validation: Ruff, Pyright, coverage and repository-policy
  checks passed; the non-live suite reported **1,038 passed**.
- No false coverage greens: only create+update newly offline-green; live/vision 0; `complete: false`.

## Review decisions (authoritative)

- Wave-5g through Wave-5i freeze/product: **ACCEPT** offline where recorded.
- Wave-5j freeze and product: **ACCEPT** offline.
- Wave-5k freeze page: **ACCEPT**.
- Wave-5k product: **ACCEPT** offline at `wiki/wave_fivek_product_independent_review.md`.
- Overall completeness: **FAIL**.

## Open coverage work

1. Wave-5l freeze + product: salesTaxPayments create+update (**+2 → 170**, tools **246**).
2. Later freezes: contactBalancePayments / invoiceLateFees create+update;
   invoiceReminders create only (PUT 405); remaining blocked CUD.
3. Bulk 92, UI/auth/vision, live CUD still open.
4. Inventory cleanup text debt on resources that still say “delete dedicated
   test resource” where singular DELETE is 405.

## Evidence boundaries

- Official API fingerprint: etag `hsisik4g9p3603`, MD5 `c2efda0ee4cf9cf200e14910c5fc6996`.
- bankPayments singular DELETE remains **405**; no delete tools.
- Product ACCEPT does not green live/UI/vision/bulk/complete.
- No coverage green from review alone.

## References

- Product ACCEPT: `wiki/wave_fivek_product_independent_review.md`
- Freeze ACCEPT: `wiki/wave_fivek_freeze_independent_review.md`
- Freeze contract: `wiki/wave_fivek_ticketed_writes_contract.md`
- Current research scratch: `.fractal/main.billy_complete/tmp/grok-research.md` (research53)
- Current review scratch: `.fractal/main.billy_complete/tmp/grok-review.md`
