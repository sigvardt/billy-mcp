---
name: wave_fivea_candidate_independent_review
desc: Independent Grok review of root fail-closed baseline and Wave-5a candidate tips (protocol ACCEPT; contacts and contact persons REJECT).
tags: [billy, api, writes, review, wave5]
sources:
  - https://www.billy.dk/api/
  - wiki/wave_five_ticketed_writes_contract.md
  - wiki/wave_five_write_protocol_independent_review.md
  - docs/superpowers/specs/2026-07-28-billy-mcp-complete-design.md
  - coverage/api_v2_manifest.yaml
  - coverage/status.json
created: 2026-07-29T14:28:00Z
updated: 2026-07-29T14:28:00Z
---

# wave_fivea_candidate_independent_review

## Verdict

| Gate | Result |
| --- | --- |
| Root fail-closed honesty @ `4b632c7` | **PASS / ACCEPT** |
| Official docs ↔ inventory fingerprint | **PASS** (`hsisik4g9p3603` / `c2efda0ee4cf9cf200e14910c5fc6996`) |
| Product completeness | **FAIL** (expected incomplete) |
| Protocol multi-root tip `09648ce` | **ACCEPT** (product files only; no inventory greening) |
| Contact writes tip `b09e5ec` | **REJECT** (nested MCP `input` envelope) |
| Contact-person writes tip `2a56a92` | **REJECT** (update `id` schema missing `minLength`) |

Root still exposes **94** `api_*` tools + 2 coverage tools. Zero write tools registered. Zero write inventory rows green. Live and vision remain 0. Bulk remains 92 empty-tool red rows. Full detail and reproducible commands: `.fractal/main.billy_complete/tmp/grok-review.md`.

## Required fixes before merge

1. **Contacts:** flatten tool parameters so callers pass `contact` / `id` / `confirmation_ticket` at the top level, not under a nested `input` object. Align with read tools and contact-person writes.
2. **Contact persons:** put `Field(min_length=1)` on the update-preview `id` function parameter so the published tool schema includes `minLength: 1` (delete already does).
3. **Merge hygiene:** product files only; never merge child `.fractal/` seed trees onto root.

## Accept path

1. Merge protocol multi-root product files after exclusive-file verification.
2. After R1–R2, merge contact and contact-person modules.
3. Spawn catalog writes (depends multi-root) and daybook writes.
4. Registration leaf: one `ConfirmationStore` + `WriteProtocolService`, 30 tools, green only the 15 offline write rows, surface 124 `api_*`. Leave `live_tested` and `complete` false.

## Sources

1. Official API documentation: https://www.billy.dk/api/
2. Frozen Wave-5 contract: [[wave_five_ticketed_writes_contract]]
3. Foundation protocol IR: [[wave_five_write_protocol_independent_review]]
4. Machine inventory: `coverage/api_v2_manifest.yaml`, `coverage/status.json`
