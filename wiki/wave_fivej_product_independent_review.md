---
name: wave_fivej_product_independent_review
title: Wave-5j offline product independent fallback review ACCEPT
desc: Independent Codex fallback acceptance of the offline bank-line ticketed-write product at root integration d86844f.
tags: [billy, api, bank, writes, review, coverage]
sources:
  - https://www.billy.dk/api/
  - wiki/wave_fivej_ticketed_writes_contract.md
  - wiki/wave_fivej_freeze_independent_review.md
  - wiki/wave_fivej_product_ready_research_independent_review.md
  - wiki/offline_write_probe_rules.md
  - .fractal/main.billy_complete/tmp/grok-research.md
  - src/billy_mcp/api/bank_line_writes.py
  - src/billy_mcp/api/write_protocol.py
  - src/billy_mcp/client.py
  - src/billy_mcp/server.py
  - tests/api/test_bank_line_writes.py
  - tests/api/test_bank_line_cross_executor.py
  - coverage/api_v2_manifest.yaml
  - coverage/status.json
created: 2026-07-30T03:11:54Z
updated: 2026-07-30T03:11:54Z
---

# Wave-5j offline product independent fallback review ACCEPT

## Verdict and review boundary

**ACCEPT — the Wave-5j offline product slice only** for parent integration
`d86844f`, reviewed on the recorded gate handoff `5a42c0f`.

Grok could not perform this review because its CLI lacked credentials before it
made any edit, so this is the required independent Codex fallback review. No
production code, tests, manifests, coverage flags, or tool surface were changed
by the review.

This is not live qualification and does not establish UI parity, vision
verification, cleanup, bulk support, `bankPayments` writes, or overall
completeness. It does not itself authorize Wave-5k work. No browser, token,
organisation data, or persistent test resource was used. The cited owner-only
research handoff was not retained in either the review worktree or the permitted
parent worktree; its durable conclusions are cited by the accepted freeze and
product-ready pages, and the public-documentation fingerprint below was
independently rechecked.

## Accepted surface

The implementation registers exactly these eighteen ticketed tools:

| Inventory id | Preview handler | Execute handler | HTTP path and request root | Response mapping |
| --- | --- | --- | --- | --- |
| `api.bankLineMatches.create` | `api_bank_line_matches_create_preview` | `api_bank_line_matches_create_execute` | `POST /bankLineMatches`; `bankLineMatch` | required `bankLineMatches`; optional `bankLines` and `bankLineSubjectAssociations` only when returned |
| `api.bankLineMatches.update` | `api_bank_line_matches_update_preview` | `api_bank_line_matches_update_execute` | `PUT /bankLineMatches/:id`; `bankLineMatch` | same |
| `api.bankLineMatches.delete` | `api_bank_line_matches_delete_preview` | `api_bank_line_matches_delete_execute` | bodyless `DELETE /bankLineMatches/:id` | returned declared roots and `meta.deletedRecords` only when present |
| `api.bankLines.create` | `api_bank_lines_create_preview` | `api_bank_lines_create_execute` | `POST /bankLines`; `bankLine` | required `bankLines` only |
| `api.bankLines.update` | `api_bank_lines_update_preview` | `api_bank_lines_update_execute` | `PUT /bankLines/:id`; `bankLine` | required `bankLines` only |
| `api.bankLines.delete` | `api_bank_lines_delete_preview` | `api_bank_lines_delete_execute` | bodyless `DELETE /bankLines/:id` | returned `bankLines` and deleted metadata only when present |
| `api.bankLineSubjectAssociations.create` | `api_bank_line_subject_associations_create_preview` | `api_bank_line_subject_associations_create_execute` | `POST /bankLineSubjectAssociations`; `bankLineSubjectAssociation` | required `bankLineSubjectAssociations` only |
| `api.bankLineSubjectAssociations.update` | `api_bank_line_subject_associations_update_preview` | `api_bank_line_subject_associations_update_execute` | `PUT /bankLineSubjectAssociations/:id`; `bankLineSubjectAssociation` | required `bankLineSubjectAssociations` only |
| `api.bankLineSubjectAssociations.delete` | `api_bank_line_subject_associations_delete_preview` | `api_bank_line_subject_associations_delete_execute` | bodyless `DELETE /bankLineSubjectAssociations/:id` | returned association records and deleted metadata only when present |

The public Billy API documentation still identifies
`https://api.billysbilling.com/v2` as the API base and documents singular-root
create/update, partial PUT with ID equality, bodyless idempotent DELETE, changed
record roots, and `meta.deletedRecords`. Its three bank-line resource tables
still list these singular CUD methods. The recheck matched the frozen source:
ETag `hsisik4g9p3603`, 147934 bytes, MD5
`c2efda0ee4cf9cf200e14910c5fc6996`.

