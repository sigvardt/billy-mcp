---
name: state
desc: Current node state, verified review decisions, and open qualification work.
tags: [billy, coverage, review]
sources:
  - docs/superpowers/specs/2026-07-28-billy-mcp-complete-design.md
  - https://www.billy.dk/api/
created: 2026-07-30T11:33:24Z
updated: 2026-07-30T11:52:30Z
---

# state

## Current state

- Wave-5c through Wave-5o write modules are merged into root; one shared confirmation store and write protocol.
- Root registry about **256** `api_*` tools. Offline coverage **175** implemented + contract_tested. Live/vision **0**. `complete: false`.
- Wave-5o freeze page is **on root** and freeze independent review is **ACCEPT**.
- Wave-5o product is **merged on root** (create row green offline). Formal product independent review page still **absent**.
- Wave-5p freeze page is **on root** (`wiki/wave_fivep_ticketed_writes_contract.md`, MD5 `2742eda7bafecd619aba5fa8ad0694c5`). Freeze independent review is **absent**.
- Wave-5p product-ready research68 is **ACCEPT as research** (`wiki/wave_fivep_product_ready_research_independent_review.md`).
- Organizations product module is **absent**. Product remains blocked until freeze independent ACCEPT.
- UI all red; bulk 92 empty-tool red; no live token; no UI credentials.

## Verification

- Independent review68 docs: ETag `wcw4x9hqvu3603`, MD5 `8b94b0135c91fd15fe54ea33e088a4be`, body 147934; byte-identical to research68.
- Independent unauth probes: organizations POST/PUT 401 DELETE 405; associations DELETE 200 meta-only; no method-gate drift vs research68.
- Coverage honesty: 175/175/0/0; complete false; zero UI greens; zero bulk greens; no false greens from research.
- Freeze page fidelity matches official Supports and probe matrix; freeze ACCEPT still required before product.

## Review decisions (authoritative)

- Wave-5m freeze/product: **ACCEPT** offline.
- Wave-5n freeze/product: **ACCEPT** offline for singular create/update only.
- Wave-5o freeze: **ACCEPT**.
- Wave-5o product on root: merged offline green for create; formal product independent review page still separate.
- Wave-5p candidate research: research only.
- Wave-5p freeze-ready research: **ACCEPT as research**.
- Wave-5p freeze page: on root; **not freeze ACCEPT**.
- Wave-5p product-ready research68: **ACCEPT as research**.
- Wave-5p product: **not accepted**.
- Overall completeness: **FAIL**.

## Open coverage work

1. Independent Grok freeze review of Wave-5p organizations freeze page (process gate before product).
2. After freeze ACCEPT: product four tools for organizations create+update; fix create cleanup wording; target 177 offline green.
3. Wave-5o product independent review page if still needed as formal record.
4. Later: users update-only; salesTaxReturns update-only.
5. invoiceReminderAssociations delete remains blocked offline until live non-production cleanup proof.
6. Bulk 92, UI/auth/vision, live CUD still open.

## Evidence boundaries

- Research ACCEPT is not freeze ACCEPT or product ACCEPT.
- Organizations singular DELETE is 405: never claim delete cleanup offline.
- Do not green coverage from research or freeze alone.
- Do not start organizations product before freeze independent ACCEPT.

## References

- Independent review body: `.fractal/main.billy_complete/tmp/grok-review.md`
- Product-ready research: `.fractal/main.billy_complete/tmp/grok-research.md` (research68)
- Wiki product-ready research review: `wiki/wave_fivep_product_ready_research_independent_review.md`
- Freeze page: `wiki/wave_fivep_ticketed_writes_contract.md`
- Wiki freeze-ready review: `wiki/wave_fivep_freeze_ready_research_independent_review.md`
- Candidate research: `wiki/wave_fivep_candidate_write_research.md`
- Wave-5o freeze: `wiki/wave_fiveo_ticketed_writes_contract.md`
- Probe rules: `wiki/offline_write_probe_rules.md`
