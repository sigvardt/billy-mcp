---
name: wave_fiveh_ticketed_writes_contract
title: Wave-5h attachment JSON ticketed-write contract (Codex Power fallback candidate)
desc: Cited fallback candidate for three offline-only Billy attachment JSON CUD operations; not an independent Grok acceptance.
tags: [billy, api, attachments, writes, confirmation, fallback]
sources:
  - https://www.billy.dk/api/
  - docs/superpowers/specs/2026-07-28-billy-mcp-complete-design.md
  - coverage/api_v2_manifest.yaml
  - coverage/status.json
  - wiki/offline_write_probe_rules.md
created: 2026-07-29T23:00:00Z
updated: 2026-07-29T23:00:00Z
---

# Wave-5h attachment JSON ticketed-write contract (Codex Power fallback candidate)

## Authority and evidence

This is a **Codex Power fallback contract candidate**, written because the
Grok CLI was unauthenticated before it could edit. It is not an independent
Grok review, acceptance verdict, or implementation gate. A later independent
Grok review alone may accept or reject this candidate; this page neither opens
nor closes a product, live-qualification, UI, vision, coverage, or completeness
gate.

The primary authority is the current [official Billy API documentation](https://www.billy.dk/api/),
fetched read-only on 2026-07-29 (HTTP 200; ETag `"hsisik4g9p3603"`; 147934
bytes; MD5 `c2efda0ee4cf9cf200e14910c5fc6996`). The fingerprint matches the
checked-in API manifest and the preceding cited research lead: no source drift
or manifest conflict was found. The resource table at
[`/v2/attachments`](https://www.billy.dk/api/#v2attachments) lists singular
create, update, and delete support. The generic official
[create/update/delete rules](https://www.billy.dk/api/#creating-a-record)
specify the singular-root request shape, partial `PUT`, bodyless idempotent
`DELETE`, changed-record responses, and deleted-id metadata.

## Frozen inventory and tool surface

This page freezes exactly these three offline-only JSON operations. Each
inventory row has one preview `tool_name`; its registered execute twin is not a
second inventory row.

| Inventory id | Preview tool | Execute tool | Official HTTP route | Runtime request | Request boundary | Response boundary |
| --- | --- | --- | --- | --- | --- | --- |
| `api.attachments.create` | `api_attachments_create_preview` | `api_attachments_create_execute` | `POST /v2/attachments` | `POST /attachments` | one `attachment` root | changed `attachments` root only |
| `api.attachments.update` | `api_attachments_update_preview` | `api_attachments_update_execute` | `PUT /v2/attachments/:id` | `PUT /attachments/:id` | one partial `attachment` root | changed `attachments` root only |
| `api.attachments.delete` | `api_attachments_delete_preview` | `api_attachments_delete_execute` | `DELETE /v2/attachments/:id` | `DELETE /attachments/:id` | no body; canonical ticket target `{"id": id}` | optional `meta.deletedRecords.attachments` only |

The locked runtime base is `https://api.billysbilling.com/v2`; runtime paths in
the table are client-relative and must never repeat `/v2`. The cited page shows
that base in its API-client example. No route, method, tool, or response root
outside this table is frozen by this candidate.

## Input, field, and response boundaries

- Every outer Pydantic preview input is strict and forbids undeclared fields.
  The inner `attachment` object remains opaque offline: this contract does not
  invent a typed inner schema or an owner encoding.
- The official property table calls `organization`, `owner`, and `file`
  immutable and required; `createdTime` is readonly. `owner` is a
  belongs-to-reference and has no published serialization recipe. In particular,
  do not synthesize `ownerId`, a typed reference string, or any other owner
  field from another resource's examples.
- `priority` is an integer with neither an immutable nor a readonly marker and
  is the sole clear mutable candidate. This does not establish the complete
  create payload or additional mutable values.
- Update is `PUT`, not `PATCH`, and is partial: omitted inner fields remain
  unchanged. If an `attachment.id` is supplied, it must exactly equal the route
  `:id`; otherwise reject the request before preview or execute.
- Create and update map only a present, well-formed changed `attachments`
  collection. Delete maps only a present, well-formed
  `meta.deletedRecords.attachments` collection. Do not fabricate an absent
  root, map a generic changed-record envelope, or add `files` or any other
  sibling root.
- List-only filters, includes, sorting, `page`, `pageSize`, and `meta.paging`
  are not inputs or response obligations for these CUD tools.

## Ticketed-write protocol

Preview is a no-write operation. It validates the strict outer input,
canonicalises the exact JSON request and target, and issues a short-lived,
single-use ticket bound to the exact execute tool, selected organisation,
canonical request, target, and expected effect. Execute accepts only
`confirmation_ticket`; it accepts no replacement business fields or approval
boolean.

All six tools use the root's single `ConfirmationStore` and
`WriteProtocolService`; no attachment-local confirmation store or protocol
service is permitted. Each `WriteOperationSpec` must carry its exact, non-empty,
server-owned `execute_tool_name`, and the executor must supply exactly that name
to the shared service. A name mismatch fails `CONFIRMATION_MISMATCH` before
ticket consumption and before HTTP. Once execute begins, it sends the prepared
request once: there is no write retry.

## Errors, sensitivity, and cleanup boundary

The manifest records all three rows as **medium** sensitivity and associates
the documented Billy authentication errors `AUTHENTICATION_REQUIRED` and
`OAUTH_INVALID_ACCESS_TOKEN`; the shared offline protocol maps missing or
invalid authentication to `AUTH_REQUIRED`. Authenticated missing resources must
map to the protocol's `NOT_FOUND` rather than be mistaken for a ticket result.

| Operation | Offline cleanup rule | What it does not prove |
| --- | --- | --- |
| create | Delete only a dedicated, disposable non-production test resource during later live qualification. | A valid create body, binary-upload dependency, or live cleanup. |
| update | Restore the prior dedicated test state during later live qualification. | Any field other than the clear `priority` candidate is mutable. |
| delete | Not recoverable; use disposable data only during later live qualification. | Cleanup or a server response merely because a missing id returns 200 unauthenticated. |

The official delete narrative is idempotent, so an unauthenticated missing-id
`DELETE` 200 is not cleanup proof, successful-authentication evidence, or a
live-test result. Cleanup requires an authenticated dedicated non-production
operation and independent read-back.

## Explicit exclusions

The official documentation separately describes high-sensitivity binary
`POST /files`: raw file bytes plus file-specific headers can optionally create
an attachment and may return both `files` and `attachments`. That is a distinct
special route, not evidence for attachment JSON CUD. This candidate therefore
keeps `api.files.create` and `api.special.files_upload` red and out of scope;
it neither infers file-upload behaviour nor serializes a file-upload request.

`api.attachments.bulk_save` and `api.attachments.bulk_delete` remain red
ambiguous-bulk rows because the public page provides no bulk method, body,
partial-failure, or limit contract. No bulk contract, webhook, special route,
unobserved response root, generic HTTP tool, or UI tool is authorised here.

There were no credentials, browser sessions, Billy records, authenticated
requests, UI observations, live tests, screenshots, HARs, traces, or vision
work in this fallback. It makes no coverage-green, `implemented`,
`contract_tested`, `live_tested`, `vision_verified`, registry-count, or
`complete` claim.

## Required offline implementation evidence

Before any later product or coverage change, the offline suite must prove:

- strict flat outer schemas and opaque inner attachment payload preservation;
- preview non-mutation; exact method, client-relative path, singular root, and
  JSON body; and no extra write;
- bodyless delete plus canonical `{"id": id}` ticket binding;
- partial `PUT` and supplied body/route id equality;
- typed authentication and not-found errors;
- ticket tamper, expiry, replay, wrong organisation, target, payload, and
  expected-effect rejection;
- exact executor-name mismatch rejection before ticket consumption and HTTP,
  including cross-resource binding through the one root store/service; and
- changed `attachments` mapping without fabricated roots, and optional delete
  metadata only when supplied.

Later authenticated non-production work, outside this candidate, must resolve
owner serialization, valid create prerequisites and `fileId` lifecycle, actual
response envelopes, priority editability, and cleanup by delete plus
independent read-back. It must not be backfilled from the binary `/files`
narrative or the unauthenticated missing-id delete observation.

## Sources

1. [Official Billy API documentation](https://www.billy.dk/api/) — current
   fingerprint above; resource table, create/update/delete rules, response
   rules, relationship narrative, and separate binary-file narrative.
2. `coverage/api_v2_manifest.yaml` and `coverage/status.json` — current
   inventory ids, tool names, documented errors, medium sensitivity, cleanup
   classifications, and red qualification state; not authority to green a row.
3. `docs/superpowers/specs/2026-07-28-billy-mcp-complete-design.md` — strict
   tool schemas, ticket binding, no-write preview, ticket-only execute, and
   no-retry requirements.
4. `wiki/offline_write_probe_rules.md` — retained probe rule that an
   unauthenticated missing-id delete result is not live cleanup evidence.
