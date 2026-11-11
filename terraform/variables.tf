variable "project_id" {
  description = "GCP project that hosts Keychain (the same project as Firestore)."
  type        = string
}

variable "region" {
  description = "Region for regional resources, e.g. europe-west1."
  type        = string
}

variable "backend_repository_id" {
  description = "Artifact Registry repository that stores the keychain-backend image."
  type        = string
  default     = "keychain"
}

variable "keep_recent_versions" {
  description = "Number of most recent backend image versions the cleanup policy always keeps."
  type        = number
  default     = 10
}

variable "untagged_image_retention_days" {
  description = "Untagged images (e.g. replaced by a newer push of the same tag) are deleted after this many days."
  type        = number
  default     = 7
}
