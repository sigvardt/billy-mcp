---
name: state
desc: Current node state, verified review decisions, and open qualification work.
tags: [billy, coverage, review]
sources:
  - docs/superpowers/specs/2026-07-28-billy-mcp-complete-design.md
  - https://www.billy.dk/api/
created: 2026-07-30T06:20:59Z
updated: 2026-07-30T08:50:00Z
---

# state

## Current state

- Wave-5c through Wave-5m write modules are merged into root; one shared confirmation store and write protocol.
- Root registry **250** `api_*` tools. Offline coverage **172** implemented + contract_tested. Live/vision **0**. `complete: false`.
- Wave-5m freeze ACCEPT and product ACCEPT offline remain valid (19 focused tests pass).
- Cited official research and independent review: Wave-5n freeze-ready package
  **ACCEPT as research**.
- Wave-5n freeze page not on root; child `wave5n_invoice_late_fee_freeze` active for freeze page only.
- Official plain API contract stable; HTTP docs ETag/MD5 continues to churn (access metadata). Inventory still pins prior MD5.
- UI all red; bulk 92 empty-tool red; no live token; no UI credentials.

## Verification

- Independent revalidation: plain contract identical to the accepted research;
  unauthenticated invoiceLateFees POST/PUT return 401 and singular/bulk DELETE
  return 405.
- contactBalancePayments POST/PUT 401, DELETE 405 reconfirmed.
- Coverage honesty: no false greens; bulk empty; complete false.
- No `invoice_late_fee_writes.py`; no late-fee write registration.
- Root offline verification passes: 19 focused contact-balance-payment tests and
  the complete 1,075-test suite; formatting, lint, typing, inventory, and
  repository-policy checks also pass.

## Review decisions (authoritative)

- Wave-5m freeze/product: **ACCEPT** offline.
- Wave-5n freeze-ready research: **ACCEPT as research**
  (`wiki/wave_fiven_freeze_ready_research_independent_review.md`,
  `tmp/grok-review.md`). The review found no current-root repair.
- Wave-5n freeze page: not present; no freeze ACCEPT.
- Wave-5n product: not started; blocked until freeze ACCEPT.
- Overall completeness: **FAIL**.

## Open coverage work

1. Finish/merge Wave-5n freeze page; independent freeze review; then product.
2. Product-time: fix `api.invoiceLateFees.create` cleanup wording (singular DELETE unsupported).
3. Later: invoiceReminders create-only; associations create/update blocked offline (405).
4. Bulk 92, UI/auth/vision, live CUD still open.

## Evidence boundaries

- Plain contract is stable across the research and its revalidation; an HTTP
  access fingerprint is not the durable contract key.
- Offline 401 opens freeze; 405 overrides Supports for delete/bulk-delete offline greening.
- Offline product ACCEPT is not live/UI/vision ACCEPT.

## References

- Review: `.fractal/main.billy_complete/tmp/grok-review.md` (review60)
- Research: `.fractal/main.billy_complete/tmp/grok-research.md` (research60)
- Research ACCEPT wiki: `wiki/wave_fiven_freeze_ready_research_independent_review.md`
- Wave-5m product ACCEPT: `wiki/wave_fivem_product_independent_review.md`
- Probe rules: `wiki/offline_write_probe_rules.md`
