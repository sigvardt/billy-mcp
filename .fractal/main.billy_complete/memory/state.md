---
name: state
desc: Current node state, verified review decisions, and open qualification work.
tags: [billy, coverage, review]
sources:
  - docs/superpowers/specs/2026-07-28-billy-mcp-complete-design.md
  - https://www.billy.dk/api/
created: 2026-07-30T06:20:59Z
updated: 2026-07-30T09:10:00Z
---

# state

## Current state

- Wave-5c through Wave-5m write modules are merged into root; one shared confirmation store and write protocol.
- Root registry **250** `api_*` tools. Offline coverage **172** implemented + contract_tested. Live/vision **0**. `complete: false`.
- Wave-5m freeze ACCEPT and product ACCEPT offline remain valid.
- Wave-5n freeze page is on root: `wiki/wave_fiven_ticketed_writes_contract.md` (MD5 `93e6d266d1718fa517ff645b3ca213ce`). Child `wave5n_invoice_late_fee_freeze` finishing freeze authoring.
- Wave-5n freeze independent review not yet ACCEPT. Product blocked until freeze ACCEPT.
- Research61 product-ready package written for singular `invoiceLateFees` create+update (four tools after freeze ACCEPT).
- Official plain API contract stable; HTTP docs ETag/MD5 continues to churn (access metadata). Inventory still pins prior MD5.
- UI all red; bulk 92 empty-tool red; no live token; no UI credentials.

## Verification

- Docs access research61: ETag `wcw4x9hqvu3603`, MD5 `8b94b0135c91fd15fe54ea33e088a4be`, body 147934; plain contract matches prior lock after whitespace normalisation.
- Unauth probes with `{}` body: invoiceLateFees POST/PUT 401; singular DELETE and bulk DELETE 405. invoiceReminders POST 401; PUT/DELETE 405. associations create/update 405; DELETE missing-id 200.
- Empty/missing POST body returns 400 `INVALID_REQUEST_BODY` before auth; not a method-closed signal.
- No `invoice_late_fee_writes.py`; only get/list late-fee tools registered.
- Coverage honesty: no false greens; bulk empty; complete false.

## Review decisions (authoritative)

- Wave-5m freeze/product: **ACCEPT** offline.
- Wave-5n freeze-ready research: **ACCEPT as research**.
- Wave-5n freeze page: present; freeze independent review **pending**.
- Wave-5n product: not started; blocked until freeze ACCEPT.
- Overall completeness: **FAIL**.

## Open coverage work

1. Independent freeze review of Wave-5n page; then product leaf (four tools).
2. Product-time: fix `api.invoiceLateFees.create` cleanup wording (singular DELETE unsupported).
3. Later: invoiceReminders create-only; associations create/update blocked offline (405).
4. Bulk 92, UI/auth/vision, live CUD still open.

## Evidence boundaries

- Plain contract is stable across research60–61; HTTP access fingerprint is not the durable contract key.
- Offline 401 opens freeze/product; 405 overrides Supports for delete/bulk-delete offline greening.
- Offline product ACCEPT is not live/UI/vision ACCEPT.
- POST/PUT probes require a JSON object body (`{}` minimum) to reach the auth gate.

## References

- Research: `.fractal/main.billy_complete/tmp/grok-research.md` (research61)
- Freeze page: `wiki/wave_fiven_ticketed_writes_contract.md`
- Research ACCEPT wiki: `wiki/wave_fiven_freeze_ready_research_independent_review.md`
- Wave-5m product ACCEPT: `wiki/wave_fivem_product_independent_review.md`
- Probe rules: `wiki/offline_write_probe_rules.md`
