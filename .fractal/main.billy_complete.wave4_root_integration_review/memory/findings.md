---
name: findings
desc: Verified audit findings for Wave-4 root integration at 3f56399.
tags: [billy, review, wave4]
created: 2026-07-29T13:07:09Z
updated: 2026-07-29T13:07:09Z
---

# findings

## Offline integration (PASS)

- Audit commit `3f56399`.
- 50 Wave-4 get/list tools match freeze paths/roots; geo `countryId` only on cities/states/zipcodes lists.
- Registry: 94 `api_*` + `coverage_status` + `coverage_report`; no write/bulk/generic HTTP/browser tools.
- Inventory: 94 implemented/contract_tested, 0 live, 92/92 clear get/list green, 0 bulk/write green, complete false.
- UI: 339 all red.
- Redaction: email/phone, bank*, downloadurl. Host: api.billysbilling.com/v2. Auth codes map to AUTH_REQUIRED.
- Docs fingerprint: etag hsisik4g9p3603 / MD5 c2efda0ee4cf9cf200e14910c5fc6996 / 147934 B.

## Product completeness (incomplete)

- No live token, UI, vision, bulk, write, or auth product qualification.

## Tests

- commit mode: 487 passed.
- full mode: exit 1 at require-complete (expected).
- ruff, pyright, coverage (non-require), repository policy: pass.
