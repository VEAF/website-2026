#!/bin/bash
# Build Docker images for the VEAF website.
#
# Usage:
#   ./scripts/build.sh                        Build prod images with default tags
#   ./scripts/build.sh dev                    Build development images only
#   ./scripts/build.sh --tag v1.0.0           Build prod images with specific tag
#   ./scripts/build.sh --push                 Build and push to registry
#   ./scripts/build.sh --tag v1.0.0 --push    Build, tag, and push

set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"

REGISTRY="${REGISTRY:-ghcr.io/veaf/website-2026}"
TAG="${TAG:-latest}"
PUSH=false
BUILD_TARGET="prod"

RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m'

log_info()  { echo -e "${GREEN}[INFO]${NC}  $*"; }
log_error() { echo -e "${RED}[ERROR]${NC} $*"; }

usage() {
    echo "Usage: $0 [dev|prod] [--tag TAG] [--registry REGISTRY] [--push]"
    echo ""
    echo "Commands:"
    echo "  dev     Build development images (deps only, source mounted at runtime)"
    echo "  prod    Build production images (default)"
    echo ""
    echo "Options:"
    echo "  --tag TAG             Image tag (default: latest)"
    echo "  --registry REGISTRY   Registry prefix (default: ghcr.io/veaf/website-2026)"
    echo "  --push                Push images to registry after building"
    exit 1
}

# Parse arguments
while [[ $# -gt 0 ]]; do
    case "$1" in
        dev)  BUILD_TARGET="dev"; shift ;;
        prod) BUILD_TARGET="prod"; shift ;;
        --tag) TAG="$2"; shift 2 ;;
        --registry) REGISTRY="$2"; shift 2 ;;
        --push) PUSH=true; shift ;;
        -h|--help) usage ;;
        *)
            log_error "Unknown argument: $1"
            usage
            ;;
    esac
done

build_dev() {
    log_info "Building DEVELOPMENT images..."

    log_info "Building backend dev image: veaf-website-backend:dev"
    docker build \
        --target dev \
        --tag "veaf-website-backend:dev" \
        "${PROJECT_ROOT}/backend"

    log_info "Building frontend dev image: veaf-website-frontend:dev"
    docker build \
        --target dev \
        --tag "veaf-website-frontend:dev" \
        "${PROJECT_ROOT}/frontend"

    echo ""
    log_info "Dev images built:"
    log_info "  veaf-website-backend:dev"
    log_info "  veaf-website-frontend:dev"
}

build_prod() {
    local backend_tag="${REGISTRY}-backend:${TAG}"
    local frontend_tag="${REGISTRY}-frontend:${TAG}"

    log_info "Building PRODUCTION images (tag: ${TAG})..."

    # Build backend
    log_info "Building backend image: ${backend_tag}"
    local backend_tags=("--tag" "$backend_tag")
    if [[ "$TAG" != "latest" ]]; then
        backend_tags+=("--tag" "${REGISTRY}-backend:latest")
    fi
    docker build \
        --target prod \
        "${backend_tags[@]}" \
        "${PROJECT_ROOT}/backend"

    # Build frontend
    log_info "Building frontend image: ${frontend_tag}"
    local frontend_tags=("--tag" "$frontend_tag")
    if [[ "$TAG" != "latest" ]]; then
        frontend_tags+=("--tag" "${REGISTRY}-frontend:latest")
    fi
    docker build \
        --target prod \
        "${frontend_tags[@]}" \
        "${PROJECT_ROOT}/frontend"

    echo ""
    log_info "Prod images built:"
    log_info "  ${backend_tag}"
    log_info "  ${frontend_tag}"

    # Push if requested
    if [[ "$PUSH" == "true" ]]; then
        echo ""
        log_info "Pushing images to registry..."

        docker push "$backend_tag"
        docker push "$frontend_tag"

        if [[ "$TAG" != "latest" ]]; then
            docker push "${REGISTRY}-backend:latest"
            docker push "${REGISTRY}-frontend:latest"
        fi

        log_info "Images pushed successfully."
    fi
}

case "$BUILD_TARGET" in
    dev)  build_dev ;;
    prod) build_prod ;;
esac
