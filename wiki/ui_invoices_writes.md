---
name: ui_invoices_writes
title: UI invoice ticketed draft writes
desc: Ticketed FastMCP preview and execute tools for Billy invoice draft create, update, and delete. Never send, email, or Godkend.
tags: [billy, ui, invoices, writes, tickets]
sources:
  - wiki/ui_write_ticket_protocol.md
  - radio:96908DC6
  - radio:EC676F84
  - radio:9310BC17
  - radio:B9C4FA7C
  - radio:DECEA79B
created: 2026-08-16T14:30:00Z
updated: 2026-08-19T04:10:00Z
---

# UI invoice ticketed draft writes

Family module `src/billy_mcp/ui_writes/invoices.py` registers six FastMCP tools
through `register_ui_invoice_write_tools`. Shared ticket rules live in
[[ui_write_ticket_protocol]]. Kunde bind lives in [[ui_invoices_writes]] helpers
`invoices_kunde.py` and `invoices_form.py`.

Preview performs no Billy mutation. Execute accepts only `confirmation_ticket`.
The UI lane never calls `https://api.billysbilling.com/v2` with an API token.
Qualification is FastMCP `call_tool`, not `BrowserRuntime` as pass proof.

## Tools

| Tool | Input | Effect |
| --- | --- | --- |
| `ui_invoices_create_preview` | `contact_name`, `product_name`, `line_description`, `unit_price`, `action`, `save_cta`, `organization_id` | Issue ticket. CTA must be `Gem som kladde`. `unit_price` must be `> 0`. `product_name` must name an existing product. |
| `ui_invoices_create_execute` | `confirmation_ticket` | Consume ticket. Runtime submitter binds Kunde then clicks draft save. |
| `ui_invoices_update_preview` | `contact_name`, `line_description`, `unit_price`, `action`, `save_cta`, `organization_id` | Issue ticket. CTA must be `Gem som kladde`. `unit_price` must be `> 0`. Open is the exact `li[role=row]`, not a POST id. |
| `ui_invoices_update_execute` | `confirmation_ticket` | Consume ticket. Types **Enhedspris** `2,00` once, clicks **Opdater** if shown, then a second session must read that price. A header `PUT /v2/invoices/:id` is not persist. Line persist is `PUT /v2/invoiceLines/:id`. |
| `ui_invoices_delete_preview` | `contact_name`, `action`, `save_cta`, `organization_id` | Issue ticket. CTA must be `Slet`. Open is the exact `li[role=row]`. |
| `ui_invoices_delete_execute` | `confirmation_ticket` | Consume ticket. Unique **Mere**, exact **Slet**, post-Slet dump, then exact **Ja, slet faktura**. Generic **Ja, slet** is the wrong confirm. |

`action` must be `draft_create`, `draft_update`, or `draft_delete`. Use unique
tagged names such as `MCP-UI-INV-...`. Create a tagged customer first with
`ui_clients_*` tools. Create a tagged product with `ui_products_*` tools.
Confirm both names in a fresh interface session before any invoice preview
(`EC676F84`, `56354201`). Do not use a leftover supplier as Kunde.
Delete the draft invoice first, then the product, then the customer.
Owner `59A3A933`: update and delete open `/invoices`, find the exact
visible customer text, scope to ancestor `li[role=row]`, and click.
Do not `goto` a create POST id. A header `PUT /v2/invoices/:id` is not
persist (`B9C4FA7C`, `DECEA79B`). Official docs update only fields in
the hash and forbid sending `lines` on an existing invoice. Line price
is `PUT /v2/invoiceLines/:id` `unitPrice`. Persist is that 2xx plus a
fresh row-open that shows the ticket **Enhedspris**. Owner `DECEA79B`
still has 1,00 on `MCP-UI-INV-6CDB396B`. Update stays red until a fresh
session shows 2,00. Then delete the six leftover triples. Do not treat
an unchanged Ember dirty-check as success. Owner `F1A2EFC2` /
`3CB4D807`: the exact control is a visible main-frame INPUT
`name=unitPrice` `placeholder=Enhedspris` on the leftover edit
URL. Update waits for that input, fills `2,00` once, and reads
the same locator before Tab. Owner `3D5A9B9C`: do not click a
product tag or guessed row. Headless zero-input is a render miss.
If the input is still absent, return sanitized URL, heading,
exact-input count, product-text count, and input count. No
seventh invoice was created.

