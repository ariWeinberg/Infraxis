#!/usr/bin/env bash
set -Eeuo pipefail
repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_root"
python_bin="${PYTHON_BIN:-python}"
[[ -x .venv/bin/python && -z "${PYTHON_BIN:-}" ]] && python_bin=".venv/bin/python"
"$python_bin" -m ruff check .
"$python_bin" -m compileall -q apps/platform-api/app
