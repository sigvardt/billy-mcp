---
name: ui_addons_open_shell
desc: Read-only Billy Fordele (add-ons) hub shell open (research123 freeze).
tags: [billy, ui, addons, fordele, discovery]
sources:
  - docs/superpowers/specs/2026-07-28-billy-mcp-complete-design.md
  - https://www.billy.dk/api/
created: 2026-07-31T18:30:00Z
updated: 2026-07-31T18:30:00Z
---

# ui_addons_open_shell

## Contract

| Field | Value |
| --- | --- |
| Tool | `ui_addons_open` |
| Coverage row | `ui.discovery.addons` |
| Path class | `/:org_slug/add-ons` (hyphen required; optional query allowed) |
| Heading | `Fordele` |
| Nav label | `Udforsk integrationer` (observe; not required for success) |
| Input | empty (`extra=forbid`) |
| Success fields | `path_class`, `heading`, `shell_markers_present` |
| parity_status | `shell_open_only` |

## Non-claims

- Soft paths (`addons`, `integrations`, nested, `settings/*`, apps/marketplace) are **not** success.
- No official Billy API addons/integrations resource. Do **not** invent `api_addons_*`.
- Never click partner CTAs (Opret adgangsnøgle, Tilføj som betalingsmetode, Aktivér rykkerservice, Kom i gang, Ansøg om lån, Læs mere, Se alle vores integrationer, Install/Connect).
- Does not green `ui.discovery.integrations`, inventory, settings_*, or annual_reports.
- API `live_tested` remains false with `out_of_scope_by_user`.

## Qualification

- Offline unit/model/server registration tests.
- Live dual independent browser sessions (no `BILLY_API_TOKEN`).
- Vision review record under tmp with `purge_verified: true` after frame purge.
