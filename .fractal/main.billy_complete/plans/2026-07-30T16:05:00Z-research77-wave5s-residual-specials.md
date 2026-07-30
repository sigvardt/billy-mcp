# Research77 — Wave-5s residual clear and specials ranking

## Goal
While Wave-5r product leaf finishes, re-verify official docs and unauth residual
gates, then deliver a cited ranking and specials map for the next Codex slices.

## Done
- Re-fetched https://www.billy.dk/api/ — MD5 8b94b0135c91fd15fe54ea33e088a4be,
  ETag wcw4x9hqvu3603, 147934 bytes; identical to research76.
- Unauth residual matrix: specials 401; 405 false friends; transactions
  POST/PUT 401 + all-readonly props + DELETE 200 meta; bankPayments DELETE 405;
  salesTaxReturns update-only unchanged.
- Product leaf completed at cf33343 with 179 offline; root still 178 (not merged).
- Brief: `.fractal/main.billy_complete/tmp/grok-research.md`
- Wiki: `wiki/wave_fives_residual_specials_research.md`

## Recommended next (not this step)
1. Merge Wave-5r product; Grok product IR.
2. Wave-5s-A: `api_invoice_logs_list` offline special.
3. Wave-5s-B: files upload ticketed pair (pair clear create + special).
4. Wave-5s-C: invoice email + delivery ticketed pairs.

## Non-goals
- No coverage greening from research.
- No live/UI/vision/bulk work.
- No offline freeze for transactions or 405 false friends.

## Post-Mortem

### Completed

- Delivered the cited residual-specials ranking without altering any coverage
  evidence. The official-doc fingerprint and unauthenticated method gates were
  reconfirmed and the shared research page is indexed.
- The planned downstream gates completed: Wave-5r salesTaxReturns update was
  integrated at `5ad69a6`, and its authoritative offline product review issued
  ACCEPT. Research77 remains research only.

### Verification and cleanup

- Project and memory wikis lint clean; static checks, coverage integrity,
  repository policy, and 1,163 non-live/non-vision tests pass after the product
  integration.
- No credentials, browser evidence, live records, or coverage greening from
  this research package were created.

### Next unresolved coverage slice

- Wave-5s-A may implement only the read-only `api_invoice_logs_list` special;
  uploads, email/delivery writes, blocked writes, bulk, live, UI, and vision
  remain separate work.
