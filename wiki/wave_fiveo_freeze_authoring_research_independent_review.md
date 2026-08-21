---
name: wave_fiveo_freeze_authoring_research_independent_review
title: Wave-5o invoice-reminder freeze authoring research independent review
desc: Independent Grok ACCEPT as research for the Wave-5o invoiceReminders create-only freeze authoring package after Wave-5n product ACCEPT; freeze page and product remain ungated until separate freeze review.
tags: [billy, api, invoice-reminders, writes, review, research]
sources:
  - https://www.billy.dk/api/
  - https://api.billysbilling.com/v2
  - .fractal/main.billy_complete/tmp/grok-research.md
  - .fractal/main.billy_complete/tmp/grok-review.md
  - wiki/offline_write_probe_rules.md
  - wiki/wave_fiven_product_independent_review.md
  - wiki/wave_fiveo_freeze_ready_research_independent_review.md
  - coverage/api_v2_manifest.yaml
  - coverage/status.json
created: 2026-07-30T10:22:00Z
updated: 2026-07-30T10:22:00Z
---

# Wave-5o invoice-reminder freeze authoring research independent review

## Verdict

**ACCEPT as research** for the Wave-5o offline freeze authoring package covering singular `invoiceReminders` **create only** (two future ticketed tools).

This page is not Wave-5o freeze acceptance, not Wave-5o product acceptance, and not project completeness.

## What was verified

- Official API docs at https://www.billy.dk/api/ (ETag `wcw4x9hqvu3603`, MD5 `8b94b0135c91fd15fe54ea33e088a4be`, body 147934) match research64 HTML bytes and the `/v2/invoiceReminders` Supports + property table.
- Unauthenticated probes on `https://api.billysbilling.com/v2` with JSON object bodies: `POST /invoiceReminders` → 401 `AUTHENTICATION_REQUIRED`; PUT and singular DELETE → 405; bulk DELETE with `ids[]` → 405.
- Wave-5n product independent review **ACCEPT** offline is present on root (`wiki/wave_fiven_product_independent_review.md`), so freeze-page authoring is unblocked.
- Inventory reserves `api_invoice_reminders_create_preview` for `api.invoiceReminders.create` and keeps it red. Bulk rows stay empty-tool red. No update or singular-delete inventory rows exist for reminders (correct).
- Root coverage honesty: 174 implemented + contract_tested, 0 live, 0 vision, `complete: false`. No research-induced greening. UI vision greens remain 0.
- Research forbids product implementation, greening, bulk tools, update/delete tools, webhooks, live/UI/vision claims from the research pass.

## Exact freeze surface accepted as research

| Inventory id | Preview | Execute | Method and client path | Singular request root | Required success root |
| --- | --- | --- | --- | --- | --- |
| `api.invoiceReminders.create` | `api_invoice_reminders_create_preview` | `api_invoice_reminders_create_execute` | `POST /invoiceReminders` | `invoiceReminder` | `invoiceReminders` |

Inner `invoiceReminder` map stays opaque. Cleanup greening text (later product only) must not claim singular DELETE cleanup.

## Explicit non-acceptances

- Wave-5o freeze wiki page (still absent on root at review time)
- Wave-5o product tools or coverage greening
- `invoiceReminderAssociations` create/update offline (POST/PUT 405)
- Bulk 92 resolution, live CUD, UI, vision, completeness

## Evidence

Independent review body: `.fractal/main.billy_complete/tmp/grok-review.md`  
Research package: `.fractal/main.billy_complete/tmp/grok-research.md`  
Probe scratch: `.fractal/main.billy_complete/tmp/write-probes-review64.json`
