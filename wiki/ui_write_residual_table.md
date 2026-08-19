---
name: ui_write_residual_table
desc: Residual honesty-16 UI write table. Product hard-delete is owner-proved. FastMCP product CUD is next.
tags: [billy, ui, writes, residual, honesty]
sources:
  - radio:96908DC6
  - radio:D68E402A
  - radio:FD39FFE7
  - radio:113F1E05
  - radio:A337A622
  - radio:67CBACB6
  - radio:56354201
  - radio:EC676F84
  - radio:9310BC17
  - radio:1F1B34F8
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
updated: 2026-08-18T22:40:00Z
---

# ui_write_residual_table

Owner-scope UI write residual after `D68E402A` and `EC676F84`.
Shared ticket rules live in [[ui_write_ticket_protocol]].

The honesty-16 gate still keeps every row red
(`implemented=false`, `live_tested=false`, `vision_verified=false`).
The manifest has no other unimplemented write-like UI parity row.

Contacts, bills, and organizations are already live-proved through
FastMCP. Owner fact-check `9310BC17` is applied: a new
`/invoices/new` plus `[data-cy='dropdown-icon']` binds an existing
customer (`vendor_bind=scoped:existing_option`, GET with
`contactId`). Invoice Kunde is not `interface_control_absent`.
Create preview now requires `unit_price > 0`. Six leftover priced
drafts persist. Update and delete open the exact `li[role=row]`.
Do not use a POST id as persist proof.

Owner `56354201` proves product create and hard-delete in the
normal UI: **Opret produkt**, **Enhedspris**=1, visible on a
fresh `/invoices/new` **Vælg produkt**, then row
`data-cy=delete-icon` and **Ja, slet**. Products list returned
to **Ingen produkter**. Do not treat product as
`interface_control_absent` or archive-only. Do not stop on
`67CBACB6`. Next is FastMCP product create/delete, then invoice
draft CUD with that disposable product. Do not remake picker,
archive, or Kunde dumps. Do not ask the owner to inspect
routine UI.

`FD39FFE7` still makes invoice draft CUD and product create mandatory
and red. They are not finished as `UI_CHANGED`.

## Categories

- `already_live_proved_honesty_red`
- `owner_proved_pending_fastmcp`
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
| `ui.parity.invoices.create` | `ui_invoices_create_open` | `ui_invoices_create_{preview,execute}` exist. Coverage still names `*_open` | Six leftover **Kladde** rows already persist. Stay red until independent accept | Reverse cleanup after one FastMCP update | `owner_proved_pending_fastmcp` |
| `ui.parity.invoices.update` | `ui_invoices_update_open` | `ui_invoices_update_{preview,execute}` | List-row open. Wait for visible main-frame `input[name=unitPrice][placeholder=Enhedspris]`, fill `2,00`. Line persist is `PUT /v2/invoiceLines/:id`. No guessed line click | Fresh-session row open must show 2,00 before delete | `owner_proved_pending_fastmcp` |
| `ui.parity.invoices.delete` | `ui_invoices_delete_open` | `ui_invoices_delete_{preview,execute}` | Same list-row open. **Mere** / **Slet** still fires no DELETE XHR | Six leftover drafts still present | `owner_proved_pending_fastmcp` |
| `ui.parity.products.create` | `ui_products_create_open` | `ui_products_create_{preview,execute}` and `ui_products_delete_{preview,execute}` | Live FastMCP create persist is proved on unfiltered visible `/products`. Delete now scopes to tagged `data-cy=table-item` then row `delete-icon` and **Ja, slet**. Stay red until leftover cleanup and independent accept | Cleanup: tagged table-item `delete-icon` then **Ja, slet**. Live FastMCP leftover sweep proved **Ingen produkter**. Stay red until independent accept and purge | `owner_proved_pending_fastmcp` |
| `ui.parity.files.create` | `ui_uploads_list` | `ui_files_create_{preview,execute}` | **Upload filer** + `input[type=file]` | Bilag **Slet** 0 dual. No singular file DELETE | `interface_control_absent_UI_CHANGED` |
| `ui.parity.daybooks.create` | `ui_daybooks_open` | `ui_daybooks_create_{preview,execute}` | Both persist counts are 1. `name_input_count=0`. `unique_persist_token=none` | **Mere** then menu **Slet**. No tagged journal | `interface_control_absent_UI_CHANGED` |
| `ui.parity.daybooks.delete` | `ui_daybooks_delete_open` | `ui_daybooks_delete_{preview,execute}` | **Mere** then menu **Slet** on disposable journals. Primary **Slet** absent | No tagged create, so no tagged cleanup | `interface_control_absent_UI_CHANGED` |
| `ui.parity.daybookTransactions.create` | `ui_daybook_transactions_create_open` | `ui_daybook_transactions_create_{preview,execute}` | Line chrome / **Tilføj**. Official persist is **Godkend** | Needs a tagged journal that can be deleted | `high_impact_prohibited` |
| `ui.parity.transactions.create` | `ui_transactions_create_open` | `ui_transactions_create_{preview,execute}` | **Godkend** / **Godkend alle** | Posting is irreversible | `high_impact_prohibited` |

Family contracts: [[ui_contacts_writes]], [[ui_bills_writes]],
[[ui_organizations_writes]], [[ui_invoices_writes]],
[[ui_products_writes]], [[ui_files_writes]], [[ui_ledger_writes]].

## Owner questions

1. Invoice (`9310BC17` / `1F1B34F8` / `56354201`): Kunde and
   **Enhedspris** work. Create ticket now requires `product_name`.
   Live FastMCP CUD is the remaining proof. Do not ask the owner
   to inspect routine UI.
2. Product (`56354201`): hard-delete is owner-proved. Do not
   remake archive or dialog dumps (`A337A622`). Implement
   FastMCP create/delete. Do not treat archive-only as the
   cleanup path.
3. Daybook: accept `UI_CHANGED`, or name the persist token. Do not arm
   `_ledger_write`.
4. Files: accept fail-closed (no UI delete), or name a delete control
   not already counted 0.
5. Postings / **Godkend** stay prohibited unless a separately safe
   fixture proves no external consequence.

Do not remake closed invoice, product, daybook, or Bilag dumps. Do not
green honesty-16 from this page.

## Coverage

This page does not green any row. `complete` stays false until a later
live FastMCP write plus independent accept plus purge exists.
