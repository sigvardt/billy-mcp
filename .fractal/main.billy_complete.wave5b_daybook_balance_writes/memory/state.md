---
name: state
desc: Current delivery state for the daybook balance account ticketed-write leaf.
created: 2026-07-29T16:27:59Z
updated: 2026-07-29T16:27:59Z
---

# state

Commit `5a0d2ac` contains the owned module and contract suite for six offline
ticketed FastMCP tools covering singular daybook balance account create, update,
and delete operations. The module uses the shared `WriteProtocolService` with
the frozen relative path and roots.

The focused offline contract suite covers strict schemas, non-mutating previews,
exact execute requests, typed errors, and ticket tamper, mismatch, replay, and
expiry rejection. Ruff, Pyright, and the node scripts pass against the committed
bytes.
