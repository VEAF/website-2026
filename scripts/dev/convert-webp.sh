#!/bin/bash
# Convert JPG/PNG images to WebP format for better web performance.
#
# Requires: cwebp (sudo apt install webp)
#
# Usage:
#   ./scripts/dev/convert-webp.sh                        Convert frontend/public/img/
#   ./scripts/dev/convert-webp.sh path/to/images/        Convert a custom directory
#   ./scripts/dev/convert-webp.sh -f                     Force reconvert existing files
#   ./scripts/dev/convert-webp.sh -q 90                  Set quality (default: 80)
#   ./scripts/dev/convert-webp.sh -f -q 90 path/to/dir/  All options combined

set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
NC='\033[0m'

log_info()  { echo -e "${GREEN}[INFO]${NC}  $*"; }
log_warn()  { echo -e "${YELLOW}[WARN]${NC}  $*"; }
log_error() { echo -e "${RED}[ERROR]${NC} $*"; }

# Defaults
QUALITY=80
FORCE=false
IMG_DIR=""

# Parse arguments
while [[ $# -gt 0 ]]; do
    case "$1" in
        -f|--force)
            FORCE=true
            shift
            ;;
        -q|--quality)
            QUALITY="$2"
            shift 2
            ;;
        -h|--help)
            head -n 11 "$0" | tail -n 9
            exit 0
            ;;
        *)
            IMG_DIR="$1"
            shift
            ;;
    esac
done

# Default directory
if [[ -z "$IMG_DIR" ]]; then
    IMG_DIR="${PROJECT_ROOT}/frontend/public/img"
fi

# Validate
if ! command -v cwebp &>/dev/null; then
    log_error "cwebp is not installed. Install it with: sudo apt install webp"
    exit 1
fi

if [[ ! -d "$IMG_DIR" ]]; then
    log_error "Directory not found: $IMG_DIR"
    exit 1
fi

log_info "Converting images in ${IMG_DIR} (quality: ${QUALITY})"

converted=0
skipped=0
total_before=0
total_after=0

for file in "$IMG_DIR"/*.{jpg,jpeg,png,JPG,JPEG,PNG}; do
    [[ -f "$file" ]] || continue

    webp_file="${file%.*}.webp"

    # Skip if webp exists and is newer than source (unless --force)
    if [[ "$FORCE" == false && -f "$webp_file" && "$webp_file" -nt "$file" ]]; then
        log_warn "Skipped (already exists): $(basename "$webp_file")"
        skipped=$((skipped + 1))
        continue
    fi

    size_before=$(stat -c%s "$file")
    total_before=$((total_before + size_before))

    cwebp -q "$QUALITY" -alpha_q 100 "$file" -o "$webp_file" -quiet

    size_after=$(stat -c%s "$webp_file")
    total_after=$((total_after + size_after))

    reduction=$(( (size_before - size_after) * 100 / size_before ))
    log_info "$(basename "$file") → $(basename "$webp_file")  (${size_before} → ${size_after} bytes, -${reduction}%)"

    converted=$((converted + 1))
done

echo ""
if [[ $converted -eq 0 && $skipped -eq 0 ]]; then
    log_warn "No images found in ${IMG_DIR}"
elif [[ $converted -eq 0 ]]; then
    log_info "Nothing to convert (${skipped} file(s) already up to date). Use -f to force."
else
    total_reduction=0
    if [[ $total_before -gt 0 ]]; then
        total_reduction=$(( (total_before - total_after) * 100 / total_before ))
    fi
    log_info "Done: ${converted} converted, ${skipped} skipped"
    log_info "Total: ${total_before} → ${total_after} bytes (-${total_reduction}%)"
fi
