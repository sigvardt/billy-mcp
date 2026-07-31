---
name: ui_settings_invoicing_open_shell
desc: Read-only Billy Indstillinger Faktura (invoicing) settings panel open (research128 freeze).
tags: [billy, ui, settings, invoicing, faktura, indstillinger, discovery]
sources:
  - docs/superpowers/specs/2026-07-28-billy-mcp-complete-design.md
  - https://www.billy.dk/api/
created: 2026-07-31T21:25:00Z
updated: 2026-07-31T21:25:00Z
---

# ui_settings_invoicing_open_shell

## Contract

| Field | Value |
| --- | --- |
| Tool | `ui_settings_invoicing_open` |
| Coverage row | `ui.discovery.settings_invoicing` |
| Open seed | `/:org_slug/settings/invoicing` (SPA rewrites to bare hub) |
| Success path class | `/:org_slug/settings` |
| Heading | `Indstillinger` |
| shell_kind | `settings_invoicing` |
| Panel markers | `Faktura`, `Produkter`, and `Betalingsmetoder` or `Standard fakturalogo` |
| Input | empty (`extra=forbid`) |
| Success fields | `path_class`, `heading`, `shell_kind`, `invoicing_panel_markers_present` |
| parity_status | `shell_open_only` |

## Non-claims

- Bare hub open (company default Virksomhed panel) is **not** success for this tool.
- Accounting Regnskab panel (`settings/accounting`) is **not** success for this tool.
- Soft nested paths (`settings/company`, `settings/faktura`, `settings/invoice`, `settings/vat`, …) are **not** success.
- Other settings panels (Profil, Momssatser, Brugere, Abonnement, Adgangsnøgler, Betas) are **not** greened.
- No official Billy API settings resource. Do **not** invent `api_settings_*`.
- Never click write CTAs (`Gem ændringer`, Opret*, Tilføj*, Upload, Opgrader, Opret betalingsmetode).
- Does not green settings_company, settings_accounting, other settings_*, annual_reports, or prior shells.
- API `live_tested` remains false with `out_of_scope_by_user`.

## Qualification

- Offline unit/model/server registration tests.
- Live dual independent browser sessions (no `BILLY_API_TOKEN`).
- Vision review record under tmp with `purge_verified: true` after frame purge.
