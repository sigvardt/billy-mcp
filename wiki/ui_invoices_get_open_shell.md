---
name: ui_invoices_get_open_shell
title: UI invoices detail get open
desc: Read-only headless ui_invoices_get_open contract for Billy invoice draft detail/edit get/open only (research169).
tags: [billy, ui, invoices, headless, get]
sources:
  - docs/superpowers/specs/2026-07-28-billy-mcp-complete-design.md
  - https://www.billy.dk/api/
created: 2026-08-01T22:30:00Z
updated: 2026-08-01T22:30:00Z
---

# UI invoices detail get open

## Contract

Tool `ui_invoices_get_open` opens an authenticated Billy **invoice draft
detail/edit** surface reached from the invoices list on `mit.billy.dk`.

Success path class is `/:org_slug/invoices/:id/edit` (not list shell, not
`/invoices/new`).

Success fields (non-PII only):

- `path_class`: `/:org_slug/invoices/:id/edit`
- `shell_kind`: `invoices_get`
- `detail_open`: edit surface open
- `entry_date_control_present`: entry date control present
- `contact_control_present`: customer/contact control present
- `line_chrome_present`: line/description chrome present
- `shell_markers_present`: shared shell markers when visible

Input is empty. Maps `api.invoices.get` only. Never Gem / Send / Slet / Godkend.

## Browser egress

`coverage/browser_egress.yaml` path-allows scoped invoices methods:

- `GET` `/v2/invoices` (list/data plane; research168)
- `POST` `/v2/invoices` (disposable draft seed in live harness; research169)
- `DELETE` `/v2/invoices` (cleanup; research169)

Bills writes and invoice email paths remain denied.

## Live seed

Harness creates disposable contact + product + invoice (line requires
`productId`) via SPA `X-Access-Token`, never `BILLY_API_TOKEN`. Cleanup deletes
invoice → product → contact and verifies markers absent on a fresh list view.

## Related

- `ui_invoices_list` — list shell only
- `ui_invoices_create_open` — create form open only
- Residual: invoices update/delete, bills.get, products.get, special.invoice_email
