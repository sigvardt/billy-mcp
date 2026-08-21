---
name: wave_fiveq_ticketed_writes_contract
title: Wave-5q users update ticketed writes contract
desc: Cited wiki-only offline contract freezing singular users update; create, delete, bulk, product, live, UI, and completeness remain excluded.
tags: [billy, api, users, writes, ticketed, offline]
sources:
  - https://www.billy.dk/api/
  - https://api.billysbilling.com/v2
  - wiki/wave_fiveq_users_freeze_ready_research.md
  - wiki/offline_write_probe_rules.md
  - wiki/wave_fivep_ticketed_writes_contract.md
  - docs/superpowers/specs/2026-07-28-billy-mcp-complete-design.md
created: 2026-07-30T12:38:29Z
updated: 2026-07-30T12:38:29Z
---

# Wave-5q users update ticketed writes contract

## Scope, evidence, and authority boundary

This is a **wiki-only offline freeze contract** for exactly one future Billy
API inventory operation: singular `api.users.update`. It declares only the two
future tools in the table below. It authorises no source implementation, server
registration, contract test, coverage or status change, inventory greening, or
product leaf.

The evidence is Grok Research70 in
[[wave_fiveq_users_freeze_ready_research]], which cites the [official Billy API
documentation](https://www.billy.dk/api/) fetched on 2026-07-30 (HTTP 200, ETag
`wcw4x9hqvu3603`, 147934 bytes, MD5
`8b94b0135c91fd15fe54ea33e088a4be`). The cited research records the locked API
base `https://api.billysbilling.com/v2`; paths in this page are client-relative
and omit `/v2`. Its prior inventory-lock fingerprint (ETag `hsisik4g9p3603`,
MD5 `c2efda0ee4cf9cf200e14910c5fc6996`) differs only through documented
access/CDN metadata drift, not the users Supports or property table.

The following authorities are separate and none may be inferred from another:

| Stage | Authority and status |
| --- | --- |
| Research | Research70 supplies cited official-doc and unauthenticated method-gate evidence only. It is not this freeze, independent acceptance, product work, or qualification. |
| This freeze | This page freezes the future offline contract only. Writing it is **not** independent freeze ACCEPT. |
| Independent freeze review | A later parent-owned **Grok** review must independently ACCEPT this page before any users product implementation. |
| Product and testing | A later, separately authorised users product leaf may implement/register the two tools and contract-test them only after that ACCEPT. None is created or evidenced here. |
| Live qualification | Separate authenticated non-production evidence is required. The unauthenticated gates and this page provide none. |
| UI and vision | Separate UI, DOM/read-back, and vision evidence is required; none is provided here. |
| Completeness | No completeness claim or coverage green follows from research, this freeze, a future test, or a later live/UI result. |

## Exact frozen surface

| Inventory id | Future preview tool | Future execute tool | Client-relative request | Required success root |
| --- | --- | --- | --- | --- |
| `api.users.update` | `api_users_update_preview` | `api_users_update_execute` | `PUT /users/:id` | `users` |

This is one inventory operation. The execute twin does not create another
inventory row. These are the **only** future tool names declared by this
contract, and no tool is implemented or registered by it.

## Future input, request, and response contract

The future preview input is exactly `{id: non-empty string, user: map}` under a
strict outer model: undeclared outer fields are forbidden. `id` is the required
non-empty path identifier for `PUT /users/:id`.

The inner `user` is an opaque `dict[str, JsonValue]`, not a generic HTTP
control and not a field-level user schema. If `user.id` is supplied, it must
equal the path `id`; an absent inner `user.id` is not invented as a required
field. This contract defines no additional required field, password, invite,
MFA, relation-wire form, `*Id` alias, enum value, date/number encoding, or
update-payload sample.

Future response mapping requires only the `users` root. This freeze specifies
no response metadata shape, record shape, extra root, or other response
extension.

## Shared confirmation-ticket protocol

- Preview is non-mutating. It validates the strict outer boundary, selects or
  confirms the Billy organization through the shared protocol, canonicalizes
  the request, describes the expected effect, and issues a single-use
  confirmation ticket lasting at most five minutes.
- Each ticket is bound to the exact `api_users_update_execute` tool, Billy
  organization, target path `id`, canonical request, and expected effect.
- Execute accepts only `{confirmation_ticket: non-empty string}`. It accepts no
  business payload, replacement target id, second preview input, or caller
  approval boolean.
- Execute validates and consumes the bound ticket, restores its request, makes
  exactly one HTTP write, and never retries that write.
- Missing, invalid, expired, consumed, or mismatched tickets—including a
  mismatch of execute tool, organization, target id, canonical request, or
  expected effect—must fail closed. A changed bound value requires a new
  preview and ticket.

Future implementation must use the shared confirmation protocol rather than
creating a separate approval mechanism. Confirmation tickets and sensitive user
values are not log or storage material.

## Official property boundaries and sensitivity

Research70 records that the official `/v2/users` Supports list get by id, list,
**update**, bulk save, and bulk delete. It omits create and singular delete.
The official property table is a boundary for the opaque inner map; it is not a
validated writable-field list or permission to change any listed value.

`email` and `phone` are PII. `isStaff`, `isSupporter`, and `isAdmin` are
high-privilege flags. Future implementation, test, and review must treat all
five values as sensitive and redact them from logs and stored artifacts. This
freeze does **not** claim that any privilege flag is safe to mutate. It also
does not turn the cited properties—such as readonly `createdTime`,
`profilePicFile`, `profilePicUrl`, and `profilePic48Url`—into request fields or
an allowlist of mutable fields.

## Method gates, bulk, cleanup, and exclusions

Research70's unauthenticated, non-mutating probes used JSON body `{}`. They
establish these gates:

| Method and client-relative path | Result | Contract consequence |
| --- | --- | --- |
| `PUT /users/:id` | 401 `AUTHENTICATION_REQUIRED` | Opens only this offline singular-update freeze; it proves neither an accepted payload nor a mutation, response, or live qualification. |
| `POST /users` | 405 `METHOD_NOT_ALLOWED` | Create is closed and excluded. |
| `DELETE /users/:id` | 405 `METHOD_NOT_ALLOWED` | Singular delete is closed and excluded. |

No bulk operation is frozen. The official page supplies no bulk request or
response body contract, so bulk save and bulk delete remain excluded, empty
tool surface, and red. There is no webhook evidence for users (the cited
official page has no webhook mention). Update restoration and every cleanup
strategy remain unproven; this page does not qualify live cleanup.

This freeze explicitly excludes create, singular delete, every bulk operation,
webhooks, generic HTTP and browser controls, credentials, password/invite/MFA
behaviour, relation wiring, field-level payload validation, enum values,
payload samples, source implementation, server registration, contract tests,
coverage or status changes, inventory greening, live work, UI/vision work,
cleanup qualification, and completeness claims. It is neither independent
freeze ACCEPT nor authority for a users product leaf.
