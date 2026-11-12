output "database_name" {
  description = "ID of the database (backend config: db.*.db_name)."
  value       = google_firestore_database.this.name
}

output "database_id" {
  description = "Full resource ID of the database."
  value       = google_firestore_database.this.id
}

output "collections" {
  description = "Collection names the application uses (backend config: db.*.collection_name)."
  value       = var.collections
}
