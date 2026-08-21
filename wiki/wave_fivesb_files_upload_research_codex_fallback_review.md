---
name: wave_fivesb_files_upload_research_codex_fallback_review
title: Wave-5s-B files-upload Codex fallback review
desc: Non-authoritative Codex Power review accepting the cited offline files-upload research handoff only; product and mandatory Grok audit remain open.
tags: [billy, api, files, upload, research, review, offline]
sources:
  - wiki/wave_fivesb_files_upload_research.md
  - wiki/wave_fives_residual_specials_research.md
  - docs/superpowers/specs/2026-07-28-billy-mcp-complete-design.md
  - coverage/api_v2_manifest.yaml
  - coverage/ui_workflows_manifest.yaml
  - coverage/status.json
  - src/billy_mcp/client.py
  - src/billy_mcp/config.py
  - src/billy_mcp/confirmations.py
  - src/billy_mcp/api/write_protocol.py
  - src/billy_mcp/redaction.py
  - coverage/browser_egress.yaml
  - tests/unit/test_client.py
  - tests/unit/test_confirmations.py
  - tests/unit/test_config.py
  - tests/unit/test_write_protocol.py
  - tests/coverage/test_coverage_inventory.py
  - tests/api/test_file_attachment_reads.py
  - tests/unit/test_redaction_errors.py
created: 2026-07-30T17:14:27Z
updated: 2026-07-30T17:16:21Z
---

# Wave-5s-B files-upload Codex fallback review

## Verdict and authority

**ACCEPT — limited to the Wave-5s-B offline research handoff.** This is a
Codex Power fallback review of parent baseline `5b8719b`, conducted because the
assigned external reviewer failed authentication before making edits. It is
useful independent review evidence, but it is **not** Grok evidence, does not
satisfy the mandatory Grok audit, and is not product approval.

The reviewed research accurately keeps the binary files special bounded to the
documented wire contract and records the prerequisite safety work rather than
claiming it exists. No actionable defect was found in that research boundary.

## Evidence boundary

The primary record, [[wave_fivesb_files_upload_research]], preserves the cited
official-document snapshot: `https://www.billy.dk/api/`, 200 response,
ETag `"wcw4x9hqvu3603"`, 147934 bytes, and MD5
`8b94b0135c91fd15fe54ea33e088a4be`. It also explains that the inventory's older
ETag/MD5 are an access/CDN-drift metadata difference. This review verified the
preserved record and its agreement with the repository inventory; it did **not**
re-fetch the official site, make a live API call, use credentials, open a
browser, or create records.

[[wave_fives_residual_specials_research]] independently preserves the same
snapshot and ranks the files special as the second residual offline product,
after the read-only invoiceLogs special. Its files section matches the dedicated
research page and does not enlarge the contract.

## Contract comparison

| Research claim | Repository evidence at `5b8719b` | Review result |
| --- | --- | --- |
| The only documented upload is `POST /v2/files` with **raw file bytes**, not a JSON resource create. | The dedicated and residual research pages agree. The manifest has the same route, fields, response roots, and high side-effect classification for both ownership rows. | **Verified as preserved research.** No JSON `{file: ...}` create, generic endpoint, or webhook is inferred. |
| The API destination remains `https://api.billysbilling.com/v2`; sample host `api.billy.dk` is not a client base. | `API_BASE_URL` is a literal in `config.py`; `BillyHttpClient._url_for` rejects scheme, netloc, query, fragment, traversal, and duplicate `/v2`; `browser_egress.yaml` gives `api.billy.dk` deny/deny and makes the official API host API-client exclusive. `test_client.py` exercises the alias-host and fixed-prefix rejection. | **Verified.** A future binary method must retain this fixed-host, relative-`/files` boundary. |
| `api.special.files_upload` owns the one preview/execute family, while `api.files.create` is only its alias. `api_files_create*` is forbidden. | `api.files.create` has `alias_of: api.special.files_upload` and no tool name; the special row plans `api_files_upload_preview`. `check_coverage.py` and `test_coverage_inventory.py` reject a second files-create name and divergence in their shared wire metadata. | **Verified.** The two rows are ownership/accounting, not two upload implementations. |
| Required wire data are client auth, `X-Filename`, `Content-Type`, and raw bytes; the four documented optional headers are attachment, variants, organisation, and scan. Success requires `files[]` and may include `attachments[]`. | Both rows preserve the same `request_fields` and `response_fields`; the research page explicitly says `X-Access-Token` is client-owned rather than a tool input. Existing `file_attachment_reads.py` models file/attachment records as opaque, and redaction covers `downloadUrl`. | **Verified as a wire-contract record.** Manifest `request_fields` are inventory metadata, not permission to expose the token or an arbitrary header map. |
| Preview is no-write and execute is ticket-only. The exact binding covers the execute tool, organisation, canonical options, canonical file path, and SHA-256 digest; file checks cover an allowed root, regular file, size, and mtime, and execute repeats them. | The approved design §§8.1–8.4 requires ticket-only execution, exact operation/file identity, and repeat validation. `ConfirmationBinding` supports tool, organisation, request, canonical path, and digest; `ConfirmationStore` is opaque, single-use, and at most five minutes. Its unit tests mutate each bound field. `AppConfig` canonicalises `BILLY_UPLOAD_ROOTS`. | **Verified as a required implementation condition, not a delivered capability.** The generic JSON `WriteProtocolService` deliberately sets file fields to `None`; a product upload path must not claim this generic protocol alone performs file identity or revalidation. |
| A product needs a narrow binary client path with allowlisted headers and no POST retry, not a permissive client extension. | `BillyHttpClient.request` currently sends `json=` only and retries only `GET`/`HEAD`; tests assert a POST is attempted exactly once. No upload registrar, upload tool, binary client method, or upload contract-test module exists. | **Verified non-claim.** The research accurately identifies this as future work rather than silently treating JSON writes as upload support. |
| Download tokens and hosts require narrow treatment. | `redaction.py` redacts `downloadUrl`; its test covers a token-bearing `download.billy.dk` URL. Egress allows that host only for a future typed-download workflow and otherwise denies by default. | **Verified.** This does not authorize generic download, navigation, or an alternate upload host. |

