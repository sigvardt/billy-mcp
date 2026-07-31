---
name: ui_invoices_list_shell
title: UI invoices list shell open
desc: Read-only headless ui_invoices_list contract for Billy invoices list shell open only.
tags: [billy, ui, invoices, headless]
sources:
  - docs/superpowers/specs/2026-07-28-billy-mcp-complete-design.md
  - https://www.billy.dk/api/
created: 2026-07-31T10:05:00Z
updated: 2026-07-31T10:05:00Z
---

# UI invoices list shell open

## Contract

Tool `ui_invoices_list` opens the authenticated Billy invoices list shell on
`mit.billy.dk` under path class `/:org_slug/invoices`.

Success fields (non-PII only):

- `path_class`: `/:org_slug/invoices` (query params allowed on the real URL)
- `heading`: `Fakturaer`
- `create_action_visible`: CTA `Opret faktura` is present (never clicked)
- `shell_markers_present`: shared shell markers when visible

Input is empty. Callers must reach READY via `auth_login_start` /
`auth_login_wait` first. Organisation slug comes only from the session URL or
the outside-git UI identity file.

## Explicit non-claims

- No invoice create/edit/delete
- No API list filter/sort/pagination UI
- No live API read-back
- Daybooks and bank-accounts are separate discovery tracks

## Qualification notes

Dual independent headless sessions prove DOM classification. Vision review
covers list-surface frames only; durable record is non-sensitive with
`purge_verified` after frame purge. Inventory rows for discovery and shell-only
parity must not embed full API filter schemas while greened.
