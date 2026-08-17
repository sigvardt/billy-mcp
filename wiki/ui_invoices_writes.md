---
name: ui_invoices_writes
title: UI invoice ticketed draft writes
desc: Ticketed FastMCP preview and execute tools for Billy invoice draft create, update, and delete. Never send, email, or Godkend.
tags: [billy, ui, invoices, writes, tickets]
sources:
  - wiki/ui_write_ticket_protocol.md
  - radio:96908DC6
created: 2026-08-16T14:30:00Z
updated: 2026-08-17T12:50:00Z
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

Kunde bind is an existing-option pick on the wrapper that owns
`input[name=contact]`. Live dump after click and after type: the field is
`input[name=contact]` (250x40), `search_trigger=false`, `page_search_count=0`,
`trigger_count=0`, `aria-expanded` absent, two hidden empty
`.ds-dropdown-list.ds-moved-with-portal` decoys, and no Ember listbox. Typing
the tagged name does not open a visible option. That is not a bind. Generic
name fill is not a bind. Page-wide tag click is not a bind. Create footer is
last resort only when an exact option exists. Stay red until a visible option
is clicked.

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
