#!/usr/bin/env bash
# Start the Keychain server.
# The server host and port come from the application configuration.
# The script exits immediately if any command fails.

set -euo pipefail

echo "Starting Keychain server..."
exec python -m keychain
