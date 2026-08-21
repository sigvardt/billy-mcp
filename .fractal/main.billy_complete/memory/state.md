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
  - radio:21A3D94F
created: 2026-08-16T14:29:47Z
updated: 2026-08-21T15:15:00Z
---

## Now

Parent `21A3D94F` owns this resume: one bounded offline
closeout, then finish. No production UI writes. No live API.
Do not spawn. Do not claim fresh production MCP qualification
from this closeout. That last check runs in the owner session
after merge.

Docs already record the 92 bulk mentions as owner-skip
(`BULK_CONTRACT_UNDOCUMENTED_OWNER_SKIP`) on `72aebd2`. The
generator, manifests, `coverage/status.json`, tests, and
checker still treat them as
`BULK_SCHEMA_UNSPECIFIED_OFFICIAL_DOCS` blockers. Encode the
skip in those surfaces. Keep the 92 rows visible, toolless,
not green, and outside the applicable count.

The six `READONLY_PROPERTY_TABLE` create/update rows stay
visible, toolless, and unimplemented:
`api.contactBalancePostings.create`,
`api.contactBalancePostings.update`, `api.postings.create`,
`api.postings.update`, `api.transactions.create`,
`api.transactions.update`. Official property tables still have
no writable request contract. Give them a separate owner-skip
scope code. Do not guess fields. Do not add tools. Reopen only
if Billy publishes a usable contract or the owner asks.

Completeness still fails while `source_kind=ambiguous_bulk`
rows exist and while API owner-skip rows must pass
`api_row_is_qualified`. Fix that so owner-skip API rows stay
visible but non-blocking. Then regenerate coverage, run
offline formatting, lint, type, unit, contract, safety, and
repository-policy checks, independent Grok review, clean
push, finish.

Do not run `BILLY_TEST_MODE=ui-full` live UI for this
closeout. Seed still names that gate; `21A3D94F` overrides it
for Fractal. API live stays deferred. Årsrapporter stays
`out_of_scope_by_user` (`ANNUAL_REPORTS_OWNER_SKIP`). Do not
invent `ui_annual_*` or `api_annual_*` tools. Do not edit
`coverage/status.json` by hand.

Typed official `GET /v2/bankLines` list filters are on
`api_bank_lines_list`. `accountId` is required. Docs lock is
ETag `pi4s9u10j037qn`, MD5 `d805f3d2bb8e339f7635d6834b4011bd`.
UI remaining unimplemented stays the six already owner-scoped
rows (annual reports, files create, daybooks create/delete,
daybookTransactions create, transactions create). Ticketed
offline `transactions` delete remains. Create/update of
transactions stay toolless.

Live official docs GET on 2026-08-21: ETag
`"usuwcuphx03ct7"`, MD5 `e1f8e5d5081645709ba736265ab9a098`.
That drifted from the frozen lock. Remaining tables still
show 46 bulk-save and 46 bulk-delete Supports flags with no
body schema, and the six create/update property tables still
have no writable request field. Do not relock. Do not infer
payloads. Recommended readonly skip code is
`READONLY_PROPERTY_TABLE_OWNER_SKIP`. Brief is
`.fractal/main.billy_complete/tmp/grok-research.md`.

Generated snapshot reads implemented 546, contract 551,
live/vision 339, `complete=true` under owner scope. Bulk92 and
six readonly-map rows stay visible and toolless. Independent
review PASS. Required fixes none. FIX-VERIFY recorded. COMMIT
next, then finish under `21A3D94F`. Do not claim fresh
production MCP qualification.

`9B979A05` bulk research is stopped. `96908DC6` Fractal
UI-write path is superseded for this closeout. Unsaved both.

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
