#!/bin/bash
# Shell wrapper for 3D AI Studio API client
# Use this as a convenience wrapper if preferred over direct Python calls

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Check Python dependencies
check_deps() {
  python3 -c "import requests; import dotenv" 2>/dev/null || {
    echo "Error: Missing dependencies. Install with:"
    echo "  pip install -r $SCRIPT_DIR/requirements.txt"
    exit 1
  }
}

# Run the Python client
run_client() {
  check_deps
  python3 "$SCRIPT_DIR/3d_api_client.py" "$@"
}

# Show help if no arguments
if [[ $# -eq 0 ]]; then
  run_client --help
else
  run_client "$@"
fi
