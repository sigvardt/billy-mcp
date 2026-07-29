---
name: environment
desc: Auth and browser environment facts for UI discovery.
created: 2026-07-29T09:37:34Z
updated: 2026-07-29T09:37:34Z
---

# environment

- Browser profile: default MCP path under user local share (`chrome-profile`);
  directory present; prior host storage for `mit.billy.dk` seen, session still
  unauthenticated at load.
- Egress for this pass: exact host `mit.billy.dk` only via
  `BrowserEgressPolicy`.
- Process env: `BILLY_API_TOKEN` and UI email/password/TOTP names absent.
- Keyring service `billy-mcp` account `default`: absent.
- Runtime module used: `src/billy_mcp/browser.py` (`BrowserRuntime`).
- Scratch: node `tmp/` only; screenshot purged after classification.