Owner `EC676F84`: the Kunde control works. An empty customer dataset shows
textbox **Vælg kunde**, **Ingen kontakter fundet**, and **Opret ny**. Do not
patch or probe the dropdown. Owner `9310BC17`: create and confirm the
customer first, then start a fresh session or hard-navigate `/invoices/new`
before opening the chevron. `submit_draft_invoice` closes the bootstrap page
and opens a new Playwright page before create, update, and delete.
`bind_kunde` clicks `[data-cy='dropdown-icon']` in the contact
`.pickerfield`, then picks the exact tag. `chevron_offset_from_box` is
fallback. Type is last. After bind, `fill_priced_line` writes
**Evt. beskrivelse**, confirms **Antal** is 1, and fills **Enhedspris**
from the ticket `unit_price`. Live GET then showed `grossAmount=1`.
It opens **Vælg produkt** and picks the exact ticket
`product_name`. It never clicks **Opret ny**. A missing picker or
missing tag is `UI_CHANGED`. Preview rejects a missing product name
and a missing or non-positive price (`1F1B34F8`).
A preloaded invoice page is a stale-session bug, not a missing control.
`submit_draft_invoice` closes the bootstrap page and opens a new Playwright
page before create, update, and delete (`9310BC17`, `32662804`). Browser
egress allows PUT prefix `/v2/invoices/` for the SPA draft save (never
collection PUT, never PATCH, never emails) and GET prefix `/v2/invoiceLines`
so the line editor can render. Do not allow PUT `/v2/invoiceLines/` unless a
captured blocked XHR names that path (`D859572B`). A 2xx PUT `/v2/invoices/:id`
means the SPA save ran. Header PUT 2xx is still not Enhedspris persist.
Fresh-session **Enhedspris** `2,00` is. Delete uses unique **Mere**, then
exact **Slet** (`70DB45E6`). Owner `4EAEAFFD`: capture post-Slet
before any confirm click. After one **Slet** click, write
`inspect-live-invoices-post-slet.json` with heading, path class, active
element, `candidates`, dialog counts, `hit_tag`, `delete_seen`, and
`navigated`. Owner `E8EA9823`: each `dialog`, `alertdialog`, and
remaining `aria-modal` candidate records `role`, allowlisted labels,
geometry, `z_index`, and `active_contained`. Prefer the `A` ancestor
of the unique **Slet** text. Live FastMCP leftover recapture:
`hit_tag=a`, `candidates=[]`, `dialog_count=0`,
`alertdialog_count=0`, `overlay_count=0`, `delete_seen=false`,
`navigated=false`. Empty `candidates` is valid after those
locators are counted. Owner `D2FD1919`: after that dump, click
exact **Ja, slet faktura**. Generic **Ja, slet** is the wrong
confirm. Then require DELETE 2xx and a fresh-session absence.
Do not page-wide sweep. Do not ask Joakim to inspect routine UI.

