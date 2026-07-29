---
name: state
desc: Current node state, verified review decisions, and open qualification work.
tags: [billy, coverage, review]
sources:
  - docs/superpowers/specs/2026-07-28-billy-mcp-complete-design.md
  - https://www.billy.dk/api/
created: 2026-07-29T12:12:38Z
updated: 2026-07-29T20:50:00Z
---

# state

## Current state

- Wave-5c through Wave-5e parent/line write modules are merged into root; root registration uses the one shared `ConfirmationStore` and `WriteProtocolService`.
- Runtime: **178** `api_*` + 2 coverage; 42 preview + 42 execute ticketed write tools. No tax write tools yet.
- Coverage: implemented 136, contract_tested 136, live 0, vision 0, `complete: false`.
- Official docs fingerprint still etag `hsisik4g9p3603`, MD5 `c2efda0ee4cf9cf200e14910c5fc6996` (body 147934 bytes). Independent freeze review re-fetch matches.
- Wave-5e product at tip **`15d0bde`** / root record **`c92ed0e`**: **ACCEPT** offline.
- Wave-5f freeze at tip **`d412e8c`**: **ACCEPT** offline by authoritative root Grok (`wiki/wave_fivef_freeze_independent_review.md`). Product gate open; product code still absent.
- UI all red; bulk 92 empty-tool red; four specials red; no live token in process env.
- Historical unmerged review branches remain intentionally closed rather than merged.

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
- Wave-5f product: **not started / not accepted**.
- Overall completeness: **FAIL** until live, bulk, remaining writes, specials, UI/vision close red rows.

## Open coverage work

1. Wave-5f product: implement `tax_writes.py` under the accepted freeze (6 clear CUD; +12 tools / +6 offline rows; registry target 190 `api_*`, coverage 142).
2. Remaining clear writes after 5f, specials, bulk (live only), UI/auth/vision, and live qualification.

## Freeze review evidence (Wave-5f)

- Docs re-fetch at review: ETag `hsisik4g9p3603`, MD5 match, 147934 bytes — no source drift.
- Six inventory CUD tool names and routes match freeze table; bulk empty-tool red.
- Unauth POST/PUT **401**; missing-id DELETE **200** (not cleanup proof).
- No `tax_writes.py`; no premature coverage green.
- The review's `api.billy.dk` restatement is non-blocking: the freeze and
  approved design positively lock API traffic to `https://api.billysbilling.com/v2`.
  Product host-lock tests should still cover the denied sample host.

## Evidence boundaries

- Official API fingerprint: etag `hsisik4g9p3603`, MD5 `c2efda0ee4cf9cf200e14910c5fc6996`.
- Tax-rate parent may optionally map `taxRateDeductionComponents` like products→productPrices; child stays without additional roots offline.
- Unauth DELETE empty 200 is not cleanup proof.
- Unauth METHOD_NOT_ALLOWED 405 overrides Supports-flag optimism for offline green paths.
- Freeze ACCEPT opens product only; product ACCEPT is offline only after separate review; no live/UI/bulk/completeness claim.

## References

- Research (scratch): `.fractal/main.billy_complete/tmp/grok-research.md`
- Review (scratch): `.fractal/main.billy_complete/tmp/grok-review.md`
- Wiki freeze 5f: `wiki/wave_fivef_ticketed_writes_contract.md`
- Wiki freeze ACCEPT 5f: `wiki/wave_fivef_freeze_independent_review.md`
- Wiki freeze ACCEPT 5e: `wiki/wave_fivee_freeze_independent_review.md`
- Wiki product ACCEPT 5e: `wiki/wave_fivee_product_independent_review.md`
