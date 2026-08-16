---
name: constraints
desc: Hard limits for this bills write node.
tags: [constraints]
sources: []
created: 2026-08-16T14:24:02Z
updated: 2026-08-16T14:24:02Z
---

# constraints

Owned paths only: `src/billy_mcp/ui_writes/bills.py`, `tests/unit/test_ui_bills_writes.py`, `tests/live/test_ui_bills_writes.py`, `wiki/ui_bills_writes.md`.

Reuse `UiWriteProtocol` and `ConfirmationStore`. Preview writes nothing. Execute accepts only `confirmation_ticket`.

No POST, PUT, or DELETE to `api.billysbilling.com`.

Qualify through FastMCP `call_tool`. Do not use `BrowserRuntime` as the pass proof.

Offline tests must cover preview no-submit, execute once, replay, expiry, and wrong-tool mismatch.

Live submit only after parent radio go-ahead. Contacts family is first. Unique tagged names. Independent second UI session read-back. Four-state capture. Purge raw frames. Store only a non-sensitive vision record.

Draft-only bills. Unique tags. Delete or restore. Never pay a bill. No emails, payments, VAT, filings, user or token changes.

Do not green coverage rows. Do not invent `ui_annual_*` tools. Do not run live API tests.

Tools: `ui_bills_create_preview`/`execute`, `ui_bills_update_preview`/`execute`, `ui_bills_delete_preview`/`execute`.
