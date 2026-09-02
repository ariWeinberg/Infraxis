#!/usr/bin/env bash
set -Eeuo pipefail
repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_root"
python_bin="${PYTHON_BIN:-python}"
[[ -x .venv/bin/python && -z "${PYTHON_BIN:-}" ]] && python_bin=".venv/bin/python"
"$python_bin" -m compileall -q apps/platform-api/app
"$python_bin" -m pytest
"$python_bin" -m ruff check apps/platform-api
if command -v helm >/dev/null 2>&1; then
  helm lint deploy/helm/platform-api deploy/helm/console
  helm template cloudspace-api deploy/helm/platform-api >/dev/null
  helm template cloudspace-console deploy/helm/console >/dev/null
fi
if command -v opa >/dev/null 2>&1; then
  opa fmt --fail policies
  opa test policies
fi
git diff --check
