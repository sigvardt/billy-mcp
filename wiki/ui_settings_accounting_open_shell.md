---
name: ui_settings_accounting_open_shell
desc: Read-only Billy Indstillinger Regnskab/Kontoplan settings panel; dual-counts api.accounts.list (research145).
tags: [billy, ui, settings, accounting, regnskab, indstillinger, discovery]
sources:
  - docs/superpowers/specs/2026-07-28-billy-mcp-complete-design.md
  - https://www.billy.dk/api/
created: 2026-07-31T20:30:00Z
updated: 2026-08-01T05:50:00Z
---

# ui_settings_accounting_open_shell

## Contract

| Field | Value |
| --- | --- |
| Tool | `ui_settings_accounting_open` |
| Coverage rows | `ui.discovery.settings_accounting`, `ui.parity.accounts.list` (maps `api.accounts.list`) |
| Open seed | `/:org_slug/settings/accounting` (SPA rewrites to bare hub) |
| Success path class | `/:org_slug/settings` |
| Heading | `Indstillinger` |
| shell_kind | `settings_accounting` |
| Panel markers | `Regnskab`, `Køb`, `Kontoplan` (also expect Bankafstemning, Momsopgørelse) |
| Input | empty (`extra=forbid`) |
| Success fields | `path_class`, `heading`, `shell_kind`, `accounting_panel_markers_present` |
| parity_status | `shell_open_only` |

## Non-claims

- Bare hub open (company default Virksomhed panel) is **not** success for this tool.
- Soft nested paths (`settings/company`, `settings/vat`, `settings/bogfoering`, …) are **not** success.
- Faktura panel (`settings/invoicing`) is **not** greened by this tool.
- Other settings panels (Profil, Momssatser, Brugere, Abonnement, Adgangsnøgler, Betas) are **not** greened.
- No official Billy API settings resource. Do **not** invent `api_settings_*`.
- Never click write CTAs (`Gem ændringer`, `Sæt låsedato`, Opret*, Tilføj*, Upload, Opgrader).
- Does not green settings_company, other settings_*, annual_reports, or prior shells.
- API `live_tested` remains false with `out_of_scope_by_user`.


## Dual-count (research145)

- `ui.parity.accounts.list` maps to this tool with `parity_status=shell_open_only`.
- Evidence: research127 product + research145 dual independent ephemeral sessions
  (no `BILLY_API_TOKEN`): accounting tool dual-ok; deep Kontoplan/Regnskab markers;
  soft `/accounts` rewrites to `/settings` with Kontoplan; pure `kontoplan` /
  `chart-of-accounts` soft-empty like nonsense.
- Offline `api.accounts.list` remains `live_tested: false` / `out_of_scope_by_user`.
- Does **not** green `ui.parity.accounts.get|create|update|delete|bulk_*`.
- Does **not** invent a dedicated `/:org_slug/accounts` list tool.

## Qualification

- Offline unit/model/server registration tests.
- Live dual independent browser sessions (no `BILLY_API_TOKEN`).
- Vision review record under tmp with `purge_verified: true` after frame purge.
