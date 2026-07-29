---
name: state
desc: Current node state, verified review decisions, and open qualification work.
tags: [billy, coverage, review]
sources:
  - docs/superpowers/specs/2026-07-28-billy-mcp-complete-design.md
  - https://www.billy.dk/api/
created: 2026-07-29T10:58:11Z
updated: 2026-07-29T11:05:00Z
---

# state

## Current state

- Wave-1 and Wave-2 offline reads are committed and product-exposed (22 tools).
- Research for Wave-3 unfiltered clear get/list is frozen with unchanged
  official docs fingerprint. No coverage greens changed during research.
- Independent review verdict still: **FAIL** for product completeness; **ACCEPT**
  offline quality and anti-false-green discipline for landed work.
- Every `live_tested` and UI qualification state remains false. `complete`
  remains false. Full mode fails closed.
- UI discovery evidence stops at unauthenticated `/login`.
- Official docs fingerprint unchanged.

## Evidence boundaries

- Official API fingerprint: ETag `hsisik4g9p3603`, 147934 bytes, MD5
  `c2efda0ee4cf9cf200e14910c5fc6996` (https://www.billy.dk/api/, re-fetched
  2026-07-29T11:02:40Z).
- 46 resources, 207 clear ops, 92 bulk ambiguous, 6 specials; no webhooks.
- Documented list filter tables only for invoices, bills, daybookTransactions.
- Wave-3 resources have **empty** official filter tables: invoiceLines,
  billLines, daybookTransactionLines, contactPersons, daybooks,
  daybookBalanceAccounts, accounts, accountGroups, accountNatures, files,
  attachments (22 get/list tools).
- All eleven Wave-3 list paths return live unauthenticated 401
  `AUTHENTICATION_REQUIRED` (probed without secrets).
- `BILLY_API_TOKEN` unavailable; no live or vision claim is valid.
- Offline suite previously: 128 tests passed after Wave-2 root integration.

## Review decisions

- Accepted: inventory arithmetic and specials match official Supports; files
  create aliases to multipart special; bankLineMatches singularization correct.
- Accepted: checker `--require-complete` and full mode fail closed on red inventory.
- Accepted: Wave-1 and Wave-2 offline greens are real typed tools + contract
  tests, not stubs; `live_tested` stays false.
- Accepted: bill/invoice `q` as non-empty free search strings.
- Deferred: invoice date/time filters remain opaque strings without a live token.
- Deferred: invent no Wave-3 parent-id list filters until documented or
  live-proven and inventoried.
- Deferred: files create double-entry (`api.files.create` vs
  `api.special.files_upload`) resolved only in write wave as one multipart tool.
- Rejected as complete: product completeness, live qualification, UI/vision
  completeness, auth product tools, bulk resolution.

## Next implementation slice (for Codex Power)

1. Wave-3 unfiltered clear get/list: 22 tools across lines, contactPersons,
   daybooks/daybookBalanceAccounts, accounts/accountGroups/accountNatures,
   files read, attachments. Contract: `wiki/wave_three_unfiltered_reads_contract.md`
   and `.fractal/main.billy_complete/tmp/grok-research.md`.
2. Prefer parallel codex-power leaves per cluster; root owns server registry +
   evidence map + regenerate coverage (target 44 offline API rows; still
   complete false).
3. Redact account bank fields and file downloadUrl tokens in logs.
4. When token exists: live-test offline-green reads; start bulk probes; do not
   invent bulk bodies.

## References

- Research: `.fractal/main.billy_complete/tmp/grok-research.md`
- Review: `.fractal/main.billy_complete/tmp/grok-review.md`
- Wiki: `wiki/billy_api_v2_research_seed.md`, `wiki/billy_ui_discovery_brief.md`,
  `wiki/phase_zero_contract.md`, `wiki/wave_one_reads_contract.md`,
  `wiki/wave_two_filtered_reads_contract.md`,
  `wiki/wave_three_unfiltered_reads_contract.md`
