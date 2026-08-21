---
name: ui_invoice_lines_not_applicable
desc: UI parity not_applicable for invoiceLines get/list/create/update/delete (research179).
tags: [billy, ui, invoiceLines, not_applicable, research179]
sources:
  - https://www.billy.dk/api/
  - docs/superpowers/specs/2026-07-28-billy-mcp-complete-design.md
  - tmp/research179_focus_dual.json
  - coverage/ui_workflows_manifest.yaml
created: 2026-08-02T08:40:00Z
updated: 2026-08-02T08:40:00Z
---

# ui_invoice_lines_not_applicable

Official docs support full invoiceLines CRUD (+ bulk). In the test organisation UI, **dedicated** invoice line surfaces are absent dual (research179):

| Soft route | Dual result |
| --- | --- |
| `/invoiceLines`, `/invoice-lines` | soft SPA chrome only |
| `/invoices/:id/lines` | empty / not a line inventory |
| Invoice edit `/:org_slug/invoices/:id/edit` | line fields **embedded** (inputs_n 9 dual) |

## Freeze (exact ops)

- `api.invoiceLines.get`
- `api.invoiceLines.list`
- `api.invoiceLines.create`
- `api.invoiceLines.update`
- `api.invoiceLines.delete`

## Rules

- Do **not** dual-count line ops onto `ui_invoices_update_open` (parent maps `invoices.update` only)
- Do **not** NA `invoiceLines.bulk_*` (external-contract bulk freeze)
- Design §10.2 NA only when no equivalent dedicated UI workflow exists — accepted for dedicated line tools
