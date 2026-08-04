---
name: ui_annual_reports_inaccessible
title: Annual reports owner out of scope for this deployment
desc: Owner skip (radio DC3B8E96, 2026-08-04) marks ui.discovery.annual_reports out_of_scope_by_user; no tool; not_applicable rejected; historical dual Upsedasse retained.
tags: [billy, ui, discovery, annual_reports, out_of_scope]
sources:
  - radio:DC3B8E96
  - https://mit.billy.dk/
  - docs/superpowers/specs/2026-07-28-billy-mcp-complete-design.md
  - .fractal/main.billy_complete/tmp/discovery122/summary_dual_saft.json
  - .fractal/main.billy_complete/tmp/research191_annual_dual.json
created: 2026-08-01T01:45:00Z
updated: 2026-08-04T10:00:00Z
---

# Annual reports owner out of scope for this deployment

## Decision (current)

`ui.discovery.annual_reports` is **out of scope by user** for this MCP
deployment. Owner radio `DC3B8E96` (2026-08-04): Årsrapporter is not included
in Joakim's Billy plan and must be skipped. It is **not** a completion blocker.

| Field | Value |
| --- | --- |
| Row | `ui.discovery.annual_reports` |
| `qualification.kind` | `out_of_scope_by_user` |
| `scope_code` | `ANNUAL_REPORTS_OWNER_SKIP` |
| `owner_decision_ref` | `radio:DC3B8E96` |
| `tools_allowed` | false |
| Tool | none (do not invent `ui_annual_*` or `api_annual_*`) |
| `parity_status` | `out_of_scope_by_user` |
| Live / vision green | false (not dual-qualified; completeness excludes owner-scoped rows) |

Honest UI `not_applicable` remains **rejected**: nav label **Årsrapporter** and
route family `/:org_slug/annual_reports` exist. Owner skip is plan scope, not
absence of a Billy UI workflow.

## Supersession

This page previously froze dual-session Upsedasse as
`ANNUAL_REPORTS_ORG_INACCESSIBLE` (stay red until a non-Upsedasse org). That
blocker is **superseded for qualification completeness** by the owner plan
decision. Historical dual evidence is retained below and in
`prior_evidence_ref` / `historical_dual_ref` on the inventory row.

## Historical dual-session evidence (dedicated non-production org)

### research122 freeze

| Field | Result |
| --- | --- |
| Path class | `/:org_slug/annual_reports` |
| h1 (both sessions) | `Upsedasse!` |
| error_upsedasse | true / true |
| plan gate | false |
| CVR hint | `# - url: /cvr/dk/companies/#` |
| Productable list/create chrome | none observed |

Scratch dual summary (non-sensitive): parent node
`tmp/discovery122/summary_dual_saft.json` under `.dual.annual_reports`.

### research191 EXECUTE reconfirm (2026-08-02)

| Field | Result |
| --- | --- |
| Login dual | READY / READY |
| Path class dual | `/:org_slug/annual_reports` |
| h1 dual | `Upsedasse!` / `Upsedasse!` |
| productable_shell | false |
| judgment | `A1_UPSEDASSE_STAY_RED` (historical) |
| API token | false |
| Writes | none |

Scratch: `tmp/research191_annual_dual.json` (owner-only node tmp).

## Related

- [[offline_write_probe_rules]]
- [[ui_exports_open_shell]]
