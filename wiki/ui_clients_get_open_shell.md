---
name: ui_clients_get_open_shell
title: UI clients detail get open
desc: Read-only headless ui_clients_get_open contract for Billy contact customer profile get/open only (research164).
tags: [billy, ui, clients, contacts, headless, get]
sources:
  - docs/superpowers/specs/2026-07-28-billy-mcp-complete-design.md
  - https://www.billy.dk/api/
created: 2026-08-01T18:35:00Z
updated: 2026-08-01T18:50:00Z
---

# UI clients detail get open

## Contract

Tool `ui_clients_get_open` opens an authenticated Billy contact **customer
profile** surface reached from the clients list on `mit.billy.dk`.

Success path class is `/:org_slug/contacts/:id/customer` (not `/clients/:id`).
The surface is a profile overview with name text `Name (Kunde)` and **Ret**
edit chrome, not an editable create-dialog name input.

Success fields (non-PII only):

- `path_class`: `/:org_slug/contacts/:id/customer`
- `shell_kind`: `clients_get`
- `detail_open`: profile detail surface open
- `contact_name_visible`: contact name header with (Kunde)/(Leverandør) marker
- `edit_action_visible`: Ret/Edit chrome present
- `detail_markers_present`: strict detail signature
- `shell_markers_present`: shared shell markers when visible

Input is empty. Maps `api.contacts.get` only.

## Browser egress

`coverage/browser_egress.yaml` path-allows scoped contacts data-plane methods
(`GET`/`POST`/`DELETE` prefix `/v2/contacts`, `GET` `/v2/countries`).

## Explicit non-claims

- No Ret/Gem/Slet submit in the product tool path
- Header-only clients table chrome is not success
- Soft `/clients/new` is not success
- Live harness may seed a disposable client when the list is empty, then delete
  it after dual get-open with fresh list read-back

## Related

- [[ui_clients_list_shell]]
- [[ui_clients_create_open_shell]]
