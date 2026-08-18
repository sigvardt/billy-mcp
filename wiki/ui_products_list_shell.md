---
name: ui_products_list_shell
title: UI products list shell open
desc: Read-only headless ui_products_list contract for Billy products list shell open only.
tags: [billy, ui, products, headless]
sources:
  - docs/superpowers/specs/2026-07-28-billy-mcp-complete-design.md
  - https://www.billy.dk/api/
created: 2026-07-31T10:25:00Z
updated: 2026-07-31T10:25:00Z
---

# UI products list shell open

## Contract

Tool `ui_products_list` opens the authenticated Billy products list shell on
`mit.billy.dk` under path class `/:org_slug/products`.

Success fields (non-PII only):

- `path_class`: `/:org_slug/products` (query params allowed on the real URL)
- `heading`: `Produkter`
- `search_control_visible`: control `[data-cy='search-button']` is present (never clicked)
- `shell_markers_present`: shared shell markers when visible

Input is empty. Callers must reach READY via `auth_login_start` /
`auth_login_wait` first. Organisation slug comes only from the session URL or
the outside-git UI identity file.

## Explicit non-claims

- ProductPrices UI parity is a separate soft-empty NA freeze: [[ui_product_prices_not_applicable]] (not dual-counted onto this shell)
- No product create/import/archive mutations
- Archive-filter classify is separate (`inspect-live-products-archive-list.json`). Exact **Vis arkiverede** / **Arkiverede** / **Skjul arkiverede** counts were 0. That dump is not this list-shell row.
- No API list filter/sort/pagination UI
- No live API read-back
- Clients and bank-accounts are separate discovery tracks
- Does not invent a missing `bankAccounts` API resource

## Qualification notes

Dual independent headless sessions prove DOM classification. Vision review
co-signs list-surface frames only; frames stay outside the repository and must
be purged after review. Inventory rows use `parity_status: list_shell_open_only`
with empty request fields and null pagination.

Maps offline `api.products.list` for list-open parity only. API `live_tested`
remains false under user-scoped qualification.

## Related

- Product create form open (inventory entry): [[ui_products_create_open_shell|ui_products_create_open_shell]]
