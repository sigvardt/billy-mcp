---
name: ui_bills_create_open_shell
title: UI bills create form open
desc: Read-only headless ui_bills_create_open contract for Billy bill create form open only (research154).
tags: [billy, ui, bills, headless, create]
sources:
  - docs/superpowers/specs/2026-07-28-billy-mcp-complete-design.md
  - https://www.billy.dk/api/
created: 2026-08-01T11:00:00Z
updated: 2026-08-01T11:00:00Z
---

# UI bills create form open

## Contract

Tool `ui_bills_create_open` opens the authenticated Billy bill create form
on `mit.billy.dk` under path class `/:org_slug/bills/new`.

Success fields (non-PII only):

- `path_class`: `/:org_slug/bills/new` (query params allowed on the real URL)
- `heading`: `Opret køb`
- `shell_kind`: `bills_create`
- `draft_save_chrome_visible`: CTA text `Gem som kladde` is present (never clicked)
- `line_chrome_visible`: line chrome `Tilføj linje`, `Beskrivelse`, or `Linje` present (never clicked)
- `shell_markers_present`: shared shell markers when visible

Input is empty. Callers must reach READY via `auth_login_start` /
`auth_login_wait` first. Organisation slug comes only from the session URL or
the outside-git UI identity file.

## Explicit non-claims

- No bill create submit, draft save, approve, or upload
- No mapping of list shell (`ui_bills_list`) to create
- No live API read-back
- Does not green get/update/delete/bulk bill UI parity or special.invoice_email

## Isolation

| Surface | Not this tool |
| --- | --- |
| List `/:org_slug/bills` h1 Køb | `ui_bills_list` |
| Invoice create `/:org_slug/invoices/new` | `ui_invoices_create_open` |
| Settings Levering af faktura pr. e-mail | `ui_settings_invoicing_open` |
| Special `POST /v2/invoices/:id/emails` | still red / deferred |

## Dual-count

Maps only `api.bills.create` to this open-only form. List remains
`ui_bills_list`. Evidence: research154 dual-session headless observation.

## Related

- [[ui_bills_list_shell]]
- [[ui_invoices_create_open_shell]]
