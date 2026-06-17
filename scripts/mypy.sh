#!/usr/bin/env bash

set -e

cd "$(dirname "$0")/.."

echo "========== MY CUSTOM MYPY.SH =========="
which mypy
mypyver=$(mypy --version)
pwd
pyver=$(python -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
echo "Running mypy with target Python ${pyver}"
echo "Mypy version: ${mypyver}"

export MYPY_CACHE_DIR=/tmp/mypy

mypy \
    --show-traceback \
    --no-incremental \
    --python-version "${pyver}" \
    --cache-dir "/tmp/mypy" \
    --config-file mypy.ini \
    .