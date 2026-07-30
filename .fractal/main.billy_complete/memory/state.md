---
name: state
desc: Current node state, verified review decisions, and open qualification work.
tags: [billy, coverage, review]
sources:
  - docs/superpowers/specs/2026-07-28-billy-mcp-complete-design.md
  - https://www.billy.dk/api/
created: 2026-07-30T06:20:59Z
updated: 2026-07-30T09:34:00Z
---

# state

## Current state

- Wave-5c through Wave-5m write modules are merged into root; one shared confirmation store and write protocol.
- Root registry **250** `api_*` tools. Offline coverage **172** implemented + contract_tested. Live/vision **0**. `complete: false`.
- Wave-5m freeze ACCEPT and product ACCEPT offline remain valid.
- Wave-5n freeze page on root: `wiki/wave_fiven_ticketed_writes_contract.md` (MD5 `93e6d266d1718fa517ff645b3ca213ce`).
- Wave-5n freeze independent review: **ACCEPT**.
- Wave-5n product-ready research: **ACCEPT as research**.
- Wave-5n product-implementation research (research62): **ACCEPT as research** (review62).
- Wave-5n product: **not on root**; child `wave5n_invoice_late_fee_product` active (codex-power).
- Official plain API contract stable (review62 == research62; ETag `wcw4x9hqvu3603`, MD5 `8b94b0135c91fd15fe54ea33e088a4be`).
- UI all red; bulk 92 empty-tool red; no live token; no UI credentials.

## Verification

- Docs review62: ETag `wcw4x9hqvu3603`, MD5 `8b94b0135c91fd15fe54ea33e088a4be`, body 147934; plain equals research62.
- Unauth probes with `{}` body: invoiceLateFees POST/PUT 401; singular DELETE and bulk DELETE 405.
- No `invoice_late_fee_writes.py` on root; only get/list late-fee tools.
- Coverage honesty: 172/172/0/0; zero false greens; complete false.
- Freeze MD5 match; freeze ACCEPT still valid.

## Review decisions (authoritative)

- Wave-5m freeze/product: **ACCEPT** offline.
- Wave-5n freeze: **ACCEPT**.
- Wave-5n product-ready research: **ACCEPT as research**.
- Wave-5n product-implementation research: **ACCEPT as research** (review62).
- Wave-5n product: **not accepted** (not present on root).
- Overall completeness: **FAIL**.

## Open coverage work

1. Finish product child; merge four tools; green create/update only; fix create cleanup wording; 174 offline / 254 tools.
2. Independent product review after merge.
3. Later: invoiceReminders create-only (Wave-5o); associations create/update blocked offline (405).
4. Bulk 92, UI/auth/vision, live CUD still open.

## Evidence boundaries

- Plain contract is stable; HTTP access fingerprint is not the durable contract key.
- Research ACCEPT is not product ACCEPT.
- Offline 401 opens product; 405 excludes singular and bulk delete offline greening.
- POST/PUT probes require a JSON object body (`{}` minimum) to reach the auth gate.

## References

- Review: `.fractal/main.billy_complete/tmp/grok-review.md` (review62)
- Research: `.fractal/main.billy_complete/tmp/grok-research.md` (research62)
- Research ACCEPT wiki: `wiki/wave_fiven_product_implementation_research_independent_review.md`
- Freeze ACCEPT: `wiki/wave_fiven_freeze_independent_review.md`
- Freeze page: `wiki/wave_fiven_ticketed_writes_contract.md`
- Probe rules: `wiki/offline_write_probe_rules.md`
