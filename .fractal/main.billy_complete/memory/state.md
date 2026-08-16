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

Ticket preview requires `organization_id`. Default execute drives the family
route, fields, and submit control. Wrong-org execute is
`CONFIRMATION_MISMATCH` before fill or click. Contacts org proof uses the
live URL only. Read-back starts a second `BrowserRuntime` (`*-readback`).
A blank read-back profile that lands on `/login` is `ORGANIZATION_REQUIRED`.
Unit tests no longer share fake records; a second fake store cannot see the
write, so execute returns `NOT_FOUND`. That is wiring, not live proof.

Coverage stays red. No greening. Daybook and posting creates with no cleanup
path still refuse.

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

Next slice: authenticate the second session (`E1E454F4` secondary refs or
login on the `-readback` profile), then live contacts create/update/delete
through FastMCP, independent-session read-back, cleanup on a third fresh
read-back. Green only those three rows after that proof.

## Review

Honesty on the 16 CUD rows still holds. Node complete stays false.
Offline org-bind wiring is in. Live independence is not.

See `decisions.md` and `todo.md`.
