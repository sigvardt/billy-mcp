---
name: decisions
desc: Binding choices for products UI writes.
tags: []
sources: []
created: 2026-08-16T14:23:58Z
updated: 2026-08-16T14:23:58Z
---

# decisions

Offline first. Preview, execute, and ticket tests are the product of this node.

Live submit is blocked until root radios a live slot. Contacts family is first in the live queue.

Reuse `billy_mcp.ui_writes.protocol.UiWriteProtocol` and `ConfirmationStore`.

No HTTP writes to `api.billysbilling.com`.

Pass proof is FastMCP `call_tool`, not BrowserRuntime.

Create only. Do not add other product write tools.

No child split. This node is a leaf. Research176 already froze product get, update, and delete as UI not applicable. There is no safe UI delete.

Offline execute consumes the ticket and returns the bound request. The register hook has no browser handle. Live submit waits for a root go-ahead.

Do not green coverage rows from this node.
