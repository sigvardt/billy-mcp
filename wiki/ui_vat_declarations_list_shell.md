---
name: ui_vat_declarations_list_shell
desc: Read-only Billy VAT declarations (Momsangivelser) list shell contract (research120 freeze).
tags: [billy, ui, vat_declarations, discovery]
sources:
  - docs/superpowers/specs/2026-07-28-billy-mcp-complete-design.md
  - https://www.billy.dk/api/
created: 2026-07-31T16:45:00Z
updated: 2026-07-31T16:45:00Z
---

# ui_vat_declarations_list_shell

## Contract

| Field | Value |
| --- | --- |
| Tool | `ui_vat_declarations_list` |
| Coverage row | `ui.discovery.vat_declarations` |
| Path class | `/:org_slug/vat-declarations` (optional query allowed) |
| Heading | `Momsangivelser` |
| Nav label | `Momsopgørelser` (sidebar; assert h1, not nav alone) |
| Chrome | `Periode` (empty table body valid) |
| Input | empty (`extra=forbid`) |
| Success fields | `path_class`, `heading`, `period_column_visible`, `shell_markers_present` |
| parity_status | `list_shell_open_only` |

## Non-claims

- Soft aliases (`vat`, `moms`, underscore `vat_declarations`, `sales-tax-returns`)
  are empty SPA chrome and are **not** success.
- Sibling families stay separate: reports (`Rapporter`), exports
  (`Eksportér data`), annual_reports (own freeze).
- Closest official API is `/v2/salesTaxReturns` (existing offline tools). Do
  **not** invent `api_vat_*` tools or re-scope salesTaxReturns from this shell.
- Never click declare, submit, create, export, download, or print.
- Does not green `ui.discovery.annual_reports`, `exports`, `saft_exports`, or
  settings_*.
- API `live_tested` remains false with `out_of_scope_by_user`.

## Qualification

- Offline unit/model/server registration tests.
- Live dual independent browser sessions (no `BILLY_API_TOKEN`).
- Vision review record under tmp with `purge_verified: true` after frame purge.
