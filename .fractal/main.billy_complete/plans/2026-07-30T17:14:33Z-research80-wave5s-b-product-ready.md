# Research80 — Wave-5s-B files upload product-ready

## Goal

Cite official-doc and code evidence for the next Codex Power product slice:
ticketed binary `api_files_upload_preview` / `api_files_upload_execute`, dual-row
green for `api.special.files_upload` + aliased `api.files.create`.

## Done

- Re-fetched https://www.billy.dk/api/ — MD5 `8b94b0135c91fd15fe54ea33e088a4be`, ETag `"wcw4x9hqvu3603"`, byte-identical to research79.
- Unauth probes on locked base reconfirmed binary POST **401**, JSON POST **401**, singular PUT/DELETE **405**.
- Mapped product gaps: JSON-only HTTP client, write protocol does not bind file identity, dual-row greening needs both evidence map entries.
- Wrote scratch `tmp/grok-research.md` (research80) and wiki `wave_fivesb_files_upload_product_ready_research.md`.
- Updated node memory `state.md`.

## Non-claims

No coverage greening, no product ACCEPT, no live/UI/vision work, no disposable records.
