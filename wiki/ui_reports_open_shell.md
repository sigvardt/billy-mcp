---
name: ui_reports_open_shell
desc: Read-only Billy reports (Rapporter) hub shell contract (research119 freeze).
tags: [billy, ui, reports, discovery]
sources:
  - docs/superpowers/specs/2026-07-28-billy-mcp-complete-design.md
  - https://www.billy.dk/api/
created: 2026-07-31T16:15:00Z
updated: 2026-07-31T16:15:00Z
---

# ui_reports_open_shell

## Contract

| Field | Value |
| --- | --- |
| Tool | `ui_reports_open` |
| Coverage row | `ui.discovery.reports` |
| Path class | `/:org_slug/reports-all` (optional tab `profit-and-loss` / `balance` / `trial-balance`; query params allowed) |
| Heading | `Rapporter` |
| Export CTA | `Eksport` present (observe only; never click) |
| Tabs | Resultatopgørelse, Balance, Saldobalance |
| Input | empty (`extra=forbid`) |
| Success fields | `path_class`, `heading`, `export_action_visible`, `shell_markers_present` |
| parity_status | `shell_open_only` |

## Non-claims

- Bare `/:org_slug/reports` is soft empty chrome and is **not** hub success.
- Sibling families stay separate: exports (`Eksportér data`), vat-declarations
  (`Momsangivelser`), annual_reports (own freeze).
- Official docs have **no** `/v2/reports` resource. Do **not** invent
  `api_reports_*` tools.
- Never click `Eksport`, download, generate, print, or submit export actions.
- Does not green `ui.discovery.vat_declarations`, `annual_reports`, `exports`,
  or `saft_exports`.
- API `live_tested` remains false with `out_of_scope_by_user`.

## Qualification

- Offline unit/model/server registration tests.
- Live dual independent browser sessions (no `BILLY_API_TOKEN`).
- Vision review record under tmp with `purge_verified: true` after frame purge.
