---
name: state
desc: Current node state, verified review decisions, and open qualification work.
tags: [billy, coverage, review]
sources:
  - docs/superpowers/specs/2026-07-28-billy-mcp-complete-design.md
  - https://www.billy.dk/api/
created: 2026-07-30T15:57:03Z
updated: 2026-07-30T17:37:00Z
---

# state

## Current state

- Wave-5c through Wave-5r write modules merged on root (including salesTaxReturns update).
- Wave-5s-A `api_invoice_logs_list` is merged on root. Root offline coverage **180** implemented + contract_tested. Live/vision **0**. `complete: false`. Registry **265** API tools.
- Wave-5s-B freeze research: **ACCEPT as research**.
- Wave-5s-B product-ready research: **ACCEPT offline** as implementation handoff only (`wiki/wave_fivesb_files_upload_product_ready_research_independent_review.md`; scratch `tmp/grok-review.md`). Product tools still absent on root.
- Active child: `wave5sb_files_upload_product` may implement against the product-ready ACCEPT.
- UI all red (339); bulk 92 red; clear not-impl 30 (includes files.create alias); specials not-impl 3; no live token; no UI credentials.

## Verification

- Independent docs re-fetch MD5 `8b94b0135c91fd15fe54ea33e088a4be`, ETag `"wcw4x9hqvu3603"`, byte-identical to research80.
- Unauth files: binary/JSON POST **401**; singular PUT/DELETE **405**; attachments DELETE **200** meta-only (not cleanup).
- Dual-row still red: special owns `api_files_upload_preview`; create alias empty tool_name.
- No `file_upload_writes.py`; client JSON-only; evidence map lacks files rows.
- Coverage honesty: 180/180/0/0, `complete: false`.

## Review decisions (authoritative)

- Wave-5m through Wave-5q freeze/product: **ACCEPT** offline.
- Wave-5r freeze/product independent: **ACCEPT** offline.
- Wave-5s residual/specials research: **ACCEPT as research**.
- Wave-5s-A invoiceLogs research IR: **ACCEPT as research** (Grok product IR still open / fallback only).
- Wave-5s-B freeze research: **ACCEPT as research**.
- Wave-5s-B product-ready research independent: **ACCEPT** offline as handoff only (not product ACCEPT).
- Overall completeness: **FAIL**.

## Open coverage work

1. Codex Power Wave-5s-B product leaf: ticketed upload pair + dual-row green + binary client path.
2. Grok product independent review after root merge (registry 267, coverage 182 offline).
3. Later: invoice email/delivery specials, 405 false friends, transactions, bulk 92, UI/auth/vision.

## Evidence boundaries

- Research/product-ready ACCEPT is not product, live, UI, vision, bulk, or completeness.
- Do not green coverage from research alone.
- Files upload is raw binary (`--data-binary`), never multipart/form-data.
- Sample host `api.billy.dk` is never the client base.
- JSON POST 401 does not authorise JSON create.
- DELETE 200 meta-only is not cleanup proof.

## References

- Product-ready IR: `wiki/wave_fivesb_files_upload_product_ready_research_independent_review.md`
- Product-ready research: `wiki/wave_fivesb_files_upload_product_ready_research.md`
- Freeze research: `wiki/wave_fivesb_files_upload_research.md`
- Review scratch: `.fractal/main.billy_complete/tmp/grok-review.md`
- Research scratch: `.fractal/main.billy_complete/tmp/grok-research.md`
