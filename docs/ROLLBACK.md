# Rollback Guide — GitOps with ArgoCD

## Overview
One of the biggest advantages of GitOps: rollback is just a git revert. Everything is declarative and versioned.

---

## Option 1: Git Revert (Recommended — full audit trail)

```bash
# Find the bad commit
git log --oneline helm/microservices/values-prod.yaml

# Revert it
git revert <bad-commit-sha>
git push origin main

# ArgoCD auto-detects the change and rolls back within 3 minutes
```

---

## Option 2: ArgoCD CLI Rollback

```bash
# List revision history
argocd app history backend-prod

# Rollback to a specific revision
argocd app rollback backend-prod <revision-id>
```

---

## Option 3: ArgoCD UI Rollback

1. Open ArgoCD UI → Applications → `backend-prod`
2. Click **History and Rollback** (clock icon)
3. Select the healthy revision
4. Click **Rollback**

---

## Emergency: Force-sync to known good tag

```bash
# Override image tag to last known good
argocd app set backend-prod \
  --helm-set image.tag=sha-abc123good

argocd app sync backend-prod
```

---

## DORA Metric: MTTR Target
**Target MTTR: < 10 minutes** using this GitOps rollback approach.
