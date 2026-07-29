---
name: state
desc: Delivered state of the scoped invoice-line ticketed-write leaf.
created: 2026-07-29T19:08:52Z
updated: 2026-07-29T19:08:52Z
---

# state

The invoice-line leaf is implemented in `src/billy_mcp/api/invoice_line_writes.py`
with six flat ticketed FastMCP tools and strict outer Pydantic inputs. Its
focused contract tests live in `tests/api/test_invoice_line_writes.py`.

Every invoice-line operation uses the shared write protocol with the required
`/invoiceLines` route family, `invoiceLine` request root, `invoiceLines`
primary response root, and optional `invoices` response mapping. Explicit
update payload IDs must match the route ID.

Focused tests, non-live node tests, and the node lint gate pass. Full mode
remains fail-closed only at the repository-wide coverage-completeness gate;
this leaf leaves coverage, registration, and shared protocol files untouched.
