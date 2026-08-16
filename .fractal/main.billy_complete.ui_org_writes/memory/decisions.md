---
name: decisions
desc: Locked org-update write choices: phone-only allowlist, inert execute without a submit hook, live slot wait.
tags: [decisions]
created: 2026-08-16T14:34:39Z
updated: 2026-08-16T14:34:39Z
---

# decisions

Preview allowlist is company `phone` only. `name` and `registrationNo` stay
closed. Users, access tokens, subscription, VAT, payments, and owners are
rejected by `extra=forbid` before a ticket is issued.

Execute without a submit hook returns `VALIDATION_ERROR` and does not consume
the ticket. Root wires the register call with no hook, so production execute
cannot change company settings.

Live execute submit waits for parent radio `D5136C2E`. Contacts holds the slot.
The live test skips before execute. That is a recorded blocker, not an unsafe
skipped submit.
