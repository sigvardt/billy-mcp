#!/usr/bin/env bash
set -euo pipefail

# Run the node's test suite; exit 0 on success, non-zero on failure
# -----------------------------------------------------------------

# No-op by default; extend per node with the project's test command.

uv run pytest -q \
    tests/api/test_bank_line_writes.py \
    tests/api/test_bank_line_cross_executor.py \
    tests/unit/test_coverage_server.py \
    tests/coverage/test_coverage_inventory.py
