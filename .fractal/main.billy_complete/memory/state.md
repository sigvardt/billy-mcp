---
name: state
desc: Current node state for the Billy MCP complete run.
tags: [billy, coverage, ui_writes]
sources:
  - docs/superpowers/specs/2026-07-28-billy-mcp-complete-design.md
  - https://www.billy.dk/api/
  - radio:96908DC6
  - radio:9B979A05
  - radio:B54A6BFC
  - radio:2D09964C
  - radio:8C5F08A8
  - radio:AF8E5A1F
  - radio:EAB2F91B
  - radio:7C9348E1
  - radio:FE6FA4B1
  - radio:DC3B8E96
created: 2026-08-16T14:29:47Z
updated: 2026-08-20T02:15:00Z
---

## Now

Ticketed offline `cities` create and update are landed. Preview
tools `api_cities_create_preview` and `api_cities_update_preview`
take a nested payload of optional string `name`, `county`,
`state`, and `country` with `extra=forbid`. `stateId` and
`countryId` fail at the FastMCP boundary. Empty nested object is
valid. Create is `POST /cities`. Update is `PUT /cities/:id` with
a non-empty encoded id. Execute takes `confirmation_ticket`
only. Preview makes no HTTP. Bulk stay red. No singular delete.
`live_tested` stays false with
`qualification.live_api=out_of_scope_by_user`. Independent review
PASS. `complete` stays false.

Generated snapshot: implemented 530, contract 535, live/vision
339, `complete=false`. Residual honesty remaining is 22 (18
method-closed, 2 readonly-map, 2 meta-delete). Bulk 92 stay
`BULK_SCHEMA_UNSPECIFIED_OFFICIAL_DOCS`. Official lock is ETag
`tmhc6wpdc835zt`, MD5 `053f755f52e3926b028e29325e3670d4`.

Next bind after this COMMIT is parent `AF8E5A1F`: ticketed
`countryGroups` create and update only. Nested optional string
`name`, `icon`, `memberCountryIds`. Binding `9B979A05` still owns
the rest of the 121 split. Unauth 405 must not override Supports.
Never infer bulk schemas. No live API. Do not finish.

Owner `96908DC6` still binds overall finish. API live stays
deferred. Årsrapporter stays `out_of_scope_by_user`
(`ANNUAL_REPORTS_OWNER_SKIP`). Do not invent `ui_annual_*` or
`api_annual_*` tools. Do not edit `coverage/status.json` by hand.

## Proved UI writes still in inventory

Contacts, draft bills, invoices, products, and organization
company fields are live FastMCP CUD with independent accept and
purged frames. Coverage names the `*_preview` tools. Honesty-16
stay red until remaining families prove the same way. Daybook
persist is not unique. Files have no UI delete. **Godkend** stays
prohibited. Product archive probes stay forbidden (`A337A622`).
Leftover reverse-clean stays isolated from reusable invoice CUD
(`D71E5B82`).

## Standing constraints

API token auth is offline only. Live `BILLY_API_TOKEN` is not
required. Persistent browser profile is MCP-owned and headless.
`auth_login_wait` READY returns `organization_id` from the live
URL slug. Ticket execute compares that slug to
`prepared.binding.organization_id`. Interface read-back starts a
second runtime and must authenticate. Cleanup needs a third
fresh read-back. Live write tests may write
`author=live_test` and `reviewer_verdict=pending_review` only.
They must not write `accept` or purge frames.

Live refs: keyring service `billy-mcp`, opaque ids
`billy-ui-primary` and `billy-ui-secondary`. Never log values.
Never read `/Users/user/Desktop/billy_login.txt`.

## Children

No children are running. Seven write children stay completed and
merged (`ui_contacts_writes`, `ui_bills_writes`,
`ui_invoices_writes` draft only, `ui_products_writes`,
`ui_ledger_writes`, `ui_files_writes`, `ui_org_writes` company
fields only). Leftover retired descendants stay unmerged. Do not
continue, reset, or merge them.

See `decisions.md` and `todo.md`.
