---
name: ui_quotes_list_shell
title: UI quotes list shell open
desc: Read-only headless ui_quotes_list contract for Billy quotes list shell open only.
tags: [billy, ui, quotes, headless]
sources:
  - docs/superpowers/specs/2026-07-28-billy-mcp-complete-design.md
  - https://www.billy.dk/api/
created: 2026-07-31T11:10:00Z
updated: 2026-07-31T11:10:00Z
---

# UI quotes list shell open

## Contract

Tool `ui_quotes_list` opens the authenticated Billy quotes list shell on
`mit.billy.dk` under path class `/:org_slug/quotes`. Empty organisations may
land on `/:org_slug/quotes/empty`; both path forms are accepted. Success always
reports the canonical class `/:org_slug/quotes`.

Success fields (non-PII only):

- `path_class`: `/:org_slug/quotes` (query params allowed on the real URL)
- `heading`: `Tilbud`
- `create_action_visible`: CTA `Opret tilbud` is present (never clicked)
- `shell_markers_present`: shared shell markers when visible

Input is empty. Callers must reach READY via `auth_login_start` /
`auth_login_wait` first. Organisation slug comes only from the session URL or
the outside-git UI identity file.

## Explicit non-claims

- No quotes API tool (`api_quotes_*` must not exist)
- No create, edit, delete, convert-to-invoice, email, or PDF actions
- No greening of invoice `quoteId` filter UI or further `ui.parity.invoices.*`
- No greening of `ui.discovery.recurring_invoices` from this shell
- No live API read-back

## Qualification notes

Dual independent headless sessions prove DOM classification. Vision review
covers list-surface frames only; durable record is non-sensitive with
`purge_verified` after frame purge. Inventory row `ui.discovery.quotes` must
not embed API filter schemas while greened.

Official docs have no `quotes` resource. The only related documented field is
invoices list filter `quoteId` (offline API only). API `live_tested` remains
false under user-scoped qualification.
