#!/usr/bin/env bash
#
# convert-to-github-raw.sh
# Convert local file:// URLs in markdown reports to GitHub raw URLs
#
# Usage:
#   ./convert-to-github-raw.sh input.md > output.md
#   ./convert-to-github-raw.sh -i input.md  # in-place edit
#

set -euo pipefail

# ============================================================================
# CONFIGURATION
# ============================================================================

GITHUB_USER="${GITHUB_USER:-kimeisele}"
GITHUB_REPO="${GITHUB_REPO:-vibe-agency}"
GITHUB_BRANCH="${GITHUB_BRANCH:-main}"

# Derived
RAW_BASE_URL="https://raw.githubusercontent.com/${GITHUB_USER}/${GITHUB_REPO}/${GITHUB_BRANCH}"

# ============================================================================
# HELPERS
# ============================================================================

usage() {
    cat <<EOF
Usage: $(basename "$0") [OPTIONS] <input.md> [output.md]

Convert local file:// URLs in markdown to GitHub raw URLs.

OPTIONS:
    -h, --help          Show this help
    -i, --in-place      Edit file in-place
    -v, --verbose       Show conversion statistics
    -u, --user USER     GitHub username (default: ${GITHUB_USER})
    -r, --repo REPO     GitHub repo (default: ${GITHUB_REPO})
    -b, --branch BRANCH GitHub branch (default: ${GITHUB_BRANCH})

EXAMPLES:
    $(basename "$0") report.md > external-report.md
    $(basename "$0") -i report.md
    $(basename "$0") -v report.md output.md
    cat report.md | $(basename "$0") -u myuser -r myrepo > out.md

PATTERNS CONVERTED:
    file:///Users/ss/Downloads/vibe-agency/docs/file.md
    → https://raw.githubusercontent.com/.../docs/file.md

    [Link](file:///.../vibe-agency/path/to/file.py)
    → [Link](https://raw.githubusercontent.com/.../path/to/file.py)

EOF
    exit 0
}

log() {
    if [[ "${VERBOSE:-0}" == "1" ]]; then
        echo "[$(basename "$0")] $*" >&2
    fi
}

die() {
    echo "ERROR: $*" >&2
    exit 1
}

# ============================================================================
# ARGUMENT PARSING
# ============================================================================

INPLACE=0
VERBOSE=0
INPUT=""
OUTPUT=""

while [[ $# -gt 0 ]]; do
    case "$1" in
        -h|--help)
            usage
            ;;
        -i|--in-place)
            INPLACE=1
            shift
            ;;
        -v|--verbose)
            VERBOSE=1
            shift
            ;;
        -u|--user)
            GITHUB_USER="$2"
            shift 2
            ;;
        -r|--repo)
            GITHUB_REPO="$2"
            shift 2
            ;;
        -b|--branch)
            GITHUB_BRANCH="$2"
            shift 2
            ;;
        -*)
            die "Unknown option: $1"
            ;;
        *)
            if [[ -z "$INPUT" ]]; then
                INPUT="$1"
            elif [[ -z "$OUTPUT" ]]; then
                OUTPUT="$1"
            else
                die "Too many arguments"
            fi
            shift
            ;;
    esac
done

# Update RAW_BASE_URL after parsing args
RAW_BASE_URL="https://raw.githubusercontent.com/${GITHUB_USER}/${GITHUB_REPO}/${GITHUB_BRANCH}"

# ============================================================================
# VALIDATION
# ============================================================================

# Determine input source
if [[ -z "$INPUT" ]] || [[ "$INPUT" == "-" ]]; then
    # Read from stdin
    INPUT_SOURCE="stdin"
    INPUT_DATA=$(cat)
else
    # Read from file (supports regular files and /dev/fd/* for process substitution)
    if [[ -f "$INPUT" ]] || [[ -r "$INPUT" ]]; then
        INPUT_SOURCE="file"
        INPUT_DATA=$(cat "$INPUT")
    else
        die "Input file not found or not readable: $INPUT"
    fi
fi

