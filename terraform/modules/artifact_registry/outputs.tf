output "repository_id" {
  description = "ID of the repository."
  value       = google_artifact_registry_repository.this.repository_id
}

output "repository_url" {
  description = "Registry path to push to and pull from, without the image name."
  value       = "${google_artifact_registry_repository.this.location}-docker.pkg.dev/${var.project_id}/${google_artifact_registry_repository.this.repository_id}"
}

output "image" {
  description = "Full image name (append :<tag>)."
  value       = "${google_artifact_registry_repository.this.location}-docker.pkg.dev/${var.project_id}/${google_artifact_registry_repository.this.repository_id}/${var.image_name}"
}
