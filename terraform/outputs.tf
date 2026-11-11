output "backend_repository_url" {
  description = "Registry path to push to and pull from, without the image name."
  value       = module.artifact_registry.repository_url
}

output "backend_image" {
  description = "Full keychain-backend image name (append :<tag>)."
  value       = module.artifact_registry.image
}
