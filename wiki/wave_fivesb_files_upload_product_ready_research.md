---
name: wave_fivesb_files_upload_product_ready_research
title: Wave-5s-B files upload product-ready research
desc: Product-ready offline handoff for ticketed binary POST /files special and dual-row create alias; path/digest/size/mtime binding; no coverage greening.
tags: [billy, api, specials, files, upload, research, product-ready, offline]
sources:
  - https://www.billy.dk/api/
  - https://api.billysbilling.com/v2
  - docs/superpowers/specs/2026-07-28-billy-mcp-complete-design.md
  - wiki/wave_fives_residual_specials_research.md
  - wiki/wave_fivesb_files_upload_research.md
  - wiki/offline_write_probe_rules.md
  - coverage/api_v2_manifest.yaml
  - coverage/status.json
  - src/billy_mcp/confirmations.py
  - src/billy_mcp/client.py
  - src/billy_mcp/config.py
  - scripts/check_coverage.py
  - scripts/generate_coverage_report.py
  - "parent scratch: .fractal/main.billy_complete/tmp/grok-research.md (research80)"
created: 2026-07-30T17:14:33Z
updated: 2026-07-30T17:26:00Z
---

# Wave-5s-B files upload product-ready research

## Authority boundary

This page freezes **product-ready research** for the binary file upload special
after the freeze page [[wave_fivesb_files_upload_research]] and after Wave-5s-A
invoiceLogs product merge. It is not product ACCEPT, live qualification,
UI/vision work, bulk resolution, or completeness. It does not green coverage.

Full probe matrices and the operator brief live at
`.fractal/main.billy_complete/tmp/grok-research.md` (research80). Residual
ranking: [[wave_fives_residual_specials_research]].

## Gate status

| Gate | Status |
| --- | --- |
| Wave-5r product IR | **ACCEPT** offline |
| Wave-5s residual ranking | **ACCEPT as research** |
| Wave-5s-A invoiceLogs product | **Merged** on root |
| Wave-5s-B files upload freeze research | **Ready** ([[wave_fivesb_files_upload_research]]) |
| Wave-5s-B product-ready research | **Ready** (this page) |
| Wave-5s-B product-ready independent review | **ACCEPT** offline ([[wave_fivesb_files_upload_product_ready_research_independent_review]]) |
| Root offline baseline | 180 implemented + contract_tested; live 0; vision 0; `complete: false`; registry 265 |

## Official docs fingerprint

| Field | Value |
| --- | --- |
| URL | https://www.billy.dk/api/ |
| HTTP | 200 |
| ETag | `"wcw4x9hqvu3603"` |
| Body bytes | 147934 |
| MD5 | `8b94b0135c91fd15fe54ea33e088a4be` |
| Note | Byte-identical to research79 HTML body |

Inventory lock metadata in `coverage/status.json` still cites ETag
`hsisik4g9p3603` / MD5 `c2efda0ee4cf9cf200e14910c5fc6996` (access/CDN drift only).

API base remains locked to `https://api.billysbilling.com/v2`. Sample upload curl
host `api.billy.dk` must never become the client base.

## Dual inventory rows

| Inventory id | tool_name | Rule |
| --- | --- | --- |
| `api.special.files_upload` | `api_files_upload_preview` (+ execute twin) | Owns the tool family |
| `api.files.create` | empty | `alias_of: api.special.files_upload` only |

Forbidden: any `api_files_create*` tool. Checker enforces shared wire
request_fields list and the alias relationship.

**Greening:** `OFFLINE_API_IMPLEMENTATION_EVIDENCE` must list **both** row ids
after contract tests pass. Alias does not inherit green from the special alone.

## Wire contract

```http
POST /v2/files
```

Body: **raw file bytes** (not JSON). Headers:

| Header | Required | Notes |
| --- | --- | --- |
| `X-Access-Token` | yes (client) | Never a tool input |
| `X-Filename` | yes | Tool `filename` |
| `Content-Type` | yes | Tool `content_type` |
| `x-create-attachment` | optional | Emit `"true"` when requested; omit otherwise |
| `x-create-variants` | optional | Emit `"true"` when requested; omit otherwise |
| `x-organizationid` | optional offline | Ticket-bound when provided |
| `x-should-scan` | optional | Narrative header for extraction |

Success roots: required `files[]`; optional `attachments[]`. Records opaque
(`extra="allow"`). Redact `downloadUrl`.

Supports table: get, list, create, bulk save, bulk delete. Property table all
**readonly**. Singular update/delete unauth probes return **405**. Bulk remains
ambiguous.

## Product shape (Codex)

| Item | Decision |
| --- | --- |
| Tools | `api_files_upload_preview` / `api_files_upload_execute` |
| Module | `src/billy_mcp/api/file_upload_writes.py` (new) |
| Client | Narrow binary POST on `BillyHttpClient`; allowlisted headers; no retries |
| Protocol | Dedicated ticket path with `file_path` + `file_digest`; not JSON `WriteOperationSpec` |
| Design §8.4 | Resolve path under `BILLY_UPLOAD_ROOTS`, regular file, size, mtime, SHA-256; revalidate on execute (`FILE_NOT_ALLOWED`, `FILE_CHANGED`) |
| Registry | 265 → 267 |
| Coverage target offline | 180 → 182 (special + create alias) |
| Out of scope | email/delivery specials, bulk, UI, live, webhooks, `api.billy.dk` base |

## Unauthenticated probes (2026-07-30T17:14:33Z)

Base `https://api.billysbilling.com/v2`, no token, no persistent records.
Detail: `tmp/write-probes-research80.json`.

| Probe | Result |
| --- | --- |
| Binary POST `/files` with documented headers | **401** AUTHENTICATION_REQUIRED |
| JSON POST `/files` | **401** (does not authorise JSON create) |
| PUT/DELETE `/files/:id` | **405** |
| DELETE `/attachments/:id` | **200** meta-only (not cleanup proof) |

## Bounded Codex Power slice

1. Client binary POST + file identity helpers.
2. Ticketed upload pair + dual-row offline green for special + alias create.
3. Contract tests for path/digest/size/mtime, ticket safety, header allowlist, registry +2.
4. Later **Wave-5s-C:** invoice email + delivery specials.
5. Keep transactions, 405 false friends, bankPayments delete, and bulk red offline.

## Non-claims

- No coverage greening from this page.
- No live, UI, vision, or completeness claims.
- No webhook API.
- No headed browser and no disposable records in research.
