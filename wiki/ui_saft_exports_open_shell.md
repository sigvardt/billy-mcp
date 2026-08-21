---
name: ui_saft_exports_open_shell
desc: Read-only Billy SAF-T CTA observe shell on exports hub (research122 freeze).
tags: [billy, ui, saft, exports, discovery]
sources:
  - docs/superpowers/specs/2026-07-28-billy-mcp-complete-design.md
  - https://www.billy.dk/api/
created: 2026-07-31T17:55:00Z
updated: 2026-07-31T17:55:00Z
---

# ui_saft_exports_open_shell

## Contract

| Field | Value |
| --- | --- |
| Tool | `ui_saft_exports_open` |
| Coverage row | `ui.discovery.saft_exports` |
| Path class | `/:org_slug/exports` (optional query allowed) |
| Heading | `Eksportér data` |
| Required CTA | `Eksportér som SAF-T` (observe-only; never click) |
| Input | empty (`extra=forbid`) |
| Success fields | `path_class`, `heading`, `saft_export_cta_observed` (true), `shell_markers_present` |
| parity_status | `shell_open_only` |

## Non-claims

- Soft `saft*` and singular `export` paths are **not** success.
- No dedicated SAF-T route; nested `exports/saft*` is not required.
- Distinct from `ui_exports_open` / `ui.discovery.exports` (SAF-T CTA is optional there).
- No official Billy API saft/export resource. Do **not** invent `api_saft_*`.
- Never click Eksportér som SAF-T, Eksport, Download, or generate/export actions.
- Does not green `ui.discovery.annual_reports`, settings_*, or re-implement exports.
- API `live_tested` remains false with `out_of_scope_by_user`.

## Qualification

- Offline unit/model/server registration tests.
- Live dual independent browser sessions (no `BILLY_API_TOKEN`).
- Vision review record under tmp with `purge_verified: true` after frame purge.
