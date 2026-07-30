---
name: wave_fivej_freeze_independent_review
title: Wave-5j contract freeze independent review ACCEPT
desc: Authoritative root Grok acceptance of the cited offline contract for singular bank-line match, line, and subject-association ticketed writes.
tags: [billy, api, bank, writes, review, coverage]
sources:
  - https://www.billy.dk/api/
  - wiki/wave_fivej_ticketed_writes_contract.md
  - wiki/wave_fivej_freeze_ready_research_independent_review.md
  - wiki/wave_fivej_freeze_implementation_research_independent_review.md
  - wiki/wave_fivei_ticketed_writes_contract.md
  - wiki/offline_write_probe_rules.md
  - coverage/api_v2_manifest.yaml
  - coverage/status.json
  - docs/superpowers/specs/2026-07-28-billy-mcp-complete-design.md
created: 2026-07-30T01:46:00Z
updated: 2026-07-30T01:46:00Z
---

# Wave-5j contract freeze independent review ACCEPT

## Verdict

| Claim | Result |
| --- | --- |
| Wave-5j cited contract freeze | **ACCEPT** |
| Official documentation versus maintained inventory | **PASS** |
| Freeze versus exact nine-row tool/path/root map | **PASS** |
| Coverage honesty before product integration | **PASS** |
| Wave-5j product implementation | **not accepted** — separate Grok review required after root integration |
| Live, UI, vision, bulk, and completeness | **not claimed / fail-closed** |

The authoritative root `INDEPENDENT-REVIEW` Grok step accepted the freeze page at
root merge **`0db66d0`** (`wiki/wave_fivej_ticketed_writes_contract.md`, leaf
commit `8272e83`). Full cited findings live outside the public repository at
`.fractal/main.billy_complete/tmp/grok-review.md`.

Any dedicated freeze-review child that exits without a durable wiki ACCEPT does
not replace this page. This root review is the authoritative freeze gate.

## Exact reviewed scope

The accepted contract freezes exactly nine singular API v2 JSON CUD operations
(eighteen ticketed tools: nine preview + nine execute):

| Inventory id | Method and client path | Singular request root | Response roots (offline) |
| --- | --- | --- | --- |
| `api.bankLineMatches.create` | `POST /bankLineMatches` | `bankLineMatch` | `bankLineMatches`; optional `bankLines`, `bankLineSubjectAssociations` when returned |
| `api.bankLineMatches.update` | `PUT /bankLineMatches/:id` | `bankLineMatch` | same |
| `api.bankLineMatches.delete` | `DELETE /bankLineMatches/:id` | bodyless id binding | `bankLineMatches` and related roots only when returned; optional deleted metadata |
| `api.bankLines.create` | `POST /bankLines` | `bankLine` | `bankLines` only |
| `api.bankLines.update` | `PUT /bankLines/:id` | `bankLine` | `bankLines` only |
| `api.bankLines.delete` | `DELETE /bankLines/:id` | bodyless id binding | `bankLines`; optional deleted metadata |
| `api.bankLineSubjectAssociations.create` | `POST /bankLineSubjectAssociations` | `bankLineSubjectAssociation` | associations only |
| `api.bankLineSubjectAssociations.update` | `PUT /bankLineSubjectAssociations/:id` | `bankLineSubjectAssociation` | associations only |
| `api.bankLineSubjectAssociations.delete` | `DELETE /bankLineSubjectAssociations/:id` | bodyless id binding | associations; optional deleted metadata |

The accepted contract preserves the locked
`https://api.billysbilling.com/v2` base, client-relative paths without a
duplicated `/v2`, opaque inner bank-line payloads, strict outer inputs, partial
`PUT`, update-id equality, and bodyless deletes. It requires the root shared
`ConfirmationStore` and `WriteProtocolService`, exact server-owned
executor-name ticket binding, single-use short-lived tickets, and no write
retry.

Spec constants implied by the freeze:

- Matches: `collection_path="/bankLineMatches"`, `singular_root="bankLineMatch"`, `plural_root="bankLineMatches"`, and `additional_plural_roots=("bankLines", "bankLineSubjectAssociations")` that are optional when present.
- Lines: `collection_path="/bankLines"`, `singular_root="bankLine"`, `plural_root="bankLines"`, `additional_plural_roots=()`.
- Subject associations: `collection_path="/bankLineSubjectAssociations"`, `singular_root="bankLineSubjectAssociation"`, `plural_root="bankLineSubjectAssociations"`, `additional_plural_roots=()`.

Official field notes match the freeze: match immutables and unpublished
`side` / `differenceType` enums stay opaque; match `lines` /
`subjectAssociations` retain the replace-on-set versus Notes-readonly
ambiguity without an embed-only tool; line and association child writes invent
no parent roots offline; association `subject` belongs-to-reference wire form
stays unproven.

Bulk save and bulk delete remain `ambiguous_bulk` with empty `tool_name`. The
freeze invents no bulk body, webhook, file upload, `bankPayments` product
(including the 405 singular DELETE), `balanceModifiers` CUD, UI tool, or live
claim. Product must land in a new module such as `bank_line_writes.py` and must
not expand `bank_reads.py` into writes.

## Recheck and product gate

Official documentation was re-fetched during review with ETag
`hsisik4g9p3603`, body length 147934, and MD5
`c2efda0ee4cf9cf200e14910c5fc6996`, matching `coverage/status.json` with no
source drift. Unauthenticated probes returned 401 for POST and PUT on all three
bank-line collections and 200 for missing-id DELETE, which the freeze correctly
refuses to treat as cleanup proof. `bankPayments` singular DELETE returned 405
`METHOD_NOT_ALLOWED`. Coverage at freeze review remains 157 implemented, 157
contract-tested, 0 live, 0 vision, and `complete: false`. No
`bank_line_writes` module exists. The nine CUD inventory rows stay red.
Registry remains 220 `api_*` tools.

This ACCEPT opens offline product implementation for the eighteen ticketed
bank-line write tools. It is not a product ACCEPT. After the product is
integrated at root, a separate independent Grok product review must inspect
exact routes, opaque payload discipline, ticket binding and replay boundaries,
registry target **238** `api_*` tools, coverage target **166** offline rows
with the nine bank-line CUD rows contract-tested only by real suites, and
fail-closed live/UI/bulk state.

No browser was launched, no credential or customer data was used, and no raw
browser evidence is retained. The acceptance remains an offline contract
decision only.
