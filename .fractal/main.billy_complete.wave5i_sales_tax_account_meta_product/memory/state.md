---
name: state
desc: Terminal state of the Wave-5i sales-tax account and meta-field product deliverable.
created: 2026-07-30T00:51:29Z
updated: 2026-07-30T00:51:29Z
---

# state

The offline Wave-5i product provides twelve strict ticketed FastMCP tools for
the documented singular `salesTaxAccounts` and `salesTaxMetaFields` CUD
operations. Both resources use the root server's one confirmation store and
write protocol, opaque inner payload maps, exact client-relative paths, and no
write retry.

The locked-transport and root-server suites cover schema strictness, request
construction, response mapping, typed errors, ticket integrity, and executor
binding. Generated coverage marks only the six matching CUD rows implemented
and contract-tested: 157 offline rows, zero live or vision rows, 92 ambiguous
bulk rows, and `complete: false`.

Full non-live verification passed. The remaining boundary is independent parent
product review; live, UI, vision, and bulk qualification are not claimed.
