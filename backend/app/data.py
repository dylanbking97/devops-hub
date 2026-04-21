TOPICS = [
    {
        "slug": "containerization",
        "title": "Containerization",
        "summary": "Package apps and their dependencies into portable, isolated containers using Docker.",
        "icon": "🐳",
        "content": """\
## What is Containerization?

Containerization packages your application code alongside its runtime dependencies into a self-contained unit called a **container**. Unlike VMs, containers share the host OS kernel — they're lightweight, start in seconds, and behave identically across dev, staging, and production.

## Key Concepts

**Dockerfile** — A recipe for building a container image. Each instruction (`RUN`, `COPY`, `ENV`) creates a cached layer. Change a late instruction and only that layer and everything after it rebuilds.

**Multi-stage builds** — Use multiple `FROM` statements in one Dockerfile. A `builder` stage installs compilers and build tools; the final stage copies only the compiled output. The result: no build toolchain in your production image.

**Container registries** — Remote storage for images (Docker Hub, GCR, GHCR). Your CI pipeline builds and pushes; your cluster pulls.

**docker-compose** — A local orchestrator that runs multi-container stacks from a single YAML file. Excellent for replicating your production service topology in development without needing a cluster.

## In This Project

Both services use multi-stage Dockerfiles:

- **Backend**: A `builder` stage installs Python packages with `pip install --user`. The `runtime` stage is a fresh `python:3.12-slim` image that copies only `/root/.local` from the builder — no pip, no gcc, no build tools in production.
- **Frontend**: A `builder` stage runs `npm ci && npm run build`. The `runtime` stage is an `nginx:alpine` image that serves the compiled `/dist` — Node.js never ends up in the final image.

`docker-compose.yaml` at the repo root runs backend, frontend, Redis, and **Traefik** together — the same routing topology used in the GKE cluster, just locally. Run `docker compose up --build` to get a fully functional stack at `http://localhost`.
""",
    },
    {
        "slug": "monitoring",
        "title": "Monitoring with Prometheus",
        "summary": "Instrument applications and collect time-series metrics for observability.",
        "icon": "📊",
        "content": """\
## What is Prometheus?

Prometheus is an open-source monitoring system that collects and stores time-series metrics. It uses a **pull model** — Prometheus periodically scrapes HTTP `/metrics` endpoints exposed by your services, rather than services pushing data to a central collector.

## Key Concepts

**Metric types** — Four types: `Counter` (monotonically increasing — request count, error count), `Gauge` (can go up/down — active connections, memory usage), `Histogram` (samples observations into configurable buckets — latency distributions), and `Summary`.

**PromQL** — Prometheus Query Language. Powers both dashboards and alerts. Example: `rate(http_requests_total[5m])` calculates per-second request rate over a 5-minute window.

**Exporters** — Libraries or sidecars that translate application state into Prometheus metrics format. `prometheus-fastapi-instrumentator` wraps FastAPI and auto-instruments every route with request counters and latency histograms.

**ServiceMonitor** — A Kubernetes CRD (from the Prometheus Operator) that declaratively tells Prometheus which services to scrape and how. Your scrape config lives in Git alongside your application manifests.

**kube-prometheus-stack** — The standard Helm chart for cluster monitoring. Bundles Prometheus, Alertmanager, Grafana, node exporters, and the Prometheus Operator in one deployment.

## In This Project

The FastAPI backend imports `prometheus-fastapi-instrumentator`, which adds a `/metrics` endpoint automatically exposing:
- `http_request_duration_seconds` — latency histogram per route and status code
- `http_requests_total` — request counter per route and status code

A `ServiceMonitor` in `infra/k8s/devops-hub/backend/` instructs the Prometheus Operator to scrape the backend's `/metrics` every 30 seconds. The `prometheus` ArgoCD Application installs kube-prometheus-stack via Helm.

After deploying, port-forward Grafana and query `rate(http_request_duration_seconds_count[5m])` to see live request rates for each API route.
""",
    },
    {
        "slug": "iac",
        "title": "Infrastructure as Code (Terraform)",
        "summary": "Provision and manage cloud infrastructure declaratively with Terraform.",
        "icon": "🏗️",
        "content": """\
## What is Infrastructure as Code?

IaC means defining infrastructure in version-controlled configuration files rather than through manual console clicks or imperative scripts. Terraform, by HashiCorp, uses a declarative language (HCL) — you describe *what* you want, Terraform figures out *how* to get there.

## Key Concepts

**Providers** — Plugins that give Terraform access to an API. The `google` provider lets you manage GCP resources; the `kubernetes` provider can manage cluster resources. Declared in `required_providers`.

**Resources** — The fundamental building block. Each `resource` block maps to a real infrastructure object: a `google_container_cluster`, a `google_compute_network`, a VPC subnet.

**State** — Terraform tracks the real-world state of your infrastructure in a state file. It diffs your config against state to determine what to create, update, or destroy. In teams, state is stored remotely (GCS, S3) to avoid conflicts.

**Plan / Apply** — `terraform plan` shows exactly what will change before touching anything. `terraform apply` executes it. Never skip the plan review.

**Modules** — Reusable, composable groups of resources with input variables and outputs. The official `terraform-google-modules` are battle-tested defaults for GCP.

## In This Project

`infra/terraform/` provisions everything needed to run the stack on GCP:

- A **custom VPC** with a subnet configured with secondary IP ranges (required for GKE VPC-native networking — pods and services get IPs directly from the VPC rather than using NAT)
- A **GKE Standard cluster** with Workload Identity enabled (lets pods authenticate to GCP APIs using K8s service accounts instead of static key files)
- A **managed node pool** with autoscaling (1–3 nodes, `e2-standard-2`)

After `terraform apply`, configure kubectl:
```
$(terraform output -raw kubeconfig_command)
```

The state backend is commented out by default — uncomment the `backend "gcs"` block and create a bucket to enable remote state for team use.
""",
    },
    {
        "slug": "gitops",
        "title": "GitOps with ArgoCD",
        "summary": "Use Git as the single source of truth for Kubernetes deployments.",
        "icon": "🔄",
        "content": """\
## What is GitOps?

GitOps is an operational model where the desired state of your cluster is fully described by files in a Git repository. An operator (ArgoCD) continuously compares the live cluster state against Git and reconciles any drift — automatically or on demand.

The key property: **Git is the only way to change production**. No manual `kubectl apply`. No ad-hoc patches. Every change is reviewed, audited, and reversible.

## Key Concepts

**Declarative** — Everything is YAML in Git. You never imperatively tell the cluster what to do; you describe what you want and ArgoCD makes it so.

**Reconciliation loop** — ArgoCD polls Git (or uses a webhook) every few minutes. If the live state diverges from Git — whether from a new commit or a manual cluster edit — ArgoCD detects it and marks the app `OutOfSync`.

**Self-heal** — With `selfHeal: true`, ArgoCD automatically reverts unauthorized manual changes to the cluster. Someone `kubectl edit`'d a deployment? Reverted within minutes.

**App of Apps** — A pattern where a root ArgoCD `Application` manages a directory of child `Application` manifests. Bootstrap the entire cluster by applying one file; ArgoCD provisions everything else.

**Sync policies** — `automated` sync applies Git changes automatically. `prune: true` deletes resources removed from Git. `ServerSideApply` (useful for large CRDs like kube-prometheus-stack) avoids annotation size limits.

## In This Project

`infra/k8s/apps/` implements the App-of-Apps pattern:

- `app-of-apps.yaml` — the root Application, applied once manually to bootstrap
- `devops-hub.yaml` — syncs backend, frontend, Redis, and IngressRoute
- `traefik.yaml` — installs Traefik via its official Helm chart
- `prometheus.yaml` — installs kube-prometheus-stack via Helm

Bootstrap sequence:
```
# 1. Install ArgoCD into the cluster
kubectl create namespace argocd
kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml

# 2. Update YOUR_USERNAME/YOUR_REPO in app-of-apps.yaml, then:
kubectl apply -f infra/k8s/apps/app-of-apps.yaml
```

From that point on, merging to `main` deploys to production.
""",
    },
]
