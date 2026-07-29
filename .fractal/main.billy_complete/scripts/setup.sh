#!/usr/bin/env bash
set -euo pipefail

# Environment setup -- runs at the start of every iteration
# ---------------------------------------------------------
#
# Must be idempotent. Update this script instead of installing
# packages inline, so the environment stays reproducible across
# iterations. The loop activates the repo venv automatically.

command -v uv >/dev/null 2>&1 || {
    echo "uv is required but not installed" >&2
    exit 1
}

if [[ -f pyproject.toml ]]; then
    uv sync --python 3.12 --all-extras --dev

    if uv run python -c "import playwright" >/dev/null 2>&1; then
        uv run playwright install chromium
    fi
fi
