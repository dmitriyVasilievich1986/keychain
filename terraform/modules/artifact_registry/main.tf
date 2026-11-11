resource "google_project_service" "artifact_registry" {
  project = var.project_id
  service = "artifactregistry.googleapis.com"

  # Keep the API enabled on `terraform destroy`; other tooling may use it.
  disable_on_destroy = false
}

# Docker repository.
# Image path: <location>-docker.pkg.dev/<project_id>/<repository_id>/<image_name>:<tag>
resource "google_artifact_registry_repository" "this" {
  project       = var.project_id
  repository_id = var.repository_id
  location      = var.location
  format        = "DOCKER"
  description   = var.description

  # Tags stay mutable (the default) so "latest" can be re-pointed to every new
  # release. No docker_config block: with immutable_tags = false the API omits
  # it, which would show up as a permanent diff in every plan.

  cleanup_policy_dry_run = false

  cleanup_policies {
    id     = "delete-untagged"
    action = "DELETE"
    condition {
      tag_state  = "UNTAGGED"
      older_than = "${var.untagged_image_retention_days * 24 * 60 * 60}s"
    }
  }

  # KEEP policies take precedence over DELETE policies.
  cleanup_policies {
    id     = "keep-recent-versions"
    action = "KEEP"
    most_recent_versions {
      package_name_prefixes = [var.image_name]
      keep_count            = var.keep_recent_versions
    }
  }

  depends_on = [google_project_service.artifact_registry]
}
