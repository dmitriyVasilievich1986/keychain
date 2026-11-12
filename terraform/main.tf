locals {
  firestore_collections = {
    passwords = "password"
    users     = "users"
  }

  # Secret Manager IDs of the backend secrets, keyed by the env variable that reads them.
  backend_secrets = {
    CRYPTOGRAPHY__SECRET_KEY = "keychain-cryptography-secret-key${var.env}"
    AUTH__JWT_SECRET_KEY     = "keychain-jwt-secret-key${var.env}"
  }
}

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
  collections   = values(local.firestore_collections)
}

module "github_actions" {
  source = "./modules/github_actions"

  project_id                      = var.project_id
  env                             = var.env
  github_repository               = var.github_repository
  artifact_registry_location      = var.region
  artifact_registry_repository_id = module.artifact_registry.repository_id
}

module "secrets" {
  source = "./modules/secrets"

  project_id = var.project_id
  location   = var.region
  secret_ids = values(local.backend_secrets)
}

module "cloud_run" {
  source = "./modules/cloud_run"

  project_id        = var.project_id
  location          = var.region
  env               = var.env
  service_name      = "keychain-backend"
  image             = "${module.artifact_registry.image}:${var.backend_image_tag}"
  health_check_path = "/keychain/health"
  min_instances     = var.backend_min_instances
  max_instances     = var.backend_max_instances

  # Overrides for backend/configurations/production.yaml (nested keys use "__").
  env_vars = {
    ENVIRONMENT                    = "production"
    GOOGLE__PROJECT_ID             = var.project_id
    DB__FIRESTORE__DB_NAME         = module.firestore.database_name
    DB__FIRESTORE__COLLECTION_NAME = local.firestore_collections.passwords
    DB__USERS__DB_NAME             = module.firestore.database_name
    DB__USERS__COLLECTION_NAME     = local.firestore_collections.users
  }

  secret_env_vars = {
    for name, id in local.backend_secrets : name => module.secrets.secret_ids[id]
  }

  # Read and write Firestore documents.
  project_roles = ["roles/datastore.user"]
}
