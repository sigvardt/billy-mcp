---
name: state
desc: Current node state, verified review decisions, and open qualification work.
tags: [billy, coverage, review]
sources:
  - docs/superpowers/specs/2026-07-28-billy-mcp-complete-design.md
  - https://www.billy.dk/api/
created: 2026-07-29T22:11:45Z
updated: 2026-07-29T22:11:45Z
---

# state

## Current state

- Wave-5c through Wave-5f parent/line write modules are merged into root; root registration uses the one shared `ConfirmationStore` and `WriteProtocolService`.
- Root merge `353449d` integrates Wave-5f product `8c1cdf6`: **190** `api_*` + 2 coverage tools and 48 preview + 48 execute ticketed write tools, including tax-rate and deduction-component CUD. Root tip records product ACCEPT at **`70e0506`**.
- Wave-5g freeze committed at **`5612aa8`** (`wiki/wave_fiveg_ticketed_writes_contract.md`). Independent root Grok freeze **ACCEPT** at `wiki/wave_fiveg_freeze_independent_review.md`. **No product code yet.**
- Product-ready research at scratch `tmp/grok-research.md`: docs fingerprint unchanged; unauth probes reconfirm 401/200 gates; handoff is Codex Power product only (12 tools, registry 202, coverage 148 offline).
- Independent Grok product-ready research **ACCEPT** offline as handoff only: `wiki/wave_fiveg_product_ready_research_independent_review.md` (scratch `tmp/grok-review.md`). Not product ACCEPT.
- The Codex Power leaf `main.billy_complete.wave5g_sales_tax_product` is implementing the accepted twelve-tool offline cohort; root has no unmerged product code.
- Coverage: implemented 142, contract_tested 142, live 0, vision 0, `complete: false`.
- Official docs fingerprint still etag `hsisik4g9p3603`, MD5 `c2efda0ee4cf9cf200e14910c5fc6996` (body 147934 bytes). Review re-fetch matches.
- Wave-5e product at tip **`15d0bde`** / root record **`c92ed0e`**: **ACCEPT** offline.
- Wave-5f freeze at tip **`d412e8c`** / record **`e39704b`**: **ACCEPT** offline (`wiki/wave_fivef_freeze_independent_review.md`).
- Wave-5f product at root merge **`353449d`** / product **`8c1cdf6`**: **ACCEPT** offline (`wiki/wave_fivef_product_independent_review.md`).
- UI all red; bulk 92 empty-tool red; four specials red; no live token in process env.
- Leaf `wave5g_freeze_review` exited without deliverable; root review is authoritative. Historical unmerged review branches remain intentionally closed rather than merged.

## Review decisions (authoritative)

- Wave-5a integrated product: **ACCEPT** offline.
- Wave-5b freeze: **ACCEPT**.
- Wave-5b product at `920ceab`: **REJECTED**.
- Wave-5b repair at `a2a0996`: **ACCEPT** offline.
- Wave-5c freeze: **ACCEPT** offline contract only.
- Wave-5c product at tip `f235ac2`: **ACCEPT** offline by independent Grok audit.
- Wave-5d freeze at tip `5c376de`: **ACCEPT** offline contract only.
- Wave-5d product at tip `1108e2f`: **ACCEPT** offline by independent Grok.
- Wave-5e freeze at `fc8118e`: **ACCEPT** offline by the authoritative root Grok independent review.
- Wave-5e product at tip `15d0bde`: **ACCEPT** offline by independent Grok.
- Wave-5f freeze at tip `d412e8c`: **ACCEPT** offline by the authoritative root Grok independent review.
- Wave-5f product-ready research at tip `1c9e6cb`: **ACCEPT** offline as implementation handoff only.
- Wave-5f product at root merge `353449d`: **ACCEPT** offline by independent Grok.
- Wave-5g freeze at tip `5612aa8`: **ACCEPT** offline by the authoritative root Grok independent review.
- Wave-5g product-ready research: **ACCEPT** offline as implementation handoff only (`wiki/wave_fiveg_product_ready_research_independent_review.md`).
- Wave-5g product: **not accepted** (not implemented).
- Overall completeness: **FAIL** until live, bulk, remaining writes, specials, UI/vision close red rows.

## Open coverage work

1. Product the accepted Wave-5g freeze: `salesTaxRulesets` + `salesTaxRules` (6 CUD; +12 tools; target 202 `api_*`, 148 offline rows), then independent product review. Product-ready research is ready in `tmp/grok-research.md`.
2. Later: sales-tax accounts/meta-fields, payments/returns partial CUD, attachments, specials, bulk (live only), UI/auth/vision.
3. Blocked offline without more evidence: `accountNatures` and `postings` writes (unauth 405 overrides Supports), `bankPayments` delete (405), `transactions` CUD (all-readonly property table). OPTIONS ACM listing POST is not authority when real method returns 405.

## Wave-5g freeze and product evidence

- Docs re-fetch at product-ready research: same ETag/MD5/bytes as inventory fingerprint.
- Unauth: salesTaxRulesets/Rules POST/PUT **401**, DELETE missing-id **200**, not cleanup proof.
- Parent `additional_plural_roots=("salesTaxRules",)`; child `()`.
- Almost all fields immutable on both resources; keep opaque payloads; still ship ticketed update (Supports + 401, not 405).
- No `sales_tax_writes` module; registry still 190; six inventory CUD rows still red.
- Attachments alternate ready later (3 CUD); not in this product.
- `accountNatures`/`postings` POST unauth **405** — do not offline-green from Supports.

## Evidence boundaries

- Official API fingerprint: etag `hsisik4g9p3603`, MD5 `c2efda0ee4cf9cf200e14910c5fc6996`.
- Unauth DELETE empty 200 is not cleanup proof.
- Unauth METHOD_NOT_ALLOWED 405 overrides Supports-flag optimism for offline green paths.
- Freeze ACCEPT opens product only; product ACCEPT is offline only after separate review; no live/UI/bulk/completeness claim.
- Product-ready research does not implement tools and does not flip coverage.

## References

- Research (scratch): `.fractal/main.billy_complete/tmp/grok-research.md`
- Review (scratch): `.fractal/main.billy_complete/tmp/grok-review.md`
- Wiki freeze 5g: `wiki/wave_fiveg_ticketed_writes_contract.md`
- Wiki freeze ACCEPT 5g: `wiki/wave_fiveg_freeze_independent_review.md`
- Wiki product-ready research ACCEPT 5g: `wiki/wave_fiveg_product_ready_research_independent_review.md`
- Wiki freeze 5f: `wiki/wave_fivef_ticketed_writes_contract.md`
- Wiki freeze ACCEPT 5f: `wiki/wave_fivef_freeze_independent_review.md`
- Wiki product ACCEPT 5f: `wiki/wave_fivef_product_independent_review.md`
- Wiki offline probe policy: `wiki/offline_write_probe_rules.md`
