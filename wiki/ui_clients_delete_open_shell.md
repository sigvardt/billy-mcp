---
name: ui_clients_delete_open_shell
title: UI clients delete chrome open shell
desc: Read-only Billy UI tool that opens a client contact detail, opens Mere, and classifies Slet kontakt delete chrome without confirming deletion.
tags: [billy, ui, clients, contacts, delete, mere]
sources:
  - https://www.billy.dk/api/
  - coverage/ui_workflows_manifest.yaml
  - coverage/browser_egress.yaml
  - src/billy_mcp/browser.py
  - tests/live/test_ui_clients_delete_open.py
created: 2026-08-01T21:00:00Z
updated: 2026-08-01T21:00:00Z
---

# UI clients delete chrome open shell

## Delivered

Typed FastMCP tool **`ui_clients_delete_open`** opens an existing client (contact)
detail surface, opens **Mere**, and returns non-PII delete-chrome flags.

| Field | Value |
| --- | --- |
| tool_name | `ui_clients_delete_open` |
| path_class | `/:org_slug/contacts/:id/customer` |
| shell_kind | `clients_delete` |
| parity | `ui.parity.contacts.delete` / `api.contacts.delete` |
| parity_status | `delete_chrome_open_only` |
| product path | never confirm Slet / Arkivér |

## Behaviour

1. Authenticated headless session (existing browser credentials).
2. Open clients list, open first non-header contact detail.
3. Click **Mere**.
4. Require **Slet kontakt** visible (optional Arkivér kontakt support flag).
5. Independent second browser profile re-opens the same delete-chrome signature.

Live harness may create a disposable client when the organisation list is empty,
then delete it after dual read-back (SPA session token cleanup or UI).

## Isolation

Distinct from:

- `ui_clients_list` (list shell)
- `ui_clients_create_open` (create dialog)
- `ui_clients_get_open` (detail overview)
- `ui_clients_update_open` (Ret edit form)

## Egress

Uses existing contacts data-plane path_allow on `api.billysbilling.com`
(GET/POST/DELETE `/v2/contacts` from clients get product). No new hosts.
