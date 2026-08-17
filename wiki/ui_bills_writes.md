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
Default `create_server` execute uses `BrowserBillSubmitter` and the
shared write browser. Create opens `/:org_slug/bills/new`, fills vendor,
date, line amount, and `billLines.0.description`, dumps those values
plus the draft-only CTA before click, then clicks **Gem som kladde**.
Update clicks **Opdater** on `/:org_slug/bills/:id/edit` after the same
dump. Delete looks for **Slet** on edit, then the read path, then the
confirm modal. Booking, pay, pull, upload, and email CTAs are refused.
Coverage stays red until live FastMCP proof, independent vision accept,
and purge.

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
| `ui_bills_create_execute` | `confirmation_ticket` | Consume the create ticket and submit the draft. |
| `ui_bills_update_preview` | `id`, `unique_tag` | Bind a draft update. No submit. |
| `ui_bills_update_execute` | `confirmation_ticket` | Consume the update ticket and submit the draft. |
| `ui_bills_delete_preview` | `id`, `unique_tag` | Bind a draft delete. No submit. |
| `ui_bills_delete_execute` | `confirmation_ticket` | Consume the delete ticket and confirm delete. |

Every preview binds `draft_only: true`. Payment, approve, email, and send
fields are rejected (`extra="forbid"`). Tickets expire in at most five minutes
and can be consumed once. Replay, expiry, and wrong-tool mismatch fail closed.

## Fail closed

- Never pay a bill. Never click Registrer betaling, Godkend, Træk, or Upload.
- Never send invoices or email. Never submit VAT or filings.
- Never change users, access, tokens, or subscription.
- Unique tagged names only. Create first as a draft.
- Vendor is a typeahead. Official field is `contact` / `contactId`. UI
  label is **Leverandør**. Bind requires a dropdown row, **Opret
  leverandør** + **Gem**, or Enter that selects a row. A typed string
  alone is not a bind. Create pre-submit dump is a separate owner-only
  file from the update dump. Do not seed a customer via
  `ui_clients_create`.
- Date chrome stores `dd.mm.yyyy`. Amount chrome stores Danish `1,00`.
- Browser egress allows PUT prefix `/v2/bills/` only (no collection PUT,
  no PATCH). Create persist is POST 2xx only.
- The no-runtime register still returns the old live-slot blocker. That
  is not qualification.

## Cleanup

After a live draft exists, delete it or restore the prior fields. Keep only a
non-sensitive vision record. Purge raw frames. Second-session read-back is a
second UI login, not an API GET.

## Tests

- Offline: `tests/unit/test_ui_bills_writes.py` (preview no-submit, execute
  once, replay, expiry, wrong tool).
- Live file: `tests/live/test_ui_bills_writes.py` runs one tagged
  create/update/delete through `create_server` `call_tool`. Vision
  `author=live_test` / `pending_review` only.
