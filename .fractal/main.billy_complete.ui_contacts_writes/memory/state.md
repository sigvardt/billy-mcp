---
name: state
desc: Current working state of the contacts UI write family.
tags: [state]
sources: []
created: 2026-08-16T14:39:35Z
updated: 2026-08-16T14:39:35Z
---

# state

Six UI contact preview and execute tools are registered from
`src/billy_mcp/ui_writes/contacts.py`. Offline FastMCP `call_tool` tests pass.
Node `scripts/test.sh` runs `tests/unit/test_ui_contacts_writes.py`.

Live MCP submit is blocked: this process has neither
`BILLY_BROWSER_PRIMARY_REFERENCE` nor `BILLY_BROWSER_SECONDARY_REFERENCE`. The
live test records that blocker and skips. Shared record:
`wiki/ui_contacts_writes.md`.

Do not green coverage. Do not claim parent complete.
