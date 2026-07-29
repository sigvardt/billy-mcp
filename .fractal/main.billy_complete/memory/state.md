---
name: state
desc: Current node state, verified review decisions, and open qualification work.
tags: [billy, coverage, review]
sources:
  - docs/superpowers/specs/2026-07-28-billy-mcp-complete-design.md
  - https://www.billy.dk/api/
created: 2026-07-29T12:12:38Z
updated: 2026-07-29T15:54:20Z
---

# state

## Current state

- Root includes the Wave-5a registration merge. Runtime exposes **124** `api_*` tools and two coverage tools, with one shared confirmation store and write protocol across all four accepted write registrars.
- Child `wave5a_root_registration` tip `7cb74e2` is integrated; its child seed was removed from the root branch while the child branch remains as the audit record.
- Coverage: implemented 109, contract_tested 109, live 0, vision 0, `complete: false`. Docs fingerprint unchanged.
- Research brief now freezes **Wave-5b** (accounts, accountGroups, daybookBalanceAccounts) offline ticketed writes for after registration merge + IR ACCEPT.
- UI all red; bulk 92 empty-tool red; four specials red; no live token.

## Review decisions (authoritative)

- Catalog/daybook tips: **ACCEPT** selective merge (prior).
- Root registration **baseline** @ plan commit: **ACCEPT honesty / FAIL product completeness** (`wiki/wave_fivea_root_registration_baseline_review.md`).
- Registration product: parent integration and offline verification passed; **not reviewed as ACCEPT** until an independent Grok re-review.
- Wave-5b: research only; no product green.

## Next work

1. Commission and merge an independent Grok product review of the integrated registration slice.
2. After ACCEPT: implement Wave-5b per `.fractal/main.billy_complete/tmp/grok-research.md` (9 CUD rows / 18 tools).
3. Then remaining clear writes, specials, bulk (live only), UI/auth/vision, live qualification.

## Evidence boundaries

- Official API fingerprint: etag `hsisik4g9p3603`, MD5 `c2efda0ee4cf9cf200e14910c5fc6996`.
- Clean-archive registration verification passed 119 focused tests; root non-live/non-vision suite passed 593 tests with coverage and repository-policy checks.
- Unauth probes research17: DELETE empty 200 on chart/daybookBalance collections; accountGroups unauth PUT 404; postings CUD 405; files PUT/DELETE 405.
- Unauth DELETE empty 200 is not cleanup proof.

## References

- Research: `.fractal/main.billy_complete/tmp/grok-research.md`
- Wiki: `wiki/wave_fivea_root_registration_baseline_review.md`, `wiki/wave_five_ticketed_writes_contract.md`
