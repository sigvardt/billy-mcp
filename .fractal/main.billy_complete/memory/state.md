---
name: state
desc: Current node state for the Billy MCP complete run.
tags: [billy, coverage, ui_writes]
sources:
  - docs/superpowers/specs/2026-07-28-billy-mcp-complete-design.md
  - https://www.billy.dk/api/
created: 2026-08-16T14:29:47Z
updated: 2026-08-17T19:03:00Z
---

## Now

Owner `96908DC6` is binding. Interface writes first. API live stays deferred.
HEAD is `66b5586`. `51E18E60`, `A3AB03C3`, and `9F777B8F` dumps are
delivered and unsaved. Right-edge hit is a nameless `DIV`. Ownership
is proved: that DIV shares the smallest wrapper with
`input[name=contact]` (`contact_input_count=1`) and the stack includes
that input. One position click ran at `{x:307, y:141}`. After click:
`option_role_count=0`, GET `/v2/contacts` count 0. `UI_CHANGED`. Field
shot purged after review. JSON flags kept.
Do not repeat that click. Do not remap. `8EFD0EAD` live trace
delivered. Listeners attached before `/invoices/new`. Center click
then exact tagged type reached `value_len=19`. No `contacts`
request, no portal insert, `option_role_count=0`,
`aria_expanded_present=false`. `named_next_action=false`.
`UI_CHANGED`. Customer deleted in a fresh session. Honesty 16 stay
red. Parent `4A5CD1E7` is saved for the slice after this IR/COMMIT.
Independent review of the 8EFD0EAD dump is FAIL. Slice met the
trace contract. Invoice CUD still unbound. After-type field shot
purged. Trace JSON kept. Next COMMIT stays red. `4A5CD1E7` waits
until after that commit.
Honesty 16 stay red. Never call the API. Stay red. Do not finish.
`91A2C363` leftover Leverandør slice is closed. `A6FB8FC2` stays a
one-close constraint.

Live FastMCP draft-bill CUD passed on existing-option bind. Vision
`run_id=9920dd9476474b41aef70e6d66d24638` is `author=independent_review`,
`reviewer_verdict=accept`, `purge_verified=true`. Frame folder is gone.
Bills CUD `tool_name` values are `ui_bills_{create,update,delete}_preview`.
Discovery and get-open stay `ui_bills_*_open`. `ui_bills_update_open` and
`ui_bills_delete_open` stay registered via `RETAINED_OPEN_SHELL_TOOLS`.
Honesty 16 stay red. `complete=false`. Invoice CUD still names
`ui_invoices_*_open`. Offline invoice form helper and FastMCP live
harness landed. Independent review of that slice is FAIL.

Live invoice create last failed closed: `UI_CHANGED` `Billy Kunde
existing option is not visible.` The opener dump now has every
`5E1EDFB4` key. Live recapture: `input` is `INPUT` type text with
id and autocomplete, no `aria-*`. Thirteen owners (`DIV` then
`BODY`/`HTML`), no `FORM`, no testids, no label/for, no wrap label.
`elementFromPoint` at the input center is that same `INPUT`
(`ember-text-field`). `named_opener` is still null. After one
normal field click and after type: `aria-expanded` still null, two
hidden decoy portals, no option. A dummy `after_type` used `tag_len=15`. That is not an
existing-customer observation.
`after_type_is_existing_customer_observation` is true only for
`MCP-UI-INV-` + 8 hex with matching `value_len`. It is not a bind.
A live FastMCP create then typed that 19-char name into the proved
`INPUT` (`value_len=19`) and still had two hidden decoys and
`option_role_count=0`. Execute returned `UI_CHANGED`. The tagged
contact is gone.
Placeholder is not an opener. Honesty 16 stay red. `complete=false`.
Do not remap.

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
DOM dump before any new create. Update save is **Opdater**. Honesty 16
stay red. Bills CUD rows name preview tools.

IR FAIL on the first live bills CUD: create dump was overwritten,
typed-only vendor bind was accepted, vision `run_id` did not name the
frame folder. FIX-VERIFY split the create dump, refused typed-only
bind, and bound vision `run_id` to the frame dir.

Page-wide `get_by_text(tag)` is no longer a bind. `evaluate` is gone.
Vendor bind picks the one short portal list with **Ingen resultater**
and footer `Opret "{tag}"`, then clicks
`[class*='DropdownFooterWrapper']`. Live chosen bind is
`scoped:portal_footer`. A leftover-footer count error is not a bind.
After bind, wait for the vendor dialog to close. Fill `billDate` and
line amount without a prior click. Live create dump now has tag,
vendor, date, amount `1,00`, **Gem som kladde**, and
`vendor_bind=scoped:portal_footer`. Draft save now inspects the exact
**Gem som kladde** button and uses `mouse.click` at the center. A
`force=True` locator click is not persist proof. Live inspect after
that dump is visible, enabled, and covered:
`hit_target=DIV.ds-moved-with-portal`. Execute waits for every visible
`.ds-moved-with-portal` node, then Tabs once. The overlay stays.
Execute now observes the leftover and closes only that portal: vendor
search toggle for the typeahead list, or **Gem** on a visible **Opret
leverandør** dialog. The leftover dump names role, heading, and
owning control. A second close is forbidden. A live run clicked that
modal **Gem**; save hit stayed `DIV.ds-moved-with-portal`. Execute
returns `UI_CHANGED` `source=leftover_portal` and does not click save.
Do not press Escape. Persist still has no POST `/v2/bills`.
Offline tests no longer write the owner save dump. Bills CUD
`tool_name` values are preview. Do not green. Do not finish. Do not
accept vision `3af923d562b546d597e9f156b5c3227f`.

## Review

Honesty on the 16 CUD rows still holds. Node complete stays false.
Offline org-bind wiring is in. One live contacts CUD used a second
session for read-back and a third session for absence. Same-session
accept plus an inverted mapping order failed independent review. The
accept record and purge stay. Mapping now points at preview after that
recorded verdict.

See `decisions.md` and `todo.md`.
