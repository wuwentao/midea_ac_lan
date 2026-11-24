#!/usr/bin/env bash
#
# One-time development environment setup, powered by uv.
# Prerequisite: install uv -> https://docs.astral.sh/uv/getting-started/installation/
#   macOS/Linux/WSL2: curl -LsSf https://astral.sh/uv/install.sh | sh
#   Windows:          powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

set -e

cd "$(dirname "$0")/.."

# Create the virtualenv (.venv) and install the development dependency group.
# uv automatically downloads the Python version pinned in .python-version if needed.
uv sync

# Runtime integration requirements are owned by manifest.json, not pyproject.toml.
uv run --no-sync python scripts/install_midea_lan.py

# Install the git hooks (pre-commit + commit-msg for Conventional Commits).
uv run --no-sync pre-commit install
uv run --no-sync pre-commit install --hook-type commit-msg

echo
echo "Setup complete. Run Home Assistant with: ./scripts/run.sh"
