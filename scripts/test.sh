#!/usr/bin/env bash
set -euo pipefail

WORKTREE_DIR="$(git rev-parse --show-toplevel)"
cd "$WORKTREE_DIR"

TEST_MODE="${BILLY_TEST_MODE:-commit}"

if [[ "$TEST_MODE" == "full" || "$TEST_MODE" == "ui-full" ]] \
    && [[ ! -f pyproject.toml ]]; then
    echo "pyproject.toml does not exist; full qualification cannot run" >&2
    exit 1
fi

if [[ "$TEST_MODE" == "full" || "$TEST_MODE" == "ui-full" ]] \
    && { [[ ! -f scripts/check_coverage.py ]] || [[ ! -f coverage/status.json ]]; }; then
    echo "coverage checker and generated status are required for full qualification" >&2
    exit 1
fi

if [[ ! -f pyproject.toml ]]; then
    echo "pyproject.toml does not exist yet; no tests can run"
    exit 0
fi

case "$TEST_MODE" in
    commit)
        uv run pytest -m "not live and not vision"
        ;;
    full)
        uv run pytest
        uv run python scripts/check_coverage.py --require-complete
        uv run python scripts/check_repository_policy.py --release
        ;;
    ui-full)
        # Offline API plus live UI and vision. Never live API traffic.
        uv run pytest -m "not live_api"
        uv run python scripts/check_coverage.py --require-complete
        uv run python scripts/check_repository_policy.py --release
        ;;
    *)
        echo "Unknown BILLY_TEST_MODE: $TEST_MODE" >&2
        exit 2
        ;;
esac
