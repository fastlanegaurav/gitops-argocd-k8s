#!/usr/bin/env bash
# port-forward.sh — Local access to ArgoCD and monitoring

set -euo pipefail

echo "Starting port-forwards (Ctrl+C to stop all)..."

kubectl port-forward svc/argocd-server -n argocd 8080:443 &
PF_ARGOCD=$!

kubectl port-forward svc/grafana -n monitoring 3000:3000 &
PF_GRAFANA=$!

echo ""
echo "ArgoCD UI  → http://localhost:8080"
echo "Grafana    → http://localhost:3000 (admin/admin)"
echo ""
echo "Press Ctrl+C to stop all port-forwards"

trap "kill $PF_ARGOCD $PF_GRAFANA 2>/dev/null; echo 'Port-forwards stopped.'" EXIT
wait
