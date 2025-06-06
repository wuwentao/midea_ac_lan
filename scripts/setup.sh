#!/usr/bin/env bash

set -e

cd "$(dirname "$0")/.."

# Install pre-commit hooks on commit
pre-commit install
pre-commit install --hook-type commit-msg

npm install @commitlint/config-conventional

# Create config dir if not present
if [[ ! -d "${PWD}/config" ]]; then
	mkdir -p "${PWD}/config"
	hass --config "${PWD}/config" --script ensure_config
fi
