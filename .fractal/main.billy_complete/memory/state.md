---
name: state
desc: Current node state, verified review decisions, and open qualification work.
tags: [billy, coverage, review]
sources:
  - docs/superpowers/specs/2026-07-28-billy-mcp-complete-design.md
  - https://www.billy.dk/api/
created: 2026-07-29T12:12:38Z
updated: 2026-07-29T16:46:00Z
---

# state

## Current state

- Root includes Wave-5a plus the Wave-5b write implementation under P1/P2
  repair and re-review.
- Runtime: **142** `api_*` + 2 coverage; shared ConfirmationStore + WriteProtocolService; 24 preview + 24 execute writes.
- Coverage: implemented 118, contract_tested 118, live 0, vision 0, `complete: false`. Docs fingerprint unchanged.
- Wave-5a registration product: **ACCEPT** offline.
- Wave-5b freeze: **ACCEPT**. Its product review is **REJECTED / superseded**
  after P1 cross-executor binding and P2 ticket-retention findings; Wave-5c
  remains blocked.
- Wave-5c **research freeze** is ready (daybookTransactions + lines), but no
  product work may start until the P1 repair receives a new independent review.
- UI all red; bulk 92 empty-tool red; four specials red; 91 clear writes still red; no live token.

## Review decisions (authoritative)

- Wave-5a integrated product: **ACCEPT** offline.
- Wave-5b freeze: **ACCEPT**.
- Wave-5b product at `920ceab`: initial ACCEPT is void. A ticket bound for one
  execute tool could previously run through a different executor; repair and
  fresh independent review are mandatory.
- The same fallback review found unbounded expired/consumed ticket and prepared
  request retention. The repair candidate prunes that volatile state while
  retaining live ticket expiry and replay errors.
- Wave-5c research remains research only, with no greening.
- Overall completeness: **FAIL** until live, bulk, remaining writes, specials, UI/vision close red rows.
- The P1/P2 repair candidate passes lint, Pyright, coverage and
  repository-policy checks; the full non-live suite has **650** passing tests.
  It is not accepted until a fresh independent Grok review.

## Next work

1. Commit the P1/P2 repair and obtain a fresh independent Grok product review;
   Wave-5c stays blocked.
2. Promote Wave-5c research to wiki freeze only after that repaired product is
   accepted, then implement its 12 tools and review them.
3. Remaining clear writes (invoices/bills first), specials, bulk (live only),
   UI/auth/vision, live qualification, and the optional `groupId` fixture note.

## Evidence boundaries

- Official API fingerprint: etag `hsisik4g9p3603`, MD5 `c2efda0ee4cf9cf200e14910c5fc6996`.
- Focused Wave-5b + coverage suite: **65** passed at product review.
- Full post-P1/P2-repair root non-live verification: **650** passed.
- P1 regression evidence: an account-create ticket must return
  `CONFIRMATION_MISMATCH` with no request when supplied to an account-group or
  daybook-balance execute tool; it remains usable only by its exact executor.
- P2 regression evidence: preview and execution prune expired request bodies
  and expired replay markers while direct live expiry and replay remain typed.
- Unauth DELETE empty 200 is not cleanup proof.
- Unauth natures/postings 405 is not a green reclassification by itself.

## References

- Review: `.fractal/main.billy_complete/tmp/grok-review.md`
- Wiki product: `wiki/wave_fiveb_product_independent_review.md`
- Freeze 5b: `wiki/wave_fiveb_ticketed_writes_contract.md`
- Research 5c: `.fractal/main.billy_complete/tmp/grok-research.md`
