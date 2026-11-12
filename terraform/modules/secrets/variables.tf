variable "project_id" {
  description = "GCP project the secrets are created in."
  type        = string
}

variable "location" {
  description = "Region the secret payloads are stored in, e.g. europe-west1."
  type        = string
}

variable "secret_ids" {
  description = "IDs of the secrets to create. Terraform creates only the secrets; their values (versions) are added outside Terraform so they never land in the state."
  type        = set(string)
}
