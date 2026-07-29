---
name: state
desc: Current state of the scoped account ticketed-write delivery.
created: 2026-07-29T16:29:43Z
updated: 2026-07-29T16:29:43Z
---

# state

The owned account write module provides twelve ticketed FastMCP tools for
`accountGroups` and `accounts`: preview and execute variants for create,
update, and delete. It uses the passed `WriteProtocolService`, strict outer
models, client-relative paths, singular request roots, and bodyless deletes.

The owned contract tests cover exact registration schemas, mutation-free
previews, exact HTTP construction, typed errors, optional deleted-record
mapping, and confirmation invalid/tamper/expiry/replay/binding rejection. The
delivery is offline-only; server registration, coverage evidence, live, UI, and
bulk work remain outside this leaf's scope.
