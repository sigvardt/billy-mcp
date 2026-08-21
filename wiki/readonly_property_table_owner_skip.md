---
name: readonly_property_table_owner_skip
desc: Owner skip for six Supports create/update rows whose official property tables have no writable field.
tags: []
sources: []
created: 2026-08-21T00:00:00Z
updated: 2026-08-21T15:29:27Z
---

# readonly_property_table_owner_skip

Official Billy API v2 Supports lists create and update for
`contactBalancePostings`, `postings`, and `transactions`. The official
property tables have no non-readonly writable request field. `organization`
on postings and transactions is immutable and required; that is not a
documented create body.

Owner radio `21A3D94F` (2026-08-21) keeps the six rows visible and
unimplemented:

- `api.contactBalancePostings.create`
- `api.contactBalancePostings.update`
- `api.postings.create`
- `api.postings.update`
- `api.transactions.create`
- `api.transactions.update`

Coverage rules:

- `qualification.kind=out_of_scope_by_user`
- `scope_code=READONLY_PROPERTY_TABLE_OWNER_SKIP`
- `supersedes_blocker_code=READONLY_PROPERTY_TABLE`
- `tools_allowed=false`
- flags stay false
- outside the applicable operation count
- reopen only if Billy publishes a writable contract or the owner asks

Singular `api.transactions.delete` stays a ticketed offline tool. Do not
guess `{posting|transaction: {organization}}`. See
[[undocumented_bulk_owner_skip]] for the separate bulk skip.
