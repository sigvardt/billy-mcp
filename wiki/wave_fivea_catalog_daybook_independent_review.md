---
name: wave_fivea_catalog_daybook_independent_review
desc: Independent Grok review of Wave-5a catalog and daybook write tips (both ACCEPT for selective product merge; product completeness FAIL; root fail-closed PASS).
tags: [billy, api, writes, review, wave5]
sources:
  - https://www.billy.dk/api/
  - wiki/wave_five_ticketed_writes_contract.md
  - wiki/wave_fivea_candidate_independent_review.md
  - docs/superpowers/specs/2026-07-28-billy-mcp-complete-design.md
  - coverage/api_v2_manifest.yaml
  - coverage/status.json
created: 2026-07-29T15:25:00Z
updated: 2026-07-29T15:25:00Z
---

# wave_fivea_catalog_daybook_independent_review

## Verdict

| Gate | Result |
| --- | --- |
| Official docs ↔ inventory fingerprint | **PASS** (`hsisik4g9p3603` / `c2efda0ee4cf9cf200e14910c5fc6996`) |
| Root fail-closed honesty @ `909d054` | **PASS / ACCEPT** |
| Catalog tip `ba4101a` (product content `03f5720`) | **ACCEPT** (product/test only; no inventory greening) |
| Daybook tip `0d4b0e5` (product content `791c84d`) | **ACCEPT** (product/test only; no inventory greening) |
| Product completeness | **FAIL** (expected) |
| UI / live / vision / bulk | **FAIL** (correctly red) |

Root still exposes **94** `api_*` tools + 2 coverage tools. Zero write tools registered. Zero write inventory rows green. Live and vision remain 0. Bulk remains 92 empty-tool red rows.

Full detail: `.fractal/main.billy_complete/tmp/grok-review.md`.  
Contract brief: `.fractal/main.billy_complete/tmp/grok-research.md`.

This page is the merge gate for the catalog and daybook leaves. Prior Wave-5a contact cohort ACCEPT remains in `wiki/wave_fivea_candidate_independent_review.md`.

## Merge path

1. Selectively merge **product and test files only** (never child `.fractal/` seed trees):
   - catalog: `src/billy_mcp/api/catalog_writes.py`, `tests/api/test_catalog_writes.py` from tip `ba4101a`
   - daybook: `src/billy_mcp/api/daybook_writes.py`, `tests/api/test_daybook_writes.py` from tip `0d4b0e5`
2. Do **not** green inventory or register tools in those merge commits.
3. Root registration (separate Codex Power slice): one confirmation store + write protocol; register contacts, contact persons, catalog, daybooks (**30** tools); green only the **15** offline write rows with real test references; keep `live_tested=false` and `complete=false`.
4. Independent Grok product review after integrated registration.

## Contract anchors

- Products: `POST/PUT/DELETE /v2/products`; singular `product`; optional embed `prices[]`; multi-root responses may include `productPrices`.
- Product prices: `POST/PUT/DELETE /v2/productPrices`; singular `productPrice`; MCP schema field **`productPrice`**.
- Daybooks: `POST/PUT/DELETE /v2/daybooks`; singular `daybook`; no additional plural roots offline.
- Execute tools accept only `confirmation_ticket`. Preview must not mutate Billy.

## Overlay evidence

Focused suite after clean export of both candidates onto root baseline: **105** passed (catalog + daybook + protocol + contacts + contact persons).
