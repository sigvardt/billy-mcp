---
name: wave_fivesa_invoice_logs_product_codex_fallback_review
title: Wave-5s-A invoiceLogs product Codex fallback review
desc: Offline-only Codex Power fallback review of the merged invoiceLogs list product at baseline 5b8719b; accepted only for bounded offline product quality and not a Grok audit or completeness claim.
tags: [billy, api, invoice_logs, review, codex, fallback, offline]
sources:
  - wiki/wave_fivesa_invoice_logs_list_research.md
  - wiki/wave_fivesa_invoice_logs_research_independent_review.md
  - docs/superpowers/specs/2026-07-28-billy-mcp-complete-design.md
  - src/billy_mcp/api/invoice_log_reads.py
  - tests/api/test_invoice_log_reads.py
  - src/billy_mcp/server.py
  - coverage/api_v2_manifest.yaml
  - coverage/ui_workflows_manifest.yaml
  - coverage/status.json
created: 2026-07-30T17:12:10Z
updated: 2026-07-30T17:12:10Z
---

# Wave-5s-A invoiceLogs product Codex fallback review

## Scope, authority, and baseline

**Verdict: ACCEPT for bounded offline product quality.** This review accepts the
merged, read-only `api_invoice_logs_list` implementation as matching the cited
offline contract. It is a Codex Power fallback review after the assigned Grok
reviewer failed authentication before making edits. It is **not** Grok review
evidence, does not satisfy the mandatory Grok product audit, and must not be
used as that audit's substitute.

The reviewed product baseline is parent commit `5b8719b`; `git merge-base
--is-ancestor 5b8719b HEAD` exited 0, and `git diff --name-status
5b8719b..HEAD` contained only this node's orchestration seed. The source,
tests, manifests, and generated coverage therefore came from that merged
baseline rather than from review-branch product edits.

The authority for the API contract is the cited research page, not a new API
probe: it freezes this exact list-only special and expressly limits itself to
research evidence (wiki/wave_fivesa_invoice_logs_list_research.md:23-33). Its
cited research review accepted that handoff only as research, not product or
completeness evidence (wiki/wave_fivesa_invoice_logs_research_independent_review.md:25-43).
The approved design requires registered tools to be real and typed, with stable
names, error codes, coverage rows, and risk-appropriate tests
(docs/superpowers/specs/2026-07-28-billy-mcp-complete-design.md §5.3).

No live HTTP request, browser/vision work, credential use, disposable data, or
coverage greening was performed in this review. The focused tests use an
in-process `httpx.MockTransport` (tests/api/test_invoice_log_reads.py:41-66).

## Contract checked

The cited contract permits exactly one read-only tool for
`GET /v2/invoiceLogs` with `invoiceId`, `organizationId`,
`sortProperty=eventTime`, and `sortDirection=DESC`; it documents no paging and
forbids a singular get and writes in this offline slice
(wiki/wave_fivesa_invoice_logs_list_research.md:61-74,86-98). It says the
`invoiceLogs[]` entries remain opaque outside the documented sample fields and
leaves several questions for live qualification, including organisation-token
optionality, additional sorts, paging, and a complete entry schema
(wiki/wave_fivesa_invoice_logs_list_research.md:95,100-107).

This review did not turn those unknowns into requirements. In particular, it
does not claim that `organizationId` is live-required, that the sample is the
full response schema, or that non-sample filtering/paging is unsupported by
Billy at runtime.

## Confirmed findings

