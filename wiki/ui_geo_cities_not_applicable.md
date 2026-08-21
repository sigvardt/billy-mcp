---
name: ui_geo_cities_not_applicable
title: Geo and reference API UI parity not applicable
desc: Dual-session research138 freeze — no equivalent mit.billy.dk workflow for cities/countries/countryGroups/states/zipcodes API parity; soft-empty paths match nonsense; NA accepted. Currencies/locales: see ui_currencies_locales_not_applicable (research139).
tags: [billy, ui, parity, geo, cities, not_applicable]
sources:
  - https://www.billy.dk/api/
  - https://mit.billy.dk/
  - docs/superpowers/specs/2026-07-28-billy-mcp-complete-design.md
  - coverage/ui_workflows_manifest.yaml
created: 2026-08-01T02:15:00Z
updated: 2026-08-01T02:45:00Z
---

# Geo and reference API UI parity not applicable

## Decision

UI parity rows for dual-proved geo/reference API families are **`not_applicable`**
with machine-readable evidence code `GEO_UI_NO_EQUIVALENT_WORKFLOW`.

Design allows UI parity `not_applicable` only when Billy exposes **no equivalent
UI workflow**. Dual independent headless sessions on the dedicated
non-production organisation support that classification for:

- `cities` (all six parity ops)
- `countries`
- `countryGroups`
- `states`
- `zipcodes`

`currencies` and `locales` were deferred here (nav-only) and are greened NA under
research139 path contrast in [[ui_currencies_locales_not_applicable]].

## Dual-session evidence (non-sensitive)

| Observation | Result |
| --- | --- |
| Sessions | Two independent ephemeral profiles → READY |
| Geo nav labels / href path classes | empty both sessions |
| Candidate path classes (`/cities`, `/countries`, `/zipcodes`, …) | soft-empty SPA chrome only (body length class 127, h1 count 0) |
| Nonsense path class control | **same** soft-empty class |
| Known list shells (`/invoices`, `/products`, `/transactions`) | real shells with headings (Fakturaer, Produkter, Posteringer) |

Scratch dual summaries (owner tmp, not git): `research138_geo_ui_dual.json`,
`research138_geo_ui_contrast.json`.

## Inventory contract

| Field | Value |
| --- | --- |
| `parity_status` | `not_applicable` |
| `tool_name` | empty (no `ui_cities_*` or peer geo UI tools) |
| Flags | discovered, implemented, contract_tested, live_tested, vision_verified all true |
| `vision_evidence` | null (no retained frames) |
| `qualification.not_applicable_decision` | `accepted` |
| `qualification.sessions` | `dual_independent_ephemeral` |

## Contrast with annual reports

`ui.discovery.annual_reports` keeps **`not_applicable` rejected**: nav label
Årsrapporter and route family exist (Upsedasse on the test org is inaccessibility,
not absence). See [[ui_annual_reports_inaccessible]].

## Non-claims

- Does not green API bulk rows or residual 405 geo writes.
- Does not change API `live_tested` (stays false, `out_of_scope_by_user`).
- Does not claim a cities list shell from soft URL landing.
- Does not set `coverage/status.json` complete true.
