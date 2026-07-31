---
name: ui_transactions_list_shell
desc: Read-only Billy transactions (Posteringer) list shell contract (research118 freeze).
tags: [billy, ui, transactions, discovery]
sources:
  - docs/superpowers/specs/2026-07-28-billy-mcp-complete-design.md
  - https://www.billy.dk/api/
created: 2026-07-31T15:45:00Z
updated: 2026-07-31T15:45:00Z
---

# ui_transactions_list_shell

## Contract

| Field | Value |
| --- | --- |
| Tool | `ui_transactions_list` |
| Coverage row | `ui.discovery.transactions` |
| Path class | `/:org_slug/transactions` (query params allowed, e.g. period) |
| Heading | `Posteringer` |
| Create CTA | `Ny postering` present (observe only; never click) |
| Input | empty (`extra=forbid`) |
| Success fields | `path_class`, `heading`, `create_action_visible`, `shell_markers_present` |
| parity_status | `shell_open_only` |

## Non-claims

- Nested `/:org_slug/transactions/:segment` (new, empty, list, …) is a create
  shell with h1 `Postering:` and is **not** list success for this tool.
- Soft aliases (`posteringer`, `transaction`, `ledger`, …) are empty shells,
  not this tool's success path.
- Official `/v2/transactions` get/list already exist offline. Do **not** invent
  create/update/delete/bulk API tools for this UI shell.
- Never click `Ny postering`, Bogfør, void, delete, or submit create forms.
- Does not green `ui.discovery.daybooks` or `ui.parity.transactions.*`.
- API `live_tested` remains false with `out_of_scope_by_user`.

## Qualification

- Offline unit/model/server registration tests.
- Live dual independent browser sessions (no `BILLY_API_TOKEN`).
- Vision review record under tmp with `purge_verified: true` after frame purge.
