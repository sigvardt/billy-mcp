---
name: ui_receipt_inbox_list_shell
title: UI receipt inbox list shell open
desc: Read-only headless ui_receipt_inbox_list contract for Billy receipt inbox (Bilagsindbakke / vouchers) list shell open only.
tags: [billy, ui, receipt_inbox, bilagsindbakke, vouchers, headless]
sources:
  - docs/superpowers/specs/2026-07-28-billy-mcp-complete-design.md
  - https://www.billy.dk/api/
created: 2026-07-31T13:45:00Z
updated: 2026-07-31T13:45:00Z
---

# UI receipt inbox list shell open

## Contract

Tool `ui_receipt_inbox_list` opens the authenticated Billy receipt inbox
(Bilagsindbakke) list shell on `mit.billy.dk` under path class
`/:org_slug/vouchers`.

Success fields (non-PII only):

- `path_class`: `/:org_slug/vouchers`
- `heading`: `Bilagsindbakke`
- `file_control_present`: at least one `input[type=file]` is present (never set)
- `shell_markers_present`: shared shell markers when visible

Input is empty. Callers must reach READY via `auth_login_start` /
`auth_login_wait` first. Organisation slug comes only from the session URL or
the outside-git UI identity file.

Hard bans: never set `input[type=file]`; never click `Ret`, `Upload filer`,
`Udfyld alle`, or `Kom i gang`; never call API upload tools from this
observation; never treat the uploads Bilag shell (`/:org_slug/uploads`) as
success for this tool.

Inventory mapping: design discovery family `receipt_inbox` maps to this route.
There is no official `/v2/vouchers` or receipt-inbox API resource.

## Explicit non-claims

- No invent `api_vouchers_*`, `api_receipt_inbox_*`, or `api_bilagsindbakke_*`
- No file pick or multipart submit
- No greening of `ui.discovery.uploads` (separate Bilag product)
- No greening of `ui.parity.files.*`, `ui.parity.attachments.*`, or
  `ui.parity.special.files_upload`
- No live API read-back

## Qualification notes

Dual independent headless sessions prove DOM classification. Vision review
covers list-surface frames only; durable record is non-sensitive with
`purge_verified` after frame purge. Inventory row greened by this shell:
`ui.discovery.receipt_inbox` only (`list_shell_open_only`).

Related offline API families (`files`, special binary upload, `attachments`)
remain contract-tested separately where producted; API `live_tested` remains
false under user-scoped qualification.
