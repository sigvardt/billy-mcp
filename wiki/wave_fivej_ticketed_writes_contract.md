---
name: wave_fivej_ticketed_writes_contract
title: Wave-5j bank-line ticketed-write contract
desc: Cited offline contract for singular bank-line match, line, and subject-association ticketed writes, accepted by independent Grok freeze review.
tags: [billy, api, bank, writes, coverage]
sources:
  - https://www.billy.dk/api/
  - wiki/wave_fivej_freeze_ready_research_independent_review.md
  - wiki/offline_write_probe_rules.md
  - wiki/wave_fivei_ticketed_writes_contract.md
  - coverage/api_v2_manifest.yaml
  - coverage/status.json
  - docs/superpowers/specs/2026-07-28-billy-mcp-complete-design.md
created: 2026-07-30T01:29:01Z
updated: 2026-07-30T01:29:01Z
---

# Wave-5j bank-line ticketed-write contract

## Authority and gate

This is the frozen offline-only implementation contract for the nine documented
singular Billy API v2 CUD rows for `bankLineMatches`, `bankLines`, and
`bankLineSubjectAssociations`. It derives from the cited official API page,
re-fetched with ETag `hsisik4g9p3603`, MD5
`c2efda0ee4cf9cf200e14910c5fc6996`, and an unchanged 147934-byte body. The
locked API base is `https://api.billysbilling.com/v2`. The complete cited
research and unauthenticated-probe record remains outside this repository in
the parent scratch handoff.

The authoring gate is the ACCEPT recorded in
`wiki/wave_fivej_freeze_ready_research_independent_review.md`. That acceptance
opens only this offline freeze-page authoring step. It is not acceptance of
product implementation, live qualification, browser/UI parity, vision
verification, bulk operations, special routes, or overall completeness. This
page itself requires a later independent freeze review before any product leaf.

## Exact inventory and tool surface

| Inventory id | Preview tool | Execute tool | HTTP request | Request root | Response-root policy |
| --- | --- | --- | --- | --- | --- |
| `api.bankLineMatches.create` | `api_bank_line_matches_create_preview` | `api_bank_line_matches_create_execute` | `POST /bankLineMatches` | `bankLineMatch` | `bankLineMatches`; optionally map `bankLines` and `bankLineSubjectAssociations` when returned |
| `api.bankLineMatches.update` | `api_bank_line_matches_update_preview` | `api_bank_line_matches_update_execute` | `PUT /bankLineMatches/:id` | `bankLineMatch` | `bankLineMatches`; optionally map `bankLines` and `bankLineSubjectAssociations` when returned |
| `api.bankLineMatches.delete` | `api_bank_line_matches_delete_preview` | `api_bank_line_matches_delete_execute` | `DELETE /bankLineMatches/:id` | id binding only; bodyless | `bankLineMatches` and related plural roots only when returned; optional deleted metadata only when present |
| `api.bankLines.create` | `api_bank_lines_create_preview` | `api_bank_lines_create_execute` | `POST /bankLines` | `bankLine` | `bankLines`; no additional plural roots are invented |
| `api.bankLines.update` | `api_bank_lines_update_preview` | `api_bank_lines_update_execute` | `PUT /bankLines/:id` | `bankLine` | `bankLines`; no additional plural roots are invented |
| `api.bankLines.delete` | `api_bank_lines_delete_preview` | `api_bank_lines_delete_execute` | `DELETE /bankLines/:id` | id binding only; bodyless | `bankLines`; optional deleted metadata only when present, with no invented parent root |
| `api.bankLineSubjectAssociations.create` | `api_bank_line_subject_associations_create_preview` | `api_bank_line_subject_associations_create_execute` | `POST /bankLineSubjectAssociations` | `bankLineSubjectAssociation` | `bankLineSubjectAssociations`; no additional plural roots are invented |
| `api.bankLineSubjectAssociations.update` | `api_bank_line_subject_associations_update_preview` | `api_bank_line_subject_associations_update_execute` | `PUT /bankLineSubjectAssociations/:id` | `bankLineSubjectAssociation` | `bankLineSubjectAssociations`; no additional plural roots are invented |
| `api.bankLineSubjectAssociations.delete` | `api_bank_line_subject_associations_delete_preview` | `api_bank_line_subject_associations_delete_execute` | `DELETE /bankLineSubjectAssociations/:id` | id binding only; bodyless | `bankLineSubjectAssociations`; optional deleted metadata only when present, with no invented parent root |

Each inventory row is one API operation: its `tool_name` is the preview tool;
the execute twin is registered later but is not a second coverage row. All nine
rows remain `implemented: false`, `contract_tested: false`, and
`live_tested: false` until a later product leaf provides code and real tests.
This freeze does not change coverage, tool registration, or status.

## Shared write protocol

- Requests use only the locked base and the client-relative paths above; no
  client path repeats `/v2`.
- Create and update requests contain exactly one stated singular root. Updates
  are partial `PUT` requests, and an inner `id`, when supplied, must equal the
  route id. Deletes have no body and bind the canonical request `{"id": "…"}`.
