---
name: ui_product_prices_not_applicable
title: Product prices UI parity not applicable
desc: Dual-session research162 freeze — no equivalent mit.billy.dk workflow for productPrices API parity; soft-empty path matches nonsense; products/Produkter shell is products only; NA accepted for productPrices only.
tags: [billy, ui, parity, productPrices, products, not_applicable]
sources:
  - https://www.billy.dk/api/
  - https://mit.billy.dk/
  - docs/superpowers/specs/2026-07-28-billy-mcp-complete-design.md
  - coverage/ui_workflows_manifest.yaml
  - wiki/ui_products_list_shell.md
  - wiki/ui_products_import_shell.md
  - wiki/ui_specials_invoice_delivery_logs_not_applicable.md
  - wiki/ui_contact_persons_not_applicable.md
created: 2026-08-01T16:56:00Z
updated: 2026-08-01T16:56:00Z
---

# Product prices UI parity not applicable

## Decision

UI parity rows for dual-proved **productPrices** API operations are
**`not_applicable`** with machine-readable evidence code
`GEO_UI_NO_EQUIVALENT_WORKFLOW` (same absence class as geo and research148–150
packages).

Design allows UI parity `not_applicable` only when Billy exposes **no equivalent
UI workflow**. Dual independent headless sessions on the dedicated
non-production organisation support that classification for all seven
productPrices ops:

- get, list, create, update, delete, bulk_save, bulk_delete

**Not** greened by this freeze (stay red or other product paths):

- `api.products.*` create/get residual discovery (products list shell greened
  separately as [[ui_products_list_shell]])
- `api.special.invoice_email` and other residual UI parity
- Soft-empty postings/bankLines/invoiceLines/salesTaxRules (steal risk onto
  greened shells; not pure NA here)
- Bulk 92 external-contract API freeze
- Annual reports org inaccessible (NA rejected)

Peer freezes: [[ui_specials_invoice_delivery_logs_not_applicable]],
[[ui_contact_persons_not_applicable]],
[[ui_products_list_shell]] (contrast only — different resource).

## Dual-session evidence (non-sensitive)

| Observation | Result |
| --- | --- |
| Sessions | Two independent ephemeral profiles → READY |
| Soft seed `/productPrices` and `/product-prices` | soft-empty SPA chrome only (body length class 127, empty h1) after waiting out loading chrome |
| Nonsense path control `zz-r162-none` | **same** soft-empty class (body 127) |
| Products shell | dual-ok as **Produkter** (`ui_products_list`); not a productPrices CRUD workflow |
| Products import shell | dual-ok import surface only |
| Soft `/products/new` | chrome-only body length class 190; no product form fields dual |
| API products create embed `prices[]` | official docs only — not a `/productPrices` UI shell |

Scratch dual summaries (owner tmp, not git):
`research162_soft_longwait_dual.json`, `research162_focus_dual.json`.

## Inventory contract

| Field | Value |
| --- | --- |
| `parity_status` | `not_applicable` |
| `tool_name` | empty (no dedicated UI tools for productPrices) |
| Flags | discovered, implemented, contract_tested, live_tested, vision_verified all true |
| `vision_evidence` | null (no retained frames) |
| `qualification.not_applicable_decision` | `accepted` |
| `qualification.sessions` | `dual_independent_ephemeral` |
| `qualification.evidence_ref` | `research162_product_prices_dual` |

## Contrast with annual reports

`ui.discovery.annual_reports` keeps **`not_applicable` rejected**: nav label
Årsrapporter and route family exist (Upsedasse on the test org is inaccessibility,
not absence). See [[ui_annual_reports_inaccessible]].

## Related surfaces that are not this freeze

- Products list/import shells remain greened for the **products** resource.
- Product create form dual is still residual (no create CTA / form fields).
- Nested price editor on a future product form would reopen productPrices
  mapping and invalidate pure NA.

## API lane note

Offline `api.productPrices.*` tools and contract tests are unchanged.
`live_tested` stays false with `out_of_scope_by_user`. No live API traffic.
