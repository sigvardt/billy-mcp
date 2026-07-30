---
name: state
desc: Current node state, verified review decisions, and open qualification work.
tags: [billy, coverage, review]
sources:
  - docs/superpowers/specs/2026-07-28-billy-mcp-complete-design.md
  - https://www.billy.dk/api/
created: 2026-07-30T06:20:59Z
updated: 2026-07-30T11:08:30Z
---

# state

## Current state

- Wave-5c through Wave-5n write modules are merged into root; one shared confirmation store and write protocol.
- Root registry **254** `api_*` tools. Offline coverage **174** implemented + contract_tested. Live/vision **0**. `complete: false`.
- Wave-5n freeze ACCEPT and product ACCEPT offline remain valid.
- Wave-5o freeze page is **on root**: `wiki/wave_fiveo_ticketed_writes_contract.md` (MD5 `6fec5754cc76c4a07b344021cbc3c36b`).
- Wave-5o freeze independent review: **ACCEPT**.
- Wave-5o product-ready research65: **ACCEPT as research**.
- Wave-5o product-implementation handoff research66: **ACCEPT as research** (`wiki/wave_fiveo_product_implementation_handoff_independent_review.md`).
- Wave-5o product tools remain **absent** on root create-row red; product child may be active separately.
- Official API contract stable (review66 HTML byte-identical to research66; ETag `wcw4x9hqvu3603`, MD5 `8b94b0135c91fd15fe54ea33e088a4be`).
- UI all red; bulk 92 empty-tool red; no live token; no UI credentials.

## Verification

- Docs review66: ETag `wcw4x9hqvu3603`, MD5 `8b94b0135c91fd15fe54ea33e088a4be`, body 147934; equals research66.
- Unauth probes: invoiceReminders POST 401; PUT/DELETE 405; bulk DELETE 405; associations POST/PUT 405.
- Inventory create still red; cleanup still incorrect delete wording until product greening.
- Coverage honesty: 174/174/0/0; complete false; zero UI greens.
- No false greens from research66 or review66.
- Commit under review (`3ffe2e2`) had no `src/**` or `coverage/**` changes.
- Root review verification passes: 205 files formatted, Ruff and Pyright clean,
  coverage inventory/policy checks clean, and 1094 non-live tests passed.

## Review decisions (authoritative)

- Wave-5m freeze/product: **ACCEPT** offline.
- Wave-5n freeze: **ACCEPT**.
- Wave-5n product: **ACCEPT** offline for singular create/update only.
- Wave-5o freeze-ready / freeze authoring / product-ready research: **ACCEPT as research**.
- Wave-5o freeze page independent review: **ACCEPT**.
- Wave-5o product-implementation handoff research66: **ACCEPT as research** (review66).
- Wave-5o product: **not accepted** (unimplemented on root).
- Overall completeness: **FAIL**.

## Open coverage work

1. Codex Power product leaf: two-tool invoice-reminder create slice; green one row after tests.
2. Independent Grok product review after product merge.
3. Later: organizations create+update; users update-only; salesTaxReturns update-only; associations delete-only candidate.
4. Bulk 92, UI/auth/vision, live CUD still open.

## Evidence boundaries

- Research ACCEPT is not product ACCEPT.
- Offline 401 permits only the approved create product slice; 405 excludes update/delete offline.
- Product may implement only the two ticketed create tools authorised by the accepted root freeze review.
- Do not green coverage from research or review.

## References

- Handoff review: `wiki/wave_fiveo_product_implementation_handoff_independent_review.md`
- Review body: `.fractal/main.billy_complete/tmp/grok-review.md` (review66)
- Research: `.fractal/main.billy_complete/tmp/grok-research.md` (research66)
- Freeze review: `wiki/wave_fiveo_freeze_independent_review.md`
- Freeze page: `wiki/wave_fiveo_ticketed_writes_contract.md`
- Probe rules: `wiki/offline_write_probe_rules.md`
