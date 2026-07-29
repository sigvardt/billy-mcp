---
name: memory
desc: Private working memory for wave4_balance_invoice_ext_reads leaf.
tags: [research, review, wave4, balance, invoice]
sources:
  - https://www.billy.dk/api/
  - wiki/wave_four_remaining_clear_reads_contract.md
created: 2026-07-29T12:26:46Z
updated: 2026-07-29T12:43:00Z
---

# memory

***

## Standing facts

- The exclusive source and test files implement the ten frozen contact-balance
  and invoice-extension get/list tools. Inputs are strict and flat; records are
  opaque; paths encode IDs; responses preserve optional `meta.paging`; malformed
  roots and both documented 401 envelopes are typed errors.
- Product commit `f5afcc7` contains only those two owned files.
- Independent review passed the offline contract. Focused Ruff format/check and
  Pyright passed; the synthetic module suite passed 24 tests; node lint and the
  non-live suite passed without changing product coverage claims.
- Contract authority is the Wave-4 project-wiki freeze and the node-local Grok
  brief. The official documentation fingerprint remains `hsisik4g9p3603` /
  `c2efda0ee4cf9cf200e14910c5fc6996`.
- Inventory integration, root server registration, redaction wiring, and all
  live, UI, vision, and completeness claims are root-owned and remain red.
