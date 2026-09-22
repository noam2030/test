variable "project_id" {
  type        = string
  description = "The Google Cloud Project ID to deploy resources to."
  default     = "extended-atrium-508907-b6"
}

variable "region" {
  type        = string
  description = "The primary Google Cloud region for compute and storage."
  default     = "us-central1"
}

variable "service_name" {
  type        = string
  description = "The name of the Cloud Run v2 service."
  default     = "customer-support-agent"
}

variable "artifact_repo_name" {
  type        = string
  description = "The name of the Artifact Registry repository for container images."
  default     = "customer-support-agent-repo"
}

variable "container_image" {
  type        = string
  description = "The full Docker image URI. If left empty, defaults to the image in the managed Artifact Registry."
  default     = ""
}

variable "adk_model" {
  type        = string
  description = "The Gemini foundation model for the Google ADK agent."
  default     = "gemini-3.6-flash"
}

variable "allow_unauthenticated" {
  type        = bool
  description = "Whether to allow unauthenticated public HTTP access to the Cloud Run service."
  default     = true
}

variable "gemini_api_key" {
  type        = string
  description = "Google Gemini API key to store in Secret Manager."
  sensitive   = true
  default     = ""
}

variable "min_instances" {
  type        = number
  description = "Minimum number of Cloud Run instances (0 allows scale-to-zero for cost savings)."
  default     = 0
}

variable "max_instances" {
  type        = number
  description = "Maximum number of Cloud Run instances for autoscaling."
  default     = 3
}

variable "cpu" {
  type        = string
  description = "CPU allocation for the Cloud Run container."
  default     = "1"
}

variable "memory" {
  type        = string
  description = "Memory allocation for the Cloud Run container."
  default     = "1Gi"
}
