---
name: wave_four_first_cohort_independent_review
desc: Independent Grok review of merged Wave-4 geo/tax/bank modules — ACCEPT quality, FAIL product complete and root wiring.
tags: [billy, api, review, wave4]
sources:
  - https://www.billy.dk/api/
  - coverage/status.json
  - docs/superpowers/specs/2026-07-28-billy-mcp-complete-design.md
  - wiki/wave_four_remaining_clear_reads_contract.md
created: 2026-07-29T12:35:00Z
updated: 2026-07-29T12:35:00Z
---

# wave_four_first_cohort_independent_review

Independent Grok review of the root tree after geo, tax, and bank read modules
were merged. Full scratch report:
`.fractal/main.billy_complete/tmp/grok-review.md`.

## Verdict

| Gate | Result |
| --- | --- |
| Official docs ↔ inventory | **PASS** (fingerprint unchanged) |
| Anti-false-green | **PASS** (44 offline greens only; Wave-4 still red) |
| First-cohort module quality | **PASS** (34 GET tools + focused tests) |
| Root registration of Wave-4 | **FAIL** (expected gap) |
| Product completeness | **FAIL** |

**Overall: FAIL** product complete. **ACCEPT** honesty and first-cohort source
quality.

## Facts frozen by this review

- Docs: ETag `hsisik4g9p3603`, MD5 `c2efda0ee4cf9cf200e14910c5fc6996`, 147934
  bytes (https://www.billy.dk/api/).
- Status: `complete: false`; implemented/contract_tested **44**; live **0**;
  vision **0**.
- Registry: **44** `api_*` + **2** `coverage_*`. No geo/tax/bank tools exposed.
- Modules present but unregistered: `geo_reads.py` (8), `tax_reads.py` (16),
  `bank_reads.py` (10). Focused tests pass; offline suite 438 pass; full mode
  fails closed at completeness.
- Inventory still requires `countryId` on cities/states/zipcodes lists without
  greening those rows.
- Second cohort (balance/invoice-ext, ledger/users) not on root.

## Required next work (Codex Power)

1. Finish and merge second-cohort leaves (16 tools).
2. Register all 50 Wave-4 tools on the server; add offline evidence IDs only
   with focused test paths; regenerate coverage → target **94** offline API
   tools, still `live_tested=0` and `complete=false`.
3. Do not green bulk, writes, live, or UI without non-production evidence.

## Explicit non-findings

- No false greens from the first-cohort merge.
- No REQUIRED rewrites of the three first-cohort modules from this review.
- No headed browser use; no credentials in tree from this review.
