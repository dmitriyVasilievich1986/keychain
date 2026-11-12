output "secret_ids" {
  description = "Created secret IDs, keyed by the requested ID."
  value       = { for id, secret in google_secret_manager_secret.this : id => secret.secret_id }
}
