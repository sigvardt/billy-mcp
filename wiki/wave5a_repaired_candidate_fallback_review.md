---
name: wave5a_repaired_candidate_fallback_review
desc: Non-authoritative Codex Power fallback inspection of three repaired Wave-5a candidate tips; mandatory Grok review remains required.
tags: [billy, api, writes, review, wave5]
sources:
  - https://www.billy.dk/api/
  - wiki/wave_five_ticketed_writes_contract.md
  - wiki/wave_fivea_candidate_independent_review.md
  - docs/superpowers/specs/2026-07-28-billy-mcp-complete-design.md
created: 2026-07-29T15:03:33Z
updated: 2026-07-29T15:03:33Z
---

# wave5a_repaired_candidate_fallback_review

## Scope and authority

This is the policy-required Codex Power fallback inspection after the planned
Grok reviewer failed before producing a review artifact because it was not
authenticated. It inspected only the pinned candidate diffs below with clean
`git archive` exports. It is **not** an independent Grok review, does **not**
satisfy the mandatory cited Grok review gate, and cannot authorize any candidate
merge.

The source baseline is `5ab3efa3e29fb08cdebe45d9fc3da7fe15c51ace`. Child seed
state and every uncommitted child file were excluded from review.

## Contract sources

The cited Grok brief identifies the official [Billy API documentation](https://www.billy.dk/api/)
as current at ETag `hsisik4g9p3603` and MD5 `c2efda0ee4cf9cf200e14910c5fc6996`.
It documents singular `POST`/`PUT`/`DELETE` under the locked
[`https://api.billysbilling.com/v2`](https://api.billysbilling.com/v2) base:
create and update use one singular request root, delete has no body, and write
responses may include all changed plural roots plus optional
`meta.deletedRecords`. See the official
[create/update/delete response guidance](https://www.billy.dk/api/#responses-to-createupdatedelete-requests)
and the frozen [[wave_five_ticketed_writes_contract]]. Unauthenticated delete
responses are explicitly non-qualification evidence.

Design sections 6 and 8 require separate preview/execute tools, ticket-only
execute input, non-mutating previews, and exact single-use ticket binding. The
prior [[wave_fivea_candidate_independent_review]] remains the authoritative
independent-review history; this page changes none of its gate requirements.

## Candidate findings and verdicts

| Candidate | Exact commit and reviewed files | Findings from the pinned diff | Fallback verdict |
| --- | --- | --- | --- |
| Protocol response mapping | `4b2c12cacad991fa07842c63054689eabed3e311` — `src/billy_mcp/api/write_protocol.py`; `tests/unit/test_write_protocol.py` | No fallback finding. Declared primary plus `additional_plural_roots` map only when present and valid; undeclared roots are omitted. `meta.deletedRecords` maps only declared roots, remains absent when absent, and malformed declared roots return `VALIDATION_ERROR`. | Checks pass; this fallback provides **no merge approval**. |
| Contact writes | `a86afe971b058567cba627b5a6fefcd32c0cc7fb` — `src/billy_mcp/api/contact_writes.py`; `tests/api/test_contact_writes.py` | No fallback finding. FastMCP exposes flat preview fields (`contact`, then `id` plus `contact` for update), never an `input` envelope. Execute schemas accept only `confirmation_ticket`; outer schemas forbid extras. | Checks pass; this fallback provides **no merge approval**. |
| Contact-person writes | `341d0b110d8beb664ec7bc75a534a1fa9bfc84ef` — `src/billy_mcp/api/contact_person_writes.py`; `tests/api/test_contact_person_writes.py` | No fallback finding. The update-preview schema has top-level `id` with `minLength: 1` and `contactPerson`; execute schemas accept only `confirmation_ticket` and forbid extras. | Checks pass; this fallback provides **no merge approval**. |

The exact three-dot comparisons (`5ab3efa...<candidate>`) contained no
non-seed product changes outside the six files listed above. In particular,
there was no inventory, coverage/status, server-registration, live, UI, vision,
or bulk-qualification change.

## Boundary inspection

| Required boundary | Evidence in the archived candidates |
| --- | --- |
| Preview is non-mutating | Protocol preview creates canonical state and a ticket without calling the client. Each focused suite asserts zero observed HTTP requests during preview. |
| Execute is ticket-only | `WriteExecuteInput` has `extra="forbid"` and only `confirmation_ticket`. Direct FastMCP inspection showed each contact and contact-person execute tool has exactly that required field and `additionalProperties: false`. |
| Exact, single-use ticket binding | Protocol tests cover tampering, expiry, concurrent execution, replay, and mismatched tool, organisation, target, canonical request, and expected effect. Exactly one concurrent execution reaches the mock transport. |
| Writes are not retried | A protocol test returns 503 and observes exactly one request; execution makes one stored `client.request` call. |
| Paths omit duplicate `/v2` | The operation validator rejects `/v2`-prefixed paths. Resource specs use `/contacts` and `/contactPersons`; tests observe `/v2` exactly once at the locked-client boundary. |
| No sensitive values are logged | The three candidate modules contain no logging or print invocation. The protocol suite verifies redaction of an upstream `confirmation_ticket` and excludes a tampered ticket from its error message. No ticket or contact value is recorded here. |
| Multi-root/deleted mapping | New protocol tests cover present/absent additional roots, declared deleted roots, undeclared-root omission, and malformed-root rejection. |

## Reproducible clean-export evidence

Each command ran from an owner-only (`0700`) `mktemp` directory under this
node's ignored `tmp/` directory. Each destination contained only committed
bytes from the named revision.

```sh
git archive 4b2c12c | tar -xf - -C "$review_tmp/protocol"
(cd "$review_tmp/protocol" && uv run pytest -q tests/unit/test_write_protocol.py)
# 29 passed in 0.57s

git archive a86afe9 | tar -xf - -C "$review_tmp/contacts"
(cd "$review_tmp/contacts" && uv run pytest -q tests/api/test_contact_writes.py)
# 18 passed in 2.25s

git archive 341d0b1 | tar -xf - -C "$review_tmp/contact_persons"
(cd "$review_tmp/contact_persons" && uv run pytest -q tests/api/test_contact_person_writes.py)
# 11 passed in 2.26s
```

For every candidate, `git diff --check` against the stated three-dot baseline,
`uv run ruff check <reviewed source> <reviewed test>`, and
`uv run pyright <reviewed source>` passed with no reported issue. The focused
tests cover schema, mutation, exact method/path/body, typed 401/404,
ticket-lifecycle, and response-mapping behavior appropriate to each file.

Direct FastMCP schema inspection also confirmed:

- contacts: preview properties are `contact`; `id`, `contact`; and `id`; every
  execute property set is only `confirmation_ticket` with `minLength: 1`.
- contact persons: update preview properties are `id`, `contactPerson`, with
  `id.minLength == 1`; every execute property set is only
  `confirmation_ticket`.

## Qualification and merge gate remain fail-closed

This inspection did not run live or browser actions, create any Billy record,
or alter any qualification record. The following stay red/fail-closed:

- `live_tested`, all UI and vision/interface states, and `complete`;
- all 92 ambiguous bulk rows;
- unauthenticated-delete cleanup/live claims;
- every out-of-cohort write, special, auth, webhook, and UI capability.

No candidate is approved for merge by this page. The mandatory cited Grok
independent review, not this fallback, must issue the merge-gate decision. After
this fallback was completed, the parent reported a separate fresh Grok review
accepting the three pinned product/test tips for selective merge while retaining
all qualification categories above as red; that separate result is not evidence
generated or approved by this page.
