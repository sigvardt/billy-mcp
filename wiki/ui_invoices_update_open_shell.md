---
name: ui_invoices_update_open_shell
title: UI invoices update form open
desc: Read-only headless ui_invoices_update_open contract for Billy invoice draft edit form open only (research174).
tags: [billy, ui, invoices, headless, update]
sources:
  - docs/superpowers/specs/2026-07-28-billy-mcp-complete-design.md
  - https://www.billy.dk/api/
created: 2026-08-02T02:10:00Z
updated: 2026-08-02T02:10:00Z
---

# UI invoices update form open

## Contract

Tool `ui_invoices_update_open` opens an authenticated Billy **invoice draft
edit form** surface reached from the invoices list on `mit.billy.dk`.

Success path class is `/:org_slug/invoices/:id/edit` (same host path as get;
distinct assertion family).

Success fields (non-PII only):

- `path_class`: `/:org_slug/invoices/:id/edit`
- `shell_kind`: `invoices_update`
- `form_open`: edit form open with update freeze
- `gem_kladde_or_save_chrome_present`: Gem som kladde / Godkend save chrome
- `date_or_payment_terms_chrome_present`: Dato / Betalingsfrist / Fakturanr family
- `contact_or_customer_chrome_present`: Kunde/contact chrome
- `inputs_present`: at least three visible form inputs
- `shell_markers_present`: shared shell markers when visible

Input is empty. Maps `api.invoices.update` only (`form_open_only`). Never Gem /
Gem som kladde / Godkend og send / Send / Slet / Mere→Slet.

Distinct from `ui_invoices_get_open` (detail_open_only: entry date + contact +
line without requiring Gem som kladde freeze).

## Browser egress

Reuses committed path_allow on `api.billysbilling.com` for GET/POST/DELETE
`/v2/invoices` plus products/contacts seed helpers. No egress expansion in this
product. No live API token.

## Live seed

Harness creates disposable contact + product + invoice via SPA `X-Access-Token`,
never `BILLY_API_TOKEN`. Cleanup deletes invoice → product → contact and
verifies markers absent on a fresh list view.

## Evidence

- research174 dual update_form_ready on edit path
- Live: `tests/live/test_ui_invoices_update_open.py`
- Vision record: owner-only frames purged; durable non-sensitive review under node tmp vision-records
