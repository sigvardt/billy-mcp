---
name: state
desc: Current node state, verified review decisions, and open qualification work.
tags: [billy, coverage, review]
sources:
  - docs/superpowers/specs/2026-07-28-billy-mcp-complete-design.md
  - https://www.billy.dk/api/
created: 2026-07-30T11:33:24Z
updated: 2026-07-30T12:02:00Z
---

# state

## Current state

- Wave-5c through Wave-5o write modules are merged into root; one shared confirmation store and write protocol.
- Root registry about **256** `api_*` tools. Offline coverage **175** implemented + contract_tested. Live/vision **0**. `complete: false`.
- Wave-5o freeze, product, and product independent review are **ACCEPT**.
- Wave-5p freeze page is **on root** (`wiki/wave_fivep_ticketed_writes_contract.md`, MD5 `2742eda7bafecd619aba5fa8ad0694c5`) and its independent review is **ACCEPT**.
- Wave-5p product-ready research is **ACCEPT as research**.
- Research69 reconfirmed official docs body MD5 `8b94b0135c91fd15fe54ea33e088a4be` (ETag `wcw4x9hqvu3603`, 147934 bytes) and unauth org POST/PUT 401, DELETE 405. No method-gate drift.
- Organizations product module is **absent**. Freeze ACCEPT authorizes a separate offline Codex Power product leaf for create and update only.
- UI all red; bulk 92 empty-tool red; no live token; no UI credentials.

## Verification

- Docs body byte-identical to research68; probes same outcomes for organizations and sequential candidates.
- Coverage honesty: 175/175/0/0; complete false; zero UI greens; zero bulk greens; no false greens from research.
- Freeze page fidelity matches official Supports and probe matrix.

## Review decisions (authoritative)

- Wave-5m freeze/product: **ACCEPT** offline.
- Wave-5n freeze/product: **ACCEPT** offline for singular create/update only.
- Wave-5o freeze/product: **ACCEPT** offline.
- Wave-5p freeze: **ACCEPT**.
- Wave-5p product-ready research: **ACCEPT as research**.
- Wave-5p product: not implemented or accepted; Codex Power offline product leaf is now authorized.
- Overall completeness: **FAIL**.

## Open coverage work

1. Codex Power product leaf for organizations create+update: four tools, fail-closed cleanup wording, contract tests, regenerate coverage to **177** offline green; then independent product review.
2. Later: users update-only; salesTaxReturns update-only.
3. invoiceReminderAssociations delete remains blocked offline until live non-production cleanup proof.
4. Bulk 92, UI/auth/vision, live CUD still open.

## Evidence boundaries

- Research ACCEPT is not freeze ACCEPT or product ACCEPT; freeze independent ACCEPT is on root.
- Organizations singular DELETE is 405: never claim delete cleanup offline.
- Do not green coverage from research or freeze alone.
- Organizations product must remain a ticketed-write implementation and product-review gate; freeze acceptance alone never greens coverage.

## References

- Product implementation handoff: `.fractal/main.billy_complete/tmp/grok-research.md` (research69)
- Product-ready research: prior research68 (same contract; superseded as handoff by research69)
- Freeze page: `wiki/wave_fivep_ticketed_writes_contract.md`
- Freeze acceptance: `wiki/wave_fivep_freeze_independent_review.md`
- Product-ready research review: `wiki/wave_fivep_product_ready_research_independent_review.md`
- Wave-5o product acceptance: `wiki/wave_fiveo_product_independent_review.md`
- Candidate research: `wiki/wave_fivep_candidate_write_research.md`
- Probe rules: `wiki/offline_write_probe_rules.md`
