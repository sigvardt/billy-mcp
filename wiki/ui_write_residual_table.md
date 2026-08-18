---
name: ui_write_residual_table
desc: Residual honesty-16 UI write table. Invoice CUD waits on Kunde option inspect after a proved customer.
tags: [billy, ui, writes, residual, honesty]
sources:
  - radio:96908DC6
  - radio:D68E402A
  - radio:FD39FFE7
  - radio:113F1E05
  - radio:A337A622
  - radio:67CBACB6
  - radio:EC676F84
  - radio:802D71CF
  - wiki/ui_write_ticket_protocol.md
  - wiki/ui_contacts_writes.md
  - wiki/ui_bills_writes.md
  - wiki/ui_organizations_writes.md
  - wiki/ui_invoices_writes.md
  - wiki/ui_products_writes.md
  - wiki/ui_files_writes.md
  - wiki/ui_ledger_writes.md
created: 2026-08-18T14:30:00Z
updated: 2026-08-18T15:30:00Z
---

# ui_write_residual_table

Owner-scope UI write residual after `D68E402A` and `EC676F84`.
Shared ticket rules live in [[ui_write_ticket_protocol]].

The honesty-16 gate still keeps every row red
(`implemented=false`, `live_tested=false`, `vision_verified=false`).
The manifest has no other unimplemented write-like UI parity row.

Contacts, bills, and organizations are already live-proved through
FastMCP. Invoice draft CUD now has a proved tagged customer on the
independent clients list. Kunde still returns
`UI_CHANGED` (`Billy Kunde existing option is not visible`).
Owner inspect `802D71CF` is unanswered. Do not remake picker dumps.

`FD39FFE7` still makes invoice draft CUD and product create mandatory
and red. They are not finished as `UI_CHANGED`.

## Categories

- `already_live_proved_honesty_red`
- `owner_decision_67CBACB6`
- `kunde_option_missing_after_proved_customer`
- `interface_control_absent_UI_CHANGED`
- `high_impact_prohibited`

## Table