Kunde bind is an existing-option pick after a named opener. The live
`input[name=contact]` field is typeable (250x40) and is **not** the bills
typeahead: `wrapper_count=0`, `search_trigger=false`, no caret, no
`aria-expanded`, two hidden empty decoy portals. Typing the tag there is not
a bind. A 15-char dummy `after_type` is not an existing-customer
observation. Existing-customer type uses a FastMCP-created
`MCP-UI-INV-` + 8 hex name in that same `INPUT`. A live type of that
19-char name reached `value_len=19` and still showed two hidden decoys,
`option_role_count=0`, and no bind. Extra keys on that field
are not a bind. Typed-only repeats are closed (`51E18E60`). The
widget-contract dump records `autocomplete_token` (allowlisted),
`list_present`, `datalist_count`, `datalist_option_count`,
`visible_input_count`, an accessibility snapshot of counts only, and
a redacted field-shot flag (`present`, `bytes`, box). Pixels stay
outside git. Live recapture: `autocomplete_token=off`, `list_present=false`,
`datalist_count=0`, `datalist_option_count=0`, `visible_input_count=11`,
accessibility snapshot has no listbox. Field shot was reviewed and
purged. A chevron on that crop is input chrome, not a guessed selector.
`A3AB03C3` recaptures the chevron **position** on the same
`input[name=contact]`: `right_edge_offset` (`dx = w - 8`,
`dy = h // 2`), `right_edge_element_from_point`,
`right_edge_same_input`, allowlisted `appearance_token` /
`background_image_kind` / `before_content_kind` /
`after_content_kind`, and `input_child_count`. Never store CSS
urls or pseudo content. One `locator.click(position=)` runs only
when `right_edge_same_input` is true. Wait for a visible option
before type or select. Live recapture: offset `{dx:242, dy:20}` on
the 250x40 field. Center hit is `INPUT` name `contact`. Right-edge
hit is a `DIV` with no name, testid, or allowlisted class tokens, so
`right_edge_same_input=false` and no click ran. Appearance and
background-image kinds are `none`. No `::before`/`::after` content.
`input_child_count=0`. If the right-edge hit is not that input, do
not click. `9F777B8F` then recaptures that nameless DIV's ownership:
`right_edge_elements_from_point_stack` (max 8, allowlisted tokens
only), `hit_box`, `hit_pointer_events`, `hit_role`,
`hit_name_present`, `hit_testid`, `hit_class_tokens`,
`hit_direct_parent`, `hit_contained_by_input`, `hit_contains_input`,
`hit_shares_smallest_wrapper`, `smallest_wrapper`, and
`nearest_clickable_ancestor`. Never store ids or accessible names.
One `page.mouse.click` at the dumped page point runs only when
`div_belongs_to_kunde_control` is true: shared wrapper with
`contact_input_count == 1` and the stack or nearest clickable
ancestor names the contact input. Live recapture: hit box `40x40`
at the field's right edge, stack includes `INPUT` name `contact`,
smallest wrapper is one `ember-view` `DIV` with
`contact_input_count=1`, so ownership was proved and one position
click ran at `{x:307, y:141}`. After that click: two hidden decoys,
`option_role_count=0`, GET `/v2/contacts` count 0. No type. Execute
returned `UI_CHANGED`. If ownership is not proved, do not click. No dump-named action. Count-only GET `/v2/contacts` after
type is 0. `8EFD0EAD` then traces the failed full flow with listeners attached
**before** `/:org_slug/invoices/new` and before any focus/click/type. The
trace dump records `listener_attached_before_form`, redacted `requests`
(`method`, `path_class`, `status`, `timing_ms`), `console_categories`
(`script` / `pageerror` / `other` counts only), `portal_inserted`,
`portal_count`, `option_role_count`, and `active_element`
(`tag`, `name_token`, `aria_expanded_present`). Never store bodies, raw
URLs, query strings, IDs, or customer text. One center click on the
proved `input[name=contact]` and one exact tagged type run only while
those listeners are on. A follow-up option click runs only when the
trace names a next action and a visible existing option exists.
Otherwise `UI_CHANGED`. Live recapture: listeners on before form
open. After center click and exact tagged type, `value_len=19`,
`portal_inserted=false`, `option_role_count=0`, no `contacts`
`path_class`, `named_next_action=false`, `UI_CHANGED`. `4A5CD1E7`
then records phase-scoped `event_counts` (`focus` / `input` /
`change` / `keydown` / `keyup` on `name=contact` only),
`console_delta`, allowlisted `errors` (`error_class`, 16-char
`fingerprint`, `phase`, `source_class`), and
`pageerror_unrelated_at_rest`. Never store message text, stack
arguments, or typed keys in git. Detailed scrubbed shapes live
only under `~/.local/share/billy-mcp/` and are purged after
review. Live after_type named `input=19` `keydown=19` `change=0`
with no contacts request, so one `dispatch_event("change")` ran
after that dump. That event dump is closed. Do not dispatch
`change` again. `F12B607E` then names the five `/v2/` bootstraps
collapsed as `other_v2`. Committed request rows add allowlisted
`route_class`, `timing_bucket` (`0_49` / `50_99` / `100_249` /
`250_499` / `500_plus`), and first-observation `phase`. Sanitized
`route_template` values stay owner-only and are purged after
review. Never store raw URLs, query strings, UUIDs, or customer
text. If a contact-adjacent class (`contactPersons`,
`contactBalancePayments`, `contactBalancePostings`) loads at rest,
wait only for that class before type. Never issue the route.
Otherwise `UI_CHANGED`. Live recapture: the five rest rows are
`user`, `user`, `user`, `organizations`, and one unnamed
`other_v2`. `contact_dataset_preloaded=false`. `452E0773` then
records the loaded control contract on that already-open form:
`input_listener_types`, `wrapper_listener_types`, sanitized
listener locators (`script_basename`, 16-char `script_hash`,
`line`, `column`), wrapper `data-*` names without values,
`wrapper_class_tokens`, and one `binding_script` row or null.
Never store source text or URLs. Live recapture: closest wrapper
is `ember-view` `super-field` `pickerfield` with `data-cy` (value
omitted). Input listeners are `keydown` / `focus` / `blur` /
`other` / `mouseup` on `legacy-core.:id.js`. Wrapper listeners
include `click`. Binding is `name_quoted_contact` in
`react-web-components.:id.js`. That classifies as `click_open`.
One wrapper click ran. `option_role_count=0`. `UI_CHANGED`. The
live dump test no longer repeats that click. Do not type or
recapture routes. No Tab, Enter, or blur. The opener dump records
parent and three ancestor class tokens, sibling/uncle search, exact **Kunde**
label count, `contactId` count, combobox count, ember-power-select trigger
count, and placeholder token flags (never the raw placeholder). It also
records the `5E1EDFB4` ownership fields as non-PII flags only: exact input
(tag, type, id present, autocomplete present, disabled, readonly, `aria-*`
names), owners until `FORM`, label/for and wrapping-label flags, aria
relationships, active element flags, roles/names/states, box, pointer-events,
z-index, and `elementFromPoint` at the input center. Never store the tag,
raw placeholder, or raw accessible name. After the resting dump, one normal
click on that same field is the observation click, then type. Bind only after
that dump names `sibling_search`, `uncle_search`, `combobox`, `contact_id`,
or `power_select_trigger`, then a visible option is clicked. A live dump of
the contact field shows no `FORM`, no label/for, no aria expander, and
`elementFromPoint` on the input itself. A placeholder is not an opener.
Generic name fill is not a bind. Page-wide tag click is not a bind. Create
footer is last resort only when an exact option exists. Stay red until a
visible option is clicked.

