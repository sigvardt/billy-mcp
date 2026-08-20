# Phase 1 offline API read-and-write coverage status

This generated inventory is currently incomplete. It freezes the official-doc snapshot with row-level implementation and contract-test evidence. Implemented/contract rows: 545/550; UI live/vision rows: 339/339. API live_tested remains false under out_of_scope_by_user (not live-verified).

| Source | Count |
| --- | ---: |
| Clear API operations | 207 |
| Ambiguous bulk mentions | 92 |
| Documented special routes | 6 |
| API snapshot total | 305 |
| UI discovery seeds | 40 |
| UI API-parity mappings | 305 |

Complete: `false`

Blocker: External-contract bulk freeze BULK_SCHEMA_UNSPECIFIED_OFFICIAL_DOCS: 92 ambiguous_bulk rows stay red after official docs/asset exhaust (research137); no bulk tools; API live_tested stays false (out_of_scope_by_user); UI annual_reports out_of_scope_by_user (owner radio:DC3B8E96); product-plane UI bulk honesty closed via dual-NA strong+soft+empty-list freezes
