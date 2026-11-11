terraform {
  required_version = ">= 1.6"

  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 7.0"
    }
  }

  # State is kept locally for now. Move it to a GCS bucket (backend "gcs")
  # once more infrastructure lives here or more than one person applies it.
}
