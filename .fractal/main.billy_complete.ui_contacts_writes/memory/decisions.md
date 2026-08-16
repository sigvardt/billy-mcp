---
name: decisions
desc: Binding constraints for contacts UI preview and execute tools.
tags: [decisions]
sources: []
created: 2026-08-16T14:38:22Z
updated: 2026-08-16T14:38:22Z
---

# decisions

Preview calls `UiWriteProtocol.preview` only. Execute accepts only
`confirmation_ticket`, then `consume`, then the injected actor.

Locate customers by unique tagged name. Canonical requests:

- create: `{"action":"create","name":"..."}`
- update: `{"action":"update","name":"...","new_name":"..."}`
- delete: `{"action":"delete","name":"..."}`

Offline proof is FastMCP `call_tool` on a tiny server. BrowserRuntime is not
pass proof. The UI lane does not use `BillyHttpClient`.

Live proof needs both browser credential references, a second UI session list
read-back, four-state capture, frame purge, and delete cleanup. Missing
references are a recorded blocker, not an unsafe skip.

Do not edit the coverage generator, coverage checker, `server.py`, or
`browser.py`. Do not green `ui.parity.contacts.create|update|delete`.