## Fail closed

Refuse `Godkend`, `Godkend og send`, `Send`, email, and any preview CTA other
than `Gem som kladde` (create/update) or `Slet` (delete). Preview returns
`VALIDATION_ERROR` and does not issue a ticket.

Default runtime submitter is armed for draft only. Tests may inject a recorder
that never talks to Billy.

## Coverage

`ui.parity.invoices.create`, `ui.parity.invoices.update`, and
`ui.parity.invoices.delete` stay `implemented=false` and `live_tested=false`
until independent review accepts a live FastMCP CUD and purge is verified.
Do not remap `tool_name` to preview before that accept.

Discovery and get-open stay `ui_invoices_*_open`.

## Cleanup

Delete drafts created for live proof, then the tagged customer, in reverse
dependency order. Prove absence in a fresh session. Do not send, approve, or
email those drafts during cleanup.

## Post-click Kunde dump

`07600147` records what one `pickerfield` click opens. Role-option zero is
not a closed picker. Attach a scoped `MutationObserver` on the contact
input, the `pickerfield` wrapper, and any initially hidden linked subtree.
Click that wrapper once. Store only newly visible or changed allowlisted
nodes: tag, role, interactive, class-token categories, data-attribute
names, text length and hash, exact-match booleans, box, z-index, ownership
path, AX name hash. Never store raw names or text. `exact_match_target` is
true only when exactly one visible interactive node matches the tagged
customer. Helper: `src/billy_mcp/ui_writes/invoices_kunde_post_click.py`.
Owner dump: `~/.local/share/billy-mcp/inspect-live-invoices-kunde-post-click.json`.
Live recapture: `baseline_input_tag=INPUT`, wrapper categories include
`pickerfield`, `baseline_hidden_subtree_count=2`, `click_count=1`,
`changed_node_count=0`, `exact_match_target=false`, `UI_CHANGED`. The
scoped subtree did not expose a newly visible interactive match. Do not
sweep the rest of the page. The wrapper-center click is closed. Do not
repeat it.