- A preview is non-mutating and yields a short-lived, exact, single-use
  confirmation ticket bound to the tool, organisation, target, canonical
  request, and expected effect. Execute accepts only `confirmation_ticket`;
  it accepts neither an approval boolean nor replacement business fields.
- All operations use the root's one shared `ConfirmationStore` and
  `WriteProtocolService`. A `WriteOperationSpec` carries the exact non-empty,
  server-owned execute-tool name. A mismatched handler/tool binding fails with
  `CONFIRMATION_MISMATCH` before ticket consumption and before HTTP.
- An execution makes one write request only: prepared writes are discarded and
  never retried.
- Outer inputs forbid undeclared fields. The three inner singular payload maps
  remain opaque offline so this contract does not hard-code relation wire
  shapes, undocumented enum members, or unproven mutability.

For non-delete success, the primary plural root is required. Match operations
may additionally map `bankLines` and `bankLineSubjectAssociations` only when a
real response contains them. The line and association operations set no
additional plural roots. Delete handlers may surface deleted metadata only when
the service actually returns it; they must not fabricate records or metadata.

## Bank-line match boundaries

The official `/v2/bankLineMatches` table documents the following boundaries;
they constrain the later product without turning opaque inner payloads into a
published field schema.

| Property | Documentation boundary | Offline treatment |
| --- | --- | --- |
| `account`, `feeAccount` | required immutable belongs-to relations | Keep their wire forms opaque. |
| `differenceType`, `side` | immutable enums whose allowed values are not published | Do not invent enum members. |
| `entryDate`, `amount` | immutable scalar fields | Preserve as opaque payload values. |
| `isApproved` | no immutable or readonly marker | A candidate for later authenticated partial-update proof. |
| `approvedTime` | readonly | Do not require it on create or update. |
| `lines`, `subjectAssociations` | description says set values replace existing children; Notes say readonly | Keep embed keys opaque; require authenticated proof before claiming embed support, replacement, cascade, or child response roots. |

The replace-on-set text and readonly Notes are intentionally unresolved. They
are the only basis for the match family's optional child-root mapping; neither
an embed-only tool nor an embed-tested behavior is frozen here.

## Bank-line boundaries

`/v2/bankLines` documents required `match`, `account`, `entryDate`,
`description`, `amount`, and `side` properties. The relation serialisations and
all inner shapes remain opaque. In particular, the required `side` enum has no
published values, and the copied wording in the `account` description is not a
reason to reinterpret the field. `description` is a candidate for later
authenticated partial-update proof, not a current update guarantee. This child
resource has no documented has-many response entitlement, so it must not map a
parent `bankLineMatches` root unless live evidence later proves one.

## Bank-line subject-association boundaries

`/v2/bankLineSubjectAssociations` documents required `match` and `subject`
relations. Both remain opaque. `subject` is a belongs-to-reference relation,
but its request field name and wire form are unproven for this resource; in
particular, the later product must not require a `subjectReference` shape by
analogy. No parent or sibling plural root is authorised for association writes
without live response evidence.

## Bulk status, probes, and safety limits

The three resource Supports tables mention bulk save and bulk delete but do not
publish a bulk request body, response body, or partial-failure contract. Every
such bulk row remains `ambiguous_bulk` with an empty tool name. This contract
authorises no bulk tool.

Unauthenticated probes against the locked base returned 401 for POST and PUT
on each of the three collections. DELETE using a missing id returned 200 for
each collection. The latter is compatible with an idempotent-delete narrative,
but is neither cleanup proof nor live qualification. These probes establish no
valid create payload, mutation result, response envelope, authenticated delete,
or organisation cleanup behavior.

`bankPayments` singular DELETE returned 405 and is excluded from this cohort;
that result overrides optimistic interpretation of its Supports entry. The
separate `balanceModifiers` CUD surface is likewise not authorised by this
freeze.

## Required later offline product evidence

Before any of these rows can become implemented or contract-tested, a later
product must provide real offline suites proving:

- strict flat outer inputs, opaque inner-payload preservation, exact methods,
  client-relative paths, singular request roots, partial-update id equality,
  and bodyless deletes;
- non-mutating previews plus ticket expiry, tamper, replay, wrong
  organisation, target, payload, and expected-effect failures;
- same-resource and cross-resource executor-binding mismatch rejection before
  ticket consumption and before HTTP through the root's single shared store;
- primary-root response mapping, match-only optional child-root mapping, no
  fabricated child-resource roots, and deleted metadata only when present; and
- exactly one request per execution with no write retry.

Those are later product targets only: 238 `api_*` tools, 166 implemented and
contract-tested offline API rows, 43 clear red CUD rows, and
`coverage/status.json` still `complete: false`. Live evidence remains absent;
UI and vision rows, ambiguous bulk rows, and overall completeness are not
advanced by this contract.

## Exclusions

This freeze excludes bulk save/delete; all `bankPayments` work (including its
405 singular DELETE); `balanceModifiers`; binary `files` specials; webhooks;
generic HTTP or browser controls; live qualification; browser/UI parity; and
vision verification. It creates no credential, persistent organisation record,
UI artifact, or completeness claim.
