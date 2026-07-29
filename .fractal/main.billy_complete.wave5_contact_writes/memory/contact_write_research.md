---
name: contact_write_research
desc: Frozen Wave-5a contact write contract and offline implementation boundaries.
tags: [billy, contacts, writes, confirmation]
sources:
  - wiki/wave_five_ticketed_writes_contract.md
  - .fractal/main.billy_complete/tmp/grok-research.md
  - docs/superpowers/specs/2026-07-28-billy-mcp-complete-design.md
  - coverage/api_v2_manifest.yaml
  - src/billy_mcp/api/write_protocol.py
  - .fractal/main.billy_complete.wave5_contact_writes/NODE.md
created: 2026-07-29T14:09:59Z
updated: 2026-07-29T14:09:59Z
---

# contact_write_research

The frozen official-document fingerprint is ETag `hsisik4g9p3603` and MD5
`c2efda0ee4cf9cf200e14910c5fc6996`. The cited parent Grok brief, frozen
contract, approved design, inventory, shared protocol, and leaf contract agree
on an offline-only ticketed contact CUD slice.

## Tool and wire contract

- `api_contacts_create_preview` and `api_contacts_create_execute`: `POST
  /contacts` with exact JSON `{ "contact": payload }`.
- `api_contacts_update_preview` and `api_contacts_update_execute`: `PUT
  /contacts/{percent-encoded id}` with exact JSON `{ "contact": payload }`.
- `api_contacts_delete_preview` and `api_contacts_delete_execute`: `DELETE
  /contacts/{percent-encoded id}` with no HTTP body; the ticket binds canonical
  `{ "id": id }`.

Every preview outer input is typed and forbids extras. Every execute accepts
only `WriteExecuteInput` (the confirmation ticket). The nested `contact`
payload remains `dict[str, JsonValue]`. `WriteProtocolService` owns ticket
issuance/consumption, canonical request binding, escaped paths, locked-client
execution without write retry, and typed response/error mapping. Success maps
the `contacts` changed-record root and optional `meta.deletedRecords` without
inventing absent metadata.

## Offline boundary

Do not add strict local validation for unresolved live-only contact semantics:
`paymentTermsDays`, contact type values, country wire shape, locale shape, or
embedded `contactPersons` replacement behaviour. The current documents suggest
`countryId`, a company/person type default, and `locale`, but only live
non-production evidence can qualify those details. Coverage and live status
remain red; no live Billy mutation is permitted.
