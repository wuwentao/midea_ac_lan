#!/usr/bin/env bash
#
# Run Home Assistant locally with this integration loaded, powered by uv.

set -e

cd "$(dirname "$0")/.."

# Create config dir if not present
if [[ ! -d "${PWD}/config" ]]; then
	mkdir -p "${PWD}/config"
	uv run hass --config "${PWD}/config" --script ensure_config
fi

# Set the path to custom_components
## This let's us have the structure we want <root>/custom_components/midea_ac_lan
## while at the same time have Home Assistant configuration inside <root>/config
## without resulting to symlinks.
export PYTHONPATH="${PYTHONPATH}:${PWD}/custom_components"

# Start Home Assistant
uv run hass --config "${PWD}/config" --debug
