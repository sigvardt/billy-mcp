---
name: ui_clients_create_open_shell
title: UI clients create form open
desc: Read-only headless ui_clients_create_open contract for Billy clients create dialog form open only (research160).
tags: [billy, ui, clients, contacts, headless, create]
sources:
  - docs/superpowers/specs/2026-07-28-billy-mcp-complete-design.md
  - https://www.billy.dk/api/
created: 2026-08-01T15:20:00Z
updated: 2026-08-01T15:20:00Z
---

# UI clients create form open

## Contract

Tool `ui_clients_create_open` opens the authenticated Billy contact/customer
create dialog on `mit.billy.dk` under path class `/:org_slug/clients` or
`/:org_slug/clients/empty` after the text CTA **Opret kontakt**.

Success fields (non-PII only):

- `path_class`: `/:org_slug/clients` or `/:org_slug/clients/empty` (dialog on list path; not soft `/clients/new`)
- `heading`: `Kunder` or `Kontakter`
- `shell_kind`: `clients_create`
- `create_dialog_open`: create dialog form surface present after CTA
- `name_field_visible`: input `name` visible
- `registration_no_field_present`: input `registrationNo` present
- `address_or_person_fields_present`: street and/or person_* fields present
- `shell_markers_present`: shared shell markers when visible

Input is empty. Callers must reach READY via `auth_login_start` /
`auth_login_wait` first. Organisation slug comes only from the session URL or
the outside-git UI identity file.

## Explicit non-claims

- No contact create submit (Gem / Opret / Save / Create)
- Soft `/clients/new` chrome-only is not a success path
- No special `POST /v2/invoices/:invoiceId/emails`
- No mapping of list shell (`ui_clients_list`) to create
- No live API read-back
- Does not green contacts.get/update/delete/bulk UI parity

## Dual-count

Maps offline `api.contacts.create` (`POST /v2/contacts`) to form-open-only UI
parity under research160 dual-session evidence.


- [[ui_clients_get_open_shell]]
