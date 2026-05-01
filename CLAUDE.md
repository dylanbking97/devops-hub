# DevOps Learning Hub

## Stack Overview
- **Frontend**: React (Vite) served by nginx
- **Backend**: Python FastAPI with uvicorn
- **Session Store**: Redis (cookie-based anonymous sessions, 24h TTL)
- **Tracing**: OpenTelemetry → otel-collector → Jaeger
- **Metrics**: Prometheus (kube-prometheus-stack) + Grafana
- **Ingress**: Traefik with Gateway API (HTTPRoute), previously used IngressRoute CRD
- **GitOps**: ArgoCD with App of Apps pattern
- **Infrastructure**: Terraform → GKE (zonal cluster, us-central1-a, e2-standard-2, spot VMs)
- **Container Registry**: GCP Artifact Registry (us-east1)

## GCP Project
- Project ID: `project-385a0cab-c44a-4b07-926`
- GKE cluster: `devops-hub` in zone `us-central1-a`
- Artifact Registry: `us-east1-docker.pkg.dev/project-385a0cab-c44a-4b07-926/devops-hub`
- GitHub repo: `dylanbking97/devops-hub` (public, branch: `main`)

## Key Architecture Decisions
- Images must be built with `--platform linux/amd64` for GKE (dev machine is ARM Mac)
- Terraform state is local (single developer)
- ArgoCD app-of-apps bootstraps: gateway-api CRDs (wave -1) → traefik (wave 0) → devops-hub (wave 1)
- devops-hub ArgoCD app uses `directory.recurse: true` to find manifests in subdirectories
- devops-hub ArgoCD app has `SkipDryRunOnMissingResource=true` and retry policy for CRD ordering
- Gateway API namespace policy set to `All` so HTTPRoutes in devops-hub/monitoring can reference traefik-gateway
- Grafana served at `/grafana` subpath (configured via grafana.ini serve_from_sub_path)
- Jaeger served at `/jaeger` subpath (QUERY_BASE_PATH env var)
- argocd-server runs in insecure mode (`server.insecure: "true"` in `argocd-cmd-params-cm`) — TLS terminates at Traefik upstream

## Scripts
- `./scripts/spin-up.sh` — creates cluster, installs ArgoCD, bootstraps apps (does NOT build images; assumes they exist in Artifact Registry)
- `./scripts/spin-down.sh` — terraform destroy
- `./scripts/build-push.sh [backend|frontend]` — build and push image(s) to Artifact Registry. Separate lifecycle from spin-up/down (which is purely cost-driven cluster on/off)

## Known Issues
- ArgoCD application controller can get stuck and not auto-sync; has required `kubectl rollout restart statefulset argocd-application-controller` to unstick
- ArgoCD install requires `--server-side --force-conflicts` due to CRD annotation size limits
- setuptools must be <82 in backend requirements.txt (pkg_resources removed in 82+)
- ArgoCD UI port-forward: use `kubectl port-forward svc/argocd-server -n argocd 8080:80` (HTTP, not HTTPS, since server runs insecure). Firefox blocks `http://localhost:8080` even in private mode (likely HTTPS-Only / HSTS) — Safari works

## Build Notes
- No venv in backend Dockerfile (was causing pkg_resources issues with multi-stage copy)
- Frontend Dockerfile: node builder stage → nginx runtime stage
