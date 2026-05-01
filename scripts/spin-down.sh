#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"

echo "==> Terraform destroy"
cd "$REPO_ROOT/infra/terraform"
terraform init
terraform plan -destroy
terraform destroy -auto-approve

echo "==> Infrastructure destroyed"
