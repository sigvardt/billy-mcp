# Research66 — Wave-5o product-implementation handoff

## Intent

Research-only pass after Wave-5o freeze ACCEPT. Reconfirm Billy official API
contract and unauth method gates, then package the exact offline product
implementation slice for Codex Power (two invoice-reminder create tools).

## Sources

- https://www.billy.dk/api/ (ETag `wcw4x9hqvu3603`, MD5 `8b94b0135c91fd15fe54ea33e088a4be`, 147934 bytes)
- https://api.billysbilling.com/v2 unauth probes (POST 401 / PUT·DELETE 405)
- `wiki/wave_fiveo_ticketed_writes_contract.md` (ACCEPTed freeze)
- `wiki/wave_fiveo_freeze_independent_review.md` (ACCEPT)
- `coverage/api_v2_manifest.yaml`, `coverage/status.json`
- Design: `docs/superpowers/specs/2026-07-28-billy-mcp-complete-design.md`

## Deliverable

`.fractal/main.billy_complete/tmp/grok-research.md` (research66)

## Result

- Official HTML **byte-identical** to research65; no contract change.
- Unauth gates unchanged: create open at auth gate; update/delete/bulk-delete closed.
- Product gates open: freeze ACCEPT + product-ready research ACCEPT on root.
- Product tools still absent; create inventory row remains red.
- No coverage greening; no product code; no live/UI work.

## Next implementation slice

Codex Power: implement `api_invoice_reminders_create_preview` +
`api_invoice_reminders_create_execute` only; green one inventory row after
tests; leave bulk red; keep `complete: false`.
