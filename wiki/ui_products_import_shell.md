---
name: ui_products_import_shell
title: UI products import shell open
desc: Read-only headless ui_products_import contract for Billy products CSV import shell open only.
tags: [billy, ui, products, import, headless]
sources:
  - docs/superpowers/specs/2026-07-28-billy-mcp-complete-design.md
  - https://www.billy.dk/api/
created: 2026-07-31T11:45:00Z
updated: 2026-07-31T11:45:00Z
---

# UI products import shell open

## Contract

Tool `ui_products_import` opens the authenticated Billy products import shell on
`mit.billy.dk` under path class `/:org_slug/products/import`.

Success fields (non-PII only):

- `path_class`: `/:org_slug/products/import` (query params allowed on the real URL)
- `heading`: `Import af produkter`
- `choose_csv_action_visible`: control label `Vælg CSV-fil` is present (never clicked;
  never chooses a file; never uploads)
- `shell_markers_present`: shared shell markers when visible

Input is empty. Callers must reach READY via `auth_login_start` /
`auth_login_wait` first. Organisation slug comes only from the session URL or
the outside-git UI identity file.

## Explicit non-claims

- No invent `api_products_import_*` / product CSV import API (docs have none)
- No file selection, file digest binding, upload, or import submit
- No greening of suppliers, bills/purchases, debtor/creditor balances, uploads,
  or other discovery shells from this tool
- No greening of `api.products.*` live cells
- No live API read-back

## Qualification notes

Dual independent headless sessions prove DOM classification. Vision review
covers import-surface frames only; durable record is non-sensitive with
`purge_verified` after frame purge. Inventory row
`ui.discovery.product_import` is the only row greened by this shell.

Official docs expose offline `products` CRUD only. Product import is UI-only.
API `live_tested` remains false under user-scoped qualification.
