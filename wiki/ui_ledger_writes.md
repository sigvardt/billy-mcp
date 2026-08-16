---
name: ui_ledger_writes
desc: Ticketed UI ledger preview and execute tools, fail-closed submit rules, and cleanup order.
tags: [billy, ui, writes, ledger, daybooks]
sources:
  - wiki/ui_write_ticket_protocol.md
  - radio:7696B03D
created: 2026-08-16T14:30:00Z
updated: 2026-08-16T14:30:00Z
---

# ui_ledger_writes

Ticketed Billy interface writes for daybooks and postings. Shared ticket
rules live in [[ui_write_ticket_protocol]]. This page is the family
contract only.

## Tools

| Preview | Execute | Preview fields |
| --- | --- | --- |
| `ui_daybooks_create_preview` | `ui_daybooks_create_execute` | `name` (min length 1). Live names should use `MCP-LEDGER-` plus a unique suffix. The schema does not require that prefix. |
| `ui_daybooks_delete_preview` | `ui_daybooks_delete_execute` | `id` |
| `ui_daybook_transactions_create_preview` | `ui_daybook_transactions_create_execute` | `daybook_id`, `text` |
| `ui_transactions_create_preview` | `ui_transactions_create_execute` | `text` |

Preview issues a confirmation ticket and does not change Billy. Execute
accepts only `confirmation_ticket`. Qualify through FastMCP `call_tool`.

Coverage rows these tools target later (root greens after live proof):
`ui.parity.daybooks.create`, `ui.parity.daybooks.delete`,
`ui.parity.daybookTransactions.create`, `ui.parity.transactions.create`.
This family does not green those rows.

## Fail closed

Execute consumes the ticket and returns `submitted=false`. It does not
POST, PUT, or DELETE `https://api.billysbilling.com`. It does not drive
`BrowserRuntime`.

`register_ui_ledger_write_tools` receives only the FastMCP server and
`UiWriteProtocol`. There is no injected submitter. Root must add one
before any live mutation.

Parent hold `7696B03D`: contacts has the live slot. This family does not
submit until root radios a slot to it.

Do not send invoices or email, make payments, submit VAT or filings, or
change users, access, tokens, or subscription.

Do not invent `ui_annual_*` tools.

## Cleanup

1. Daybook create is the only live-eligible create. Use a unique
   `MCP-LEDGER-` name when a live slot exists.
2. Delete that same daybook through `ui_daybooks_delete_preview` /
   `ui_daybooks_delete_execute` after an independent second UI session
   read-back.
3. If a created daybook cannot be deleted, stop. Do not post more.
4. Daybook transaction create and Posteringer create stay unsubmitted
   until a delete or cleanup path is proven on the same tagged record.

Live proof, when a slot exists: four-state capture, purge raw frames, store
only a non-sensitive vision record.

## Tests

- Offline: `tests/unit/test_ui_ledger_writes.py` (preview no-submit,
  execute once, replay, expiry, wrong tool).
- Live-marked fail-closed: `tests/live/test_ui_ledger_writes.py` asserts
  `submitted=false` and the blocker text. It does not skip an unsafe
  submit.
