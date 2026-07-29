---
name: research_status
desc: Wave-4 tax-reads research state for this node.
tags: [research, tax, wave4]
sources: []
created: 2026-07-29T12:08:00Z
updated: 2026-07-29T12:25:11Z
---

# research_status

## Stands

- Official docs fingerprint: etag `hsisik4g9p3603`, MD5 `c2efda0ee4cf9cf200e14910c5fc6996`, 147934 bytes.
- Cited brief delivered at node `tmp/grok-research.md` for Codex Power.
- Contract freeze: worktree `wiki/wave_four_remaining_clear_reads_contract.md` Tax § (16 tools) remains authoritative.
- All 16 inventory get/list tax rows still offline-red (`implemented/contract_tested/live_tested` false).
- `BILLY_API_TOKEN` unset; no authenticated response bodies captured.
- UI discovery blocked at unauth login SPA (etag `28562ca594d82a782f4d4cb6496fe9dd`).

## Tax slice contract

- Eight resources × get+list = **16** tools; default unfiltered list surface only.
- Paths/roots as freeze table; client-relative paths without `/v2`.
- Flat Pydantic params, `extra="forbid"`, opaque allow-extra records, optional `meta.paging`, encoded IDs, typed 401.
- Reject `offset` and all resource filters (`taxRateId`, `source`, `type`, `contactType`, `periodType`, …).
- Do not invent enum values for `source`, `type`, `contactType`, `periodType`.
- Clone Wave-3 `account_reads.py` pattern.

## Live probe notes (unauth)

- All eight lists: 401 `AUTHENTICATION_REQUIRED`.
- Invalid token on taxRates list: 401 `OAUTH_INVALID_ACCESS_TOKEN`.
- Get `…/test-id` on all eight: 404 `RECORD_NOT_FOUND` naming singular roots (not 401).
- Invented list query keys still 401 pre-auth; no geo-style required filter proven for tax.

## Out of scope for this node

- server registration, coverage greening, redaction, writes, bulk, live_tested, wiki freeze edits, sibling Wave-4 clusters.