| ID | Severity | Confirmed finding and evidence | Disposition |
| --- | --- | --- | --- |
| F-01 | none | The request model forbids undeclared controls, requires non-empty `invoiceId` and `organizationId`, and constrains both sort values to the cited sample (src/billy_mcp/api/invoice_log_reads.py:15-27). The service sends only those four controls to relative `/invoiceLogs` with GET (src/billy_mcp/api/invoice_log_reads.py:50-65); the locked client adds the fixed v2 base and rejects a caller-supplied `/v2` prefix or absolute URL (src/billy_mcp/client.py:81-101,130-139). | Matches the documented offline route and query boundary. |
| F-02 | none | The success envelope is typed as `invoiceLogs: list[InvoiceLogEntry]`; entries deliberately allow additional upstream fields, while only a mapping under the documented `invoiceLogs` root is accepted. Malformed envelopes or entries return the stable typed Billy error (src/billy_mcp/api/invoice_log_reads.py:30-41,99-128). This preserves the cited opaque-entry boundary rather than inventing a complete schema. | Matches the cited response boundary. |
| F-03 | none | The module registers only `api_invoice_logs_list` with a typed signature and metadata (src/billy_mcp/api/invoice_log_reads.py:72-96). The production server imports and invokes that registrar (src/billy_mcp/server.py:43,105-122). The registry suite includes the one-name Wave-5s-A set and asserts 265 API tools (tests/unit/test_coverage_server.py:327,457-504). An offline `create_server().list_tools()` check reported 267 total tools (265 `api_*` plus two coverage tools) and the expected strict input schema. | Wiring and callable metadata verified. |
| F-04 | none | Focused tests assert the exact outgoing query and preserve unknown entry fields (tests/api/test_invoice_log_reads.py:73-102), reject missing, empty, paging, non-sample sort, and undeclared query controls (tests/api/test_invoice_log_reads.py:105-142), preserve typed authentication errors (tests/api/test_invoice_log_reads.py:174-192), and verify the registered tool's strict schema and structured result (tests/api/test_invoice_log_reads.py:195-241). | Contract and error behaviour are locally substantiated. |
| F-05 | none | Generator evidence binds `api.special.invoice_logs` to the focused suite and server registry test (scripts/generate_coverage_report.py:280-292); its generated manifest row records the exact special route, field list, tool name, `implemented: true`, `contract_tested: true`, and `live_tested: false` (coverage/api_v2_manifest.yaml:12028-12072). The inventory test enforces that implementation and contract-tested flags arise only from this evidence map and keeps live testing false (tests/coverage/test_coverage_inventory.py:150-165). | Offline evidence is honest; it is not a live green. |

No confirmed offline product defect was found within this review's bounded
contract. The findings above are positive verification findings, not a claim
that the wider product is complete.

## Coverage and lane status

Coverage is correctly fail-closed. `coverage/status.json` records 180
implemented and contract-tested rows, zero live-tested and vision-verified
rows, 92 ambiguous bulk rows, 305 API rows, 339 UI rows, and `complete: false`
(coverage/status.json:1-24). The current special row has `vision_verified:
null`, which is appropriate for an API row; its required `live_tested` field
remains false (coverage/api_v2_manifest.yaml:12031-12072).

The corresponding UI-parity row is still unimplemented, undiscovered,
un-tested, non-live, and non-vision-verified, with `discovery_required` status
(coverage/ui_workflows_manifest.yaml:13035-13078). This is consistent with the
approved design's separate API and interface lanes and its rule that an API row
requires live testing while a UI row additionally requires vision verification
(docs/superpowers/specs/2026-07-28-billy-mcp-complete-design.md §§5.2,12.1-12.3).

## Reproduced local evidence

| Command | Result |
| --- | --- |
| `uv run pytest tests/api/test_invoice_log_reads.py tests/unit/test_coverage_server.py tests/coverage/test_coverage_inventory.py` | 32 passed. |
| `uv run ruff check src/billy_mcp/api/invoice_log_reads.py src/billy_mcp/server.py tests/api/test_invoice_log_reads.py tests/unit/test_coverage_server.py tests/coverage/test_coverage_inventory.py scripts/generate_coverage_report.py` | Passed. |
| `uv run pyright src/billy_mcp/api/invoice_log_reads.py src/billy_mcp/server.py tests/api/test_invoice_log_reads.py` | 0 errors, warnings, and information messages. |
| `uv run python scripts/generate_coverage_report.py` | Current generated artifacts verified as 305 API rows, 339 UI rows, `complete=False`; no coverage artifact changed. |
| `uv run python scripts/check_coverage.py --reject-false-completeness` | Passed. |
| `uv run python scripts/check_coverage.py --require-complete` | Exited 1 as intended: `complete` is false, 92 bulk rows remain, and live/UI qualification is incomplete. |
| Offline FastMCP `create_server().list_tools()` inspection | 267 total tools, including `api_invoice_logs_list`; its parameter schema has exactly the two required non-empty IDs, fixed/defaulted `eventTime` and `DESC`, and `additionalProperties: false`. |

## Explicit non-claims and remaining gates

- No live Billy API qualification was run or established.
- No UI workflow, browser, or vision qualification was run or established.
- No bulk operation was resolved or qualified; 92 remain ambiguous.
- No whole-product or release-completeness claim is made; generated
  `coverage/status.json` remains `complete: false`.
- No mandatory Grok product audit occurred. That audit remains unfulfilled and
  is still required independently of this fallback acceptance.
- This review does not claim a full-suite result beyond the focused local tests
  listed above.

The offline acceptance therefore permits only the stated product-quality
conclusion. It neither opens any missing live/UI/bulk/completeness gate nor
changes their recorded status.
