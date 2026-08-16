---
name: ui_files_writes
title: UI files create ticketed writes
desc: Ticketed ui_files_create preview and execute. Path and digest bound. Live submit held.
tags: [billy, ui, writes, files, tickets]
sources:
  - wiki/ui_write_ticket_protocol.md
  - src/billy_mcp/ui_writes/files.py
  - src/billy_mcp/ui_writes/protocol.py
created: 2026-08-16T14:30:00Z
updated: 2026-08-16T14:30:00Z
---

# UI files create ticketed writes

Family tools for `ui.parity.files.create`. Shared ticket rules live in
[[ui_write_ticket_protocol]]. This page does not green coverage.

## Tools

| Tool | Input | Effect |
| --- | --- | --- |
| `ui_files_create_preview` | `path`, `filename`, optional `organization_id` | Resolve a regular file under `BILLY_UPLOAD_ROOTS`, bind the exact path and SHA-256 digest, issue a ticket. Writes nothing. |
| `ui_files_create_execute` | `confirmation_ticket` only | Consume the ticket once. Reject a changed path or digest (`FILE_CHANGED`). Then call the injected UI submitter. |

Qualify through FastMCP `call_tool`. Do not treat `BrowserRuntime` as the pass
proof.

The UI lane never sends POST, PUT, or DELETE to
`https://api.billysbilling.com`. Read-back is a second interface session.

## Fail closed

- Preview performs no Billy mutation.
- Execute accepts only `confirmation_ticket`. Extra fields are rejected.
- Tickets expire in at most five minutes and cannot be replayed.
- A ticket issued for another execute tool is `CONFIRMATION_MISMATCH`.
- A changed local path or digest after preview is `FILE_CHANGED`. No submit.
- A path outside `BILLY_UPLOAD_ROOTS`, missing, or not a regular file is
  `FILE_NOT_ALLOWED`. Preview writes nothing.
- The default register (the two-arg `create_server` call) uses a fail-closed
  submitter. Execute returns `PLAN_UNAVAILABLE` and does not open a browser or
  call `api.billysbilling.com`.
- Do not send invoices or emails, pay, file VAT, or change users, tokens, or
  subscription.
- Do not invent `ui_annual_*` tools.

## Cleanup

Live submit uses a disposable local fixture file outside git, with a unique
tagged name such as `MCP-TEST-ui-files-<hex>.txt`. After a successful upload,
delete that record through the UI. If delete chrome is absent, do not submit.

## Live slot hold

Live submit is held. Parent radio `5D46AAC4` said contacts has the current live
slot. This family must not run a live execute submit until root radios an
explicit files live-slot go-ahead.

That hold is a concrete live blocker, not an unsafe skipped submit. Offline
ticket tests still run.

When the slot arrives: unique tagged name, independent second UI session
read-back, four-state capture, purge raw frames, store only a non-sensitive
vision record, then delete the uploaded record.
