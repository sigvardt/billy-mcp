---
name: state
desc: Current state of the scoped catalog ticketed-write delivery.
created: 2026-07-29T15:19:07Z
updated: 2026-07-29T15:19:07Z
---

# state

The clean committed catalog delivery is `7a025e9`; its net diff from this
node's base contains only the two owned catalog source and test files. It
contains twelve flat typed FastMCP tools in
`src/billy_mcp/api/catalog_writes.py`: product and product-price create, update,
and delete preview/execute pairs. All executions flow solely through the shared
`WriteProtocolService`; product operations preserve the additional
`productPrices` changed-record root.

`tests/api/test_catalog_writes.py` verifies strict schemas, opaque payloads,
mutation-free previews, exact singular HTTP requests, ticket failure states,
empty-token no-network behavior, typed upstream errors, optional deletion
metadata, and product multi-root response mapping. Registration and all
coverage, live, UI, bulk, and completion state remain root-owned and unchanged.
