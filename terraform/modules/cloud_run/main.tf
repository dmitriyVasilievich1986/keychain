locals {
  name = "${var.service_name}${var.env}"
}

resource "google_project_service" "run" {
  project = var.project_id
  service = "run.googleapis.com"

  disable_on_destroy = false
}

# Identity the container runs as. The backend uses it through Application
# Default Credentials, so no key file is needed.
resource "google_service_account" "runtime" {
  project      = var.project_id
  account_id   = local.name
  display_name = "Cloud Run: ${local.name}"
}

resource "google_project_iam_member" "runtime" {
  for_each = var.project_roles

  project = var.project_id
  role    = each.value
  member  = "serviceAccount:${google_service_account.runtime.email}"
}

resource "google_secret_manager_secret_iam_member" "runtime" {
  for_each = var.secret_env_vars

  project   = var.project_id
  secret_id = each.value
  role      = "roles/secretmanager.secretAccessor"
  member    = "serviceAccount:${google_service_account.runtime.email}"
}

# New IAM grants take a while to reach Firestore and Secret Manager. Without
# this pause the first revision starts before its roles are effective, every
# health check gets "403 Missing or insufficient permissions", and the
# revision fails its startup probe.
resource "time_sleep" "iam_propagation" {
  create_duration = var.iam_propagation_delay

  triggers = {
    service_account = google_service_account.runtime.email
    project_roles   = join(",", sort(tolist(var.project_roles)))
    secrets         = join(",", sort(values(var.secret_env_vars)))
  }

  depends_on = [
    google_project_iam_member.runtime,
    google_secret_manager_secret_iam_member.runtime,
  ]
}

resource "google_cloud_run_v2_service" "this" {
  project  = var.project_id
  name     = local.name
  location = var.location
  ingress  = "INGRESS_TRAFFIC_ALL"

  # Stateless service: allow `terraform destroy` / replacement.
  deletion_protection = false

  template {
    service_account = google_service_account.runtime.email

    scaling {
      min_instance_count = var.min_instances
      max_instance_count = var.max_instances
    }

    containers {
      # A tag such as "latest" is resolved to a digest at deploy time; pushing
      # a new image under the same tag does not redeploy the service.
      image = var.image

      ports {
        container_port = var.container_port
      }

      resources {
        limits = {
          cpu    = var.cpu
          memory = var.memory
        }
        # Bill CPU only while handling requests.
        cpu_idle = true
      }

      dynamic "env" {
        for_each = var.env_vars
        content {
          name  = env.key
          value = env.value
        }
      }

      dynamic "env" {
        for_each = var.secret_env_vars
        content {
          name = env.key
          value_source {
            secret_key_ref {
              secret  = env.value
              version = "latest"
            }
          }
        }
      }

      startup_probe {
        http_get {
          path = var.health_check_path
          port = var.container_port
        }
        initial_delay_seconds = 0
        period_seconds        = 5
        timeout_seconds       = 3
        failure_threshold     = 12
      }

      liveness_probe {
        http_get {
          path = var.health_check_path
          port = var.container_port
        }
        period_seconds    = 60
        timeout_seconds   = 5
        failure_threshold = 3
      }
    }
  }

  lifecycle {
    # Set by gcloud / the console when deploying outside Terraform.
    ignore_changes = [client, client_version]
  }

  depends_on = [
    google_project_service.run,
    time_sleep.iam_propagation,
  ]
}

resource "google_cloud_run_v2_service_iam_member" "public" {
  count = var.allow_unauthenticated ? 1 : 0

  project  = var.project_id
  location = google_cloud_run_v2_service.this.location
  name     = google_cloud_run_v2_service.this.name
  role     = "roles/run.invoker"
  member   = "allUsers"
}
