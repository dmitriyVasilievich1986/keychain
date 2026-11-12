variable "project_id" {
  description = "GCP project the identity pool and service account are created in."
  type        = string
}

variable "env" {
  description = "Environment suffix appended to the pool and service account IDs, e.g. \"-dev\". Empty for no suffix."
  type        = string
  default     = ""
}

variable "github_repository" {
  description = "GitHub repository allowed to authenticate, as \"owner/name\" (case-sensitive, as GitHub reports it)."
  type        = string
}

variable "artifact_registry_location" {
  description = "Location of the Artifact Registry repository GitHub Actions pushes to."
  type        = string
}

variable "artifact_registry_repository_id" {
  description = "ID of the Artifact Registry repository GitHub Actions pushes to."
  type        = string
}
