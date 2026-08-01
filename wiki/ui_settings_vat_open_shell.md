---
name: ui_settings_vat_open_shell
desc: Read-only Billy Indstillinger Momssatser (VAT) settings panel; dual-counts api.taxRates.list (research158) and api.salesTaxRulesets.list (research159).
tags: [billy, ui, settings, vat, momssatser, indstillinger, discovery, taxRates, salesTaxRulesets]
sources:
  - docs/superpowers/specs/2026-07-28-billy-mcp-complete-design.md
  - https://www.billy.dk/api/
created: 2026-07-31T22:10:00Z
updated: 2026-08-01T14:30:00Z
---

# ui_settings_vat_open_shell

## Contract

| Field | Value |
| --- | --- |
| Tool | `ui_settings_vat_open` |
| Coverage rows | `ui.discovery.settings_vat`, `ui.parity.taxRates.list` (maps `api.taxRates.list`), `ui.parity.salesTaxRulesets.list` (maps `api.salesTaxRulesets.list`) |
| Open sequence | hub `/:org_slug/settings` then observe-only click **Momssatser** |
| Success path class | `/:org_slug/settings` |
| Heading | `Indstillinger` |
| shell_kind | `settings_vat` |
| Panel markers | `Regelsæt`, `Satser for salg`, `Satser for køb` |
| Input | empty (`extra=forbid`) |
| Success fields | `path_class`, `heading`, `shell_kind`, `vat_panel_markers_present` |
| parity_status | `shell_open_only` |

## Dual-count (`api.taxRates.list`)

- research158 dual independent headless sessions: typed tool dual-ok with
  `vat_panel_markers_present=true`; soft `/taxRates`, `/tax-rates`,
  `/momssatser`, `/settings/vat` body 127 soft-empty (= nonsense).
- Soft hub `/settings` shows Momssatser in side nav; VAT panel requires tool
  click (Regelsæt + Satser for salg + Satser for køb).
- `ui.parity.taxRates.list` maps to this tool with `parity_status=shell_open_only`
  (Satser sections).
- API list filters/sort/pagination UI not producted.
- Offline `api.taxRates.list` remains `live_tested: false` / `out_of_scope_by_user`.

## Dual-count (`api.salesTaxRulesets.list`)

- research159 dual independent headless sessions: typed tool dual-ok with
  `vat_panel_markers_present=true` (signature includes **Regelsæt**); soft
  `/salesTaxRulesets` body 127 soft-empty (= nonsense).
- `ui.parity.salesTaxRulesets.list` maps to this tool with
  `parity_status=shell_open_only` (Regelsæt section on same Momssatser panel).
- API list filters/sort/pagination UI not producted.
- Offline `api.salesTaxRulesets.list` remains `live_tested: false` /
  `out_of_scope_by_user`.
- Does **not** green residual `salesTaxRulesets.get|create|update|delete|bulk_*`
  or nested `salesTaxRules.*` / `taxRateDeductionComponents.*`.

## Non-claims

- Soft seeds (`settings/vat`, `settings/moms`, `settings/tax`, `taxRates`,
  `salesTaxRulesets`, …) are **not** success.
- Company default, accounting Regnskab, invoicing Faktura, and user Profil panels are **not** success.
- Other settings panels (Brugere, Abonnement, Adgangsnøgler, Betas) are **not** greened.
- No official Billy API settings resource. Do **not** invent `api_settings_*`.
- Does **not** green `taxRates.get|create|update|delete|bulk_*` UI parity.
- Does **not** green nested `salesTaxRules.*` / `taxRateDeductionComponents.*` UI parity.
- Does **not** green residual `salesTaxRulesets` write/detail/bulk UI parity.
- Offline salesTax API tools are a separate lane; this open shell dual-counts only
  `taxRates.list` and `salesTaxRulesets.list`.
- Never click write CTAs (`Opret`, `Opret regelsæt`, `Opret sats`, Gem*, Tilføj*).
- Does not green settings_company, settings_accounting, settings_invoicing, settings_user, other settings_*, annual_reports, or prior shells.
- API `live_tested` remains false with `out_of_scope_by_user`.

## Qualification

- Offline unit/model/server registration tests.
- Live dual independent browser sessions (no `BILLY_API_TOKEN`).
- Vision review record under tmp with `purge_verified: true` after frame purge.
