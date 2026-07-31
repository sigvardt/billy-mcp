---
name: ui_suppliers_list_shell
title: UI suppliers list shell open
desc: Read-only headless ui_suppliers_list contract for Billy suppliers list shell open only.
tags: [billy, ui, suppliers, contacts, headless]
sources:
  - docs/superpowers/specs/2026-07-28-billy-mcp-complete-design.md
  - https://www.billy.dk/api/
created: 2026-07-31T12:00:00Z
updated: 2026-07-31T12:00:00Z
---

# UI suppliers list shell open

## Contract

Tool `ui_suppliers_list` opens the authenticated Billy suppliers list shell on
`mit.billy.dk` under path class `/:org_slug/suppliers`.

Success fields (non-PII only):

- `path_class`: `/:org_slug/suppliers` (query params allowed on the real URL)
- `heading`: `Leverandører`
- `create_action_visible`: CTA `Opret kontakt` is present (never clicked)
- `shell_markers_present`: shared shell markers when visible

Input is empty. Callers must reach READY via `auth_login_start` /
`auth_login_wait` first. Organisation slug comes only from the session URL or
the outside-git UI identity file.

## Explicit non-claims

- No invent `api_suppliers_*` / `api_vendors_*` (docs have no suppliers resource;
  vendors are contacts with `isSupplier`)
- No contact create/edit/delete (never click `Opret kontakt` or `Mere`)
- No greening of purchases/bills, debtor/creditor balances, or uploads discovery
- No greening of `api.contacts.*` live cells
- No live API read-back

## Qualification notes

Dual independent headless sessions prove DOM classification. Vision review
covers list-surface frames only; durable record is non-sensitive with
`purge_verified` after frame purge. Inventory row `ui.discovery.suppliers` is
the only row greened by this shell.

Official docs expose offline `contacts` CRUD with `isSupplier`. The suppliers
UI is a vendor-filtered contacts surface. API `live_tested` remains false under
user-scoped qualification.
