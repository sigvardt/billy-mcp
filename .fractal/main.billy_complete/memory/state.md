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
  - radio:4DE5EE18
  - radio:47B85E43
  - radio:05F3200D
  - radio:AB6ABE84
  - radio:8FE83270
  - radio:7453B98F
  - radio:4DBD7C3F
  - radio:7B947636
  - radio:A485F530
  - radio:EAB2F91B
  - radio:7C9348E1
  - radio:FE6FA4B1
  - radio:DC3B8E96
  - radio:3DA6FB8E
created: 2026-08-16T14:29:47Z
updated: 2026-08-20T14:30:00Z
---

## Now

Parent `3DA6FB8E` is done: independent review of the
bankLines list-filter slice on `df2f475` PASSed. Frozen
List filters match `BankLinesListRequest`. GET is
`/bankLines` only. Shared `BankListRequest` still rejects
`accountId` and `q`. Owner-input report is posted. No
required fixes. Stopped for owner scope on bulk92 plus six
readonly-map rows. No new tools. No live docs GET. Do not
spawn. `complete` stays false. Do not finish.

Typed official `GET /v2/bankLines` list filters are on
`api_bank_lines_list`. `accountId` is required. Docs lock is
ETag `pi4s9u10j037qn`, MD5 `d805f3d2bb8e339f7635d6834b4011bd`.
Remaining unimplemented API rows stay bulk92 plus six
readonly-map create/update rows. UI remaining unimplemented
stays six owner-scoped rows. Do not guess bulk or
readonly-map tools.

Ticketed offline `transactions` delete remains on `bb66a48`.
Preview tool `api_transactions_delete_preview` takes a non-empty
`id` with `extra=forbid`. Execute
`api_transactions_delete_execute` takes `confirmation_ticket`
only. Create/update stay red. Bulk stay red.

Generated snapshot: implemented 546, contract 551, live/vision
339, `complete=false`. Residual honesty remaining is 6, all
readonly-map. Meta-delete remaining is none. Bulk 92 stay
`BULK_SCHEMA_UNSPECIFIED_OFFICIAL_DOCS`. Official lock is ETag
`pi4s9u10j037qn`, MD5 `d805f3d2bb8e339f7635d6834b4011bd`.

EXECUTE recheck tests that still lock the residual set:

- `tests/api/test_bank_reads.py`
- `tests/coverage/test_official_docs_lock.py`
- `tests/coverage/test_coverage_inventory.py::test_residual_audit_unimplemented_api_set_is_bulk_plus_readonly_map`
- `tests/coverage/test_coverage_inventory.py::test_residual_clear_honesty_rows_are_toolless_and_qualified`
- `tests/coverage/test_coverage_inventory.py::test_bulk_rows_remain_ambiguous_and_toolless`
- `tests/coverage/test_ui_residual_write_owner_scope.py::test_unimplemented_ui_rows_are_exactly_owner_scoped`

Unread owner radio after the recheck: none besides already
handled `3DA6FB8E`.

Binding `9B979A05` still owns the rest of the 121 split. Unauth
405 must not override current official Supports. Never infer
bulk schemas. Do not finish.

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

No children are running. Parent `main` and `origin/main` are
already in HEAD `df2f475`. Seven write children stay completed
and merged (`ui_contacts_writes`, `ui_bills_writes`,
`ui_invoices_writes` draft only, `ui_products_writes`,
`ui_ledger_writes`, `ui_files_writes`, `ui_org_writes` company
fields only) with empty logs versus this branch. 62 leftover
retired descendants still have commits; they stay unmerged. Do
not continue, reset, or merge them.

See `decisions.md` and `todo.md`.
