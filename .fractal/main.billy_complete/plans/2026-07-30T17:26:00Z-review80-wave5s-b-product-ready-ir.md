# Review80 — Wave-5s-B product-ready independent review

## Goal

Independently verify research80 product-ready handoff against current official
Billy docs, freeze, design §8.4, inventory honesty, and code absence of product.

## Verdict

**ACCEPT** offline as implementation handoff only. Completeness **FAIL**.
Product not accepted.

## Deliverables

- `tmp/grok-review.md`
- `wiki/wave_fivesb_files_upload_product_ready_research_independent_review.md`
- Memory and residual/product-ready gate updates

## Post-Mortem

Independently rechecked the research80 handoff against current official Billy
documentation and accepted it only as an offline product-implementation input.
No blocking contract defect was found. The review preserved the raw-binary
upload constraint, the live boolean ambiguity, and the mandatory post-product
Grok audit as explicit red gates. No browser, credentials, customer data, or
raw evidence were used. The next unresolved slice is the Codex Power product
implementation and its real offline tests; no product, live, UI, vision, bulk,
or completeness claim is supported yet.

Finding disposition: F1 was confirmed in the checker/test wording and corrected
to `raw-binary`; the cited official sample uses `--data-binary`, not
`multipart/form-data`. F2 was accepted as cosmetic because the maintained
residual wiki ranks files-upload as the next offline product slice. F3 remains
an explicit live-only ambiguity, so no offline green claim was added. F4 remains
an explicit project-completeness gate: the Wave-5s-A Grok product review is
still open and this Wave-5s-B handoff does not substitute for it.
