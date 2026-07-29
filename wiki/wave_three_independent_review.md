---
name: wave_three_independent_review
desc: Independent Grok review of Wave-3 unfiltered get/list API reads (22 rows) on branch integration a206eb0.
tags: [billy, api, read_only, review, wave3]
sources:
  - https://www.billy.dk/api/
  - wiki/wave_three_unfiltered_reads_contract.md
  - docs/superpowers/specs/2026-07-28-billy-mcp-complete-design.md
  - src/billy_mcp/server.py
  - coverage/api_v2_manifest.yaml
  - coverage/status.json
created: 2026-07-29T11:42:00Z
updated: 2026-07-29T11:45:00Z
---

# wave_three_independent_review

## Verdict

**Offline Wave-3 ACCEPT with one required fix.** All 22 get/list tools are registered, path-correct, and inventory-marked `implemented` + `contract_tested` with `live_tested=false`. Official docs fingerprint is unchanged. Product completeness remains **not** claimed (`complete=false`).

**Required discrepancies:** 1 (files/attachments list success envelope).  
**Blockers (expected product gates, not Wave-3 path defects):** live/UI still red; `BILLY_API_TOKEN` unavailable for qualification.  
**Advisory:** input-empty-string consistency; file tool FastMCP nested `request` param; inventory `sensitivity: low` on bank/email/`downloadUrl` fields.

## Revision and method

| Field | Value |
| --- | --- |
| Branch | `main.billy_complete.wave3_independent_review` |
| Revision | `a206eb0ff0ed094504eb72c0077eaee84794d383` |
| Reviewer role | Independent Grok (read-only; no production edits) |
| Method | Re-fetch official docs; cross-check frozen contract, five modules + tests, `server.py`, coverage inventory/status, shared redaction helper |
| Claim re-check | After draft, re-derived all 22 inventory flags, re-read file list success models, re-confirmed registry tool names and docs etag/MD5/size from cached official HTML |
| Official docs URL | https://www.billy.dk/api/ |
| Docs access (UTC) | 2026-07-29T11:41:13Z |
| Docs fingerprint (verified) | etag `hsisik4g9p3603`, MD5 `c2efda0ee4cf9cf200e14910c5fc6996`, 147934 bytes |
| Contract | `wiki/wave_three_unfiltered_reads_contract.md` (same fingerprint cited) |
| Design | `docs/superpowers/specs/2026-07-28-billy-mcp-complete-design.md` (safety / redacted logging; no Wave-3 green live claim) |

## Verified facts vs inferences

**Verified (primary sources this review):**

