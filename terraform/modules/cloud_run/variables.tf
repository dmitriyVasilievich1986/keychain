variable "project_id" {
  description = "GCP project the service runs in."
  type        = string
}

variable "location" {
  description = "Region of the service, e.g. europe-west1."
  type        = string
}

variable "env" {
  description = "Environment suffix appended to the service and service account names, e.g. \"-dev\". Empty for no suffix."
  type        = string
  default     = ""
}

variable "service_name" {
  description = "Base name of the Cloud Run service (and its runtime service account); env is appended to it."
  type        = string
}

variable "image" {
  description = "Container image to deploy, including the tag, e.g. <registry>/keychain-backend:latest."
  type        = string
}

variable "container_port" {
  description = "Port the container listens on."
  type        = number
  default     = 8080
}

variable "health_check_path" {
  description = "HTTP path for the startup and liveness probes."
  type        = string
}

variable "env_vars" {
  description = "Plain environment variables for the container."
  type        = map(string)
  default     = {}
}

variable "secret_env_vars" {
  description = "Environment variables read from Secret Manager: variable name => secret ID. The latest version of each secret is used."
  type        = map(string)
  default     = {}
}

variable "project_roles" {
  description = "Project-level IAM roles granted to the service's runtime service account."
  type        = set(string)
  default     = []
}

variable "cpu" {
  description = "CPU limit of the container."
  type        = string
  default     = "1"
}

variable "memory" {
  description = "Memory limit of the container."
  type        = string
  default     = "512Mi"
}

variable "min_instances" {
  description = "Minimum number of instances. 0 lets the service scale to zero when idle (cold starts, no idle cost)."
  type        = number
  default     = 0
}

variable "max_instances" {
  description = "Maximum number of instances."
  type        = number
  default     = 2
}

variable "allow_unauthenticated" {
  description = "Let anyone on the internet invoke the service (public API)."
  type        = bool
  default     = true
}

variable "iam_propagation_delay" {
  description = "How long to wait after granting the runtime service account its roles before deploying a revision."
  type        = string
  default     = "90s"
}
