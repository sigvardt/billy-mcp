---
name: ui_recurring_invoices_list_shell
title: UI recurring invoices list shell open
desc: Read-only headless ui_recurring_invoices_list contract for Billy Abonnementer list shell open only.
tags: [billy, ui, recurring_invoices, headless]
sources:
  - docs/superpowers/specs/2026-07-28-billy-mcp-complete-design.md
  - https://www.billy.dk/api/
created: 2026-07-31T11:30:00Z
updated: 2026-07-31T11:30:00Z
---

# UI recurring invoices list shell open

## Contract

Tool `ui_recurring_invoices_list` opens the authenticated Billy recurring
invoices list shell on `mit.billy.dk` under path class
`/:org_slug/recurring_invoices`. An optional empty-state suffix
`/:org_slug/recurring_invoices/empty` is accepted. Success always reports the
canonical class `/:org_slug/recurring_invoices`.

Success fields (non-PII only):

- `path_class`: `/:org_slug/recurring_invoices` (query params allowed on the real URL)
- `heading`: `Abonnementer`
- `create_action_visible`: CTA `Opret abonnement` is present (never clicked)
- `shell_markers_present`: shared shell markers when visible

Input is empty. Callers must reach READY via `auth_login_start` /
`auth_login_wait` first. Organisation slug comes only from the session URL or
the outside-git UI identity file.

## Explicit non-claims

- No recurring invoices API tool (`api_recurring_*` / `api_recurring_invoices_*`
  must not exist)
- No create, edit, delete, pause, resume, schedule, or invoice-generation actions
- No greening of invoice `recurringInvoiceId` filter UI or further
  `ui.parity.invoices.*`
- No greening of other discovery shells from this tool
- No live API read-back

## Qualification notes

Dual independent headless sessions prove DOM classification. Vision review
covers list-surface frames only; durable record is non-sensitive with
`purge_verified` after frame purge. Inventory row
`ui.discovery.recurring_invoices` must not embed API filter schemas while greened.

Official docs have no `recurringInvoices` resource. The only related documented
field is invoices list filter `recurringInvoiceId` (offline API only). API
`live_tested` remains false under user-scoped qualification.
