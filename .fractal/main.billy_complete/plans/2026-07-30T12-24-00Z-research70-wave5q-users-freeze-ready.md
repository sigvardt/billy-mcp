# Research70 — Wave-5q users update freeze-ready package

## Goal

After Wave-5p freeze ACCEPT and while organizations product runs, reconfirm
official Billy API docs and unauth method gates, then package the next offline
freeze surface: singular `users` update only.

## Findings

- Docs body MD5 `8b94b0135c91fd15fe54ea33e088a4be`, ETag `wcw4x9hqvu3603`, 147934
  bytes (byte-identical to research69).
- users: POST/DELETE 405; PUT 401. salesTaxReturns same pattern. No gate drift
  vs research69 for core matrix.
- Extra matrix: many Supports-create/update inventory rows are unauth POST/PUT
  405 (geo/reference). transactions POST/PUT 401; DELETE 200 meta-only.
  Specials (files, invoice emails/deliveries, invoiceLogs) open at 401.
- Wave-5q freeze package: exactly two tools
  (`api_users_update_preview` / `_execute`), opaque `user` map, root `users`.
- salesTaxReturns update deferred to Wave-5r. associations delete still blocked.
- No coverage greens. No headed browser. No credentials. No disposable data.

## Deliverables

- `.fractal/main.billy_complete/tmp/grok-research.md` (research70 brief)
- `wiki/wave_fiveq_users_freeze_ready_research.md` (durable freeze-ready package)

## Next (not this research step)

1. Optional independent research review ACCEPT as research.
2. Codex Power wiki freeze page `wiki/wave_fiveq_ticketed_writes_contract.md`.
3. Independent freeze ACCEPT, then product leaf (+1 offline green after orgs).
4. Merge completed organizations product child (`fbc8996`) before claiming 177
   on root; Wave-5q freeze page may be wiki-only in parallel if ownership is
   disjoint.

## Post-Mortem

- Completed: current official-doc fingerprint, core and extra unauth matrices,
  users freeze surface, sequential candidates, and coverage honesty recorded.
- Deviation: organizations product child completed mid-research; brief/memory
  updated to unmerged-child status without greening root coverage.
- Verification: docs HTML byte-identical to research69; probe outcomes match
  prior core matrix; no credentials used; root status.json remains 175.
- Unresolved: Wave-5p product unmerged and unreviewed on root; Wave-5q freeze
  not authored; bulk 92 and UI/vision remain open.
