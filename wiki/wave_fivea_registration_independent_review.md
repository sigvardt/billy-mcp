---
name: wave_fivea_registration_independent_review
desc: Independent Grok ACCEPT of integrated Wave-5a ticketed write registration on the root branch.
tags: [billy, review, writes, coverage]
sources:
  - https://www.billy.dk/api/
  - docs/superpowers/specs/2026-07-28-billy-mcp-complete-design.md
  - wiki/wave_five_ticketed_writes_contract.md
  - coverage/status.json
created: 2026-07-29T16:05:00Z
updated: 2026-07-29T16:05:00Z
---

# wave_fivea_registration_independent_review

## Verdict

**ACCEPT** the integrated Wave-5a root registration product as offline-complete
for its frozen scope. **FAIL** overall product completeness (expected).

Root HEAD under review: `36e5b6250b0cef97cdb68e52a16649252a8b74a9` (merge
`45f099f` of `main.billy_complete.wave5a_root_registration` tip `7cb74e2`).

## What was accepted

- Runtime exposes **124** `api_*` tools and **2** coverage tools, including
  **30** ticketed write tools (15 preview + 15 execute) for products,
  productPrices, contacts, contactPersons, and daybooks.
- One shared `ConfirmationStore` and one shared `WriteProtocolService` are
  constructed in `create_server` and passed to all four write registrars.
- Fifteen clear inventory CUD rows are offline-green only:
  `implemented=true`, `contract_tested=true`, `live_tested=false`, with
  preview `tool_name` values and real test references.
- Focused offline suite: **128** passed. Coverage checker
  `--reject-false-completeness` passed. Official docs fingerprint matches
  inventory (ETag `hsisik4g9p3603`, MD5 `c2efda0ee4cf9cf200e14910c5fc6996`).

## What remains deliberately red

- All `live_tested` flags (token unavailable).
- **92** ambiguous bulk rows (empty `tool_name`).
- **100** remaining clear singular write rows.
- Four special routes (files upload, invoice email, invoice delivery, invoice
  logs). User get / organisations stay green as before.
- All **339** UI rows and all vision states.
- `coverage/status.json` `complete: false`.

## Safety sampled

Ticket entropy ≥256 bits, TTL ≤5 minutes, single-use consume, execute accepts
only `confirmation_ticket`, preview performs no HTTP write, API base locked to
`https://api.billysbilling.com/v2`, no generic HTTP/browser tools, no live
greening from unauthenticated DELETE 200 observations, no retained browser
frames or credentials in product trees.

## Next product gate

Wave-5b offline ticketed writes for `accountGroups`, `accounts`, and
`daybookBalanceAccounts` only after a cited research brief and Codex Power
implementation. Do not treat this ACCEPT as live, UI, bulk, or completeness
approval.

Full evidence path for the run that produced this verdict:
`.fractal/main.billy_complete/tmp/grok-review.md`.
