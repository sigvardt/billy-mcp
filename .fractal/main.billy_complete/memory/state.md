---
name: state
desc: Current node state, verified review decisions, and open qualification work.
tags: [billy, coverage, review]
sources:
  - docs/superpowers/specs/2026-07-28-billy-mcp-complete-design.md
  - https://www.billy.dk/api/
created: 2026-07-30T06:20:59Z
updated: 2026-07-30T07:26:00Z
---

# state

## Current state

- Wave-5c through Wave-5l write modules are merged into root; root registration uses the one shared `ConfirmationStore` and `WriteProtocolService`.
- Root registry **246** `api_*` tools. Offline coverage **170** implemented + contract_tested. Live/vision still 0. `complete: false`.
- Wave-5k freeze and product: ACCEPT offline.
- Wave-5l freeze ACCEPT: `wiki/wave_fivel_freeze_independent_review.md` (contract MD5 `3c49c4f41f3d9485a177a6ee643db412`).
- Wave-5l product is on root (`sales_tax_payment_writes.py`); offline create+update green. Product independent review ACCEPT is still open (Grok review child exited on PREPARE; codex-power fallback allowed if no edits yet).
- bankPayments create+update offline-qualified only; delete stays red (405); bulk stays ambiguous.
- salesTaxPayments create+update offline-qualified on root.
- Wave-5m freeze child `main.billy_complete.wave5m_contact_balance_payment_freeze_contract` is active; freeze page not on root yet.
- Wave-5m product-ready research package is in `.fractal/main.billy_complete/tmp/grok-research.md` (research57). Docs fingerprint unchanged. Product waits for freeze ACCEPT. Sequential planning: invoiceLateFees create+update; invoiceReminders create only. contactBalancePostings and invoiceReminderAssociations create/update stay 405-blocked offline.
- UI all red; bulk 92 empty-tool red; no live token; no UI credentials.

## Verification

- Official docs retain ETag `hsisik4g9p3603`, MD5 `c2efda0ee4cf9cf200e14910c5fc6996`, and a 147934-byte body (research57 reconfirm).
- Latest unauth probes: contactBalancePayments POST/PUT **401**, DELETE **405**; invoiceLateFees same; invoiceReminders POST **401**, PUT/DELETE **405**; contactBalancePostings create/update/delete **405**; bankPayments and salesTaxPayments unchanged.
- Freeze MD5 `3c49c4f41f3d9485a177a6ee643db412` unchanged for Wave-5l.
- Coverage honesty on root: implemented/contract_tested **170**, live/vision **0**, `complete: false`.

## Review decisions (authoritative)

- Wave-5g through Wave-5k freeze/product: **ACCEPT** offline where recorded.
- Wave-5l freeze page: **ACCEPT** offline.
- Wave-5l product on root offline implementation: present; independent product review **not accepted** yet.
- Wave-5m freeze: **not accepted** (child authoring; research package only on root).
- Wave-5m product: **not accepted** (blocked on freeze ACCEPT).
- Overall completeness: **FAIL**.

## Open coverage work

1. Complete Wave-5l product independent review ACCEPT (parallel; optional for freeze path).
2. Land Wave-5m freeze page + freeze ACCEPT; product four tools for contactBalancePayments (**+2 → 172**, tools **250**).
3. Later freezes: invoiceLateFees create+update; invoiceReminders create only; remaining blocked CUD (405 or reference data).
4. Bulk 92, UI/auth/vision, live CUD still open.
5. Inventory cleanup text debt on resources that still say “delete dedicated test resource” where singular DELETE is 405.

## Evidence boundaries

- Official API fingerprint: etag `hsisik4g9p3603`, MD5 `c2efda0ee4cf9cf200e14910c5fc6996`.
- contactBalancePayments Supports omits singular delete; unauth DELETE **405**.
- bankPayment “Posting a payment” sample is not the contactBalancePayment request schema.
- Research does not green coverage.

## References

- Current research: `.fractal/main.billy_complete/tmp/grok-research.md` (Wave-5m product-ready, research57)
- Wave-5l freeze ACCEPT: `wiki/wave_fivel_freeze_independent_review.md`
- Wave-5l freeze contract: `wiki/wave_fivel_ticketed_writes_contract.md`
- Wave-5k product ACCEPT: `wiki/wave_fivek_product_independent_review.md`
- Offline probe rules: `wiki/offline_write_probe_rules.md`
- Product template: `src/billy_mcp/api/sales_tax_payment_writes.py`
