---
name: ui_contacts_writes
title: UI contacts ticketed writes
desc: Ticketed UI preview and execute tools for Billy customer create, update, and delete.
tags: [billy, ui, clients, contacts, writes, tickets]
sources:
  - wiki/ui_write_ticket_protocol.md
  - radio:40B617CE
created: 2026-08-16T14:30:00Z
updated: 2026-08-16T14:40:00Z
---

# UI contacts ticketed writes

Family module `src/billy_mcp/ui_writes/contacts.py` registers six FastMCP tools
on the shared UI write ticket protocol. Preview performs no Billy mutation.
Execute accepts only `confirmation_ticket`. This lane never calls
`https://api.billysbilling.com/v2` itself. Read-back is a second interface
session.

Root owns greening of `ui.parity.contacts.create`,
`ui.parity.contacts.update`, and `ui.parity.contacts.delete`. This family does
not mark those rows live or complete.

## Tools

| Tool | Inputs | Effect |
| --- | --- | --- |
| `ui_clients_create_preview` | `name` | Ticket only |
| `ui_clients_create_execute` | `confirmation_ticket` | Create the previewed customer |
| `ui_clients_update_preview` | `name`, `new_name` | Ticket only |
| `ui_clients_update_execute` | `confirmation_ticket` | Rename the previewed customer |
| `ui_clients_delete_preview` | `name` | Ticket only |
| `ui_clients_delete_execute` | `confirmation_ticket` | Delete the previewed customer |

Customers are located by unique tagged name, not an API id. Inputs are flat.
There is no nested `input` object. Extra fields are rejected.

Qualify through FastMCP `call_tool`. BrowserRuntime is not the pass proof.

## Fail closed

Do not send invoices or emails, make payments, submit VAT or filings, or change
users, access, tokens, or subscription from this family.

Tickets expire in at most five minutes. A ticket can be executed once. A replay
returns `CONFIRMATION_CONSUMED`. A ticket for another execute tool returns
`CONFIRMATION_MISMATCH`. An expired ticket returns `CONFIRMATION_EXPIRED`.

## Live cleanup

Live submit uses disposable names of the form `MCP-UI-C-<8hex>` and
`MCP-UI-C-<8hex>-U` after update. Session A runs create, then update, then
delete through preview and execute. Session B is an independent login that
lists customers after each step. Four-state frames are purged. Only a
non-sensitive vision record is kept.

If create or update succeeds and delete later fails, retry delete through the
same execute tool. Do not leave a tagged customer when delete can still run.

## Live status

Live qualification requires both `BILLY_BROWSER_PRIMARY_REFERENCE` and
`BILLY_BROWSER_SECONDARY_REFERENCE`. When those are unset, the live test writes
a blocker and skips. That is a credential blocker, not an unsafe skipped
submit. Root radio `40B617CE` granted the first live slot. Root greens the
three contacts parity rows only after a live MCP proof.
