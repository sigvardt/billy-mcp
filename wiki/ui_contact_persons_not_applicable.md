---
name: ui_contact_persons_not_applicable
title: Contact persons API UI parity not applicable
desc: Dual-session research148 freeze — no equivalent mit.billy.dk workflow for contactPersons API parity; soft-empty path matches nonsense; clients/Kunder shell is contacts only; NA accepted.
tags: [billy, ui, parity, contactPersons, not_applicable]
sources:
  - https://www.billy.dk/api/
  - https://mit.billy.dk/
  - docs/superpowers/specs/2026-07-28-billy-mcp-complete-design.md
  - coverage/ui_workflows_manifest.yaml
  - wiki/ui_contact_balance_payments_not_applicable.md
  - wiki/ui_contact_postings_late_fees_reminder_assoc_not_applicable.md
  - wiki/ui_geo_cities_not_applicable.md
created: 2026-08-01T07:30:00Z
updated: 2026-08-01T07:30:00Z
---

# Contact persons API UI parity not applicable

## Decision

UI parity rows for the dual-proved `contactPersons` API family are
**`not_applicable`** with machine-readable evidence code
`GEO_UI_NO_EQUIVALENT_WORKFLOW` (same absence class as geo and research144–147
join/meta NA).

Design allows UI parity `not_applicable` only when Billy exposes **no equivalent
UI workflow**. Dual independent headless sessions on the dedicated
non-production organisation support that classification for:

- `contactPersons` (seven parity ops: get, list, create, update, delete,
  bulk_save, bulk_delete)

This is **not** the same family as `contacts` list shell (`ui_clients_list` /
Kunder) and **not** a dual-count onto clients (Kontaktperson markers dual
false on `/clients`).

Peer freezes: [[ui_geo_cities_not_applicable]],
[[ui_account_groups_not_applicable]],
[[ui_contact_postings_late_fees_reminder_assoc_not_applicable]],
[[ui_contact_balance_payments_not_applicable]],
[[ui_invoice_reminders_not_applicable]].

## Dual-session evidence (non-sensitive)

| Observation | Result |
| --- | --- |
| Sessions | Two independent ephemeral profiles → READY |
| Soft seed `/contactPersons` (camel, kebab, DA) | soft-empty SPA chrome only (body length class 127, empty h1) |
| Nonsense path control | **same** soft-empty class |
| Clients shell | dual-ok as **contacts** (path `/clients`, h1 Kunder); Kontaktperson / person markers dual false |
| Typed contrast shells | invoices, suppliers, uploads, settings, daybooks editor, bank recon, products dual-ok |

Scratch dual summaries (owner tmp, not git):
`research148_residual_dual.json`, `research148_shell_markers_dual.json`.

## Inventory contract

| Field | Value |
| --- | --- |
| `parity_status` | `not_applicable` |
| `tool_name` | empty (no dedicated UI tools for this family) |
| Flags | discovered, implemented, contract_tested, live_tested, vision_verified all true |
| `vision_evidence` | null (no retained frames) |
| `qualification.not_applicable_decision` | `accepted` |
| `qualification.sessions` | `dual_independent_ephemeral` |
| `qualification.evidence_ref` | `research148_contact_persons_dual` |

## Contrast with annual reports

`ui.discovery.annual_reports` keeps **`not_applicable` rejected**: nav label
Årsrapporter and route family exist (Upsedasse on the test org is inaccessibility,
not absence). See [[ui_annual_reports_inaccessible]].

## Related surfaces that are not this freeze

| Surface | Why not greened as this package |
| --- | --- |
| Clients / Kunder list shell | Contacts workflow only; person markers dual false |
| Soft `invoiceReminders` + invoices list | Greened NA under research149 — see [[ui_invoice_reminders_not_applicable]] |
| Soft attachments + Bilag uploads | Bilag greened with bilag markers → **reject pure NA** |
| Soft specials delivery/logs/user_orgs | Settings Levering ambiguity → defer |
| taxRateDeductionComponents / taxRates | Momssatser multi-resource greened → defer |
| Soft `productPrices` + `/products/new` | Product create form is a real surface → **reject NA** |
| bankLine* / bankPayments | Bank shells greened → **reject pure NA** |

## Non-claims

- No invent `ui_contact_persons_*` tools.
- No dual-count of contactPersons onto `ui_clients_list`.
- No greening of API `live_tested` (remains false with `out_of_scope_by_user`).
- No greening of bulk API tools (92 external-contract rows stay red).
- No greening of invoiceReminders / attachments / specials this freeze.
- Offline API contactPersons clear ops stay offline-green where already producted.
