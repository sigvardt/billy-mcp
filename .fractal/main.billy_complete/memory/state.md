---
name: state
desc: Current node state, verified review decisions, and open qualification work.
tags: [billy, coverage, review]
sources:
  - docs/superpowers/specs/2026-07-28-billy-mcp-complete-design.md
  - https://www.billy.dk/api/
created: 2026-07-30T11:33:24Z
updated: 2026-07-30T12:24:30Z
---

# state

## Current state

- Wave-5c through Wave-5o write modules are merged into root; one shared confirmation store and write protocol.
- Root registry has **260** `api_*` tools. Offline coverage **177** implemented + contract_tested. Live/vision **0**. `complete: false`.
- Wave-5o freeze, product, and product independent review are **ACCEPT**.
- Wave-5p freeze page is **on root** (MD5 `2742eda7bafecd619aba5fa8ad0694c5`) and freeze independent review is **ACCEPT**.
- Wave-5p product-ready research and product-implementation handoff research are **ACCEPT as research**.
- Research70 reconfirmed docs MD5 `8b94b0135c91fd15fe54ea33e088a4be` (ETag `wcw4x9hqvu3603`, 147934 bytes) byte-identical to research69. Core unauth gates unchanged. Extra matrix: many Supports-create/update red rows are unauth 405; transactions POST/PUT 401; specials open at 401.
- Organizations create/update is integrated on root with four typed ticketed tools. Its documented `organizations[]` create response root is covered by generated API and UI-parity inventory metadata; all UI workflow flags remain red.
- Wave-5q users update freeze-ready research package is written (`wiki/wave_fiveq_users_freeze_ready_research.md` + `tmp/grok-research.md` research70). Not freeze ACCEPT and not product.
- UI all red (339); bulk 92 empty-tool red; no live token; no UI credentials.

## Verification

- Docs body byte-identical to research69; core probe matrix matches.
- Extra method-closed Supports rows documented for offline refusal (not greened).
- Coverage honesty: 177/177/0/0; complete false; zero UI greens; zero bulk greens; no false greens from research or integration.

## Review decisions (authoritative)

- Wave-5m freeze/product: **ACCEPT** offline.
- Wave-5n freeze/product: **ACCEPT** offline for singular create/update only.
- Wave-5o freeze/product: **ACCEPT** offline.
- Wave-5p freeze: **ACCEPT**.
- Wave-5p product-ready research: **ACCEPT as research**.
- Wave-5p product-implementation handoff research69: **ACCEPT as research**.
- Wave-5p product: integrated on root; independent Grok product review remains required before offline product acceptance.
- Wave-5q users freeze-ready research70: **packaged**; independent research review not yet run.
- Overall completeness: **FAIL**.

## Open coverage work

1. Independent Grok review of the integrated Wave-5p organizations product; offline product acceptance remains pending.
2. Wave-5q: freeze page for users update only (two tools), freeze ACCEPT, then product (+1 → 178 after orgs).
3. Wave-5r: salesTaxReturns update-only freeze/product (narrow writable fields).
4. Later research: transactions create/update (method-open), specials (files/emails/deliveries/logs), method-closed Supports honesty pass.
5. invoiceReminderAssociations delete remains blocked offline until live non-production cleanup proof.
6. Bulk 92, UI/auth/vision, live CUD still open.

## Evidence boundaries

- Research ACCEPT is not product ACCEPT or live qualification.
- Organizations singular DELETE is 405: never claim delete cleanup offline.
- Users singular create/delete are 405: freeze is update-only.
- Do not green coverage from research or freeze alone.
- Unauth 405 overrides Supports create/update text for geo/reference rows.

## References

- Research70 brief: `.fractal/main.billy_complete/tmp/grok-research.md`
- Wave-5q freeze-ready wiki: `wiki/wave_fiveq_users_freeze_ready_research.md`
- Wave-5p product handoff review: `wiki/wave_fivep_product_implementation_research_independent_review.md`
- Wave-5p freeze page: `wiki/wave_fivep_ticketed_writes_contract.md`
- Wave-5p freeze acceptance: `wiki/wave_fivep_freeze_independent_review.md`
- Wave-5p candidate research (prior users/salesTaxReturns): `wiki/wave_fivep_candidate_write_research.md`
- Probe rules: `wiki/offline_write_probe_rules.md`
