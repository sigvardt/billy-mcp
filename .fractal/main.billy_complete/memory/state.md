---
name: state
desc: Current node state, verified review decisions, and open qualification work.
tags: [billy, coverage, review]
sources:
  - docs/superpowers/specs/2026-07-28-billy-mcp-complete-design.md
  - https://www.billy.dk/api/
created: 2026-07-29T09:43:28Z
updated: 2026-07-29T09:43:28Z
---

# state

## Current state

- The shared foundation is merged: typed FastMCP coverage tools, locked API
  client, confirmation tickets, redaction, and forced-headless browser runtime
  exist. No domain `api_*`, `ui_*`, or `auth_*` tool is registered.
- The root still lacks the checked-in coverage manifests. The active coverage
  child must first fix the confirmed `bankLineMatche` singularization error and
  make the full-mode checker fail on every incomplete row before integration.
- The active hardening child owns three confirmed review fixes: reject `/v2/`
  client paths, redact organization subscription payment-card keys recursively,
  and load the browser allowlist fail-closed from the coverage manifest.
- The first headless UI pass reached only `https://mit.billy.dk/login` with no
  credentials or restored session. It made no write, retained no raw frame, and
  leaves every authenticated UI row red.

## Evidence boundaries

- Current official API fingerprint: ETag `hsisik4g9p3603`, 147934 bytes, MD5
  `c2efda0ee4cf9cf200e14910c5fc6996`; source is https://www.billy.dk/api/.
- The public source enumerates 46 resources, 207 clear operations, 92
  unresolved bulk mentions, six special routes, and no webhook API.
- `BILLY_API_TOKEN` and dedicated non-production organization credentials are
  unavailable. No live API, authenticated UI, or vision claim is valid.
- Full qualification must remain failing until generated coverage evidence
  marks every applicable API and UI row complete; an ordinary offline suite is
  only slice-level verification.

## Review decisions

- Confirmed: the pre-fix coverage manifest used `bankLineMatche` for the
  singular bank-line-match object in get/create/update/delete rows. The active
  coverage child owns the correction.
- Confirmed: the foundation allowed `/v2/...` in a relative API path, producing
  a doubled `/v2/v2/...` URL; payment-card subscription fields were not covered
  by the existing redaction key set; the browser policy lacked a typed manifest
  loader. The active hardening child owns these fixes.
- Rejected: removing all `.fractal` child seed files as "product pollution".
  The Fractal contract explicitly tracks node seeds in git; only a tracked empty
  runtime error artifact was removed. No seed contains credentials or raw UI
  evidence.

## References

- Current official research is in `wiki/billy_api_v2_research_seed.md`.
- Current UI login-surface evidence is in `wiki/billy_ui_discovery_brief.md`.
- The uncommitted independent review source is
  `.fractal/main.billy_complete/tmp/grok-review.md`.