## Descendant map

`E87B6AEF` records visible descendants inside the proved `pickerfield`
only. Do not click the wrapper center. For each descendant store tag
category, role, class-token categories, `data-*` names, `{dx,dy,w,h}`
from the wrapper, `pointer-events`, and listener types. Omit text and
every attribute value. Classify the already-loaded wrapper click
handler as `input_ignored`, `suffix_accepted`, `toggle_accepted`, or
`none`. Never persist source. `unique_target` is true only when exactly
one unused interactive descendant remains (not the contact `INPUT` and
not the already-clicked overlay suffix). Helper:
`src/billy_mcp/ui_writes/invoices_kunde_descendants.py`. Owner dump:
`~/.local/share/billy-mcp/inspect-live-invoices-kunde-descendants.json`.
Live recapture: two visible descendants, the contact `INPUT` at
`{dx:0,w:210,h:40}` and a nameless overlay `DIV` at
`{dx:242,w:40,h:40}`. `unique_target=false`.
`wrapper_handler_guard=none`. `UI_CHANGED`. Do not click either
target. Do not repeat the wrapper-center click.

## Ember view inspect

`31B0C7A6` records the already loaded Ember view or component that
owns the proved `pickerfield`. DevTools `Runtime.getProperties`
only. Do not click. Do not call `Ember.get`, `view.get`, or any
view method. Persist only allowlisted name tokens, value types,
and booleans for bound selection, candidate collection, open
state, and named open/select/filter actions. Never persist raw
values, ids, source, or URLs. `unique_normal_action` is true only
when exactly one named action is present and a unique unused DOM
target exists. A method with no new DOM target is `UI_CHANGED`.
Do not inspect React fiber in this slice. Helper:
`src/billy_mcp/ui_writes/invoices_kunde_ember.py`. Owner dump:
`~/.local/share/billy-mcp/inspect-live-invoices-kunde-ember.json`.
Live recapture: `ember_global_present=true`,
`view_registry_present=true`, `wrapper_ember_id_class=ember_digit`,
`lookup_class=view_registry`, `view_present=true`,
`view_constructor_token=pickerfield`. `property_rows` empty.
`method_name_tokens` empty. All named actions `none`.
`unique_normal_action=false`. `UI_CHANGED`. No click. No customer.
Empty `property_rows` is not a bind and is not a reason to remake
this inspect. Do not invoke the view.

## React fiber inspect

The next different capture records the React fiber on the proved
contact `INPUT` and closest `pickerfield`, if present. Ember inspect
skipped own-properties whose names start with `_`, so
`__reactFiber$` was never read. The name bind lives in
`react-web-components.:id.js`. Do not remake Ember inspect. Do not
click. Persist only `fiber_key_class`, `wrapper_fiber_key_class`,
`type_token`, `prop_rows`, method tokens, selection / collection /
open flags, `host_class`, `unique_fiber_host`, and
`unique_normal_action`. Never persist fiber key suffixes, raw
values, ids, or source. `unique_normal_action` is true only when
exactly one named open/select/filter action is present and
`unique_fiber_host` is true (one unused host that is not the
contact `INPUT`, not wrapper-center, and not the overlay at
`dx=242`). Helper: `src/billy_mcp/ui_writes/invoices_kunde_fiber.py`.
Owner dump:
`~/.local/share/billy-mcp/inspect-live-invoices-kunde-fiber.json`.
Walk `return` at most 8. Do not invoke fiber methods, `dispatch`,
or `setState`. Do not install React DevTools. Live recapture:
`fiber_key_class=none`, `wrapper_fiber_key_class=none`,
`type_token=none`, empty `prop_rows`, empty methods, all named
actions `none`, `host_class=none`, `unique_fiber_host=false`,
`unique_normal_action=false`, `UI_CHANGED`. No click. No customer.
The two proved DOM nodes have no `__reactFiber` key. That is not a
bind and is not a reason to remake Ember inspect or click. Do not
remake this fiber inspect.

## Listener contract

