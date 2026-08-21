---
name: wave_four_root_integration_independent_review
desc: Independent Grok review of committed Wave-4 root integration at 3f56399 — offline PASS; product completeness incomplete.
tags: [billy, api, read_only, review, wave4]
sources:
  - https://www.billy.dk/api/
  - wiki/wave_four_remaining_clear_reads_contract.md
  - docs/superpowers/specs/2026-07-28-billy-mcp-complete-design.md
  - src/billy_mcp/server.py
  - coverage/api_v2_manifest.yaml
  - coverage/status.json
created: 2026-07-29T13:05:00Z
updated: 2026-07-29T13:05:00Z
---

# wave_four_root_integration_independent_review

## Verdict

| Gate | Result |
| --- | --- |
| Offline Wave-4 root integration (50 get/list + registration + evidence) | **PASS** |
| Product completeness | **incomplete (FAIL)** |
| Live API / UI / vision / bulk / write / auth product tools | **not claimed; remain red** |

**Offline integration: PASS.** Committed archive `3f56399` registers all five Wave-4 modules, exposes exactly **94** `api_*` tools plus `coverage_status` and `coverage_report`, greened only the **94** offline read inventory rows (92 clear get/list + 2 user specials), keeps every `live_tested` false, keeps all UI/vision red, and keeps `complete: false`. Focused non-live suite **487 passed**. Full mode exits **1** only at the completeness gate (expected fail-closed).

**Product completeness: incomplete.** No live token qualification, 92 bulk rows still ambiguous, 115 clear writes still red, 4 of 6 specials still red, no `auth_*` tools, no UI/vision greens. This is expected incomplete work, not a false green.

**Concrete product discrepancies requiring code repair for the offline slice: none.** No REQUIRED rewrite of Wave-4 modules, registry, inventory evidence, redaction, host lock, or error mapping.

---

## Revision and method

| Field | Value |
| --- | --- |
| Audit commit | `3f56399193393fe449c99e2adcba3bdc2756f723` (`main.billy_complete: iteration 2.9 (register wave four offline read tools)`) |
| Reviewer role | Independent Grok (read-only; no product/coverage/test edits) |
| Method | Re-fetch official docs fingerprint; cross-check freeze, five Wave-4 modules + tests, `server.py`, inventory/status, redaction/client/errors; reproduce offline and full-mode gates without live API, browser, or credentials |
| Official docs URL | https://www.billy.dk/api/ |
| Docs access (UTC) | 2026-07-29T12:58:20Z |
| Docs fingerprint (verified) | etag `hsisik4g9p3603`, MD5 `c2efda0ee4cf9cf200e14910c5fc6996`, content-length **147934** |
| Contract freeze | `wiki/wave_four_remaining_clear_reads_contract.md` |
| Research briefs | node `tmp/grok-research.md`; parent `.fractal/main.billy_complete/tmp/grok-research.md` |
| Design | `docs/superpowers/specs/2026-07-28-billy-mcp-complete-design.md` |

Worktree HEAD during review was `0d0848a` (init commit on top of `3f56399`). Product paths under `src/`, `coverage/`, `scripts/`, and `tests/` match the audit commit (no product delta).

Parent feed claims of offline ACCEPT + 487 pass were treated as leads and **re-derived independently** (not rubber-stamped).

---

## 1. Fifty Wave-4 clear get/list tools

Freeze: `wiki/wave_four_remaining_clear_reads_contract.md` (50 tools; default list paging; geo `countryId` only extra filter).

### 1.1 Modules

| Module | Tools | Focused tests |
| --- | ---: | --- |
| `src/billy_mcp/api/geo_reads.py` | 8 | `tests/api/test_geo_reads.py` |
| `src/billy_mcp/api/tax_reads.py` | 16 | `tests/api/test_tax_reads.py` |
| `src/billy_mcp/api/bank_reads.py` | 10 | `tests/api/test_bank_reads.py` |
| `src/billy_mcp/api/balance_invoice_ext_reads.py` | 10 | `tests/api/test_balance_invoice_ext_reads.py` |
| `src/billy_mcp/api/ledger_user_reads.py` | 6 | `tests/api/test_ledger_user_reads.py` |

All **50** freeze tool names are present as `server.tool(name=...)` registrations in those modules. Static path/root scan against the freeze matrix found **0** mismatches.

### 1.2 Paths and roots (summary)

| Cohort | Paths | Singular / plural roots | List extras |
| --- | --- | --- | --- |
| Geo (8) | `/countryGroups`, `/cities`, `/states`, `/zipcodes` | `countryGroup`/`countryGroups[]`, `city`/`cities[]`, `state`/`states[]`, `zipcode`/`zipcodes[]` | `countryId` required on cities/states/zipcodes lists only |
| Tax (16) | `/taxRates`, `/taxRateDeductionComponents`, `/salesTaxRulesets`, `/salesTaxRules`, `/salesTaxAccounts`, `/salesTaxMetaFields`, `/salesTaxReturns`, `/salesTaxPayments` | matching singular/plural camelCase roots | default paging only |
| Bank (10) | `/bankPayments`, `/bankLineMatches`, `/bankLines`, `/bankLineSubjectAssociations`, `/balanceModifiers` | matching roots | default paging only |
| Balance / invoice ext (10) | `/contactBalancePayments`, `/contactBalancePostings`, `/invoiceLateFees`, `/invoiceReminders`, `/invoiceReminderAssociations` | matching roots | default paging only |
| Ledger / users (6) | `/transactions`, `/postings`, `/users` | matching roots | default paging only; **`/users` distinct from specials `/user` and `/user/organizations`** |

