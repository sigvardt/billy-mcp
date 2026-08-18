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
  - radio:31B0C7A6
  - radio:28C8FBC8
  - radio:C0721A14
  - radio:D326FFB3
  - radio:AD8966F2
  - radio:23709235
  - radio:FD39FFE7
created: 2026-08-16T14:29:47Z
updated: 2026-08-18T08:20:00Z
---

## Now

Owner `96908DC6` is binding. Interface writes first. API live stays deferred.
HEAD is `e49c8f3`. Stay red. Do not finish. No children are running.

`2683CE6B` is the next binding after this commit. Scoped
post-validation capture on the contact input, not another
page-wide dump. `FD39FFE7` still makes invoice draft CUD and
product create mandatory. Invoice draft CUD first, then product
create, then files or ledger. Both stay mandatory and red. They are
not finished as `UI_CHANGED`. Official first-invoice support names
**Vælg kunde** then **Opret ny**. Live rest dump is committed on
`e49c8f3`: button 0, link 0, other 0, `hit_is_contact_input=true`,
no click, `proved_bind=none`, `UI_CHANGED`. Those words are the
contact-input placeholder, not a separate named control. Do not remake
that rest dump. Do not remake the closed picker set. Invoice CUD stays
red and is not finished.

Draft-save validation-open dump is delivered. One **Gem som kladde**
click: `gem_clicked=true`, `invoice_persisted=false`,
`validation_message_present=false`, `ingen_kontakter_count=0`,
`opret_ny_count=1`, `option_role_count=0`, `proved_bind=none`,
`UI_CHANGED`. Page-wide `opret_ny_count=1` is not a proved list
open (sidebar decoy). No existing-option bind. Do not remake that
dump. Do not click **Opret ny**. Leftover tagged customer deleted.
Absence count 0.
Honesty 16 stay red. Never call the API. Do not guess selectors.
Do not force or evaluate clicks. If that path cannot bind, ask the
owner. Do not freeze either as done.

`23709235` organization remap is committed. Live FastMCP tagged set
plus exact empty restore passed. Independent review accepted
`run_id=0937a009bf7e496ca2ce15a8af313868`. Frames purged.
`ui.parity.organizations.update` names
`ui_organizations_update_preview`. Honesty 16 stay red. Do not
remake the phone dump.

`D326FFB3` product delete-chrome recapture is closed and unsaved.
`proved_delete_path=none`. Do not remake that dump. `FD39FFE7`
keeps product create mandatory and red. Do not treat the closed
probe as a finished product. Do not create an uncleanable product.

`AD8966F2` phone dump is delivered and unsaved. Do not remake that dump.

`C0721A14` customer-detail **Opret faktura** inspect is delivered
and closed on `5fa106c`. Path `contacts_customer`. Tagged name
visible. **Ret** count 1. Exact **Opret faktura** count 0. Role
`none`. Href `none`. No click. `proved_prebind=none`. `UI_CHANGED`.
Customer deleted. Absence proved. This alternative route is closed.
Do not remake.

`31B0C7A6` Ember inspect is delivered and closed. Ember view is present
(`view_registry`, `pickerfield`, `ember_digit` id class). No
allowlisted selection, collection, open state, or methods.
`unique_normal_action=false`. `UI_CHANGED`. No click. No customer.
Do not remake this inspect. Do not invoke the view.

Fiber inspect is delivered and closed. `fiber_key_class=none`.
`unique_normal_action=false`. `UI_CHANGED`. Do not remake.

Listener contract (`28C8FBC8`) is delivered, closed, and unsaved.
Nine sanitized rows. Input `keydown` / `focus` / `blur` / `other` /
`mouseup`. Overlay `mousedown`. Pickerfield `other` / `other` /
`click`. All bubble. No property categories. No accepted key. No
named invoke. `unique_normal_action=false`. `UI_CHANGED`. No click.
No customer. Do not remake Ember, fiber, or the `452E0773` locator
dump. Do not infer `click_open`. Stay red.

Structure compare is closed on `8feb636`. Kunde is `pickerfield` plus
`data-cy` and overlay. Bills is `input_wrapper` plus search plus
portal list. `same_family=false`. `transferable_action=none`.
`unique_normal_action=false`. `UI_CHANGED`. No click. No customer.
Do not copy the bills wrapper. Do not remake Ember, fiber,
listener, or this compare.

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
instrumented post-click dump (`07600147`), the descendant map
(`E87B6AEF`), the Ember inspect (`31B0C7A6`), the fiber inspect,
the listener contract (`28C8FBC8`), the structure compare, and
the customer-detail **Opret faktura** inspect (`C0721A14`),
the product delete-chrome recapture (`D326FFB3`), the
**Vælg kunde** named-control rest dump (`hit_is_contact_input=true`),
and the draft-save validation-open dump (`opret_ny_count=1`,
`proved_bind=none`).
Do not type. Do not recapture routes. Do not force or evaluate clicks.
Do not sweep portals. Do not send a second diagnostic click.
Do not remake the descendant map. Do not remake the Ember inspect.
Do not remake the fiber inspect.
Do not remake the listener contract.
Do not remake the structure compare.

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

Parent `main` is already in this branch. No new parent commits.

Merged with `--no-ff` and parked. No new child commits:

- `ui_contacts_writes`
- `ui_bills_writes`
- `ui_invoices_writes` (draft only; no send or email)
- `ui_products_writes`
- `ui_ledger_writes`
- `ui_files_writes`
- `ui_org_writes` (company fields only; fail-closed on users or tokens)

No children are running. 157 old wave or review descendants stay retired
and unmerged. Do not continue, reset, or merge them.

Coverage stays red until remaining honesty families prove live FastMCP
CUD with independent review. Node complete stays false.
See `decisions.md` and `todo.md`.
