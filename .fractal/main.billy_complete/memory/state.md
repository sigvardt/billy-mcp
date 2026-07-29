---
name: state
desc: Current node state, verified review decisions, and open qualification work.
tags: [billy, coverage, review]
sources:
  - docs/superpowers/specs/2026-07-28-billy-mcp-complete-design.md
  - https://www.billy.dk/api/
created: 2026-07-29T10:58:11Z
updated: 2026-07-29T11:55:30Z
---

# state

## Current state

- Wave-1 through Wave-3 offline reads are on root: **44** real `api_*` tools +
  2 `coverage_*`. Status: 44 implemented/contract_tested, 0 live_tested,
  complete false.
- Wave-4 research freeze is ready: all **50** remaining clear get/list
  operations cited in `tmp/grok-research.md` and
  `wiki/wave_four_remaining_clear_reads_contract.md`.
- Official docs fingerprint unchanged.
- UI discovery still unauthenticated login only; all UI rows red.
- `BILLY_API_TOKEN` unavailable; full mode fails closed after the offline suite
  passes.
- Child `wave3_envelope_rereview` may still be active for Wave-3 envelope
  re-review; it does not block the Wave-4 freeze.

## Evidence boundaries

- Official API fingerprint: ETag `hsisik4g9p3603`, 147934 bytes, MD5
  `c2efda0ee4cf9cf200e14910c5fc6996` (https://www.billy.dk/api/, research re-fetch
  2026-07-29T11:52:46Z).
- 46 resources, 207 clear ops, 92 bulk ambiguous, 6 specials; 0 webhooks.
- Documented list filter tables only for invoices, bills, daybookTransactions.
- **Live (unauth):** cities/states/zipcodes require `countryId` (400 OTHER
  without it). countryGroups, countries, currencies, locales return 200 without
  a token. Most other Wave-4 lists return 401 AUTHENTICATION_REQUIRED.
- Wave-3 offline greens remain: invoiceLines, billLines, daybookTransactionLines,
  contactPersons, daybooks, daybookBalanceAccounts, accounts, accountGroups,
  accountNatures, files, attachments (plus prior waves).
- Remaining clear red: 165 (50 get/list + 115 writes). Specials red except user
  get/organizations.

## Review decisions

- Accepted: inventory arithmetic still matches official Supports.
- Accepted: Wave-3 modules empty filter allowlists (except Wave-2 filtered
  resources), flat schemas, meta.paging preserved.
- Accepted for Wave-4: require `countryId` on cities/states/zipcodes lists from
  live evidence; do not invent other resource filters offline.
- Rejected as complete: product completeness, live, UI/vision, auth product
  tools, bulk resolution.

## Next implementation slice (for Codex Power)

1. Wave-4 offline: 50 remaining clear get/list via five leaf modules
   (geo, tax, bank, balance/invoice-ext, ledger/users) per research brief.
2. Target registry after Wave-4: **94** `api_*` + 2 `coverage_*`; complete stays
   false; live_tested stays false.
3. When token exists: live-test offline-green reads; bulk probes; ticketed
   writes; never invent bulk bodies.
4. Authenticated UI only with credentials + DOM + read-back + vision + purge.

## References

- Research: `.fractal/main.billy_complete/tmp/grok-research.md`
- Review: `.fractal/main.billy_complete/tmp/grok-review.md`
- Wiki: `wiki/billy_api_v2_research_seed.md`, `wiki/billy_ui_discovery_brief.md`,
  `wiki/phase_zero_contract.md`, `wiki/wave_one_reads_contract.md`,
  `wiki/wave_two_filtered_reads_contract.md`,
  `wiki/wave_three_unfiltered_reads_contract.md`,
  `wiki/wave_four_remaining_clear_reads_contract.md`
