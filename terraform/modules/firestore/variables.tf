variable "project_id" {
  description = "GCP project the database is created in."
  type        = string
}

variable "location" {
  description = "Location of the database, e.g. europe-west1. Cannot be changed after creation."
  type        = string
}

variable "database_name" {
  description = "Base ID of the Firestore database; the env suffix is appended to it. \"(default)\" (only with an empty env) is the project's default database, which is the one eligible for the free tier."
  type        = string
}

variable "env" {
  description = "Environment suffix appended to the database name, e.g. \"-dev\". Empty for no suffix."
  type        = string
  default     = ""
}

variable "collections" {
  description = "Collections the application stores documents in. Firestore creates a collection on its first document write; this list only documents and exposes the names."
  type        = set(string)
  default     = []
}

variable "delete_protection" {
  description = "Block deleting the database (in Terraform and in the console)."
  type        = bool
  default     = true
}

variable "point_in_time_recovery" {
  description = "Keep 7 days of versions so the data can be restored to any minute in that window."
  type        = bool
  default     = false
}