Geo list parameter evidence: `src/billy_mcp/api/geo_reads.py` uses `extra="forbid"` (line 28), `pageSize` bounds (lines 57–58), required `countryId` min_length 1 on cities/states/zipcodes list tools (lines 82, 375, 404, 433).

Inventory rows for all 50 Wave-4 IDs: `implemented: true`, `contract_tested: true`, `live_tested: false`, matching `tool_name`, `GET /v2/...` routes, response roots, and geo filters on cities/states/zipcodes lists only. No invented non-geo filters on Wave-4 lists.

### 1.3 Official docs alignment

- Endpoint host: `https://api.billysbilling.com/v2` (docs Endpoint section; fingerprint above).
- List paging: `page` + `pageSize` (max/default 1000).
- Sorting: `sortProperty` + `sortDirection` ASC|DESC.
- Documented filter tables remain only for invoices/bills/daybookTransactions; Wave-4 lists stay default-only except live-required `countryId` for geo lists (freeze + prior unauth probes in parent research; not re-probed live in this review).
- Webhooks: 0 on official page (stripped docs text count).

---

## 2. Root registry (`server.py`)

Evidence: `src/billy_mcp/server.py` lines 60–82 register `coverage_status`, `coverage_report`, then Wave-1–3 registers, then:

- `register_geo_read_tools` (line 78)
- `register_tax_read_tools` (line 79)
- `register_bank_read_tools` (line 80)
- `register_balance_invoice_extension_read_tools` (line 81)
- `register_ledger_user_read_tools` (line 82)

Runtime `create_server(...).list_tools()`:

| Surface | Count |
| --- | ---: |
| `api_*` | **94** |
| `coverage_status`, `coverage_report` | **2** |
| Other tools | **0** |

User specials vs Wave-4 resource tools both present and distinct: `api_user_get`, `api_user_list_organizations`, `api_users_get`, `api_users_list`.

Unit assertion: `tests/unit/test_coverage_server.py` asserts `len(api_tool_names) == 94` and exact pre-Wave-4 set union of 50 Wave-4 names (lines 196–199 region).

No write, bulk, generic HTTP, or generic browser tools are registered on the server. `browser.py` remains library/unit-test surface only.

---

## 3. Generated inventory and status

### 3.1 `coverage/status.json` @ `3f56399`

| Field | Value |
| --- | --- |
| `complete` | **false** |
| `official_docs.etag` / `md5` | `hsisik4g9p3603` / `c2efda0ee4cf9cf200e14910c5fc6996` (matches re-fetch) |
| `qualification.implemented_rows` | **94** |
| `qualification.contract_tested_rows` | **94** |
| `qualification.live_tested_rows` | **0** |
| `qualification.vision_verified_rows` | **0** |
| Blocker text | `BILLY_API_TOKEN is unavailable; no live or UI qualification is claimed` |
| Source counts | API 305 (207 clear + 92 bulk + 6 special); UI 339; all 644 |

### 3.2 `coverage/api_v2_manifest.yaml`

| Metric | Count |
| --- | ---: |
| Operations | 305 |
| `implemented: true` / `contract_tested: true` | **94** / **94** |
| `live_tested: true` | **0** |
| Clear get/list offline green | **92 / 92** |
| Special greens | 2 (`api.special.user_get`, `api.special.user_organizations`) |
| Bulk green | **0** |
| Write (create/update/delete/upload/send_email) green | **0** |
| Remaining clear red (writes + non-read clear ops) | **115** |

Evidence map `OFFLINE_API_IMPLEMENTATION_EVIDENCE` in `scripts/generate_coverage_report.py` lists all 50 Wave-4 inventory IDs with focused test paths plus registry test reference.

### 3.3 UI inventory

`coverage/ui_workflows_manifest.yaml`: **339** rows; `implemented: false` and `vision_verified: false` for all. No UI or vision qualification claimed.

---

## 4. Redaction, host lock, typed errors

### 4.1 Redaction (`src/billy_mcp/redaction.py`)

`_SENSITIVE_READ_KEYS` (lines 28–40) includes:

- `email`, `emailbody`, `emailsubject`, `phone`
- `bankname`, `bankroutingno`, `bankaccountno`, `bankswift`, `bankiban`
- `downloadurl`

Plus subscription/payment organization keys and token-like substrings. Unit tests: `tests/unit/test_redaction_errors.py` (7 passed in full suite).

