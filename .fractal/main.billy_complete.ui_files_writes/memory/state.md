---
name: state
desc: Files-create tools are registered offline. Live execute submit is held.
tags: [state, ui, files]
sources: []
created: 2026-08-16T14:34:24Z
updated: 2026-08-16T14:34:24Z
---

# state

`ui_files_create_preview` and `ui_files_create_execute` are registered from
`src/billy_mcp/ui_writes/files.py`. Offline FastMCP tests cover preview
no-submit, execute once, replay, expiry, wrong tool, path or digest change,
outside path, and the default fail-closed submitter.

Live execute submit is held on parent radio `5D46AAC4`. Contacts has the slot.
The hold is recorded in `wiki/ui_files_writes.md`. It is a concrete blocker,
not an unsafe skipped submit.

Coverage stays red. No children.