# Validate conflicting options
if [[ "$INPLACE" == "1" ]] && [[ "$INPUT_SOURCE" == "stdin" ]]; then
    die "Cannot use --in-place with stdin"
fi

if [[ "$INPLACE" == "1" ]] && [[ -n "$OUTPUT" ]]; then
    die "Cannot specify output file with --in-place"
fi

# ============================================================================
# CONVERSION LOGIC
# ============================================================================

log "Converting URLs..."
log "  Target: ${RAW_BASE_URL}"

# Count for statistics
COUNT_BEFORE=0
COUNT_AFTER=0

if [[ "$VERBOSE" == "1" ]]; then
    # Count occurrences before conversion (both file:// and absolute paths)
    COUNT_FILE=$(echo "$INPUT_DATA" | { grep -o 'file://[^[:space:])]*vibe-agency[^[:space:])]*' 2>/dev/null || true; } | wc -l)
    COUNT_FILE=${COUNT_FILE:-0}
    COUNT_FILE=$((COUNT_FILE + 0))  # Force numeric

    COUNT_ABS=$(echo "$INPUT_DATA" | { grep -o '/[^[:space:])]*vibe-agency/[^[:space:])]*' 2>/dev/null || true; } | wc -l)
    COUNT_ABS=${COUNT_ABS:-0}
    COUNT_ABS=$((COUNT_ABS + 0))  # Force numeric

    COUNT_BEFORE=$((COUNT_FILE + COUNT_ABS))
fi

# Perform conversion
# Strategy: Extract everything after "vibe-agency/" and prepend RAW_BASE_URL
# Handles multiple patterns:
#   1. file://[path]/vibe-agency/FILE
#   2. /absolute/path/vibe-agency/FILE
#   3. Both in markdown links and plaintext

# Pass 1: Convert file:// URLs
CONVERTED_DATA=$(echo "$INPUT_DATA" | sed -E "s|file://[^[:space:])]*/vibe-agency/([^[:space:])]+)|${RAW_BASE_URL}/\1|g")

# Pass 2: Convert absolute paths without file:// prefix
# Pattern: /[path]/vibe-agency/FILE (but NOT if preceded by https: or http:)
# Only match at line start, after whitespace, or after opening parenthesis
CONVERTED_DATA=$(echo "$CONVERTED_DATA" | sed -E "s#(^|[[:space:](])/[^[:space:])]*/vibe-agency/([^[:space:])]+)#\1${RAW_BASE_URL}/\2#g")

if [[ "$VERBOSE" == "1" ]]; then
    # Count occurrences after conversion
    COUNT_FILE_AFTER=$(echo "$CONVERTED_DATA" | { grep -o 'file://[^[:space:])]*vibe-agency[^[:space:])]*' 2>/dev/null || true; } | wc -l)
    COUNT_FILE_AFTER=${COUNT_FILE_AFTER:-0}
    COUNT_FILE_AFTER=$((COUNT_FILE_AFTER + 0))  # Force numeric

    COUNT_ABS_AFTER=$(echo "$CONVERTED_DATA" | { grep -o '/[^[:space:])]*vibe-agency/[^[:space:])]*' 2>/dev/null || true; } | wc -l)
    COUNT_ABS_AFTER=${COUNT_ABS_AFTER:-0}
    COUNT_ABS_AFTER=$((COUNT_ABS_AFTER + 0))  # Force numeric

    COUNT_AFTER=$((COUNT_FILE_AFTER + COUNT_ABS_AFTER))
    CONVERTED=$((COUNT_BEFORE - COUNT_AFTER))
    log "Converted ${CONVERTED} URL(s)"
fi

# ============================================================================
# OUTPUT
# ============================================================================

if [[ "$INPLACE" == "1" ]]; then
    # Write back to original file
    echo "$CONVERTED_DATA" > "$INPUT"
    log "File updated in-place: $INPUT"
elif [[ -n "$OUTPUT" ]]; then
    # Write to output file
    echo "$CONVERTED_DATA" > "$OUTPUT"
    log "Output written to: $OUTPUT"
else
    # Write to stdout
    echo "$CONVERTED_DATA"
fi

log "Done."
