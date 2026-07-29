---
name: contact_write_research
desc: Frozen Wave-5a contact write contract and offline implementation boundaries.
tags: [billy, contacts, writes, confirmation]
sources:
  - wiki/wave_five_ticketed_writes_contract.md
  - .fractal/main.billy_complete/tmp/grok-research.md (cited parent brief; unavailable in this worktree)
  - docs/superpowers/specs/2026-07-28-billy-mcp-complete-design.md
  - coverage/api_v2_manifest.yaml
  - src/billy_mcp/api/write_protocol.py
  - .fractal/main.billy_complete.wave5_contact_writes/NODE.md
created: 2026-07-29T14:32:56Z
updated: 2026-07-29T14:32:56Z
---

# contact_write_research

The frozen official-document fingerprint is ETag `hsisik4g9p3603` and MD5
`c2efda0ee4cf9cf200e14910c5fc6996`. The frozen contract, approved design,
inventory, shared protocol, and leaf contract agree on an offline-only ticketed
contact CUD slice. The cited parent Grok brief is an explicit source of the
contract, but its ignored path is unavailable in this worktree; no replacement
research was performed. The contract preserves its cited, frozen conclusions,
including that an unauthenticated DELETE observation is not live-mutation or
cleanup qualification.

## Tool and wire contract

The six required registrations are `api_contacts_create_preview`,
`api_contacts_create_execute`, `api_contacts_update_preview`,
`api_contacts_update_execute`, `api_contacts_delete_preview`, and
`api_contacts_delete_execute`.

- Create: `POST /contacts` with exact JSON `{ "contact": payload }`.
- Update: `PUT /contacts/{percent-encoded id}` with exact JSON
  `{ "contact": payload }`.
- Delete: `DELETE /contacts/{percent-encoded id}` with no HTTP body; its ticket
  binds canonical `{ "id": id }`.

Every preview outer input is typed and forbids extras. Every execute accepts
only `WriteExecuteInput` (the confirmation ticket). The nested `contact`
payload remains `dict[str, JsonValue]`. `WriteProtocolService` owns ticket
issuance/consumption, canonical request binding, escaped paths, locked-client
execution without write retry, and typed response/error mapping. The inventory
lists the three request roots as `contact`, IDs as the update/delete input, and
the `contacts` changed-record root plus optional `meta.deletedRecords` without
inventing absent metadata.

FastMCP registration must expose the preview fields and execute
`confirmation_ticket` as direct handler parameters so generated tool schemas
do not add an `input` wrapper. Handlers construct these existing outer Pydantic
models internally before using `WriteProtocolService`; registrations remain the
six literal names above.

## Offline boundary

Do not add strict local validation for unresolved live-only contact semantics:
`paymentTermsDays`, contact type values, country wire shape, locale shape, or
embedded `contactPersons` replacement behaviour. The current documents suggest
`countryId`, a company/person type default, and `locale`, but only live
non-production evidence can qualify those details. Coverage and live status
remain red; no live Billy mutation is permitted.
