# ==============================================================================
# Google Cloud APIs Enablement
# ==============================================================================
locals {
  gcp_services = [
    "run.googleapis.com",
    "artifactregistry.googleapis.com",
    "secretmanager.googleapis.com",
    "cloudbuild.googleapis.com",
    "iam.googleapis.com"
  ]

  # Default image URL if custom container_image is not provided
  default_image   = "${var.region}-docker.pkg.dev/${var.project_id}/${var.artifact_repo_name}/${var.service_name}:latest"
  effective_image = var.container_image != "" ? var.container_image : local.default_image
}

resource "google_project_service" "enabled_apis" {
  for_each           = toset(local.gcp_services)
  project            = var.project_id
  service            = each.key
  disable_on_destroy = false
}

# ==============================================================================
# Artifact Registry for Container Images
# ==============================================================================
resource "google_artifact_registry_repository" "agent_repo" {
  provider      = google-beta
  project       = var.project_id
  location      = var.region
  repository_id = var.artifact_repo_name
  description   = "Docker repository for Customer Support Agent container images"
  format        = "DOCKER"

  depends_on = [google_project_service.enabled_apis]
}

# ==============================================================================
# Dedicated Service Account for Cloud Run
# ==============================================================================
resource "google_service_account" "agent_sa" {
  project      = var.project_id
  account_id   = "sa-support-agent"
  display_name = "Customer Support Agent Cloud Run Service Account"

  depends_on = [google_project_service.enabled_apis]
}

# ==============================================================================
# Secret Manager: Gemini API Key Storage
# ==============================================================================
resource "google_secret_manager_secret" "gemini_api_key" {
  project   = var.project_id
  secret_id = "gemini-api-key"

  replication {
    auto {}
  }

  depends_on = [google_project_service.enabled_apis]
}

resource "google_secret_manager_secret_version" "gemini_api_key_version" {
  count       = var.gemini_api_key != "" ? 1 : 0
  secret      = google_secret_manager_secret.gemini_api_key.id
  secret_data = var.gemini_api_key
}

# Grant the Cloud Run Service Account permission to read the secret
resource "google_secret_manager_secret_iam_member" "sa_secret_accessor" {
  project   = var.project_id
  secret_id = google_secret_manager_secret.gemini_api_key.secret_id
  role      = "roles/secretmanager.secretAccessor"
  member    = "serviceAccount:${google_service_account.agent_sa.email}"
}

# ==============================================================================
# Google Cloud Run (v2 Service)
# ==============================================================================
resource "google_cloud_run_v2_service" "agent_service" {
  project  = var.project_id
  name     = var.service_name
  location = var.region
  ingress  = "INGRESS_TRAFFIC_ALL"

  template {
    service_account = google_service_account.agent_sa.email

    scaling {
      min_instance_count = var.min_instances
      max_instance_count = var.max_instances
    }

    containers {
      image = local.effective_image

      ports {
        container_port = 8080
      }

      resources {
        limits = {
          cpu    = var.cpu
          memory = var.memory
        }
      }

      env {
        name  = "ADK_MODEL"
        value = var.adk_model
      }

      env {
        name  = "APP_ENV"
        value = "production"
      }

      # Mount Gemini API key securely from Secret Manager
      env {
        name = "GOOGLE_API_KEY"
        value_source {
          secret_key_ref {
            secret  = google_secret_manager_secret.gemini_api_key.secret_id
            version = "latest"
          }
        }
      }
    }
  }

  depends_on = [
    google_project_service.enabled_apis,
    google_secret_manager_secret_iam_member.sa_secret_accessor,
    google_artifact_registry_repository.agent_repo
  ]
}

# ==============================================================================
# Public Access IAM Policy (Optional, enabled by default)
# ==============================================================================
resource "google_cloud_run_v2_service_iam_member" "public_access" {
  count    = var.allow_unauthenticated ? 1 : 0
  project  = var.project_id
  location = var.region
  name     = google_cloud_run_v2_service.agent_service.name
  role     = "roles/run.invoker"
  member   = "allUsers"
}
