---
name: api_live_qualification_semantics
title: API live qualification semantics
desc: Owner-scoped live API skip. Completeness uses discovered, implemented, and contract_tested. live_tested stays false with live_api=out_of_scope_by_user. Not a completeness claim.
tags: [billy, api, coverage, live_api, qualification]
sources:
  - https://www.billy.dk/api/
  - docs/superpowers/specs/2026-07-28-billy-mcp-complete-design.md
  - scripts/generate_coverage_report.py
  - scripts/check_coverage.py
  - tests/coverage/test_api_live_qualification_semantics.py
created: 2026-08-19T20:10:00Z
updated: 2026-08-19T20:10:00Z
---

# API live qualification semantics

Owner 2026-07-31 and NODE.md requirement 2 override design §12.2: API
`live_tested` is never greened. Live API tests stay out of scope.

## Inventory rules

Every API row:

- `discovered`, `implemented`, and `contract_tested` are the
  completeness flags
- `live_tested` stays false
- `qualification.live_api` is `out_of_scope_by_user`
- `qualification.kind` is **not** `out_of_scope_by_user` (that kind
  is owner-skip for a whole UI operation)

Implemented offline rows use `kind=live_api_deferred` and
`scope_code=LIVE_API_OWNER_SKIP`. Existing tools stay.
`tools_allowed` is not forced false.

Residual 29 and bulk 92 keep their existing kinds and
`tools_allowed=false`. See
[[residual_clear_method_closed_inventory_honesty]].

## Completeness

`coverage_is_complete` requires API
`api_row_is_qualified`: the three offline flags, `live_tested is
False`, and `live_api=out_of_scope_by_user`. An API row with
`live_tested=true` is incomplete.

`kind=out_of_scope_by_user` remains UI-only (annual reports,
residual-five writes).

## Lock

Generator `DOCS_ETAG` / `DOCS_MD5` stay the inventory lock until a
test-first reconcile of the live official page. Live observation
may be recorded as `docs_etag_observed` on the deferred
qualification. Do not invent bulk tools from an ETag change.

## Not this page

This is not product ACCEPT, not live verification, and not
`complete: true`.
