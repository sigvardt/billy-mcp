---
name: state
desc: Current node state, verified review decisions, and open qualification work.
tags: [billy, coverage, review]
sources:
  - docs/superpowers/specs/2026-07-28-billy-mcp-complete-design.md
  - https://www.billy.dk/api/
created: 2026-07-30T06:20:59Z
updated: 2026-07-30T09:56:34Z
---

# state

## Current state

- Wave-5c through Wave-5m write modules are merged into root; one shared confirmation store and write protocol.
- Root registry **254** `api_*` tools. Offline coverage **174** implemented + contract_tested. Live/vision **0**. `complete: false`.
- Wave-5m freeze ACCEPT and product ACCEPT offline remain valid.
- Wave-5n freeze page on root: `wiki/wave_fiven_ticketed_writes_contract.md` (MD5 `93e6d266d1718fa517ff645b3ca213ce`).
- Wave-5n freeze independent review: **ACCEPT**.
- Wave-5n product source merged on root (four create/update tools; create cleanup wording correct; bulk empty-tool red).
- Wave-5n product independent review: **pending** (active child `wave5n_product_review_grok`; no product ACCEPT wiki yet).
- Wave-5o freeze-ready research (research63): **ACCEPT as research** (review63).
- Official API contract stable (review63 HTML byte-identical to research63; ETag `wcw4x9hqvu3603`, MD5 `8b94b0135c91fd15fe54ea33e088a4be`).
- UI all red; bulk 92 empty-tool red; no live token; no UI credentials.

## Verification

- Docs review63: ETag `wcw4x9hqvu3603`, MD5 `8b94b0135c91fd15fe54ea33e088a4be`, body 147934; HTML equals research63.
- Unauth probes with `{}` body: invoiceReminders POST 401; PUT/DELETE 405; bulk DELETE 405. invoiceLateFees POST/PUT 401; singular/bulk DELETE 405. associations POST/PUT 405; DELETE 200 meta-only; DELETE without ids 400 `INVALID_DELETE_ID_ARRAY`.
- Root late-fee writes module present and registered; reminders create inventory still red with reserved preview tool name.
- Coverage honesty: 174/174/0/0; complete false; zero UI greens.
- Freeze MD5 match; freeze ACCEPT still valid.

## Review decisions (authoritative)

- Wave-5m freeze/product: **ACCEPT** offline.
- Wave-5n freeze: **ACCEPT**.
- Wave-5n product-ready research: **ACCEPT as research**.
- Wave-5n product-implementation research: **ACCEPT as research** (review62).
- Wave-5n product: **not accepted** (merged on root; product review pending).
- Wave-5o freeze-ready research: **ACCEPT as research** (review63).
- Wave-5o freeze page / product: **not accepted**.
- Overall completeness: **FAIL**.

## Open coverage work

1. Complete Wave-5n product independent review ACCEPT on root.
2. After product ACCEPT: author Wave-5o freeze for invoiceReminders create-only from research63 package; freeze review; two-tool product.
3. Later: organizations create+update; users update-only; salesTaxReturns update-only (opaque/cautious); associations delete-only candidate.
4. Bulk 92, UI/auth/vision, live CUD still open.

## Evidence boundaries

- Research ACCEPT is not freeze ACCEPT or product ACCEPT.
- Product merge on root is not product ACCEPT.
- Offline 401 opens freeze after product ACCEPT; 405 excludes methods offline.
- POST/PUT probes require a JSON object body (`{}` minimum) to reach the auth gate.

## References

- Review: `.fractal/main.billy_complete/tmp/grok-review.md` (review63)
- Research: `.fractal/main.billy_complete/tmp/grok-research.md` (research63)
- Research ACCEPT wiki: `wiki/wave_fiveo_freeze_ready_research_independent_review.md`
- Freeze ACCEPT: `wiki/wave_fiven_freeze_independent_review.md`
- Freeze page: `wiki/wave_fiven_ticketed_writes_contract.md`
- Probe rules: `wiki/offline_write_probe_rules.md`
