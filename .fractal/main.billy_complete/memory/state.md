---
name: state
desc: Current node state, verified review decisions, and open qualification work.
tags: [billy, coverage, review]
sources:
  - docs/superpowers/specs/2026-07-28-billy-mcp-complete-design.md
  - https://www.billy.dk/api/
created: 2026-07-30T06:20:59Z
updated: 2026-07-30T10:47:16Z
---

# state

## Current state

- Wave-5c through Wave-5n write modules are merged into root; one shared confirmation store and write protocol.
- Root registry **254** `api_*` tools. Offline coverage **174** implemented + contract_tested. Live/vision **0**. `complete: false`.
- Wave-5n freeze ACCEPT and product ACCEPT offline remain valid.
- Wave-5o freeze page is **on root**: `wiki/wave_fiveo_ticketed_writes_contract.md` (MD5 `6fec5754cc76c4a07b344021cbc3c36b`).
- Wave-5o freeze authoring research: **ACCEPT as research** (`wiki/wave_fiveo_freeze_authoring_research_independent_review.md`).
- Wave-5o product-ready research65: **ACCEPT as research** (`wiki/wave_fiveo_product_ready_research_independent_review.md`).
- Wave-5o freeze independent review: **not accepted yet** (active child `wave5o_freeze_review`). Product blocked until freeze ACCEPT.
- Official API contract stable (review65 HTML byte-identical to research65; ETag `wcw4x9hqvu3603`, MD5 `8b94b0135c91fd15fe54ea33e088a4be`).
- UI all red; bulk 92 empty-tool red; no live token; no UI credentials; no product write module for reminders.

## Verification

- Docs review65: ETag `wcw4x9hqvu3603`, MD5 `8b94b0135c91fd15fe54ea33e088a4be`, body 147934; equals research65.
- Unauth probes: invoiceReminders POST 401; PUT/DELETE 405; bulk DELETE 405; associations POST/PUT 405.
- Inventory create still red; cleanup still incorrect delete wording until product greening.
- Coverage honesty: 174/174/0/0; complete false; zero UI greens.
- No false greens from research65 or freeze page merge.
- Root non-live verification is green: 203 files formatted, Ruff/Pyright clean,
  inventory checks 305 API/339 UI, and 1094 tests passed.

## Review decisions (authoritative)

- Wave-5m freeze/product: **ACCEPT** offline.
- Wave-5n freeze: **ACCEPT**.
- Wave-5n product: **ACCEPT** offline for singular create/update only.
- Wave-5o freeze-ready research: **ACCEPT as research**.
- Wave-5o freeze authoring research: **ACCEPT as research**.
- Wave-5o product-ready research65: **ACCEPT as research** (review65).
- Wave-5o freeze page independent review: reviewer reports **ACCEPT**; its
  committed review record and root merge remain pending.
- Wave-5o product: **not accepted**.
- Overall completeness: **FAIL**.

## Open coverage work

1. Merge the accepted freeze independent-review record into root; then the
   bounded two-tool product slice may use the research65 package.
2. Later: organizations create+update; users update-only; salesTaxReturns update-only (opaque/cautious); associations delete-only candidate.
3. Bulk 92, UI/auth/vision, live CUD still open.

## Evidence boundaries

- Research ACCEPT is not freeze ACCEPT or product ACCEPT.
- Offline 401 opens create product only after freeze ACCEPT; 405 excludes update/delete offline.
- Product must not start until freeze independent review ACCEPT of the root freeze page.

## References

- Review: `.fractal/main.billy_complete/tmp/grok-review.md` (review65)
- Research: `.fractal/main.billy_complete/tmp/grok-research.md` (research65)
- Product-ready research ACCEPT: `wiki/wave_fiveo_product_ready_research_independent_review.md`
- Freeze page (root): `wiki/wave_fiveo_ticketed_writes_contract.md`
- Freeze authoring research ACCEPT: `wiki/wave_fiveo_freeze_authoring_research_independent_review.md`
- Probe rules: `wiki/offline_write_probe_rules.md`
