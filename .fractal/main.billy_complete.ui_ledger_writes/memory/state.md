---
name: state
desc: Current work posture for UI ledger writes.
tags: [state]
sources: []
created: 2026-08-16T14:32:44Z
updated: 2026-08-16T14:32:44Z
---

# state

Eight ticketed tools are registered from `src/billy_mcp/ui_writes/ledger.py`.
Offline `tests/unit/test_ui_ledger_writes.py` covers preview no-submit, execute
once, replay, expiry, and wrong tool. Live-marked
`tests/live/test_ui_ledger_writes.py` asserts `submitted=false` and the blocker
text. Family contract is `wiki/ui_ledger_writes.md`. Node `test.sh` runs the
owned unit file.

Live mutation is refused. `register_ui_ledger_write_tools` has no submitter.
Parent hold `7696B03D` still gives contacts the live slot. No children.
Parent tip remains `56462d8`.
