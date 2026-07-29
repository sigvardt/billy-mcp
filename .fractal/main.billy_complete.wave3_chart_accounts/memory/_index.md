---
name: memory
desc: Final private state for the Wave-3 chart-of-accounts read cluster.
tags: [billy, chart_accounts, delivered]
sources:
  - wiki/wave_three_unfiltered_reads_contract.md
created: 2026-07-29T11:30:55Z
updated: 2026-07-29T11:30:55Z
---

# memory

***

## Status

The scoped chart-of-accounts read delivery is committed at `22f2fe3`.
Independent review passed the product contract. Focused pytest, Ruff, Pyright,
and the offline node suite pass; full qualification correctly fails closed on
the intentionally incomplete shared coverage and UI evidence.

## Delivered facts

- Six typed get/list tools cover accounts, accountGroups, and accountNatures.
- IDs are URL-encoded; response payloads remain opaque; list inputs allow only
  page, pageSize, include, sortProperty, and ASC/DESC sortDirection.
- Tests cover resource roots, paths, paging, input rejection, typed 401 errors,
  and module-local registration without printing bank-field values.
- No writes, bulk calls, UI automation, live requests, secrets, or coverage
  updates were performed.

## Root residuals

- Root owns server registration, coverage evidence, and shared bank-field
  redaction; live/UI qualification and overall completeness remain red.