| ID | Coverage tool | Registered preview / execute | Mutation control | Cleanup / read-back | Category |
| --- | --- | --- | --- | --- | --- |
| `ui.parity.contacts.create` | `ui_clients_create_preview` | `ui_clients_create_{preview,execute}` | **Gem** `data-cy=save-button`. Live FastMCP | Fresh-session name read-back. **Ja, slet**. Absence 0. Vision `3d5b151dfd5342258f8734373597f8c1` accept, purged | `already_live_proved_honesty_red` |
| `ui.parity.contacts.update` | `ui_clients_update_preview` | `ui_clients_update_{preview,execute}` | Exact **Ret**, then **Gem** | `{tag}-U` is a different name. Same vision | `already_live_proved_honesty_red` |
| `ui.parity.contacts.delete` | `ui_clients_delete_preview` | `ui_clients_delete_{preview,execute}` | **Slet kontakt** link, **Ja, slet** | Fresh-session absence. Same vision | `already_live_proved_honesty_red` |
| `ui.parity.bills.create` | `ui_bills_create_preview` | `ui_bills_create_{preview,execute}` | Existing-option vendor bind. **Gem som kladde** | Fresh-session draft read-back. Vision `9920dd9476474b41aef70e6d66d24638` accept, purged | `already_live_proved_honesty_red` |
| `ui.parity.bills.update` | `ui_bills_update_preview` | `ui_bills_update_{preview,execute}` | Draft edit + draft save | Independent read-back. Same vision | `already_live_proved_honesty_red` |
| `ui.parity.bills.delete` | `ui_bills_delete_preview` | `ui_bills_delete_{preview,execute}` | Delete chrome + confirm | Reverse cleanup. Same vision | `already_live_proved_honesty_red` |
| `ui.parity.organizations.update` | `ui_organizations_update_preview` | `ui_organizations_update_{preview,execute}` | Company phone field + **Gem** | Tagged set then exact empty restore. Vision `0937a009bf7e496ca2ce15a8af313868` accept, purged | `already_live_proved_honesty_red` |
| `ui.parity.invoices.create` | `ui_invoices_create_open` | `ui_invoices_create_{preview,execute}` exist offline. Coverage still names `*_open` | Tagged FastMCP customer independently visible. **Vælg kunde** click plus type still finds no existing option (`802D71CF`) | Draft delete chrome exists. Create never persists | `kunde_option_missing_after_proved_customer` |
| `ui.parity.invoices.update` | `ui_invoices_update_open` | `ui_invoices_update_{preview,execute}` | Blocked on a tagged draft | Blocked on create | `kunde_option_missing_after_proved_customer` |
| `ui.parity.invoices.delete` | `ui_invoices_delete_open` | `ui_invoices_delete_{preview,execute}` | **Mere** then **Slet** on open chrome | Blocked on create | `kunde_option_missing_after_proved_customer` |
| `ui.parity.products.create` | `ui_products_create_open` | `ui_products_create_{preview,execute}` | **Gem produkt** count 1. **Arkiveret** count 1 | **Slet** counts 0. Both list shells archive-filter counts 0. `unique_restore_readback=none` | `owner_decision_67CBACB6` |
| `ui.parity.files.create` | `ui_uploads_list` | `ui_files_create_{preview,execute}` | **Upload filer** + `input[type=file]` | Bilag **Slet** 0 dual. No singular file DELETE | `interface_control_absent_UI_CHANGED` |
| `ui.parity.daybooks.create` | `ui_daybooks_open` | `ui_daybooks_create_{preview,execute}` | Both persist counts are 1. `name_input_count=0`. `unique_persist_token=none` | **Mere** then menu **Slet**. No tagged journal | `interface_control_absent_UI_CHANGED` |
| `ui.parity.daybooks.delete` | `ui_daybooks_delete_open` | `ui_daybooks_delete_{preview,execute}` | **Mere** then menu **Slet** on disposable journals. Primary **Slet** absent | No tagged create, so no tagged cleanup | `interface_control_absent_UI_CHANGED` |
| `ui.parity.daybookTransactions.create` | `ui_daybook_transactions_create_open` | `ui_daybook_transactions_create_{preview,execute}` | Line chrome / **Tilføj**. Official persist is **Godkend** | Needs a tagged journal that can be deleted | `high_impact_prohibited` |
| `ui.parity.transactions.create` | `ui_transactions_create_open` | `ui_transactions_create_{preview,execute}` | **Godkend** / **Godkend alle** | Posting is irreversible | `high_impact_prohibited` |

Family contracts: [[ui_contacts_writes]], [[ui_bills_writes]],
[[ui_organizations_writes]], [[ui_invoices_writes]],
[[ui_products_writes]], [[ui_files_writes]], [[ui_ledger_writes]].

## Owner questions still open

1. Invoice (`802D71CF`): inspect Kunde with a known customer already
   on the clients list. Name the exact existing-option click, or
   confirm the in-app list is empty while clients list shows the
   name. `113F1E05` forbids another entry-CTA dump. Do not treat
   this as `interface_control_absent`.
2. Product: answer `67CBACB6`. Does archive-until-absent count as
   restored state, or must create stay unbound? `A337A622` forbids more
   product list, dialog, or archive probes.
3. Daybook: accept `UI_CHANGED`, or name the persist token. Do not arm
   `_ledger_write`.
4. Files: accept fail-closed (no UI delete), or name a delete control
   not already counted 0.
5. Postings / **Godkend** stay prohibited unless a separately safe
   fixture proves no external consequence.

Do not remake closed invoice, product, daybook, or Bilag dumps. Do not
green honesty-16 from this page.

## Coverage

This page does not green any row. `complete` stays false until the
owner answers or a later live FastMCP write plus independent accept
plus purge exists.
