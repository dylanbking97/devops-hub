#!/usr/bin/env bash
set -euo pipefail

PROJECT_ID="project-385a0cab-c44a-4b07-926"
ZONE="us-central1-a"
CLUSTER_NAME="devops-hub"
REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"

echo "==> Terraform apply"
cd "$REPO_ROOT/infra/terraform"
terraform init
terraform apply -auto-approve

echo "==> Getting GKE credentials"
gcloud container clusters get-credentials "$CLUSTER_NAME" --zone "$ZONE"

echo "==> Installing ArgoCD"
kubectl create namespace argocd --dry-run=client -o yaml | kubectl apply -f -
kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml --server-side --force-conflicts
echo "Waiting for ArgoCD server..."
kubectl wait --for=condition=available deployment/argocd-server -n argocd --timeout=120s

echo "==> Bootstrapping App of Apps"
kubectl apply -f "$REPO_ROOT/infra/k8s/apps/app-of-apps.yaml"

echo "==> Waiting for LoadBalancer IP..."
for i in $(seq 1 30); do
  IP=$(kubectl get svc traefik -n traefik -o jsonpath='{.status.loadBalancer.ingress[0].ip}' 2>/dev/null || true)
  if [ -n "$IP" ]; then
    echo "App available at http://$IP"
    exit 0
  fi
  sleep 10
done
echo "LoadBalancer IP not ready yet — check 'kubectl get svc -n traefik' later"
