#!/usr/bin/env bash
# ==============================================================================
# Google Cloud Run Deployment Script for Customer Support Agent
# ==============================================================================

set -euo pipefail

# Export paths for standard gcloud, terraform, and homebrew installations
export PATH="${HOME}/google-cloud-sdk/bin:${HOME}/.local/bin:/opt/homebrew/bin:${PATH}"

# Configuration
PROJECT_ID="${GCP_PROJECT_ID:-extended-atrium-508907-b6}"
REGION="${GCP_REGION:-us-central1}"
REPO_NAME="customer-support-agent-repo"
SERVICE_NAME="customer-support-agent"
IMAGE_TAG="${IMAGE_TAG:-latest}"
IMAGE_URI="${REGION}-docker.pkg.dev/${PROJECT_ID}/${REPO_NAME}/${SERVICE_NAME}:${IMAGE_TAG}"

# Locate root directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
cd "${ROOT_DIR}"

# Extract API key if available
GEMINI_API_KEY="${GOOGLE_API_KEY:-}"
if [[ -z "${GEMINI_API_KEY}" && -f "${ROOT_DIR}/.env" ]]; then
    GEMINI_API_KEY=$(grep -E "^GOOGLE_API_KEY=" "${ROOT_DIR}/.env" | cut -d '=' -f2- | tr -d '"' | tr -d "'" || true)
fi

echo "========================================================================"
echo "  🚀 Deploying Customer Support Agent to Google Cloud"
echo "  • Project: ${PROJECT_ID}"
echo "  • Region:  ${REGION}"
echo "  • Image:   ${IMAGE_URI}"
echo "========================================================================"

# Step 1: Verify prerequisites
command -v gcloud >/dev/null 2>&1 || { echo "❌ Error: 'gcloud' CLI is required."; exit 1; }
command -v terraform >/dev/null 2>&1 || { echo "❌ Error: 'terraform' is required."; exit 1; }

# Step 2: Configure gcloud project and refresh auth tokens
echo "⚙️ Configuring gcloud project..."
gcloud config set project "${PROJECT_ID}" --quiet

echo "🔑 Exporting Google Cloud OAuth access token for Terraform..."
export GOOGLE_OAUTH_ACCESS_TOKEN=$(gcloud auth print-access-token)

# Step 3: Enable essential services
echo "📦 Ensuring core Google Cloud APIs are enabled..."
gcloud services enable \
    artifactregistry.googleapis.com \
    cloudbuild.googleapis.com \
    run.googleapis.com \
    secretmanager.googleapis.com \
    --project="${PROJECT_ID}" --quiet

TF_VARS=(
    -var="project_id=${PROJECT_ID}"
    -var="region=${REGION}"
    -var="service_name=${SERVICE_NAME}"
    -var="artifact_repo_name=${REPO_NAME}"
    -var="container_image=${IMAGE_URI}"
)

if [[ -n "${GEMINI_API_KEY}" ]]; then
    TF_VARS+=(-var="gemini_api_key=${GEMINI_API_KEY}")
fi

# Step 4: Provision Artifact Registry repository via Terraform
echo "📦 Provisioning Artifact Registry repository via Terraform..."
cd "${ROOT_DIR}/terraform"
terraform init
terraform apply -target=google_artifact_registry_repository.agent_repo -auto-approve "${TF_VARS[@]}"
cd "${ROOT_DIR}"

# Step 5: Build and Push Container Image
# Check if local Docker daemon is running; otherwise fall back smoothly to Cloud Build
if command -v docker >/dev/null 2>&1 && docker info >/dev/null 2>&1; then
    echo "🐳 Local Docker daemon detected. Building locally for linux/amd64..."
    gcloud auth configure-docker "${REGION}-docker.pkg.dev" --quiet
    docker build --platform linux/amd64 -t "${IMAGE_URI}" .
    echo "⬆️ Pushing image to Artifact Registry via Docker..."
    docker push "${IMAGE_URI}"
else
    echo "☁️ Docker daemon not active locally. Building and pushing via Google Cloud Build..."
    gcloud builds submit --tag "${IMAGE_URI}" --project="${PROJECT_ID}" .
fi

# Step 6: Apply complete Terraform infrastructure (Cloud Run, Secret Manager, IAM)
echo "🏗️ Applying complete Terraform infrastructure..."
cd "${ROOT_DIR}/terraform"
terraform apply -auto-approve "${TF_VARS[@]}"

echo "========================================================================"
echo "  ✅ Deployment completed successfully!"
echo "  Live Service URL:"
terraform output cloud_run_url
echo "========================================================================"
