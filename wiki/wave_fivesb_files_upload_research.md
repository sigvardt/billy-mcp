---
name: wave_fivesb_files_upload_research
title: Wave-5s-B files upload research
desc: Cited offline contract for ticketed binary POST /files special and aliased files.create row; path and digest bound preview or execute; no coverage greening.
tags: [billy, api, specials, files, upload, research, offline]
sources:
  - https://www.billy.dk/api/
  - https://api.billysbilling.com/v2
  - docs/superpowers/specs/2026-07-28-billy-mcp-complete-design.md
  - wiki/wave_fives_residual_specials_research.md
  - wiki/offline_write_probe_rules.md
  - coverage/api_v2_manifest.yaml
  - coverage/status.json
  - src/billy_mcp/confirmations.py
  - src/billy_mcp/config.py
  - scripts/check_coverage.py
  - "parent scratch: .fractal/main.billy_complete/tmp/grok-research.md (research79)"
created: 2026-07-30T16:45:00Z
updated: 2026-07-30T16:45:00Z
---

# Wave-5s-B files upload research

## Authority boundary

This page freezes **research evidence** for the binary file upload special after
Wave-5s-A invoiceLogs research acceptance. It is not product ACCEPT, live
qualification, UI/vision work, bulk resolution, or completeness. It does not
green coverage.

Full probe matrices and the operator brief live at
`.fractal/main.billy_complete/tmp/grok-research.md` (research79). Residual
ranking: [[wave_fives_residual_specials_research]].

## Gate status

| Gate | Status |
| --- | --- |
| Wave-5r product IR | **ACCEPT** offline |
| Wave-5s residual ranking | **ACCEPT as research** |
| Wave-5s-A invoiceLogs research IR | **ACCEPT as research** |
| Wave-5s-A product | **In flight** on child (not root-merged at research time) |
| Wave-5s-B files upload research | **Ready** (this page) |
| Root offline baseline | 179 implemented + contract_tested; live 0; vision 0; `complete: false` |

## Official docs fingerprint

| Field | Value |
| --- | --- |
| URL | https://www.billy.dk/api/ |
| HTTP | 200 |
| ETag | `"wcw4x9hqvu3603"` |
| Body bytes | 147934 |
| MD5 | `8b94b0135c91fd15fe54ea33e088a4be` |
| Note | Byte-identical to research78 HTML body |

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

## Wire contract

```http
POST /v2/files
```

Body: **raw file bytes** (not JSON). Headers from official sample and narrative:

| Header | Required | Notes |
| --- | --- | --- |
| `X-Access-Token` | yes (client) | Never a tool input |
| `X-Filename` | yes | Tool `filename` |
| `Content-Type` | yes | Tool `content_type` |
| `x-create-attachment` | optional | Emit `"true"` when requested |
| `x-create-variants` | optional | Emit `"true"` when requested |
| `x-organizationid` | optional offline | Ticket-bound when provided |
| `x-should-scan` | optional | Narrative header for extraction |

Success roots: required `files[]`; optional `attachments[]` when attachment
creation is enabled. Records stay opaque (`extra="allow"`). Redact token-like
`downloadUrl` values.

Supports table: get, list, create, bulk save, bulk delete. Property table all
**readonly** — JSON property create is not documented. Singular update/delete
unauth probes return **405**. Bulk remains ambiguous.

## MCP tools

| Tool | Role |
| --- | --- |
| `api_files_upload_preview` | Resolve path under `BILLY_UPLOAD_ROOTS`, hash SHA-256, bind ticket, no HTTP |
| `api_files_upload_execute` | Ticket only; revalidate path/digest; binary POST `/files` |

Preview fields (strict): `path`, `filename`, `content_type`, optional
`create_attachment`, `create_variants`, `organization_id`, `should_scan`.

Ticket binds tool, organisation, canonical request options, `file_path`,
`file_digest` (SHA-256). Design §8.4 also requires regular-file, size, and mtime
revalidation on execute (`FILE_NOT_ALLOWED`, `FILE_CHANGED`).

## Unauthenticated probes (2026-07-30T16:44:44Z)

Base `https://api.billysbilling.com/v2`, no token, no persistent records.
Detail: `tmp/write-probes-research79.json`.

| Probe | Result |
| --- | --- |
| Binary POST `/files` with documented headers | **401** AUTHENTICATION_REQUIRED |
| JSON POST `/files` | **401** (does not authorise JSON create) |
| PUT/DELETE `/files/:id` | **405** |
| DELETE `/attachments/:id` | **200** meta-only (not cleanup proof) |

## Client implementation note

`BillyHttpClient` currently sends JSON only. Product must add a narrow binary
POST with allowlisted headers. No generic header map. No retries on POST. No
alternate host.

## Bounded Codex Power slice

1. Finish Wave-5s-A product IR before or in parallel only if ownership stays
   disjoint; root merge of logs first is preferred.
2. **Wave-5s-B product:** ticketed upload pair + client binary path + dual-row
   offline green for special + alias create.
3. Later **Wave-5s-C:** invoice email + delivery specials.
4. Keep transactions, 405 false friends, bankPayments delete, and bulk red
   offline.

## Non-claims

- No coverage greening from this page.
- No live, UI, vision, or completeness claims.
- No webhook API.
- No headed browser and no disposable records in research.
