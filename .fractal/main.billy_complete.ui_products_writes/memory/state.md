---
name: state
desc: Current standing of the products UI write node.
tags: []
sources: []
created: 2026-08-16T14:33:50Z
updated: 2026-08-16T14:33:50Z
---

# state

`register_ui_product_write_tools` registers `ui_products_create_preview` and
`ui_products_create_execute`. Offline FastMCP `call_tool` tests cover preview
no-submit, optional form fields, execute-once, replay, expiry, and wrong-tool
mismatch. Node `test.sh` runs that unit file.

Live submit is gated on the parent live slot (contacts family first). Cleanup
blocker is recorded: research176, no safe UI delete. Shared page:
`wiki/ui_products_writes.md`.

Coverage row `ui.parity.products.create` is not greened here. Parent
`complete:true` is not claimed.

Parent `main.billy_complete` is merged. No child branches.
