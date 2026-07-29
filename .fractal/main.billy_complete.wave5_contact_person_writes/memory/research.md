---
name: research
desc: Frozen Wave-5a contact-person write contract used by this leaf.
tags: [billy, contact-persons, writes, confirmation]
sources:
  - wiki/wave_five_ticketed_writes_contract.md
  - /Volumes/ssd_1/Repositories/billy-mcp/.worktrees/main.billy_complete/.fractal/main.billy_complete/tmp/grok-research.md
  - docs/superpowers/specs/2026-07-28-billy-mcp-complete-design.md
  - coverage/api_v2_manifest.yaml
  - src/billy_mcp/api/write_protocol.py
  - .fractal/main.billy_complete.wave5_contact_person_writes/NODE.md
created: 2026-07-29T14:09:46Z
updated: 2026-07-29T14:09:46Z
---

# research

The official documentation fingerprint is ETag `hsisik4g9p3603` and MD5
`c2efda0ee4cf9cf200e14910c5fc6996`. The cited parent Grok brief and the frozen
shared contract are authoritative; this leaf performs no new web, interface,
or live research.

Register exactly these paired tools through
`register_contact_person_write_tools(server, client, write_protocol)`:

- `api_contact_persons_create_preview` and `api_contact_persons_create_execute`
- `api_contact_persons_update_preview` and `api_contact_persons_update_execute`
- `api_contact_persons_delete_preview` and `api_contact_persons_delete_execute`

Create is `POST /contactPersons` with `{ "contactPerson": payload }`; update
is `PUT /contactPersons/{escaped-id}` with the same singular body; delete is
`DELETE /contactPersons/{escaped-id}` with no body. Preview must produce the
ticket through `WriteOperationSpec` and `WriteProtocolService`; execute accepts
only `WriteExecuteInput` and delegates to the protocol.

The contact-person property table makes `contactId` dependency-sensitive and
describes name-or-email semantics inconsistently. Do not add offline name/email
XOR or required-field validators; retain the nested payload as opaque JSON and
leave that question for live qualification.

`contactId` remains caller-supplied opaque payload data as well: its documented
dependency does not establish a locally provable value shape or availability.

Sources are the frozen contract at `wiki/wave_five_ticketed_writes_contract.md`,
the cited parent Grok brief at
`/Volumes/ssd_1/Repositories/billy-mcp/.worktrees/main.billy_complete/.fractal/main.billy_complete/tmp/grok-research.md`,
design sections 6–8 in
`docs/superpowers/specs/2026-07-28-billy-mcp-complete-design.md`, the
contact-person CUD rows in `coverage/api_v2_manifest.yaml`, the existing
`src/billy_mcp/api/write_protocol.py`, and this leaf's `NODE.md` contract.
