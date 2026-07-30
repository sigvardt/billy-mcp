---
name: state
desc: Current node state, verified review decisions, and open qualification work.
tags: [billy, coverage, review]
sources:
  - docs/superpowers/specs/2026-07-28-billy-mcp-complete-design.md
  - https://www.billy.dk/api/
created: 2026-07-30T06:20:59Z
updated: 2026-07-30T10:10:00Z
---

# state

## Current state

- Wave-5c through Wave-5n write modules are merged into root; one shared confirmation store and write protocol.
- Root registry **254** `api_*` tools. Offline coverage **174** implemented + contract_tested. Live/vision **0**. `complete: false`.
- Wave-5n freeze ACCEPT and product ACCEPT offline remain valid.
- Wave-5n freeze page: `wiki/wave_fiven_ticketed_writes_contract.md` (MD5 `93e6d266d1718fa517ff645b3ca213ce`).
- Wave-5n product independent review: **ACCEPT** offline (`wiki/wave_fiven_product_independent_review.md`).
- Wave-5o freeze-ready research: **ACCEPT as research** (research63 + review63).
- Wave-5o freeze authoring package: **research64** reconfirmed docs byte-identical and probes identical; Wave-5n product ACCEPT opens freeze-page authoring. Freeze page **absent**.
- Official API contract stable (research64 HTML byte-identical to research63; ETag `wcw4x9hqvu3603`, MD5 `8b94b0135c91fd15fe54ea33e088a4be`).
- UI all red; bulk 92 empty-tool red; no live token; no UI credentials.

## Verification

- Docs research64: ETag `wcw4x9hqvu3603`, MD5 `8b94b0135c91fd15fe54ea33e088a4be`, body 147934; HTML equals research63.
- Unauth probes with `{}` body: invoiceReminders POST 401; PUT/DELETE 405; bulk DELETE 405. invoiceLateFees POST/PUT 401; singular/bulk DELETE 405. associations POST/PUT 405; DELETE 200 meta-only; DELETE without ids 400 `INVALID_DELETE_ID_ARRAY`.
- Root late-fee writes module present and registered; reminders create inventory still red with reserved preview tool name; cleanup still says `delete dedicated test resource` (fix only when product greens).
- Coverage honesty: 174/174/0/0; complete false; zero UI greens.
- Freeze MD5 match for Wave-5n; product ACCEPT still valid.

## Review decisions (authoritative)

- Wave-5m freeze/product: **ACCEPT** offline.
- Wave-5n freeze: **ACCEPT**.
- Wave-5n product: **ACCEPT** offline for singular create/update only.
- Wave-5o freeze-ready research: **ACCEPT as research** (review63).
- Wave-5o freeze authoring package research64: ready for Codex Power wiki-only freeze page (not yet freeze ACCEPT).
- Wave-5o freeze page / product: **not accepted**.
- Overall completeness: **FAIL**.

## Open coverage work

1. Author `wiki/wave_fiveo_ticketed_writes_contract.md` from research64 freeze-authoring package (create-only two tools); then freeze independent review; then two-tool product.
2. Later: organizations create+update; users update-only; salesTaxReturns update-only (opaque/cautious); associations delete-only candidate.
3. Bulk 92, UI/auth/vision, live CUD still open.

## Evidence boundaries

- Research ACCEPT is not freeze ACCEPT or product ACCEPT.
- The Wave-5n product ACCEPT is offline only; it does not green live, UI, vision, bulk, delete, or completeness states.
- Offline 401 opens freeze after product ACCEPT; 405 excludes methods offline.
- POST/PUT probes require a JSON object body (`{}` minimum) to reach the auth gate.
- Freeze authoring must not green inventory or ship product code.

## References

- Research: `.fractal/main.billy_complete/tmp/grok-research.md` (research64)
- Probes: `.fractal/main.billy_complete/tmp/write-probes-research64.json`
- Prior research ACCEPT wiki: `wiki/wave_fiveo_freeze_ready_research_independent_review.md`
- Product ACCEPT: `wiki/wave_fiven_product_independent_review.md`
- Freeze ACCEPT (Wave-5n): `wiki/wave_fiven_freeze_independent_review.md`
- Freeze page (Wave-5n): `wiki/wave_fiven_ticketed_writes_contract.md`
- Probe rules: `wiki/offline_write_probe_rules.md`
