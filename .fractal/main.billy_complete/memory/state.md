---
name: state
desc: Current node state, verified review decisions, and open qualification work.
tags: [billy, coverage, review]
sources:
  - docs/superpowers/specs/2026-07-28-billy-mcp-complete-design.md
  - https://www.billy.dk/api/
created: 2026-07-29T09:43:28Z
updated: 2026-07-29T09:52:00Z
---

# state

## Current state

- Shared foundation is merged on root: FastMCP coverage tools, locked API
  client, confirmation tickets, redaction, forced-headless browser runtime.
  No domain `api_*`, `ui_*`, or `auth_*` tool is registered.
- Root contains the generated coverage inventory: 305 API rows and 339 UI
  rows. They remain red except for discovery evidence where documented;
  `coverage/status.json` is generated and `complete: false`.
- Root includes the reviewed hardening: client paths beginning `/v2/` are
  rejected, subscription card fields are redacted, and browser egress loads
  fail-closed from the checked-in manifest.
- UI discovery completed: headless reach of `https://mit.billy.dk/login` only.
  No credentials; no writes; frame purged. Brief in
  `wiki/billy_ui_discovery_brief.md`.
- Latest Grok research brief:
  `.fractal/main.billy_complete/tmp/grok-research.md` (docs fingerprint
  unchanged; next slice is Phase 0 merge then wave-1 reads).

## Evidence boundaries

- Current official API fingerprint: ETag `hsisik4g9p3603`, 147934 bytes, MD5
  `c2efda0ee4cf9cf200e14910c5fc6996`; source is https://www.billy.dk/api/.
- Public source: 46 resources, 207 clear operations, 92 unresolved bulk
  mentions, six special routes, no webhook API, no `ids[]` on page.
- `BILLY_API_TOKEN` and dedicated non-production organization credentials are
  unavailable. No live API, authenticated UI, or vision claim is valid.
- Full qualification must remain failing until generated coverage evidence
  marks every applicable API and UI row complete.
- Ordinary lint and offline tests pass on the merged root. Full mode fails at
  `--require-complete` because all API/UI live evidence is absent and the 92
  bulk contracts remain ambiguous; it does not soft-pass.

## Review decisions

- Confirmed: coverage uses `bankLineMatch`, not `bankLineMatche`.
- Confirmed: the `POST /v2/files` mapping uses
  `alias_of: api.special.files_upload`.
- Confirmed: foundation double-prefix `/v2/v2/...` risk; hardening rejects
  paths that start with `/v2/`.
- Confirmed: subscription card fields need redaction; hardening expands keys.
- Rejected: removing Fractal seed trees as product pollution (tracked seeds
  are intentional).

## Next Codex Power slice (from research)

1. Implement Wave 1 read tools only: user/orgs bootstrap, currencies/countries/
   locales, products/productPrices, contacts get/list.
2. Contract tests use fixtures and locked mock transport; no `live_tested`
   without a dedicated non-production token.

## References

- Research: `.fractal/main.billy_complete/tmp/grok-research.md`
- Review: `.fractal/main.billy_complete/tmp/grok-review.md`
- Wiki: `wiki/billy_api_v2_research_seed.md`, `wiki/billy_ui_discovery_brief.md`,
  `wiki/phase_zero_contract.md`
