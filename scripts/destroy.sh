#!/usr/bin/env bash
# destroy.sh — Teardown the GitOps platform

set -euo pipefail

RED='\033[0;31m'
NC='\033[0m'

echo -e "${RED}WARNING: This will delete ALL ArgoCD applications and namespaces!${NC}"
read -p "Type 'yes' to confirm: " CONFIRM

if [ "$CONFIRM" != "yes" ]; then
  echo "Aborted."
  exit 0
fi

echo "Removing ArgoCD applications..."
kubectl delete applications --all -n argocd 2>/dev/null || true

echo "Removing ArgoCD..."
kubectl delete namespace argocd 2>/dev/null || true

echo "Removing workload namespaces..."
for ns in dev staging production monitoring; do
  kubectl delete namespace "$ns" 2>/dev/null || true
done

echo "Stopping Minikube..."
minikube stop

echo "✅ Teardown complete"
