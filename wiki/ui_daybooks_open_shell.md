---
name: ui_daybooks_open_shell
desc: Read-only Billy daybook editor (Kassekladde) shell contract (research117 freeze).
tags: [billy, ui, daybooks, discovery]
sources:
  - docs/superpowers/specs/2026-07-28-billy-mcp-complete-design.md
  - https://www.billy.dk/api/
created: 2026-07-31T15:20:00Z
updated: 2026-07-31T15:20:00Z
---

# ui_daybooks_open_shell

## Contract

| Field | Value |
| --- | --- |
| Tool | `ui_daybooks_open` |
| Coverage row | `ui.discovery.daybooks` |
| Path class | `/:org_slug/daybooks/new` |
| Heading | empty allowed (editor has no h1 in freeze) |
| Editor markers | `Opret ny kassekladde`, `Tilføj kassekladdelinje`, `Ingen postering valgt` |
| Input | empty (`extra=forbid`) |
| Success fields | `path_class`, `heading`, `editor_markers_present`, `shell_markers_present` |
| parity_status | `shell_open_only` |

## Non-claims

- Bare `/:org_slug/daybooks` is a dual-session **Upsedasse!** error shell in the
  test organisation. This tool must not treat bare daybooks as success.
- Official `/v2/daybooks` API tools already exist offline. Do **not** invent
  additional daybooks API tools for this shell.
- Never click create/add-line/post CTAs (`Opret ny kassekladde`,
  `Tilføj kassekladdelinje`, Bogfør, Ny postering, …).
- Does not green `ui.discovery.transactions` (Posteringer list is separate).
- Does not green `ui.parity.daybook*` rows.
- Soft aliases (`kassekladde`, `daybook`, …) are not this tool's success path.
- API `live_tested` remains false with `out_of_scope_by_user`.

## Qualification

- Offline unit/model/server registration tests.
- Live dual independent browser sessions (no `BILLY_API_TOKEN`).
- Vision review record under tmp with `purge_verified: true` after frame purge.
