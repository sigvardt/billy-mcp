---
name: memory
desc: Private working state for wave3 document-lines node.
tags: [delivery]
sources: []
created: 2026-07-29T11:09:32Z
updated: 2026-07-29T11:29:00Z
---

# memory

***

## Status

The document-line read cluster is committed at `9a797bc` with six typed, offline-verified tools and focused contract tests.

## Contract pointers

- Wiki freeze: `wiki/wave_three_unfiltered_reads_contract.md`
- Research: `tmp/grok-research.md`

## Delivered contract

- Tools: `api_invoice_lines_get/list`, `api_bill_lines_get/list`, and `api_daybook_transaction_lines_get/list`.
- Collections accept only `page`, `pageSize`, `include`, `sortProperty`, and `sortDirection` (`ASC` / `DESC`).
- Requests reject empty `include`, offset, parent-id filters, and undeclared keys.
- Responses map only documented camel-case roots, preserve optional `meta.paging`, keep payloads opaque, and use the shared typed auth path.

## Verification boundaries

- Focused contract suite, Ruff, Pyright, and the commit-mode repository suite pass offline.
- Docs MD5 `c2efda0ee4cf9cf200e14910c5fc6996` unchanged
- Six inventory get/list rows remain red; root owns server registration and evidence before any inventory transition. Live qualification and product completeness remain false.
