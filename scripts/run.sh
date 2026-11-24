#!/usr/bin/env bash
#
# Run Home Assistant locally with this integration loaded, powered by uv.

set -e

cd "$(dirname "$0")/.."

# Install runtime requirements from manifest.json after uv has synchronized the
# development environment. Keep later uv commands from syncing them away.
uv run --group run python scripts/install_manifest_requirements.py

# Create config dir if not present
if [[ ! -d "${PWD}/config" ]]; then
	mkdir -p "${PWD}/config"
	uv run --no-sync --group run hass --config "${PWD}/config" --script ensure_config
fi

# Set the path to custom_components
## This let's us have the structure we want <root>/custom_components/midea_ac_lan
## while at the same time have Home Assistant configuration inside <root>/config
## without resulting to symlinks.
export PYTHONPATH="${PYTHONPATH}:${PWD}/custom_components"

# Start Home Assistant
# `--group run` pulls in the optional runtime extras (colorlog, numpy, mutagen)
# declared in pyproject.toml; setup.sh and CI intentionally skip them.
uv run --no-sync --group run hass --config "${PWD}/config" --debug
