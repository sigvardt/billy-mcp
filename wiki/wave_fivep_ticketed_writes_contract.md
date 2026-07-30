---
name: wave_fivep_ticketed_writes_contract
title: Wave-5p organizations ticketed writes contract
desc: Cited wiki-only offline contract freezing singular organizations create and update ticketed writes; delete and bulk remain excluded.
tags: [billy, api, organizations, writes, ticketed, offline]
sources:
  - https://www.billy.dk/api/
  - https://api.billysbilling.com/v2
  - wiki/wave_fivep_candidate_write_research.md
  - wiki/offline_write_probe_rules.md
  - wiki/wave_fiveo_ticketed_writes_contract.md
  - docs/superpowers/specs/2026-07-28-billy-mcp-complete-design.md
created: 2026-07-30T11:28:27Z
updated: 2026-07-30T11:28:27Z
---

# Wave-5p organizations ticketed writes contract

## Scope, evidence, and authority boundary

This is a **wiki-only offline freeze contract** for exactly two singular Billy
API operations: organizations create and organizations update. It declares the
four future API tools in the table below and authorises no other future tool.
It authorises no source implementation, server registration, test, coverage or
status change, or inventory greening.

The evidence is the Grok research67 candidate record
[[wave_fivep_candidate_write_research]], which cited the [official Billy API
documentation](https://www.billy.dk/api/) fetched on 2026-07-30 (HTTP 200,
ETag `wcw4x9hqvu3603`, 147934 bytes, MD5
`8b94b0135c91fd15fe54ea33e088a4be`). The client base stays locked to
`https://api.billysbilling.com/v2`; paths in this page are client-relative and
therefore omit `/v2`. [[offline_write_probe_rules]] and
[[wave_fiveo_ticketed_writes_contract]] are protocol precedents, not additional
write authority.

The following stages are deliberately separate:

| Stage | Status and meaning |
| --- | --- |
| Research | The cited Grok record supplies official-doc and unauthenticated method-gate evidence only. It is not this freeze, product authority, a test, or qualification. |
| This freeze page | Freezes the future offline contract only. Authoring it is **not** independent freeze ACCEPT. |
| Independent freeze ACCEPT | A separate parent-owned **Grok** review must ACCEPT this page before any organizations product work. |
| Product implementation and contract testing | Later work may implement/register the four tools and run contract tests only after that ACCEPT; neither exists or is evidenced here. |
| Live testing | Requires separate authenticated non-production evidence; it is not established by the unauthenticated gates or this page. |
| UI/vision verification | Separate headless UI, DOM/read-back, and vision work; all remain out of scope and red. |
| Completeness | No completeness claim follows from research, this contract, any future contract test, or a later live/UI result. |

## Exact frozen surface

| Inventory id | Preview tool | Execute tool | Client-relative request | Required success root |
| --- | --- | --- | --- | --- |
| `api.organizations.create` | `api_organizations_create_preview` | `api_organizations_create_execute` | `POST /organizations`; outer `{organization: map}` | `organizations` |
| `api.organizations.update` | `api_organizations_update_preview` | `api_organizations_update_execute` | `PUT /organizations/:id`; outer `{id, organization: map}` | `organizations` |

These four names are the **only** future tools declared by this contract. Each
inventory row is one operation; its execute twin does not create another
inventory row. No tool is currently implemented or registered by this page.

## Future input, request, and response contract

Each future tool uses a strict Pydantic outer model with undeclared outer
fields forbidden (`extra="forbid"`). The inner `organization` value is an
opaque `dict[str, JsonValue]`; it is not a generic HTTP body and is not a
validated field-level organization schema.

| Future preview | Strict outer input | Bound request |
| --- | --- | --- |
| `api_organizations_create_preview` | exactly `{organization: dict[str, JsonValue]}` | `POST /organizations` with outer `organization` map |
| `api_organizations_update_preview` | exactly `{id: non-empty string, organization: dict[str, JsonValue]}` | `PUT /organizations/:id` with the same outer `organization` map |

For update, `id` is a required non-empty path identifier. If the opaque inner
map supplies `organization.id`, it must equal that path `id`; an absent inner
`organization.id` is not invented as a required field. The contract specifies
no relation wire form, `*Id` alias, enum member set, date/number encoding,
additional required-field validation, or organization-create sample.

Future response mapping requires only the `organizations` root. This freeze
does not claim a fixed metadata shape, additional root, record, or response
extra when Billy returns one.

## Shared ticketed-write protocol

The approved design requires preview/execute writes, and these future tools
must use the shared `ConfirmationStore` and `WriteProtocolService`.

- Preview is non-mutating. It validates only the strict outer shape, selects or
  confirms the organization context as the shared service requires,
  canonicalizes the full request, describes the expected effect, and issues a
  single-use confirmation ticket lasting at most five minutes.
