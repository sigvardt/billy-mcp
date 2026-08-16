---
name: state
title: state
desc: Present-tense position of the invoice UI write family.
created: 2026-08-16T14:24:23Z
updated: 2026-08-16T14:24:23Z
---

# state

Six draft-only ticket tools are registered in `invoices.py`. Offline FastMCP
`call_tool` tests cover preview no-submit, execute-once, replay, expiry,
wrong-tool mismatch, and send/email/Godkend fail-closed.

Live submit is not armed. Default execute returns `submitted=false`. The live
test records the contacts-slot hold (`30D194C8`) and does not import a browser
or Billy HTTP client.

Coverage rows `ui.parity.invoices.create|update|delete` remain
`implemented=false` and `live_tested=false`. This node does not green them.

Live-slot hold `30D194C8` is handed to the parent via `wiki/ui_invoices_writes.md`.
No child branches. Delivery is the six tools, offline tests, and the recorded
blocker.
