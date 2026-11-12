module "artifact_registry" {
  source = "./modules/artifact_registry"

  project_id                    = var.project_id
  location                      = var.region
  repository_id                 = var.backend_repository_id
  description                   = "Docker images for the Keychain backend."
  image_name                    = "keychain-backend"
  keep_recent_versions          = var.keep_recent_versions
  untagged_image_retention_days = var.untagged_image_retention_days
}

module "firestore" {
  source = "./modules/firestore"

  project_id    = var.project_id
  location      = var.region
  database_name = var.firestore_database_name
  env           = var.env
  collections   = ["password", "users"]
}
