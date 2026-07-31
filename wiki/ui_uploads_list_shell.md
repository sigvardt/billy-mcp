---
name: ui_uploads_list_shell
title: UI uploads list shell open
desc: Read-only headless ui_uploads_list contract for Billy uploads (Bilag) list shell open only.
tags: [billy, ui, uploads, bilag, headless]
sources:
  - docs/superpowers/specs/2026-07-28-billy-mcp-complete-design.md
  - https://www.billy.dk/api/
created: 2026-07-31T13:20:00Z
updated: 2026-07-31T13:20:00Z
---

# UI uploads list shell open

## Contract

Tool `ui_uploads_list` opens the authenticated Billy uploads (Bilag) list shell
on `mit.billy.dk` under path class `/:org_slug/uploads`.

Success fields (non-PII only):

- `path_class`: `/:org_slug/uploads` (query params such as drawerMode/type allowed
  on the real URL)
- `heading`: `Bilag`
- `upload_action_visible`: CTA `Upload filer` is present (never clicked)
- `shell_markers_present`: shared shell markers when visible

Input is empty. Callers must reach READY via `auth_login_start` /
`auth_login_wait` first. Organisation slug comes only from the session URL or
the outside-git UI identity file.

Hard bans: never set `input[type=file]`; never click `Upload filer`,
`Udfyld alle`, or `Kom i gang`; never call API upload tools from this
observation.

Inventory mapping: design discovery family `uploads` maps to this route. There
is no official `/v2/uploads` API resource.

## Explicit non-claims

- No invent `api_uploads_*` or `api_bilag_*`
- No file pick or multipart submit
- No greening of `ui.discovery.receipt_inbox`
- No greening of `ui.parity.files.*`, `ui.parity.attachments.*`, or
  `ui.parity.special.files_upload`
- No live API read-back

## Qualification notes

Dual independent headless sessions prove DOM classification. Vision review
covers list-surface frames only; durable record is non-sensitive with
`purge_verified` after frame purge. Inventory row greened by this shell:
`ui.discovery.uploads` only (`list_shell_open_only`).

Related offline API families (`files`, special binary upload, `attachments`)
remain contract-tested separately where producted; API `live_tested` remains
false under user-scoped qualification.
