---
name: ui_uploads_list_shell
title: UI uploads list shell open
desc: Read-only headless ui_uploads_list contract for Billy Bilag list plus special files upload surface open only.
tags: [billy, ui, uploads, bilag, files_upload, headless]
sources:
  - docs/superpowers/specs/2026-07-28-billy-mcp-complete-design.md
  - https://www.billy.dk/api/
created: 2026-07-31T13:20:00Z
updated: 2026-08-01T12:00:00Z
---

# UI uploads list shell open

## Contract

Tool `ui_uploads_list` opens the authenticated Billy uploads (Bilag) list shell
on `mit.billy.dk` under path class `/:org_slug/uploads`.

Success fields (non-PII only):

- `path_class`: `/:org_slug/uploads` (query params such as drawerMode/type allowed
  on the real URL)
- `heading`: `Bilag`
- `upload_action_visible`: CTA `Upload filer` is present (never required to click
  for success)
- `file_input_present`: at least one `input[type=file]` is present (research155
  dual count class ≥1; never set via Playwright)
- `shell_markers_present`: shared shell markers when visible

Input is empty. Callers must reach READY via `auth_login_start` /
`auth_login_wait` first. Organisation slug comes only from the session URL or
the outside-git UI identity file.

Hard bans: never set `input[type=file]`; never click upload submit paths that
send bytes; never call API upload tools from this observation.

## Inventory mapping

| Row | Mapping |
| --- | --- |
| `ui.discovery.uploads` | discovery shell on this tool |
| `ui.parity.special.files_upload` | dual-count of `api.special.files_upload` (`POST /v2/files` binary upload surface) onto this tool (research155) |

There is no official `/v2/uploads` API resource. Soft path `/files` is empty SPA
chrome (body class 127) and is not this shell.

## Explicit non-claims

- No invent `api_uploads_*` or `api_bilag_*`
- No file pick or multipart submit
- No greening of `ui.discovery.receipt_inbox` (`/:org_slug/vouchers`)
- No greening of `ui.parity.files.*` CRUD or `ui.parity.attachments.*`
- No greening of `ui.parity.special.invoice_email`
- No live API read-back

## Qualification notes

Dual independent headless sessions prove DOM classification (research113 list
shell; research155 file-input binding chrome). Vision review covers list-surface
frames only; durable record is non-sensitive with `purge_verified` after frame
purge.

Related offline API families (`files` CRUD, special binary upload execute,
`attachments`) remain contract-tested separately where producted; API
`live_tested` remains false under user-scoped qualification.
