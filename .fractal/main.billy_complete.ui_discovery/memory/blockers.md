---
name: blockers
desc: Open blockers that stop authenticated UI discovery.
created: 2026-07-29T09:37:34Z
updated: 2026-07-29T09:37:34Z
---

# blockers

- **Credentials absent.** Login form visible on `mit.billy.dk/login`; no UI
  credentials in environment; default keyring token absent. Do not invent a
  password path. Stop without submit.
- Authenticated product routes remain unobserved until credentials or a live
  session exist outside git.
- MFA, CAPTCHA, passkey, and push were not observed on the login screen; shape
  after password submit is unverified.
