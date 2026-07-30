---
name: wave_fivesb_files_upload_product_ready_research_independent_review
title: Wave-5s-B product-ready research independent review ACCEPT
desc: Authoritative root Grok acceptance of the cited offline product-ready handoff for ticketed binary POST /files special and dual-row create alias; product and completeness remain open.
tags: [billy, api, files, upload, research, review, product-ready, offline]
sources:
  - https://www.billy.dk/api/
  - https://api.billysbilling.com/v2
  - wiki/wave_fivesb_files_upload_product_ready_research.md
  - wiki/wave_fivesb_files_upload_research.md
  - wiki/wave_fives_residual_specials_research.md
  - docs/superpowers/specs/2026-07-28-billy-mcp-complete-design.md
  - coverage/api_v2_manifest.yaml
  - coverage/status.json
  - "parent scratch: .fractal/main.billy_complete/tmp/grok-review.md"
created: 2026-07-30T17:26:00Z
updated: 2026-07-30T17:26:00Z
---

# Wave-5s-B product-ready research independent review ACCEPT

## Verdict

| Claim | Result |
| --- | --- |
| Wave-5s-B product-ready research handoff (research80) | **ACCEPT** offline as implementation handoff only |
| Official documentation versus maintained inventory | **PASS** |
| Research versus freeze tool/path/header map | **PASS** |
| Design §8.3–§8.4 file-identity requirements | **PASS** |
| Coverage honesty before product | **PASS** |
| Wave-5s-B product implementation | **not accepted** — separate Grok product review required after root integration |
| Live, UI, vision, bulk, and completeness | **not claimed / fail-closed** |

The authoritative root `INDEPENDENT-REVIEW` Grok step accepted the product-ready
research at scratch `.fractal/main.billy_complete/tmp/grok-research.md`
(research80) against freeze page [[wave_fivesb_files_upload_research]],
product-ready page [[wave_fivesb_files_upload_product_ready_research]], residual
ranking [[wave_fives_residual_specials_research]], design §8.3–§8.4, and root
baseline **`4e78e37`**. Full cited findings live outside the public repository
at `.fractal/main.billy_complete/tmp/grok-review.md`.

## Exact reviewed scope

This ACCEPT covers only the cited handoff that opens Codex Power product work
for the dual-row binary upload special:

| Inventory id | Preview tool | Execute tool | HTTP | Body | Response roots |
| --- | --- | --- | --- | --- | --- |
| `api.special.files_upload` | `api_files_upload_preview` | `api_files_upload_execute` | `POST /files` | raw bytes | `files` required; `attachments` optional |
| `api.files.create` | (none; empty tool_name) | (alias only) | same | same | same |

Independent re-fetch of [official Billy API documentation](https://www.billy.dk/api/)
returned HTTP 200, ETag `"wcw4x9hqvu3603"`, 147934 bytes, MD5
`8b94b0135c91fd15fe54ea33e088a4be` — matching research80. Unauth probes on
`https://api.billysbilling.com/v2` reconfirmed binary and JSON POST **401**,
singular PUT/DELETE **405**, attachments DELETE **200** meta-only (not cleanup
proof).

Research arithmetic and ownership match the freeze:

- Registry **265 → 267** after product.
- Offline coverage **180 → 182** only when **both** special and create-alias rows
  receive real suite evidence (alias does not inherit green).
- Module `src/billy_mcp/api/file_upload_writes.py`, narrow client binary POST,
  direct ticket binding with `file_path` + `file_digest` and size/mtime
  revalidation; not JSON `WriteOperationSpec`.
- No `api_files_create*`, no multipart form, no bulk bodies, no webhook invention,
  no `api.billy.dk` client base.

## Product gate

This ACCEPT opens offline Codex Power product implementation for the two upload
tools. It is not product ACCEPT, live qualification, UI/vision acceptance, bulk
resolution, or completeness.

After product integrates at root, a separate independent Grok product review
must confirm registry **267**, coverage **182** offline with dual-row greening
only by real suites, ticket path/digest/size/mtime safety, binary allowlisted
headers, redacted `downloadUrl`, and fail-closed live/UI/bulk.

No browser was launched, no credential or customer data was used, and no raw
browser evidence is retained. Coverage remains 180/180/0/0 with
`complete: false` until product and tests land.

## Non-claims

- Not product ACCEPT.
- Codex Power fallback freeze review remains non-authoritative for the mandatory
  Grok audit (this page is the Grok product-ready ACCEPT).
- Completeness remains **FAIL**.
