#!/usr/bin/env bash

set -e

cd "$(dirname "$0")/.."

python3 -m pip install --requirement requirements.txt
python3 -m pip install --requirement requirements.dev.txt

# Install pre-commit hooks on commit
pre-commit install

# Create config dir if not present
if [[ ! -d "${PWD}/config" ]]; then
	mkdir -p "${PWD}/config"
	hass --config "${PWD}/config" --script ensure_config
fi
