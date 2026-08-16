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

`auth_login_wait` READY now returns `organization_id` from the live URL slug.
Default `create_server` login drives write and `-readback` profiles. Mismatched
slugs are `CONFIRMATION_MISMATCH`. A blank read-back after that sequence is
`ORGANIZATION_REQUIRED`. Ticket execute still compares the live URL slug.

Live UI write tests may write `author=live_test` and
`reviewer_verdict=pending_review` only. They must not write `accept` or purge
frames. Coverage vision is true only after an independent review accepts and
purge is verified (`C7DBE974`).

Coverage stays red until live contacts CUD through `create_server` `call_tool`
passes that provenance rule. Daybook and posting creates with no cleanup path
still refuse.

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
