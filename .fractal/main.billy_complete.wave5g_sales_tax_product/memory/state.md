---
name: state
title: Wave-5g delivery state
desc: Current bounded delivery state for the sales-tax ruleset and rule write slice.
created: 2026-07-29T22:18:36Z
updated: 2026-07-29T22:18:36Z
---

# Wave-5g delivery state

The bounded offline sales-tax delivery contains twelve ticketed ruleset and
rule CUD tools. It uses the root server's shared write protocol and confirmation
store, preserves opaque inner payloads with strict flat outer schemas, and
keeps all requests client-relative and single-attempt.

Focused and root-server cross-executor tests cover ticket binding, replay and
expiry, exact request construction, declared response roots, and delete
metadata. Generated coverage marks only the six accepted CUD rows as
implemented and contract-tested: 148 offline rows, zero live and vision rows,
92 ambiguous bulk rows, and `complete: false`.

The product contract remains limited to the accepted Wave-5g ruleset/rule
slice. Parent ownership covers post-merge integration and the independent Grok
product audit.
