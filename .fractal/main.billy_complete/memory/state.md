---
name: state
desc: Current node state, verified review decisions, and open qualification work.
tags: [billy, coverage, review]
sources:
  - docs/superpowers/specs/2026-07-28-billy-mcp-complete-design.md
  - https://www.billy.dk/api/
created: 2026-07-30T06:20:59Z
updated: 2026-07-30T10:38:04Z
---

# state

## Current state

- Wave-5c through Wave-5n write modules are merged into root; one shared confirmation store and write protocol.
- Root registry **254** `api_*` tools. Offline coverage **174** implemented + contract_tested. Live/vision **0**. `complete: false`.
- Wave-5n freeze ACCEPT and product ACCEPT offline remain valid.
- Wave-5n freeze page: `wiki/wave_fiven_ticketed_writes_contract.md` (MD5 `93e6d266d1718fa517ff645b3ca213ce`).
- Wave-5n product independent review: **ACCEPT** offline (`wiki/wave_fiven_product_independent_review.md`).
- Wave-5o freeze-ready research: **ACCEPT as research** (research63 + review63).
- Wave-5o freeze authoring package research64: **ACCEPT as research** (review64). Durable: `wiki/wave_fiveo_freeze_authoring_research_independent_review.md`.
- Wave-5o product-ready research65: cited package only (docs byte-identical to research64; probes same). Brief: `.fractal/main.billy_complete/tmp/grok-research.md`.
- Wave-5o freeze page still **absent on root**. The completed `wave5o_invoice_reminder_freeze` child has committed the create-only page (MD5 `6fec5754cc76c4a07b344021cbc3c36b`). Root must merge it and regenerate the parent-owned `wiki/_index.md`; freeze independent review and product remain blocked until then.
- Official API contract stable (research65 HTML byte-identical to research64; ETag `wcw4x9hqvu3603`, MD5 `8b94b0135c91fd15fe54ea33e088a4be`).
- UI all red; bulk 92 empty-tool red; no live token; no UI credentials.

## Verification

- Docs research65: ETag `wcw4x9hqvu3603`, MD5 `8b94b0135c91fd15fe54ea33e088a4be`, body 147934; HTML equals research64.
- Unauth probes with `{}` body: invoiceReminders POST 401; PUT/DELETE 405; bulk DELETE 405. Empty body POST 400 INVALID_REQUEST_BODY. associations POST/PUT 405; DELETE 200 meta-only.
- Root late-fee writes present; reminders create inventory still red with reserved preview tool name; cleanup still `delete dedicated test resource` (fix only when product greens).
- Coverage honesty: 174/174/0/0; complete false; zero UI greens.
- No false greens from research65.

## Review decisions (authoritative)

- Wave-5m freeze/product: **ACCEPT** offline.
- Wave-5n freeze: **ACCEPT**.
- Wave-5n product: **ACCEPT** offline for singular create/update only.
- Wave-5o freeze-ready research: **ACCEPT as research** (review63).
- Wave-5o freeze authoring research64: **ACCEPT as research** (review64).
- Wave-5o product-ready research65: cited package only; it is not freeze or product acceptance.
- Wave-5o freeze page / product: **not accepted**.
- Overall completeness: **FAIL**.

## Open coverage work

1. Merge `wiki/wave_fiveo_ticketed_writes_contract.md` from the completed freeze child, regenerate the root index, then obtain independent freeze review before any two-tool product work using research65.
2. Later: organizations create+update; users update-only; salesTaxReturns update-only (opaque/cautious); associations delete-only candidate.
3. Bulk 92, UI/auth/vision, live CUD still open.

## Evidence boundaries

- Research ACCEPT is not freeze ACCEPT or product ACCEPT.
- The Wave-5n product ACCEPT is offline only; it does not green live, UI, vision, bulk, delete, or completeness states.
- Offline 401 opens freeze after product ACCEPT; 405 excludes methods offline.
- POST/PUT probes require a JSON object body (`{}` minimum) to reach the auth gate.
- Freeze authoring must not green inventory or ship product code.
- Product must not start until freeze independent review ACCEPT of the root freeze page.

## References

- Research: `.fractal/main.billy_complete/tmp/grok-research.md` (research65)
- Prior review: `.fractal/main.billy_complete/tmp/grok-review.md` (review64)
- Research ACCEPT wiki: `wiki/wave_fiveo_freeze_authoring_research_independent_review.md`
- Prior freeze-ready ACCEPT: `wiki/wave_fiveo_freeze_ready_research_independent_review.md`
- Product ACCEPT: `wiki/wave_fiven_product_independent_review.md`
- Freeze ACCEPT (Wave-5n): `wiki/wave_fiven_freeze_independent_review.md`
- Freeze page (Wave-5n): `wiki/wave_fiven_ticketed_writes_contract.md`
- Probe rules: `wiki/offline_write_probe_rules.md`
