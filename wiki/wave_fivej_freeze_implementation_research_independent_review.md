---
name: wave_fivej_freeze_implementation_research_independent_review
title: Wave-5j freeze-implementation research independent Grok review ACCEPT
desc: Independent Grok acceptance of the cited offline freeze-implementation research handoff for singular bank-line match, line, and subject-association ticketed writes.
tags: [billy, api, bank, writes, review, research]
sources:
  - https://www.billy.dk/api/
  - wiki/wave_fivej_freeze_ready_research_independent_review.md
  - wiki/offline_write_probe_rules.md
  - coverage/api_v2_manifest.yaml
  - coverage/status.json
  - docs/superpowers/specs/2026-07-28-billy-mcp-complete-design.md
created: 2026-07-30T01:26:00Z
updated: 2026-07-30T01:26:00Z
---

# Wave-5j freeze-implementation research independent Grok review ACCEPT

## Verdict and authority

**ACCEPT — freeze-implementation research handoff only** for the nine clear
singular Billy API v2 CUD operations on `bankLineMatches`, `bankLines`, and
`bankLineSubjectAssociations`.

The cited research lives outside the public repository at
`.fractal/main.billy_complete/tmp/grok-research.md` (research41). Full review
findings: `.fractal/main.billy_complete/tmp/grok-review.md`.

This ACCEPT deepens the freeze-ready ACCEPT in
`wiki/wave_fivej_freeze_ready_research_independent_review.md`. Together they
open only the offline freeze-page authoring gate. This is **not** acceptance of
a freeze contract page, product tools, coverage greens, bulk tools,
`bankPayments` work, live qualification, UI parity, vision, or overall
completeness.

No production code or coverage flags were changed in this review. Official
documentation was re-fetched at ETag `hsisik4g9p3603`, content-length 147934
bytes, MD5 `c2efda0ee4cf9cf200e14910c5fc6996`, matching `coverage/status.json`
and research41.

## Accepted research scope

Nine inventory rows / planned eighteen ticketed tools (preview + execute), with
inventory preview names verified:

| Inventory id | Planned preview tool | HTTP |
| --- | --- | --- |
| `api.bankLineMatches.create` | `api_bank_line_matches_create_preview` | `POST /bankLineMatches` |
| `api.bankLineMatches.update` | `api_bank_line_matches_update_preview` | `PUT /bankLineMatches/:id` |
| `api.bankLineMatches.delete` | `api_bank_line_matches_delete_preview` | `DELETE /bankLineMatches/:id` |
| `api.bankLines.create` | `api_bank_lines_create_preview` | `POST /bankLines` |
| `api.bankLines.update` | `api_bank_lines_update_preview` | `PUT /bankLines/:id` |
| `api.bankLines.delete` | `api_bank_lines_delete_preview` | `DELETE /bankLines/:id` |
| `api.bankLineSubjectAssociations.create` | `api_bank_line_subject_associations_create_preview` | `POST /bankLineSubjectAssociations` |
| `api.bankLineSubjectAssociations.update` | `api_bank_line_subject_associations_update_preview` | `PUT /bankLineSubjectAssociations/:id` |
| `api.bankLineSubjectAssociations.delete` | `api_bank_line_subject_associations_delete_preview` | `DELETE /bankLineSubjectAssociations/:id` |

Verified independently against the official page, inventory, and unauth probes:

- Supports tables list singular create, update, and delete for all three
  resources; bulk save/delete remain without body contracts and stay
  empty-tool `ambiguous_bulk`.
- Unauthenticated probes reconfirm POST/PUT **401** and DELETE-missing-id
  **200** for the three bank-line resources; DELETE **200** is not cleanup
  proof.
- `bankPayments` singular DELETE remains **405** and is correctly excluded.
- Field boundaries require opaque offline inners: unpublished `side` /
  `differenceType` enums; `subject` belongs-to-reference wire form unproven;
  match has-many `lines` / `subjectAssociations` document replace-on-set while
  Notes say readonly (live must prove embed).
- Match writes may declare optional additional plural roots
  `bankLines` and `bankLineSubjectAssociations`; child resources keep empty
  additional roots offline.
- Research correctly keeps all nine CUD rows red and does not author product
  modules.

## Explicit non-acceptance

- No Wave-5j freeze contract page is accepted here (`wiki/wave_fivej_ticketed_writes_contract.md` is still missing on root after child `wave5j_freeze_contract` exited without a deliverable).
- No bank-line product implementation or registry tools.
- No coverage greens for the nine CUD rows or any bulk row.
- No `bankPayments` create/update/delete product claim.
- No live, UI, vision, or completeness claim.

## Next gate after this ACCEPT

Codex Power must deliver `wiki/wave_fivej_ticketed_writes_contract.md` from
research41 and the freeze-ready ACCEPT. That freeze then requires its own
independent Grok freeze review before any product leaf.
