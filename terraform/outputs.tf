output "cloud_run_url" {
  description = "The publicly accessible HTTPS URL of the deployed Cloud Run customer support agent."
  value       = google_cloud_run_v2_service.agent_service.uri
}

output "artifact_registry_repo_url" {
  description = "Docker repository URI in Google Artifact Registry."
  value       = "${var.region}-docker.pkg.dev/${var.project_id}/${google_artifact_registry_repository.agent_repo.repository_id}"
}

output "service_account_email" {
  description = "The dedicated service account running the Cloud Run container."
  value       = google_service_account.agent_sa.email
}

output "secret_id" {
  description = "Secret Manager secret ID holding the GOOGLE_API_KEY."
  value       = google_secret_manager_secret.gemini_api_key.secret_id
}
