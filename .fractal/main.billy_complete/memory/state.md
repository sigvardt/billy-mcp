---
name: state
desc: Current node state, verified review decisions, and open qualification work.
tags: [billy, coverage, review]
sources:
  - docs/superpowers/specs/2026-07-28-billy-mcp-complete-design.md
  - https://www.billy.dk/api/
created: 2026-07-30T06:20:59Z
updated: 2026-07-30T08:30:00Z
---

# state

## Current state

- Wave-5c through Wave-5m write modules are merged into root; root registration uses the one shared `ConfirmationStore` and `WriteProtocolService`.
- Root registry **250** `api_*` tools. Offline coverage **172** implemented + contract_tested. Live/vision still 0. `complete: false`.
- Wave-5k freeze and product: ACCEPT offline.
- Wave-5l freeze ACCEPT: `wiki/wave_fivel_freeze_independent_review.md`.
- Wave-5l product on root; Codex fallback product ACCEPT recorded.
- Wave-5m freeze ACCEPT: `wiki/wave_fivem_freeze_independent_review.md` (contract MD5 `fcb0e58742c8abc8ca9078859bb74eb8`).
- Wave-5m product on root: `contact_balance_payment_writes.py` + tests; merge `8297713`.
- Wave-5m product independent review: **ACCEPT** offline at `wiki/wave_fivem_product_independent_review.md` and `tmp/grok-review.md` (review59).
- Research59: Wave-5n `invoiceLateFees` freeze-ready package **ACCEPT as research** only. Freeze page not yet authored.
- bankPayments / salesTaxPayments / contactBalancePayments create+update offline-qualified; deletes 405 red where applicable; bulk ambiguous empty.
- UI all red; bulk 92 empty-tool red; no live token; no UI credentials.

## Verification

- Official docs retain ETag `hsisik4g9p3603`, MD5 `c2efda0ee4cf9cf200e14910c5fc6996`, body 147934 (review59 reconfirm).
- Unauth contactBalancePayments POST/PUT **401**, DELETE **405** reconfirmed.
- Unauth invoiceLateFees POST/PUT **401**, singular DELETE **405**, bulk DELETE **405** reconfirmed.
- Focused product suite: 19 passed (`tests/api/test_contact_balance_payment_writes.py`).
- Coverage honesty: implemented/contract_tested **172**, live/vision **0**, `complete: false`. No false greens. No bulk greened. Create cleanup does not claim singular delete.

## Review decisions (authoritative)

- Wave-5g through Wave-5k freeze/product: **ACCEPT** offline where recorded.
- Wave-5l freeze page: **ACCEPT** offline.
- Wave-5l product: Codex fallback ACCEPT recorded.
- Wave-5m freeze page: **ACCEPT** offline.
- Wave-5m product: **ACCEPT** offline (review59).
- Research59 Wave-5n freeze-ready: **ACCEPT as research** only.
- Wave-5n freeze page: not present; no ACCEPT.
- Overall completeness: **FAIL**.

## Open coverage work

1. Author Wave-5n freeze for invoiceLateFees create+update (research59 package); then freeze review and product.
2. Later: invoiceReminders create only; associations create/update stay blocked offline (405).
3. Bulk 92, UI/auth/vision, live CUD still open.

## Evidence boundaries

- Official API fingerprint: etag `hsisik4g9p3603`, MD5 `c2efda0ee4cf9cf200e14910c5fc6996`.
- contactBalancePayments / invoiceLateFees Supports omit singular delete; unauth DELETE **405**.
- invoiceLateFees bulk DELETE unauth **405** overrides Supports bulk delete for offline greening.
- Product offline ACCEPT is not live/UI/vision ACCEPT.

## References

- Review: `.fractal/main.billy_complete/tmp/grok-review.md` (review59)
- Product ACCEPT wiki: `wiki/wave_fivem_product_independent_review.md`
- Research: `.fractal/main.billy_complete/tmp/grok-research.md` (research59)
- Wave-5m freeze: `wiki/wave_fivem_ticketed_writes_contract.md`
- Offline probe rules: `wiki/offline_write_probe_rules.md`
