---
name: state
desc: Current node state, verified review decisions, and open qualification work.
tags: [billy, coverage, review]
sources:
  - docs/superpowers/specs/2026-07-28-billy-mcp-complete-design.md
  - https://www.billy.dk/api/
created: 2026-07-29T21:14:11Z
updated: 2026-07-29T21:42:00Z
---

# state

## Current state

- Wave-5c through Wave-5f parent/line write modules are merged into root; root registration uses the one shared `ConfirmationStore` and `WriteProtocolService`.
- Root merge `353449d` integrates Wave-5f product `8c1cdf6`: **190** `api_*` + 2 coverage tools and 48 preview + 48 execute ticketed write tools, including tax-rate and deduction-component CUD. Root tip records product ACCEPT at **`70e0506`**.
- Coverage: implemented 142, contract_tested 142, live 0, vision 0, `complete: false`.
- Root verification passed Ruff, Pyright, 260 focused contract tests, 850 non-live tests, coverage validation, and repository policy checks.
- Official docs fingerprint still etag `hsisik4g9p3603`, MD5 `c2efda0ee4cf9cf200e14910c5fc6996` (body 147934 bytes). Research31 re-fetch matches (byte-identical to research30).
- Wave-5e product at tip **`15d0bde`** / root record **`c92ed0e`**: **ACCEPT** offline.
- Wave-5f freeze at tip **`d412e8c`** / record **`e39704b`**: **ACCEPT** offline (`wiki/wave_fivef_freeze_independent_review.md`).
- Product-ready research tip **`1c9e6cb`**: independent Grok **ACCEPT** as Codex handoff only.
- Wave-5f product at root merge **`353449d`** / product **`8c1cdf6`**: **ACCEPT** offline (`wiki/wave_fivef_product_independent_review.md`).
- Wave-5g research revalidated (research31): freeze target remains **`salesTaxRulesets` + `salesTaxRules`** (6 CUD; +12 tools; target 202 `api_*`, 148 offline). Brief at `.fractal/main.billy_complete/tmp/grok-research.md`. Research is not freeze or product authorisation.
- UI all red; bulk 92 empty-tool red; four specials red; no live token in process env.
- Historical unmerged review branches remain intentionally closed rather than merged.
- Parent branch `main` is current at this branch's merge base. Remaining divergent historical child branches hold review seed or non-authoritative fallback evidence already covered by root review records.

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
- Wave-5g freeze: **research only** (not frozen, not accepted).
- Overall completeness: **FAIL** until live, bulk, remaining writes, specials, UI/vision close red rows.

## Open coverage work

1. Freeze then product the research-backed Wave-5g `salesTaxRulesets` + `salesTaxRules` cohort (6 CUD; +12 tools; target 202 `api_*`, 148 offline rows). Wave-5f product acceptance is done.
2. Later: sales-tax accounts/meta-fields, payments/returns partial CUD, attachments, specials, bulk (live only), UI/auth/vision.
3. Blocked offline without more evidence: `accountNatures` and `postings` writes (unauth 405 overrides Supports), `bankPayments` delete (405), `transactions` CUD (all-readonly property table). OPTIONS ACM listing POST is not authority when real method returns 405.

## Wave-5g research evidence (pre-freeze, research31)

- Docs re-fetch: same ETag/MD5/bytes as freeze fingerprint; date `Wed, 29 Jul 2026 21:40:38 GMT`.
- Unauth: salesTaxRulesets/Rules POST/PUT **401**, DELETE missing-id **200**, OPTIONS 204 with full ACM set.
- Parent `additional_plural_roots=("salesTaxRules",)`; child `()`.
- Almost all fields immutable on both resources; keep opaque payloads; still ship ticketed update (Supports + 401, not 405).
- Attachments alternate ready (3 CUD; mutable `priority`; needs `fileId` for live).
- `accountNatures`/`postings` POST/PUT/DELETE unauth **405** — do not offline-green from Supports; OPTIONS ACM is not write proof.
- `salesTaxPayments` DELETE **405** (inventory already create/update only); `salesTaxReturns` POST/DELETE **405** (update only).
- `bankPayments` DELETE **405** despite Supports delete claim.
- Files create remains special binary upload; empty `tool_name` on clear `api.files.create`.

## Evidence boundaries

- Official API fingerprint: etag `hsisik4g9p3603`, MD5 `c2efda0ee4cf9cf200e14910c5fc6996`.
- Tax-rate parent may optionally map `taxRateDeductionComponents` like products→productPrices; child stays without additional roots offline.
- Unauth DELETE empty 200 is not cleanup proof.
- Unauth METHOD_NOT_ALLOWED 405 overrides Supports-flag optimism for offline green paths.
- Freeze ACCEPT opens product only; product ACCEPT is offline only after separate review; no live/UI/bulk/completeness claim.
- Product-ready research ACCEPT is handoff only, not product ACCEPT.
- Wave-5g research is not freeze ACCEPT and not product ACCEPT.

## References

- Research (scratch): `.fractal/main.billy_complete/tmp/grok-research.md`
- Review (scratch): `.fractal/main.billy_complete/tmp/grok-review.md`
- Wiki freeze 5f: `wiki/wave_fivef_ticketed_writes_contract.md`
- Wiki freeze ACCEPT 5f: `wiki/wave_fivef_freeze_independent_review.md`
- Wiki product ACCEPT 5f: `wiki/wave_fivef_product_independent_review.md`
- Wiki freeze ACCEPT 5e: `wiki/wave_fivee_freeze_independent_review.md`
- Wiki product ACCEPT 5e: `wiki/wave_fivee_product_independent_review.md`
- Wiki offline probe policy: `wiki/offline_write_probe_rules.md`
