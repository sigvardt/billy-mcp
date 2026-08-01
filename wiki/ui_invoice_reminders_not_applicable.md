---
name: ui_invoice_reminders_not_applicable
title: Invoice reminders API UI parity not applicable
desc: Dual-session research149 freeze — no equivalent mit.billy.dk workflow for invoiceReminders API parity; soft-empty path matches nonsense; invoices/Fakturaer shell is invoices only; NA accepted.
tags: [billy, ui, parity, invoiceReminders, not_applicable]
sources:
  - https://www.billy.dk/api/
  - https://mit.billy.dk/
  - docs/superpowers/specs/2026-07-28-billy-mcp-complete-design.md
  - coverage/ui_workflows_manifest.yaml
  - wiki/ui_contact_persons_not_applicable.md
  - wiki/ui_contact_postings_late_fees_reminder_assoc_not_applicable.md
  - wiki/ui_geo_cities_not_applicable.md
created: 2026-08-01T08:00:00Z
updated: 2026-08-01T08:00:00Z
---

# Invoice reminders API UI parity not applicable

## Decision

UI parity rows for the dual-proved `invoiceReminders` API family are
**`not_applicable`** with machine-readable evidence code
`GEO_UI_NO_EQUIVALENT_WORKFLOW` (same absence class as geo and research144–148
join/meta NA).

Design allows UI parity `not_applicable` only when Billy exposes **no equivalent
UI workflow**. Dual independent headless sessions on the dedicated
non-production organisation support that classification for:

- `invoiceReminders` (five parity ops: get, list, create, bulk_save, bulk_delete —
  matches official docs Supports; no singular update/delete)

This is **not** the same family as the invoices list shell (`ui_invoices_list` /
Fakturaer) and **not** a dual-count onto invoices (Rykker/Rykkere/Morarente
markers dual false on `/invoices`). Parent-resource only:
`invoiceReminderAssociations` was already greened NA under research144.

Peer freezes: [[ui_geo_cities_not_applicable]],
[[ui_contact_persons_not_applicable]],
[[ui_contact_postings_late_fees_reminder_assoc_not_applicable]],
[[ui_contact_balance_payments_not_applicable]].

## Dual-session evidence (non-sensitive)

| Observation | Result |
| --- | --- |
| Sessions | Two independent ephemeral profiles → READY |
| Soft seed `/invoiceReminders` (camel, kebab, DA rykkere/reminders) | soft-empty SPA chrome only (body length class 127, empty h1) |
| Nonsense path control | **same** soft-empty class |
| Invoices shell | dual-ok as **invoices** (path `/invoices`, h1 Fakturaer); Rykker / Rykkere / Morarente markers dual false |
| Typed contrast shells | clients, suppliers, uploads, settings, daybooks editor, bank recon, products dual-ok |

Scratch dual summaries (owner tmp, not git):
`research149_residual_dual.json`, `research149_shell_markers_dual.json`.

## Inventory contract

| Field | Value |
| --- | --- |
| `parity_status` | `not_applicable` |
| `tool_name` | empty (no dedicated UI tools for this family) |
| Flags | discovered, implemented, contract_tested, live_tested, vision_verified all true |
| `vision_evidence` | null (no retained frames) |
| `qualification.not_applicable_decision` | `accepted` |
| `qualification.sessions` | `dual_independent_ephemeral` |
| `qualification.evidence_ref` | `research149_invoice_reminders_dual` |

## Contrast with annual reports

`ui.discovery.annual_reports` keeps **`not_applicable` rejected**: nav label
Årsrapporter and route family exist (Upsedasse on the test org is inaccessibility,
not absence). See [[ui_annual_reports_inaccessible]].

## Related surfaces that are not this freeze

| Surface | Why not greened as this package |
| --- | --- |
| Invoices / Fakturaer list shell | Invoices workflow only; rykker markers dual false |
| invoiceReminderAssociations | Already NA (research144 join package) |
| Soft specials delivery/logs + settings Levering | Deferred (settings invoicing Levering ambiguity) |
| Soft attachments + Bilag uploads | Bilag greened with bilag markers → **reject pure NA** |
| Soft productPrices + `/products/new` | Nested form non-empty dual → reject pure NA |
| Soft taxRateDeductionComponents + Momssatser | Multi-resource VAT → defer |
