---
name: state
desc: Current node state, verified review decisions, and open qualification work.
tags: [billy, coverage, review]
sources:
  - docs/superpowers/specs/2026-07-28-billy-mcp-complete-design.md
  - https://www.billy.dk/api/
created: 2026-07-30T06:20:59Z
updated: 2026-07-30T09:18:00Z
---

# state

## Current state

- Wave-5c through Wave-5m write modules are merged into root; one shared confirmation store and write protocol.
- Root registry **250** `api_*` tools. Offline coverage **172** implemented + contract_tested. Live/vision **0**. `complete: false`.
- Wave-5m freeze ACCEPT and product ACCEPT offline remain valid (19 focused tests still pass).
- Wave-5n freeze page on root: `wiki/wave_fiven_ticketed_writes_contract.md` (MD5 `93e6d266d1718fa517ff645b3ca213ce`). Freeze leaf completed.
- Wave-5n freeze independent review child active: `wave5n_freeze_independent_review` (freeze ACCEPT not yet recorded on root).
- Research61 product-ready package **ACCEPT as research** (review61). Product still blocked until freeze ACCEPT.
- Official plain API contract stable; HTTP docs ETag/MD5 access churn continues. Inventory still pins prior MD5.
- UI all red; bulk 92 empty-tool red; no live token; no UI credentials.

## Verification

- Docs review61: ETag `wcw4x9hqvu3603`, MD5 `8b94b0135c91fd15fe54ea33e088a4be`, body 147934; plain equals research61.
- Unauth probes with `{}` body: invoiceLateFees POST/PUT 401; singular DELETE and bulk DELETE 405.
- No `invoice_late_fee_writes.py`; only get/list late-fee tools.
- Coverage honesty: no false greens; complete false.
- Focused Wave-5m product tests: 19 passed.

## Review decisions (authoritative)

- Wave-5m freeze/product: **ACCEPT** offline.
- Wave-5n freeze-ready research: **ACCEPT as research**.
- Wave-5n product-ready research: **ACCEPT as research**
  (`wiki/wave_fiven_product_ready_research_independent_review.md`,
  `tmp/grok-review.md` review61).
- Wave-5n freeze page: present and contract-sound; freeze **ACCEPT pending** on independent freeze review child.
- Wave-5n product: not started; blocked until freeze ACCEPT.
- Overall completeness: **FAIL**.

## Open coverage work

1. Finish freeze independent review ACCEPT; then product leaf (four tools).
2. Product-time: fix `api.invoiceLateFees.create` cleanup wording (singular DELETE unsupported).
3. Later: invoiceReminders create-only; associations create/update blocked offline (405).
4. Bulk 92, UI/auth/vision, live CUD still open.

## Evidence boundaries

- Plain contract is stable; HTTP access fingerprint is not the durable contract key.
- Offline 401 opens freeze/product; 405 overrides Supports for delete/bulk-delete offline greening.
- Product-ready research ACCEPT is not freeze ACCEPT or product ACCEPT.
- POST/PUT probes require a JSON object body (`{}` minimum) to reach the auth gate.

## References

- Review: `.fractal/main.billy_complete/tmp/grok-review.md` (review61)
- Research: `.fractal/main.billy_complete/tmp/grok-research.md` (research61)
- Product-ready research ACCEPT wiki: `wiki/wave_fiven_product_ready_research_independent_review.md`
- Freeze page: `wiki/wave_fiven_ticketed_writes_contract.md`
- Wave-5m product ACCEPT: `wiki/wave_fivem_product_independent_review.md`
- Probe rules: `wiki/offline_write_probe_rules.md`
