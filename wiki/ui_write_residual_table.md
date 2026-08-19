---
name: ui_write_residual_table
desc: Residual UI write table. Eleven accepted CUD rows are preview_execute. Five files and ledger rows stay red.
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
  - radio:A6A2B60C
  - radio:31BAF1FF
  - radio:D71E5B82
  - radio:A0633A17
  - radio:58D7D0E1
  - wiki/ui_write_ticket_protocol.md
  - wiki/ui_contacts_writes.md
  - wiki/ui_bills_writes.md
  - wiki/ui_organizations_writes.md
  - wiki/ui_invoices_writes.md
  - wiki/ui_products_writes.md
  - wiki/ui_files_writes.md
  - wiki/ui_ledger_writes.md
created: 2026-08-18T14:30:00Z
updated: 2026-08-19T18:05:00Z
---

# ui_write_residual_table

Owner-scope UI write residual after `D68E402A`, `EC676F84`, and
`58D7D0E1`. Shared ticket rules live in [[ui_write_ticket_protocol]].

The 11 accepted rows are `preview_execute` with
`implemented=live_tested=vision_verified=true`. Honesty now covers
only the five files and ledger rows. `complete` stays false.
The manifest has no other unimplemented write-like UI parity row.

Contacts, bills, and organizations are already live-proved through
FastMCP. Owner fact-check `9310BC17` is applied: a new
`/invoices/new` plus `[data-cy='dropdown-icon']` binds an existing
customer (`vendor_bind=scoped:existing_option`, GET with
`contactId`). Invoice Kunde is not `interface_control_absent`.
Create preview now requires `unit_price > 0`. Owner `A6A2B60C`
and `31BAF1FF` independently proved empty invoices, products,
and contacts after reverse cleanup and after disposable CUD.
Update and delete open the exact `li[role=row]`. Do not use a
POST id as persist proof. Do not remake leftover reverse-clean.

Owner `56354201` proves product create and hard-delete in the
normal UI: **Opret produkt**, **Enhedspris**=1, visible on a
fresh `/invoices/new` **Vælg produkt**, then row
`data-cy=delete-icon` and **Ja, slet**. Products list returned
to **Ingen produkter**. Do not treat product as
`interface_control_absent` or archive-only. Do not stop on
`67CBACB6`. Invoice CUD vision
`run_id=60b6d620772644f3bca9609c8ae53846` is accept with purge
verified. Product create vision
`run_id=29c1b1de26a14976aaa1b98bfe9de46e` is accept with purge
verified. Do not remake picker, archive, leftover, or Kunde dumps.

`FD39FFE7` still makes invoice draft CUD and product create mandatory
MCP capabilities. They are now `preview_execute`, not `UI_CHANGED`.

## Categories

- `proved_preview_execute`
- `interface_control_absent_UI_CHANGED`
- `high_impact_prohibited`

## Table

