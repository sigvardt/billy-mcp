---
name: ui_settings_beta_open_shell
desc: Read-only Billy Indstillinger Betas (Tidlig adgang) settings panel open (research133 freeze).
tags: [billy, ui, settings, beta, betas, tidlig-adgang, indstillinger, discovery]
sources:
  - docs/superpowers/specs/2026-07-28-billy-mcp-complete-design.md
  - https://www.billy.dk/api/
created: 2026-07-31T23:58:00Z
updated: 2026-07-31T23:58:00Z
---

# ui_settings_beta_open_shell

## Contract

| Field | Value |
| --- | --- |
| Tool | `ui_settings_beta_open` |
| Coverage row | `ui.discovery.settings_beta` |
| Open sequence | hub `/:org_slug/settings` then observe-only click **Betas** |
| Success path class | `/:org_slug/settings` |
| Heading | `Indstillinger` |
| shell_kind | `settings_beta` |
| Panel markers | `Betas`, `Tidlig adgang` |
| Input | empty (`extra=forbid`) |
| Success fields | `path_class`, `heading`, `shell_kind`, `beta_panel_markers_present` |
| parity_status | `shell_open_only` |

## Non-claims

- Soft seeds (`settings/beta`, `settings/labs`, `settings/experimental`, …) are **not** sole success. Soft seed `settings/betas` may dual-open beta but product uses hub+click.
- Company default, accounting Regnskab, invoicing Faktura, user Profil, VAT Momssatser, users Brugere, and access-token Adgangsnøgler panels are **not** success.
- Other settings panels (Abonnement empty chrome) are **not** greened by this open shell alone.
- No official Billy API settings or beta / early-access CRUD resource. Do **not** invent `api_settings_*` or `api_beta_*`.
- Never click write CTAs (`Opret*`, Gem*, Tilføj*, Slet, Upload, Opgrader*).
- Does not green settings_company, settings_accounting, settings_invoicing, settings_user, settings_vat, settings_users, settings_access_token, settings_subscription, annual_reports, or prior shells.
- API `live_tested` remains false with `out_of_scope_by_user`.

## Qualification

- Offline unit/model/server registration tests.
- Live dual independent browser sessions (no `BILLY_API_TOKEN`).
- Vision review record under tmp with `purge_verified: true` after frame purge.
