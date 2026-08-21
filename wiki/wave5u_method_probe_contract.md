---
name: wave5u_method_probe_contract
title: Wave-5u safe method-observation contract
desc: Research-only, fail-closed contract for residual and bulk real-method observation. Every unproven candidate is blocked before network traffic; no coverage or review gate changes.
tags: [billy, api, research, live-gate, residual, bulk, safety]
sources:
  - https://www.billy.dk/api/
  - ".fractal/main.billy_complete/tmp/grok-research.md (research90; transient parent scratch)"
  - wiki/wave_fives_residual_specials_research.md
  - .fractal/main.billy_complete/plans/2026-07-30T21:14:49.522Z-142.21-wave5u_method_level_observation.md
  - src/billy_mcp/live_probe.py
  - tests/unit/test_live_probe.py
  - tests/live/test_live_probe.py
created: 2026-07-30T21:25:30Z
updated: 2026-08-01T01:45:00Z
---

# Wave-5u safe method-observation contract

## Delivered boundary

This is a research/infrastructure contract, not an implementation, a live
qualification, a supported-operation claim, or a mutation-success claim. It
freezes the only candidate request shapes a future runner may consider, then
blocks every one of them before network traffic because current evidence does
not prove the shape cannot make a durable Billy change.

The public [Billy API v2 documentation](https://www.billy.dk/api/) fixes the
base URL as `https://api.billysbilling.com/v2`, describes plural resource paths,
JSON roots for ordinary create/update requests, bodyless singular deletes, and
idempotent delete responses for missing records. It does **not** document a
safe no-op real-method probe, a bulk payload/response contract, or a cleanup
proof for this frozen matrix.

This Codex Power fallback was required after the designated Grok research leaf
failed host authentication before making an edit. It names that limitation and
does **not** replace the mandatory Grok research or independent-review gate.
Nothing here authorizes implementation, a live run, coverage greening, or a
product decision.

## Evidence provenance and classification

### Facts

- The exact base is `https://api.billysbilling.com/v2`; an alternate Billy host,
  a proxy, a caller-supplied base, or an unrecognised path is rejected before
  networking. The official documentation is the authority for this endpoint and
  the generic create/update/delete conventions.
- The existing immutable matrix in `src/billy_mcp/live_probe.py` names 29
  residual rows and 92 bulk rows: each residual row is `POST`, `PUT`, or
  `DELETE`; bulk-save is `PUT /{resource}/bulk`; bulk-delete is
  `DELETE /{resource}` with `ids[]`.
- **research90** is the cited parent-scratch brief at
  `.fractal/main.billy_complete/tmp/grok-research.md`. Its reproducible
  unauthenticated observations are preserved in the checked-in relay
  [[wave_fives_residual_specials_research]]: `OPTIONS` produced an empty `204`
  and indistinguishable full CORS method lists on both a known-closed route and
  routes that returned `401` for their real method. The transient scratch file
  is not present in this fallback checkout, so no raw response is recreated or
  represented as newly observed evidence.
- The parent implementation plan and the focused probe tests already require a
  token, matching dedicated non-production organisation values, a locked base,
  and owner-only evidence. Those existing `OPTIONS` observations remain
  unqualified.

### Conservative inferences and resulting rule

- An unauthenticated `401` only records that authentication stopped the
  request. It does not establish an authenticated supported operation, a safe
  payload, a response root, or live qualification.
- An unauthenticated `405` is not a live-qualified capability result.
- An empty `OPTIONS` `204`, even with advertised methods, is not a real-method
  contract and never qualifies a route.
- A `200` containing only `meta` is not a changed-record response, cleanup
  proof, or mutation-success signal.

Therefore, a body with no business values, an empty array, or a missing-id
route is only a *candidate shape*. It is not proof of non-persistence. The
safety decision for every candidate below is **BLOCK BEFORE NETWORK** until a
later, separately reviewed non-production study proves that exact shape is
non-persistent and supplies cleanup/read-back evidence where relevant.

## Universal pre-network gate

All checks are local and fail closed. A future runner must make zero HTTP
requests unless every condition holds:

1. The base URL equals the literal
   `https://api.billysbilling.com/v2`; the candidate id exists in the frozen
   matrix; and its route, method, query, body root, and content type are chosen
   by that matrix rather than caller input.
2. A token is available locally, and two independently supplied values identify
   the **same dedicated non-production organisation**. The runner must verify
   that the token is explicitly matched to that organisation before observing a
   real method. Tokens, organisation ids, names, and verification responses are
   never read into this page, evidence record, or commit.
3. A pre-existing owner-only evidence directory lies outside the repository and
   has verified owner access. Repository paths, temporary captures, screenshots,
   HAR files, browser traces, headers, and response bodies are forbidden.
4. The candidate has a later approved non-production safety proof for the exact
   construction in the table. **No row has that proof in this contract**, so the
   required result now is a pre-network block rather than a request.

No browser is needed or authorised by this contract. Any later browser work is
headless-only and remains outside this method-observation scope.

## Frozen static candidate construction

`R` is the exact resource segment already frozen for the candidate id; it is
not supplied by a caller. `S` is that resource's documented singular JSON root
and `P` its documented plural root. `:id` has one nominal replacement only:
an owner-verified absent identifier held outside the repository. A literal
placeholder is not evidence that the identifier is absent, so a missing proof
causes the universal gate to block before any URL is built.

| Candidate kind | Frozen method and route replacement | Query | Frozen body and content type | Non-persistence decision |
| --- | --- | --- | --- | --- |
| residual create | `POST /R` | none | `{"S": {}}`; `application/json` | The documentation's ordinary create envelope establishes only syntax. It does not prove an empty object cannot create a default record. **BLOCK BEFORE NETWORK.** |
| residual update | `PUT /R/:id` with `:id →` owner-verified absent identifier | none | `{"S": {}}`; `application/json` | The generic update convention says omitted properties are unchanged, but neither that rule nor an unverified absent identifier proves this precise request has no durable effect. **BLOCK BEFORE NETWORK.** |
| residual singular delete | `DELETE /R/:id` with `:id →` owner-verified absent identifier | none | no body; no `Content-Type` | The public idempotent-delete rule describes a missing record response, not proof that this identifier is absent in the matched organisation or that cleanup is complete. **BLOCK BEFORE NETWORK.** |
| bulk save | `PUT /R/bulk` | none | JSON **object** root required (`INVALID_REQUEST_BODY` for array/null/string/missing); object root reaches unauth `AUTHENTICATION_REQUIRED` (research136). Empty-array no-op, plural-key field schema, response, and partial failure remain unproven. Official page lists Supports bulk save only. **BLOCK BEFORE NETWORK.** |
| bulk delete | `DELETE /R` | exactly `ids[]=` (one empty `ids[]` value) | no body; no `Content-Type` | The collection query form is only a shape hint. It does not prove that an empty list is a no-op rather than an error or a broad delete. **BLOCK BEFORE NETWORK.** |

### Bulk-delete form evidence (research95 unauth reconfirm)

Unauthenticated probes on open bulk-delete collections (for example contacts,
products, accounts, invoices, bills) and on
`invoiceReminderAssociations` establish these form facts. They are **not**
authenticated non-persistence proofs and do **not** open networking:

| Form | Unauth result | Rule |
| --- | --- | --- |
| `DELETE /R?ids[]=` (empty value), bare `ids[]`, `ids=`, JSON `{"ids":[]}`, or empty plural root body | **400** `INVALID_DELETE_ID_ARRAY` | Empty is a validation **error**, never a safe no-op product path |
| `DELETE /R?ids[]=<synthetic-absent-id>` | **200** meta-only | Looks like a missing-id response without auth; **not** live cleanup proof under a real token |
| `DELETE /bankPayments?ids[]=` | **405** | bankPayments does not open this bulk form unauth |

The frozen bulk-delete candidate may keep the query name exactly `ids[]`. It
must still **BLOCK BEFORE NETWORK** until a separately reviewed non-production
study proves non-persistence with dual organisation match, owner-verified
identifiers, cleanup/read-back, and sanitised owner-only evidence.

The 29 residual rows contain create, update, and singular-delete shapes. The
92 bulk rows are 46 resource pairs using the last two shapes. A future runner
must emit the fixed row shape only; it must never substitute a resource,
identifier, query value, root name, or payload from user input.

### Invoice-reminder-association delete reconciliation

`api.invoiceReminderAssociations.delete` is the residual **singular** candidate:
`DELETE /invoiceReminderAssociations/:id`, no query, no body, and the
owner-verified-absent-id replacement above. It remains blocked.

The `ids[]` hint belongs only to the distinct collection bulk-delete candidate:
`DELETE /invoiceReminderAssociations?ids[]=`. An unauthenticated error or
meta-only response on either route neither converts the singular row into bulk
delete nor proves that the collection request is safe. That bulk candidate also
remains blocked.

## Evidence and result handling

If a later reviewed contract opens a candidate, the only retained evidence is
one sanitised record per observation with these fields and no others:

```json
{
  "candidateId": "frozen candidate id",
  "method": "POST, PUT, or DELETE",
  "route": "frozen static route template",
  "status": 401,
  "errorCode": "optional top-level errorCode only"
}
```

`status` is the HTTP status; `errorCode` is omitted unless it is a top-level
field in a parsed response object. The route is the matrix template, never an
actual identifier, organisation value, full URL, or response-derived value.
No evidence may retain headers, response bodies, tokens, customer values,
organisation values, screenshots, HAR files, traces, request bodies, or
transport diagnostics. Evidence stays owner-only and outside the repository.

No status or evidence record changes a candidate state by itself. In particular,
`401`, `405`, empty `OPTIONS` `204`, transport failure, and meta-only `200`
remain unqualified observations. A mutation-success claim requires a later
explicit changed-record and cleanup/read-back contract; it cannot be inferred
from this page.

## Programme state and explicit non-claims

- Residual **29**, ambiguous bulk **92**, and every UI row remain red.
- Coverage remains **184/184/0/0** and `complete: false`; this page makes zero
  coverage, status, source, test, dependency, tool, webhook, or browser-control
  changes.
- No generic HTTP controller, MCP tool, write path, webhook, live probe, or
  persistent/disposable data path is introduced.
- The required Grok research/review gate remains open. This named Codex Power
  fallback is supplemental research infrastructure only.

## Research136 bulk-save body matrix (offline)

Fail-closed fixture `research136_bulk_save_body_matrix` in
`src/billy_mcp/live_probe.py` freezes unauthenticated bulk-save body classes
only. It does **not** open real-method network paths, register tools, claim
cleanup, or change coverage green state. Bulk delete empty-`ids[]` and
synthetic meta-only 200 rules remain research95/96. All 92 bulk inventory rows
stay `ambiguous_bulk` with empty tools.

## Bulk external-contract blocker (research137)

After official documentation and versioned official asset exhaust, bulk save and
bulk delete remain **BLOCK BEFORE NETWORK** for product tools. Inventory rows
carry `qualification.blocker_code=BULK_SCHEMA_UNSPECIFIED_OFFICIAL_DOCS` and
stay `ambiguous_bulk`. Offline object-root / `ids[]` shape hints (research136)
are not a full contract. Live API bulk qualification is out of user scope.
Further bulk evidence-only loops are closed until Billy publishes schemas.

