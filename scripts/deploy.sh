#!/usr/bin/env bash
# ==============================================================================
# Google Cloud Run Deployment Script for Customer Support Agent
# ==============================================================================

set -euo pipefail

# Configuration
PROJECT_ID="${GCP_PROJECT_ID:-extended-atrium-508907-b6}"
REGION="${GCP_REGION:-us-central1}"
REPO_NAME="customer-support-agent-repo"
SERVICE_NAME="customer-support-agent"
IMAGE_TAG="${IMAGE_TAG:-latest}"
IMAGE_URI="${REGION}-docker.pkg.dev/${PROJECT_ID}/${REPO_NAME}/${SERVICE_NAME}:${IMAGE_TAG}"

echo "========================================================================"
echo "  🚀 Deploying Customer Support Agent to Google Cloud"
echo "  • Project: ${PROJECT_ID}"
echo "  • Region:  ${REGION}"
echo "  • Image:   ${IMAGE_URI}"
echo "========================================================================"

# Step 1: Verify prerequisites
command -v docker >/dev/null 2>&1 || { echo "❌ Error: 'docker' is required but not installed."; exit 1; }
command -v gcloud >/dev/null 2>&1 || { echo "❌ Error: 'gcloud' CLI is required. Install via: brew install --cask google-cloud-sdk"; exit 1; }
command -v terraform >/dev/null 2>&1 || { echo "❌ Error: 'terraform' is required. Install via: brew install hashicorp/tap/terraform"; exit 1; }

# Step 2: Configure gcloud project
echo "⚙️ Setting active gcloud project..."
gcloud config set project "${PROJECT_ID}" --quiet

# Step 3: Enable Artifact Registry API and authenticate Docker
echo "🔐 Authenticating Docker with Google Artifact Registry..."
gcloud services enable artifactregistry.googleapis.com --project="${PROJECT_ID}" --quiet
gcloud auth configure-docker "${REGION}-docker.pkg.dev" --quiet

# Step 4: Ensure Artifact Registry repository exists
if ! gcloud artifacts repositories describe "${REPO_NAME}" --location="${REGION}" --project="${PROJECT_ID}" >/dev/null 2>&1; then
    echo "📦 Creating Artifact Registry repository '${REPO_NAME}'..."
    gcloud artifacts repositories create "${REPO_NAME}" \
        --repository-format=docker \
        --location="${REGION}" \
        --project="${PROJECT_ID}" \
        --description="Docker repository for Customer Support Agent" \
        --quiet
fi

# Step 5: Build container image for linux/amd64 (Cloud Run standard)
echo "🔨 Building Docker image (${IMAGE_URI})..."
docker build --platform linux/amd64 -t "${IMAGE_URI}" .

# Step 6: Push container image
echo "⬆️ Pushing Docker image to Artifact Registry..."
docker push "${IMAGE_URI}"

# Step 7: Apply Terraform infrastructure
echo "🏗️ Applying Terraform configuration..."
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "${SCRIPT_DIR}/../terraform"

terraform init
terraform apply -auto-approve \
    -var="project_id=${PROJECT_ID}" \
    -var="region=${REGION}" \
    -var="service_name=${SERVICE_NAME}" \
    -var="artifact_repo_name=${REPO_NAME}" \
    -var="container_image=${IMAGE_URI}"

echo "========================================================================"
echo "  ✅ Deployment completed successfully!"
echo "  Live Service URL:"
terraform output cloud_run_url
echo "========================================================================"
