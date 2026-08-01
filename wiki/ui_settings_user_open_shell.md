---
name: ui_settings_user_open_shell
desc: Read-only Billy Indstillinger Profil (user) settings panel open; dual-counts api.special.user_get (research129/151).
tags: [billy, ui, settings, user, profil, indstillinger, discovery, parity]
sources:
  - docs/superpowers/specs/2026-07-28-billy-mcp-complete-design.md
  - https://www.billy.dk/api/
created: 2026-07-31T21:40:00Z
updated: 2026-08-01T09:50:00Z
---

# ui_settings_user_open_shell

## Contract

| Field | Value |
| --- | --- |
| Tool | `ui_settings_user_open` |
| Coverage rows | `ui.discovery.settings_user`; dual-count `ui.parity.special.user_get` ↔ `api.special.user_get` |
| Open sequence | hub `/:org_slug/settings` then observe-only click **Profil** |
| Success path class | `/:org_slug/settings` |
| Heading | `Indstillinger` |
| shell_kind | `settings_user` |
| Panel markers | `Profil`, `Billede`, `Sprog og tema`, `Skift adgangskode` |
| Input | empty (`extra=forbid`) |
| Success fields | `path_class`, `heading`, `shell_kind`, `user_panel_markers_present` |
| parity_status | `shell_open_only` |

## Dual-count (research151)

- Soft `/user` and related seeds dual soft-empty (body class = nonsense).
- Greened Profil tool dual-ok; observe-only Profil click dual shows current-user fields (name/email/phone/picture/password change).
- Maps bootstrap `GET /v2/user` UI parity only. Does **not** green `user_organizations`, `users.get|update|bulk_*`, or org Brugere panel (`users.list` uses `ui_settings_users_open`).

## Non-claims

- Soft seeds (`settings/user`, `settings/profile`, query tabs) are **not** success.
- Company default, accounting Regnskab, and invoicing Faktura panels are **not** success.
- Other settings panels (Momssatser, Brugere, Abonnement, Adgangsnøgler, Betas) are **not** greened by this tool.
- Nested user sub-pages Notifikationer / Privatliv are **not** greened by this tool. Virksomheder multi-org membership is greened separately via `ui_settings_user_organizations_open` (research152).
- No official Billy API settings resource. Do **not** invent `api_settings_*`.
- Never click write CTAs (`Gem ændringer`, Upload, password submit, Opret*, Tilføj*).
- Does not green settings_company, settings_accounting, settings_invoicing, other settings_*, annual_reports, or prior shells beyond the listed dual-count.
- API `live_tested` remains false with `out_of_scope_by_user`.

## Qualification

- Offline unit/model/server registration tests.
- Live dual independent browser sessions (no `BILLY_API_TOKEN`).
- Vision review record under tmp with `purge_verified: true` after frame purge.
- research151 dual residual reconfirm for special.user_get dual-count.
