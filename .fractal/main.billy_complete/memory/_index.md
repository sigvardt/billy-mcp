---
name: memory
desc: Node private working state for billy_complete.
tags: []
sources: []
created: 2026-07-29T07:56:19Z
updated: 2026-07-29T09:12:00Z
---

# memory

***

## Status

- Independent review: **FAIL**. Report: `.fractal/main.billy_complete/tmp/grok-review.md`.
- Research brief stands: `.fractal/main.billy_complete/tmp/grok-research.md`.
- Phase 0 package baseline: `pyproject.toml`, `uv.lock`,
  `src/billy_mcp/models.py`, `tests/test_models.py`, repository-policy scan,
  CI workflow, and wiki contract pages.
- Missing on the root branch: entire `coverage/`, `server.py` and foundation
  modules, and all domain tools. Their absence is red/incomplete, not a stub.
- Broken entrypoint: `billy-mcp` → `billy_mcp.server:main` but no `server.py`.
- `BILLY_TEST_MODE=full` now fails closed until `scripts/check_coverage.py`
  and generated `coverage/status.json` exist; qualification stays unavailable.
- Active Codex Power children: `coverage_inventory` owns red manifests,
  generated status/report, and coverage tests; `shared_foundation` owns the
  FastMCP safety foundation and unit tests. Their product work has not merged.

## Contract fingerprint (current)

- Primary: https://www.billy.dk/api/
- etag `hsisik4g9p3603`; body 147934 bytes; MD5 `c2efda0ee4cf9cf200e14910c5fc6996` (unchanged)
- 46 resources; 207 clear G/L/C/U/D; 92 bulk ambiguous; 6 specials; 0 webhooks
- Live 401s: `AUTHENTICATION_REQUIRED`, `OAUTH_INVALID_ACCESS_TOKEN`
- No false greens: there are not yet coverage rows on the root branch.

## Operator facts

- `BILLY_API_TOKEN`: unavailable
- Headless profile path (research): `/Users/user/.local/share/billy-mcp/chrome-profile`
- Playwright is a declared dependency; runtime module not present

## Blockers for completeness

1. Freeze red inventories + `status.json` complete:false
2. Merge the shared FastMCP foundation; fix entrypoint; coverage_* only; no stubs
3. Token + live/UI/vision work remains blocked until credentials and foundation land

## Design / wiki

- Design: `docs/superpowers/specs/2026-07-28-billy-mcp-complete-design.md`
- Wiki: `wiki/billy_api_v2_research_seed.md`, `wiki/phase_zero_contract.md`