`28C8FBC8` records a sanitized event contract on the proved contact
`INPUT`, overlay `DIV` at `{dx:242,w:40,h:40}`, closest
`.pickerfield`, and nearest ancestors (cap 8). Chrome DevTools
`DOMDebugger.getEventListeners` once per host. No `depth`. No
`pierce`. Classify a short already-loaded source window at the
listener `scriptId` + line + column, then delete the source.
Persist only `event_type`, `phase` (`capture` / `bubble`),
`target_category`, `event_property_categories`,
`accepted_key_category`, `invoked_action_token`, and
`unique_normal_action`. Never persist source, URLs, locators,
`scriptId`, ids, or values. A `click` listener with no named
invoke is not unique. Do not reuse the `452E0773` `click_open`
inference. Do not remake Ember inspect or fiber inspect. Do not
click. Helpers: `src/billy_mcp/ui_writes/invoices_kunde_listeners.py`
and `src/billy_mcp/ui_writes/invoices_kunde_listener_inspect.py`.
Owner dump:
`~/.local/share/billy-mcp/inspect-live-invoices-kunde-listeners.json`.
`unique_normal_action` is true only when exactly one pointer or
named-key keyboard row also names an invoke. Else `UI_CHANGED`.
Live recapture: nine rows. Input has `keydown` / `focus` / `blur` /
`other` / `mouseup`. Overlay has `mousedown`. Pickerfield has
`other` / `other` / `click`. All bubble. Empty property categories.
`accepted_key_category=none`. `invoked_action_token=none`.
`unique_normal_action=false`. `UI_CHANGED`. No click. No customer.
The pickerfield `click` is not unique because it names no invoke.
That is not a bind and is not a reason to remake Ember, fiber, or
the `452E0773` locator dump.

## Structure compare

The next slice after a non-actionable listener dump compares only
the sanitized invoice Kunde control structure to the live-proved
bills Leverandør picker. Helper:
`src/billy_mcp/ui_writes/invoices_kunde_structure.py`. Owner dump:
`~/.local/share/billy-mcp/inspect-live-invoices-kunde-structure.json`.
Persist input name tokens, wrapper families, Kunde data-attr names,
search triggers, overlay present, list hosts, option-role counts,
`same_family`, `transferable_action`, `unique_normal_action`, and
proved binds. Map already delivered dumps. Do not remake Ember,
fiber, listener, descendant, or post-click dumps. Do not click or
type. `same_family` is true only when both sides are
`input_wrapper` plus search plus `ds_dropdown_portal`.
`transferable_action` is non-`none` only when the invoice rest page
has an unused bills-family host on the contact field. Else
`UI_CHANGED`. Do not copy the bills wrapper onto this field. Live
map from existing dumps: Kunde `pickerfield` plus `data-cy` and
overlay at `dx=242`. Bills `input_wrapper` plus search plus portal
list. `same_family=false`. `transferable_action=none`.
`proved_kunde_bind=none`. `proved_bills_bind=scoped_existing_option`.
`unique_normal_action=false`. `UI_CHANGED`. No click. No customer.

## Customer-detail Opret faktura prebind

Parent `C0721A14` checks a different route: an exact **Opret faktura**
action on a tagged customer detail. Helper:
`src/billy_mcp/ui_writes/invoices_customer_detail_prebind.py`. Owner
dump:
`~/.local/share/billy-mcp/inspect-live-invoices-customer-detail-prebind.json`.
Create one `MCP-UI-INV-` + 8 hex customer through FastMCP. Fresh
session confirms the name. Open that row with `open_named_customer`.
Do not use `ui_clients_get_open`. Persist only path class, tagged-name
visible, exact **Ret** count, exact **Opret faktura** role and count,
href path class, href query token class, clicked, destination heading
token, contact input length, tag match, `unique_normal_action`,
`proved_prebind`, and `missing_keys`. Never persist ids, URLs, query
values, or names. `unique_normal_action` is true only when exactly one
**Opret faktura** control is visible. `proved_prebind` is
`customer_detail_opret_faktura` only when the destination heading is
**Opret faktura** and the contact field shows the tagged name. Else
`UI_CHANGED`. Opening create is safe. Do not save until prebind is
proved. Live recapture: path `contacts_customer`, tagged name visible,
**Ret** count 1, **Opret faktura** count 0, role `none`, href `none`,
no click, `proved_prebind=none`, `UI_CHANGED`. Customer deleted.
Absence proved. This alternative route is closed. Do not start another
identity-only inspector.

