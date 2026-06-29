# Rollback Playbook

This playbook describes safe rollback paths for production incidents.

## 1. Trigger Conditions

Use rollback when one or more of the following occurs after deployment:

- Availability or readiness checks fail continuously.
- Critical user flows are broken in production.
- Security regression is detected in the deployed version.
- Error rate or latency exceeds SLO and does not recover.

## 2. Fastest Rollback Path (Container/Image)

1. Identify the last known good image tag from CI artifacts or release records.
2. Redeploy the previous image tag to the target environment.
3. Verify:
   - `GET /healthz` returns `200`.
   - `GET /readyz` returns `200`.
   - Key smoke tests and login flows pass.
4. Announce rollback completion and incident status.

## 3. GitHub Release Rollback Path

1. Go to Releases and identify the previous stable release tag (e.g., `v1.2.2`).
2. Check out or deploy assets from that release bundle.
3. If needed, create a hotfix branch from the stable tag:

```bash
git checkout v1.2.2
git checkout -b hotfix/incident-<date>
```

4. Apply targeted fix, run full CI locally and remotely, then publish patched tag.

## 4. Database Safety Guidance

- Always take a backup/snapshot before schema-affecting deployment.
- If rollback needs schema downgrade, use migration rollback scripts only after backup validation.
- Avoid destructive rollback steps without backup verification.

## 5. Post-Rollback Validation Checklist

- Application responds normally on core routes.
- Authentication and role-based access flows are healthy.
- Metrics endpoint `/metrics` is accessible as expected.
- Error logs and structured request logs show stable behavior.
- CI for rollback target branch/tag is green.

## 6. Communication Template

- Incident start time:
- Impact scope:
- Rolled back version:
- Current stable version:
- Next action owner:
- ETA for permanent fix:
