variable "env" {
  description = "Environment suffix appended to resource names, e.g. \"-dev\" or \"-prod\". Empty for no suffix."
  type        = string
  default     = ""

  validation {
    condition     = can(regex("^(-[a-z0-9]+)*$", var.env))
    error_message = "env must be empty or start with \"-\" followed by lowercase letters, digits and hyphens, e.g. \"-dev\"."
  }
}

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

variable "firestore_database_name" {
  description = "Base ID of the Firestore database the backend stores users and passwords in; env is appended to it. \"(default)\" gets the free tier but allows no env suffix."
  type        = string
  default     = "(default)"
}

variable "github_repository" {
  description = "GitHub repository whose workflows may push images, as \"owner/name\" (case-sensitive)."
  type        = string
  default     = "dmitriyVasilievich1986/keychain"
}
