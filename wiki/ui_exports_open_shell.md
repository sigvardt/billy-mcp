---
name: ui_exports_open_shell
desc: Read-only Billy exports (Eksportér data) hub shell contract (research121 freeze).
tags: [billy, ui, exports, discovery]
sources:
  - docs/superpowers/specs/2026-07-28-billy-mcp-complete-design.md
  - https://www.billy.dk/api/
created: 2026-07-31T17:30:00Z
updated: 2026-07-31T17:30:00Z
---

# ui_exports_open_shell

## Contract

| Field | Value |
| --- | --- |
| Tool | `ui_exports_open` |
| Coverage row | `ui.discovery.exports` |
| Path class | `/:org_slug/exports` (optional query allowed) |
| Heading | `Eksportér data` |
| Nav label | `Eksportér data` (sidebar under Regnskab) |
| Chrome | export category hub; `Eksport` / `Download` / `Eksportér som SAF-T` observe-only |
| Input | empty (`extra=forbid`) |
| Success fields | `path_class`, `heading`, `saft_export_cta_observed`, `shell_markers_present` |
| parity_status | `shell_open_only` |

## Non-claims

- Soft aliases and wrong spellings are **not** success.
- Sibling families stay separate: reports (`Rapporter`), vat-declarations
  (`Momsangivelser`), annual_reports (inaccessible Upsedasse freeze).
- No official Billy API exports resource. Do **not** invent `api_exports_*`.
- Never click Eksport, Download, Eksportér som SAF-T, or any download control.
- Observing SAF-T CTA presence does **not** green `ui.discovery.saft_exports`.
- Does not green `ui.discovery.annual_reports`, `saft_exports`, or settings_*.
- API `live_tested` remains false with `out_of_scope_by_user`.

## Qualification

- Offline unit/model/server registration tests.
- Live dual independent browser sessions (no `BILLY_API_TOKEN`).
- Vision review record under tmp with `purge_verified: true` after frame purge.
