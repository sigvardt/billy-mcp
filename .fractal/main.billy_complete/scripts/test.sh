#!/usr/bin/env bash
set -euo pipefail

# Run the node's test suite; exit 0 on success, non-zero on failure
# -----------------------------------------------------------------

# No-op by default; extend per node with the project's test command.

WORKTREE_DIR="$(git rev-parse --show-toplevel)"
cd "$WORKTREE_DIR"

# A full qualification run must never treat an uninitialised project as green.
if [[ "${BILLY_TEST_MODE:-commit}" == "full" && ! -f pyproject.toml ]]; then
    echo "pyproject.toml does not exist; full qualification cannot run" >&2
    exit 1
fi

if [[ ! -f pyproject.toml ]]; then
    echo "pyproject.toml does not exist yet; no tests can run"
    exit 0
fi

TEST_MODE="${BILLY_TEST_MODE:-commit}"

case "$TEST_MODE" in
    commit)
        uv run pytest -m "not live and not vision"
        ;;
    full)
        uv run pytest

        if [[ -f scripts/check_coverage.py ]]; then
            uv run python scripts/check_coverage.py --require-complete
        fi

        if [[ -f scripts/check_repository_policy.py ]]; then
            uv run python scripts/check_repository_policy.py --release
        fi
        ;;
    *)
        echo "Unknown BILLY_TEST_MODE: $TEST_MODE" >&2
        exit 2
        ;;
esac
