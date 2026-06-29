#!/usr/bin/env bash
set -euo pipefail

if [ "$#" -ne 1 ]; then
  echo "Usage: $0 <release-tag>"
  exit 1
fi

RELEASE_TAG="$1"
REPO_OWNER="frankwyf"
REPO_NAME="Flask_Gym"
WORKFLOW_FILE="release.yml"
OIDC_ISSUER="https://token.actions.githubusercontent.com"

ZIP_FILE="flask-gym-${RELEASE_TAG}.zip"
TAR_FILE="flask-gym-${RELEASE_TAG}.tar.gz"
SUM_FILE="flask-gym-${RELEASE_TAG}.sha256"

for required in "$ZIP_FILE" "$TAR_FILE" "$SUM_FILE" \
  "${ZIP_FILE}.sig" "${ZIP_FILE}.pem" "${TAR_FILE}.sig" "${TAR_FILE}.pem"; do
  if [ ! -f "$required" ]; then
    echo "Missing required artifact: $required"
    exit 1
  fi
done

sha256sum -c "$SUM_FILE"

cosign verify-blob \
  --certificate "${ZIP_FILE}.pem" \
  --signature "${ZIP_FILE}.sig" \
  --certificate-identity-regexp "^https://github.com/${REPO_OWNER}/${REPO_NAME}/.github/workflows/${WORKFLOW_FILE}@refs/tags/${RELEASE_TAG}$" \
  --certificate-oidc-issuer "${OIDC_ISSUER}" \
  "$ZIP_FILE"

cosign verify-blob \
  --certificate "${TAR_FILE}.pem" \
  --signature "${TAR_FILE}.sig" \
  --certificate-identity-regexp "^https://github.com/${REPO_OWNER}/${REPO_NAME}/.github/workflows/${WORKFLOW_FILE}@refs/tags/${RELEASE_TAG}$" \
  --certificate-oidc-issuer "${OIDC_ISSUER}" \
  "$TAR_FILE"

echo "Release signature verification succeeded for tag ${RELEASE_TAG}."
