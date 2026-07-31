---
name: ui_settings_users_open_shell
desc: Read-only Billy Indstillinger Brugere (org users) settings panel open (research131 freeze).
tags: [billy, ui, settings, users, brugere, indstillinger, discovery]
sources:
  - docs/superpowers/specs/2026-07-28-billy-mcp-complete-design.md
  - https://www.billy.dk/api/
created: 2026-07-31T22:40:00Z
updated: 2026-07-31T22:40:00Z
---

# ui_settings_users_open_shell

## Contract

| Field | Value |
| --- | --- |
| Tool | `ui_settings_users_open` |
| Coverage row | `ui.discovery.settings_users` |
| Open sequence | hub `/:org_slug/settings` then observe-only click **Brugere** |
| Success path class | `/:org_slug/settings` |
| Heading | `Indstillinger` |
| shell_kind | `settings_users` |
| Panel markers | `Brugere`, `Revisorer og bogholdere` |
| Input | empty (`extra=forbid`) |
| Success fields | `path_class`, `heading`, `shell_kind`, `users_panel_markers_present` |
| parity_status | `shell_open_only` |

## Non-claims

- Soft seeds (`settings/users`, `settings/brugere`, `settings/team`, `settings/user`, …) are **not** success.
- Company default, accounting Regnskab, invoicing Faktura, user Profil, and VAT Momssatser panels are **not** success.
- Other settings panels (Abonnement, Adgangsnøgler, Betas) are **not** greened.
- Distinct from `ui_settings_user_open` (Profil / self account).
- No official Billy API settings resource. Do **not** invent `api_settings_*`.
- Offline `api_users_*` / `api_user_*` tools are a separate lane and are not greened by this open shell.
- Never click write CTAs (`Invitér`, `Invitér bruger`, `Invitér revisor`, `Overdrag ejerskab`, Find en bogholder*, Gem*, Opret*).
- Does not green settings_company, settings_accounting, settings_invoicing, settings_user, settings_vat, other settings_*, annual_reports, or prior shells.
- API `live_tested` remains false with `out_of_scope_by_user`.

## Qualification

- Offline unit/model/server registration tests.
- Live dual independent browser sessions (no `BILLY_API_TOKEN`).
- Vision review record under tmp with `purge_verified: true` after frame purge.
