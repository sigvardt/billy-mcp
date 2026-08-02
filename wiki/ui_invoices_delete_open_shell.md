---
name: ui_invoices_delete_open_shell
title: UI invoices delete chrome open shell
desc: Read-only Billy UI tool that opens a draft invoice edit surface, opens Mere, and classifies Slet delete chrome without confirming deletion.
tags: [billy, ui, invoices, delete, mere]
sources:
  - https://www.billy.dk/api/
  - coverage/ui_workflows_manifest.yaml
  - coverage/browser_egress.yaml
  - src/billy_mcp/browser.py
  - tests/live/test_ui_invoices_delete_open.py
created: 2026-08-02T02:00:00Z
updated: 2026-08-02T02:00:00Z
---

# UI invoices delete chrome open shell

## Delivered

Typed FastMCP tool **`ui_invoices_delete_open`** opens an existing draft invoice
edit surface, opens **Mere**, and returns non-PII delete-chrome flags.

| Field | Value |
| --- | --- |
| tool_name | `ui_invoices_delete_open` |
| path_class | `/:org_slug/invoices/:id/edit` |
| shell_kind | `invoices_delete` |
| parity | `ui.parity.invoices.delete` / `api.invoices.delete` |
| parity_status | `delete_chrome_open_only` |
| product path | never confirm Slet / Send / Gem |

## Behaviour

1. Authenticated headless session (existing browser credentials).
2. Open invoices list, open first non-header draft invoice edit.
3. Assert primary Slet **button** absent; open **Mere**.
4. Require exact text **Slet** visible (optional Duplikér support flag).
5. Independent second browser profile re-opens the same delete-chrome signature.

Live harness may create a disposable draft invoice when needed, then delete it
after dual read-back (SPA session token cleanup; not env API token).

## Isolation

Distinct from:

- `ui_invoices_list` (list shell)
- `ui_invoices_create_open` (create form)
- `ui_invoices_get_open` (detail freeze)
- `ui_invoices_update_open` (edit form freeze)
- `ui_bills_delete_open` (primary Slet + confirm Annuller)

## Egress

Uses existing invoices data-plane path_allow on `api.billysbilling.com`
(GET/POST/DELETE `/v2/invoices` from invoices get/update product). No new hosts.
