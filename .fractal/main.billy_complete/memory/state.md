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

Old wave/review descendants stay retired and unmerged. No children are running.

Parent `E1E454F4` live refs stay: keyring service `billy-mcp`, opaque ids
`billy-ui-primary` and `billy-ui-secondary`. `BILLY_ORGANIZATION_ID` stays
unset until the dedicated non-production org is proved in the interface.

The nine named idle `billy-live-contacts-*` profiles are gone. Zero remain.

Live DualSessionLogin READY now returns a slug. The dedicated org's customers
page is `/:org_slug/clients/empty` with heading Kontakter, not Kunder. List and
create-open still require the old path and heading, so they return UI_CHANGED.
The create dialog fields are still present. No submit was done.

`/:org_slug/clients/empty` and heading Kontakter are accepted. Live create
through FastMCP submits and a second session sees the new name.

Update and delete clicks now use exact labels. Substring `Ret` matches **Opret**.
Exact **Ret** opens `input[name=name]` plus **Gem**. **Slet kontakt** is a link,
not a button. Confirm is **Ja, slet** (fallback **Slet**). Never **Arkivér**.

Read-back treats `{tag}-U` as a different name from `{tag}`. Live create through
FastMCP still submits and a second session sees the exact name. The live save
control is `button[data-cy='save-button']` (Ember action, text **Gem**). The
edit form stays open after that click. List exact-name is the persist proof.
Live FastMCP create, update, and delete of one tagged contact passed.
Browser egress now allows PUT `/v2/contacts/:id` only. PATCH stays
denied. The SPA save is PUT with the new name. Persist waits for that
response after the proved pointer click.

The durable vision record is `author=independent_review`,
`reviewer_verdict=accept`, `purge_verified=true`,
`run_id=3d5b151dfd5342258f8734373597f8c1`. That frame folder is gone.
Contacts CUD `tool_name` values are `ui_clients_{create,update,delete}_preview`.
Discovery and get-open stay on `ui_clients_*_open`. `93D7A063` is closed.
Honesty 16 stays red. Coverage stays red.
`check_coverage.RETAINED_OPEN_SHELL_TOOLS` keeps
`ui_clients_update_open` and `ui_clients_delete_open` registered.
Empty untagged bill drafts are gone. A fresh session list is
`/:org_slug/bills/empty`. Parent `31F6E753` still requires a pre-submit
DOM dump before the next create. Update save is **Opdater**. Honesty 16
stay red. Do not remap.

Independent review **FAIL** still stands for live proof. Offline IR
fixes are in: pre-submit dump, all four fields required, forbidden CTA
refuse, POST-only create persist, created id from POST, PUT prefix
`/v2/bills/` only. Login now reaches READY. Live create still fails on
vendor typeahead bind (`UI_CHANGED` field `vendor`) after a contacts
preview create. No bills CUD vision record. Do not green. Do not remap.
Do not finish.

## Review

Honesty on the 16 CUD rows still holds. Node complete stays false.
Offline org-bind wiring is in. One live contacts CUD used a second
session for read-back and a third session for absence. Same-session
accept plus an inverted mapping order failed independent review. The
accept record and purge stay. Mapping now points at preview after that
recorded verdict.

See `decisions.md` and `todo.md`.
