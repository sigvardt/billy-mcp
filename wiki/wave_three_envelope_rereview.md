---
name: wave_three_envelope_rereview
desc: PASS — both prior findings closed at 7965072 (8 flat inputs; files/attachments meta.paging preserved; coverage still red).
tags: [billy, api, review, wave3, envelope]
sources:
  - https://www.billy.dk/api/
  - wiki/wave_three_unfiltered_reads_contract.md
  - src/billy_mcp/api/file_attachment_reads.py
  - src/billy_mcp/api/catalog_reads.py
  - coverage/status.json
  - coverage/api_v2_manifest.yaml
created: 2026-07-29T11:52:00Z
updated: 2026-07-29T11:55:00Z
---

# wave_three_envelope_rereview

Independent Grok re-review of Wave-3 tool-surface corrections at revision
`7965072` (`main.billy_complete: correct Wave-3 tool contract envelopes`).

**Verdict: PASS. Both prior findings are CLOSED.** This page is not a live,
UI, vision, or product-completeness claim.

## Official documentation fingerprint

| Field | Value |
| --- | --- |
| Source | https://www.billy.dk/api/ |
| etag | `hsisik4g9p3603` |
| body MD5 | `c2efda0ee4cf9cf200e14910c5fc6996` |
| bytes | `147934` |
| Checked at | 2026-07-29 (headless GET, this re-review) |

Matches `coverage/status.json` → `official_docs` and the freeze cited in
`wiki/wave_three_unfiltered_reads_contract.md`.

Official paging rule (docs Paging section): collection truncation is reported
under the response key `meta.paging` (not a top-level `paging` field). List
query params remain `page` and `pageSize` (max 1000).

## Finding 1 — nested `request` inputs → CLOSED

Prior defect: FastMCP registration bound service methods whose single pydantic
argument was named `request`, so clients saw a nested `request` object instead
of documented flat fields.

At `7965072`, each of the eight tools is registered via thin wrappers with
explicit flat parameters. In-process FastMCP `FunctionTool.parameters` on HEAD
confirms no `request` property:

| Tool | Input property keys | Nested `request`? |
| --- | --- | --- |
| `api_files_get` | `id`, `include` | no |
| `api_files_list` | `page`, `pageSize`, `include`, `sortProperty`, `sortDirection` | no |
| `api_attachments_get` | `id`, `include` | no |
| `api_attachments_list` | `page`, `pageSize`, `include`, `sortProperty`, `sortDirection` | no |
| `api_products_get` | `id`, `include` | no |
| `api_products_list` | `page`, `pageSize`, `include`, `sortProperty`, `sortDirection` | no |
| `api_product_prices_get` | `id`, `include` | no |
| `api_product_prices_list` | `page`, `pageSize`, `include`, `sortProperty`, `sortDirection` | no |

Source: `register_file_attachment_read_tools` and `register_catalog_read_tools`
in `src/billy_mcp/api/file_attachment_reads.py` and
`src/billy_mcp/api/catalog_reads.py`. Pre-correction (`a206eb0`) registered
`service.files_list` / `service.products_list` directly; `7965072` registers
the flat wrappers instead.

**Filters not widened:** list wire params remain only `page`, `pageSize`,
optional `include`, `sortProperty`, `sortDirection` (`ASC`|`DESC`). No
`offset`, parent-id, or resource-specific filters appear in
`_list_params` for either module. Contract tests reject invented filters
(`tests/api/test_file_attachment_reads.py`, `tests/api/test_catalog_reads.py`).

## Finding 2 — files/attachments `meta.paging` → CLOSED

Prior defect: list success models exposed top-level `paging`, flattening the
official optional `meta.paging` envelope.

At `7965072`:

- `FilesListSuccess` / `AttachmentsListSuccess` expose optional `meta:
  FileAttachmentMeta` with nested optional `paging` (not top-level `paging`).
- `_meta_from_response` reads payload key `meta` only.
- FastMCP structured tool result for mocked list responses:

```json
{"files":[{"id":"x1"}],"meta":{"paging":{"page":1,"pageSize":20}}}
```

```json
{"attachments":[{"id":"a1"}],"meta":{"paging":{"page":1,"pageSize":20}}}
```

No top-level `paging` key on either payload. Output schema `$defs` for
`FilesListSuccess` / `AttachmentsListSuccess` require `files`/`attachments` and
optional `meta.paging` only.

Focused contract test
`test_list_tool_preserves_the_documented_meta_paging_envelope` asserts the same
shape via `server.call_tool("api_files_list", ...)`.

## Coverage non-regression (truthful reds preserved)

| Check | Observed at `7965072` |
| --- | --- |
| `coverage/status.json` `complete` | `false` |
| `live_tested_rows` | `0` |
| `vision_verified_rows` | `0` |
| Docs fingerprint in status | etag `hsisik4g9p3603` / MD5 `c2efda0ee4cf9cf200e14910c5fc6996` |
| Eight get/list rows (files, attachments, products, productPrices) | `implemented=true`, `contract_tested=true`, **`live_tested=false`** |
| Writes/bulk for same areas | still `implemented=false`, `live_tested=false` |
| UI workflows | **0** implemented/live/vision greens (339 rows remain red) |

The correction commit touches only catalog/file-attachment modules, their
tests, phase-zero wiki note, and node memory — not coverage greening.

## Out-of-scope residual (not either prior finding)

`api_products_list` and `api_product_prices_list` still map upstream
`meta.paging` into a **top-level** success field `paging` (reads from
`meta.paging` in `_paging_from`, then flattens). That shape is **outside** the
two findings this re-review was scoped to close (finding 2 named only
`api_files_list` / `api_attachments_list`). It is recorded here so a later
catalog-envelope pass can align products with the official `meta.paging` key if
desired. It does **not** reopen finding 1 or 2.

## Evidence method

- Headless official docs GET + etag/MD5/size.
- Source review of `file_attachment_reads.py` / `catalog_reads.py` at HEAD.
- In-process FastMCP: `get_tool(...).parameters` and `call_tool` structured
  content with a fake client (no credentials, no network to Billy API host).
- Coverage files read-only; focused pytest: 23 passed for the two modules.
- Frozen contract: `wiki/wave_three_unfiltered_reads_contract.md`.

## Claims not made

No live Billy API success, no UI workflow, no vision frame, no bulk
qualification, and no `complete=true` claim. `BILLY_API_TOKEN` was not used.
