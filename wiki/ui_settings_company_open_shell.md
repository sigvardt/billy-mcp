---
name: ui_settings_company_open_shell
desc: Read-only Billy Indstillinger company settings shell open (research126); dual-counts api.organizations.list (research146).
tags: [billy, ui, settings, company, indstillinger, discovery, organizations, parity]
sources:
  - docs/superpowers/specs/2026-07-28-billy-mcp-complete-design.md
  - https://www.billy.dk/api/
created: 2026-07-31T20:00:00Z
updated: 2026-08-01T06:25:00Z
---

# ui_settings_company_open_shell

## Contract

| Field | Value |
| --- | --- |
| Tool | `ui_settings_company_open` |
| Coverage rows | `ui.discovery.settings_company`; dual-count `ui.parity.organizations.list` → `api.organizations.list` (research146) |
| Path class | `/:org_slug/settings` |
| Heading | `Indstillinger` |
| shell_kind | `settings_company` |
| Panel markers | `Navn og adresse`, `Kontaktinformation` (default Virksomhed panel) |
| Input | empty (`extra=forbid`) |
| Success fields | `path_class`, `heading`, `shell_kind`, `company_panel_markers_present` |
| parity_status | `shell_open_only` (settings multi-section panel; not a dedicated `/organizations` list route) |

## Dual-count (research146)

- Soft seeds `/organizations`, `/organization`, `/company` dual soft-empty (body length equals nonsense control). No dedicated multi-org list route in the app.
- Active-org identity is the Indstillinger company / Virksomhed panel opened by `ui_settings_company_open`.
- Only **`api.organizations.list`** is greened as shell-open parity. get/create/update/bulk stay red.
- API list filters, sort, and pagination UI are not producted.
- API offline list remains contract-tested with `live_tested: false` and `out_of_scope_by_user`.

## Non-claims

- Soft nested paths (`settings/company`, `settings/vat`, `settings/users`, …) are **not** success.
- Other settings panels (Regnskab, Faktura, Profil, Brugere, Abonnement, Adgangsnøgler, Betas) are **not** greened by this tool.
- No official Billy API settings resource. Do **not** invent `api_settings_*`.
- Never click write CTAs (`Gem ændringer`, `Tilføj ejer`, upload, Opret*).
- Does not green other settings_*, annual_reports, inventory, or prior shells.
- Does not green `ui.parity.organizations.get|create|update|bulk_save|bulk_delete`.
- API `live_tested` remains false with `out_of_scope_by_user`.

## Qualification

- Offline unit/model/server registration tests.
- Live dual independent browser sessions (no `BILLY_API_TOKEN`).
- research146 dual-session reconfirm for organizations.list dual-count.
- Vision review record under tmp with `purge_verified: true` after frame purge.
