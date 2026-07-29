---
name: research_contact_persons
desc: Research findings for Wave-3 contact-person get/list (private node memory).
tags: [billy, api, research, contact_persons]
sources:
  - https://www.billy.dk/api/
  - wiki/wave_three_unfiltered_reads_contract.md
  - .fractal/main.billy_complete.wave3_contact_persons/tmp/grok-research.md
created: 2026-07-29T11:14:00Z
updated: 2026-07-29T11:14:00Z
---

# research_contact_persons

## Status

Research brief delivered to node scratch `tmp/grok-research.md`. Docs fingerprint
is unchanged. The scoped typed implementation and offline verification are complete.

## Locked contract for owned tools

- Tools: `api_contact_persons_get`, `api_contact_persons_list`
- Paths: `/contactPersons`, `/contactPersons/{id}` (URL-encode id)
- Roots: `contactPerson`, `contactPersons[]` + optional `meta.paging`
- List query only: page, pageSize (1–1000), include, sortProperty, sortDirection ASC|DESC
- Reject: offset, contactId, every undeclared input
- Map 401 `AUTHENTICATION_REQUIRED` and `OAUTH_INVALID_ACCESS_TOKEN` to AUTH_REQUIRED
- Pattern: mirror `contact_reads.py` + its tests; module-local register only
- Sensitivity: do not log email fixtures or live emails; root owns redaction module

## Evidence highlights

- Official `/v2/contactPersons` properties: contact (belongs-to, immutable required), isPrimary, name, email
- No resource filter table; Filtering section only links bills, daybook transactions, invoices
- Live unauth list: 401 AUTHENTICATION_REQUIRED
- Live invalid token: 401 OAUTH_INVALID_ACCESS_TOKEN
- Live unauth get id `x`: 404 RECORD_NOT_FOUND text names singular `contactPerson`
- Inventory rows still implemented/contract_tested/live_tested false
- UI discovery blocked (no non-prod credentials)

## Out of scope for this node

Root registration, coverage green, live tests, writes, bulk, UI, wiki contract edits, redaction.py
