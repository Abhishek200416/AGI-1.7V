#!/usr/bin/env bash
# Forwarding launcher to run_iva.sh
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
exec "$SCRIPT_DIR/run_iva.sh" "$@"
