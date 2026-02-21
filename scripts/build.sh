#!/bin/bash
# Build Docker images for the VEAF website.
#
# Usage:
#   ./scripts/build.sh dev    Build development images (deps only, no source)
#   ./scripts/build.sh prod   Build production images (deps + source)
#   ./scripts/build.sh all    Build both dev and prod images

set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"

IMAGE_PREFIX="veaf-website"

RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m'

log_info()  { echo -e "${GREEN}[INFO]${NC}  $*"; }
log_error() { echo -e "${RED}[ERROR]${NC} $*"; }

build_backend() {
    local target="$1"
    local tag="${IMAGE_PREFIX}-backend:${target}"
    log_info "Building backend image: ${tag} (target: ${target})"
    docker build \
        --target "$target" \
        --tag "$tag" \
        "${PROJECT_ROOT}/backend"
}

build_frontend() {
    local target="$1"
    local tag="${IMAGE_PREFIX}-frontend:${target}"
    log_info "Building frontend image: ${tag} (target: ${target})"
    docker build \
        --target "$target" \
        --tag "$tag" \
        "${PROJECT_ROOT}/frontend"
}

build_dev() {
    log_info "Building DEVELOPMENT images..."
    build_backend dev
    build_frontend dev
    echo ""
    log_info "Dev images built:"
    log_info "  ${IMAGE_PREFIX}-backend:dev"
    log_info "  ${IMAGE_PREFIX}-frontend:dev"
}

build_prod() {
    log_info "Building PRODUCTION images..."
    build_backend prod
    build_frontend prod
    echo ""
    log_info "Prod images built:"
    log_info "  ${IMAGE_PREFIX}-backend:prod"
    log_info "  ${IMAGE_PREFIX}-frontend:prod"
}

usage() {
    echo "Usage: $0 {dev|prod|all}"
    echo ""
    echo "Commands:"
    echo "  dev   Build development images (deps only, source mounted at runtime)"
    echo "  prod  Build production images (self-contained with source + deps)"
    echo "  all   Build both dev and prod images"
    exit 1
}

if [[ $# -lt 1 ]]; then
    usage
fi

case "$1" in
    dev)  build_dev  ;;
    prod) build_prod ;;
    all)  build_dev; echo ""; build_prod ;;
    *)
        log_error "Unknown command: $1"
        usage
        ;;
esac
