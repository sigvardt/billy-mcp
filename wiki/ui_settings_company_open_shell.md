---
name: ui_settings_company_open_shell
desc: Read-only Billy Indstillinger company settings shell; dual-counts organizations.list (research146) plus get/update (research177); create is NA.
tags: [billy, ui, settings, company, indstillinger, discovery, organizations, parity]
sources:
  - docs/superpowers/specs/2026-07-28-billy-mcp-complete-design.md
  - https://www.billy.dk/api/
created: 2026-07-31T20:00:00Z
updated: 2026-08-02T04:00:00Z
---

# ui_settings_company_open_shell

## Contract

| Field | Value |
| --- | --- |
| Tool | `ui_settings_company_open` |
| Coverage rows | `ui.discovery.settings_company`; dual-count `ui.parity.organizations.list` → `api.organizations.list` (research146); dual-count `ui.parity.organizations.get` → `api.organizations.get` (research177, `detail_open_only`); dual-count `ui.parity.organizations.update` → `api.organizations.update` (research177, `form_open_only`) |
| Path class | `/:org_slug/settings` |
| Heading | `Indstillinger` |
| shell_kind | `settings_company` |
| Panel markers | `Navn og adresse`, `Kontaktinformation` (default Virksomhed panel) |
| Identity form fields (get) | Navn/CVR/Adresse family (`name`, `registrationNo`, street/city/country/phone/email, …) |
| Update chrome | `Gem ændringer` present; **never clicked** |
| Input | empty (`extra=forbid`) |
| Success fields | `path_class`, `heading`, `shell_kind`, `company_panel_markers_present` |

## Dual-count

### research146 — organizations.list (`shell_open_only`)

- Soft seeds `/organizations`, `/organization`, `/company` dual soft-empty. No dedicated multi-org list route.
- Active-org identity surface is the Indstillinger company / Virksomhed panel.
- API list filters, sort, and pagination UI are not producted.

### research177 — organizations.get (`detail_open_only`)

- Dual independent headless sessions: company panel identity fields dual (Navn/CVR/Adresse family; inputs_n 12 dual).
- Maps **get** onto the same tool with stronger identity freeze; observe-only.

### research177 — organizations.update (`form_open_only`)

- Same panel with **Gem ændringer = 1 dual**; never click Gem / Tilføj ejer / upload.
- Sensitivity medium (form write surface open-only; peer daybooks.create).

### research177 — organizations.create (`not_applicable`)

- Create CTAs (Opret/Ny/Tilføj virksomhed) **0 dual**.
- See `wiki/ui_organizations_create_not_applicable.md`.
- Exact id freeze only; does not steal list/get/update dual-count or bulk rows.

## Non-claims

- Soft nested paths (`settings/company`, `settings/vat`, `settings/users`, …) are **not** success.
- Other settings panels (Regnskab, Faktura, Profil, Brugere, Abonnement, Adgangsnøgler, Betas) are **not** greened by this tool.
- No official Billy API settings resource. Do **not** invent `api_settings_*`.
- Never click write CTAs (`Gem ændringer`, `Tilføj ejer`, upload, Opret*).
- Does not green other settings_*, annual_reports, inventory, or prior shells.
- Does not green `ui.parity.organizations.bulk_save|bulk_delete` (external-contract bulk freeze).
- API `live_tested` remains false with `out_of_scope_by_user`.

## Qualification

- Offline unit/model/server registration tests.
- Live dual independent browser sessions (no `BILLY_API_TOKEN`).
- research146 list dual-count; research177 get/update dual-count + create NA.
- Vision review record under tmp with `purge_verified: true` after frame purge.
