# Phase 1 offline API read-and-write coverage status

This generated inventory is currently incomplete. It freezes the official-doc snapshot with row-level implementation and contract-test evidence. Implemented/contract rows: 350/350; UI live/vision rows: 166/166. API live_tested remains false under out_of_scope_by_user (not live-verified).

| Source | Count |
| --- | ---: |
| Clear API operations | 207 |
| Ambiguous bulk mentions | 92 |
| Documented special routes | 6 |
| API snapshot total | 305 |
| UI discovery seeds | 40 |
| UI API-parity mappings | 305 |

Complete: `false`

Blocker: External-contract bulk freeze BULK_SCHEMA_UNSPECIFIED_OFFICIAL_DOCS: 92 ambiguous_bulk rows stay red after official docs/asset exhaust (research137); no bulk tools; API live_tested stays false (out_of_scope_by_user); UI live and vision qualification incomplete (annual_reports org_inaccessible; residual UI parity open)
