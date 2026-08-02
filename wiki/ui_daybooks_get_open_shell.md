---
name: ui_daybooks_get_open_shell
desc: Read-only daybook detail get-open UI tool (research179); path /:org_slug/daybooks/:id.
tags: [billy, ui, daybooks, get, research179]
sources:
  - https://www.billy.dk/api/
  - docs/superpowers/specs/2026-07-28-billy-mcp-complete-design.md
  - tmp/research179_focus_dual.json
  - coverage/ui_workflows_manifest.yaml
created: 2026-08-02T08:40:00Z
updated: 2026-08-02T08:40:00Z
---

# ui_daybooks_get_open_shell

Typed tool `ui_daybooks_get_open` opens an **existing** Billy daybook editor surface for the authenticated headless session.

| Field | Value |
| --- | --- |
| Path class | `/:org_slug/daybooks/:id` |
| Shell kind | `daybooks_get` |
| Maps | `api.daybooks.get` only |
| Kind | `detail_open_only` |
| Evidence | research179 dual SPA-seeded daybook; editor markers dual |

## Markers (non-PII)

- Opret ny kassekladde
- Tilføj kassekladdelinje
- Ingen postering valgt

## Non-goals

- Does not create daybooks, add lines, post, or delete
- Distinct from `ui_daybooks_open` list+create on `/daybooks/new`
- Does not green daybooks.update or daybooks.delete (research179 DEFER)

## Qualification

Live dual-session test `tests/live/test_ui_daybooks_get_open.py` with independent second profile, DOM markers, vision record under node tmp (frames purged).
