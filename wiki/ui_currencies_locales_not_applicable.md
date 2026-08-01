---
name: ui_currencies_locales_not_applicable
title: Currencies and locales API UI parity not applicable
desc: Dual-session research139 freeze — no equivalent mit.billy.dk workflow for currencies/locales API parity; soft-empty paths match nonsense; NA accepted.
tags: [billy, ui, parity, currencies, locales, not_applicable]
sources:
  - https://www.billy.dk/api/
  - https://mit.billy.dk/
  - docs/superpowers/specs/2026-07-28-billy-mcp-complete-design.md
  - coverage/ui_workflows_manifest.yaml
  - wiki/ui_geo_cities_not_applicable.md
created: 2026-08-01T02:45:00Z
updated: 2026-08-01T02:45:00Z
---

# Currencies and locales API UI parity not applicable

## Decision

UI parity rows for dual-proved `currencies` and `locales` API families are
**`not_applicable`** with machine-readable evidence code
`GEO_UI_NO_EQUIVALENT_WORKFLOW` (same absence class as geo reference NA).

Design allows UI parity `not_applicable` only when Billy exposes **no equivalent
UI workflow**. Dual independent headless sessions on the dedicated
non-production organisation support that classification for:

- `currencies` (all six parity ops: get, list, create, update, bulk_save, bulk_delete)
- `locales` (same six ops)

This freeze closes the research138 deferral (nav absence only) with full path
contrast. Peer geo NA remains in [[ui_geo_cities_not_applicable]].

## Dual-session evidence (non-sensitive)

| Observation | Result |
| --- | --- |
| Sessions | Two independent ephemeral profiles → READY |
| Currency/locale/valuta/sprog/language nav labels / hrefs | empty both sessions |
| Candidate path classes (`/currencies`, `/locales`, `/valutaer`, `/sprog`, `settings/currencies`, …) | soft-empty SPA chrome only (body length class 127, h1 count 0) |
| Nonsense path class control | **same** soft-empty class |
| Known shells (`/invoices`, `/products`, `/transactions`, `/vat-declarations`, `/settings`) | real shells with headings |

Scratch dual summaries (owner tmp, not git):
`research139_currencies_locales_dual.json`,
`research139_currencies_locales_contrast.json`.

## Inventory contract

| Field | Value |
| --- | --- |
| `parity_status` | `not_applicable` |
| `tool_name` | empty (no `ui_currencies_*` / `ui_locales_*` tools) |
| Flags | discovered, implemented, contract_tested, live_tested, vision_verified all true |
| `vision_evidence` | null (no retained frames) |
| `qualification.not_applicable_decision` | `accepted` |
| `qualification.sessions` | `dual_independent_ephemeral` |
| `qualification.evidence_ref` | `research139_currencies_locales_dual+contrast` |

## Contrast with annual reports

`ui.discovery.annual_reports` keeps **`not_applicable` rejected**: nav label
Årsrapporter and route family exist (Upsedasse on the test org is inaccessibility,
not absence). See [[ui_annual_reports_inaccessible]].

## Settings hub trap

`/:org_slug/settings` is a real hub (h1 Indstillinger). Nested
`settings/currencies` and `settings/locales` are soft-empty, not productable
panels. Do not invent settings currency tools from hub success alone.

## Non-claims

- Does not green API bulk rows or residual 405 currency/locale writes.
- Does not change API `live_tested` (stays false, `out_of_scope_by_user`).
- Does not claim a currencies/locales list shell from soft URL landing.
- Does not dual-count `salesTaxReturns.list` (residual).
- Does not set `coverage/status.json` complete true.
