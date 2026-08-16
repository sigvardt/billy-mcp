---
name: ui_bills_writes
desc: Ticketed UI bill create, update, and delete. Draft-only. Never pays.
tags: [billy, ui, bills, writes, tickets]
sources:
  - wiki/ui_write_ticket_protocol.md
  - radio:9F2EC46E
created: 2026-08-16T14:35:00Z
updated: 2026-08-16T14:35:00Z
---

# ui_bills_writes

Six FastMCP tools preview and ticket draft bill writes. Preview issues a
ticket and writes nothing. Execute accepts only `confirmation_ticket`.
Default execute consumes the ticket and refuses live mutation until root
radios a live slot. No Billy interface submit has run yet.

This lane never calls `https://api.billysbilling.com/v2`. Qualification is
`server.call_tool`, not `BrowserRuntime`. Root greens
`ui.parity.bills.create`, `ui.parity.bills.update`, and
`ui.parity.bills.delete` only after a live MCP proof.

Shared ticket rules live in [[ui_write_ticket_protocol]]. Open-only shells
stay read-only: [[ui_bills_create_open_shell]],
[[ui_bills_update_open_shell]], [[ui_bills_delete_open_shell]].

## Tools

| Tool | Input | Effect |
| --- | --- | --- |
| `ui_bills_create_preview` | `unique_tag` | Bind a draft create. No submit. |
| `ui_bills_create_execute` | `confirmation_ticket` | Consume the create ticket. Submit only with a live-slot submitter. |
| `ui_bills_update_preview` | `id`, `unique_tag` | Bind a draft update. No submit. |
| `ui_bills_update_execute` | `confirmation_ticket` | Consume the update ticket. Submit only with a live-slot submitter. |
| `ui_bills_delete_preview` | `id`, `unique_tag` | Bind a draft delete. No submit. |
| `ui_bills_delete_execute` | `confirmation_ticket` | Consume the delete ticket. Submit only with a live-slot submitter. |

Every preview binds `draft_only: true`. Payment, approve, email, and send
fields are rejected (`extra="forbid"`). Tickets expire in at most five minutes
and can be consumed once. Replay, expiry, and wrong-tool mismatch fail closed.

## Fail closed

- Never pay a bill. Never click Registrer betaling, Godkend, Træk, or Upload.
- Never send invoices or email. Never submit VAT or filings.
- Never change users, access, tokens, or subscription.
- Default execute refuses live submit until root radios a live slot. Contacts
  family is first (radio `9F2EC46E`).
- Unique tagged names only. Create first as a draft.

## Cleanup

After a live draft exists, delete it or restore the prior fields. Keep only a
non-sensitive vision record. Purge raw frames. Second-session read-back is a
second UI login, not an API GET.

## Tests

- Offline: `tests/unit/test_ui_bills_writes.py` (preview no-submit, execute
  once, replay, expiry, wrong tool).
- Live file: `tests/live/test_ui_bills_writes.py` records the live-slot
  blocker through `call_tool`. It does not skip a submit.
