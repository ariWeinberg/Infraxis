#!/usr/bin/env bash
set -Eeuo pipefail
repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_root"
docker build --file apps/platform-api/Dockerfile --tag "${CLOUDSPACE_API_IMAGE:-cloudspace/platform-api:dev}" .
