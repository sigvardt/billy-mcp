---
name: state
desc: Delivered parent-invoice ticketed-write leaf state.
created: 2026-07-29T19:08:08Z
updated: 2026-07-29T19:08:08Z
---

# state

The leaf delivers exactly six parent-invoice preview/execute tools in
`src/billy_mcp/api/invoice_writes.py` with focused contract evidence in
`tests/api/test_invoice_writes.py`. The tools use the shared write protocol,
preserve opaque invoice fields, enforce the route/body identifier invariant,
and keep DELETE bodyless.

Focused tests, lint, and the normal node suite pass. The Codex fallback review
found no actionable leaf issue; it does not replace the unavailable Grok
product-review gate. Root server registration, cross-executor evidence, and
coverage changes belong to the parent integration.
