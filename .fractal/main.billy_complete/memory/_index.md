---
name: memory
desc: Node private working state for billy_complete.
tags: []
sources: []
created: 2026-07-29T07:56:19Z
updated: 2026-07-29T08:56:00Z
---

# memory

***

## Status

- Step role: Grok research. Official API contract reconfirmed unchanged.
- Research brief: `.fractal/main.billy_complete/tmp/grok-research.md` (replaced).
- Independent review still **FAIL** until Phase 0 freeze lands: `.fractal/main.billy_complete/tmp/grok-review.md`.
- Phase 0 baseline now provides `pyproject.toml`, `uv.lock`, root-owned typed
  models, CI, repository-policy scanning, and baseline unit tests. It is
  dependency-audited and passes Ruff, Pyright, pytest, and policy checks.
- `coverage/` and the concrete FastMCP foundation are not yet present; they
  remain owned by the planned focused children.
- Parent radio `F6A16386`: write access restored; implement Phase 0 now (Codex Power execute).

## Contract fingerprint (current)

- Primary: https://www.billy.dk/api/
- etag `hsisik4g9p3603`; body 147934 bytes; MD5 `c2efda0ee4cf9cf200e14910c5fc6996`
- 46 resources; 299 Supports flags; 207 clear G/L/C/U/D; 92 bulk ambiguous; 0 webhooks
- Paging: `page` + `pageSize` only (offset is bank-fee prose, not list param)
- Live 401s: `AUTHENTICATION_REQUIRED`, `OAUTH_INVALID_ACCESS_TOKEN` (+ optional non-JSON log prefix)
- Specials: files upload, invoice emails, invoiceDeliveries, invoiceLogs, user, user/organizations
- Singular sample `GET /v2/organization` unproven vs `/v2/organizations`
- No `/v2/documents` resource (CMS noise)

## Operator facts

- `BILLY_API_TOKEN`: unavailable (env, keyring module, common paths, security keychain name probes empty)
- Headless profile: `/Users/user/.local/share/billy-mcp/chrome-profile` (exists; use headless only after Playwright installed)
- Playwright is installed from the locked dependency set; Chromium launch has
  not yet been exercised.

## Next owned work (Codex Power)

1. Freeze red `coverage/api_v2_manifest.yaml` (+ UI + browser_egress + status.json complete:false).
2. Shared FastMCP foundation: locked client, tickets, redaction, coverage_* only; zero domain stubs.
3. Keep all live_tested false without token; later UI discovery may use only a
   headless, read-only session.

## Design / wiki

- Design: `docs/superpowers/specs/2026-07-28-billy-mcp-complete-design.md`
- Wiki seed: `wiki/billy_api_v2_research_seed.md` (orientation only, not inventory)
