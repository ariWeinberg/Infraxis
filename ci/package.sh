#!/usr/bin/env bash
set -Eeuo pipefail
repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_root"
helm package deploy/helm/platform-api deploy/helm/console --destination "${ARTIFACT_DIR:-/tmp/cloudspace-artifacts}"
