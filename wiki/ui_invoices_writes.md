---
name: ui_invoices_writes
title: UI invoice ticketed draft writes
desc: Ticketed FastMCP preview and execute tools for Billy invoice draft create, update, and delete. Never send, email, or Godkend.
tags: [billy, ui, invoices, writes, tickets]
sources:
  - wiki/ui_write_ticket_protocol.md
  - radio:96908DC6
created: 2026-08-16T14:30:00Z
updated: 2026-08-18T00:20:00Z
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
| `ui_invoices_create_preview` | `contact_name`, `line_description`, `action`, `save_cta`, `organization_id` | Issue ticket. CTA must be `Gem som kladde`. |
| `ui_invoices_create_execute` | `confirmation_ticket` | Consume ticket. Runtime submitter binds Kunde then clicks draft save. |
| `ui_invoices_update_preview` | `id`, `line_description`, `action`, `save_cta`, `organization_id` | Issue ticket. CTA must be `Gem som kladde`. |
| `ui_invoices_update_execute` | `confirmation_ticket` | Consume ticket. Clicks observed draft save or **Opdater**. |
| `ui_invoices_delete_preview` | `id`, `action`, `save_cta`, `organization_id` | Issue ticket. CTA must be `Slet`. |
| `ui_invoices_delete_execute` | `confirmation_ticket` | Consume ticket. **Mere** then **Slet**, then **Ja, slet** if shown. |

`action` must be `draft_create`, `draft_update`, or `draft_delete`. Use unique
tagged names such as `MCP-UI-INV-...`. Create a tagged customer first with
`ui_clients_*` tools. Do not use a leftover supplier as Kunde.

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
repeat it. Next read-only slice maps visible descendants inside that
wrapper only.

## Live proof

`tests/live/test_ui_invoices_writes.py` drives create, update, and delete
through `create_server` `call_tool`. Independent second session after each
write. Third session for final absence. Vision record is
`author=live_test` and `reviewer_verdict=pending_review` only.
The post-click dump creates one tagged customer through FastMCP, confirms
it in a fresh session, then deletes it and proves absence.
