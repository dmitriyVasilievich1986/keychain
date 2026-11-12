locals {
  pool_id            = "github${var.env}"
  service_account_id = "github-actions${var.env}"
}

resource "google_project_service" "this" {
  for_each = toset([
    "iam.googleapis.com",            # service accounts, workload identity pools
    "iamcredentials.googleapis.com", # short-lived service account tokens
    "sts.googleapis.com",            # exchanges the GitHub OIDC token for a Google token
  ])

  project = var.project_id
  service = each.value

  disable_on_destroy = false
}

# Workload Identity Federation: GitHub Actions signs in with its OIDC token,
# so no service account key is stored in GitHub.
# Note: a deleted pool stays reserved for 30 days; its ID cannot be reused
# in that time.
resource "google_iam_workload_identity_pool" "github" {
  project                   = var.project_id
  workload_identity_pool_id = local.pool_id
  display_name              = "GitHub Actions"
  description               = "Identities from GitHub Actions workflows."

  depends_on = [google_project_service.this]
}

resource "google_iam_workload_identity_pool_provider" "github" {
  project                            = var.project_id
  workload_identity_pool_id          = google_iam_workload_identity_pool.github.workload_identity_pool_id
  workload_identity_pool_provider_id = "github-oidc"
  display_name                       = "GitHub OIDC"

  attribute_mapping = {
    "google.subject"       = "assertion.sub"
    "attribute.repository" = "assertion.repository"
    "attribute.ref"        = "assertion.ref"
  }

  # Only tokens issued to this repository are accepted at all.
  attribute_condition = "assertion.repository == \"${var.github_repository}\""

  oidc {
    issuer_uri = "https://token.actions.githubusercontent.com"
  }
}

resource "google_service_account" "github_actions" {
  project      = var.project_id
  account_id   = local.service_account_id
  display_name = "GitHub Actions"
  description  = "Used by ${var.github_repository} workflows to push images."

  depends_on = [google_project_service.this]
}

# Workflows of the repository may act as the service account.
resource "google_service_account_iam_member" "workload_identity_user" {
  service_account_id = google_service_account.github_actions.name
  role               = "roles/iam.workloadIdentityUser"
  member             = "principalSet://iam.googleapis.com/${google_iam_workload_identity_pool.github.name}/attribute.repository/${var.github_repository}"
}

# Push (and re-tag) images in the one repository only, not project-wide.
resource "google_artifact_registry_repository_iam_member" "writer" {
  project    = var.project_id
  location   = var.artifact_registry_location
  repository = var.artifact_registry_repository_id
  role       = "roles/artifactregistry.writer"
  member     = "serviceAccount:${google_service_account.github_actions.email}"
}
