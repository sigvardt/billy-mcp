---
name: state
desc: Current node state, verified review decisions, and open qualification work.
tags: [billy, coverage, review]
sources:
  - docs/superpowers/specs/2026-07-28-billy-mcp-complete-design.md
  - https://www.billy.dk/api/
created: 2026-07-29T09:43:28Z
updated: 2026-07-29T10:19:00Z
---

# state

## Current state

- Phase 0 inventory and safety baseline are on root: coverage manifests (305
  API + 339 UI, all progress flags red except discovery on API rows), status
  complete false, locked client, tickets, redaction, browser egress, and
  coverage_* tools.
- Wave-1 read modules are merged for bootstrap, reference, catalogue, and
  contacts (16 tools + focused contract tests). Root `server.py` still
  registers only coverage tools; inventory `implemented` /
  `contract_tested` remain false until integration wires and proves them.
- UI discovery evidence stops at unauthenticated `/login`.
- Full test mode fails closed until every applicable row qualifies.
- Latest research brief targets Wave-1 root integration then Wave-2 filtered
  invoice/bill/daybookTransaction reads. Official docs fingerprint unchanged.

## Evidence boundaries

- Official API fingerprint: ETag `hsisik4g9p3603`, 147934 bytes, MD5
  `c2efda0ee4cf9cf200e14910c5fc6996` (https://www.billy.dk/api/).
- 46 resources, 207 clear ops, 92 bulk ambiguous, 6 specials; no webhooks.
- Documented list filter tables exist only for invoices, bills, and
  daybookTransactions (inventory freeze matches official parameters).
- `BILLY_API_TOKEN` unavailable; no live or vision claim is valid.

## Review decisions

- Accepted: inventory arithmetic and specials match official Supports; files
  create aliases to multipart special; dual-tool and bankLineMatch defects fixed.
- Accepted: checker `--require-complete` and full mode fail closed on red inventory.
- Rejected as complete: any product completeness or Phase 0 auth/UI closure claim.
- Residual medium: create request_fields remain singular body keys until write
  tools have official property-table evidence; user/organizations root keys
  assumed by fixtures until live proof; Fractal child seed trees remain
  tracked orchestration metadata rather than product artifacts.

## References

- Research: `.fractal/main.billy_complete/tmp/grok-research.md`
- Review: `.fractal/main.billy_complete/tmp/grok-review.md`
- Wiki: `wiki/billy_api_v2_research_seed.md`, `wiki/billy_ui_discovery_brief.md`,
  `wiki/phase_zero_contract.md`, `wiki/wave_one_reads_contract.md`
