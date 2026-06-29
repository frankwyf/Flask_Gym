# Verify Release Signatures (Cosign Keyless)

Release assets are signed in CI using Cosign keyless signing (OIDC).

Published release assets include:

- `flask-gym-<tag>.zip`
- `flask-gym-<tag>.tar.gz`
- `flask-gym-<tag>.sha256`
- `flask-gym-<tag>.zip.sig` and `flask-gym-<tag>.zip.pem`
- `flask-gym-<tag>.tar.gz.sig` and `flask-gym-<tag>.tar.gz.pem`

## 1. Validate checksums

```bash
sha256sum -c flask-gym-<tag>.sha256
```

Expected output: `OK` for both archive files.

## 2. Install Cosign

```bash
# Example on Linux/macOS
brew install cosign
```

Or see official docs: https://docs.sigstore.dev/cosign/installation/

## 3. Verify ZIP artifact signature

```bash
cosign verify-blob \
  --certificate flask-gym-<tag>.zip.pem \
  --signature flask-gym-<tag>.zip.sig \
  --certificate-identity-regexp "^https://github.com/.+" \
  --certificate-oidc-issuer "https://token.actions.githubusercontent.com" \
  flask-gym-<tag>.zip
```

## 4. Verify TAR.GZ artifact signature

```bash
cosign verify-blob \
  --certificate flask-gym-<tag>.tar.gz.pem \
  --signature flask-gym-<tag>.tar.gz.sig \
  --certificate-identity-regexp "^https://github.com/.+" \
  --certificate-oidc-issuer "https://token.actions.githubusercontent.com" \
  flask-gym-<tag>.tar.gz
```

## 5. Recommended policy checks

For stricter policy, constrain identity to this repository/workflow when verifying:

- Repository: `frankwyf/Flask_Gym`
- Workflow: `.github/workflows/release.yml`

Use exact identity constraints in environments that require provenance lock-down.
