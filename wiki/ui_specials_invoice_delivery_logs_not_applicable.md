---
name: ui_specials_invoice_delivery_logs_not_applicable
title: Specials invoice delivery and logs UI parity not applicable
desc: Dual-session research150 freeze — no equivalent mit.billy.dk workflow for special invoice_delivery and invoice_logs API parity; soft-empty path matches nonsense; settings Levering is email-only; NA accepted for those two specials only.
tags: [billy, ui, parity, specials, invoice_delivery, invoice_logs, not_applicable]
sources:
  - https://www.billy.dk/api/
  - https://mit.billy.dk/
  - docs/superpowers/specs/2026-07-28-billy-mcp-complete-design.md
  - coverage/ui_workflows_manifest.yaml
  - wiki/ui_invoice_reminders_not_applicable.md
  - wiki/ui_contact_persons_not_applicable.md
  - wiki/ui_geo_cities_not_applicable.md
created: 2026-08-01T08:35:00Z
updated: 2026-08-01T08:35:00Z
---

# Specials invoice delivery and logs UI parity not applicable

## Decision

UI parity rows for two dual-proved specials are **`not_applicable`** with
machine-readable evidence code `GEO_UI_NO_EQUIVALENT_WORKFLOW` (same absence
class as geo and research144–149 packages).

Design allows UI parity `not_applicable` only when Billy exposes **no equivalent
UI workflow**. Dual independent headless sessions on the dedicated
non-production organisation support that classification for:

- `api.special.invoice_delivery` (`POST /v2/invoiceDeliveries` e-invoice start)
- `api.special.invoice_logs` (`GET /v2/invoiceLogs` async delivery/email log poll)

**Not** greened by this freeze (stay red or other product paths):

- `api.special.invoice_email` — settings Faktura panel shows
  **"Levering af faktura pr. e-mail"** (email delivery settings related)
- `api.special.files_upload` — Bilag uploads shell greened
- `api.special.user_get` / `api.special.user_organizations` — org switcher /
  profil ambiguity

Exact full API ids only (never bare `api.special.`).

Peer freezes: [[ui_invoice_reminders_not_applicable]],
[[ui_contact_persons_not_applicable]],
[[ui_geo_cities_not_applicable]],
[[ui_product_prices_not_applicable]].

## Dual-session evidence (non-sensitive)

| Observation | Result |
| --- | --- |
| Sessions | Two independent ephemeral profiles → READY |
| Soft seed `/invoiceDeliveries` and `/invoiceLogs` (camel/kebab) | soft-empty SPA chrome only (body length class 127, empty h1) |
| Nonsense path control | **same** soft-empty class |
| Invoices shell | dual-ok as **Fakturaer**; e-invoice / log markers dual false |
| Settings invoicing panel | dual body length class 1494; string **Levering af faktura pr. e-mail**; e_invoice/GLN markers dual false |
| Typed contrast shells | uploads Bilag, transactions Posteringer, clients, products, daybooks editor, bank recon dual-ok |

Scratch dual summaries (owner tmp, not git):
`research150_residual_dual.json`, `research150_levering_context_dual.json`.

## Inventory contract

| Field | Value |
| --- | --- |
| `parity_status` | `not_applicable` |
| `tool_name` | empty (no dedicated UI tools for these specials) |
| Flags | discovered, implemented, contract_tested, live_tested, vision_verified all true |
| `vision_evidence` | null (no retained frames) |
| `qualification.not_applicable_decision` | `accepted` |
| `qualification.sessions` | `dual_independent_ephemeral` |
| `qualification.evidence_ref` | `research150_specials_invoice_delivery_logs_dual` |

## Contrast with annual reports

`ui.discovery.annual_reports` keeps **`not_applicable` rejected**: nav label
Årsrapporter and route family exist (Upsedasse on the test org is inaccessibility,
not absence). See [[ui_annual_reports_inaccessible]].

## Related surfaces that are not this freeze

| Surface | Why not greened as this package |
| --- | --- |
| Invoices / Fakturaer list shell | Invoices workflow only; no e-invoice/log markers |
| Settings Faktura / Levering email text | Email delivery **settings** for invoice_email special; not e-invoice or logs UI |
| Bilag uploads shell | Files/attachments / files_upload — reject pure NA |
| invoiceReminders | Already NA (research149) |