## Vælg kunde named control

Official first-invoice support says click **Vælg kunde**, then **Opret
ny**. Helper: `src/billy_mcp/ui_writes/invoices_vaelg_kunde.py`. Owner
dump:
`~/.local/share/billy-mcp/inspect-live-invoices-vaelg-kunde.json`.
Open `/:org_slug/invoices/new` through FastMCP
`ui_invoices_create_open`. Persist only button/link/other counts,
`unique_vaelg_kunde`, `hit_is_contact_input`, `clicked`,
`opret_ny_count`, `option_role_count`, `proved_bind`, and
`missing_keys`. Never persist ids, URLs, or names. Click only when
exactly one named control exists and it is not the contact `INPUT`.
`proved_bind` is `vaelg_kunde_existing_option` only after that click
picks a FastMCP-created existing customer. Else `UI_CHANGED`. Live
recapture: button 0, link 0, other 0, `hit_is_contact_input=true`,
`unique_vaelg_kunde=false`, no click, `proved_bind=none`,
`UI_CHANGED`. Official **Vælg kunde** is the input placeholder, not a
separate named control. Do not remake this rest dump. Do not fall
back to closed picker probes. Invoice CUD stays red and is not
finished.

## Draft-save validation open

Official first-invoice shot 2 shows the customer list after field
validation: tooltip **Dette felt skal udfyldes.**, empty copy
**Ingen kontakter fundet.**, footer **Opret ny**. Helper:
`src/billy_mcp/ui_writes/invoices_draft_save_validation.py`. Owner
dump:
`~/.local/share/billy-mcp/inspect-live-invoices-draft-save-validation.json`.
Create one `MCP-UI-INV-` + 8 hex customer through FastMCP. Confirm
in a fresh session. Open `/:org_slug/invoices/new` through
`ui_invoices_create_open`. Persist only
`validation_message_present`, `ingen_kontakter_count`,
`opret_ny_count`, `option_role_count`, `gem_clicked`,
`invoice_persisted`, `proved_bind`, and `missing_keys`. Never
persist ids, URLs, or names. One click of exact **Gem som kladde**.
Do not click **Opret ny**. Do not click **Godkend**.
`proved_bind` is `draft_save_validation_existing_option` only when
that click leaves `invoice_persisted=false`, shows the official
validation copy or an open list, and a unique existing option
matches the tagged customer. Else `UI_CHANGED`. Live recapture:
`gem_clicked=true`, `invoice_persisted=false`,
`validation_message_present=false`, `ingen_kontakter_count=0`,
`opret_ny_count=1`, `option_role_count=0`, `proved_bind=none`,
`UI_CHANGED`. Page-wide **Opret ny** is not a proved customer-list
open: official shot 1 has that label on the sidebar. Validation
copy and empty-list copy were absent. No existing-option bind. Do
not remake this dump, the **Vælg kunde** rest dump, or the closed
picker set. Do not click **Opret ny**.

## Draft-save scoped capture

