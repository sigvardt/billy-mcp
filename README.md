# Billy MCP

A FastMCP stdio server project targeting verified full coverage of Billy's official API and web interface.

The server will contain two explicit tool lanes:

- `api_*` for every supported operation in Billy's official API
- `ui_*` for full interface parity with the API where Billy exposes the capability, followed by every additional UI-only workflow

Authentication, organisation selection, autonomous write confirmation, coverage reporting, and testing are shared across both lanes.

Implementation has not started. Completeness will not be claimed until every applicable coverage row is implemented and tested.

Writes use a separate preview and execute call with a short-lived, exact-operation ticket. There is no caller-supplied confirmation boolean, no mandatory human approval, and no stub tool.

All browser automation is headless and never manipulates desktop windows. Every UI feature requires end-to-end headless testing, independent read-back, and agent-vision verification before its coverage row can become green.

The [approved design](docs/superpowers/specs/2026-07-28-billy-mcp-complete-design.md) is the normative project contract.
