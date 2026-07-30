---
name: state
desc: Current node state, verified review decisions, and open qualification work.
tags: [billy, coverage, review]
sources:
  - docs/superpowers/specs/2026-07-28-billy-mcp-complete-design.md
  - https://www.billy.dk/api/
created: 2026-07-30T15:57:03Z
updated: 2026-07-30T17:14:33Z
---

# state

## Current state

- Wave-5c through Wave-5r write modules merged on root (including salesTaxReturns update).
- Wave-5s-A `api_invoice_logs_list` is merged on root (`5b8719b`). Root offline coverage **180** implemented + contract_tested. Live/vision **0**. `complete: false`. Registry **265** API tools.
- Wave-5q freeze/product IR: **ACCEPT** offline.
- Wave-5r freeze IR: **ACCEPT**. Wave-5r product IR: **ACCEPT** offline (`wiki/wave_fiver_product_independent_review.md`, baseline `5ad69a6`).
- Research77 residual specials ranking: **ACCEPT as research** (`wiki/wave_fives_residual_specials_research.md`).
- Research78 Wave-5s-A invoiceLogs list contract: **ACCEPT as research** (`wiki/wave_fivesa_invoice_logs_research_independent_review.md` @ `97f7e12`).
- Research79 Wave-5s-B files upload freeze contract: **ACCEPT as research** (`wiki/wave_fivesb_files_upload_research.md`).
- Research80 Wave-5s-B **product-ready** handoff: cited (`wiki/wave_fivesb_files_upload_product_ready_research.md`; scratch `tmp/grok-research.md`). Product tools still absent.
- Designated Grok product/research reviewers previously failed authentication before editing. Codex Power fallback reviews may still be active; they provide limited review evidence only and cannot satisfy the mandatory Grok audit.
- UI all red (339); bulk 92 red; clear not-impl 30 (includes files.create alias); specials not-impl 3 on root; no live token; no UI credentials.

## Verification

- Official docs MD5 `8b94b0135c91fd15fe54ea33e088a4be` reconfirmed research80 (byte-identical to research79; ETag `"wcw4x9hqvu3603"`).
- Inventory lock strings in `status.json` still older ETag/MD5 (CDN drift only).
- Unauth files: binary/JSON POST **401**; singular PUT/DELETE **405**; GET id **404**.
- Dual-row rule: special owns `api_files_upload_preview`; `api.files.create` aliases with empty tool_name; no `api_files_create*`.
- Greening requires **both** row ids in `OFFLINE_API_IMPLEMENTATION_EVIDENCE` (alias does not inherit).
- `WriteProtocolService` is JSON-only; product needs dedicated binary POST + direct ticket binding with path/digest and size/mtime revalidation.
- Root baseline: 180/180/0/0 coverage state, `complete: false`, bulk/UI red, registry 265.

## Review decisions (authoritative)

- Wave-5m through Wave-5q freeze/product: **ACCEPT** offline.
- Wave-5r freeze independent: **ACCEPT**.
- Wave-5r product independent: **ACCEPT** offline.
- Wave-5s residual/specials research: **ACCEPT as research**.
- Wave-5s-A invoiceLogs research IR: **ACCEPT as research** (not product ACCEPT).
- Wave-5s-B freeze research: **ACCEPT as research**.
- Wave-5s-B product-ready research: **ready handoff** (not product ACCEPT).
- Overall completeness: **FAIL**.

## Open coverage work

1. Integrate any active Codex Power fallback review pages; retain the mandatory Grok-audit blocker.
2. Codex Power Wave-5s-B product leaf: ticketed `api_files_upload_preview` / `api_files_upload_execute` per research80; dual-row green for special + create alias; client binary POST allowlist; size/mtime + digest revalidation.
3. Later: invoice email/delivery specials, 405 false friends (live/docs), transactions (live), bulk 92, UI/auth/vision.

## Evidence boundaries

- Research ACCEPT/ready is not product, live, UI, vision, bulk, or completeness.
- 405 overrides Supports offline; DELETE 200 meta-only is not cleanup proof.
- Sample host `api.billy.dk` is never the client base.
- JSON POST `/files` reaching 401 does not authorise a JSON create tool.
- Do not green coverage from research alone.
- An authentication-failed Grok leaf has no review provenance; discard any uncommitted draft it leaves behind and retry through the permitted fallback route.

## References

- Wave-5s-B product-ready: `wiki/wave_fivesb_files_upload_product_ready_research.md`
- Wave-5s-B freeze research: `wiki/wave_fivesb_files_upload_research.md`
- Research brief: `.fractal/main.billy_complete/tmp/grok-research.md`
- Wave-5s-A research IR: `wiki/wave_fivesa_invoice_logs_research_independent_review.md`
- Residual specials research: `wiki/wave_fives_residual_specials_research.md`
- Product IR (Wave-5r): `wiki/wave_fiver_product_independent_review.md`
