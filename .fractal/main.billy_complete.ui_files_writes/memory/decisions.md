---
name: decisions
desc: Fail-closed default submitter, path-digest bind, and live-slot hold.
tags: [decisions, ui, files]
sources: []
created: 2026-08-16T14:34:24Z
updated: 2026-08-16T14:34:24Z
---

# decisions

Preview binds the resolved regular-file path and SHA-256 digest through
`UiWriteProtocol`. Execute accepts only `confirmation_ticket`. A changed path
or digest is `FILE_CHANGED`. A missing or out-of-root path is
`FILE_NOT_ALLOWED`. This family does not call `api.billysbilling.com`.

`create_server` calls `register_ui_file_write_tools(server, protocol)` with no
submitter. The default submitter returns `PLAN_UNAVAILABLE` and opens no
browser. Tests inject a recording submitter. A Bilag submitter is not wired
until root gives this family a live slot.

research185 found no attachments delete chrome on an empty Bilag list. Live
submit also needs a proven UI delete path. If that is still missing after a
go-ahead, do not submit.
