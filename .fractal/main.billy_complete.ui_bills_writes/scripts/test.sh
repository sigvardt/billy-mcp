#!/usr/bin/env bash
set -euo pipefail

# Run the node's test suite; exit 0 on success, non-zero on failure
# -----------------------------------------------------------------

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd -P)"
NODE_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
WORKTREE_DIR="$(git -C "$(dirname "$NODE_DIR")" rev-parse --show-toplevel)"
cd "$WORKTREE_DIR"
uv run pytest tests/unit/test_ui_bills_writes.py tests/live/test_ui_bills_writes.py -q
