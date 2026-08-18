---
name: state
desc: Current node state for the Billy MCP complete run.
tags: [billy, coverage, ui_writes]
sources:
  - docs/superpowers/specs/2026-07-28-billy-mcp-complete-design.md
  - https://www.billy.dk/api/
  - radio:96908DC6
  - radio:07600147
  - radio:E87B6AEF
created: 2026-08-16T14:29:47Z
updated: 2026-08-18T00:20:00Z
---

## Now

Owner `96908DC6` is binding. Interface writes first. API live stays deferred.
HEAD is `1936b7c`. `E87B6AEF` files wait for COMMIT. Stay red. Do not finish.

Invoice CUD stays unbound. Honesty 16 stay red. Never call the API.

`452E0773` is closed. The loaded control contract names `click_open` on
the closest `pickerfield` wrapper (`data-cy` name only). Binding
`token_class=name_quoted_contact`. One wrapper click already ran.
`option_role_count=0`. `UI_CHANGED`. Role-option zero is not proof the
picker stayed closed.

`07600147` is closed and committed. One FastMCP tagged customer, fresh
confirm, scoped observer, one `pickerfield` click. `changed_node_count=0`.
`exact_match_target=false`. `UI_CHANGED`. Customer deleted. Absence
proved. Live test verifies the dump without repeating that click.

`E87B6AEF` dump is delivered and review FAIL. Two visible descendants:
contact `INPUT` and overlay `DIV` at `dx=242`. `unique_target=false`.
`wrapper_handler_guard=none`. `UI_CHANGED`. No customer. No click.
Independent review: dump contract met. Invoice CUD still unbound.
Do not remap. Do not click the overlay or the wrapper.

Closed and not to be repeated: typed-only bind (`51E18E60`), right-edge
chevron dump (`A3AB03C3`), DIV ownership click (`9F777B8F`), tagged type
trace (`8EFD0EAD`), event or pageerror dump (`4A5CD1E7`), rest route
capture (`F12B607E`), the first `pickerfield` click (`452E0773`), the
instrumented post-click dump (`07600147`), and the descendant map
(`E87B6AEF`).
Do not type. Do not recapture routes. Do not force or evaluate clicks.
Do not sweep portals. Do not send a second diagnostic click.
Do not remake the descendant map. Next is a different read-only
capture.

## Proved and still red

Contacts CUD through FastMCP is live-proved. Tools are
`ui_clients_{create,update,delete}_preview`. Vision
`run_id=3d5b151dfd5342258f8734373597f8c1` is
`author=independent_review`, `reviewer_verdict=accept`,
`purge_verified=true`. Frame folder is gone.
`ui_clients_update_open` and `ui_clients_delete_open` stay on
`RETAINED_OPEN_SHELL_TOOLS`. Browser egress allows PUT
`/v2/contacts/:id` only.

Draft bills CUD through FastMCP is live-proved on existing-option bind.
Tools are `ui_bills_{create,update,delete}_preview`. Vision
`run_id=9920dd9476474b41aef70e6d66d24638` is accept with purge
verified. Frame folder is gone. `ui_bills_update_open` and
`ui_bills_delete_open` stay retained. Never book, approve, pay, or email.

Invoice CUD still names `ui_invoices_*_open`. Offline preview or execute
helpers exist. Independent review of that family is FAIL. Dummy 15-char
type is not an existing-customer observation. Existing-customer type
uses `MCP-UI-INV-` plus 8 hex and matching `value_len`. That is not a
bind.

## Standing constraints

`auth_login_wait` READY returns `organization_id` from the live URL slug.
Ticket execute compares that slug to `prepared.binding.organization_id`.
Read-back starts a second runtime and must authenticate
(`E1E454F4`). Cleanup needs a third fresh read-back.
Live write tests may write `author=live_test` and
`reviewer_verdict=pending_review` only. They must not write `accept` or
purge frames (`C7DBE974`).

Live refs: keyring service `billy-mcp`, opaque ids `billy-ui-primary`
and `billy-ui-secondary`. `BILLY_ORGANIZATION_ID` stays unset until the
dedicated non-production org is proved in the interface.
Never log values. Never read `/Users/user/Desktop/billy_login.txt`.

`/:org_slug/clients/empty` with heading Kontakter is the empty customers
page. Exact **Ret** opens edit. **Slet kontakt** is a link. Confirm is
**Ja, slet**. `{tag}-U` is a different name from `{tag}`. Save is
`button[data-cy='save-button']` (**Gem**).

`A6FB8FC2` stays a one-close leftover-portal constraint. `91A2C363`
leftover Leverandør slice is closed.

## Children

Merged with `--no-ff` and parked:

- `ui_contacts_writes`
- `ui_bills_writes`
- `ui_invoices_writes` (draft only; no send or email)
- `ui_products_writes`
- `ui_ledger_writes`
- `ui_files_writes`
- `ui_org_writes` (company fields only; fail-closed on users or tokens)

No children are running. Old wave or review descendants stay retired and
unmerged.

Coverage stays red until remaining honesty families prove live FastMCP
CUD with independent review. Node complete stays false.
See `decisions.md` and `todo.md`.
