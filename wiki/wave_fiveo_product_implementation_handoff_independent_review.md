---
name: wave_fiveo_product_implementation_handoff_independent_review
title: Wave-5o invoice-reminder product-implementation handoff independent review
desc: Independent Grok ACCEPT as research for the Wave-5o invoiceReminders create-only product-implementation handoff after freeze ACCEPT; product tools and greening remain separate.
tags: [billy, api, invoice-reminders, writes, review, research]
sources:
  - https://www.billy.dk/api/
  - https://api.billysbilling.com/v2
  - .fractal/main.billy_complete/tmp/grok-research.md
  - .fractal/main.billy_complete/tmp/grok-review.md
  - wiki/wave_fiveo_ticketed_writes_contract.md
  - wiki/wave_fiveo_freeze_independent_review.md
  - wiki/wave_fiveo_product_ready_research_independent_review.md
  - wiki/offline_write_probe_rules.md
  - coverage/api_v2_manifest.yaml
  - coverage/status.json
  - docs/superpowers/specs/2026-07-28-billy-mcp-complete-design.md
created: 2026-07-30T11:08:00Z
updated: 2026-07-30T11:08:00Z
---

# Wave-5o invoice-reminder product-implementation handoff independent review

## Verdict

**ACCEPT as research** for the Wave-5o offline product-implementation handoff covering singular `invoiceReminders` create only (exactly two ticketed tools).

This is not product ACCEPT, live ACCEPT, UI ACCEPT, vision ACCEPT, bulk resolution, or overall completeness.

## Scope accepted

- Official plain API contract for `/v2/invoiceReminders` permits create among singular writes; Supports omits update and singular delete.
- Unauthenticated probes against `https://api.billysbilling.com/v2` with a JSON object body: POST returns 401 `AUTHENTICATION_REQUIRED`; PUT, singular DELETE, and bulk DELETE with `ids[]` return 405 `METHOD_NOT_ALLOWED`.
- Wave-5o freeze page on root and freeze independent review **ACCEPT** remain valid (freeze MD5 `6fec5754cc76c4a07b344021cbc3c36b`).
- Research66 handoff correctly opens product for only `api_invoice_reminders_create_preview` and `api_invoice_reminders_create_execute` under the accepted freeze.
- Inner `invoiceReminder` map stays opaque. Cleanup greening text (later product only) must not claim singular DELETE cleanup.
- Inventory create row remains red. Bulk rows stay empty-tool red. No product module is present on root. Coverage honesty remains 174 implemented and contract-tested, zero live, zero vision, `complete: false`.
- Delivery plan 110.10 correctly scopes a Codex Power product leaf and keeps greening limited to one row after real tests.

## Exact product surface accepted as research handoff

| Inventory id | Preview | Execute | Method and client path | Singular request root | Required success root |
| --- | --- | --- | --- | --- | --- |
| `api.invoiceReminders.create` | `api_invoice_reminders_create_preview` | `api_invoice_reminders_create_execute` | `POST /invoiceReminders` | `invoiceReminder` | `invoiceReminders` |

## Explicit non-acceptances

- Wave-5o product tools or coverage greening
- `invoiceReminderAssociations` create/update offline (POST/PUT 405)
- Bulk 92 resolution, live CUD, UI, vision, completeness
- Any active product child’s unmerged or unreviewed diff

## Evidence

Independent review body: `.fractal/main.billy_complete/tmp/grok-review.md`  
Research package: `.fractal/main.billy_complete/tmp/grok-research.md` (research66)  
Probe scratch: `.fractal/main.billy_complete/tmp/write-probes-review66.json`  
Docs: ETag `wcw4x9hqvu3603`, MD5 `8b94b0135c91fd15fe54ea33e088a4be`, body 147934
