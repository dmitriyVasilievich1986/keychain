#!/usr/bin/env bash
# Install dependencies and build the frontend bundle into ../static.
# The script exits immediately if any command fails.

set -euo pipefail

echo "Installing npm..."
npm install -g npm@12.0.1

echo "Installing dependencies..."
npm ci

echo "Building frontend bundle..."
npm run build
