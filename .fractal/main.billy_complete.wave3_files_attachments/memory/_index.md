---
name: memory
desc: Node working memory for wave3 files/attachments read cluster.
tags: [billy, review, files, attachments]
sources:
  - https://www.billy.dk/api/
  - wiki/wave_three_unfiltered_reads_contract.md
created: 2026-07-29T11:09:58Z
updated: 2026-07-29T11:25:09Z
---

# memory

***

## Status

Independent review **PASS** on contract implementation of the two owned files.
Review report: node `tmp/grok-review.md`. Commit `66c900b` records the scoped
implementation delivery.

Committed delivery:

- `src/billy_mcp/api/file_attachment_reads.py`
- `tests/api/test_file_attachment_reads.py`

Both are the complete source delivery for the parent branch.

## Review facts

- Official docs fingerprint unchanged: etag `hsisik4g9p3603`, MD5
  `c2efda0ee4cf9cf200e14910c5fc6996`.
- Four tools match freeze: get/list files + attachments; no writes/upload.
- Focused tests 15 passed; node `scripts/test.sh` 143 passed; ruff/pyright OK.
- `BILLY_TEST_MODE=full` executes the same 143 tests, then correctly fails
  closed because global qualification still has 92 ambiguous bulk rows, 305
  incomplete API rows, and 339 incomplete UI rows. This leaf does not change
  those root-owned coverage states.
- Coverage rows `api.files.get/list` and `api.attachments.get/list` correctly
  still red; UI parity rows red.
- Root does not register the module yet (expected).
- Root confirmed the shared `downloadUrl` and account-bank-key redaction fix
  in commit `9555d79`; the leaf does not own that layer.

## Out of scope (unchanged)

Root registration, coverage greening, upload, writes, bulk, UI, live_tested.
