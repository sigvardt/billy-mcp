---
name: ui_contact_balance_payments_not_applicable
title: Contact balance payments API UI parity not applicable
desc: Dual-session research147 freeze — no equivalent mit.billy.dk workflow for contactBalancePayments API parity; soft-empty path matches nonsense; balance shells are contrast only; NA accepted.
tags: [billy, ui, parity, contactBalancePayments, not_applicable]
sources:
  - https://www.billy.dk/api/
  - https://mit.billy.dk/
  - docs/superpowers/specs/2026-07-28-billy-mcp-complete-design.md
  - coverage/ui_workflows_manifest.yaml
  - wiki/ui_contact_postings_late_fees_reminder_assoc_not_applicable.md
  - wiki/ui_geo_cities_not_applicable.md
created: 2026-08-01T07:00:00Z
updated: 2026-08-01T07:00:00Z
---

# Contact balance payments API UI parity not applicable

## Decision

UI parity rows for the dual-proved `contactBalancePayments` API family are
**`not_applicable`** with machine-readable evidence code
`GEO_UI_NO_EQUIVALENT_WORKFLOW` (same absence class as geo and research144
join/meta NA).

Design allows UI parity `not_applicable` only when Billy exposes **no equivalent
UI workflow**. Dual independent headless sessions on the dedicated
non-production organisation support that classification for:

- `contactBalancePayments` (six parity ops: get, list, create, update,
  bulk_save, bulk_delete)

This is **not** the same family as `contactBalancePostings` (already NA under
[[ui_contact_postings_late_fees_reminder_assoc_not_applicable]]) and **not**
`bankPayments` (stays red; bank shells greened).

Peer freezes: [[ui_geo_cities_not_applicable]],
[[ui_account_groups_not_applicable]],
[[ui_contact_postings_late_fees_reminder_assoc_not_applicable]].

## Dual-session evidence (non-sensitive)

| Observation | Result |
| --- | --- |
| Sessions | Two independent ephemeral profiles → READY |
| Soft seed `/contactBalancePayments` | soft-empty SPA chrome only (body length class 127, empty h1) |
| Nonsense path control | **same** soft-empty class |
| Debtor/creditor balance shells | dual-ok as **balances** (h1 Tilgodehavender / Skyldige udgifter); Betaling marker dual false |
| Typed contrast shells | invoices, balances, settings, daybooks editor, bank recon, products, uploads dual-ok |

Scratch dual summaries (owner tmp, not git):
`research147_soft_routes_dual.json`, `research147_residual_parity_dual.json`.

## Inventory contract

| Field | Value |
| --- | --- |
| `parity_status` | `not_applicable` |
| `tool_name` | empty (no dedicated UI tools for this family) |
| Flags | discovered, implemented, contract_tested, live_tested, vision_verified all true |
| `vision_evidence` | null (no retained frames) |
| `qualification.not_applicable_decision` | `accepted` |
| `qualification.sessions` | `dual_independent_ephemeral` |
| `qualification.evidence_ref` | `research147_contact_balance_payments_dual` |

## Contrast with annual reports

`ui.discovery.annual_reports` keeps **`not_applicable` rejected**: nav label
Årsrapporter and route family exist (Upsedasse on the test org is inaccessibility,
not absence). See [[ui_annual_reports_inaccessible]].

## Related surfaces that are not this freeze

| Surface | Why not greened as this package |
| --- | --- |
| Debtor/creditor balance list shells | Balance workflows only; no dual-proved contactBalancePayments surface |
| Soft `bankPayments` + bank recon/accounts | Related bank shells greened → **reject pure NA** for bankPayments |
| Soft `productPrices` + `/products/new` | Product create form is a real surface → **reject NA** |
| bankLineMatches / bankLineSubjectAssociations | Bank recon shell greened → **reject pure NA** |
| daybooks / daybook* soft seeds | Daybooks editor greened; list dual-count deferred (editor ≠ list) |
| salesTax* / taxRates soft seeds | Momssatser multi-resource greened → **reject pure NA** |
| Nested invoiceLines / billLines / contactPersons | Nested under parent list shells → not pure absence |

## Non-claims

- No invent `ui_contact_balance_payments_*` tools.
- No greening of API `live_tested` (remains false with `out_of_scope_by_user`).
- No greening of bulk API tools (92 external-contract rows stay red).
- No re-scope of debtor/creditor tools as payment workflows.
- Offline API contactBalancePayments clear ops stay offline-green where already
  producted; bulk rows stay external-contract red on the API lane.
