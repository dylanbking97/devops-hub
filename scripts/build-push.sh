#!/usr/bin/env bash
set -euo pipefail

PROJECT_ID="project-385a0cab-c44a-4b07-926"
AR_REPO="us-east1-docker.pkg.dev/${PROJECT_ID}/devops-hub"
REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"

# Tag with git short SHA so argocd-image-updater can detect new builds.
# Working tree must be clean to avoid tagging a build that doesn't match a commit.
cd "$REPO_ROOT"
if ! git diff --quiet HEAD -- backend frontend; then
  echo "ERROR: backend/ or frontend/ has uncommitted changes." >&2
  echo "Commit first so the SHA tag matches what's in the registry." >&2
  exit 1
fi
SHA="$(git rev-parse --short HEAD)"

TARGETS=("$@")
if [ ${#TARGETS[@]} -eq 0 ]; then
  TARGETS=(backend frontend)
fi

echo "==> Configuring docker auth"
gcloud auth configure-docker us-east1-docker.pkg.dev --quiet

for target in "${TARGETS[@]}"; do
  case "$target" in
    backend|frontend) ;;
    *) echo "Unknown target: $target (expected: backend, frontend)" >&2; exit 1 ;;
  esac
  echo "==> Building $target ($SHA)"
  docker build --platform linux/amd64 \
    -t "$AR_REPO/$target:$SHA" \
    "$REPO_ROOT/$target"
  echo "==> Pushing $target:$SHA"
  docker push "$AR_REPO/$target:$SHA"
done

echo "==> Done."
echo "    Image tag: $SHA"
echo "    argocd-image-updater will detect this and open a write-back commit."
