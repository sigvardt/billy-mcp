---
name: ui_write_ticket_protocol
desc: Shared ticket protocol and file ownership for Billy interface writes.
tags: [billy, ui, writes, tickets]
sources:
  - docs/superpowers/specs/2026-07-28-billy-mcp-complete-design.md
  - radio:96908DC6
  - radio:728BD2E4
  - radio:E004E7D5
created: 2026-08-16T14:05:51Z
updated: 2026-08-16T14:05:51Z
---

# ui_write_ticket_protocol

Interface writes use the same two-step ticket rule as API writes. Preview
performs no Billy mutation. Execute accepts only `confirmation_ticket`.

The UI lane never calls `https://api.billysbilling.com/v2`. Read-back is a
second interface session.

## Binding

`ConfirmationStore` binds execute tool name, organisation, target, canonical
request, expected effect, optional file path and digest, and optional
destination URL. Preview refuses a missing organisation id
(`ORGANIZATION_REQUIRED`). `create_server` passes its shared write `BrowserRuntime` and a second
read-back runtime (profile name plus `-readback`) into every family register.
Default execute performs the family route, fields, and submit control only
when the live URL slug matches the ticket organisation. The live URL is the
only org proof. A stored identity file is not a substitute. It returns
`submitted=True` only after a second authenticated session proves the change.
A blank `-readback` profile that lands on `/login` is `ORGANIZATION_REQUIRED`,
not proof. A second page on the same persistent context is not a second
session. Start-only is not a submit. Wrong-org execute is
`CONFIRMATION_MISMATCH` before fill or click. Tickets are process-volatile
and expire in at most five minutes. Coverage rows stay red until live FastMCP
proof.

Qualify tools through FastMCP `call_tool`, not `BrowserRuntime` as proof.

## Fail closed

Do not submit invoice send/email, payments, VAT or filings, user/access/token
or subscription changes unless a separate owner decision says so.

## File ownership

Root owns `src/billy_mcp/ui_writes/protocol.py`, the generator honesty pass,
`server.py` wiring, and this page.

Children fill one family module only:

- `contacts.py` — contacts create/update/delete
- `bills.py` — bills create/update/delete
- `invoices.py` — invoices create/update/delete (never send)
- `products.py` — products create
- `ledger.py` — daybooks create/delete, daybookTransactions create, transactions create
- `files.py` — files create (bind path and digest)
- `organizations.py` — organizations update (restore company fields; no users/tokens/subscription)

Children do not edit `generate_coverage_report.py`, `server.py`, or
`browser.py`. Root greens a parity row only after a live MCP proof.
