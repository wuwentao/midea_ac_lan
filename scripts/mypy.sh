#!/usr/bin/env bash
#
# Run mypy through the uv-managed virtualenv.

set -e

cd "$(dirname "$0")/.."

pyver=$(uv run --no-sync python -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
echo "Running mypy with target Python ${pyver}"

export MYPY_CACHE_DIR=/tmp/mypy

uv run --no-sync mypy \
    --show-traceback \
    --no-incremental \
    --python-version "${pyver}" \
    --cache-dir "/tmp/mypy" \
    --config-file mypy.ini \
    .
