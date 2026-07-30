# research81 — Wave-5s-C email + delivery freeze

## Outcome
Freeze research for `api.special.invoice_email` and `api.special.invoice_delivery` after re-verifying official docs (no body drift vs research80).

## Deliverables
- `.fractal/main.billy_complete/tmp/grok-research.md` (research81)
- `wiki/wave_fivesc_invoice_email_delivery_research.md`
- residual ranking pointer updates
- unauth probes in `tmp/write-probes-research81*.json`

## Next (not this step)
1. Finish/merge Wave-5s-B files upload product + product IR
2. Codex Power implements Wave-5s-C offline ticketed pairs
3. Grok product IR for Wave-5s-C

## Non-claims
No coverage green, no live, no UI/vision, no bulk.

## Post-Mortem

- Completed the cited email and e-invoice delivery freeze, durable wiki page,
  residual-ranking links, and unauthenticated method-gate evidence. Scratch
  probe bodies remain in ignored owner-only node storage.
- Root Grok independent review **ACCEPTED the research only**. It independently
  matched the official-page fingerprint and the method-gate matrix; it found no
  required correction to the freeze.
- Reproduction confirmed the product remains absent on root, both inventory
  rows are red, and generic POST confirmation binding has no target, so an
  email implementation must specialise `target=invoiceId`.
- No finding was rejected: response roots remain explicitly provisional, and
  no email destination URL, receiver CVR field, delivery reads, or webhooks
  were inferred.
- Verification passed: both wiki stores lint clean (the memory index has its
  existing empty-content note), repository lint/type/policy gates passed, and
  the non-live suite passed **1180 tests**.
- Next unresolved coverage slice: merge and review the active Wave-5s-B binary
  upload product before opening the ticketed Wave-5s-C product leaf.
