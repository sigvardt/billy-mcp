---
name: evidence
title: evidence
desc: Independently rechecked primary and repo evidence for Wave-5p freeze ACCEPT.
created: 2026-07-30T11:54:25Z
updated: 2026-07-30T11:54:25Z
---

# evidence

## Primary

- Docs https://www.billy.dk/api/ : HTTP 200, ETag `wcw4x9hqvu3603`, 147934 bytes,
  MD5 `8b94b0135c91fd15fe54ea33e088a4be`
- `/v2/organizations` Supports: get by id, list, create, update, bulk save,
  bulk delete (no singular delete)
- Unauth base `https://api.billysbilling.com/v2`, body `{}` where applicable:
  - POST `/organizations` → 401 `AUTHENTICATION_REQUIRED`
  - PUT `/organizations/:id` → 401 `AUTHENTICATION_REQUIRED`
  - DELETE `/organizations/:id` → 405 `METHOD_NOT_ALLOWED` (no singular delete)
  - bulk DELETE with ids query → 405 (supplemental; bulk already excluded)

## Repository at `afbe5188`

- Freeze MD5 `2742eda7bafecd619aba5fa8ad0694c5`
- Coverage: implemented/contract-tested 175; live 0; vision 0; bulk 92;
  complete false
- Organizations create/update inventory red; preview tool names reserved;
  bulk empty-tool ambiguous_bulk
- Registry 256 `api_*` tools; only organizations get/list present
- Redaction keys include subscription card fields

## Verdict

ACCEPT freeze only. Product leaf separate. Unauth gates are not live
qualification.
