---
name: undocumented_bulk_owner_skip
desc: Owner decision to skip 92 undocumented bulk API mentions without claiming support.
tags: []
sources: []
created: 2026-08-21T00:00:00Z
updated: 2026-08-21T00:00:00Z
---

# Undocumented bulk API owner skip

Billy's official documentation exposes bulk save and bulk delete Supports flags
for 46 resources, producing 92 inventory mentions. It does not provide a usable
request body, query, response, or error contract for those mentions.

The owner stopped this work on 2026-08-21 before establishing that separate bulk
tools are needed. The same business actions already have individual operations.
This is not proof that Billy has no usable bulk endpoint. It is also not a claim
that any bulk operation works.

Coverage rules:

- Keep all 92 rows visible.
- Set owner scope to `out_of_scope_by_user`.
- Use `scope_code=BULK_CONTRACT_UNDOCUMENTED_OWNER_SKIP`.
- Do not register tools, infer payloads, run live API probes, or mark rows green.
- Exclude these rows from the applicable operation count and current completion
  blocker set.
- Reopen only after Billy publishes a complete contract or the owner explicitly
  requests separate bulk tools.
