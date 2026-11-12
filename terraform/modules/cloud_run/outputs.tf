output "service_name" {
  description = "Name of the Cloud Run service."
  value       = google_cloud_run_v2_service.this.name
}

output "url" {
  description = "HTTPS URL of the service."
  value       = google_cloud_run_v2_service.this.uri
}

output "service_account_email" {
  description = "Runtime service account of the service."
  value       = google_service_account.runtime.email
}
