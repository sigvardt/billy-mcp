---
name: state
desc: Current node state, verified review decisions, and open qualification work.
tags: [billy, coverage, review]
sources:
  - docs/superpowers/specs/2026-07-28-billy-mcp-complete-design.md
  - https://www.billy.dk/api/
created: 2026-07-29T12:12:38Z
updated: 2026-07-29T19:32:00Z
---

# state

## Current state

- Wave-5c and Wave-5d parent/line write modules are merged into root; root registration uses the one shared `ConfirmationStore` and `WriteProtocolService`.
- Runtime: **166** `api_*` + 2 coverage; 36 preview + 36 execute ticketed write tools.
- Coverage: implemented 130, contract_tested 130, live 0, vision 0, `complete: false`.
- Official docs fingerprint still etag `hsisik4g9p3603`, MD5 `c2efda0ee4cf9cf200e14910c5fc6996` (body 147934 bytes). Re-fetched this research pass; byte-identical to prior freeze snapshot.
- Wave-5a registration product: **ACCEPT** offline.
- Wave-5b freeze: **ACCEPT**. Wave-5b product at `920ceab`: **REJECTED**. Repair product at `a2a0996`: **ACCEPT**.
- Wave-5c freeze: **ACCEPT**. Wave-5c product at tip `f235ac2`: **ACCEPT** offline by independent Grok.
- Wave-5d freeze at tip `5c376de`: **ACCEPT** offline contract only.
- Wave-5d product at tip **`1108e2f`**: **ACCEPT** offline by independent Grok (`wiki/wave_fived_product_independent_review.md`; full note `tmp/grok-review.md`).
- Reproduced the product review verification locally: focused ticket/registry/coverage suite **110 passed** and the non-live repository suite **753 passed**.
- Wave-5e contract is committed at `fc8118e`, but no independent Grok freeze ACCEPT exists. The Grok reviewer failed before edits because its CLI was unauthenticated; the required Codex fallback is active but non-gating.
- Clear red remaining: **77** of 207 clear ops (includes 6 Wave-5e bill/line CUD). After Wave-5e product: target **178** `api_*`, **136** offline rows.
- UI all red; bulk 92 empty-tool red; four specials red; no live token in process env.
- Historical unmerged review branches contain child-seed state and superseded fallback reports only, so they remain intentionally closed rather than merged. The completed Wave-5d Codex fallback audit is non-invasive and cannot replace the already-recorded Grok acceptance.

## Review decisions (authoritative)

- Wave-5a integrated product: **ACCEPT** offline.
- Wave-5b freeze: **ACCEPT**.
- Wave-5b product at `920ceab`: **REJECTED**.
- Wave-5b repair at `a2a0996`: **ACCEPT** offline.
- Wave-5c freeze: **ACCEPT** offline contract only.
- Wave-5c product at tip `f235ac2`: **ACCEPT** offline by independent Grok audit.
- Wave-5d freeze at tip `5c376de`: **ACCEPT** offline contract only.
- Wave-5d product at tip `1108e2f`: **ACCEPT** offline by independent Grok.
- Wave-5e freeze contract: **written, not independently accepted**. An unauthenticated Grok child and an unproven scratch claim do not open the product gate.
- Wave-5e product: **not accepted** until freeze ACCEPT + product review.
- Overall completeness: **FAIL** until live, bulk, remaining writes, specials, UI/vision close red rows.

## Open coverage work

1. Obtain an authenticated Grok freeze review for the committed Wave-5e contract; only then implement bills + billLines (target 178 `api_*`, 136 offline rows).
2. Remaining clear writes (~71 after Wave-5e), specials, bulk (live only), UI/auth/vision, and live qualification.

## Evidence boundaries

- Official API fingerprint: etag `hsisik4g9p3603`, MD5 `c2efda0ee4cf9cf200e14910c5fc6996`.
- Invoice-line writes declare `additional_plural_roots=("invoices",)` and map the parent root only when present.
- Bill line writes must declare `additional_plural_roots=("bills",)` (optional parent root when absent).
- Bill lines fields: account/taxRate/description/amount (not product/unitPrice).
- Bill `lines` has-many has no invoice-style required/replace/create-only notes offline.
- Unauth DELETE empty 200 is not cleanup proof.
- Product ACCEPT is offline only; no live/UI/bulk/completeness claim.
- Postings CUD still unauth HTTP 405 despite Supports flags — out of Wave-5e.
- `tmp/grok-review.md` claimed a Wave-5e Grok ACCEPT without attributable authenticated child evidence; it was rejected and purged rather than used as a gate.

## References

- Research (scratch): `.fractal/main.billy_complete/tmp/grok-research.md`
- Review (scratch): `.fractal/main.billy_complete/tmp/grok-review.md`
- Wiki freeze 5d: `wiki/wave_fived_ticketed_writes_contract.md`
- Wiki freeze ACCEPT 5d: `wiki/wave_fived_freeze_independent_review.md`
- Wiki product ACCEPT 5d: `wiki/wave_fived_product_independent_review.md`
- Wave-5c Grok product ACCEPT: `wiki/wave_fivec_product_independent_review.md`
