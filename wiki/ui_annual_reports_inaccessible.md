---
name: ui_annual_reports_inaccessible
title: Annual reports route inaccessible on dedicated test organisation
desc: Dual-session Upsedasse freeze for mit.billy.dk annual_reports (research122 + research191 reconfirm); not_applicable rejected because nav exists; unlock requires non-Upsedasse shell.
tags: [billy, ui, discovery, annual_reports, inaccessible]
sources:
  - https://mit.billy.dk/
  - docs/superpowers/specs/2026-07-28-billy-mcp-complete-design.md
  - .fractal/main.billy_complete/tmp/discovery122/summary_dual_saft.json
  - .fractal/main.billy_complete/tmp/research191_annual_dual.json
created: 2026-08-01T01:45:00Z
updated: 2026-08-02T19:10:00Z
---

# Annual reports route inaccessible on dedicated test organisation

## Decision

Honest UI `not_applicable` is **rejected** for `ui.discovery.annual_reports`.

The Billy interface exposes nav label **Årsrapporter** and route family
`/:org_slug/annual_reports`. Design allows `not_applicable` only when evidence
shows Billy exposes **no equivalent UI workflow**. An error shell is not
absence of UI.

## Dual-session evidence (dedicated non-production org)

### research122 freeze

| Field | Result |
| --- | --- |
| Path class | `/:org_slug/annual_reports` |
| h1 (both sessions) | `Upsedasse!` |
| error_upsedasse | true / true |
| plan gate | false |
| CVR hint | `# - url: /cvr/dk/companies/#` |
| Recovery CTAs | Log ind igen / Gå til forsiden / Genindlæs side |
| Productable list/create chrome | none observed |

Scratch dual summary (non-sensitive): parent node
`tmp/discovery122/summary_dual_saft.json` under `.dual.annual_reports`.

### research191 EXECUTE reconfirm (2026-08-02)

| Field | Result |
| --- | --- |
| Login dual | READY / READY (independent ephemeral profiles) |
| Path class dual | `/:org_slug/annual_reports` / `/:org_slug/annual_reports` |
| h1 dual | `Upsedasse!` / `Upsedasse!` |
| error_upsedasse | true / true |
| productable_shell | false |
| judgment | `A1_UPSEDASSE_STAY_RED` |
| API token | false |
| Writes | none |
| Profiles | purged |

Scratch: `tmp/research191_annual_dual.json` (owner-only node tmp; not a product tool).

## Inventory

| Field | Value |
| --- | --- |
| Row | `ui.discovery.annual_reports` |
| Status | red (`discovered`/`implemented`/`live_tested`/`vision_verified` false) |
| `parity_status` | `discovery_required` (not `not_applicable`) |
| `blocker_code` | `ANNUAL_REPORTS_ORG_INACCESSIBLE` |
| `evidence_ref` | `research191_annual_dual` (prior `discovery122_summary_dual_saft.annual_reports`) |
| Tool | none (do not invent `api_annual_*` or `ui_annual_*` until unlock) |

## Unlock requirement

A non-production Billy organisation (or Billy platform fix) where
`mit.billy.dk/:org_slug/annual_reports` dual-session renders a **non-Upsedasse**
annual-reports shell, so a typed open/list workflow can be implemented with DOM
assertions, independent second-interface read-back, and vision review.

## Related

- [[offline_write_probe_rules]]
- [[ui_exports_open_shell]]
- [[ui_vat_declarations_list_shell]]
- [[residual_clear_method_closed_inventory_honesty]]

## research192 note (2026-08-02)

Docs/API residual and bulk walls reconfirmed offline (research192). No new annual dual this pass (same-day research191 A1 Upsedasse still binding). Annual row stays red; dual evidence_ref remains `research191_annual_dual`.

## research193 stop-churn (2026-08-02)

No annual dual re-probe this pass (parent STEER: report blockers; no wall-hygiene churn without a new shell).

| Field | Value |
| --- | --- |
| Dual evidence | still research191 + discovery122 (A1 Upsedasse) |
| `evidence_ref` | `research191_annual_dual` (**unchanged**) |
| Row | stays red; `parity_status=discovery_required`; `not_applicable` still rejected |
| Tools | none |

Unlock remains a non-Upsedasse `/:org_slug/annual_reports` shell on a dedicated non-production organisation (or Billy platform fix), then open/list dual + vision.
