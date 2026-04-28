terraform {
  required_version = ">= 1.7"

  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 6.0"
    }
  }

  backend "gcs" {
    bucket = "devops-hub-tfstate-385a0cab"
    prefix = "devops-hub/terraform"
  }
}

provider "google" {
  project = var.project_id
  region  = var.region
}

# Enable required GCP APIs
resource "google_project_service" "apis" {
  for_each = toset([
    "container.googleapis.com",
    "compute.googleapis.com",
  ])
  service            = each.value
  disable_on_destroy = false
}

# ── Networking ──────────────────────────────────────────────────────────────

resource "google_compute_network" "vpc" {
  name                    = "${var.cluster_name}-vpc"
  auto_create_subnetworks = false
  depends_on              = [google_project_service.apis]
}

# Subnet with secondary IP ranges for GKE VPC-native networking.
# VPC-native means pods and services get real VPC IPs — no double-NAT,
# better network policy support, and direct load balancer routing to pods.
resource "google_compute_subnetwork" "subnet" {
  name          = "${var.cluster_name}-subnet"
  ip_cidr_range = "10.0.0.0/20"
  region        = var.region
  network       = google_compute_network.vpc.id

  secondary_ip_range {
    range_name    = "pods"
    ip_cidr_range = "10.48.0.0/14"
  }

  secondary_ip_range {
    range_name    = "services"
    ip_cidr_range = "10.52.0.0/20"
  }
}

# ── GKE Cluster ─────────────────────────────────────────────────────────────

resource "google_container_cluster" "primary" {
  name     = var.cluster_name
  location = var.zone  # Zonal cluster — single zone, cheaper than regional

  # We manage the node pool separately via google_container_node_pool,
  # which gives us independent lifecycle control (resize without cluster recreation).
  remove_default_node_pool = true
  initial_node_count       = 1

  network    = google_compute_network.vpc.name
  subnetwork = google_compute_subnetwork.subnet.name

  ip_allocation_policy {
    cluster_secondary_range_name  = "pods"
    services_secondary_range_name = "services"
  }

  # Workload Identity lets pods authenticate to GCP APIs using K8s service accounts
  # instead of storing static key files in secrets. Best practice for GCP.
  workload_identity_config {
    workload_pool = "${var.project_id}.svc.id.goog"
  }

  deletion_protection = false

  depends_on = [google_project_service.apis]
}

# ── Node Pool ────────────────────────────────────────────────────────────────

resource "google_container_node_pool" "primary_nodes" {
  name     = "${var.cluster_name}-nodes"
  location = var.zone
  cluster  = google_container_cluster.primary.name

  autoscaling {
    min_node_count = var.min_node_count
    max_node_count = var.max_node_count
  }

  node_config {
    machine_type = var.node_machine_type
    disk_size_gb = 30
    disk_type    = "pd-standard"
    spot         = true

    # Required to activate Workload Identity on the nodes
    workload_metadata_config {
      mode = "GKE_METADATA"
    }

    oauth_scopes = [
      "https://www.googleapis.com/auth/cloud-platform",
    ]
  }
}