- Official host is `https://api.billysbilling.com/v2` (docs Endpoint section).
- Global list paging uses `page` + `pageSize` (max and default 1000); paging metadata lives under response `meta.paging` (docs Paging section).
- Global sort uses `sortProperty` + `sortDirection` in `ASC`|`DESC` (docs Sorting section).
- Global include uses the `include` query parameter for relationship sideload/embed (docs Relationships section).
- Each Wave-3 resource Supports includes **get by id** and **list** (resource tables on https://www.billy.dk/api/).
- `/v2/files` Supports: get by id, list, create, bulk save, bulk delete (no update, no singular delete).
- `/v2/accountNatures` Supports omits singular delete (create/update/bulk only beyond get/list).
- Account bank fields and file `downloadUrl` are documented as readonly strings on those resources.
- Contact person `email` is documented on `/v2/contactPersons`.
- Branch modules call relative paths without a leading `/v2` prefix; client targets `api.billysbilling.com`.
- `create_server` registers all 22 Wave-3 tools (plus prior waves); unit registry test expects the full set.
- Coverage status: `complete=false`, `implemented_rows=44`, `contract_tested_rows=44`, `live_tested_rows=0`.
- All 22 Wave-3 inventory rows: `implemented=true`, `contract_tested=true`, `live_tested=false`.

**Inferences (not live-proved here):**

- Resource-specific list filters (for example `invoiceId`, `contactId`) are absent from official resource tables for these resources; modules correctly refuse inventing them offline.
- Per-resource allowed `sortProperty` values are only partially listed in docs; free-form `sortProperty` strings match project freeze (caller may still get upstream validation errors live).
- Success tool payloads intentionally remain opaque (`extra=allow`); redaction of bank/email/`downloadUrl` is enforced in the shared helper for structured logging/error sanitisation, not by stripping successful MCP results (design: redacted logging).

## Modules reviewed

| Module | Tools | Tests |
| --- | --- | --- |
| `src/billy_mcp/api/line_reads.py` | invoice/bill/daybookTransaction lines get+list | `tests/api/test_line_reads.py` |
| `src/billy_mcp/api/contact_person_reads.py` | contactPersons get+list | `tests/api/test_contact_person_reads.py` |
| `src/billy_mcp/api/daybook_reads.py` | daybooks + daybookBalanceAccounts get+list | `tests/api/test_daybook_reads.py` |
| `src/billy_mcp/api/account_reads.py` | accounts + accountGroups + accountNatures get+list | `tests/api/test_account_reads.py` |
| `src/billy_mcp/api/file_attachment_reads.py` | files + attachments get+list | `tests/api/test_file_attachment_reads.py` |
| `src/billy_mcp/server.py` | registration of the five `register_*` hooks | `tests/unit/test_coverage_server.py` |
| `src/billy_mcp/redaction.py` | bank*, email, downloadUrl keys | `tests/unit/test_redaction_errors.py` |

## 22-row results

Legend: **P** = pass for offline contract; **F** = fail / required fix; **n/a** = dimension not applicable.

| Row id | Official route (docs) | Inputs | Paging/sort | Roots | Typed errors | Registry | Coverage | Redaction keys | Result |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `api.invoiceLines.get` | GET `/v2/invoiceLines/:id` | id + optional include | n/a | `invoiceLine` | 401→AUTH_REQUIRED (client) | yes | impl+ct; live false | n/a | **P** |
| `api.invoiceLines.list` | GET `/v2/invoiceLines` | page, pageSize 1–1000, include, sortProperty, sortDirection | page/pageSize; meta.paging | `invoiceLines[]` + meta | same | yes | same | n/a | **P** |
| `api.billLines.get` | GET `/v2/billLines/:id` | id + include | n/a | `billLine` | same | yes | same | n/a | **P** |
| `api.billLines.list` | GET `/v2/billLines` | list allowlist | page/pageSize; meta.paging | `billLines[]` + meta | same | yes | same | n/a | **P** |
| `api.daybookTransactionLines.get` | GET `/v2/daybookTransactionLines/:id` | id + include | n/a | `daybookTransactionLine` | same | yes | same | n/a | **P** |
| `api.daybookTransactionLines.list` | GET `/v2/daybookTransactionLines` | list allowlist | page/pageSize; meta.paging | `daybookTransactionLines[]` + meta | same | yes | same | n/a | **P** |
| `api.contactPersons.get` | GET `/v2/contactPersons/:id` | id + include | n/a | `contactPerson` | same | yes | same | email key in helper | **P** |
| `api.contactPersons.list` | GET `/v2/contactPersons` | list allowlist | page/pageSize; meta.paging | `contactPersons[]` + meta | same | yes | same | email key in helper | **P** |
| `api.daybooks.get` | GET `/v2/daybooks/:id` | id + include | n/a | `daybook` | same | yes | same | n/a | **P** |
| `api.daybooks.list` | GET `/v2/daybooks` | list allowlist | page/pageSize; meta.paging | `daybooks[]` + meta | same | yes | same | n/a | **P** |
| `api.daybookBalanceAccounts.get` | GET `/v2/daybookBalanceAccounts/:id` | id + include | n/a | `daybookBalanceAccount` | same | yes | same | n/a | **P** |
| `api.daybookBalanceAccounts.list` | GET `/v2/daybookBalanceAccounts` | list allowlist | page/pageSize; meta.paging | `daybookBalanceAccounts[]` + meta | same | yes | same | n/a | **P** |
| `api.accounts.get` | GET `/v2/accounts/:id` | id + include | n/a | `account` | same | yes | same | bank* keys in helper | **P** |
| `api.accounts.list` | GET `/v2/accounts` | list allowlist | page/pageSize; meta.paging | `accounts[]` + meta | same | yes | same | bank* keys in helper | **P** |
| `api.accountGroups.get` | GET `/v2/accountGroups/:id` | id + include | n/a | `accountGroup` | same | yes | same | n/a | **P** |
| `api.accountGroups.list` | GET `/v2/accountGroups` | list allowlist | page/pageSize; meta.paging | `accountGroups[]` + meta | same | yes | same | n/a | **P** |
| `api.accountNatures.get` | GET `/v2/accountNatures/:id` | id + include | n/a | `accountNature` | same | yes | same | n/a | **P** |
| `api.accountNatures.list` | GET `/v2/accountNatures` | list allowlist | page/pageSize; meta.paging | `accountNatures[]` + meta | same | yes | same | n/a | **P** |
| `api.files.get` | GET `/v2/files/:id` | id + include | n/a | `file` | same | yes | same | downloadUrl key in helper | **P** |
| `api.files.list` | GET `/v2/files` | list allowlist | page/pageSize **wire** OK; **tool shape F** | `files[]` OK; **paging not under meta** | same | yes | same | downloadUrl key in helper | **F** |
| `api.attachments.get` | GET `/v2/attachments/:id` | id + include | n/a | `attachment` | same | yes | same | n/a | **P** |
| `api.attachments.list` | GET `/v2/attachments` | list allowlist | page/pageSize **wire** OK; **tool shape F** | `attachments[]` OK; **paging not under meta** | same | yes | same | n/a | **F** |

Shared offline behaviours verified across the green rows:

- No offset paging; undeclared parent filters rejected in models/tests.
- URL-encoding of ids (`quote(..., safe='')`).
- Typed 401 mapping for `AUTHENTICATION_REQUIRED` and `OAUTH_INVALID_ACCESS_TOKEN` via client/error layer (fixtures in each suite).
- Offset and invented filters rejected.

## Actionable findings

### Required

1. **`api.files.list` / `api.attachments.list` success envelope flattens paging**  
   - **Evidence:** `FilesListSuccess` / `AttachmentsListSuccess` expose top-level `paging` (`src/billy_mcp/api/file_attachment_reads.py`). Upstream and official docs place paging under `meta.paging`. Frozen contract requires optional `meta.paging`. Inventory `response_fields` list `meta.paging` for both rows. Other Wave-3 lists return `meta: { paging: ... }`. Tests lock the flattened shape (`tests/api/test_file_attachment_reads.py`).  
   - **Wire still correct:** handlers read `payload["meta"]["paging"]` from Billy; only the tool-facing envelope diverges.  
   - **Fix (for codex-power):** align list success models with `meta.paging` (and update focused tests + any callers). Do not green live.

### Blocker (product completeness; outside this offline wave)

1. **`live_tested=0` / no `BILLY_API_TOKEN`** — status blocker text already records this. Do not claim live or UI qualification.
2. **`complete=false`** remains correct while bulk ambiguous rows, remaining API, and all UI stay red.

### Advisory

1. **Empty `include` / `sortProperty`:** line, daybook, and file modules often use `min_length=1`; contact-person and account modules allow empty strings that serialise onto the wire. Prefer a single reject-empty rule.
2. **File tool MCP parameter nesting:** file/attachment tools take a single Pydantic `request` object in FastMCP registration, while sibling Wave-3 tools use flat parameters. Behaviour is tested; surface is inconsistent for agents.
3. **Inventory sensitivity:** accounts bank fields, contact person email, and file `downloadUrl` remain `sensitivity: low` while the freeze calls out log redaction; helper keys exist and unit tests cover them. Consider raising inventory sensitivity metadata without greening live.

## Live and UI (explicit non-claim)

This review did **not** run authenticated live probes, headed browser flows, vision checks, or credential configuration. UI parity and discovery rows stay red. No screenshots, HAR, frames, or traces are attached. Do not treat offline Wave-3 ACCEPT as product complete.

## Radio disposition

Required finding #1 sent to the parent inbox as message `BC8031B3` with exact row ids (`api.files.list`, `api.attachments.list`) and evidence. No other required discrepancies found.
