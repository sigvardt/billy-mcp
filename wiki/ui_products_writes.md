---
name: ui_products_writes
desc: Ticketed UI product create and owner-proved hard-delete. No coverage greening.
tags: [billy, ui, writes, products, tickets]
sources:
  - wiki/ui_write_ticket_protocol.md
  - wiki/ui_products_create_open_shell.md
  - wiki/ui_products_get_update_delete_not_applicable.md
created: 2026-08-16T14:31:10Z
updated: 2026-08-19T15:30:00Z
---

# ui_products_writes

Ticketed interface create and delete for Billy products. Preview writes
nothing. Execute accepts only `confirmation_ticket`. This lane never
calls `https://api.billysbilling.com/v2`.

See [[ui_write_ticket_protocol]] for the shared ticket rule. The read-only
form-open tool remains [[ui_products_create_open_shell]].

## Tools

| Tool | Role |
| --- | --- |
| `ui_products_create_preview` | Bind name and required `unitPrice > 0`. Optional account and salesTaxRuleset. Return a ticket. |
| `ui_products_create_execute` | Consume that ticket once. Fill **Enhedspris**, then **Gem produkt**. |
| `ui_products_delete_preview` | Bind unique tagged name and organisation. Optional id. Return a ticket. |
| `ui_products_delete_execute` | Consume that ticket once. Row `data-cy=delete-icon`, then **Ja, slet**. |

The bound create follows owner `C6DA7FC8` on `/:org_slug/products`:
**Opret produkter**, then the **Opret produkt** dialog if the name
field is not yet visible. Soft `/products/new` is not success.
Delete starts on `/products`, then tries `/inventory` once if the
icon is missing.

Create and delete execute compare the live URL slug to the ticket
organisation before fill or click. A mismatch is
`CONFIRMATION_MISMATCH`. After **Gem produkt**, a still-visible
create dialog is `UI_CHANGED` with any visible validation text.
That is not a successful persist. Hidden Ember dialog nodes are
not failure.

Owner `C6DA7FC8` proves persist on `/:org/products`: **Opret
produkter**, then the **Opret produkt** dialog, name, **Enhedspris**=1,
defaults 1110 Salg / Normalt salg af varer / DKK, **Gem produkt**.
The modal closes. Create execute starts on `/:org/products` (**Opret produkter** then
the dialog). After **Gem produkt** it hard-navigates `/products`
and proves the tag in visible body text (`allow_search=False`,
`visible_body=True`). Hidden Ember `get_by_text` hits are not
persist. Inventory is only the second attempt. Delete scopes to the tagged `[data-cy='table-item']`, reveals
row actions, then clicks that row's `delete-icon` and **Ja,
slet**. Watch `DELETE /v2/products/:id` 2xx before independent
`/products` row absence. Collection and `ids[]` bulk do not
count. Never a page-wide `delete-icon`.first. No `force=True`.
Stay red.

Qualify through FastMCP `call_tool`. Do not treat BrowserRuntime as the pass
proof.

## Fail closed

Do not send invoices or emails. Do not make payments. Do not submit VAT or
filings. Do not change users, access, tokens, or subscription. Do not invent
`ui_annual_*` tools. Do not add product update tools. Owner `56354201`
requires exact product delete through the proved row control.

## Coverage

Row `ui.parity.products.create` stays ungreened by this family. Root may point
it at the preview tool after a live MCP proof.

## Live and cleanup

`D326FFB3` is the live go-ahead for this family. Stale radio
`72C01DF9` no longer holds the slot.

Recapture dump
`~/.local/share/billy-mcp/inspect-live-products-delete-chrome.json`
still shows no unique UI delete path. Products **Mere** opened.
**Slet** and **Slet produkt** counts are 0 on `/:org_slug/products`
and `/:org_slug/inventory`. Create form opened. Name field visible.
Save CTA token is `other`, not exact **Gem**.
`proved_delete_path=none`. `UI_CHANGED`. Do not remake that dump.

Official dialog dump
`~/.local/share/billy-mcp/inspect-live-products-form-contract.json`
classifies the Lagermodul **Opret produkt** form as
`proved_submit=gem_produkt` and
`unique_cleanup_path=archive_checkbox`. Exact **Gem produkt**
count is 1. Exact **Gem** count is 0. Exact **Arkiveret (skjul
fra lister)** count is 1. Dialog heading is `opret_produkt`.
Archive hides from lists (`isArchived`). It is not **Slet**.
Do not remake this dump. Do not click **Gem produkt**.

Archive-list dump
`~/.local/share/billy-mcp/inspect-live-products-archive-list.json`
classifies `/:org_slug/products` as `products_path_class=products`,
`products_heading_token=produkter`, `search_control_visible=false`,
exact **Vis arkiverede** / **Arkiverede** / **Skjul arkiverede**
counts 0, `archived_filter_token=none`,
`unique_restore_readback=none`, `proved_bind=none`. No product
created. Do not remake this dump. Do not click those labels.

Lagermodul archive-list dump
`~/.local/share/billy-mcp/inspect-live-inventory-archive-list.json`
classifies `/:org_slug/inventory` as `inventory_path_class=inventory`,
`inventory_heading_token=lagermodul`, `create_form_open=false`,
exact **Vis arkiverede** / **Arkiverede** / **Skjul arkiverede**
counts 0, `archived_filter_token=none`,
`unique_restore_readback=none`, `proved_bind=none`. No product
created. Do not remake this dump. Do not open **Opret produkt**
in inspect tests. Archive-until-absent is not the cleanup path.

Owner `56354201` proves the unique cleanup path: row
`data-cy=delete-icon` then **Ja, slet**. The products list
returns to **Ingen produkter**. Archive-until-absent is not
the cleanup path. Do not remake the form-contract, Mere/Slet,
or archive-list dumps (`A337A622`).

Do not remake inspect dumps. Do not click **Arkiveret**. Live
FastMCP create/delete uses `call_tool`. Do not treat
BrowserRuntime as the pass proof. Do not API-delete.

Cleanup: delete the tagged product through the owner-proved
row delete, then prove **Ingen produkter** on a fresh session.

Live FastMCP create/delete now captures four owner-only frames
(`01_before.png`, `02_before_submit.png` filled **Opret produkt**
dialog before **Gem produkt**, `03_after_create.png`,
`04_after_delete.png`). Before screenshot, capture reads the name
field and **Enhedspris** / `input[name=unitPrice]` and requires
normalized equality with the bound price (`94A4C844`). The durable
record is `tmp/vision-records/ui_products_writes.json`,
`run_id=29c1b1de26a14976aaa1b98bfe9de46e`, `author=live_test`,
`pending_review`. Frames stay outside git. Do not accept or purge
in this slice. Honesty stays red until independent accept and purge.
