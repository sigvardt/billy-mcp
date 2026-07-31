---
name: ui_settings_user_open_shell
desc: Read-only Billy Indstillinger Profil (user) settings panel open (research129 freeze).
tags: [billy, ui, settings, user, profil, indstillinger, discovery]
sources:
  - docs/superpowers/specs/2026-07-28-billy-mcp-complete-design.md
  - https://www.billy.dk/api/
created: 2026-07-31T21:40:00Z
updated: 2026-07-31T21:40:00Z
---

# ui_settings_user_open_shell

## Contract

| Field | Value |
| --- | --- |
| Tool | `ui_settings_user_open` |
| Coverage row | `ui.discovery.settings_user` |
| Open sequence | hub `/:org_slug/settings` then observe-only click **Profil** |
| Success path class | `/:org_slug/settings` |
| Heading | `Indstillinger` |
| shell_kind | `settings_user` |
| Panel markers | `Profil`, `Billede`, `Sprog og tema`, `Skift adgangskode` |
| Input | empty (`extra=forbid`) |
| Success fields | `path_class`, `heading`, `shell_kind`, `user_panel_markers_present` |
| parity_status | `shell_open_only` |

## Non-claims

- Soft seeds (`settings/user`, `settings/profile`, query tabs) are **not** success.
- Company default, accounting Regnskab, and invoicing Faktura panels are **not** success.
- Other settings panels (Momssatser, Brugere, Abonnement, Adgangsnøgler, Betas) are **not** greened.
- Nested user sub-pages (Notifikationer, Privatliv, Virksomheder) are **not** greened.
- No official Billy API settings resource. Do **not** invent `api_settings_*`.
- Never click write CTAs (`Gem ændringer`, Upload, password submit, Opret*, Tilføj*).
- Does not green settings_company, settings_accounting, settings_invoicing, other settings_*, annual_reports, or prior shells.
- API `live_tested` remains false with `out_of_scope_by_user`.

## Qualification

- Offline unit/model/server registration tests.
- Live dual independent browser sessions (no `BILLY_API_TOKEN`).
- Vision review record under tmp with `purge_verified: true` after frame purge.
