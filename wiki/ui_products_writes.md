---
name: ui_products_writes
desc: Ticketed UI product create preview and execute. No coverage greening.
tags: [billy, ui, writes, products, tickets]
sources:
  - wiki/ui_write_ticket_protocol.md
  - wiki/ui_products_create_open_shell.md
  - wiki/ui_products_get_update_delete_not_applicable.md
created: 2026-08-16T14:31:10Z
updated: 2026-08-18T04:32:00Z
---

# ui_products_writes

Ticketed interface create for Billy products. Preview writes nothing. Execute
accepts only `confirmation_ticket`. This lane never calls
`https://api.billysbilling.com/v2`.

See [[ui_write_ticket_protocol]] for the shared ticket rule. The read-only
form-open tool remains [[ui_products_create_open_shell]].

## Tools

| Tool | Role |
| --- | --- |
| `ui_products_create_preview` | Bind name plus optional account, salesTaxRuleset, unitPrice. Return a ticket. |
| `ui_products_create_execute` | Consume that ticket once. Offline execute returns the bound request. It does not open a browser. |

The bound action is the Lagermodul **Opret produkt** form on
`/:org_slug/inventory`. Offline execute does not open that form. Catalog
`/products` has no create CTA. Soft `/products/new` is not success.

Qualify through FastMCP `call_tool`. Do not treat BrowserRuntime as the pass
proof.

## Fail closed

Do not send invoices or emails. Do not make payments. Do not submit VAT or
filings. Do not change users, access, tokens, or subscription. Do not invent
`ui_annual_*` tools. Do not add product update or delete tools.

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
`proved_delete_path=none`. `UI_CHANGED`.

Do not click **Gem**. Do not run `ui_products_create_execute` until
a later recapture proves a unique delete control. Do not invent
`ui_products_delete_*`. Do not API-delete. Do not remake this dump
unless the page shows a genuinely new Slet control.

Cleanup blocker: [[ui_products_get_update_delete_not_applicable]]
(research176) still holds. If a live create ever submits, record
that tagged name as leftover cleanup.
