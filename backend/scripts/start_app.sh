#!/usr/bin/env bash
# Apply pending database migrations, then start the Keychain server.
# The server host and port come from the application configuration.
# The script exits immediately if any command fails.

set -euo pipefail

echo "Applying pending database migrations..."
keychain db upgrade

echo "Starting Keychain server..."
exec python -m keychain
