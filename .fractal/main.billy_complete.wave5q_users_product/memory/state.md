---
name: state
desc: Current durable state for the bounded users-update product leaf.
created: 2026-07-30T14:23:20Z
updated: 2026-07-30T14:23:20Z
---

# state

The offline users-update product slice is implemented in the owned source and
test paths. It exposes exactly `api_users_update_preview` and
`api_users_update_execute`, using the shared confirmation protocol for a
ticket-only, single-use, no-retry `PUT /users/:id` request.

The strict outer input rejects unknown fields and empty ids. The inner `user`
map remains opaque, with an optional matching `user.id` check. The generated
coverage inventory marks only `api.users.update` implemented and
contract-tested; it remains unqualified for live, UI, vision, bulk, and
completeness.

Focused tests, lint, coverage policy checks, and the offline commit suite pass.
Inherited node-seed runtime changes are preserved outside the product scope.
