---
name: state
desc: Current node state, verified review decisions, and open qualification work.
tags: [billy, coverage, review]
sources:
  - docs/superpowers/specs/2026-07-28-billy-mcp-complete-design.md
  - https://www.billy.dk/api/
created: 2026-07-30T06:20:59Z
updated: 2026-07-30T09:26:00Z
---

# state

## Current state

- Wave-5c through Wave-5m write modules are merged into root; one shared confirmation store and write protocol.
- Root registry **250** `api_*` tools. Offline coverage **172** implemented + contract_tested. Live/vision **0**. `complete: false`.
- Wave-5m freeze ACCEPT and product ACCEPT offline remain valid.
- Wave-5n freeze page on root: `wiki/wave_fiven_ticketed_writes_contract.md` (MD5 `93e6d266d1718fa517ff645b3ca213ce`).
- Wave-5n freeze independent review: **ACCEPT** (`wiki/wave_fiven_freeze_independent_review.md`, merged at `40b1f1d`).
- Wave-5n product-ready research: **ACCEPT as research** (research61 + wiki IR).
- Research62 product-implementation package: freeze gate open; product module still absent; Codex Power product leaf is next.
- Official plain API contract stable (research62 norm-equal research61; ETag `wcw4x9hqvu3603`, MD5 `8b94b0135c91fd15fe54ea33e088a4be`). Inventory still pins prior MD5.
- UI all red; bulk 92 empty-tool red; no live token; no UI credentials.

## Verification

- Docs research62: ETag `wcw4x9hqvu3603`, MD5 `8b94b0135c91fd15fe54ea33e088a4be`, body 147934; plain equals research61.
- Unauth probes with `{}` body: invoiceLateFees POST/PUT 401; singular DELETE and bulk DELETE 405.
- No `invoice_late_fee_writes.py`; only get/list late-fee tools.
- Freeze ACCEPT page present; freeze MD5 match.
- Coverage honesty: no false greens; complete false.

## Review decisions (authoritative)

- Wave-5m freeze/product: **ACCEPT** offline.
- Wave-5n freeze-ready research: **ACCEPT as research**.
- Wave-5n product-ready research: **ACCEPT as research**.
- Wave-5n freeze page: **ACCEPT** (independent freeze review).
- Wave-5n product: **authorised**; not started.
- Overall completeness: **FAIL**.

## Open coverage work

1. Codex Power product leaf: four tools + greening create/update only (174 offline; cleanup wording fix).
2. Independent product review after product lands.
3. Later: invoiceReminders create-only (Wave-5o); associations create/update blocked offline (405).
4. Bulk 92, UI/auth/vision, live CUD still open.

## Evidence boundaries

- Plain contract is stable; HTTP access fingerprint is not the durable contract key.
- Offline 401 opens freeze/product; 405 overrides Supports for delete/bulk-delete offline greening.
- Freeze ACCEPT is the product gate; product ACCEPT is separate.
- POST/PUT probes require a JSON object body (`{}` minimum) to reach the auth gate.

## References

- Research: `.fractal/main.billy_complete/tmp/grok-research.md` (research62)
- Prior product-ready research: research61 + `wiki/wave_fiven_product_ready_research_independent_review.md`
- Freeze page: `wiki/wave_fiven_ticketed_writes_contract.md`
- Freeze ACCEPT: `wiki/wave_fiven_freeze_independent_review.md`
- Wave-5m product ACCEPT: `wiki/wave_fivem_product_independent_review.md`
- Probe rules: `wiki/offline_write_probe_rules.md`
