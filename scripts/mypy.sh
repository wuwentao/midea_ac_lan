#!/usr/bin/env bash

set -e

cd "$(dirname "$0")/.."

pyver=$(python3 -c 'import platform; major, minor, path = platform.python_version_tuple(); print(f"{major}.{minor}")')

mypy --config-file mypy-$pyver.ini .


