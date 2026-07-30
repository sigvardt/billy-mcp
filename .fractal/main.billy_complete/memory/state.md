---
name: state
desc: Current node state, verified review decisions, and open qualification work.
tags: [billy, coverage, review]
sources:
  - docs/superpowers/specs/2026-07-28-billy-mcp-complete-design.md
  - https://www.billy.dk/api/
created: 2026-07-30T11:33:24Z
updated: 2026-07-30T12:41:00Z
---

# state

## Current state

- Wave-5c through Wave-5o write modules are merged into root; one shared confirmation store and write protocol.
- Root registry has **260** `api_*` tools. Offline coverage **177** implemented + contract_tested. Live/vision **0**. `complete: false`.
- Wave-5o freeze, product, and product independent review are **ACCEPT**.
- Wave-5p freeze page is **on root** (MD5 `2742eda7bafecd619aba5fa8ad0694c5`) and freeze independent review is **ACCEPT**.
- Wave-5p product-ready research and product-implementation handoff research are **ACCEPT as research**.
- Organizations create/update product is **integrated on root** with four typed ticketed tools and 19 passing contract tests. Offline product independent ACCEPT is **pending** (child `wave5p_product_review` active or subsequent full product IR).
- Research70 docs MD5 `8b94b0135c91fd15fe54ea33e088a4be` (ETag `wcw4x9hqvu3603`, 147934 bytes) reconfirmed by review70.
- Wave-5q users freeze-ready research package: **ACCEPT as research** (`wiki/wave_fiveq_users_freeze_ready_research_independent_review.md`). Not freeze ACCEPT and not product.
- Child `wave5q_users_freeze` may author freeze page. UI all red (339); bulk 92 empty-tool red; no live token; no UI credentials.

## Verification

- Review70 independent docs re-fetch and unauth probes match research70 (users PUT 401; POST/DELETE 405).
- Coverage honesty: 177/177/0/0; complete false; zero UI greens; zero bulk greens; users update still red.
- Organizations create cleanup inventory uses fail-closed non-delete wording.

## Review decisions (authoritative)

- Wave-5m freeze/product: **ACCEPT** offline.
- Wave-5n freeze/product: **ACCEPT** offline for singular create/update only.
- Wave-5o freeze/product: **ACCEPT** offline.
- Wave-5p freeze: **ACCEPT**.
- Wave-5p product-ready research: **ACCEPT as research**.
- Wave-5p product-implementation handoff research69: **ACCEPT as research**.
- Wave-5p product: integrated offline; **product independent ACCEPT not yet recorded** by review70 (delegated/pending).
- Wave-5q users freeze-ready research70: **ACCEPT as research** (review70).
- Overall completeness: **FAIL**.

## Open coverage work

1. Independent product ACCEPT for Wave-5p organizations (active product review child or full product IR).
2. Wave-5q freeze page for users update only, freeze ACCEPT, then product (+1 → 178).
3. Wave-5r: salesTaxReturns update-only freeze/product.
4. Later research: transactions create/update, specials, method-closed Supports honesty pass.
5. invoiceReminderAssociations delete blocked offline until live cleanup proof.
6. Bulk 92, UI/auth/vision, live CUD still open.

## Evidence boundaries

- Research ACCEPT is not freeze ACCEPT, product ACCEPT, or live qualification.
- Organizations singular DELETE is 405: never claim delete cleanup offline.
- Users singular create/delete are 405: freeze is update-only.
- Do not green coverage from research or freeze alone.
- Unauth 405 overrides Supports create/update text for geo/reference rows.

## References

- Review70 body: `.fractal/main.billy_complete/tmp/grok-review.md`
- Research70 brief: `.fractal/main.billy_complete/tmp/grok-research.md`
- Wave-5q freeze-ready wiki: `wiki/wave_fiveq_users_freeze_ready_research.md`
- Wave-5q research independent review: `wiki/wave_fiveq_users_freeze_ready_research_independent_review.md`
- Wave-5p freeze page: `wiki/wave_fivep_ticketed_writes_contract.md`
- Wave-5p freeze acceptance: `wiki/wave_fivep_freeze_independent_review.md`
- Probe rules: `wiki/offline_write_probe_rules.md`
