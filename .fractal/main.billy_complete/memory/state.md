---
name: state
desc: Current node state, verified review decisions, and open qualification work.
tags: [billy, coverage, review]
sources:
  - docs/superpowers/specs/2026-07-28-billy-mcp-complete-design.md
  - https://www.billy.dk/api/
created: 2026-07-30T11:33:24Z
updated: 2026-07-30T14:46:30Z
---

# state

## Current state

- Wave-5c through Wave-5q write modules merged; shared confirmation store and write protocol.
- Root offline coverage **178** implemented + contract_tested. Live/vision **0**. `complete: false`.
- Wave-5q freeze page + freeze IR **ACCEPT** on root (freeze MD5 `c53717468aff0406799feca225a00728`).
- Wave-5q users product merged (`user_writes.py`); registry 262; `api.users.update` offline-green only; live still red; product independent ACCEPT still open as a separate review gate.
- Research73 Wave-5r salesTaxReturns update freeze-ready package on root wiki + scratch brief.
- UI all red (339); bulk 92 empty-tool red; no live token; no UI credentials.
- Docs body still MD5 `8b94b0135c91fd15fe54ea33e088a4be` (ETag `wcw4x9hqvu3603`, 147934 bytes).

## Verification

- Research73 re-fetch byte-identical to research72; salesTaxReturns POST 405 / PUT 401 / DELETE 405 / empty PUT 400.
- Coverage honesty: 178/178/0/0; complete false; zero false-green rows from research.
- Freeze-ready only: no freeze page yet for Wave-5r; no product module for salesTaxReturns.

## Review decisions (authoritative)

- Wave-5m through Wave-5p freeze/product: **ACCEPT** offline.
- Wave-5q freeze independent: **ACCEPT**.
- Wave-5q product-ready research: **ACCEPT as research**.
- Research72 product implementation handoff: **ACCEPT as research** (review72).
- Wave-5q product on root: **merged / product independent ACCEPT still open**.
- Research73 Wave-5r freeze-ready: **packaged** (not freeze ACCEPT).
- Overall completeness: **FAIL**.

## Open coverage work

1. Codex Power: wiki-only Wave-5r freeze page `wiki/wave_fiver_ticketed_writes_contract.md`.
2. Grok: Wave-5r freeze independent review after freeze page; Wave-5q product independent review of merged users tools (parallel).
3. After Wave-5r freeze IR ACCEPT: salesTaxReturns update product (178 → 179 offline).
4. Later: transactions (method-open but all columns readonly offline), specials, method-closed Supports honesty; associations delete needs live cleanup proof.
5. Bulk 92, UI/auth/vision, live CUD still open.

## Evidence boundaries

- Research ACCEPT is not freeze ACCEPT, product ACCEPT, or live qualification.
- Freeze IR ACCEPT authorises product source; greening requires product + generator + tests.
- salesTaxReturns singular create/delete are 405: freeze is update-only; cleanup restore-via-PUT unproven; settlement may be one-way.
- Do not green coverage from research or freeze alone.

## References

- Research73 brief: `.fractal/main.billy_complete/tmp/grok-research.md`
- Freeze-ready wiki: `wiki/wave_fiver_sales_tax_returns_freeze_ready_research.md`
- Wave-5q freeze page: `wiki/wave_fiveq_ticketed_writes_contract.md`
- Wave-5q product: `src/billy_mcp/api/user_writes.py`
