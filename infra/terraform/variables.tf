variable "project_id" {
  description = "GCP project ID"
  type        = string
}

variable "region" {
  description = "GCP region"
  type        = string
  default     = "us-central1"
}

variable "zone" {
  description = "GCP zone for zonal cluster (single zone = fewer nodes = cheaper)"
  type        = string
  default     = "us-central1-a"
}

variable "cluster_name" {
  description = "GKE cluster name"
  type        = string
  default     = "devops-hub"
}

variable "node_machine_type" {
  description = "GCE machine type for cluster nodes"
  type        = string
  default     = "e2-small"
}

variable "min_node_count" {
  description = "Minimum nodes per zone in the node pool"
  type        = number
  default     = 1
}

variable "max_node_count" {
  description = "Maximum nodes per zone in the node pool"
  type        = number
  default     = 3
}
