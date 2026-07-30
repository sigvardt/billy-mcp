#!/usr/bin/env bash
set -euo pipefail

# Run the node's test suite; exit 0 on success, non-zero on failure
# -----------------------------------------------------------------

# No-op by default; extend per node with the project's test command.

if [[ "${BILLY_TEST_MODE:-}" == "commit" ]]; then
    uv run ruff format --check src tests scripts
    uv run ruff check src tests scripts
    uv run pyright
    uv run pytest \
        tests/api/test_contact_balance_payment_writes.py \
        tests/coverage/test_coverage_inventory.py \
        tests/unit/test_coverage_server.py
    uv run python scripts/generate_coverage_report.py --write
    uv run python scripts/check_coverage.py --reject-false-completeness
    uv run python scripts/check_repository_policy.py
fi
