---
name: state
desc: Current delivery state for the bill-line ticketed-write leaf.
created: 2026-07-29T20:14:13Z
updated: 2026-07-29T20:14:13Z
---

# state

The bill-line ticketed-write slice is ready for its scoped commit. The two owned
files provide six flat FastMCP preview/execute tools for `POST /billLines`,
`PUT /billLines/:id`, and bodyless `DELETE /billLines/:id`, using the shared
write protocol and optional `bills` response mapping.

The local contract suite covers strict outer inputs, opaque inner payloads,
canonical request binding, encoded paths, response mapping, typed errors,
ticket safeguards, executor mismatch, and one-shot execution. Focused pytest,
Ruff, Pyright, and the node scripts pass. The shared Wave-5e contract already
records the durable cross-resource rules, so this leaf has no project-wiki
addition.
