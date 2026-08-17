---
name: ui_invoices_writes
title: UI invoice ticketed draft writes
desc: Ticketed FastMCP preview and execute tools for Billy invoice draft create, update, and delete. Never send, email, or Godkend.
tags: [billy, ui, invoices, writes, tickets]
sources:
  - wiki/ui_write_ticket_protocol.md
  - radio:96908DC6
created: 2026-08-16T14:30:00Z
updated: 2026-08-17T17:45:00Z
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
not click. No dump-named action. Count-only GET `/v2/contacts` after
type is 0. The opener dump records
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

## Live proof

`tests/live/test_ui_invoices_writes.py` drives create, update, and delete
through `create_server` `call_tool`. Independent second session after each
write. Third session for final absence. Vision record is
`author=live_test` and `reviewer_verdict=pending_review` only.
