---
name: findings
desc: Durable verification facts from the Wave-3 independent offline review.
created: 2026-07-29T11:45:01Z
updated: 2026-07-29T11:45:01Z
---

# findings

## Docs fingerprint (verified)

- URL: https://www.billy.dk/api/
- etag: hsisik4g9p3603
- MD5: c2efda0ee4cf9cf200e14910c5fc6996
- bytes: 147934

## Required

- api.files.list and api.attachments.list tool success models expose top-level paging while official docs, wave_three contract, inventory response_fields, and sibling list tools use meta.paging. Wire read of payload.meta.paging is correct; tool-facing envelope is wrong.

## Coverage snapshot on reviewed revision

- 22 Wave-3 get/list rows: implemented true, contract_tested true, live_tested false
- status.complete false; live_tested_rows 0; implemented_rows 44

## Canonical shared report

Project wiki page wave_three_independent_review (not duplicated here).
