---
name: ui_settings_access_token_open_shell
desc: Read-only Billy Indstillinger Adgangsnøgler (access keys) settings panel open (research132 freeze).
tags: [billy, ui, settings, access_token, adgangsnogler, indstillinger, discovery]
sources:
  - docs/superpowers/specs/2026-07-28-billy-mcp-complete-design.md
  - https://www.billy.dk/api/
created: 2026-07-31T23:15:00Z
updated: 2026-07-31T23:15:00Z
---

# ui_settings_access_token_open_shell

## Contract

| Field | Value |
| --- | --- |
| Tool | `ui_settings_access_token_open` |
| Coverage row | `ui.discovery.settings_access_token` |
| Open sequence | hub `/:org_slug/settings` then observe-only click **Adgangsnøgler** |
| Success path class | `/:org_slug/settings` |
| Heading | `Indstillinger` |
| shell_kind | `settings_access_token` |
| Panel markers | `Adgangsnøgler` |
| Input | empty (`extra=forbid`) |
| Success fields | `path_class`, `heading`, `shell_kind`, `access_token_panel_markers_present` |
| parity_status | `shell_open_only` |

## Non-claims

- Soft seeds (`settings/access-token`, `settings/api`, `settings/keys`, …) are **not** success.
- Company default, accounting Regnskab, invoicing Faktura, user Profil, VAT Momssatser, users Brugere, and beta panels are **not** success.
- Other settings panels (Abonnement empty chrome, Betas product) are **not** greened by this open shell alone.
- No official Billy API settings or access-keys CRUD resource. Do **not** invent `api_settings_*` or `api_access_token_*`.
- Official docs OAuth/API-token **authentication** prose is a separate lane and is not greened by this UI open tool.
- Never click write CTAs (`Opret adgangsnøgle`, Gem*, Opret*, Slet, Upload).
- Does not green settings_company, settings_accounting, settings_invoicing, settings_user, settings_vat, settings_users, settings_beta, settings_subscription, annual_reports, or prior shells.
- API `live_tested` remains false with `out_of_scope_by_user`.
- Never log or return secret key material.

## Qualification

- Offline unit/model/server registration tests.
- Live dual independent browser sessions (no `BILLY_API_TOKEN`).
- Vision review record under tmp with `purge_verified: true` after frame purge.
