---
name: state
desc: Current node state, verified review decisions, and open qualification work.
tags: [billy, coverage, review]
sources:
  - docs/superpowers/specs/2026-07-28-billy-mcp-complete-design.md
  - https://www.billy.dk/api/
created: 2026-07-29T10:58:11Z
updated: 2026-07-29T11:48:00Z
---

# state

## Current state

- Wave-1 through Wave-3 offline reads are on root: **44** real `api_*` tools +
  2 `coverage_*`. Status: 44 implemented/contract_tested, 0 live_tested,
  complete false.
- Independent review after Wave-3 integration: **FAIL** product completeness;
  **ACCEPT** offline Wave-3 quality and anti-false-green discipline.
- Official docs fingerprint unchanged.
- UI discovery still unauthenticated login only; all UI rows red.
- `BILLY_API_TOKEN` unavailable; full mode fails closed (exit 1) after the
  offline suite passes.

## Evidence boundaries

- Official API fingerprint: ETag `hsisik4g9p3603`, 147934 bytes, MD5
  `c2efda0ee4cf9cf200e14910c5fc6996` (https://www.billy.dk/api/, review re-fetch
  2026-07-29T11:39:44Z).
- 46 resources, 207 clear ops, 92 bulk ambiguous, 6 specials; 0 webhooks.
- Documented list filter tables only for invoices, bills, daybookTransactions.
- Wave-3 unfiltered get/list greened offline only for: invoiceLines, billLines,
  daybookTransactionLines, contactPersons, daybooks, daybookBalanceAccounts,
  accounts, accountGroups, accountNatures, files, attachments.
- Offline suite and repository policy pass. Full mode still fails only at the
  required completeness gate.
- Remaining clear red: 165 (50 get/list + 115 writes). Specials red except user
  get/organizations.

## Review decisions

- Accepted: inventory arithmetic still matches official Supports.
- Accepted: Wave-3 modules enforce empty filter allowlists, reject parent ids
  and offset, map documented roots, leave live_tested false.
- Accepted: redaction covers email, bank*, downloadUrl for Wave-3 sensitive
  fields.
- Accepted: files create dual row (clear + special alias) remains red; no
  JSON invent create.
- Fixed after independent review: file and attachment list success envelopes
  preserve the documented optional `meta.paging` rather than flattening it.
- Fixed after independent review: files, attachments, products, and product
  prices expose flat MCP parameters instead of a nested `request` object;
  schema and structured-content regression tests cover both corrections.
- Rejected as complete: product completeness, live, UI/vision, auth product
  tools, bulk resolution.

## Next implementation slice (for Codex Power)

1. Wave-4+ remaining clear get/list (50) behind a fresh Grok freeze if docs
   unchanged (tax/bank/geo/users/postings/sales-tax clusters).
2. When token exists: live-test offline-green reads; bulk probes; ticketed
   writes; never invent bulk bodies.
3. Authenticated UI only with credentials + DOM + read-back + vision + purge.

## References

- Research: `.fractal/main.billy_complete/tmp/grok-research.md`
- Review: `.fractal/main.billy_complete/tmp/grok-review.md`
- Wiki: `wiki/billy_api_v2_research_seed.md`, `wiki/billy_ui_discovery_brief.md`,
  `wiki/phase_zero_contract.md`, `wiki/wave_one_reads_contract.md`,
  `wiki/wave_two_filtered_reads_contract.md`,
  `wiki/wave_three_unfiltered_reads_contract.md`
