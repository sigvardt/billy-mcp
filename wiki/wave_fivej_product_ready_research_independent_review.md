---
name: wave_fivej_product_ready_research_independent_review
title: Wave-5j product-ready research independent review ACCEPT
desc: Authoritative root Grok acceptance of the cited offline product-ready handoff for singular bank-line match, line, and subject-association ticketed writes under the accepted Wave-5j freeze.
tags: [billy, api, bank, writes, review, coverage, research]
sources:
  - https://www.billy.dk/api/
  - wiki/wave_fivej_ticketed_writes_contract.md
  - wiki/wave_fivej_freeze_independent_review.md
  - coverage/api_v2_manifest.yaml
  - coverage/status.json
  - docs/superpowers/specs/2026-07-28-billy-mcp-complete-design.md
created: 2026-07-30T02:07:00Z
updated: 2026-07-30T02:07:00Z
---

# Wave-5j product-ready research independent review ACCEPT

## Verdict

| Claim | Result |
| --- | --- |
| Wave-5j product-ready research handoff | **ACCEPT** offline as implementation handoff only |
| Official documentation versus maintained inventory | **PASS** |
| Research versus accepted freeze tool/path/root map | **PASS** |
| Coverage honesty before product | **PASS** |
| Wave-5j product implementation | **not accepted** — separate Grok review required after root integration |
| Live, UI, vision, bulk, and completeness | **not claimed / fail-closed** |

The authoritative root `INDEPENDENT-REVIEW` Grok step accepted the product-ready
research at scratch `.fractal/main.billy_complete/tmp/grok-research.md`
(research43) against freeze page `wiki/wave_fivej_ticketed_writes_contract.md`,
freeze ACCEPT `wiki/wave_fivej_freeze_independent_review.md`, and root HEAD
**`5b6d2a9`**. Full cited findings live outside the public repository at
`.fractal/main.billy_complete/tmp/grok-review.md`.

## Exact reviewed scope

This ACCEPT covers only the cited handoff that opens Codex Power product work
for the nine singular API v2 CUD operations already frozen:

| Inventory id | Preview tool | Execute tool | HTTP | Request root | Response roots |
| --- | --- | --- | --- | --- | --- |
| `api.bankLineMatches.create` | `api_bank_line_matches_create_preview` | `api_bank_line_matches_create_execute` | `POST /bankLineMatches` | `bankLineMatch` | `bankLineMatches` + optional `bankLines`, `bankLineSubjectAssociations` |
| `api.bankLineMatches.update` | `api_bank_line_matches_update_preview` | `api_bank_line_matches_update_execute` | `PUT /bankLineMatches/:id` | `bankLineMatch` | same |
| `api.bankLineMatches.delete` | `api_bank_line_matches_delete_preview` | `api_bank_line_matches_delete_execute` | `DELETE /bankLineMatches/:id` | id binding | `bankLineMatches` + optional deleted meta |
| `api.bankLines.create` | `api_bank_lines_create_preview` | `api_bank_lines_create_execute` | `POST /bankLines` | `bankLine` | `bankLines` |
| `api.bankLines.update` | `api_bank_lines_update_preview` | `api_bank_lines_update_execute` | `PUT /bankLines/:id` | `bankLine` | `bankLines` |
| `api.bankLines.delete` | `api_bank_lines_delete_preview` | `api_bank_lines_delete_execute` | `DELETE /bankLines/:id` | id binding | `bankLines` + optional deleted meta |
| `api.bankLineSubjectAssociations.create` | `api_bank_line_subject_associations_create_preview` | `api_bank_line_subject_associations_create_execute` | `POST /bankLineSubjectAssociations` | `bankLineSubjectAssociation` | associations only |
| `api.bankLineSubjectAssociations.update` | `api_bank_line_subject_associations_update_preview` | `api_bank_line_subject_associations_update_execute` | `PUT /bankLineSubjectAssociations/:id` | `bankLineSubjectAssociation` | associations only |
| `api.bankLineSubjectAssociations.delete` | `api_bank_line_subject_associations_delete_preview` | `api_bank_line_subject_associations_delete_execute` | `DELETE /bankLineSubjectAssociations/:id` | id binding | associations + optional deleted meta |

Research arithmetic and file ownership match the freeze:

- Registry **220 → 238** `api_*` tools after product.
- Offline coverage **157 → 166** after real suites only.
- Suggested module `src/billy_mcp/api/bank_line_writes.py` and tests
  `tests/api/test_bank_line_writes.py` plus
  `tests/api/test_bank_line_cross_executor.py`.
- Match specs: `collection_path="/bankLineMatches"`,
  `singular_root="bankLineMatch"`, `plural_root="bankLineMatches"`, optional
  `additional_plural_roots=("bankLines", "bankLineSubjectAssociations")`.
- Line specs: `collection_path="/bankLines"`, `singular_root="bankLine"`,
  `plural_root="bankLines"`, `additional_plural_roots=()`.
- Association specs: `collection_path="/bankLineSubjectAssociations"`,
  `singular_root="bankLineSubjectAssociation"`,
  `plural_root="bankLineSubjectAssociations"`, `additional_plural_roots=()`.
- Opaque inner payloads. Do not invent `side` or `differenceType` enum values.
  Do not force association `subject` wire form. Keep match embed A1 unresolved
  offline. Do not expand `bank_reads.py`. No bulk tools. No bankPayments.

## Product gate

This ACCEPT, together with
`wiki/wave_fivej_freeze_independent_review.md`, opens offline Codex Power
product implementation for the eighteen ticketed tools. It is not product
ACCEPT, live qualification, UI/vision acceptance, bulk resolution, or
completeness.

After product integrates at root, a separate independent Grok product review
must confirm registry **238**, coverage **166** offline with the nine bank-line
CUD rows greened only by real suites, ticket binding and replay boundaries,
match-only optional child roots, empty additional roots for line/association
writes, and fail-closed live/UI/bulk state.

No browser was launched, no credential or customer data was used, and no raw
browser evidence is retained. Coverage remains 157/157/0/0 with
`complete: false` until product and tests land.
