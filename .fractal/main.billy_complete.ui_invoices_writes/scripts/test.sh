#!/usr/bin/env bash
set -euo pipefail

# Run the node's test suite; exit 0 on success, non-zero on failure
# -----------------------------------------------------------------

# No-op by default; extend per node with the project's test command.
ROOT="$(git rev-parse --show-toplevel)"
cd "$ROOT"
uv run pytest tests/unit/test_ui_invoices_writes.py -q
