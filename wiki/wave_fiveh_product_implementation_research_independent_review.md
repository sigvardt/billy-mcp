---
name: wave_fiveh_product_implementation_research_independent_review
title: Wave-5h product-implementation research independent review ACCEPT
desc: Authoritative root Grok acceptance of the research36 offline product-implementation handoff for singular attachment JSON ticketed writes under the accepted Wave-5h freeze.
tags: [billy, api, attachments, writes, review, coverage, research]
sources:
  - https://www.billy.dk/api/
  - wiki/wave_fiveh_ticketed_writes_contract.md
  - wiki/wave_fiveh_freeze_independent_review.md
  - wiki/wave_fiveh_product_ready_research_independent_review.md
  - coverage/api_v2_manifest.yaml
  - coverage/status.json
  - docs/superpowers/specs/2026-07-28-billy-mcp-complete-design.md
created: 2026-07-29T23:36:00Z
updated: 2026-07-29T23:36:00Z
---

# Wave-5h product-implementation research independent review ACCEPT

## Verdict

| Claim | Result |
| --- | --- |
| Research36 product-implementation handoff | **ACCEPT** offline as implementation handoff only |
| Official documentation versus maintained inventory | **PASS** (fingerprint unchanged) |
| Research versus accepted freeze tool/path/root map | **PASS** |
| Coverage honesty before product | **PASS** |
| Wave-5h product implementation | **not accepted** — separate Grok product review required after root integration |
| Live, UI, vision, bulk, and completeness | **not claimed / fail-closed** |

The authoritative root `INDEPENDENT-REVIEW` Grok step accepted the
product-implementation research at scratch
`.fractal/main.billy_complete/tmp/grok-research.md` (research36) against freeze
page `wiki/wave_fiveh_ticketed_writes_contract.md`, freeze ACCEPT
`wiki/wave_fiveh_freeze_independent_review.md`, prior product-ready ACCEPT
`wiki/wave_fiveh_product_ready_research_independent_review.md`, and root handoff
record commit **`e75cdfb`**. Full cited findings live outside the public
repository at `.fractal/main.billy_complete/tmp/grok-review.md`.

## Exact reviewed scope

This ACCEPT covers only the cited handoff that restates Codex Power product work
for the three singular API v2 CUD operations already frozen:

| Inventory id | Preview tool | Execute tool | HTTP | Request root | Response roots |
| --- | --- | --- | --- | --- | --- |
| `api.attachments.create` | `api_attachments_create_preview` | `api_attachments_create_execute` | `POST /attachments` | `attachment` | `attachments` |
| `api.attachments.update` | `api_attachments_update_preview` | `api_attachments_update_execute` | `PUT /attachments/:id` | `attachment` | `attachments` |
| `api.attachments.delete` | `api_attachments_delete_preview` | `api_attachments_delete_execute` | `DELETE /attachments/:id` | id binding | `attachments` + optional deleted meta |

Independent re-fetch of [official Billy API documentation](https://www.billy.dk/api/)
on 2026-07-29 returned HTTP 200, ETag `"hsisik4g9p3603"`, 147934 bytes, MD5
`c2efda0ee4cf9cf200e14910c5fc6996` — matching `coverage/status.json` and the
research36 snapshot. The
[`/v2/attachments`](https://www.billy.dk/api/#v2attachments) table still lists
singular create, update, and delete plus ambiguous bulk support without a bulk
body contract.

Research arithmetic and planned file ownership match the freeze:

- Registry **202 → 208** `api_*` tools after product.
- Offline coverage **148 → 151** after real suites only.
- Suggested module `src/billy_mcp/api/attachment_writes.py` and tests
  `tests/api/test_attachment_writes.py` plus cross-executor coverage, cloning
  sales-tax write patterns.
- Specs: `collection_path="/attachments"`, `singular_root="attachment"`,
  `plural_root="attachments"`, `additional_plural_roots=()`.
- Opaque inner payload; `priority` only clear mutable candidate; no invented
  owner encoding; no binary `/files` special; no bulk tools.

Unauthenticated method probes reconfirmed by the reviewer: attachments POST/PUT
return **401**; missing-id DELETE returns **200** (not cleanup proof); files
valid JSON may **401** and invalid JSON **400** `INVALID_JSON` — none of which
authorise greening files create.

## Product gate

This ACCEPT is a **compatible refresh** of the already-open offline product
gate (freeze ACCEPT + product-ready research ACCEPT). It does not accept
implementation, live qualification, browser/UI parity, vision verification,
bulk operations, special routes, or overall completeness.

At review time root still lacks `attachment_writes.py`; only
`api_attachments_get` and `api_attachments_list` are registered among
attachment tools; registry remains **202**; coverage remains **148**
implemented/contract_tested with live and vision **0**.

After product integrates at root, a separate independent Grok product review
must confirm registry **208**, coverage **151** offline with the three
attachment CUD rows greened only by real suites, ticket binding and replay
boundaries, no fabricated `files` multi-root, and fail-closed live/UI/bulk.

No browser was launched, no credential or customer data was used, and no raw
browser evidence is retained. Coverage remains 148/148/0/0 with
`complete: false` until product and tests land.
