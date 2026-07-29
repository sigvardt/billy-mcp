---
name: state
desc: Contacts read delivery state for this node.
created: 2026-07-29T10:09:53Z
updated: 2026-07-29T10:09:53Z
---

# state

The contacts read slice is implemented in `src/billy_mcp/api/contact_reads.py`
with focused coverage in `tests/api/test_contact_reads.py`. It provides typed
inputs and successes for `api_contacts_get` and `api_contacts_list`, maps only
the documented roots and paging, and leaves coverage/server integration to the
parent. Offline verification passes; no Billy credentials were used and
`live_tested` remains false.
