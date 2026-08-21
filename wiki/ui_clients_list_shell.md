---
name: ui_clients_list_shell
title: UI clients list shell open
desc: Read-only headless ui_clients_list contract for Billy clients list shell open only.
tags: [billy, ui, clients, contacts, headless]
sources:
  - docs/superpowers/specs/2026-07-28-billy-mcp-complete-design.md
  - https://www.billy.dk/api/
created: 2026-07-31T10:35:00Z
updated: 2026-07-31T10:35:00Z
---

# UI clients list shell open

## Contract

Tool `ui_clients_list` opens the authenticated Billy clients list shell on
`mit.billy.dk` under path class `/:org_slug/clients` or
`/:org_slug/clients/empty`.

Success fields (non-PII only):

- `path_class`: `/:org_slug/clients` or `/:org_slug/clients/empty` (query params allowed)
- `heading`: `Kunder` or `Kontakter`
- `create_action_visible`: CTA `Opret kontakt` is present (never clicked)
- `shell_markers_present`: shared shell markers when visible

Input is empty. Callers must reach READY via `auth_login_start` /
`auth_login_wait` first. Organisation slug comes only from the session URL or
the outside-git UI identity file.

## Explicit non-claims

- No contact create/edit/delete
- No API list filter/sort/pagination UI
- No live API read-back
- Bank-accounts and daybooks are separate discovery tracks

## Qualification notes

Dual independent headless sessions prove DOM classification. Vision review
covers list-surface frames only; durable record is non-sensitive with
`purge_verified` after frame purge. Inventory rows for discovery
(`ui.discovery.customers`) and shell-only parity (`ui.parity.contacts.list`)
must not embed full API filter schemas while greened.

Maps offline `api.contacts.list` for list-open parity only. API `live_tested`
remains false under user-scoped qualification.

- [[ui_clients_get_open_shell]]
