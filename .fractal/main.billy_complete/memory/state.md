---
name: state
desc: Current node state, verified review decisions, and open qualification work.
tags: [billy, coverage, review]
sources:
  - docs/superpowers/specs/2026-07-28-billy-mcp-complete-design.md
  - https://www.billy.dk/api/
created: 2026-07-29T10:38:45Z
updated: 2026-07-29T10:38:45Z
---

# state

## Current state

- The coverage and safety foundation is on root: coverage manifests (305 API +
  339 UI), locked client, tickets, redaction, browser egress, and coverage
  tools.
- Exactly 16 Wave-1 API rows are offline-qualified (`implemented` +
  `contract_tested`): user, user organizations, organizations, currencies,
  countries, locales, products, product prices, contacts. All are registered
  in root `server.py`. Every `live_tested` and UI qualification state remains
  false.
- Generated status and report accurately identify this bounded slice as
  `phase_1_offline_api_reads`; `complete` remains false.
- Three active Codex Power leaves own Wave-2 invoice, bill, and daybook
  transaction read modules. Root retains server wiring and generated coverage
  evidence until clean merge.
- UI discovery evidence stops at unauthenticated `/login`.
- Full test mode fails closed until every applicable row qualifies.
- Official docs fingerprint unchanged.

## Evidence boundaries

- Official API fingerprint: ETag `hsisik4g9p3603`, 147934 bytes, MD5
  `c2efda0ee4cf9cf200e14910c5fc6996` (https://www.billy.dk/api/).
- 46 resources, 207 clear ops, 92 bulk ambiguous, 6 specials; no webhooks.
- Documented list filter tables exist only for invoices, bills, and
  daybookTransactions (inventory freeze matches official parameters).
- `BILLY_API_TOKEN` unavailable; no live or vision claim is valid.
- Offline suite: 77 passed; full mode exit 1 on require-complete.

## Review decisions

- Accepted: inventory arithmetic and specials match official Supports; files
  create aliases to multipart special; dual-tool and bankLineMatch defects fixed.
- Accepted: checker `--require-complete` and full mode fail closed on red inventory.
- Accepted: Wave-1 offline greens are real typed tools + contract tests, not stubs.
- Rejected as complete: product completeness, live qualification, UI/vision
  completeness, auth product tools, bulk resolution.
- Residual medium: create request_fields remain singular body keys until write
  tools; user/organizations root keys are assumed by fixtures until live proof.

## References

- Research: `.fractal/main.billy_complete/tmp/grok-research.md`
- Review: `.fractal/main.billy_complete/tmp/grok-review.md`
- Wiki: `wiki/billy_api_v2_research_seed.md`, `wiki/billy_ui_discovery_brief.md`,
  `wiki/phase_zero_contract.md`, `wiki/wave_one_reads_contract.md`,
  `wiki/wave_two_filtered_reads_contract.md`
