---
name: wave_fiveh_product_ready_research_independent_review
title: Wave-5h product-ready research independent review ACCEPT
desc: Authoritative root Grok acceptance of the cited offline product-ready handoff for singular attachment JSON ticketed writes under the accepted Wave-5h freeze.
tags: [billy, api, attachments, writes, review, coverage, research]
sources:
  - https://www.billy.dk/api/
  - wiki/wave_fiveh_ticketed_writes_contract.md
  - wiki/wave_fiveh_freeze_independent_review.md
  - coverage/api_v2_manifest.yaml
  - coverage/status.json
  - docs/superpowers/specs/2026-07-28-billy-mcp-complete-design.md
created: 2026-07-29T23:16:00Z
updated: 2026-07-29T23:16:00Z
---

# Wave-5h product-ready research independent review ACCEPT

## Verdict

| Claim | Result |
| --- | --- |
| Wave-5h product-ready research handoff | **ACCEPT** offline as implementation handoff only |
| Official documentation versus maintained inventory | **PASS** |
| Research versus accepted freeze tool/path/root map | **PASS** |
| Coverage honesty before product | **PASS** |
| Wave-5h product implementation | **not accepted** — separate Grok review required after root integration |
| Live, UI, vision, bulk, and completeness | **not claimed / fail-closed** |

The authoritative root `INDEPENDENT-REVIEW` Grok step accepted the product-ready
research at scratch `.fractal/main.billy_complete/tmp/grok-research.md`
(research35) against freeze merge HEAD **`c14266e`**, freeze page
`wiki/wave_fiveh_ticketed_writes_contract.md`, and freeze ACCEPT
`wiki/wave_fiveh_freeze_independent_review.md`. Full cited findings live outside
the public repository at `.fractal/main.billy_complete/tmp/grok-review.md`.

## Exact reviewed scope

This ACCEPT covers only the cited handoff that opens Codex Power product work
for the three singular API v2 CUD operations already frozen:

| Inventory id | Preview tool | Execute tool | HTTP | Request root | Response roots |
| --- | --- | --- | --- | --- | --- |
| `api.attachments.create` | `api_attachments_create_preview` | `api_attachments_create_execute` | `POST /attachments` | `attachment` | `attachments` |
| `api.attachments.update` | `api_attachments_update_preview` | `api_attachments_update_execute` | `PUT /attachments/:id` | `attachment` | `attachments` |
| `api.attachments.delete` | `api_attachments_delete_preview` | `api_attachments_delete_execute` | `DELETE /attachments/:id` | id binding | `attachments` + optional deleted meta |

Research arithmetic and file ownership match the freeze:

- Registry **202 → 208** `api_*` tools after product.
- Offline coverage **148 → 151** after real suites only.
- Suggested module `src/billy_mcp/api/attachment_writes.py` and tests
  `tests/api/test_attachment_writes.py` cloning sales-tax write patterns.
- Specs: `collection_path="/attachments"`, `singular_root="attachment"`,
  `plural_root="attachments"`, `additional_plural_roots=()`.
- Opaque inner payload; `priority` only clear mutable candidate; no invented
  owner encoding; no binary `/files` special; no bulk tools.

A stale research sentence that still described the freeze page as unmerged is
superseded by freeze merge `c14266e` and freeze ACCEPT; the tool/path/field
surface is unchanged and accepted.

## Product gate

This ACCEPT, together with
`wiki/wave_fiveh_freeze_independent_review.md`, opens offline Codex Power
product implementation for the six ticketed tools. It is not product ACCEPT,
live qualification, UI/vision acceptance, bulk resolution, or completeness.

After product integrates at root, a separate independent Grok product review
must confirm registry **208**, coverage **151** offline with the three
attachment CUD rows greened only by real suites, ticket binding and replay
boundaries, no fabricated `files` multi-root, and fail-closed live/UI/bulk.

No browser was launched, no credential or customer data was used, and no raw
browser evidence is retained. Coverage remains 148/148/0/0 with
`complete: false` until product and tests land.
