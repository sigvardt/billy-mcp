---
name: wave_fiveh_freeze_independent_review
title: Wave-5h contract freeze independent review ACCEPT
desc: Authoritative root Grok acceptance of the cited offline contract for singular attachment JSON ticketed writes.
tags: [billy, api, attachments, writes, review, coverage]
sources:
  - https://www.billy.dk/api/
  - wiki/wave_fiveh_ticketed_writes_contract.md
  - wiki/wave_fiveh_freeze_ready_research_independent_review.md
  - wiki/offline_write_probe_rules.md
  - coverage/api_v2_manifest.yaml
  - coverage/status.json
  - docs/superpowers/specs/2026-07-28-billy-mcp-complete-design.md
created: 2026-07-29T23:16:00Z
updated: 2026-07-29T23:16:00Z
---

# Wave-5h contract freeze independent review ACCEPT

## Verdict

| Claim | Result |
| --- | --- |
| Wave-5h cited contract freeze | **ACCEPT** |
| Official documentation versus maintained inventory | **PASS** |
| Freeze versus exact three-row tool/path/root map | **PASS** |
| Coverage honesty before product integration | **PASS** |
| Wave-5h product implementation | **not accepted** — separate Grok review required after root integration |
| Live, UI, vision, bulk, and completeness | **not claimed / fail-closed** |

The authoritative root `INDEPENDENT-REVIEW` Grok step accepted the merged freeze
page at root HEAD **`c14266e`** (`wiki/wave_fiveh_ticketed_writes_contract.md`,
originally authored as a Codex Power fallback candidate). Full cited findings
live outside the public repository at
`.fractal/main.billy_complete/tmp/grok-review.md`.

A dedicated freeze-review child exited without a durable verdict; this root
review is the authoritative freeze gate.

## Exact reviewed scope

The accepted contract freezes exactly three singular API v2 JSON CUD operations
(six ticketed tools: three preview + three execute):

| Inventory id | Method and client path | Singular request root | Response roots (offline) |
| --- | --- | --- | --- |
| `api.attachments.create` | `POST /attachments` | `attachment` | `attachments` only |
| `api.attachments.update` | `PUT /attachments/:id` | `attachment` | `attachments` only |
| `api.attachments.delete` | `DELETE /attachments/:id` | bodyless id binding | `attachments`, optional deleted metadata |

The accepted contract preserves the locked
`https://api.billysbilling.com/v2` base, client-relative paths without a
duplicated `/v2`, opaque inner `attachment` payloads, strict outer Pydantic
inputs, partial `PUT`, update-id equality, and bodyless deletes. It requires
the root shared `ConfirmationStore` and `WriteProtocolService`, exact
server-owned executor-name ticket binding, single-use short-lived tickets, and
no write retry. Spec constants:

- `collection_path="/attachments"`
- `singular_root="attachment"`
- `plural_root="attachments"`
- `additional_plural_roots=()`

Official field notes match the freeze: `organization`, `owner`, and `file` are
immutable required; `createdTime` is readonly; `owner` is a
belongs-to-reference with no public serialization recipe; `priority` is the
only clear mutable candidate. Binary `POST /files` (and `api.files.create` /
`api.special.files_upload`) stay out of scope. Bulk save/delete remain
`ambiguous_bulk` with empty `tool_name`.

## Recheck and product gate

Official documentation was re-fetched during review with ETag
`hsisik4g9p3603`, body length 147934, and MD5
`c2efda0ee4cf9cf200e14910c5fc6996`, matching `coverage/status.json` with no
source drift. Unauthenticated probes returned 401 for POST and PUT on
`/attachments`, 200 for missing-id DELETE (not cleanup proof), and 400
`INVALID_JSON` for a deliberate JSON body on `/files` (not a JSON create
contract). Coverage at freeze merge remains 148 implemented, 148
contract-tested, 0 live, 0 vision, and `complete: false`. No
`attachment_writes` module exists. Attachment CUD inventory rows stay red.
Registry remains 202 `api_*` tools.

This ACCEPT opens offline product implementation for the six ticketed
attachment JSON write tools. It is not a product ACCEPT. After the product is
integrated at root, a separate independent Grok product review must inspect
exact routes, opaque payload discipline, ticket binding and replay boundaries,
registry target **208** `api_*` tools, coverage target **151** offline rows
with the three attachment CUD rows contract-tested only by real suites, and
fail-closed live/UI/bulk state.

No browser was launched, no credential or customer data was used, and no raw
browser evidence is retained. The acceptance remains an offline contract
decision only.
