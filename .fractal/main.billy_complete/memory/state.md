---
name: state
desc: Current node state, verified review decisions, and open qualification work.
tags: [billy, coverage, review]
sources:
  - docs/superpowers/specs/2026-07-28-billy-mcp-complete-design.md
  - https://www.billy.dk/api/
created: 2026-07-30T11:33:24Z
updated: 2026-07-30T12:52:30Z
---

# state

## Current state

- Wave-5c through Wave-5p write modules are merged into root; one shared confirmation store and write protocol.
- Root registry offline coverage **177** implemented + contract_tested. Live/vision **0**. `complete: false`.
- Wave-5o freeze, product, and product independent review are **ACCEPT**.
- Wave-5p freeze, product, and product independent review are **ACCEPT** (organizations create+update, four tools).
- Wave-5q freeze page is **on root** (`wiki/wave_fiveq_ticketed_writes_contract.md` MD5 `c53717468aff0406799feca225a00728`). Freeze independent review is **not landed**.
- Wave-5q freeze-ready research and research independent review are **ACCEPT as research**.
- Wave-5q **product-ready research** package is written (research71): `tmp/grok-research.md` and `wiki/wave_fiveq_users_product_ready_research.md`. Not freeze ACCEPT, not product.
- Research71 docs MD5 `8b94b0135c91fd15fe54ea33e088a4be` (ETag `wcw4x9hqvu3603`, 147934 bytes) reconfirmed byte-identical to research70; users PUT 401 / POST+DELETE 405 unchanged.
- UI all red (339); bulk 92 empty-tool red; no live token; no UI credentials.

## Verification

- Research71 independent docs re-fetch and unauth probes match research70 (users PUT 401; POST/DELETE 405).
- Coverage honesty: 177/177/0/0; complete false; zero UI greens; zero bulk greens; users update still red.
- Organizations product ACCEPT on root; create cleanup uses fail-closed non-delete wording.

## Review decisions (authoritative)

- Wave-5m freeze/product: **ACCEPT** offline.
- Wave-5n freeze/product: **ACCEPT** offline for singular create/update only.
- Wave-5o freeze/product: **ACCEPT** offline.
- Wave-5p freeze: **ACCEPT**.
- Wave-5p product: **ACCEPT** offline.
- Wave-5q users freeze-ready research: **ACCEPT as research**.
- Wave-5q freeze page: on root; **freeze independent ACCEPT not yet recorded**.
- Wave-5q product-ready research71: packaged; **independent research ACCEPT not yet recorded**.
- Overall completeness: **FAIL**.

## Open coverage work

1. Independent freeze ACCEPT for Wave-5q users freeze page.
2. Optional independent ACCEPT as research for Wave-5q product-ready package.
3. Wave-5q product for users update only after freeze ACCEPT (+1 → 178 offline).
4. Wave-5r: salesTaxReturns update-only freeze/product.
5. Later research: transactions create/update, specials, method-closed Supports honesty pass.
6. invoiceReminderAssociations delete blocked offline until live cleanup proof.
7. Bulk 92, UI/auth/vision, live CUD still open.

## Evidence boundaries

- Research ACCEPT is not freeze ACCEPT, product ACCEPT, or live qualification.
- Freeze page on root is not freeze independent ACCEPT.
- Organizations singular DELETE is 405: never claim delete cleanup offline.
- Users singular create/delete are 405: product is update-only.
- Do not green coverage from research or freeze alone.
- Unauth 405 overrides Supports create/update text for geo/reference rows.

## References

- Research71 brief: `.fractal/main.billy_complete/tmp/grok-research.md`
- Wave-5q product-ready wiki: `wiki/wave_fiveq_users_product_ready_research.md`
- Wave-5q freeze page: `wiki/wave_fiveq_ticketed_writes_contract.md`
- Wave-5q freeze-ready wiki: `wiki/wave_fiveq_users_freeze_ready_research.md`
- Wave-5p product acceptance: `wiki/wave_fivep_product_independent_review.md`
- Probe rules: `wiki/offline_write_probe_rules.md`
