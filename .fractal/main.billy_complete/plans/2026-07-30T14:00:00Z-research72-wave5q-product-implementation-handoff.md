# Research72 — Wave-5q users product implementation handoff

## Goal

Reconfirm official docs and method gates, then hand a bounded Codex Power product slice for singular `users` update now that freeze IR is ACCEPT.

## Done

- Re-fetched https://www.billy.dk/api/ — ETag `wcw4x9hqvu3603`, MD5 `8b94b0135c91fd15fe54ea33e088a4be`, 147934 bytes (byte-identical to research71).
- Unauth probes: users PUT 401; POST/DELETE 405; empty PUT body 400.
- Confirmed freeze IR ACCEPT and product-ready IR ACCEPT on root; no `user_writes` module yet.
- Wrote `tmp/grok-research.md` and `wiki/wave_fiveq_users_product_implementation_research.md`.

## Next (not this research step)

- Codex Power leaf `wave5q_users_product`: two tools, greening to 178 offline, api tools 262.
- Then Grok product independent review.
- Then Wave-5r salesTaxReturns update freeze.