`2683CE6B` requires a contact-owned dump after empty **Gem som
kladde**, not another page-wide count. Helper:
`src/billy_mcp/ui_writes/invoices_draft_save_scoped.py`. Owner
dump:
`~/.local/share/billy-mcp/inspect-live-invoices-draft-save-scoped.json`.
Create one `MCP-UI-INV-` + 8 hex customer through FastMCP. Confirm
in a fresh session. Open `/:org_slug/invoices/new` through
`ui_invoices_create_open`. Attach a read-only observer to
`input[name=contact]`, the closest `.pickerfield`, in-control
ancestors and siblings, and pre-existing `aria-controls` /
`aria-owns` / `for` links. Do not observe `document.body`. One click
of exact **Gem som kladde**. Persist only `gem_clicked`,
`invoice_persisted`, `contact_input_present`,
`pickerfield_present`, `active_element_category`,
`mutation_owned_count`, `scoped_rows` (cap 16), `unique_action`,
`unique_action_owned_by_picker`, `proved_bind`, and
`missing_keys`. Each row stores tag, role, visible, interactive,
exact-match token, relative box, z-index, ownership path tokens,
and `is_mutation_owned`. Never persist ids, URLs, or names.
`unique_action` is `existing_option` only for one picker-owned
visible option, or `inline_opret_ny` only for one picker-owned
footer with no option. Sidebar **Opret ny** is not owned.
`proved_bind` is `draft_save_scoped_existing_option` only when
that existing option is unique and the invoice did not persist.
Else `UI_CHANGED`. Do not click **Opret ny**. Do not click
**Godkend**. `8EBC19D5` forbids a body-wide observer and forbids
raising the row cap. Allowed recapture after that fix:
`gem_clicked=true`, `invoice_persisted=false`,
`contact_input_present=true`, `pickerfield_present=true`,
`active_element_category=gem_button`, `mutation_owned_count=1`,
seven pickerfield rows (chevron overlay only),
`unique_action=none`, `unique_action_owned_by_picker=false`,
`proved_bind=none`, `UI_CHANGED`. No option. No picker-owned
footer. Contact-owned roots have no unique action. Choose a
different normal-interface path next. Do not remake this dump,
the page-wide draft-save dump, the **Vælg kunde** rest dump, or
the closed picker set. Do not click **Opret ny**.

## Invoice-list Opret faktura entry

Official first-invoice and discount guides start from the invoice
index **Opret faktura** button. Current `_create_draft` skips that
and goes to `/invoices/new`. Helper:
`src/billy_mcp/ui_writes/invoices_list_opret_faktura.py`. Owner
dump:
`~/.local/share/billy-mcp/inspect-live-invoices-list-opret-faktura.json`.
Create one `MCP-UI-INV-` + 8 hex customer through FastMCP. Confirm
in a fresh session. Open the list through `ui_invoices_list`. Do
not `goto /invoices/new`. Click exact **Opret faktura** only when
the list count is 1. Persist only `list_path_class`,
`exact_list_opret_faktura_count`, `list_opret_faktura_role`,
`clicked_list_opret_faktura`, `destination_path_class`,
`destination_query_token_class`, `destination_heading_token`,
`contact_input_present`, `contact_input_value_len`,
`contact_input_matches_tag`, `option_role_count`,
`aria_expanded_token`, `unique_action`, `proved_bind`, and
`missing_keys`. Never persist ids, URLs, query values, or names.
`proved_bind` is `list_cta_prebound` only when the contact field
matches the tagged customer, or `list_cta_existing_option` only
when exactly one option is visible. Else `UI_CHANGED`. Do not type.
Do not click the picker. Do not **Gem som kladde**. Do not
**Godkend**. Live recapture: `list_path_class=invoices_empty`,
`exact_list_opret_faktura_count=1`, role `button`,
`clicked_list_opret_faktura=true`, destination `invoices_new`
with query `none`, heading `opret_faktura`,
`contact_input_present=true`, `contact_input_value_len=0`,
`contact_input_matches_tag=false`, `option_role_count=0`,
`aria_expanded_token=missing`, `unique_action=none`,
`proved_bind=none`, `UI_CHANGED`. Official list CTA lands on the
same empty closed form. Do not remake this dump, the scoped dump,
or the closed picker set.

## Create-form control derivation

`113F1E05` forbids another **Opret faktura** entry dump, including
**Tilgodehavender**. Helper:
`src/billy_mcp/ui_writes/invoices_create_form_control.py`. Owner
dump:
`~/.local/share/billy-mcp/inspect-live-invoices-create-form-control.json`.
This helper restates frozen closed-probe flags. It is **not** a new
scoped DOM/AX or page-local source inspect. Invented tokens such as
`arrow_open` are ignored. Closed evidence derives
`derived_interaction=none`, `next_slice=product_create`,
`proved_bind=none`, `UI_CHANGED`. Do not remake those dumps. Do not
click a new entry CTA.

## Live proof

`tests/live/test_ui_invoices_writes.py` drives create, update, and delete
through `create_server` `call_tool`. Independent second session after each
write. Third session for final absence. Vision record is
`author=live_test` and `reviewer_verdict=pending_review` only.
The post-click dump creates one tagged customer through FastMCP, confirms
it in a fresh session, then deletes it and proves absence.
