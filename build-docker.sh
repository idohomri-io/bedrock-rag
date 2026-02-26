#!/usr/bin/env bash
set -euo pipefail

if [[ $# -lt 1 ]]; then
  echo "Usage: $0 <version> [--push=false]  (e.g. v1.2.0)"
  exit 1
fi

VERSION="$1"
PUSH=true

for arg in "${@:2}"; do
  case "$arg" in
    --push=false) PUSH=false ;;
    --push=true)  PUSH=true  ;;
    *) echo "Unknown argument: $arg"; exit 1 ;;
  esac
done

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO="ghcr.io/idohomri-io/bedrock-rag"

if $PUSH; then
  # Build for both amd64 (Linux servers) and arm64 (Apple Silicon, AWS Graviton).
  # buildx --push writes a multi-platform manifest directly to the registry;
  # Docker then auto-selects the right variant on each machine.
  docker buildx build \
    --platform linux/amd64,linux/arm64 \
    --push \
    --no-cache \
    -t "${REPO}:${VERSION}" \
    -t "${REPO}:latest" \
    "$SCRIPT_DIR"
  echo "Published ${REPO}:${VERSION} and ${REPO}:latest (amd64 + arm64)"
else
  # Local build for the current machine's native architecture only.
  # Uses plain docker build so the image is loaded into the local daemon.
  docker build \
    --no-cache \
    -t "${REPO}:${VERSION}" \
    -t "${REPO}:latest" \
    "$SCRIPT_DIR"
  echo "Built locally: ${REPO}:${VERSION} and ${REPO}:latest (not pushed)"
fi
