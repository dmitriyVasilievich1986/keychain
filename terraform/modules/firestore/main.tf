locals {
  database_name = "${var.database_name}${var.env}"
}

resource "google_project_service" "firestore" {
  project = var.project_id
  service = "firestore.googleapis.com"

  # Keep the API enabled on `terraform destroy`; other databases use it.
  disable_on_destroy = false
}

resource "google_firestore_database" "this" {
  project     = var.project_id
  name        = local.database_name
  location_id = var.location
  type        = "FIRESTORE_NATIVE"

  concurrency_mode                  = "PESSIMISTIC"
  app_engine_integration_mode       = "DISABLED"
  point_in_time_recovery_enablement = var.point_in_time_recovery ? "POINT_IN_TIME_RECOVERY_ENABLED" : "POINT_IN_TIME_RECOVERY_DISABLED"
  delete_protection_state           = var.delete_protection ? "DELETE_PROTECTION_ENABLED" : "DELETE_PROTECTION_DISABLED"

  deletion_policy = "DELETE"

  depends_on = [google_project_service.firestore]

  lifecycle {
    precondition {
      condition     = var.database_name != "(default)" || var.env == ""
      error_message = "The \"(default)\" database cannot take an env suffix. Set env to \"\" or use a named database_name, e.g. \"keychain\"."
    }
  }
}
