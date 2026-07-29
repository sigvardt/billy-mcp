---
name: state
desc: Delivered coverage inventory state and durable validation facts.
created: 2026-07-29T09:22:14Z
updated: 2026-07-29T09:22:14Z
---

# state

The owned Phase 0 coverage slice is a deterministic red-only inventory. Its
canonical data builder is `scripts/generate_coverage_report.py`; checked-in
coverage artifacts are JSON documents with `.yaml` extensions, which is a valid
YAML subset and avoids adding a parser dependency.

The API freeze contains exactly 207 clear operations, 92 `ambiguous_bulk`
mentions, and six special routes. The UI manifest maps every API row to a red
parity-discovery row and keeps `vision_verified: false` with no evidence data.
The browser policy denies by default, allows only the documented UI/auth and
future typed-download hosts, reserves the official API host for the API client,
and denies its alias.

The duplicate evidence for `POST /v2/files` is intentionally represented by a
clear Supports `api.files.create` row that aliases
`api.special.files_upload`. Both rows preserve the documented multipart request
headers, but only the special row plans `api_files_upload_preview`; no JSON
`api_files_create` tool may be introduced.

`scripts/check_coverage.py` rejects schema omissions, stale generated output,
false green completeness, green bulk rows, unsupported domain-tool
registrations, and raw browser-evidence paths. Normal validation accepts a
coherent red inventory. `--reject-false-completeness` is the root lint mode;
`--require-complete` additionally requires every API state, every UI vision
state, and no unresolved bulk row. All implementation, contract-test,
live-test, and UI vision states remain false because no API token or UI
qualification evidence is available.

The generated completeness flag is derived from the row evidence, not from a
permanent Phase 0 constant. The `bankLineMatches` response and write root key
is `bankLineMatch`; the generator and API/UI manifests must never emit the
incorrect `bankLineMatche` singularization.
