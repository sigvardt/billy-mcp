#!/usr/bin/env bash
set -euo pipefail

# Run the node's test suite; exit 0 on success, non-zero on failure
# -----------------------------------------------------------------

# The child owns only the fail-closed live-probe fixture pair.
uv run pytest tests/unit/test_live_probe.py
