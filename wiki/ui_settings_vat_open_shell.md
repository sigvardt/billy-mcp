---
name: ui_settings_vat_open_shell
desc: Read-only Billy Indstillinger Momssatser (VAT) settings panel open (research130 freeze).
tags: [billy, ui, settings, vat, momssatser, indstillinger, discovery]
sources:
  - docs/superpowers/specs/2026-07-28-billy-mcp-complete-design.md
  - https://www.billy.dk/api/
created: 2026-07-31T22:10:00Z
updated: 2026-07-31T22:10:00Z
---

# ui_settings_vat_open_shell

## Contract

| Field | Value |
| --- | --- |
| Tool | `ui_settings_vat_open` |
| Coverage row | `ui.discovery.settings_vat` |
| Open sequence | hub `/:org_slug/settings` then observe-only click **Momssatser** |
| Success path class | `/:org_slug/settings` |
| Heading | `Indstillinger` |
| shell_kind | `settings_vat` |
| Panel markers | `Regelsæt`, `Satser for salg`, `Satser for køb` |
| Input | empty (`extra=forbid`) |
| Success fields | `path_class`, `heading`, `shell_kind`, `vat_panel_markers_present` |
| parity_status | `shell_open_only` |

## Non-claims

- Soft seeds (`settings/vat`, `settings/moms`, `settings/tax`, …) are **not** success.
- Company default, accounting Regnskab, invoicing Faktura, and user Profil panels are **not** success.
- Other settings panels (Brugere, Abonnement, Adgangsnøgler, Betas) are **not** greened.
- No official Billy API settings resource. Do **not** invent `api_settings_*`.
- Offline salesTax API tools are a separate lane and are not greened by this open shell.
- Never click write CTAs (`Opret`, `Opret regelsæt`, `Opret sats`, Gem*, Tilføj*).
- Does not green settings_company, settings_accounting, settings_invoicing, settings_user, other settings_*, annual_reports, or prior shells.
- API `live_tested` remains false with `out_of_scope_by_user`.

## Qualification

- Offline unit/model/server registration tests.
- Live dual independent browser sessions (no `BILLY_API_TOKEN`).
- Vision review record under tmp with `purge_verified: true` after frame purge.
