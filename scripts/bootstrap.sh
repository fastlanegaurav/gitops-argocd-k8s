#!/usr/bin/env bash
# ═══════════════════════════════════════════════════════════════════
# bootstrap.sh — One-command GitOps platform setup
# Author: Gaurav Kumar (github.com/fastlanegaurav)
# ═══════════════════════════════════════════════════════════════════

set -euo pipefail

GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

ARGOCD_NAMESPACE="argocd"
ARGOCD_VERSION="v2.10.0"

log()   { echo -e "${BLUE}[INFO]${NC} $1"; }
ok()    { echo -e "${GREEN}[OK]${NC}   $1"; }
warn()  { echo -e "${YELLOW}[WARN]${NC} $1"; }
error() { echo -e "${RED}[ERR]${NC}  $1"; exit 1; }

check_prerequisites() {
  log "Checking prerequisites..."
  for cmd in kubectl helm minikube; do
    if ! command -v "$cmd" &> /dev/null; then
      error "$cmd is not installed. Please install it first."
    fi
  done
  ok "All prerequisites found"
}

start_minikube() {
  if minikube status &> /dev/null; then
    warn "Minikube already running — skipping start"
  else
    log "Starting Minikube cluster (4 CPU, 8GB RAM)..."
    minikube start \
      --cpus=4 \
      --memory=8192 \
      --disk-size=30g \
      --driver=docker \
      --addons=ingress,metrics-server
    ok "Minikube started"
  fi
}

create_namespaces() {
  log "Creating namespaces..."
  kubectl apply -f kubernetes/namespaces/namespaces.yaml
  ok "Namespaces created: dev, staging, production, monitoring, argocd"
}

install_argocd() {
  log "Installing ArgoCD ${ARGOCD_VERSION}..."

  kubectl create namespace "${ARGOCD_NAMESPACE}" --dry-run=client -o yaml | kubectl apply -f -

  kubectl apply -n "${ARGOCD_NAMESPACE}" \
    -f "https://raw.githubusercontent.com/argoproj/argo-cd/${ARGOCD_VERSION}/manifests/install.yaml"

  log "Waiting for ArgoCD pods to be ready (this takes ~2 minutes)..."
  kubectl wait --for=condition=ready pod \
    -l app.kubernetes.io/name=argocd-server \
    -n "${ARGOCD_NAMESPACE}" \
    --timeout=300s

  ok "ArgoCD installed and ready"
}

configure_argocd() {
  log "Applying ArgoCD project and RBAC..."
  kubectl apply -f argocd/projects/gitops-project.yaml
  ok "ArgoCD AppProject configured"
}

bootstrap_app_of_apps() {
  log "Deploying Root App (App-of-Apps pattern)..."
  kubectl apply -f argocd/app-of-apps/root-app.yaml

  log "Waiting for root-app to sync..."
  sleep 15

  ok "Root App deployed — ArgoCD will now auto-deploy all child applications"
}

print_access_info() {
  ARGOCD_PASSWORD=$(kubectl -n argocd get secret argocd-initial-admin-secret \
    -o jsonpath="{.data.password}" | base64 -d)

  echo ""
  echo "═══════════════════════════════════════════════════════════════"
  echo -e "${GREEN}✅ GitOps Platform Ready!${NC}"
  echo "═══════════════════════════════════════════════════════════════"
  echo ""
  echo -e "${BLUE}ArgoCD UI:${NC}"
  echo "  Run: ./scripts/port-forward.sh"
  echo "  URL: http://localhost:8080"
  echo "  Username: admin"
  echo -e "  Password: ${YELLOW}${ARGOCD_PASSWORD}${NC}"
  echo ""
  echo -e "${BLUE}Apps being synced:${NC}"
  echo "  • frontend-dev    → namespace: dev"
  echo "  • backend-dev     → namespace: dev"
  echo "  • auth-service-dev → namespace: dev"
  echo "  • monitoring       → namespace: monitoring"
  echo ""
  echo -e "${BLUE}Watch sync status:${NC}"
  echo "  kubectl get applications -n argocd"
  echo "═══════════════════════════════════════════════════════════════"
}

main() {
  echo "═══════════════════════════════════════════════════════════════"
  echo "  GitOps with ArgoCD on Kubernetes — Bootstrap Script"
  echo "  Author: Gaurav Kumar (github.com/fastlanegaurav)"
  echo "═══════════════════════════════════════════════════════════════"
  echo ""

  check_prerequisites
  start_minikube
  create_namespaces
  install_argocd
  configure_argocd
  bootstrap_app_of_apps
  print_access_info
}

main "$@"
