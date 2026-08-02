---
name: ui_special_invoice_email_not_applicable
title: Special invoice email UI parity not applicable
desc: Dual-session research178 freeze — no durable mit.billy.dk invoice email compose form; soft email/send/delivery empty; Godkend og send rejected as non-compose; exact NA for api.special.invoice_email only.
tags: [billy, ui, parity, invoices, special, not_applicable]
sources:
  - https://www.billy.dk/api/
  - https://mit.billy.dk/
  - docs/superpowers/specs/2026-07-28-billy-mcp-complete-design.md
  - coverage/ui_workflows_manifest.yaml
  - wiki/ui_invoices_update_open_shell.md
created: 2026-08-02T07:45:00Z
updated: 2026-08-02T07:45:00Z
---

# Special invoice email UI parity not applicable

## Decision

UI parity for **`api.special.invoice_email`** is **`not_applicable`** with
evidence code `GEO_UI_NO_EQUIVALENT_WORKFLOW`.

Dual independent headless sessions found **no durable email compose form**. Soft
paths `/invoices/:id/email`, `/send`, and `/delivery` are empty (inputs 0, Send 0).
Invoice edit shows **Godkend og send**, which is irreversible approve-and-send
chrome and is **not** accepted as an email compose workflow.

**Not** greened by this freeze:

- Invoice list/create/get/update/delete UI tools (already producted separately)
- Offline API ticketed email/delivery tools (API lane; live API out of scope)
- `api.special.invoice_delivery` / `invoice_logs` (research150 NA)

Peer freezes: [[ui_accounts_get_create_update_delete_not_applicable]],
[[ui_specials_invoice_delivery_logs_not_applicable]].

## Dual-session evidence (non-sensitive)

| Observation | Result |
| --- | --- |
| Sessions | Two independent ephemeral profiles → READY |
| Soft `/email` `/send` `/delivery` | path dual; inputs_n 0; Send 0 dual |
| Invoice edit | Godkend og send 1 dual — rejected as non-compose |
| Compose form_ready | false dual |
| Env `BILLY_API_TOKEN` | unused |

Scratch dual summary (owner tmp, not git):
`research178_focus_dual.json`.

## Inventory contract

| Field | Value |
| --- | --- |
| `parity_status` | `not_applicable` |
| `tool_name` | empty |
| Flags | discovered, implemented, contract_tested, live_tested, vision_verified all true |
| `vision_evidence` | null |
| `qualification.evidence_ref` | `research178_special_invoice_email_dual` |
| Scope | exact `api.special.invoice_email` only |
