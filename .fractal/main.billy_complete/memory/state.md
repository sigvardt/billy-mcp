---
name: state
desc: Current node state for the Billy MCP complete run.
tags: [billy, coverage, ui_writes]
sources:
  - docs/superpowers/specs/2026-07-28-billy-mcp-complete-design.md
  - https://www.billy.dk/api/
created: 2026-08-16T14:29:47Z
updated: 2026-08-16T14:29:47Z
---

## Now

Owner `96908DC6` is binding. Interface writes first. API live stays deferred.

Parent `5018B3FA` is addressed on the default path. Execute now drives the
family route, fields, and submit control, then returns `submitted=True`
only after a second page proves the marker. Daybook and posting creates
that have no cleanup path still refuse (`submitted=False`). Start-only
returns an error, not success. Contacts also does second-page read-back.

Coverage: complete false. Sixteen CUD parity rows stay open-only. Do not
green. Live FastMCP proof is still later.

Lint is green. Commit-mode suite: 1802 passed, 59 deselected. No live UI
or live API ran.

## Children

Merged with `--no-ff` and parked:

- `ui_contacts_writes` (`ui_clients_*`; live still later)
- `ui_bills_writes`
- `ui_invoices_writes` (draft only; no send/email)
- `ui_products_writes`
- `ui_ledger_writes`
- `ui_files_writes`
- `ui_org_writes` (company fields only; fail-closed on users/tokens)

Old wave/review descendants stay retired and unmerged.

Parent `E1E454F4` live refs stay: keyring service `billy-mcp`, opaque ids
`billy-ui-primary` and `billy-ui-secondary`. `BILLY_ORGANIZATION_ID` stays
unset until the dedicated non-production org is proved in the interface.

Live contacts contract remains in
`.fractal/main.billy_complete/tmp/grok-research.md` for the next slice.

## Review

`.fractal/main.billy_complete/tmp/grok-review.md`: package FAIL. Start-only
execute is a false submit (`5018B3FA`). Honesty on the 16 CUD rows still
holds. Node complete stays false.

See `decisions.md` and `todo.md`.