| ID | Coverage tool | Registered preview / execute | Mutation control | Cleanup / read-back | Category |
| --- | --- | --- | --- | --- | --- |
| `ui.parity.contacts.create` | `ui_clients_create_preview` | `ui_clients_create_{preview,execute}` | **Gem** `data-cy=save-button`. Live FastMCP | Fresh-session name read-back. **Ja, slet**. Absence 0. Vision `3d5b151dfd5342258f8734373597f8c1` accept, purged | `proved_preview_execute` |
| `ui.parity.contacts.update` | `ui_clients_update_preview` | `ui_clients_update_{preview,execute}` | Exact **Ret**, then **Gem** | `{tag}-U` is a different name. Same vision | `proved_preview_execute` |
| `ui.parity.contacts.delete` | `ui_clients_delete_preview` | `ui_clients_delete_{preview,execute}` | **Slet kontakt** link, **Ja, slet** | Fresh-session absence. Same vision | `proved_preview_execute` |
| `ui.parity.bills.create` | `ui_bills_create_preview` | `ui_bills_create_{preview,execute}` | Existing-option vendor bind. **Gem som kladde** | Fresh-session draft read-back. Vision `9920dd9476474b41aef70e6d66d24638` accept, purged | `proved_preview_execute` |
| `ui.parity.bills.update` | `ui_bills_update_preview` | `ui_bills_update_{preview,execute}` | Draft edit + draft save | Independent read-back. Same vision | `proved_preview_execute` |
| `ui.parity.bills.delete` | `ui_bills_delete_preview` | `ui_bills_delete_{preview,execute}` | Delete chrome + confirm | Reverse cleanup. Same vision | `proved_preview_execute` |
| `ui.parity.organizations.update` | `ui_organizations_update_preview` | `ui_organizations_update_{preview,execute}` | Company phone field + **Gem** | Tagged set then exact empty restore. Vision `0937a009bf7e496ca2ce15a8af313868` accept, purged | `proved_preview_execute` |
| `ui.parity.invoices.create` | `ui_invoices_create_preview` | `ui_invoices_create_{preview,execute}` | Self-contained FastMCP CUD. Pre-submit `02_before_submit.png` before **Gem som kladde** (`A342BBDC`) | Reverse-clean invoice, product, customer. Vision `60b6d620772644f3bca9609c8ae53846` accept, purged | `proved_preview_execute` |
| `ui.parity.invoices.update` | `ui_invoices_update_preview` | `ui_invoices_update_{preview,execute}` | Fresh page. Exact **Enhedspris** fill `2,00`. List result `2,00 DKK` | Independent read-back. Same vision | `proved_preview_execute` |
| `ui.parity.invoices.delete` | `ui_invoices_delete_preview` | `ui_invoices_delete_{preview,execute}` | Unique **Mere**, `A` **Slet**, dump, exact **Ja, slet faktura** | Owner independently empty after reverse cleanup and after disposable CUD. Same vision | `proved_preview_execute` |
| `ui.parity.products.create` | `ui_products_create_preview` | `ui_products_create_{preview,execute}` and `ui_products_delete_{preview,execute}` | Live FastMCP create persist is proved on unfiltered visible `/products`. Delete scopes to tagged `data-cy=table-item` then row `delete-icon` and **Ja, slet**, then one `DELETE /v2/products/:id` 2xx | Reverse-clean used singular DELETE 2xx then settled `/products` **Ingen produkter**. Vision `29c1b1de26a14976aaa1b98bfe9de46e` accept, purged | `proved_preview_execute` |
| `ui.parity.files.create` | `ui_uploads_list` | `ui_files_create_{preview,execute}` | **Upload filer** + `input[type=file]` | Bilag **Slet** 0 dual. No singular file DELETE | `interface_control_absent_UI_CHANGED` |
| `ui.parity.daybooks.create` | `ui_daybooks_open` | `ui_daybooks_create_{preview,execute}` | Both persist counts are 1. `name_input_count=0`. `unique_persist_token=none` | **Mere** then menu **Slet**. No tagged journal | `interface_control_absent_UI_CHANGED` |
| `ui.parity.daybooks.delete` | `ui_daybooks_delete_open` | `ui_daybooks_delete_{preview,execute}` | **Mere** then menu **Slet** on disposable journals. Primary **Slet** absent | No tagged create, so no tagged cleanup | `interface_control_absent_UI_CHANGED` |
| `ui.parity.daybookTransactions.create` | `ui_daybook_transactions_create_open` | `ui_daybook_transactions_create_{preview,execute}` | Line chrome / **Tilføj**. Official persist is **Godkend** | Needs a tagged journal that can be deleted | `high_impact_prohibited` |
| `ui.parity.transactions.create` | `ui_transactions_create_open` | `ui_transactions_create_{preview,execute}` | **Godkend** / **Godkend alle** | Posting is irreversible | `high_impact_prohibited` |

Family contracts: [[ui_contacts_writes]], [[ui_bills_writes]],
[[ui_organizations_writes]], [[ui_invoices_writes]],
[[ui_products_writes]], [[ui_files_writes]], [[ui_ledger_writes]].

## Owner questions

1. Invoice and product CUD are `preview_execute` after `58D7D0E1`.
   Do not remake leftover reverse-clean or product dumps (`A337A622`).
2. Daybook: accept `UI_CHANGED`, or name the persist token. Do not arm
   `_ledger_write`.
3. Files: accept fail-closed (no UI delete), or name a delete control
   not already counted 0.
4. Postings / **Godkend** stay prohibited unless a separately safe
   fixture proves no external consequence.

Do not remake closed invoice, product, daybook, or Bilag dumps.

## Coverage

The generator greens only the 11 proved rows from vision records.
This page does not hand-edit coverage. `complete` stays false while
files, daybook, **Godkend**, bulk92, and API live stay out of green.
