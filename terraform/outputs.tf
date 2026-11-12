output "backend_repository_url" {
  description = "Registry path to push to and pull from, without the image name."
  value       = module.artifact_registry.repository_url
}

output "backend_image" {
  description = "Full keychain-backend image name (append :<tag>)."
  value       = module.artifact_registry.image
}

output "firestore_database_name" {
  description = "Firestore database ID for the backend config (db.*.db_name)."
  value       = module.firestore.database_name
}

output "firestore_collections" {
  description = "Firestore collection names for the backend config (db.*.collection_name)."
  value       = module.firestore.collections
}

output "github_workload_identity_provider" {
  description = "GitHub repository variable GCP_WORKLOAD_IDENTITY_PROVIDER."
  value       = module.github_actions.workload_identity_provider
}

output "github_service_account" {
  description = "GitHub repository variable GCP_SERVICE_ACCOUNT."
  value       = module.github_actions.service_account_email
}
