#!/usr/bin/env bash
set -euo pipefail

# Run the node's test suite; exit 0 on success, non-zero on failure
# -----------------------------------------------------------------

# This offline product slice must run the repository's non-live regression suite.
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd -P)"
NODE_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
WORKTREE_DIR="$(git -C "$(dirname "$NODE_DIR")" rev-parse --show-toplevel)"
cd "$WORKTREE_DIR"

uv run pytest -m "not live and not vision"
uv run python scripts/check_coverage.py --reject-false-completeness
uv run python scripts/check_repository_policy.py
