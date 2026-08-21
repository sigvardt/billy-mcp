---
name: ui_daybooks_open_shell
desc: Read-only Billy daybook editor (Kassekladde) shell contract; dual-counts api.daybooks.list (research156) and api.daybooks.create (research157).
tags: [billy, ui, daybooks, discovery]
sources:
  - docs/superpowers/specs/2026-07-28-billy-mcp-complete-design.md
  - https://www.billy.dk/api/
created: 2026-07-31T15:20:00Z
updated: 2026-08-01T13:10:00Z
---

# ui_daybooks_open_shell

## Contract

| Field | Value |
| --- | --- |
| Tool | `ui_daybooks_open` |
| Coverage rows | `ui.discovery.daybooks`; dual-count `ui.parity.daybooks.list`; dual-count `ui.parity.daybooks.create` |
| Path class | `/:org_slug/daybooks/new` |
| Heading | empty allowed (editor has no h1 in freeze) |
| Editor markers | `Opret ny kassekladde`, `Tilføj kassekladdelinje`, `Ingen postering valgt` |
| Input | empty (`extra=forbid`) |
| Success fields | `path_class`, `heading`, `editor_markers_present`, `shell_markers_present` |
| parity_status | discovery/list: `shell_open_only`; create: `form_open_only` |
| Dual-count API | exact `api.daybooks.list` (research156); exact `api.daybooks.create` (research157) |

## Dual-count (research156 list)

Maps **`api.daybooks.list`** onto this existing editor shell only. Same dual-count
class as accounts.list → Regnskab and organizations.list → company settings.
Discovery keeps `api_row_id=None`. List parity keeps `api_row_id=api.daybooks.list`
with `shell_open_only` (bare index is Upsedasse; editor is the Billy daybook surface).

Evidence: dual independent headless sessions READY; tool dual-ok path
`/:org_slug/daybooks/new` with editor+shell markers; bare `/daybooks` dual
Upsedasse (not success); no create/add-line/post clicks; no `BILLY_API_TOKEN`.
Scratch dual JSON (non-git): `research156_residual_dual.json`.

## Dual-count (research157 create)

Maps **`api.daybooks.create`** onto the same tool with **`form_open_only`**.
Path is literally `/:org_slug/daybooks/new` with create CTAs (“Opret ny
kassekladde”, “Tilføj kassekladdelinje”). Open-only; product never submits.
Create parity keeps `api_row_id=api.daybooks.create`. Soft `/daybooks/new`
dual body non-empty (class 318); bare `/daybooks` still Upsedasse.

Evidence: research157 dual independent headless sessions READY; tool dual-ok;
create CTAs observe-only; no `BILLY_API_TOKEN`. Scratch dual JSON (non-git):
`research157_residual_dual.json`.

## Non-claims

- Bare `/:org_slug/daybooks` is a dual-session **Upsedasse!** error shell in the
  test organisation. This tool must not treat bare daybooks as success.
- Official `/v2/daybooks` API tools already exist offline. Do **not** invent
  additional daybooks API tools for this shell.
- Never click create/add-line/post CTAs (`Opret ny kassekladde`,
  `Tilføj kassekladdelinje`, Bogfør, Ny postering, …).
- Does not green `ui.discovery.transactions` (Posteringer list is separate).
- Does **not** green `ui.parity.daybooks.get|update|delete|bulk_*`.
- Does **not** green nested daybookTransactions / daybookTransactionLines /
  daybookBalanceAccounts parity rows.
- Soft aliases (`kassekladde`, `daybook`, …) are not this tool's success path.
- API `live_tested` remains false with `out_of_scope_by_user`.

## Qualification

- Offline unit/model/server registration tests.
- Live dual independent browser sessions (no `BILLY_API_TOKEN`).
- Vision review record under tmp with `purge_verified: true` after frame purge.
- Inventory dual-count asserts research156 list + research157 create + exact ids.
