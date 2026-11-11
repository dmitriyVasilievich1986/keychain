variable "project_id" {
  description = "GCP project the repository is created in."
  type        = string
}

variable "location" {
  description = "Region of the repository, e.g. europe-west1."
  type        = string
}

variable "repository_id" {
  description = "ID of the Artifact Registry repository."
  type        = string
}

variable "description" {
  description = "Human-readable description of the repository."
  type        = string
  default     = ""
}

variable "image_name" {
  description = "Image (package) name whose recent versions the cleanup policy keeps."
  type        = string
}

variable "keep_recent_versions" {
  description = "Number of most recent image versions the cleanup policy always keeps."
  type        = number
  default     = 10
}

variable "untagged_image_retention_days" {
  description = "Untagged images (e.g. replaced by a newer push of the same tag) are deleted after this many days."
  type        = number
  default     = 7
}
