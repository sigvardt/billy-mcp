---
name: state
desc: Current node state, verified review decisions, and open qualification work.
tags: [billy, coverage, review]
sources:
  - docs/superpowers/specs/2026-07-28-billy-mcp-complete-design.md
  - https://www.billy.dk/api/
created: 2026-07-30T05:56:53Z
updated: 2026-07-30T06:01:00Z
---

# state

## Current state

- Wave-5c through Wave-5k write modules are merged into root; root registration uses the one shared `ConfirmationStore` and `WriteProtocolService`.
- Wave-5k product is on root (`src/billy_mcp/api/bank_payment_writes.py`). Registry **242** `api_*` tools. Offline coverage **168** implemented + contract_tested. Live/vision still 0. `complete: false`.
- Wave-5k freeze ACCEPT: `wiki/wave_fivek_freeze_independent_review.md`.
- Wave-5k product ACCEPT: `wiki/wave_fivek_product_independent_review.md`.
- bankPayments create+update offline-qualified only; delete stays red (405); bulk stays ambiguous.
- **Wave-5l freeze ACCEPT:** `wiki/wave_fivel_freeze_independent_review.md` for `wiki/wave_fivel_ticketed_writes_contract.md` (MD5 `3c49c4f41f3d9485a177a6ee643db412`).
- **Wave-5l product-ready research package ACCEPT** (independent review in `.fractal/main.billy_complete/tmp/grok-review.md`). Product still **absent on root** (`sales_tax_payment_writes.py` missing); do not confuse with `sales_tax_writes.py` rulesets. Product child may be in flight; product ACCEPT waits for root merge + product review.
- UI all red; bulk 92 empty-tool red; no live token; no UI credentials.

## Verification

- Official docs retain ETag `hsisik4g9p3603`, MD5 `c2efda0ee4cf9cf200e14910c5fc6996`, and a 147934-byte body (reconfirmed at product-ready independent review).
- Unauth probes: salesTaxPayments POST/PUT **401**; DELETE **405** exact singular-delete refusal.
- Freeze MD5 `3c49c4f41f3d9485a177a6ee643db412` unchanged; freeze ACCEPT still authoritative.
- Coverage honesty: implemented/contract_tested **168**, live/vision **0**, `complete: false`; create/update inventory rows still red.

## Review decisions (authoritative)

- Wave-5g through Wave-5i freeze/product: **ACCEPT** offline where recorded.
- Wave-5j freeze and product: **ACCEPT** offline.
- Wave-5k freeze page: **ACCEPT**.
- Wave-5k product: **ACCEPT** offline.
- Wave-5l freeze page: **ACCEPT** offline (`wiki/wave_fivel_freeze_independent_review.md`).
- Wave-5l product: **not accepted** (not implemented on root; product child may be in flight).
- Wave-5l product-ready research package: **ACCEPT** (independent review; see `.fractal/main.billy_complete/tmp/grok-review.md`).
- Overall completeness: **FAIL**.

## Open coverage work

1. Wave-5l product four tools after freeze ACCEPT (**+2 → 170**, tools **246**), then product independent review.
2. Later freezes: contactBalancePayments / invoiceLateFees create+update; invoiceReminders create only (PUT 405); remaining blocked CUD.
3. Bulk 92, UI/auth/vision, live CUD still open.
4. Inventory cleanup text debt on resources that still say “delete dedicated test resource” where singular DELETE is 405.

## Evidence boundaries

- Official API fingerprint: etag `hsisik4g9p3603`, MD5 `c2efda0ee4cf9cf200e14910c5fc6996`.
- salesTaxPayments Supports omits singular delete; unauth DELETE **405**.
- Freeze ACCEPT opens product leaf only; does not green live/UI/vision/bulk/complete.
- Research and freeze reviews do not green coverage.

## References

- Wave-5l freeze ACCEPT: `wiki/wave_fivel_freeze_independent_review.md`
- Wave-5l freeze contract: `wiki/wave_fivel_ticketed_writes_contract.md`
- Wave-5k product ACCEPT: `wiki/wave_fivek_product_independent_review.md`
- Current research scratch: `.fractal/main.billy_complete/tmp/grok-research.md` (research55 product-ready)
- Current review scratch: `.fractal/main.billy_complete/tmp/grok-review.md`
