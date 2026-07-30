#!/usr/bin/env bash
set -euo pipefail

# Run the node's test suite; exit 0 on success, non-zero on failure
# -----------------------------------------------------------------

# No-op by default; extend per node with the project's test command.

WORKTREE_DIR="$(git rev-parse --show-toplevel)"
cd "$WORKTREE_DIR"
uv run pytest tests/api/test_organization_writes.py tests/coverage/test_coverage_inventory.py tests/unit/test_coverage_server.py
uv run python scripts/check_coverage.py --reject-false-completeness
uv run python scripts/check_repository_policy.py
