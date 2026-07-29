---
name: wave_four_offline_integration_review
desc: Independent Grok review of Wave-4 offline get/list integration on root.
tags: [billy, api, review, wave4]
sources:
  - https://www.billy.dk/api/
  - docs/superpowers/specs/2026-07-28-billy-mcp-complete-design.md
  - .fractal/main.billy_complete/tmp/grok-review.md
created: 2026-07-29T13:02:00Z
updated: 2026-07-29T13:02:00Z
---

# wave_four_offline_integration_review

Independent Grok review of the registered Wave-4 offline read surface on
`main.billy_complete` at commit `3f56399`.

## Verdict

- **ACCEPT** the Wave-4 offline-read slice: 50 remaining clear get/list tools
  are real, registered, contract-tested, and inventory-evidenced.
- **FAIL** product completeness: live, UI/vision, bulk, writes, auth product
  tools, and four specials remain red; `complete` stays false.

## Verified product facts

- Registry: 94 `api_*` tools + 2 `coverage_*` tools.
- Clear resource get/list offline: 92/92; specials offline-green: user get and
  user organizations only.
- Coverage: implemented 94, contract_tested 94, live_tested 0, vision 0,
  complete false.
- Official docs fingerprint: ETag `hsisik4g9p3603`, MD5
  `c2efda0ee4cf9cf200e14910c5fc6996` (https://www.billy.dk/api/).
- Offline suite: 487 tests pass (`not live and not vision`). Full mode fails
  only at the completeness gate (expected fail-closed).
- No false-green bulk, write, live, or UI rows.
- No REQUIRED rewrites of geo, tax, bank, balance/invoice-ext, or ledger/users
  read modules.

## Explicitly still incomplete

- 92 ambiguous bulk rows
- All clear create/update/delete
- Specials: files upload, invoice email, invoice delivery, invoice logs
- Live qualification without a non-production token
- Authenticated UI, vision, and auth product tools

Full review narrative (scratch): `.fractal/main.billy_complete/tmp/grok-review.md`.
