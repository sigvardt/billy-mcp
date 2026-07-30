#!/usr/bin/env bash
set -euo pipefail

# Run the node's test suite; exit 0 on success, non-zero on failure
# -----------------------------------------------------------------

# No-op by default; extend per node with the project's test command.

WORKTREE_DIR="$(git rev-parse --show-toplevel)"
cd "$WORKTREE_DIR"

nice -n 15 uv run ruff format --check src tests scripts
nice -n 15 uv run ruff check src tests scripts
nice -n 15 uv run pyright
nice -n 15 uv run pytest \
    tests/api/test_contact_balance_payment_writes.py \
    tests/coverage/test_coverage_inventory.py \
    tests/unit/test_coverage_server.py
nice -n 15 uv run python scripts/check_coverage.py --reject-false-completeness
nice -n 15 uv run python scripts/check_repository_policy.py
wiki lint --path="$WORKTREE_DIR/wiki"
