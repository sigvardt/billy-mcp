---
name: ui_products_create_open_shell
desc: Read-only headless ui_products_create_open contract for Billy product create form open only (research163).
tags: [billy, ui, products, create, inventory, lagermodul, form_open]
sources:
  - docs/superpowers/specs/2026-07-28-billy-mcp-complete-design.md
  - https://www.billy.dk/api/
created: 2026-08-01T17:45:00Z
updated: 2026-08-01T17:45:00Z
---

# ui_products_create_open_shell

## Contract

| Field | Value |
| --- | --- |
| Tool | `ui_products_create_open` |
| Coverage rows | `ui.discovery.products_create`, `ui.parity.products.create` |
| Path class | `/:org_slug/inventory` (form opens on Lagermodul; not catalog `/products`) |
| Heading | `Lagermodul` |
| shell_kind | `products_create` |
| CTA | **Opret produkt** (observe-only click) |
| Input | empty (`extra=forbid`) |
| Success fields | `path_class`, `heading`, `shell_kind`, `create_form_open`, `name_field_visible`, `account_field_present`, `sales_tax_ruleset_field_present`, `unit_price_field_present`, `shell_markers_present` |
| parity_status | `form_open_only` |
| API map | exact `api.products.create` only |

## Navigation

1. Auth READY on non-production Billy organisation.
2. Open `/:org_slug/inventory` (Lagermodul).
3. Click **Opret produkt** (never Opret primo / Opret status).
4. Classify form fields matching official product create (name, account, salesTaxRuleset, unitPrice embed chrome).
5. Escape to close; never Gem / submit / file upload.

## Non-claims

- Catalog list `ui_products_list` (`/:org_slug/products`) has **no** create CTA in the test org (Mere → export/import only).
- Soft `/products/new` is chrome-only and is **not** success.
- `ui_inventory_open` remains shell_open_only and **must not** click Opret*.
- Does not green `products.get` / `update` / `delete` / bulk_*.
- `unitPrice` on the create form is products.create prices embed chrome; **not** the `productPrices` resource (dual-NA research162).
- Never invent `api_inventory_*`.
- API `live_tested` remains false with `out_of_scope_by_user`.

## Qualification

- Offline unit/model/server registration tests.
- Live dual independent browser sessions (no `BILLY_API_TOKEN`).
- Vision review record under tmp with `purge_verified: true` after frame purge.

## Related

- [[ui_products_list_shell|ui_products_list_shell]]
- [[ui_products_import_shell|ui_products_import_shell]]
- [[ui_inventory_open_shell|ui_inventory_open_shell]]
- [[ui_product_prices_not_applicable|ui_product_prices_not_applicable]]