### 4.2 Host lock

- `src/billy_mcp/config.py` line 13: `API_BASE_URL = "https://api.billysbilling.com/v2"`; typed literal on config model (line 34).
- `src/billy_mcp/client.py` `_url_for` (lines 131–139): relative paths only; rejects absolute URLs and paths that include the `/v2` prefix.

### 4.3 Typed error mapping (`src/billy_mcp/errors.py`)

- Lines 11–12: maps `AUTHENTICATION_REQUIRED` and `OAUTH_INVALID_ACCESS_TOKEN` → `StableErrorCode.AUTH_REQUIRED`.
- Lines 33–40: 404 → `NOT_FOUND`, 409 → `CONFLICT`, 429 → `RATE_LIMITED`, else `BILLY_ERROR`.
- Upstream envelopes pass through `redact(...)` (line 25) so sensitive keys do not leak in tool error details.

---

## 5. Reproduced offline and full-mode gates

Commands run from worktree root with `BILLY_API_TOKEN` unset. No live API calls, browser, or credentials.

| Command | Exit | Result |
| --- | ---: | --- |
| `BILLY_TEST_MODE=commit` → `uv run pytest -m "not live and not vision"` (via node `scripts/test.sh`) | **0** | **487 passed** in ~4.9s |
| `uv run python scripts/check_coverage.py` | **0** | 305 API + 339 UI rows OK |
| `uv run python scripts/check_coverage.py --require-complete` | **1** | complete false; 92 bulk; 305 API incomplete live; 339 UI incomplete |
| `uv run python scripts/check_repository_policy.py` | **0** | policy OK |
| `uv run ruff check src tests scripts` | **0** | All checks passed |
| `uv run pyright src` | **0** | 0 errors, 0 warnings |
| `BILLY_TEST_MODE=full` node `scripts/test.sh` | **1** | 487 pytest passed, then completeness gate failed with the four `--require-complete` errors above |

Full-mode failure excerpt (expected):

```text
Coverage inventory checks failed:
- --require-complete requires coverage/status.json complete=true
- --require-complete requires no ambiguous_bulk rows (92 remain)
- --require-complete requires discovered, implemented, contract_tested, and live_tested for every API row (305 incomplete)
- --require-complete requires all API qualification states and vision_verified for every UI row (339 incomplete)
```

This is **correct fail-closed** behavior, not a regression.

---

## 6. Discrepancies

### 6.1 Offline integration (must fix for PASS)

**None.** No file/line product defects found against the freeze or registration/evidence gates.

### 6.2 Product completeness (expected open work; not offline defects)

| Gap | Evidence | Minimal path later (not this review) |
| --- | --- | --- |
| Live API qualification | `live_tested_rows: 0`; status blocker names missing token | Supply dedicated non-production token; live-test offline greens |
| UI + vision | 339 UI rows all red | Authenticated UI discovery + DOM + vision + purge |
| Bulk (92) | all `implemented: false` | Resolve official bulk body contract before greening |
| Clear writes (115) | red | Ticketed preview/execute writes per design |
| Specials (4 of 6 red) | files upload, invoice email/delivery/logs | Specials wave |
| Auth product tools | no `auth_*` registered | Out of Wave-4 offline scope |
| `complete: false` | status + require-complete exit 1 | Only after all parent completion conditions are met |

---

## 7. Explicit non-claims

This review does **not** claim:

- Live Billy API qualification
- UI workflow or vision verification
- Bulk body contracts or bulk tools
- Write/create/update/delete product tools
- Product completeness or `complete: true`
- That unauthenticated live probes were repeated in this pass (docs fingerprint rechecked; prior live notes cited only as historical freeze support)

---

## 8. Citations

1. Official API docs: https://www.billy.dk/api/ — ETag `hsisik4g9p3603`, MD5 `c2efda0ee4cf9cf200e14910c5fc6996`, 147934 bytes, access **2026-07-29T12:58:20Z**.
2. Freeze: `wiki/wave_four_remaining_clear_reads_contract.md`.
3. Audit commit: `3f56399` — `src/billy_mcp/server.py`, five Wave-4 modules under `src/billy_mcp/api/`, `src/billy_mcp/redaction.py`, `src/billy_mcp/config.py`, `src/billy_mcp/client.py`, `src/billy_mcp/errors.py`, `coverage/api_v2_manifest.yaml`, `coverage/status.json`, `scripts/generate_coverage_report.py`, `tests/unit/test_coverage_server.py`.
4. Research: node `tmp/grok-research.md`; parent `.fractal/main.billy_complete/tmp/grok-research.md`.
5. Design: `docs/superpowers/specs/2026-07-28-billy-mcp-complete-design.md`.

---

## Bottom line

Independent re-verification of **`3f56399`**: **PASS** for offline Wave-4 root integration honesty and contract alignment; **product completeness incomplete**. Offline suite **487 passed**; full mode **fails closed** at completeness. No required module rewrites. No live/UI/vision/bulk/write qualification.
