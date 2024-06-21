#!/usr/bin/env bash

set -e

cd "$(dirname "$0")/.."

# Install pre-commit hooks on commit
pre-commit install

# Create config dir if not present
if [[ ! -d "${PWD}/config" ]]; then
	mkdir -p "${PWD}/config"
	hass --config "${PWD}/config" --script ensure_config
fi
