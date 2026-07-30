# Research68 — Wave-5p organizations product-ready

## Intent

Research-only pass after Wave-5o product and Wave-5p freeze page land on root.
Reconfirm Billy official API contract and unauth method gates, then package the
exact offline product-ready surface for Codex Power (four organizations
create/update tools), gated on independent freeze ACCEPT.

## Sources

- https://www.billy.dk/api/ (ETag `wcw4x9hqvu3603`, MD5 `8b94b0135c91fd15fe54ea33e088a4be`, 147934 bytes)
- https://api.billysbilling.com/v2 unauth probes (orgs POST/PUT 401; DELETE 405)
- `wiki/wave_fivep_ticketed_writes_contract.md` (on root; freeze ACCEPT pending)
- `wiki/wave_fivep_candidate_write_research.md`
- `coverage/api_v2_manifest.yaml`, `coverage/status.json` (175 offline green)
- Design: `docs/superpowers/specs/2026-07-28-billy-mcp-complete-design.md`

## Deliverable

`.fractal/main.billy_complete/tmp/grok-research.md` (research68)

## Result

- Official HTML **byte-identical** to research67; no contract change.
- Unauth gates unchanged: organizations create/update open at auth gate; singular delete closed.
- Freeze page on root (MD5 `2742eda7bafecd619aba5fa8ad0694c5`); freeze independent review still absent.
- Product tools still absent; create cleanup inventory wording still incorrectly assumes delete.
- No coverage greening; no product code; no live/UI work.

## Next implementation slice

1. Grok freeze independent review of `wiki/wave_fivep_ticketed_writes_contract.md`.
2. After freeze ACCEPT: Codex Power four tools
   `api_organizations_{create,update}_{preview,execute}` only; green two inventory
   rows after tests; leave bulk red; keep `complete: false`.

## Post-Mortem

- Completed: research68 reconfirmed the public API body, organizations POST/PUT
  authentication gates, DELETE-405 exclusion, and the exact future four-tool
  surface without changing product code or coverage.
- Independent review68 accepted this package as research and produced the
  durable project-wiki record
  `wiki/wave_fivep_product_ready_research_independent_review.md`.
- Verified: root formatting, Ruff, Pyright, coverage-policy, credential/safety,
  both wiki lints, and the 1,110-test non-live suite pass. No raw evidence,
  credentials, records, screenshots, HAR files, or traces were retained in the
  repository.
- No confirmed review defect required a fix. The organizations-create cleanup
  wording is knowingly wrong only on the currently red inventory row and must
  change through the generator when a later product has real contract evidence;
  changing it during research would be false qualification.
- Next unresolved slice: the separate organizations freeze review must record
  an authoritative ACCEPT before a Codex Power leaf may implement create/update;
  the independent Wave-5o product review remains a separate formal gate.
