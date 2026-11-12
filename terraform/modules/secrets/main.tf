resource "google_project_service" "secret_manager" {
  project = var.project_id
  service = "secretmanager.googleapis.com"

  disable_on_destroy = false
}

# Secret containers only. Add a value with:
#   printf '%s' "<value>" | gcloud secrets versions add <secret_id> --data-file=-
resource "google_secret_manager_secret" "this" {
  for_each = var.secret_ids

  project   = var.project_id
  secret_id = each.value

  replication {
    user_managed {
      replicas {
        location = var.location
      }
    }
  }

  depends_on = [google_project_service.secret_manager]
}
