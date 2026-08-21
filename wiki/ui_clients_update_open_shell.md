---
name: ui_clients_update_open_shell
title: UI clients update form open shell
desc: Read-only Billy UI tool that opens a client contact in Ret edit mode and classifies non-PII form flags without submitting.
tags: [billy, ui, clients, contacts, update, form_open]
sources:
  - https://www.billy.dk/api/
  - coverage/ui_workflows_manifest.yaml
  - coverage/browser_egress.yaml
  - src/billy_mcp/browser.py
  - tests/live/test_ui_clients_update_open.py
created: 2026-08-01T20:10:00Z
updated: 2026-08-01T20:10:00Z
---

# UI clients update form open shell

## Delivered

Typed FastMCP tool **`ui_clients_update_open`** opens an existing client (contact)
detail surface, activates **Ret**, and returns non-PII edit-form flags.

| Field | Value |
| --- | --- |
| tool_name | `ui_clients_update_open` |
| path_class | `/:org_slug/contacts/:id/customer` |
| shell_kind | `clients_update` |
| parity | `ui.parity.contacts.update` / `api.contacts.update` |
| parity_status | `form_open_only` |
| product path | never Gem / Slet / Save |

## Behaviour

1. Authenticated headless session (existing browser credentials).
2. Open clients list, open first non-header contact detail.
3. Click **Ret**.
4. Require valued `name` input plus address/person or country fields (content floor).
5. Independent second browser profile re-opens the same edit signature.

Live harness may create a disposable client when the organisation list is empty,
then delete it after dual read-back.

## Isolation

Distinct from:

- `ui_clients_list` (list shell)
- `ui_clients_create_open` (create dialog)
- `ui_clients_get_open` (detail overview without requiring Ret edit fields)

`contacts.delete` remains separate residual work.

## Egress

Uses existing contacts data-plane path_allow on `api.billysbilling.com`
(GET/POST/DELETE `/v2/contacts` from clients get product). No new hosts.
