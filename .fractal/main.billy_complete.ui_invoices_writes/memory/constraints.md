---
name: constraints
title: constraints
desc: Binding safety and scope rules for invoice UI writes.
created: 2026-08-16T14:24:23Z
updated: 2026-08-16T14:24:23Z
---

# constraints

Live submit waits for an explicit root radio go-ahead. Contacts family is first in the live slot.

Create drafts only (Billy UI label Gem som kladde). Never Godkend, Send, or email. Fail closed on send/email. Delete drafts in cleanup.

Reuse `billy_mcp.ui_writes.protocol.UiWriteProtocol` and `ConfirmationStore`. Preview writes nothing. Execute accepts only `confirmation_ticket`. No POST/PUT/DELETE to `api.billysbilling.com`.

Qualify through FastMCP `call_tool`. `BrowserRuntime` is not the pass proof.

Offline tests must cover preview no-submit, execute once, replay, expiry, and wrong-tool mismatch.

Live submit, when later allowed: unique tagged names, independent second UI session read-back, four-state capture, purge raw frames, store only a non-sensitive vision record.

Do not green coverage rows. Do not invent `ui_annual_*` tools. Do not run live API tests. Do not send invoices or emails, make payments, submit VAT/filings, or change users/access/tokens/subscription.

Owned paths only: `src/billy_mcp/ui_writes/invoices.py`, `tests/unit/test_ui_invoices_writes.py`, `tests/live/test_ui_invoices_writes.py`, `wiki/ui_invoices_writes.md`. Do not edit `generate_coverage_report.py`, `scripts/check_coverage.py`, `src/billy_mcp/server.py`, or `src/billy_mcp/browser.py`.
