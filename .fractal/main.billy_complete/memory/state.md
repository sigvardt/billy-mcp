---
name: state
desc: Current node state, verified review decisions, and open qualification work.
tags: [billy, coverage, review]
sources:
  - docs/superpowers/specs/2026-07-28-billy-mcp-complete-design.md
  - https://www.billy.dk/api/
created: 2026-07-29T10:58:11Z
updated: 2026-07-29T10:58:11Z
---

# state

## Current state

- Wave-1 offline reads are committed and product-exposed (16 tools).
- Wave-2 invoice, bill, and daybook-transaction modules are merged and
  registered on root with focused contract tests. Their six rows have offline
  implementation and contract-test evidence, for 22 such API rows total.
- Independent review verdict: **FAIL** for product completeness; **ACCEPT**
  Wave-2 offline quality and anti-false-green discipline on the working tree.
- Every `live_tested` and UI qualification state remains false. `complete`
  remains false. Full mode fails closed.
- UI discovery evidence stops at unauthenticated `/login`.
- Official docs fingerprint unchanged.

## Evidence boundaries

- Official API fingerprint: ETag `hsisik4g9p3603`, 147934 bytes, MD5
  `c2efda0ee4cf9cf200e14910c5fc6996` (https://www.billy.dk/api/).
- 46 resources, 207 clear ops, 92 bulk ambiguous, 6 specials; no webhooks.
- Documented list filter tables only for invoices, bills, daybookTransactions;
  code allowlists match official tables on the working tree.
- `BILLY_API_TOKEN` unavailable; no live or vision claim is valid.
- Offline suite and final integration gate: 128 tests passed.

## Review decisions

- Accepted: inventory arithmetic and specials match official Supports; files
  create aliases to multipart special; bankLineMatches singularization correct.
- Accepted: checker `--require-complete` and full mode fail closed on red inventory.
- Accepted: Wave-1 and Wave-2 offline greens (working tree) are real typed tools
  + contract tests, not stubs; `live_tested` stays false.
- Accepted: bill `q` as free search string (not field-name enum) matches official
  search parameter semantics.
- Fixed: invoice `q` now rejects an empty string, matching bill and daybook
  query validation.
- Deferred with evidence: invoice date/time filters remain opaque strings. The
  public documentation provides examples but no canonical accepted wire format,
  and no non-production token exists to validate a parser; enforcing one would
  invent contract behavior.
- Rejected as complete: product completeness, live qualification, UI/vision
  completeness, auth product tools, bulk resolution.
- Residual low/medium: invoice date filters as opaque strings vs bill `date`
  types; create request_fields singular until writes; user/organizations root
  keys fixture-assumed until live proof.

## Next implementation slice (for Codex Power)

1. Commit/push Wave-2 root integration WIP (server + evidence map + tests).
2. Wave-3 unfiltered clear get/list clusters (lines, contactPersons, daybooks,
   accounts, files read, attachments).
3. When token exists: live-test offline-green reads; start bulk probes; do not
   invent bulk bodies.

## References

- Research: `.fractal/main.billy_complete/tmp/grok-research.md`
- Review: `.fractal/main.billy_complete/tmp/grok-review.md`
- Wiki: `wiki/billy_api_v2_research_seed.md`, `wiki/billy_ui_discovery_brief.md`,
  `wiki/phase_zero_contract.md`, `wiki/wave_one_reads_contract.md`,
  `wiki/wave_two_filtered_reads_contract.md`
