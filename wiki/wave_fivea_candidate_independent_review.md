---
name: wave_fivea_candidate_independent_review
desc: Independent Grok review of root fail-closed baseline and Wave-5a candidate tips (protocol, contacts, and contact persons ACCEPT for selective product merge; product completeness FAIL).
tags: [billy, api, writes, review, wave5]
sources:
  - https://www.billy.dk/api/
  - wiki/wave_five_ticketed_writes_contract.md
  - wiki/wave_five_write_protocol_independent_review.md
  - docs/superpowers/specs/2026-07-28-billy-mcp-complete-design.md
  - coverage/api_v2_manifest.yaml
  - coverage/status.json
created: 2026-07-29T14:28:00Z
updated: 2026-07-29T15:05:00Z
---

# wave_fivea_candidate_independent_review

## Verdict

| Gate | Result |
| --- | --- |
| Root fail-closed honesty @ `5ab3efa` | **PASS / ACCEPT** |
| Official docs ↔ inventory fingerprint | **PASS** (`hsisik4g9p3603` / `c2efda0ee4cf9cf200e14910c5fc6996`) |
| Execute-twin coverage gate @ `5ab3efa` | **PASS / ACCEPT** |
| Product completeness | **FAIL** (expected incomplete) |
| Protocol multi-root tip `4b2c12c` (product content from `239bc52`) | **ACCEPT** (product/test files only; no inventory greening) |
| Contact writes tip `a86afe9` (product content from `1b8bb42`) | **ACCEPT** (flat schema; prior nested-`input` reject closed) |
| Contact-person writes tip `341d0b1` (product content from `cd0a379`) | **ACCEPT** (update `id` minLength; prior reject closed) |
| UI / live / vision / bulk | **FAIL** (correctly red) |

Root still exposes **94** `api_*` tools + 2 coverage tools. Zero write tools registered on root. Zero write inventory rows green. Live and vision remain 0. Bulk remains 92 empty-tool red rows. Focused overlay of the three product modules: **58** tests passed. Full detail: `.fractal/main.billy_complete/tmp/grok-review.md`.

This page supersedes the earlier contact and contact-person **REJECT** rows for those repaired tips.

## Merge path

1. Selectively merged **product and test files only** (never child `.fractal/`
   seed trees) in labelled commits `95e03c4`, `9d40949`, and `b25582f`:
   - protocol: `src/billy_mcp/api/write_protocol.py`, `tests/unit/test_write_protocol.py`
   - contacts: `src/billy_mcp/api/contact_writes.py`, `tests/api/test_contact_writes.py`
   - contact persons: `src/billy_mcp/api/contact_person_writes.py`, `tests/api/test_contact_person_writes.py`
2. Merge order was protocol, contacts, then contact persons. The resulting root
   passed lint and **546** non-live tests; the source leaves were then
   intentionally closed.
3. Do **not** green inventory until root registration with one shared confirmation store and write protocol, real evidence paths, and non-live suite green.
4. The next disjoint implementation leaves are catalog writes (multi-root;
   declare `productPrices` additional root on product ops) and daybook writes.
5. Registration target after those four resource cohorts: 30 write tools, 15
   offline-green write rows, surface **124** `api_*`. Leave `live_tested` and
   `complete` false.

## Residual product blockers (not merge defects)

- 115 clear write operations still red after the three accepted modules merged
  without registration.
- 92 bulk operations without body contracts.
- Four specials still red (files upload; invoice email/delivery/logs).
- All 339 UI rows red; no vision evidence.
- No live qualification without `BILLY_API_TOKEN`.

## Sources

1. Official Billy API documentation: https://www.billy.dk/api/
2. Frozen Wave-5 contract: [[wave_five_ticketed_writes_contract]]
3. Foundation protocol IR: [[wave_five_write_protocol_independent_review]]
4. Machine inventory: `coverage/api_v2_manifest.yaml`, `coverage/status.json`
5. Review artifact: `.fractal/main.billy_complete/tmp/grok-review.md`
6. Research brief: `.fractal/main.billy_complete/tmp/grok-research.md`

## Related review

Catalog and daybook tips are gated in
`wiki/wave_fivea_catalog_daybook_independent_review.md` (both ACCEPT for
selective product merge; registration still blocked).
