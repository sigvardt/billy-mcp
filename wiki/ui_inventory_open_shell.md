---
name: ui_inventory_open_shell
desc: Read-only Billy Lagermodul inventory shell open (research125 freeze).
tags: [billy, ui, inventory, lagermodul, discovery]
sources:
  - docs/superpowers/specs/2026-07-28-billy-mcp-complete-design.md
  - https://www.billy.dk/api/
created: 2026-07-31T19:30:00Z
updated: 2026-07-31T19:30:00Z
---

# ui_inventory_open_shell

## Contract

| Field | Value |
| --- | --- |
| Tool | `ui_inventory_open` |
| Coverage row | `ui.discovery.inventory` |
| Path class | `/:org_slug/inventory` (optional query allowed) |
| Heading | `Lagermodul` |
| shell_kind | `lagermodul` |
| Input | empty (`extra=forbid`) |
| Success fields | `path_class`, `heading`, `shell_kind`, `create_cta_markers_present` |
| parity_status | `shell_open_only` |

## Non-claims

- Soft paths (`lager`, `lagermodul`, `stock`, `warehouse`, nested `inventory/*`, `settings/inventory`, `products/inventory`) are **not** success.
- Products list (`/:org_slug/products`, h1 `Produkter`) is a different shell already greened by `ui_products_list`.
- No official Billy API inventory/stock/warehouse resource. Do **not** invent `api_inventory_*`.
- Never click create CTAs (`Opret primo`, `Opret produkt`, `Opret status`).
- Product create form open is a **separate** tool: `ui_products_create_open` (see [[ui_products_create_open_shell|ui_products_create_open_shell]]).
- Does not green settings_*, annual_reports, or re-green products/addons/integrations.
- API `live_tested` remains false with `out_of_scope_by_user`.

## Qualification

- Offline unit/model/server registration tests.
- Live dual independent browser sessions (no `BILLY_API_TOKEN`).
- Vision review record under tmp with `purge_verified: true` after frame purge.