## Independent evidence

- `src/billy_mcp/api/bank_line_writes.py` uses strict, flat outer Pydantic
  inputs, opaque `JsonValue` payload maps, non-empty IDs, and validators that
  reject an inner update ID different from the route ID. Each preview owns an
  exact server-supplied execute-tool name. No handler accepts caller-selected
  method, path, payload replacement, or approval boolean.
- Its three fixed specifications use client-relative paths without `/v2`. Match
  writes alone declare optional child roots; line and association writes declare
  none. Delete previews pass `payload=None`, so the shared protocol sends no
  JSON body.
- `WriteProtocolService` keeps canonical prepared requests server-side. It
  checks `prepared.binding.tool` before `ConfirmationStore.consume`, returns
  typed `CONFIRMATION_MISMATCH` before HTTP, consumes atomically, discards the
  prepared body, and calls the client once. `BillyHttpClient` retries only GET
  and HEAD, never POST, PUT, or DELETE.
- The focused suites cover all preview/execute tool schemas, canonical request
  and effect binding, no-preview HTTP, opaque payload retention, ID mismatch,
  bodyless delete, all three CUD method/path shapes, match-only optional roots,
  no fabricated line/association roots, absent delete metadata, tamper/expiry/
  replay, typed authentication/not-found/upstream errors, and no retry. The
  root-server integration test proves both same-resource and cross-resource
  executor mismatches leave the ticket unconsumed and make no HTTP request.
- The integration diff contains the bank-line module, root registration, real
  focused tests, nine inventory evidence entries, and coverage regeneration.
  `git diff --check d86844f^ d86844f` completed cleanly.

## Commands executed and observed results

```text
printf 'etag='
curl --fail --silent --show-error --location --head https://www.billy.dk/api/ | tr -d '\r' | awk 'tolower($1) == "etag:" {value=$2} END {print value}'
# etag="hsisik4g9p3603"

curl --fail --silent --show-error --location https://www.billy.dk/api/ | wc -c
# 147934

curl --fail --silent --show-error --location https://www.billy.dk/api/ | md5 -q
# c2efda0ee4cf9cf200e14910c5fc6996

uv run pytest tests/coverage/test_coverage_inventory.py \
  tests/api/test_bank_line_writes.py \
  tests/api/test_bank_line_cross_executor.py \
  tests/unit/test_coverage_server.py
# 71 passed in 3.26s

uv run ruff check src/billy_mcp/api/bank_line_writes.py \
  src/billy_mcp/api/write_protocol.py \
  tests/api/test_bank_line_writes.py tests/api/test_bank_line_cross_executor.py
# All checks passed!

uv run pyright src/billy_mcp/api/bank_line_writes.py src/billy_mcp/api/write_protocol.py
# 0 errors, 0 warnings, 0 informations

uv run python -c "from pathlib import Path; import asyncio; from billy_mcp.server import create_server; print(len([t.name for t in asyncio.run(create_server(Path.cwd()).list_tools()) if t.name.startswith('api_')]))"
# 238

uv run python -c "from pathlib import Path; from billy_mcp.coverage import load_coverage_report; r=load_coverage_report(Path.cwd()); s=[x.status for x in r.api_rows]; print(len(s), sum(x.implemented for x in s), sum(x.contract_tested for x in s), sum(x.live_tested for x in s), r.status.complete)"
# 305 166 166 0 False

bash .fractal/main.billy_complete.wave5j_product_codex_fallback_review/scripts/test.sh
# exit 0; configured no-op node script

wiki update --path=/Volumes/ssd_1/Repositories/billy-mcp/.worktrees/main.billy_complete.wave5j_product_codex_fallback_review/wiki
# Added 1 new link; Updated 2 files.

wiki lint --path=/Volumes/ssd_1/Repositories/billy-mcp/.worktrees/main.billy_complete.wave5j_product_codex_fallback_review/wiki
# No issues found.
```

A read-only server/manifest check then reported: 305 API inventory rows; 166
implemented and 166 contract-tested; 0 live-tested; exactly 238 registered
`api_*` tools; 92 empty-tool ambiguous bulk rows; 339 UI rows with 0
implemented, contract-tested, live-tested, or vision-verified; and
`coverage/status.json` `complete: false`. All nine Wave-5j CUD rows are
implemented and contract-tested but remain `live_tested: false`.

## Explicit non-acceptance

The `bankPayments` create, update, delete, and bulk rows remain unimplemented
and untested; its preview-like inventory labels do not register a write tool.
All three bank-line bulk save/delete rows remain ambiguous, empty-tool red.
This review neither treats unauthenticated probes as valid mutations nor treats
offline tests as live, UI, vision, cleanup, or completeness qualification.
