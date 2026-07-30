# Research78 — Wave-5s-A invoiceLogs list contract

## Goal
After Wave-5r product ACCEPT, freeze the exact offline contract for
`api_invoice_logs_list` from current official docs and unauth probes so Codex
Power can implement one special read tool.

## Done
- Re-fetched https://www.billy.dk/api/ — MD5 8b94b0135c91fd15fe54ea33e088a4be,
  ETag wcw4x9hqvu3603, 147934 bytes; identical to research77.
- invoiceLogs: not in Supports TOC; narrative GET sample + response fields;
  unauth GET collection 401; GET id 404; writes 405.
- Residual specials ranking still holds; files/email/delivery remain next.
- Brief: `.fractal/main.billy_complete/tmp/grok-research.md`
- Wiki: `wiki/wave_fivesa_invoice_logs_list_research.md`
- Residual ranking page updated for Wave-5r done + Wave-5s-A ready.

## Recommended next (not this step)
1. Codex Power Wave-5s-A product: `api_invoice_logs_list` only → 180 offline, 265 tools.
2. Grok product IR for Wave-5s-A.
3. Wave-5s-B files upload ticketed pair.
4. Wave-5s-C invoice email + delivery ticketed pairs.

## Non-goals
- No coverage greening from research.
- No singular get, writes, paging invention, live/UI/vision/bulk work.

## Post-Mortem

### Completed

- The cited list-only invoiceLogs contract was recorded in the project wiki
  without changing product source or coverage evidence.
- Independent Grok review accepted the handoff as research only; the result is
  recorded at `wiki/wave_fivesa_invoice_logs_research_independent_review.md`.

### Verification and cleanup

- The review reconfirmed the official docs fingerprint, collection GET auth
  gate, singular 404 boundary, and write 405 boundaries.
- No token, live record, browser, frame, HAR, or screenshot was used or
  retained. Coverage stayed 179/179/0/0 with `complete: false`.

### Next unresolved coverage slice

- The active Codex Power leaf must implement and test exactly
  `api_invoice_logs_list`; product independent review is required after a
  merged implementation.