- Every ticket is bound to the exact execute tool name, Billy organization,
  target, canonical request, and expected effect. Create binds a `null` target;
  update binds the non-empty path `id` as its target.
- Each execute accepts only `{confirmation_ticket: non-empty string}`. It
  accepts no business payload, replacement id, second preview input, or caller
  boolean as approval.
- Execute validates and consumes the matching unexpired ticket, restores its
  bound request, performs exactly one HTTP write, and has no retry. A changed
  request, target, organization, expected effect, or execute tool requires a
  new preview and ticket.

Missing, invalid, expired, consumed, or mismatched tickets must fail closed
under the shared confirmation protocol. Confirmation tickets and sensitive
organization values are not log or storage material.

## Official property boundaries and sensitivity

The official organization property table constrains the opaque inner map. It
does **not** become Pydantic required-field validation, an input sample, or a
claim that every listed property is writable or accepted live.

| Documented required property | Official type/boundary | Contract treatment |
| --- | --- | --- |
| `ownerUser` | belongs-to; required | Opaque inner value only; no relation wire form. |
| `name` | string; required | Opaque inner value only; no string rules beyond the official boundary. |
| `country` | belongs-to; immutable, required | Opaque inner value only; never treat the table as permission to change it. |
| `baseCurrency` | belongs-to; immutable, required | Opaque inner value only; never treat the table as permission to change it. |
| `fiscalYearEndMonth` | integer; required | Opaque inner value only; no numeric validation is frozen. |
| `firstFiscalYearStart` | date; required | Opaque inner value only; no date encoding is frozen. |
| `firstFiscalYearEnd` | date; required | Opaque inner value only; no date encoding is frozen. |
| `subscriptionPeriod` | enum; required | Opaque inner value only; no enum set or default is frozen. |
| `locale` | belongs-to; required | Opaque inner value only; no relation wire form. |
| `emailAttachmentDeliveryMode` | enum; required | Opaque inner value only; no enum set is frozen. |
| `vatPeriod` | enum; required | Opaque inner value only; no enum set is frozen. |
| `invoiceNoMode` | enum; required | Opaque inner value only; no enum set is frozen. |
| `nextInvoiceNo` | integer; required | Opaque inner value only; no numeric validation is frozen. |
| `paymentTermsMode` | enum; required | Opaque inner value only; no enum set is frozen. |
| `paymentTermsDays` | integer; required | Opaque inner value only; no numeric validation is frozen. |

`country` and `baseCurrency` are documented immutable. Documented readonly
properties—including `createdTime`, `url`, `logoPdfFile`, `logoUrl`, `iconUrl`,
`icon48Url`, `subscriptionDiscount`, `isTrial`, `terminationTime`,
`billEmailAddress`, `isUnmigrated`, `isLocked`, `lockedCode`, `lockedReason`,
and `appUrl`—are not client-writable. This is a boundary, not a mutable-field
allowlist.

`subscriptionCardType`, `subscriptionCardNumber`, and
`subscriptionCardExpires` are sensitive. Any future implementation, test, or
review must redact these values and must not log or store them. This page makes
no claim that it can safely retain, transmit, or validate card data.

## Method gates, errors, cleanup, and exclusions

The cited unauthenticated, non-mutating probes against the locked base used an
object body `{}` and establish these gates:

| Method and client-relative path | Result | Freeze consequence |
| --- | --- | --- |
| `POST /organizations` | 401 `AUTHENTICATION_REQUIRED` | Admits only the singular create contract at the authentication gate. It proves neither a valid payload nor a mutation, response, or live qualification. |
| `PUT /organizations/:id` | 401 `AUTHENTICATION_REQUIRED` | Admits only the singular update contract at the authentication gate. It proves neither a valid payload nor a mutation, response, or live qualification. |
| `DELETE /organizations/:id` | 405 `METHOD_NOT_ALLOWED` | Singular delete is closed and excluded. |

The official Supports list get, list, create, update, bulk save, and bulk
delete. The two POST/PUT gates plus Supports admit this limited singular
surface; a 405 overrides Supports optimism. The official page has no full bulk
body contract, so all bulk operations—including all 92 ambiguous bulk rows—are
excluded, empty-tool, and red.

Create cleanup is exactly:
`live non-production cleanup strategy unqualified; singular DELETE is unsupported`.
That is not live cleanup qualification. Update restoration is unproven; it is
not live cleanup qualification either.

This freeze excludes singular delete, every bulk save/delete operation,
webhooks, relation-wire speculation, payload schemas, caller approval booleans,
generic HTTP or browser controls, credentials, live work, browser/UI work,
vision verification, product implementation, server registration, contract
testing, coverage/status changes, inventory greening, and completeness claims.
The required independent Grok freeze review remains a later parent-owned gate
before any organizations product work.
