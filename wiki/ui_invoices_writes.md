---
name: ui_invoices_writes
title: UI invoice ticketed draft writes
desc: Ticketed FastMCP preview and execute tools for Billy invoice draft create, update, and delete. Never send, email, or Godkend.
tags: [billy, ui, invoices, writes, tickets]
sources:
  - wiki/ui_write_ticket_protocol.md
  - radio:30D194C8
created: 2026-08-16T14:30:00Z
updated: 2026-08-16T14:35:00Z
---

# UI invoice ticketed draft writes

Family module `src/billy_mcp/ui_writes/invoices.py` registers six FastMCP tools
through the pre-wired `register_ui_invoice_write_tools` hook. Shared ticket
rules live in [[ui_write_ticket_protocol]].

Preview performs no Billy mutation. Execute accepts only `confirmation_ticket`.
The UI lane never calls `https://api.billysbilling.com/v2`. Qualification is
FastMCP `call_tool`, not `BrowserRuntime`.

## Tools

| Tool | Input | Effect |
| --- | --- | --- |
| `ui_invoices_create_preview` | `contact_name`, `line_description`, `action`, `save_cta`, optional `organization_id` | Issue ticket. CTA must be `Gem som kladde`. |
| `ui_invoices_create_execute` | `confirmation_ticket` | Consume ticket. Default submitter returns `submitted=false` and does not click. |
| `ui_invoices_update_preview` | `id`, `line_description`, `action`, `save_cta`, optional `organization_id` | Issue ticket. CTA must be `Gem som kladde`. |
| `ui_invoices_update_execute` | `confirmation_ticket` | Consume ticket. Default submitter returns `submitted=false` and does not click. |
| `ui_invoices_delete_preview` | `id`, `action`, `save_cta`, optional `organization_id` | Issue ticket. CTA must be `Slet` (Mere then Slet). |
| `ui_invoices_delete_execute` | `confirmation_ticket` | Consume ticket. Default submitter returns `submitted=false` and does not click. |

`action` must be `draft_create`, `draft_update`, or `draft_delete`. Use unique
tagged names such as `MCP-UI-INV-...`.

This family does not green coverage rows. `ui.parity.invoices.create`,
`ui.parity.invoices.update`, and `ui.parity.invoices.delete` stay
`implemented=false` and `live_tested=false` until root sees a live MCP proof.

## Fail closed

Refuse `Godkend`, `Godkend og send`, `Send`, email, and any CTA other than
`Gem som kladde` (create/update) or `Slet` (delete). Preview returns
`VALIDATION_ERROR` and does not issue a ticket.

Default submitter is unarmed: after consume it returns `submitted=false` and
does not click Billy chrome. Tests inject a recorder that never talks to Billy.

## Cleanup

Delete drafts created for live proof. Do not leave tagged `MCP-UI-INV-`
invoices in the test organisation. Do not send, approve, or email those drafts
during cleanup.

## Live submit gate

Parent radio `30D194C8` gives the live slot to the contacts family first. This
family must not click `Gem som kladde`, `Godkend`, `Send`, or email until root
radios a live slot for invoices.

When a slot opens: unique tagged draft, independent second UI session
read-back, four-state capture, purge raw frames, store only a non-sensitive
vision record, then delete the draft.

Recorded blocker: live submit is held by contacts. See
`tests/live/test_ui_invoices_writes.py`.
