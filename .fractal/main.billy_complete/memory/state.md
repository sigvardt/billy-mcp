---
name: state
desc: Current node state, verified review decisions, and open qualification work.
tags: [billy, coverage, review]
sources:
  - docs/superpowers/specs/2026-07-28-billy-mcp-complete-design.md
  - https://www.billy.dk/api/
created: 2026-07-30T06:20:59Z
updated: 2026-07-30T06:20:59Z
---

# state

## Current state

- Wave-5c through Wave-5k write modules are merged into root; root registration uses the one shared `ConfirmationStore` and `WriteProtocolService`.
- Root registry **242** `api_*` tools. Offline coverage **168** implemented + contract_tested. Live/vision still 0. `complete: false`.
- Wave-5k freeze and product: ACCEPT offline.
- Wave-5l freeze ACCEPT: `wiki/wave_fivel_freeze_independent_review.md` (contract MD5 `3c49c4f41f3d9485a177a6ee643db412`).
- Wave-5l product-ready research package: ACCEPT (prior independent review).
- Wave-5l product child `main.billy_complete.wave5l_sales_tax_payment_product` **completed** with feat commit `00aae09` (`sales_tax_payment_writes.py` + tests). **Not merged to root**; root still lacks the module. Product independent review waits for root merge.
- bankPayments create+update offline-qualified only; delete stays red (405); bulk stays ambiguous.
- salesTaxPayments create+update still red on root inventory until merge.
- The current Wave-5m freeze-ready package for `contactBalancePayments` create+update is in `.fractal/main.billy_complete/tmp/grok-research.md`. Docs fingerprint unchanged. Sequential planning: invoiceLateFees create+update; invoiceReminders create only. contactBalancePostings and invoiceReminderAssociations create/update stay 405-blocked offline.
- UI all red; bulk 92 empty-tool red; no live token; no UI credentials.

## Verification

- Official docs retain ETag `hsisik4g9p3603`, MD5 `c2efda0ee4cf9cf200e14910c5fc6996`, and a 147934-byte body (research56 reconfirm).
- Latest unauth probes: contactBalancePayments POST/PUT **401**, DELETE **405**; invoiceLateFees same; invoiceReminders POST **401**, PUT/DELETE **405**; contactBalancePostings and invoiceReminderAssociations create/update **405**.
- Freeze MD5 `3c49c4f41f3d9485a177a6ee643db412` unchanged for Wave-5l.
- Coverage honesty on root: implemented/contract_tested **168**, live/vision **0**, `complete: false`.

## Review decisions (authoritative)

- Wave-5g through Wave-5k freeze/product: **ACCEPT** offline where recorded.
- Wave-5l freeze page: **ACCEPT** offline.
- Wave-5l product-ready research package: **ACCEPT**.
- Wave-5l product on root: **not accepted** (not merged; product independent review pending).
- Wave-5m freeze: **not accepted** (research package only; freeze page not authored).
- Overall completeness: **FAIL**.

## Open coverage work

1. Merge Wave-5l product child (`00aae09`) to root; independent product review ACCEPT (**+2 → 170**, tools **246**).
2. Author Wave-5m freeze from research56; freeze ACCEPT; product four tools for contactBalancePayments (**+2 → 172**, tools **250**).
3. Later freezes: invoiceLateFees create+update; invoiceReminders create only; remaining blocked CUD (405 or reference data).
4. Bulk 92, UI/auth/vision, live CUD still open.
5. Inventory cleanup text debt on resources that still say “delete dedicated test resource” where singular DELETE is 405.

## Evidence boundaries

- Official API fingerprint: etag `hsisik4g9p3603`, MD5 `c2efda0ee4cf9cf200e14910c5fc6996`.
- contactBalancePayments Supports omits singular delete; unauth DELETE **405**.
- bankPayment “Posting a payment” sample is not the contactBalancePayment request schema.
- Research does not green coverage.

## References

- Current research: `.fractal/main.billy_complete/tmp/grok-research.md` (Wave-5m freeze-ready)
- Wave-5l freeze ACCEPT: `wiki/wave_fivel_freeze_independent_review.md`
- Wave-5l freeze contract: `wiki/wave_fivel_ticketed_writes_contract.md`
- Wave-5k product ACCEPT: `wiki/wave_fivek_product_independent_review.md`
- Offline probe rules: `wiki/offline_write_probe_rules.md`
- Product child branch: `main.billy_complete.wave5l_sales_tax_payment_product` @ `00aae09`
