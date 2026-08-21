---
name: ui_products_get_update_delete_not_applicable
title: Products get update delete UI parity not applicable
desc: Dual-session research176 freeze — no equivalent mit.billy.dk get-detail, update-form, or delete-chrome workflow for products; list and create stay tool-green; exact NA for get/update/delete only.
tags: [billy, ui, parity, products, not_applicable]
sources:
  - https://www.billy.dk/api/
  - https://mit.billy.dk/
  - docs/superpowers/specs/2026-07-28-billy-mcp-complete-design.md
  - coverage/ui_workflows_manifest.yaml
  - wiki/ui_products_list_shell.md
  - wiki/ui_products_create_open_shell.md
  - wiki/ui_product_prices_not_applicable.md
created: 2026-08-02T03:15:00Z
updated: 2026-08-02T03:15:00Z
---

# Products get update delete UI parity not applicable

## Decision

UI parity rows for dual-proved **products get, update, and delete** API operations
are **`not_applicable`** with machine-readable evidence code
`GEO_UI_NO_EQUIVALENT_WORKFLOW` (same absence class as geo and research148–162
packages).

Design allows UI parity `not_applicable` only when Billy exposes **no equivalent
UI workflow**. Dual independent headless sessions on the dedicated
non-production organisation support that classification for **exact** ops:

- `api.products.get`
- `api.products.update`
- `api.products.delete`

**Not** greened by this freeze:

- `api.products.list` — greened as [[ui_products_list_shell]]
- `api.products.create` — greened as [[ui_products_create_open_shell]]
- `api.products.bulk_save` / `bulk_delete` — external-contract bulk freeze
- `api.productPrices.*` — separate NA [[ui_product_prices_not_applicable]]
- `api.special.invoice_email` and other residual UI parity
- Soft-empty postings/bankLines/invoiceLines (steal risk onto greened shells)
- Annual reports org inaccessible (NA rejected)

Peer freezes: [[ui_product_prices_not_applicable]],
[[ui_specials_invoice_delivery_logs_not_applicable]],
[[ui_products_list_shell]], [[ui_products_create_open_shell]].

## Dual-session evidence (non-sensitive)

| Observation | Result |
| --- | --- |
| Sessions | Two independent ephemeral profiles → READY |
| SPA product seed/cleanup | POST/DELETE 200 dual under committed egress; markers gone dual |
| Soft `/products/:id`, `/:id/edit`, `/:id/overview` | nav chrome only; marker false; inputs_n 0 dual |
| Soft inventory product paths | chrome only; marker false dual |
| List shell `/products` | marker true dual; click stays list (false-green if used as get) |
| List Mere | Eksportér/Importér produkter dual; Slet/Slet produkt 0 dual |
| Ret / product-id href / row open | no dual detail open |
| Inventory Opret produkt | create form dual — create only (already greened) |
| Env `BILLY_API_TOKEN` | unused (SPA session token capture only) |

Scratch dual summary (owner tmp, not git):
`research176_focus_dual.json`.

## Inventory contract

| Field | Value |
| --- | --- |
| `parity_status` | `not_applicable` |
| `tool_name` | empty (no ui_products_get/update/delete tools) |
| Flags | discovered, implemented, contract_tested, live_tested, vision_verified all true |
| `vision_evidence` | null (no retained frames) |
| `qualification.not_applicable_decision` | `accepted` |
| `qualification.sessions` | `dual_independent_ephemeral` |
| `qualification.evidence_ref` | `research176_products_get_update_delete_dual` |
| Scope | exact `api.products.get` / `update` / `delete` only |

## Contrast with list and create

- List is the list op (`ui_products_list`) — not get-by-id detail.
- Create is inventory form_open (`ui_products_create_open`) — not update of an existing product.
- Clients/bills/invoices have dual detail/edit/delete chrome; products do not on this org.

## Contrast with annual reports

`ui.discovery.annual_reports` keeps **`not_applicable` rejected**: nav label
exists (inaccessibility, not absence). See [[ui_annual_reports_inaccessible]].

## API lane note

Offline `api.products.get/update/delete` tools and contract tests are unchanged.
`live_tested` stays false with `out_of_scope_by_user`. No live API traffic.
