---
name: state
desc: Delivered safety-hardening state for the owned foundation slice.
created: 2026-07-29T09:48:55Z
updated: 2026-07-29T09:48:55Z
---

# state

Delivered C1/C2/S3 offline safety hardening: fixed-version API paths reject a
duplicate `/v2` prefix before request dispatch; organisation subscription-card
and payment fields are recursively redacted; upstream error text is never
returned; and browser egress policies load only from the typed, deny-by-default
manifest schema. Browser policy tests use local fixtures and fake runtime
dependencies only. No coverage artifacts or domain tools changed.
