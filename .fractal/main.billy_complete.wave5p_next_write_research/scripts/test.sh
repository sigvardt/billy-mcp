#!/usr/bin/env bash
set -euo pipefail

# Run the node's test suite; exit 0 on success, non-zero on failure
# -----------------------------------------------------------------

# Research changes only the project wiki; make the leaf's test gate real.
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd -P)"
NODE_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
WORKTREE_DIR="$(git -C "$(dirname "$NODE_DIR")" rev-parse --show-toplevel)"

wiki lint --path="$WORKTREE_DIR/wiki"
git -C "$WORKTREE_DIR" diff --check