The research's use of the generic word `tool` for ticket binding is read as the
matching **execute** tool: the design requires execute to accept only the
ticket, and the confirmation test fixture names `api_files_upload_execute`.
It does not authorize replacement path, filename, content type, flags,
organisation, headers, or a destination URL at execution time.

## Red status and product absence

The evidence remains explicitly red:

- `api.files.create` and `api.special.files_upload` are each `implemented:
  false`, `contract_tested: false`, and `live_tested: false` in
  `coverage/api_v2_manifest.yaml`. The create row has no tool name; the special
  row only reserves `api_files_upload_preview`.
- UI parity rows `ui.parity.files.create` and
  `ui.parity.special.files_upload` are discovery-required and all
  implementation, contract, live, and vision states are false.
- `coverage/status.json` reports `complete: false`, 180 implemented and
  contract-tested rows overall, zero live-tested rows, zero vision-verified
  rows, 92 ambiguous bulk rows, and 339 UI rows. The files bulk rows therefore
  remain unresolved; this review does not green any row.
- The file-specific read registrar contains exactly four file/attachment read
  tools; no upload preview/execute pair is registered. Neither a binary POST
  nor ticketed file revalidation is present today.

## Command evidence

All commands were local and read-only with respect to product behaviour:

| Command | Result |
| --- | --- |
| `uv run pytest tests/unit/test_client.py tests/unit/test_confirmations.py tests/unit/test_config.py tests/unit/test_write_protocol.py tests/coverage/test_coverage_inventory.py tests/api/test_file_attachment_reads.py tests/unit/test_redaction_errors.py` | **87 passed**. Confirms fixed-host/path, token/confirmation semantics, upload-root configuration, no-retry writes, dual-row inventory guard, file-read layout, and redaction conventions. |
| `uv run python scripts/check_coverage.py --reject-false-completeness` | **Passed** — 305 API rows and 339 UI rows. This validates inventory consistency, not product completeness. |
| `uv run pytest` | **1180 passed**. Offline suite only; it contains no files-upload product suite or live qualification. |
| `uv run python scripts/check_coverage.py --require-complete` | **Expected exit 1** — `complete=false`; 92 ambiguous bulk rows remain; 305 API rows lack all live evidence; 339 UI rows lack required qualification/vision evidence. This is the correct fail-closed result. |
| Node `scripts/test.sh` and `scripts/lint.sh`; `uv run ruff check .`; `uv run pyright`; `uv run python scripts/check_repository_policy.py` | **Passed.** The seeded test script intentionally has no extra command. The lint wrapper reports that the project wiki index would need regeneration for this new page, but exits successfully; `wiki update` was deliberately not run because this review is forbidden from changing the existing `wiki/_index.md`. Ruff, Pyright, and repository-policy checks pass. |

## Explicit non-claims and remaining gates

This acceptance does **not** deliver or approve product implementation, a live
API upload, UI parity, browser work, vision evidence, bulk behaviour, webhook
behaviour, cleanup proof, or overall completeness. It also does not validate
the cited unauthenticated probes anew.

Before any product verdict, the project still needs a deliberately scoped
binary upload implementation and its offline contract tests, an evidence-backed
coverage update for both owned rows, any safe live qualification and cleanup
plan, applicable UI/vision work, continued bulk red status until documented,
and the separate mandatory **Grok** audit. None of those gates is discharged by
this page.
