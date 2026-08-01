---
name: ui_invoices_create_open_shell
title: UI invoices create form open
desc: Read-only headless ui_invoices_create_open contract for Billy invoice create form open only (research153).
tags: [billy, ui, invoices, headless, create]
sources:
  - docs/superpowers/specs/2026-07-28-billy-mcp-complete-design.md
  - https://www.billy.dk/api/
created: 2026-08-01T10:30:00Z
updated: 2026-08-01T10:30:00Z
---

# UI invoices create form open

## Contract

Tool `ui_invoices_create_open` opens the authenticated Billy invoice create form
on `mit.billy.dk` under path class `/:org_slug/invoices/new`.

Success fields (non-PII only):

- `path_class`: `/:org_slug/invoices/new` (query params allowed on the real URL)
- `heading`: `Opret faktura`
- `shell_kind`: `invoices_create`
- `draft_save_chrome_visible`: CTA text `Gem som kladde` is present (never clicked)
- `line_chrome_visible`: line chrome `Tilføj linje` or `Beskrivelse` present (never clicked)
- `shell_markers_present`: shared shell markers when visible

Input is empty. Callers must reach READY via `auth_login_start` /
`auth_login_wait` first. Organisation slug comes only from the session URL or
the outside-git UI identity file.

## Explicit non-claims

- No invoice create submit, draft save, approve, or send
- No special `POST /v2/invoices/:invoiceId/emails` (custom email subject/body)
- No mapping of list shell (`ui_invoices_list`) to create
- No live API read-back
- Does not green get/update/delete/bulk invoice UI parity or special.invoice_email

## Isolation

| Surface | Not this tool |
| --- | --- |
| List `/:org_slug/invoices` h1 Fakturaer | `ui_invoices_list` |
| Settings Levering af faktura pr. e-mail | `ui_settings_invoicing_open` |
| Special invoice email API | offline `api_invoices_send_email_*` only; UI parity still red |

## Qualification notes

Dual independent headless sessions prove DOM classification (research153).
Vision review covers create-form frames only; durable record is non-sensitive
with `purge_verified` after frame purge. Inventory dual-counts exact
`api.invoices.create` only.
