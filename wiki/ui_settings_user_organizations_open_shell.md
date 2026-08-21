---
name: ui_settings_user_organizations_open_shell
desc: Read-only Billy Indstillinger Virksomheder multi-org panel open; dual-counts api.special.user_organizations (research152).
tags: [billy, ui, settings, user_organizations, virksomheder, indstillinger, discovery, parity]
sources:
  - docs/superpowers/specs/2026-07-28-billy-mcp-complete-design.md
  - https://www.billy.dk/api/
created: 2026-08-01T09:50:00Z
updated: 2026-08-01T09:50:00Z
---

# ui_settings_user_organizations_open_shell

## Contract

| Field | Value |
| --- | --- |
| Tool | `ui_settings_user_organizations_open` |
| Coverage rows | `ui.discovery.settings_user_organizations`; dual-count `ui.parity.special.user_organizations` ↔ `api.special.user_organizations` |
| Open sequence | hub `/:org_slug/settings` then observe-only click **Profil** then **Virksomheder** |
| Success path class | `/:org_slug/settings` |
| Heading | `Indstillinger` |
| shell_kind | `settings_user_organizations` |
| Panel markers | `Virksomheder`, `Alle organisationer`, `Opret organisation` (chrome only) |
| Input | empty (`extra=forbid`) |
| Success fields | `path_class`, `heading`, `shell_kind`, `user_organizations_panel_markers_present` |
| parity_status | `shell_open_only` |

## Dual-count (research152)

- Soft `/userOrganizations` and related seeds dual soft-empty (body class = nonsense).
- Greened Virksomheder tool opens multi-org membership list chrome (Alle organisationer / Navn / CVR class).
- Maps docs `GET /v2/user/organizations` UI parity only. Does **not** green `user_get` (Profil), `users.list` (Brugere), `organizations.*` (company form), `invoice_email`, or `files_upload`.

## Non-claims

- Soft seeds alone are **not** success.
- Profil user-edit fields (Billede / Sprog og tema / Skift adgangskode) are **not** success for this tool.
- Company default, accounting, invoicing, Brugere, Momssatser panels are **not** success.
- Never click write CTAs (`Opret organisation`, `Gem ændringer`, Upload, password submit, Opret*, Tilføj*, Slet).
- No official Billy API settings resource. Do **not** invent `api_settings_*`.
- API `live_tested` remains false with `out_of_scope_by_user`.

## Qualification

- Offline unit/model/server registration tests.
- Live dual independent browser sessions (no `BILLY_API_TOKEN`).
- Vision review record under tmp with `purge_verified: true` after frame purge.
- research152 dual residual reconfirm for special.user_organizations dual-count.
